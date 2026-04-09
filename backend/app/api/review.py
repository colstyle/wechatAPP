# -*- coding: utf-8 -*-
"""
评价晒图相关API
"""
from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
from database import db

router = APIRouter()


# ============ 请求模型 ============

class CreateReviewRequest(BaseModel):
    """创建评价请求"""
    product_id: int
    order_id: Optional[int] = None
    rating: int  # 1-5
    content: str
    images: Optional[List[str]] = None
    is_anonymous: bool = False


# ============ 评价API ============

@router.post("/reviews")
async def create_review(request: CreateReviewRequest, authorization: Optional[str] = Header(None)):
    """
    创建评价
    """
    # TODO: 从 authorization 解析 token 并获取 user_id
    user_id = 1

    # 验证评分
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="评分必须在1-5之间")

    # 检查商品是否存在
    product = db.execute_one(
        "SELECT * FROM products WHERE id = %s AND status = 1",
        (request.product_id,)
    )
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 如果指定了订单，检查订单是否存在且属于该用户
    order = None
    if request.order_id:
        order = db.execute_one(
            "SELECT * FROM orders WHERE id = %s AND user_id = %s",
            (request.order_id, user_id)
        )
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        # 检查订单商品是否包含该商品
        order_item = db.execute_one(
            "SELECT id FROM order_items WHERE order_id = %s AND product_id = %s",
            (request.order_id, request.product_id)
        )
        if not order_item:
            raise HTTPException(status_code=400, detail="订单中不包含该商品")

        # 检查是否已评价
        exists = db.execute_one(
            "SELECT id FROM reviews WHERE user_id = %s AND product_id = %s AND order_id = %s",
            (user_id, request.product_id, request.order_id)
        )
        if exists:
            raise HTTPException(status_code=400, detail="该订单商品已评价")

    # 检查是否已评价过该商品
    exists = db.execute_one(
        "SELECT id FROM reviews WHERE user_id = %s AND product_id = %s",
        (user_id, request.product_id)
    )
    if exists:
        raise HTTPException(status_code=400, detail="您已评价过该商品")

    # 创建评价
    review_id = db.execute_insert(
        """INSERT INTO reviews (user_id, product_id, order_id, rating, content, images, is_anonymous, created_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())""",
        (user_id, request.product_id, request.order_id, request.rating,
         request.content, json.dumps(request.images or []), request.is_anonymous)
    )

    return {
        "code": 0,
        "message": "评价成功",
        "data": {"review_id": review_id}
    }


@router.get("/reviews")
async def get_reviews(
    product_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    获取商品评价列表
    """
    # 检查商品是否存在
    product = db.execute_one(
        "SELECT * FROM products WHERE id = %s AND status = 1",
        (product_id,)
    )
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 查询总数
    count_sql = "SELECT COUNT(*) as total FROM reviews WHERE product_id = %s"
    total_result = db.execute_one(count_sql, (product_id,))
    total = total_result['total'] if total_result else 0

    # 查询评价列表
    offset = (page - 1) * page_size
    list_sql = """
        SELECT r.*, u.nickname, u.avatar
        FROM reviews r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.product_id = %s
        ORDER BY r.created_at DESC
        LIMIT %s OFFSET %s
    """

    reviews = db.execute_query(list_sql, (product_id, page_size, offset))

    # 计算平均评分
    avg_sql = "SELECT AVG(rating) as avg_rating FROM reviews WHERE product_id = %s"
    avg_result = db.execute_one(avg_sql, (product_id,))
    avg_rating = round(float(avg_result['avg_rating']), 1) if avg_result and avg_result['avg_rating'] else 0

    # 评分分布
    rating_sql = """
        SELECT rating, COUNT(*) as count
        FROM reviews
        WHERE product_id = %s
        GROUP BY rating
        ORDER BY rating DESC
    """
    ratings = db.execute_query(rating_sql, (product_id,))
    rating_distribution = {r['rating']: r['count'] for r in ratings}

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "list": [
                {
                    "id": r['id'],
                    "user_id": r['user_id'],
                    "user": {
                        "nickname": r['nickname'] if not r['is_anonymous'] else "匿名用户",
                        "avatar": r['avatar'] if not r['is_anonymous'] else ""
                    } if not r['is_anonymous'] else {
                        "nickname": "匿名用户",
                        "avatar": ""
                    },
                    "rating": r['rating'],
                    "content": r['content'],
                    "images": json.loads(r['images']) if r['images'] else [],
                    "is_anonymous": r['is_anonymous'],
                    "created_at": r['created_at'].isoformat() if r['created_at'] else None
                }
                for r in reviews
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "summary": {
                "avg_rating": avg_rating,
                "total_reviews": total,
                "rating_5": rating_distribution.get(5, 0),
                "rating_4": rating_distribution.get(4, 0),
                "rating_3": rating_distribution.get(3, 0),
                "rating_2": rating_distribution.get(2, 0),
                "rating_1": rating_distribution.get(1, 0)
            }
        }
    }


@router.get("/reviews/{review_id}")
async def get_review(review_id: int):
    """
    获取评价详情
    """
    review = db.execute_one(
        """SELECT r.*, u.nickname, u.avatar
           FROM reviews r
           LEFT JOIN users u ON r.user_id = u.id
           WHERE r.id = %s""",
        (review_id,)
    )

    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")

    # 获取商品信息
    product = db.execute_one(
        "SELECT id, name, cover_image FROM products WHERE id = %s",
        (review['product_id'],)
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": review['id'],
            "user": {
                "nickname": review['nickname'] if not review['is_anonymous'] else "匿名用户",
                "avatar": review['avatar'] if not review['is_anonymous'] else ""
            },
            "product": product,
            "rating": review['rating'],
            "content": review['content'],
            "images": json.loads(review['images']) if review['images'] else [],
            "is_anonymous": review['is_anonymous'],
            "created_at": review['created_at'].isoformat() if review['created_at'] else None
        }
    }


@router.get("/reviews/my")
async def get_my_reviews(
    token: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    获取我的评价列表
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询总数
    count_sql = "SELECT COUNT(*) as total FROM reviews WHERE user_id = %s"
    total_result = db.execute_one(count_sql, (user_id,))
    total = total_result['total'] if total_result else 0

    # 查询评价列表
    offset = (page - 1) * page_size
    list_sql = """
        SELECT r.*, p.name as product_name, p.cover_image as product_image
        FROM reviews r
        LEFT JOIN products p ON r.product_id = p.id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
        LIMIT %s OFFSET %s
    """

    reviews = db.execute_query(list_sql, (user_id, page_size, offset))

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "list": [
                {
                    "id": r['id'],
                    "product_id": r['product_id'],
                    "product_name": r['product_name'],
                    "product_image": r['product_image'],
                    "rating": r['rating'],
                    "content": r['content'],
                    "images": json.loads(r['images']) if r['images'] else [],
                    "is_anonymous": r['is_anonymous'],
                    "order_id": r['order_id'],
                    "created_at": r['created_at'].isoformat() if r['created_at'] else None
                }
                for r in reviews
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.delete("/reviews/{review_id}")
async def delete_review(review_id: int, token: str):
    """
    删除评价
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 检查评价是否存在且属于该用户
    review = db.execute_one(
        "SELECT * FROM reviews WHERE id = %s AND user_id = %s",
        (review_id, user_id)
    )

    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")

    # 删除评价
    db.execute_update(
        "DELETE FROM reviews WHERE id = %s",
        (review_id,)
    )

    return {
        "code": 0,
        "message": "删除成功"
    }
