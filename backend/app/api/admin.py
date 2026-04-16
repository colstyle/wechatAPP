# -*- coding: utf-8 -*-
"""
店主后台管理 API
"""
from fastapi import APIRouter, HTTPException, Body, Query, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from database import db
from app.utils.wechat_pay import wechat_pay
from app.utils.auth import require_admin
from app.utils.audit import write_order_audit
import uuid
import hashlib

router = APIRouter()

# ============ 响应模型 ============

class AdminOrderResponse(BaseModel):
    id: int
    order_sn: str
    user_id: int
    nickname: Optional[str]
    total_amount: float
    status: int
    status_text: str
    created_at: str

class AdminCategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: int
    icon: Optional[str]
    sort_order: int

# ============ 管理端API ============

class CategoryCreateRequest(BaseModel):
    name: str
    parent_id: int = 0
    icon: Optional[str] = None


class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None


class CategoryReorderRequest(BaseModel):
    parent_id: int = 0
    ordered_ids: List[int]


@router.get("/categories")
async def admin_get_categories(
    parent_id: int = Query(0),
    authorization: Optional[str] = Header(None)
):
    require_admin(authorization)
    categories = db.execute_query(
        "SELECT * FROM categories WHERE parent_id = %s ORDER BY sort_order ASC, id ASC",
        (parent_id,)
    )
    return {
        "code": 0,
        "message": "获取成功",
        "data": [
            {
                "id": c["id"],
                "name": c["name"],
                "parent_id": c["parent_id"],
                "icon": c.get("icon"),
                "sort_order": c.get("sort_order", 0),
            }
            for c in categories
        ],
    }


@router.post("/categories")
async def admin_create_category(
    request: CategoryCreateRequest,
    authorization: Optional[str] = Header(None)
):
    require_admin(authorization)
    name = (request.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="分类名称不能为空")

    max_row = db.execute_one(
        "SELECT COALESCE(MAX(sort_order), -1) as mx FROM categories WHERE parent_id = %s",
        (request.parent_id,)
    )
    next_sort = int((max_row or {}).get("mx", -1)) + 1
    new_id = db.execute_insert(
        "INSERT INTO categories (name, parent_id, icon, sort_order, created_at) VALUES (%s, %s, %s, %s, NOW())",
        (name, request.parent_id, request.icon, next_sort)
    )
    return {"code": 0, "message": "创建成功", "data": {"id": new_id}}


@router.put("/categories/{category_id}")
async def admin_update_category(
    category_id: int,
    request: CategoryUpdateRequest,
    authorization: Optional[str] = Header(None)
):
    require_admin(authorization)
    cat = db.execute_one("SELECT * FROM categories WHERE id = %s", (category_id,))
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")

    updates = []
    params = []
    if request.name is not None:
        name = request.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="分类名称不能为空")
        updates.append("name = %s")
        params.append(name)
    if request.icon is not None:
        updates.append("icon = %s")
        params.append(request.icon)

    if not updates:
        return {"code": 0, "message": "更新成功", "data": {"id": category_id}}

    params.append(category_id)
    db.execute_update(f"UPDATE categories SET {', '.join(updates)} WHERE id = %s", tuple(params))
    return {"code": 0, "message": "更新成功", "data": {"id": category_id}}


@router.delete("/categories/{category_id}")
async def admin_delete_category(
    category_id: int,
    authorization: Optional[str] = Header(None)
):
    require_admin(authorization)
    cat = db.execute_one("SELECT * FROM categories WHERE id = %s", (category_id,))
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")

    child = db.execute_one("SELECT id FROM categories WHERE parent_id = %s LIMIT 1", (category_id,))
    if child:
        raise HTTPException(status_code=400, detail="存在子分类，无法删除")

    prod = db.execute_one("SELECT id FROM products WHERE category_id = %s LIMIT 1", (category_id,))
    if prod:
        raise HTTPException(status_code=400, detail="该分类下存在商品，无法删除")

    db.execute_update("DELETE FROM categories WHERE id = %s", (category_id,))
    return {"code": 0, "message": "删除成功"}


