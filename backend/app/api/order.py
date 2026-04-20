# -*- coding: utf-8 -*-
"""
订单相关API
"""
from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date, timedelta
from decimal import Decimal
import json
import time
import random
from database import db
from app.utils.auth import get_current_user, require_admin
from app.utils.audit import write_order_audit

router = APIRouter()


# ============ 请求模型 ============

class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    rental_type: int  # 1按天 2按次 3订阅 4单品租赁 5套餐租赁
    items: List[dict]  # 商品列表 [{"product_id": 1, "size": "M", "color": "白色", "quantity": 1}]
    rent_days: Optional[int] = None  # 租赁天数(按天模式需要)
    start_date: Optional[str] = None  # 开始日期 (租赁模式需要)
    remark: Optional[str] = None


class PayOrderRequest(BaseModel):
    """支付订单请求"""
    # 支付相关参数
    pass


class ReturnOrderRequest(BaseModel):
    """归还订单请求"""
    remark: Optional[str] = None


class PickupOrderRequest(BaseModel):
    """取衣请求"""
    remark: Optional[str] = None


# ============ 响应模型 ============

class OrderItemResponse(BaseModel):
    """订单商品响应"""
    id: int
    product_id: int
    product_name: str
    product_image: str
    size: str
    color: str
    price: float
    deposit: float
    quantity: int


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    order_sn: str
    rental_type: int
    total_rent: float
    total_deposit: float
    total_amount: float
    rent_days: int
    start_date: str
    end_date: str
    status: int
    items: list


# ============ 工具函数 ============

def generate_order_no() -> str:
    """生成订单号"""
    timestamp = str(int(time.time()))
    random_str = ''.join(random.choices('0123456789', k=6))
    return f"RC{timestamp}{random_str}"


# ============ 订单API ============

