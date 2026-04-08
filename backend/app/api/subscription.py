# -*- coding: utf-8 -*-
"""
订阅相关API
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import time
import random
from database import db

router = APIRouter()


# ============ 请求模型 ============

class BuySubscriptionRequest(BaseModel):
    """购买订阅请求"""
    package_id: int


# ============ 工具函数 ============

def generate_subscription_no() -> str:
    """生成订阅号"""
    timestamp = str(int(time.time()))
    random_str = ''.join(random.choices('0123456789', k=6))
    return f"SUB{timestamp}{random_str}"


# ============ 订阅套餐API ============

@router.get("/packages")
async def get_packages():
    """
    获取订阅套餐列表
    """
    packages = db.execute_query(
        "SELECT * FROM subscription_packages WHERE is_active = TRUE ORDER BY days ASC"
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": [
            {
                "id": p['id'],
                "name": p['name'],
                "price": float(p['price']),
                "days": p['days'],
                "max_times": p['max_times'],
                "description": p['description']
            }
            for p in packages
        ]
    }


@router.get("/packages/{package_id}")
async def get_package(package_id: int):
    """
    获取订阅套餐详情
    """
    package = db.execute_one(
        "SELECT * FROM subscription_packages WHERE id = %s AND is_active = TRUE",
        (package_id,)
    )

    if not package:
        raise HTTPException(status_code=404, detail="套餐不存在")

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": package['id'],
            "name": package['name'],
            "price": float(package['price']),
            "days": package['days'],
            "max_times": package['max_times'],
            "description": package['description']
        }
    }


# ============ 订阅API ============

@router.post("/subscribe")
async def buy_subscription(request: BuySubscriptionRequest, token: str):
    """
    购买订阅
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询套餐
    package = db.execute_one(
        "SELECT * FROM subscription_packages WHERE id = %s AND is_active = TRUE",
        (request.package_id,)
    )

    if not package:
        raise HTTPException(status_code=404, detail="套餐不存在")

    # 检查是否已有激活中的订阅
    active_subscription = db.execute_one(
        """SELECT * FROM subscriptions
           WHERE user_id = %s AND status = 1
           ORDER BY end_date DESC LIMIT 1""",
        (user_id,)
    )

    if active_subscription:
        raise HTTPException(status_code=400, detail="您已有激活中的订阅")

    # 生成订阅号
    subscription_no = generate_subscription_no()

    # 计算起止日期
    start_date = date.today()
    end_date = start_date + timedelta(days=package['days'])
    remaining_times = package['max_times']

    # TODO: 调用微信支付
    # 这里简化处理，直接创建订阅

    # 创建订阅
    subscription_id = db.execute_insert(
        """INSERT INTO subscriptions (user_id, subscription_no, package_id, start_date, end_date,
           remaining_times, status, payment_time, created_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
        (user_id, subscription_no, request.package_id, start_date, end_date, remaining_times, 1)
    )

    return {
        "code": 0,
        "message": "订阅成功",
        "data": {
            "subscription_id": subscription_id,
            "subscription_no": subscription_no,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "remaining_times": remaining_times
        }
    }


@router.get("/subscriptions")
async def get_subscriptions(
    token: str,
    status: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    获取订阅列表
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
    count_sql = f"SELECT COUNT(*) as total FROM subscriptions WHERE {where_clause}"
    total_result = db.execute_one(count_sql, tuple(params))
    total = total_result['total'] if total_result else 0

    # 查询订阅列表
    offset = (page - 1) * page_size
    list_sql = f"""
        SELECT s.*, p.name as package_name, p.days, p.max_times, p.description
        FROM subscriptions s
        LEFT JOIN subscription_packages p ON s.package_id = p.id
        WHERE {where_clause}
        ORDER BY s.created_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([page_size, offset])

    subscriptions = db.execute_query(list_sql, tuple(params))

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "list": [
                {
                    "id": s['id'],
                    "subscription_no": s['subscription_no'],
                    "package_name": s['package_name'],
                    "package_id": s['package_id'],
                    "start_date": s['start_date'].isoformat() if s['start_date'] else None,
                    "end_date": s['end_date'].isoformat() if s['end_date'] else None,
                    "remaining_times": s['remaining_times'],
                    "status": s['status'],
                    "days": s['days'],
                    "max_times": s['max_times'],
                    "description": s['description'],
                    "payment_time": s['payment_time'].isoformat() if s['payment_time'] else None,
                    "created_at": s['created_at'].isoformat() if s['created_at'] else None
                }
                for s in subscriptions
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/subscriptions/active")
async def get_active_subscription(token: str):
    """
    获取激活中的订阅
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    subscription = db.execute_one(
        """SELECT s.*, p.name as package_name, p.days, p.max_times, p.description
           FROM subscriptions s
           LEFT JOIN subscription_packages p ON s.package_id = p.id
           WHERE s.user_id = %s AND s.status = 1 AND s.end_date >= CURDATE()
           ORDER BY s.end_date DESC LIMIT 1""",
        (user_id,)
    )

    if not subscription:
        return {
            "code": 0,
            "message": "获取成功",
            "data": None
        }

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": subscription['id'],
            "subscription_no": subscription['subscription_no'],
            "package_name": subscription['package_name'],
            "package_id": subscription['package_id'],
            "start_date": subscription['start_date'].isoformat() if subscription['start_date'] else None,
            "end_date": subscription['end_date'].isoformat() if subscription['end_date'] else None,
            "remaining_times": subscription['remaining_times'],
            "days": subscription['days'],
            "max_times": subscription['max_times'],
            "description": subscription['description'],
            "is_unlimited": subscription['max_times'] == 0
        }
    }


@router.post("/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(subscription_id: int, token: str):
    """
    取消订阅
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询订阅
    subscription = db.execute_one(
        "SELECT * FROM subscriptions WHERE id = %s AND user_id = %s",
        (subscription_id, user_id)
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="订阅不存在")

    if subscription['status'] != 1:
        raise HTTPException(status_code=400, detail="订阅状态不正确")

    # 更新状态为已取消
    db.execute_update(
        "UPDATE subscriptions SET status = 3 WHERE id = %s",
        (subscription_id,)
    )

    return {
        "code": 0,
        "message": "取消成功"
    }


# ============ 订阅租赁API ============

@router.post("/orders/subscription")
async def create_subscription_order(
    product_ids: list,
    subscription_id: Optional[int] = None,
    address_id: int = None,
    remark: Optional[str] = None,
    token: str = None
):
    """
    使用订阅创建订单
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 检查是否有激活的订阅
    active_subscription = db.execute_one(
        """SELECT * FROM subscriptions
           WHERE user_id = %s AND status = 1 AND end_date >= CURDATE()
           ORDER BY end_date DESC LIMIT 1""",
        (user_id,)
    )

    if not active_subscription:
        raise HTTPException(status_code=400, detail="没有激活的订阅，请先购买订阅")

    # 检查订阅次数
    if active_subscription['max_times'] > 0 and active_subscription['remaining_times'] <= 0:
        raise HTTPException(status_code=400, detail="订阅次数已用完")

    # 如果指定了subscription_id，验证是否匹配
    if subscription_id and subscription_id != active_subscription['id']:
        raise HTTPException(status_code=400, detail="订阅ID不正确")

    # 检查地址
    address = db.execute_one(
        "SELECT * FROM addresses WHERE id = %s AND user_id = %s",
        (address_id, user_id)
    )
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    # 获取商品信息
    products_query = "SELECT * FROM products WHERE id IN (%s)" % ','.join(['%s'] * len(product_ids))
    products = db.execute_query(products_query, tuple(product_ids))

    product_map = {p['id']: p for p in products}

    order_items = []

    for product_id in product_ids:
        product = product_map.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"商品ID {product_id} 不存在")

        if product['stock'] < 1:
            raise HTTPException(status_code=400, detail=f"商品 {product['name']} 库存不足")

        order_items.append({
            'product_id': product_id,
            'product_name': product['name'],
            'product_image': product['cover_image'],
            'size': '',
            'color': '',
            'rent_price': Decimal('0.00'),  # 订阅订单租金为0
            'deposit': Decimal(str(product['deposit'])),
            'quantity': 1
        })

    # 计算押金
    total_deposit = sum(item['deposit'] for item in order_items)

    # 生成订单号
    from app.api.order import generate_order_no
    order_no = generate_order_no()

    # 创建订单
    db.begin_transaction()
    try:
        order_id = db.execute_insert(
            """INSERT INTO orders (order_no, user_id, rental_type, total_rent, total_deposit, total_amount,
               rent_days, start_date, end_date, address_id, status, remark, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
            (order_no, user_id, 3, Decimal('0.00'), total_deposit, total_deposit, 0, None, None,
             address_id, 0, remark)
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

        # 扣减库存
        for product_id in product_ids:
            db.execute_update(
                "UPDATE products SET stock = stock - 1 WHERE id = %s",
                (product_id,)
            )

        # 扣减订阅次数
        if active_subscription['max_times'] > 0:
            db.execute_update(
                "UPDATE subscriptions SET remaining_times = remaining_times - %s WHERE id = %s",
                (len(product_ids), active_subscription['id'])
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
            "total_deposit": float(total_deposit),
            "subscription_id": active_subscription['id'],
            "remaining_times": active_subscription['remaining_times'] - len(product_ids)
        }
    }
