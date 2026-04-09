# -*- coding: utf-8 -*-
"""
店主后台管理 API
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from database import db

router = APIRouter()

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

    refund_amount = Decimal(str(request.amount)) if request.amount else order['total_deposit']
    
    # 模拟微信支付退款逻辑
    # wechat_pay.refund(...)

    db.execute_update(
        "UPDATE orders SET status = 7, refund_amount = %s, refund_time = NOW(), remark = %s WHERE id = %s",
        (refund_amount, request.reason, request.order_id)
    )

    return {"code": 0, "message": "退款成功", "data": {"refund_amount": float(refund_amount)}}

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

    refund_amount = order['total_deposit'] - Decimal(str(request.amount))

    db.execute_update(
        "UPDATE orders SET status = 7, refund_amount = %s, refund_time = NOW(), remark = %s WHERE id = %s",
        (refund_amount, f"扣除押金 {request.amount} 元: {request.reason}", request.order_id)
    )

    return {"code": 0, "message": "扣除成功", "data": {"refund_amount": float(refund_amount)}}

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