@router.post("/orders")
async def create_order(
    request: CreateOrderRequest,
    authorization: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    创建订单 (租赁)
    """
    user = get_current_user(authorization)
    user_id = user['id']

    # 核心规则：必须有开始日期
    if not request.start_date:
        raise HTTPException(status_code=400, detail="必须选择使用日期")
    
    start_date = datetime.strptime(request.start_date, '%Y-%m-%d').date()

    # 获取商品信息
    product_ids = [item['product_id'] for item in request.items]
    products_query = "SELECT * FROM products WHERE id IN (%s)" % ','.join(['%s'] * len(product_ids))
    products = db.execute_query(products_query, tuple(product_ids))
    product_map = {p['id']: p for p in products}

    total_rent = Decimal('0.00')
    total_deposit = Decimal('0.00')
    order_items = []

    # ===== 套餐服务端校验（type=5：3件69.9元）=====
    if request.rental_type == 5:
        if len(request.items) != 3:
            raise HTTPException(status_code=400, detail="套餐必须选择3件衣物")
        # 防止同一件衣物重复加入套餐
        item_ids = [i['product_id'] for i in request.items]
        if len(item_ids) != len(set(item_ids)):
            raise HTTPException(status_code=400, detail="套餐中不能重复选择同一件衣物")
        total_rent = Decimal('69.90')

    for item in request.items:
        product = product_map.get(item['product_id'])
        if not product:
            raise HTTPException(status_code=404, detail=f"商品ID {item['product_id']} 不存在")

        # 套餐资格服务端强校验
        if request.rental_type == 5 and not bool(product.get('is_package_eligible')):
            raise HTTPException(status_code=400, detail=f"衣物《{product['name']}》不参与套餐活动")

        # 检查日期锁定：同一日期同一件衣服仅支持一单
        existing = db.execute_one(
            "SELECT id FROM reservations WHERE product_id = %s AND reserved_date = %s",
            (item['product_id'], start_date)
        )
        if existing:
            raise HTTPException(status_code=400, detail=f"衣物《{product['name']}》在 {request.start_date} 已被预订")

        # ===== 快照固化：下单时记录当前价格，与商品表解耦 =====
        # 后续修改商品价格不影响历史订单金额
        snapshot_price   = Decimal(str(product.get('price', 0)))
        snapshot_deposit = Decimal(str(product.get('deposit', 0)))
        snapshot_image   = product.get('main_image') or ''

        deposit = snapshot_deposit
        total_deposit += deposit * item.get('quantity', 1)

        if request.rental_type != 5:
            rent_price  = snapshot_price
            total_rent += rent_price * item.get('quantity', 1)
        else:
            rent_price = Decimal('0.00')  # 套餐模式：单品租金记为0，总额固定69.9

        order_items.append({
            'product_id':       item['product_id'],
            'product_name':     product['name'],
            'product_image':    snapshot_image,
            'snapshot_price':   snapshot_price,   # 价格快照
            'snapshot_deposit': snapshot_deposit, # 押金快照
            'size':             item.get('size', ''),
            'color':            item.get('color', ''),
            'price':            rent_price,
            'deposit':          deposit,
            'quantity':         item.get('quantity', 1)
        })

    total_amount = total_rent + total_deposit
    order_no = generate_order_no()
    
    # 租赁天数，默认为1天
    rent_days = request.rent_days or 1
    # 租赁结束日期 (24小时制在取衣时激活，这里预存一个日期)
    end_date = start_date + timedelta(days=rent_days)

    db.begin_transaction()
    try:
        order_sn = generate_order_no()
        order_id = db.execute_insert(
            """INSERT INTO orders (order_sn, user_id, rental_type, total_rent, total_deposit, total_amount,
               rent_days, start_date, end_date, status, remark, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
            (order_sn, user_id, request.rental_type, total_rent, total_deposit, total_amount,
             rent_days, start_date, end_date, 0, request.remark)
        )

        for item in order_items:
            # 尝试写入含快照字段的版本，若表中无该字段则回退（兼容旧表结构）
            db.execute_insert(
                """INSERT INTO order_items
                   (order_id, product_id, product_name, product_image,
                    price, deposit, quantity)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (order_id, item['product_id'], item['product_name'], item['product_image'],
                 item['price'], item['deposit'], item['quantity'])
            )
            # 锁定日期库存
            try:
                db.execute_insert(
                    "INSERT INTO reservations (product_id, reserved_date, order_id, created_at) VALUES (%s, %s, %s, NOW())",
                    (item['product_id'], start_date, order_id)
                )
            except Exception as e:
                msg = str(e)
                if "Duplicate entry" in msg or "1062" in msg:
                    raise HTTPException(status_code=400, detail=f"衣物《{item['product_name']}》在 {request.start_date} 已被预订")
                raise

        db.commit()
        write_order_audit(
            order_id=order_id,
            action="create",
            operator_role=str(user.get("role", "user")),
            operator_id=user_id,
            request_id=x_request_id,
            amount=float(total_amount),
            reason=request.remark,
            before_status=None,
            after_status=0,
            extra={"order_sn": order_sn, "rental_type": request.rental_type},
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")

    return {
        "code": 0,
        "message": "订单预定成功",
        "data": {
            "order_id": order_id,
            "order_sn": order_sn,
            "total_amount": float(total_amount),
            "total_deposit": float(total_deposit)
        }
    }

@router.post("/orders/{order_id}/pickup")
async def pickup_order(
    order_id: int,
    request: PickupOrderRequest,
    authorization: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    用户点击「我已取衣」：状态由「已预订/已支付」变为「租赁中」
    """
    user = get_current_user(authorization)
    user_id = user['id']

    now = datetime.now()
    order = db.execute_one(
        "SELECT * FROM orders WHERE id = %s AND user_id = %s",
        (order_id, user_id)
    )
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order['status'] == 2:
        return {
            "code": 0,
            "message": "取衣成功，24小时计时开始",
            "data": {
                "pickup_time": order['pickup_time'].isoformat() if order.get('pickup_time') else None,
                "expected_return_time": order['expected_return_time'].isoformat() if order.get('expected_return_time') else None
            }
        }

    if order['status'] != 1:
        raise HTTPException(status_code=400, detail="当前订单状态不可执行取衣操作")

    rent_hours = (order['rent_days'] or 1) * 24
    expected_return_time = now + timedelta(hours=rent_hours)

    affected = db.execute_update(
        """UPDATE orders SET 
           status = 2, 
           pickup_time = %s, 
           expected_return_time = %s,
           remark = %s
           WHERE id = %s AND user_id = %s AND status = 1""",
        (now, expected_return_time, request.remark or "用户已取衣", order_id, user_id)
    )
    if affected <= 0:
        latest = db.execute_one("SELECT * FROM orders WHERE id = %s AND user_id = %s", (order_id, user_id))
        if latest and latest.get('status') == 2:
            return {
                "code": 0,
                "message": "取衣成功，24小时计时开始",
                "data": {
                    "pickup_time": latest['pickup_time'].isoformat() if latest.get('pickup_time') else None,
                    "expected_return_time": latest['expected_return_time'].isoformat() if latest.get('expected_return_time') else None
                }
            }
        raise HTTPException(status_code=400, detail="当前订单状态不可执行取衣操作")

    write_order_audit(
        order_id=order_id,
        action="pickup",
        operator_role=str(user.get("role", "user")),
        operator_id=user_id,
        request_id=x_request_id,
        amount=None,
        reason=request.remark or "用户已取衣",
        before_status=1,
        after_status=2,
        extra={"expected_return_time": expected_return_time.isoformat()},
    )

    return {
        "code": 0,
        "message": "取衣成功，24小时计时开始",
        "data": {
            "pickup_time": now.isoformat(),
            "expected_return_time": expected_return_time.isoformat()
        }
    }


@router.post("/orders/{order_id}/return")
async def return_order(
    order_id: int,
    request: ReturnOrderRequest,
    authorization: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    用户点击「我已还衣」：状态由「租赁中」或「逾期」变为「已归还待审核」
    """
    user = get_current_user(authorization)
    user_id = user['id']

    now = datetime.now()
    order = db.execute_one(
        "SELECT * FROM orders WHERE id = %s AND user_id = %s",
        (order_id, user_id)
    )
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order['status'] == 4:
        return {
            "code": 0,
            "message": "归还申请成功，请等待店主核验",
            "data": {
                "return_time": order['return_time'].isoformat() if order.get('return_time') else None
            }
        }

    if order['status'] not in [2, 3]:
        raise HTTPException(status_code=400, detail="当前订单状态不可执行还衣操作")

    affected = db.execute_update(
        """UPDATE orders SET 
           status = 4, 
           return_time = %s,
           remark = %s
           WHERE id = %s AND user_id = %s AND status IN (2, 3)""",
        (now, request.remark or "用户已还衣，待店主审核", order_id, user_id)
    )
    if affected <= 0:
        latest = db.execute_one("SELECT * FROM orders WHERE id = %s AND user_id = %s", (order_id, user_id))
        if latest and latest.get('status') == 4:
            return {
                "code": 0,
                "message": "归还申请成功，请等待店主核验",
                "data": {
                    "return_time": latest['return_time'].isoformat() if latest.get('return_time') else None
                }
            }
        raise HTTPException(status_code=400, detail="当前订单状态不可执行还衣操作")

    write_order_audit(
        order_id=order_id,
        action="return",
        operator_role=str(user.get("role", "user")),
        operator_id=user_id,
        request_id=x_request_id,
        amount=None,
        reason=request.remark or "用户已还衣，待店主审核",
        before_status=int(order['status']),
        after_status=4,
        extra=None,
    )

    return {
        "code": 0,
        "message": "归还申请成功，请等待店主核验",
        "data": {
            "return_time": now.isoformat()
        }
    }


@router.get("/orders")
async def get_orders(
    status: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    authorization: Optional[str] = Header(None)
):
    """
    获取订单列表
    """
    user = get_current_user(authorization)
    user_id = user['id']

    # 构建查询条件
    conditions = ["o.user_id = %s"]
    params = [user_id]

    if status is not None:
        conditions.append("o.status = %s")
        params.append(status)

    where_clause = " AND ".join(conditions)

    # 查询总数
    count_sql = f"SELECT COUNT(*) as total FROM orders o WHERE {where_clause}"
    total_result = db.execute_one(count_sql, tuple(params))
    total = total_result['total'] if total_result else 0

    # 查询订单列表
    offset = (page - 1) * page_size
    list_sql = f"""
        SELECT o.*
        FROM orders o
        WHERE {where_clause}
        ORDER BY o.created_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([page_size, offset])

    orders = db.execute_query(list_sql, tuple(params))

    # 查询每个订单的商品
    order_ids = [o['id'] for o in orders]
    items_map = {}
    if order_ids:
        items_query = f"SELECT * FROM order_items WHERE order_id IN ({','.join(['%s'] * len(order_ids))})"
        items = db.execute_query(items_query, tuple(order_ids))

        for item in items:
            order_id = item['order_id']
            if order_id not in items_map:
                items_map[order_id] = []
            items_map[order_id].append({
                "id": item['id'],
                "product_id": item['product_id'],
                "product_name": item['product_name'],
                "product_image": item['product_image'],
                "size": item['size'],
                "color": item['color'],
                "price": float(item['price']),
                "deposit": float(item['deposit']),
                "quantity": item['quantity']
            })

    status_text_map = {
        0: '待支付',
        1: '待取衣',
        2: '租赁中',
        3: '已逾期',
        4: '待审核',
        5: '已取消',
        6: '退款中',
        7: '已完成'
    }

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "list": [
                {
                    "id": o['id'],
                    "order_sn": o['order_sn'],
                    "rental_type": o['rental_type'],
                    "total_rent": float(o['total_rent']),
                    "total_deposit": float(o['total_deposit']),
                    "total_amount": float(o['total_amount']),
                    "rent_days": o['rent_days'],
                    "start_date": o['start_date'].isoformat() if o['start_date'] else None,
                    "end_date": o['end_date'].isoformat() if o['end_date'] else None,
                    "expected_return_time": o['expected_return_time'].isoformat() if o['expected_return_time'] else None,
                    "door_lock_password": o['door_lock_password'],
                    "overdue_duration": o['overdue_duration'],
                    "status": o['status'],
                    "status_text": status_text_map.get(o['status'], '未知'),
                    "items": items_map.get(o['id'], []),
                    "payment_time": o['payment_time'].isoformat() if o['payment_time'] else None,
                    "ship_time": o['ship_time'].isoformat() if o['ship_time'] else None,
                    "receive_time": o['receive_time'].isoformat() if o['receive_time'] else None,
                    "return_time": o['return_time'].isoformat() if o['return_time'] else None,
                    "refund_time": o['refund_time'].isoformat() if o['refund_time'] else None,
                    "refund_amount": float(o['refund_amount']) if o['refund_amount'] else 0,
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
async def get_order(order_id: int, authorization: Optional[str] = Header(None)):
    """
    获取订单详情
    """
    user = get_current_user(authorization)
    user_id = user['id']

    # 查询订单
    order = db.execute_one(
        """SELECT o.*
           FROM orders o
           WHERE o.id = %s AND o.user_id = %s""",
        (order_id, user_id)
    )

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 自动检查逾期时长
    if order['status'] == 2 and order['expected_return_time']:
        now = datetime.now()
        if now > order['expected_return_time']:
            overdue_hours = int((now - order['expected_return_time']).total_seconds() / 3600)
            if overdue_hours != order.get('overdue_duration'):
                db.execute_update(
                    "UPDATE orders SET overdue_duration = %s WHERE id = %s",
                    (overdue_hours, order_id)
                )
            order['overdue_duration'] = overdue_hours

    # 查询订单商品
    items = db.execute_query(
        "SELECT * FROM order_items WHERE order_id = %s",
        (order_id,)
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": order['id'],
            "order_no": order.get('order_sn') or order.get('order_no', ''),
            "order_sn": order.get('order_sn') or order.get('order_no', ''),
            "rental_type": order['rental_type'],
            "total_rent": float(order.get('total_rent') or 0),
            "total_deposit": float(order.get('total_deposit') or 0),
            "total_amount": float(order.get('total_amount') or 0),
            "rent_days": order.get('rent_days'),
            "start_date": order['start_date'].isoformat() if order.get('start_date') else None,
            "end_date": order['end_date'].isoformat() if order.get('end_date') else None,
            "pickup_time": order['pickup_time'].isoformat() if order.get('pickup_time') else None,
            "expected_return_time": order['expected_return_time'].isoformat() if order.get('expected_return_time') else None,
            "door_lock_password": order.get('door_lock_password'),
            "overdue_duration": order.get('overdue_duration'),
            "status": order['status'],
            "items": [
                {
                    "id": item['id'],
                    "product_id": item['product_id'],
                    "product_name": item['product_name'],
                    "product_image": item.get('product_image'),
                    "size": item.get('size'),
                    "color": item.get('color'),
                    "rent_price": float(item.get('rent_price') or item.get('price') or 0),
                    "deposit": float(item.get('deposit') or 0),
                    "quantity": item.get('quantity', 1)
                }
                for item in items
            ],
            "payment_time": order['payment_time'].isoformat() if order.get('payment_time') else None,
            "ship_time": order['ship_time'].isoformat() if order.get('ship_time') else None,
            "receive_time": order['receive_time'].isoformat() if order.get('receive_time') else None,
            "return_time": order['return_time'].isoformat() if order.get('return_time') else None,
            "refund_time": order['refund_time'].isoformat() if order.get('refund_time') else None,
            "refund_amount": float(order['refund_amount']) if order.get('refund_amount') else 0,
            "remark": order.get('remark'),
            "created_at": order['created_at'].isoformat() if order.get('created_at') else None
        }
    }


@router.post("/orders/{order_id}/pay")
async def pay_order(
    order_id: int,
    authorization: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    支付订单
    """
    user = get_current_user(authorization)
    user_id = user['id']

    db.begin_transaction()
    try:
        order = db.execute_one(
            "SELECT * FROM orders WHERE id = %s AND user_id = %s FOR UPDATE",
            (order_id, user_id)
        )
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        if order['status'] == 5:
            raise HTTPException(status_code=400, detail="订单已取消")

        if order['status'] != 0:
            db.commit()
            return {
                "code": 0,
                "message": "已支付",
                "data": {"order_id": order_id, "status": int(order['status'])}
            }

        door_password = None
        expected_return_time = None
        new_status = 1
        if order['rental_type'] in [2, 4, 5]:
            door_password = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            expected_return_time = datetime.now() + timedelta(hours=24)
            new_status = 1

        update_fields = ["status = %s", "payment_time = NOW()"]
        update_values = [new_status]

        if door_password:
            update_fields.append("door_lock_password = %s")
            update_values.append(door_password)

        if expected_return_time:
            update_fields.append("expected_return_time = %s")
            update_values.append(expected_return_time)

        update_sql = f"UPDATE orders SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s AND status = 0"
        update_values.extend([order_id, user_id])

        affected = db.execute_update(update_sql, tuple(update_values))
        if affected <= 0:
            latest = db.execute_one("SELECT * FROM orders WHERE id = %s AND user_id = %s", (order_id, user_id))
            db.commit()
            if latest and int(latest.get('status', 0)) != 0:
                return {
                    "code": 0,
                    "message": "已支付",
                    "data": {"order_id": order_id, "status": int(latest['status'])}
                }
            raise HTTPException(status_code=400, detail="订单状态不正确")

        items = db.execute_query("SELECT product_id, quantity FROM order_items WHERE order_id = %s", (order_id,))
        for item in items:
            db.execute_update(
                "UPDATE products SET rent_count = rent_count + %s WHERE id = %s",
                (item['quantity'], item['product_id'])
            )

        db.commit()
        write_order_audit(
            order_id=order_id,
            action="pay",
            operator_role=str(user.get("role", "user")),
            operator_id=user_id,
            request_id=x_request_id,
            amount=float(order.get("total_amount") or 0),
            reason=None,
            before_status=0,
            after_status=new_status,
            extra={"door_lock_password": door_password, "expected_return_time": expected_return_time.isoformat() if expected_return_time else None},
        )

        return {
            "code": 0,
            "message": "支付成功",
            "data": {"order_id": order_id, "status": 1}
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"支付失败: {str(e)}")


@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    authorization: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    取消订单
    """
    user = get_current_user(authorization)
    user_id = user['id']

    # 查询订单
    order = db.execute_one(
        "SELECT * FROM orders WHERE id = %s AND user_id = %s",
        (order_id, user_id)
    )

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    db.begin_transaction()
    try:
        before_status = int(order.get('status', 0))
        affected = db.execute_update(
            "UPDATE orders SET status = 5 WHERE id = %s AND user_id = %s AND status IN (0, 1)",
            (order_id, user_id)
        )
        if affected <= 0:
            latest = db.execute_one("SELECT * FROM orders WHERE id = %s AND user_id = %s", (order_id, user_id))
            if latest and int(latest.get('status', 0)) == 5:
                db.commit()
                return {"code": 0, "message": "取消成功"}
            raise HTTPException(status_code=400, detail="订单状态不允许取消")

        db.execute_update("DELETE FROM reservations WHERE order_id = %s", (order_id,))
        db.commit()

        write_order_audit(
            order_id=order_id,
            action="cancel",
            operator_role=str(user.get("role", "user")),
            operator_id=user_id,
            request_id=x_request_id,
            amount=None,
            reason=None,
            before_status=before_status,
            after_status=5,
            extra=None,
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"取消订单失败: {str(e)}")

    return {
        "code": 0,
        "message": "取消成功"
    }


@router.post("/orders/{order_id}/ship")
async def ship_order(order_id: int, authorization: Optional[str] = Header(None)):
    """
    发货（管理员接口）
    """
    require_admin(authorization)
    raise HTTPException(status_code=400, detail="当前版本不支持发货流程")


@router.post("/orders/{order_id}/receive")
async def receive_order(order_id: int, authorization: Optional[str] = Header(None)):
    """
    确认收货
    """
    raise HTTPException(status_code=400, detail="当前版本不支持收货流程")


@router.post("/admin/orders/{order_id}/confirm-return")
async def admin_confirm_return(
    order_id: int,
    refund_amount: Optional[float] = None,
    authorization: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    店主核验无误，确认还衣：衣服自动恢复可租赁状态，一键退还押金
    """
    admin = require_admin(authorization)

    db.begin_transaction()
    try:
        order = db.execute_one("SELECT * FROM orders WHERE id = %s FOR UPDATE", (order_id,))
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        if int(order.get('status', 0)) == 7:
            db.commit()
            return {
                "code": 0,
                "message": "确认还衣成功，押金已原路退回",
                "data": {"refund_amount": float(order.get('refund_amount') or 0)}
            }

        if order['status'] != 4:
            raise HTTPException(status_code=400, detail="订单尚未申请还衣")

        final_refund = Decimal(str(refund_amount)) if refund_amount is not None else Decimal(str(order['total_deposit']))
        if final_refund <= 0:
            raise HTTPException(status_code=400, detail="退款金额必须大于0")
        if final_refund > Decimal(str(order['total_deposit'])):
            raise HTTPException(status_code=400, detail="退款金额不能超过总押金")

        affected = db.execute_update(
            "UPDATE orders SET status = 7, refund_amount = %s, refund_time = NOW() WHERE id = %s AND status = 4",
            (final_refund, order_id)
        )
        if affected <= 0:
            latest = db.execute_one("SELECT * FROM orders WHERE id = %s", (order_id,))
            db.commit()
            if latest and int(latest.get('status', 0)) == 7:
                return {
                    "code": 0,
                    "message": "确认还衣成功，押金已原路退回",
                    "data": {"refund_amount": float(latest.get('refund_amount') or 0)}
                }
            raise HTTPException(status_code=400, detail="订单尚未申请还衣")

        db.execute_update("DELETE FROM reservations WHERE order_id = %s", (order_id,))
        db.commit()

        write_order_audit(
            order_id=order_id,
            action="confirm_return",
            operator_role=str(admin.get("role", "admin")),
            operator_id=int(admin.get("id")) if admin.get("id") is not None else None,
            request_id=x_request_id,
            amount=float(final_refund),
            reason=None,
            before_status=4,
            after_status=7,
            extra=None,
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"确认还衣失败: {str(e)}")

    return {
        "code": 0,
        "message": "确认还衣成功，押金已原路退回",
        "data": {"refund_amount": float(final_refund)}
    }


@router.post("/orders/{order_id}/refund")
async def refund_order(
    order_id: int,
    authorization: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id"),
):
    """
    退款押金（管理员接口）
    """
    admin = require_admin(authorization)

    db.begin_transaction()
    try:
        order = db.execute_one("SELECT * FROM orders WHERE id = %s FOR UPDATE", (order_id,))
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        if int(order.get('status', 0)) == 7 and Decimal(str(order.get('refund_amount') or 0)) > 0:
            db.commit()
            return {
                "code": 0,
                "message": "退款成功",
                "data": {"refund_amount": float(order.get('refund_amount') or 0)}
            }

        if order['status'] != 4:
            raise HTTPException(status_code=400, detail="订单状态不正确")

        if Decimal(str(order.get('refund_amount') or 0)) > 0:
            db.commit()
            return {
                "code": 0,
                "message": "退款成功",
                "data": {"refund_amount": float(order.get('refund_amount') or 0)}
            }

        refund_amount = Decimal(str(order['total_deposit']))

        affected = db.execute_update(
            "UPDATE orders SET status = 6, refund_amount = %s, refund_time = NOW() WHERE id = %s AND status = 4",
            (refund_amount, order_id)
        )
        if affected <= 0:
            latest = db.execute_one("SELECT * FROM orders WHERE id = %s", (order_id,))
            db.commit()
            if latest and Decimal(str(latest.get('refund_amount') or 0)) > 0:
                return {
                    "code": 0,
                    "message": "退款成功",
                    "data": {"refund_amount": float(latest.get('refund_amount') or 0)}
                }
            raise HTTPException(status_code=400, detail="订单状态不正确")

        db.execute_update("DELETE FROM reservations WHERE order_id = %s", (order_id,))
        db.commit()

        write_order_audit(
            order_id=order_id,
            action="refund",
            operator_role=str(admin.get("role", "admin")),
            operator_id=int(admin.get("id")) if admin.get("id") is not None else None,
            request_id=x_request_id,
            amount=float(refund_amount),
            reason=None,
            before_status=4,
            after_status=6,
            extra=None,
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"退款失败: {str(e)}")

    return {
        "code": 0,
        "message": "退款成功",
        "data": {"refund_amount": float(refund_amount)}
    }


@router.post("/admin/orders/{order_id}/resend-password")
async def admin_resend_password(order_id: int, authorization: Optional[str] = Header(None)):
    """
    管理员重新发送门锁密码
    """
    require_admin(authorization)
    # 查询订单
    order = db.execute_one(
        "SELECT * FROM orders WHERE id = %s",
        (order_id,)
    )

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order['rental_type'] not in [4, 5]:
        raise HTTPException(status_code=400, detail="非租赁订单")

    # 生成新密码
    new_password = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    # 更新订单
    db.execute_update(
        "UPDATE orders SET door_lock_password = %s WHERE id = %s",
        (new_password, order_id)
    )

    # TODO: 发送密码到用户手机

    return {
        "code": 0,
        "message": "密码重新发送成功",
        "data": {"password": new_password}
    }
