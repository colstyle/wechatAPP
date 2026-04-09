# -*- coding: utf-8 -*-
"""
店主后台管理 API
"""
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from database import db
from app.utils.wechat_pay import wechat_pay
import uuid

router = APIRouter()

# ============ 响应模型 ============

class AdminOrderResponse(BaseModel):
    id: int
    order_no: str
    user_id: int
    nickname: Optional[str]
    total_amount: float
    status: int
    status_text: str
    created_at: str

# ============ 管理端API ============

@router.get("/orders")
async def get_all_orders(
    status: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    获取全量订单 (店主端)
    """
    conditions = []
    params = []

    if status is not None:
        conditions.append("o.status = %s")
        params.append(status)
    
    if keyword:
        conditions.append("(o.order_no LIKE %s OR u.nickname LIKE %s)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # 查询总数
    count_sql = f"""
        SELECT COUNT(*) as total 
        FROM orders o 
        LEFT JOIN users u ON o.user_id = u.id
        {where_clause}
    """
    total_result = db.execute_one(count_sql, tuple(params))
    total = total_result['total'] if total_result else 0

    # 查询列表
    offset = (page - 1) * page_size
    list_sql = f"""
        SELECT o.*, u.nickname, u.avatar
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.id
        {where_clause}
        ORDER BY o.created_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([page_size, offset])
    orders = db.execute_query(list_sql, tuple(params))

    status_text_map = {
        0: '待支付', 1: '待取衣', 2: '租赁中', 3: '已逾期',
        4: '待审核', 5: '已取消', 6: '退款中', 7: '已完成'
    }

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "list": [
                {
                    "id": o['id'],
                    "order_no": o['order_no'],
                    "user_id": o['user_id'],
                    "nickname": o['nickname'],
                    "avatar": o['avatar'],
                    "total_amount": float(o['total_amount']),
                    "status": o['status'],
                    "status_text": status_text_map.get(o['status'], '未知'),
                    "created_at": o['created_at'].isoformat() if o['created_at'] else None
                }
                for o in orders
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }

class RefundRequest(BaseModel):
    order_id: int
    amount: Optional[float] = None # 如果不填则退全额押金
    reason: Optional[str] = "店主确认无误，原路退还押金"

class DeductionRequest(BaseModel):
    order_id: int
    amount: float
    reason: str

class UpdateOrderItemsRequest(BaseModel):
    order_id: int
    items: List[dict] # [{"product_id": 1, "size": "M", "color": "白色"}]

@router.post("/refund")
async def refund_order(request: RefundRequest):
    """
    一键退还押金 (模拟)
    """
    order = db.execute_one("SELECT * FROM orders WHERE id = %s", (request.order_id,))
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order['status'] != 4: # 4 为已归还待审核
        raise HTTPException(status_code=400, detail="当前订单状态不可退押金")

    refund_amount_decimal = Decimal(str(request.amount)) if request.amount else order['total_deposit']
    
    # 微信支付 V3 退款框架调用
    out_refund_no = f"REF{uuid.uuid4().hex[:20].upper()}"
    wechat_pay.refund(
        out_trade_no=order['order_no'],
        out_refund_no=out_refund_no,
        refund_amount=int(refund_amount_decimal * 100), # 转换为分
        total_amount=int(order['total_amount'] * 100), # 转换为分
        reason=request.reason
    )

    db.execute_update(
        "UPDATE orders SET status = 7, refund_amount = %s, refund_time = NOW(), remark = %s WHERE id = %s",
        (refund_amount_decimal, request.reason, request.order_id)
    )

    return {"code": 0, "message": "退款成功", "data": {"refund_amount": float(refund_amount_decimal)}}

@router.post("/deduct")
async def deduct_deposit(request: DeductionRequest):
    """
    手动扣除押金 (逾期或损坏)
    """
    order = db.execute_one("SELECT * FROM orders WHERE id = %s", (request.order_id,))
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order['status'] not in [2, 3, 4]: # 租赁中、逾期、已归还
        raise HTTPException(status_code=400, detail="当前订单状态不可扣除押金")

    if Decimal(str(request.amount)) > order['total_deposit']:
        raise HTTPException(status_code=400, detail="扣除金额不能超过总押金")

    refund_amount_decimal = order['total_deposit'] - Decimal(str(request.amount))

    # 微信支付 V3 退款框架调用
    out_refund_no = f"DED{uuid.uuid4().hex[:20].upper()}"
    wechat_pay.refund(
        out_trade_no=order['order_no'],
        out_refund_no=out_refund_no,
        refund_amount=int(refund_amount_decimal * 100), # 转换为分
        total_amount=int(order['total_amount'] * 100), # 转换为分
        reason=request.reason
    )

    db.execute_update(
        "UPDATE orders SET status = 7, refund_amount = %s, refund_time = NOW(), remark = %s WHERE id = %s",
        (refund_amount_decimal, f"扣除押金 {request.amount} 元: {request.reason}", request.order_id)
    )

    return {"code": 0, "message": "扣除成功", "data": {"refund_amount": float(refund_amount_decimal)}}

@router.post("/update-items")
async def update_order_items(request: UpdateOrderItemsRequest):
    """
    手动修改订单衣物 (换款逻辑)
    """
    order = db.execute_one("SELECT * FROM orders WHERE id = %s", (request.order_id,))
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order['status'] != 1: # 仅支持待取衣状态修改
        raise HTTPException(status_code=400, detail="仅待取衣状态可修改衣物")

    # 获取新商品信息
    product_ids = [item['product_id'] for item in request.items]
    products = db.execute_query("SELECT * FROM products WHERE id IN (%s)" % ','.join(['%s'] * len(product_ids)), tuple(product_ids))
    product_map = {p['id']: p for p in products}

    db.begin_transaction()
    try:
        # 删除旧商品和预约
        db.execute_update("DELETE FROM order_items WHERE order_id = %s", (request.order_id,))
        db.execute_update("DELETE FROM reservations WHERE order_id = %s", (request.order_id,))

        new_total_deposit = Decimal('0.00')
        for item in request.items:
            product = product_map.get(item['product_id'])
            if not product:
                raise HTTPException(status_code=404, detail=f"商品ID {item['product_id']} 不存在")
            
            deposit = Decimal(str(product['deposit']))
            new_total_deposit += deposit

            db.execute_insert(
                """INSERT INTO order_items (order_id, product_id, product_name, product_image, size, color,
                   rent_price, deposit, quantity, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
                (request.order_id, item['product_id'], product['name'], product['cover_image'],
                 item.get('size', ''), item.get('color', ''), 0, deposit, 1)
            )
            
            db.execute_insert(
                "INSERT INTO reservations (product_id, reserved_date, order_id, created_at) VALUES (%s, %s, %s, NOW())",
                (item['product_id'], order['start_date'], request.order_id)
            )

        # 更新订单总押金和总额
        new_total_amount = order['total_rent'] + new_total_deposit
        db.execute_update(
            "UPDATE orders SET total_deposit = %s, total_amount = %s WHERE id = %s",
            (new_total_deposit, new_total_amount, request.order_id)
        )

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"修改订单失败: {str(e)}")

    return {"code": 0, "message": "订单衣物已更新"}