@router.post("/categories/reorder")
async def admin_reorder_categories(
    request: CategoryReorderRequest,
    authorization: Optional[str] = Header(None)
):
    require_admin(authorization)
    if not request.ordered_ids:
        return {"code": 0, "message": "更新成功"}

    existing = db.execute_query(
        f"SELECT id FROM categories WHERE parent_id = %s AND id IN ({','.join(['%s'] * len(request.ordered_ids))})",
        tuple([request.parent_id] + request.ordered_ids)
    )
    existing_ids = {row["id"] for row in (existing or [])}
    for cid in request.ordered_ids:
        if cid not in existing_ids:
            raise HTTPException(status_code=400, detail="包含无效分类ID")

    db.begin_transaction()
    try:
        for idx, cid in enumerate(request.ordered_ids):
            db.execute_update(
                "UPDATE categories SET sort_order = %s WHERE id = %s AND parent_id = %s",
                (idx, cid, request.parent_id)
            )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"code": 0, "message": "更新成功"}

@router.get("/orders")
async def get_all_orders(
    status: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    authorization: Optional[str] = Header(None)
):
    """
    获取全量订单 (店主端)
    """
    require_admin(authorization)
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
        SELECT o.*, u.nickname, u.avatar_url
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
                    "order_sn": o['order_sn'],
                    "user_id": o['user_id'],
                    "nickname": o['nickname'],
                    "avatar_url": o['avatar_url'],
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

@router.get("/orders/{order_id}")
async def get_order_detail(order_id: int, authorization: Optional[str] = Header(None)):
    """
    获取单个订单详情 (店主端)
    """
    require_admin(authorization)
    
    order = db.execute_one(
        """SELECT o.*, u.nickname, u.avatar_url 
           FROM orders o 
           LEFT JOIN users u ON o.user_id = u.id 
           WHERE o.id = %s""", 
        (order_id,)
    )
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 获取订单项
    items = db.execute_query(
        "SELECT * FROM order_items WHERE order_id = %s",
        (order_id,)
    )

    status_text_map = {
        0: '待支付', 1: '待取衣', 2: '租赁中', 3: '已逾期',
        4: '待审核', 5: '已取消', 6: '退款中', 7: '已完成'
    }

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": order['id'],
            "order_no": order['order_no'],
            "user_id": order['user_id'],
            "nickname": order['nickname'],
            "avatar": order['avatar'],
            "total_rent": float(order['total_rent']),
            "total_deposit": float(order['total_deposit']),
            "total_amount": float(order['total_amount']),
            "status": order['status'],
            "status_text": status_text_map.get(order['status'], '未知'),
            "pickup_time": order['pickup_time'].isoformat() if order['pickup_time'] else None,
            "return_time": order['return_time'].isoformat() if order['return_time'] else None,
            "expected_return_time": order['expected_return_time'].isoformat() if order['expected_return_time'] else None,
            "created_at": order['created_at'].isoformat() if order['created_at'] else None,
            "items": [
                {
                    "id": i['id'],
                    "product_id": i['product_id'],
                    "product_name": i['product_name'],
                    "product_image": i['product_image'],
                    "size": i['size'],
                    "color": i['color'],
                    "price": float(i['price']),
                    "deposit": float(i['deposit']),
                    "quantity": i['quantity']
                }
                for i in items
            ]
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


def _make_out_refund_no(prefix: str, order_no: str, request_id: Optional[str]) -> str:
    if request_id:
        digest = hashlib.sha1(f"{order_no}:{request_id}".encode("utf-8")).hexdigest()[:20].upper()
        return f"{prefix}{digest}"
    return f"{prefix}{uuid.uuid4().hex[:20].upper()}"


