# -*- coding: utf-8 -*-
"""
订单相关API
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date, timedelta
from decimal import Decimal
import json
import time
import random
from database import db

router = APIRouter()


# ============ 请求模型 ============

class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    rental_type: int  # 1按天 2按次 3订阅 4单品租赁 5套餐租赁
    items: List[dict]  # 商品列表 [{"product_id": 1, "size": "M", "color": "白色", "quantity": 1}]
    rent_days: Optional[int] = None  # 租赁天数(按天模式需要)
    start_date: Optional[str] = None  # 开始日期 (租赁模式需要)
    address_id: int
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
    rent_price: float
    deposit: float
    quantity: int


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    order_no: str
    rental_type: int
    total_rent: float
    total_deposit: float
    total_amount: float
    rent_days: int
    start_date: str
    end_date: str
    status: int
    address: dict
    items: list


# ============ 工具函数 ============

def generate_order_no() -> str:
    """生成订单号"""
    timestamp = str(int(time.time()))
    random_str = ''.join(random.choices('0123456789', k=6))
    return f"RC{timestamp}{random_str}"


# ============ 订单API ============

@router.post("/orders")
async def create_order(request: CreateOrderRequest, token: str):
    """
    创建订单
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 检查地址是否存在且属于该用户
    address = db.execute_one(
        "SELECT * FROM addresses WHERE id = %s AND user_id = %s",
        (request.address_id, user_id)
    )
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    # 获取商品信息并计算金额
    product_ids = [item['product_id'] for item in request.items]
    products_query = "SELECT * FROM products WHERE id IN (%s)" % ','.join(['%s'] * len(product_ids))
    products = db.execute_query(products_query, tuple(product_ids))

    product_map = {p['id']: p for p in products}

    total_rent = Decimal('0.00')
    total_deposit = Decimal('0.00')
    order_items = []

    # 特殊处理租赁类型
    if request.rental_type in [2, 4, 5]:  # 单次租赁或单品/套餐租赁，按日期锁定
        if not request.start_date:
            raise HTTPException(status_code=400, detail="租赁模式需要选择开始日期")
        start_date = datetime.strptime(request.start_date, '%Y-%m-%d').date()
        rent_days = 1  # 固定24小时
        if request.rental_type == 5:  # 套餐租赁
            if len(request.items) != 3:
                raise HTTPException(status_code=400, detail="套餐租赁需要选择3件商品")
            total_rent = Decimal('69.90')  # 固定租金
    else:
        start_date = None
        rent_days = request.rent_days or 0

    for item in request.items:
        product = product_map.get(item['product_id'])
        if not product:
            raise HTTPException(status_code=404, detail=f"商品ID {item['product_id']} 不存在")

        # 计算租金和押金
        rent_price = Decimal('0.00')
        deposit = Decimal(str(product['deposit']))

        if request.rental_type == 1:  # 按天
            if not request.rent_days or request.rent_days < 1:
                raise HTTPException(status_code=400, detail="请选择租赁天数")
            rent_price = Decimal(str(product['daily_rent'])) * request.rent_days
        if request.rental_type == 2:  # 按次 / 单次租赁
            rent_price = Decimal(str(product['single_rent']))
        elif request.rental_type == 3:  # 订阅
            rent_price = Decimal(str(product['month_card_rent']))
        elif request.rental_type in [4, 5]:  # 租赁模式
            if request.rental_type == 4:  # 单品租赁
                rent_price = Decimal(str(product['daily_rent']))  # 按日租金算24小时
            # 套餐租金已设置

        if request.rental_type not in [5]:  # 非套餐模式累加租金
            total_rent += rent_price * item['quantity']
        total_deposit += deposit * item['quantity']

        order_items.append({
            'product_id': item['product_id'],
            'product_name': product['name'],
            'product_image': product['cover_image'],
            'size': item.get('size', ''),
            'color': item.get('color', ''),
            'rent_price': rent_price,
            'deposit': deposit,
            'quantity': item['quantity']
        })

    total_amount = total_rent + total_deposit

    # 计算起止日期
    end_date = None
    if start_date:
        from datetime import timedelta
        end_date = start_date + timedelta(days=rent_days)

    # 检查日期锁定（租赁类型2/4/5）
    if request.rental_type in [2, 4, 5]:
        for item in request.items:
            # 检查是否已被预订
            existing = db.execute_one(
                "SELECT id FROM reservations WHERE product_id = %s AND reserved_date = %s",
                (item['product_id'], start_date)
            )
            if existing:
                raise HTTPException(status_code=400, detail=f"商品 {product_map[item['product_id']]['name']} 在 {request.start_date} 已被预订")

    # 生成订单号
    order_no = generate_order_no()

    # 创建订单
    db.begin_transaction()
    try:
        order_id = db.execute_insert(
            """INSERT INTO orders (order_no, user_id, rental_type, total_rent, total_deposit, total_amount,
               rent_days, start_date, end_date, address_id, status, remark, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
            (order_no, user_id, request.rental_type, total_rent, total_deposit, total_amount,
             rent_days, start_date, end_date, request.address_id, 0, request.remark)
        )

        # 创建订单商品
        for item in order_items:
            db.execute_insert(
                """INSERT INTO order_items (order_id, product_id, product_name, product_image, size, color,
                   rent_price, deposit, quantity, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
                (order_id, item['product_id'], item['product_name'], item['product_image'],
                 item['size'], item['color'], item['rent_price'], item['deposit'], item['quantity'])
            )

        # 日期锁定订单：锁定日期而不是扣库存
        if request.rental_type in [2, 4, 5]:
            for item in request.items:
                db.execute_insert(
                    "INSERT INTO reservations (product_id, reserved_date, order_id, created_at) VALUES (%s, %s, %s, NOW())",
                    (item['product_id'], start_date, order_id)
                )
        else:
            # 原有模式：扣减库存
            for item in request.items:
                db.execute_update(
                    "UPDATE products SET stock = stock - %s WHERE id = %s",
                    (item['quantity'], item['product_id'])
                )

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")

    return {
        "code": 0,
        "message": "订单创建成功",
        "data": {
            "order_id": order_id,
            "order_no": order_no,
            "total_amount": float(total_amount),
            "total_rent": float(total_rent),
            "total_deposit": float(total_deposit)
        }
    }


@router.get("/orders")
async def get_orders(
    token: str,
    status: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    获取订单列表
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 构建查询条件
    conditions = ["user_id = %s"]
    params = [user_id]

    if status is not None:
        conditions.append("status = %s")
        params.append(status)

    where_clause = " AND ".join(conditions)

    # 查询总数
    count_sql = f"SELECT COUNT(*) as total FROM orders WHERE {where_clause}"
    total_result = db.execute_one(count_sql, tuple(params))
    total = total_result['total'] if total_result else 0

    # 查询订单列表
    offset = (page - 1) * page_size
    list_sql = f"""
        SELECT o.*, a.receiver_name, a.receiver_phone, a.province, a.city, a.district, a.detail_address
        FROM orders o
        LEFT JOIN addresses a ON o.address_id = a.id
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
                "rent_price": float(item['rent_price']),
                "deposit": float(item['deposit']),
                "quantity": item['quantity']
            })

    status_text_map = {
        0: '待支付',
        1: '待取衣',
        2: '租赁中',
        3: '待归还',
        4: '已归还',
        5: '已取消',
        6: '已退款',
        7: '已完成'
    }

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "list": [
                {
                    "id": o['id'],
                    "order_no": o['order_no'],
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
                    "address": {
                        "receiver_name": o['receiver_name'],
                        "receiver_phone": o['receiver_phone'],
                        "province": o['province'],
                        "city": o['city'],
                        "district": o['district'],
                        "detail_address": o['detail_address']
                    } if o['receiver_name'] else None,
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
async def get_order(order_id: int, token: str):
    """
    获取订单详情
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询订单
    order = db.execute_one(
        """SELECT o.*, a.receiver_name, a.receiver_phone, a.province, a.city, a.district, a.detail_address
           FROM orders o
           LEFT JOIN addresses a ON o.address_id = a.id
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
            "order_no": order['order_no'],
            "rental_type": order['rental_type'],
            "total_rent": float(order['total_rent']),
            "total_deposit": float(order['total_deposit']),
            "total_amount": float(order['total_amount']),
            "rent_days": order['rent_days'],
            "start_date": order['start_date'].isoformat() if order['start_date'] else None,
            "end_date": order['end_date'].isoformat() if order['end_date'] else None,
            "pickup_time": order['pickup_time'].isoformat() if order['pickup_time'] else None,
            "expected_return_time": order['expected_return_time'].isoformat() if order['expected_return_time'] else None,
            "door_lock_password": order['door_lock_password'],
            "overdue_duration": order['overdue_duration'],
            "status": order['status'],
            "address": {
                "receiver_name": order['receiver_name'],
                "receiver_phone": order['receiver_phone'],
                "province": order['province'],
                "city": order['city'],
                "district": order['district'],
                "detail_address": order['detail_address']
            } if order['receiver_name'] else None,
            "items": [
                {
                    "id": item['id'],
                    "product_id": item['product_id'],
                    "product_name": item['product_name'],
                    "product_image": item['product_image'],
                    "size": item['size'],
                    "color": item['color'],
                    "rent_price": float(item['rent_price']),
                    "deposit": float(item['deposit']),
                    "quantity": item['quantity']
                }
                for item in items
            ],
            "payment_time": order['payment_time'].isoformat() if order['payment_time'] else None,
            "ship_time": order['ship_time'].isoformat() if order['ship_time'] else None,
            "receive_time": order['receive_time'].isoformat() if order['receive_time'] else None,
            "return_time": order['return_time'].isoformat() if order['return_time'] else None,
            "refund_time": order['refund_time'].isoformat() if order['refund_time'] else None,
            "refund_amount": float(order['refund_amount']) if order['refund_amount'] else 0,
            "remark": order['remark'],
            "created_at": order['created_at'].isoformat() if order['created_at'] else None
        }
    }


@router.post("/orders/{order_id}/pay")
async def pay_order(order_id: int, token: str):
    """
    支付订单
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询订单
    order = db.execute_one(
        "SELECT * FROM orders WHERE id = %s AND user_id = %s",
        (order_id, user_id)
    )

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order['status'] != 0:
        raise HTTPException(status_code=400, detail="订单状态不正确")

    # TODO: 调用微信支付
    # 这里简化处理，直接标记为已支付

    # 生成门锁密码（租赁订单）
    door_password = None
    expected_return_time = None
    new_status = 1  # 默认已支付
    if order['rental_type'] in [2, 4, 5]:
        # 生成6位数字密码
        door_password = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        expected_return_time = datetime.now() + timedelta(hours=24)
        new_status = 1  # 已支付待取衣

    # 更新订单状态
    update_fields = ["status = %s", "payment_time = NOW()"]
    update_values = [new_status]

    if door_password:
        update_fields.append("door_lock_password = %s")
        update_values.append(door_password)

    if expected_return_time:
        update_fields.append("expected_return_time = %s")
        update_values.append(expected_return_time)

    update_sql = f"UPDATE orders SET {', '.join(update_fields)} WHERE id = %s"
    update_values.append(order_id)

    db.execute_update(update_sql, tuple(update_values))

    # 增加商品租赁次数
    items = db.execute_query("SELECT product_id, quantity FROM order_items WHERE order_id = %s", (order_id,))
    for item in items:
        db.execute_update(
            "UPDATE products SET rent_count = rent_count + %s WHERE id = %s",
            (item['quantity'], item['product_id'])
        )

    return {
        "code": 0,
        "message": "支付成功",
        "data": {"order_id": order_id, "status": 1}
    }


@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: int, token: str):
    """
    取消订单
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询订单
    order = db.execute_one(
        "SELECT * FROM orders WHERE id = %s AND user_id = %s",
        (order_id, user_id)
    )

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order['status'] not in [0, 1]:
        raise HTTPException(status_code=400, detail="订单状态不允许取消")

    # 更新订单状态
    db.begin_transaction()
    try:
        db.execute_update(
            "UPDATE orders SET status = 5 WHERE id = %s",
            (order_id,)
        )

        # 恢复库存或释放预订
        items = db.execute_query("SELECT product_id, quantity FROM order_items WHERE order_id = %s", (order_id,))
        if order['rental_type'] in [2, 4, 5]:
            # 释放日期预订
            db.execute_delete("DELETE FROM reservations WHERE order_id = %s", (order_id,))
        else:
            for item in items:
                db.execute_update(
                    "UPDATE products SET stock = stock + %s WHERE id = %s",
                    (item['quantity'], item['product_id'])
                )

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"取消订单失败: {str(e)}")

    return {
        "code": 0,
        "message": "取消成功"
    }


@router.post("/orders/{order_id}/ship")
async def ship_order(order_id: int, token: str):
    """
    发货（管理员接口）
    """
    # 查询订单
    order = db.execute_one(
        "SELECT * FROM orders WHERE id = %s",
        (order_id,)
    )

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order['status'] != 1:
        raise HTTPException(status_code=400, detail="订单状态不正确")

    # 更新订单状态
    db.execute_update(
        """UPDATE orders SET status = 2, ship_time = NOW()
           WHERE id = %s""",
        (order_id,)
    )

    return {
        "code": 0,
        "message": "发货成功"
    }


@router.post("/orders/{order_id}/receive")
async def receive_order(order_id: int, token: str):
    """
    确认收货
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询订单
    order = db.execute_one(
        "SELECT * FROM orders WHERE id = %s AND user_id = %s",
        (order_id, user_id)
    )

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order['status'] != 2:
        raise HTTPException(status_code=400, detail="订单状态不正确")

    # 更新订单状态
    db.execute_update(
        """UPDATE orders SET status = 3, receive_time = NOW()
           WHERE id = %s""",
        (order_id,)
    )

    return {
        "code": 0,
        "message": "确认收货成功"
    }


@router.post("/orders/{order_id}/pickup")
async def pickup_order(order_id: int, request: PickupOrderRequest, token: str):
    """
    取衣确认
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询订单
    order = db.execute_one(
        "SELECT * FROM orders WHERE id = %s AND user_id = %s",
        (order_id, user_id)
    )

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order['status'] != 1 or order['rental_type'] not in [2, 4, 5]:
        raise HTTPException(status_code=400, detail="订单状态不正确")

    # 更新订单状态
    db.execute_update(
        """UPDATE orders SET status = 2, pickup_time = NOW(), remark = CONCAT(COALESCE(remark, ''), '\n', %s)
           WHERE id = %s""",
        (request.remark or "用户已取衣", order_id)
    )

    return {
        "code": 0,
        "message": "取衣确认成功"
    }


@router.post("/orders/{order_id}/return")
async def return_order(order_id: int, request: ReturnOrderRequest, token: str):
    """
    申请归还
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询订单
    order = db.execute_one(
        "SELECT * FROM orders WHERE id = %s AND user_id = %s",
        (order_id, user_id)
    )

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order['status'] != 2:
        raise HTTPException(status_code=400, detail="订单状态不正确")

    # 更新订单状态
    db.execute_update(
        """UPDATE orders SET status = 3, remark = CONCAT(COALESCE(remark, ''), '\n', %s)
           WHERE id = %s""",
        (request.remark or "用户已还衣", order_id)
    )

    return {
        "code": 0,
        "message": "申请归还成功"
    }


@router.post("/orders/{order_id}/refund")
async def refund_order(order_id: int, token: str):
    """
    退款押金（管理员接口）
    """
    # 查询订单
    order = db.execute_one(
        "SELECT * FROM orders WHERE id = %s",
        (order_id,)
    )

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order['status'] != 4:
        raise HTTPException(status_code=400, detail="订单状态不正确")

    if order['refund_amount'] > 0:
        raise HTTPException(status_code=400, detail="已退款")

    # TODO: 调用微信支付退款

    # 更新订单状态
    db.begin_transaction()
    try:
        # 退还押金
        refund_amount = order['total_deposit']
        db.execute_update(
            """UPDATE orders SET status = 6, refund_amount = %s, refund_time = NOW()
               WHERE id = %s""",
            (refund_amount, order_id)
        )

        # 恢复库存或释放预订
        items = db.execute_query("SELECT product_id, quantity FROM order_items WHERE order_id = %s", (order_id,))
        if order['rental_type'] in [2, 4, 5]:
            db.execute_delete("DELETE FROM reservations WHERE order_id = %s", (order_id,))
        else:
            for item in items:
                db.execute_update(
                    "UPDATE products SET stock = stock + %s WHERE id = %s",
                    (item['quantity'], item['product_id'])
                )

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"退款失败: {str(e)}")

    return {
        "code": 0,
        "message": "退款成功",
        "data": {"refund_amount": float(refund_amount)}
    }


@router.post("/admin/orders/{order_id}/confirm-return")
async def admin_confirm_return(order_id: int):
    """
    管理员确认还衣
    """
    # 查询订单
    order = db.execute_one(
        "SELECT * FROM orders WHERE id = %s",
        (order_id,)
    )

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order['status'] != 3:
        raise HTTPException(status_code=400, detail="订单状态不正确")

    # 更新订单状态
    db.execute_update(
        """UPDATE orders SET status = 4, return_time = NOW()
           WHERE id = %s""",
        (order_id,)
    )

    return {
        "code": 0,
        "message": "确认还衣成功"
    }


@router.post("/admin/orders/{order_id}/resend-password")
async def admin_resend_password(order_id: int):
    """
    管理员重新发送门锁密码
    """
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