@router.post("/refund")
async def refund_order(
    request: RefundRequest,
    authorization: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    一键退还押金 (模拟)
    """
    admin = require_admin(authorization)

    db.begin_transaction()
    try:
        order = db.execute_one("SELECT * FROM orders WHERE id = %s FOR UPDATE", (request.order_id,))
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        if int(order.get('status', 0)) == 7 and order.get('refund_time'):
            db.commit()
            return {"code": 0, "message": "退款成功", "data": {"refund_amount": float(order.get('refund_amount') or 0)}}

        if order['status'] != 4:
            raise HTTPException(status_code=400, detail="当前订单状态不可退押金")

        refund_amount_decimal = Decimal(str(request.amount)) if request.amount is not None else Decimal(str(order['total_deposit']))
        if refund_amount_decimal <= 0:
            raise HTTPException(status_code=400, detail="退款金额必须大于0")
        if refund_amount_decimal > Decimal(str(order['total_deposit'])):
            raise HTTPException(status_code=400, detail="退款金额不能超过总押金")

        out_refund_no = _make_out_refund_no("REF", order['order_no'], x_request_id)

        wechat_pay.refund(
            out_trade_no=order['order_no'],
            out_refund_no=out_refund_no,
            refund_amount=int(refund_amount_decimal * 100),
            total_amount=int(order['total_amount'] * 100),
            reason=request.reason
        )

        db.execute_update(
            "UPDATE orders SET status = 7, refund_amount = %s, refund_time = NOW(), remark = %s, last_refund_no = %s, last_refund_action = %s WHERE id = %s",
            (refund_amount_decimal, request.reason, out_refund_no, "refund", request.order_id)
        )
        db.commit()

        write_order_audit(
            order_id=request.order_id,
            action="refund",
            operator_role=str(admin.get("role", "admin")),
            operator_id=int(admin.get("id")) if admin.get("id") is not None else None,
            request_id=x_request_id,
            amount=float(refund_amount_decimal),
            reason=request.reason,
            before_status=4,
            after_status=7,
            extra={"out_refund_no": out_refund_no},
        )

        return {"code": 0, "message": "退款成功", "data": {"refund_amount": float(refund_amount_decimal)}}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"退款失败: {str(e)}")

@router.post("/deduct")
async def deduct_deposit(
    request: DeductionRequest,
    authorization: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    手动扣除押金 (逾期或损坏)
    """
    admin = require_admin(authorization)

    db.begin_transaction()
    try:
        order = db.execute_one("SELECT * FROM orders WHERE id = %s FOR UPDATE", (request.order_id,))
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        if int(order.get('status', 0)) == 7 and order.get('refund_time'):
            db.commit()
            return {"code": 0, "message": "扣除成功", "data": {"refund_amount": float(order.get('refund_amount') or 0)}}

        if order['status'] not in [2, 3, 4]:
            raise HTTPException(status_code=400, detail="当前订单状态不可扣除押金")

        if Decimal(str(request.amount)) <= 0:
            raise HTTPException(status_code=400, detail="扣除金额必须大于0")
        if not request.reason:
            raise HTTPException(status_code=400, detail="扣费原因必填")
        if Decimal(str(request.amount)) > Decimal(str(order['total_deposit'])):
            raise HTTPException(status_code=400, detail="扣除金额不能超过总押金")

        refund_amount_decimal = Decimal(str(order['total_deposit'])) - Decimal(str(request.amount))

        out_refund_no = _make_out_refund_no("DED", order['order_no'], x_request_id)
        wechat_pay.refund(
            out_trade_no=order['order_no'],
            out_refund_no=out_refund_no,
            refund_amount=int(refund_amount_decimal * 100),
            total_amount=int(order['total_amount'] * 100),
            reason=request.reason
        )

        remark = f"扣除押金 {request.amount} 元: {request.reason}"
        db.execute_update(
            "UPDATE orders SET status = 7, refund_amount = %s, refund_time = NOW(), remark = %s, last_refund_no = %s, last_refund_action = %s WHERE id = %s",
            (refund_amount_decimal, remark, out_refund_no, "deduct", request.order_id)
        )
        db.commit()

        write_order_audit(
            order_id=request.order_id,
            action="deduct",
            operator_role=str(admin.get("role", "admin")),
            operator_id=int(admin.get("id")) if admin.get("id") is not None else None,
            request_id=x_request_id,
            amount=float(request.amount),
            reason=request.reason,
            before_status=int(order.get('status', 0)),
            after_status=7,
            extra={"out_refund_no": out_refund_no, "refund_amount": float(refund_amount_decimal)},
        )

        return {"code": 0, "message": "扣除成功", "data": {"refund_amount": float(refund_amount_decimal)}}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"扣除失败: {str(e)}")

@router.post("/update-items")
async def update_order_items(
    request: UpdateOrderItemsRequest,
    authorization: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    手动修改订单衣物 (换款逻辑)
    """
    admin = require_admin(authorization)
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
        before_items = db.execute_query("SELECT * FROM order_items WHERE order_id = %s", (request.order_id,))
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
                   price, deposit, quantity)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (request.order_id, item['product_id'], product['name'], product['main_image'],
                 item.get('size', ''), item.get('color', ''), 0, deposit, 1)
            )
            
            try:
                db.execute_insert(
                    "INSERT INTO reservations (product_id, reserved_date, order_id, created_at) VALUES (%s, %s, %s, NOW())",
                    (item['product_id'], order['start_date'], request.order_id)
                )
            except Exception as e:
                msg = str(e)
                if "Duplicate entry" in msg or "1062" in msg:
                    raise HTTPException(status_code=400, detail=f"衣物《{product['name']}》在 {order['start_date'].isoformat()} 已被预订")
                raise

        # 更新订单总押金和总额
        new_total_amount = order['total_rent'] + new_total_deposit
        db.execute_update(
            "UPDATE orders SET total_deposit = %s, total_amount = %s WHERE id = %s",
            (new_total_deposit, new_total_amount, request.order_id)
        )

        db.commit()
        write_order_audit(
            order_id=request.order_id,
            action="update_items",
            operator_role=str(admin.get("role", "admin")),
            operator_id=int(admin.get("id")) if admin.get("id") is not None else None,
            request_id=x_request_id,
            amount=None,
            reason=None,
            before_status=int(order.get('status', 0)),
            after_status=int(order.get('status', 0)),
            extra={
                "before_items": [{"product_id": i.get("product_id"), "size": i.get("size"), "color": i.get("color")} for i in (before_items or [])],
                "after_items": [{"product_id": i.get("product_id"), "size": i.get("size"), "color": i.get("color")} for i in request.items],
            },
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"修改订单失败: {str(e)}")

    return {"code": 0, "message": "订单衣物已更新"}


class PackageEligibleRequest(BaseModel):
    is_package_eligible: bool


@router.get("/package/products")
async def get_package_products(
    eligible: Optional[bool] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    authorization: Optional[str] = Header(None)
):
    require_admin(authorization)
    conditions = []
    params = []

    if eligible is not None:
        conditions.append("p.is_package_eligible = %s")
        params.append(1 if eligible else 0)

    if keyword:
        conditions.append("p.name LIKE %s")
        params.append(f"%{keyword}%")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    total_result = db.execute_one(
        f"SELECT COUNT(*) as total FROM products p {where_clause}",
        tuple(params)
    )
    total = total_result['total'] if total_result else 0

    offset = (page - 1) * page_size
    params.extend([page_size, offset])
    products = db.execute_query(
        f"""SELECT p.id, p.name, p.main_image, p.deposit
            FROM products p
            {where_clause}
            ORDER BY p.id DESC
            LIMIT %s OFFSET %s""",
        tuple(params)
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "list": [
                {
                    "id": p['id'],
                    "name": p['name'],
                    "main_image": p['main_image'],
                    "deposit": float(p['deposit']),
                }
                for p in products
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.put("/package/products/{product_id}")
async def set_package_product_eligible(
    product_id: int,
    request: PackageEligibleRequest,
    authorization: Optional[str] = Header(None)
):
    require_admin(authorization)

    product = db.execute_one("SELECT id FROM products WHERE id = %s", (product_id,))
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    db.execute_update(
        "UPDATE products SET is_package_eligible = %s WHERE id = %s",
        (1 if request.is_package_eligible else 0, product_id)
    )

    return {"code": 0, "message": "更新成功", "data": {"id": product_id, "is_package_eligible": request.is_package_eligible}}
