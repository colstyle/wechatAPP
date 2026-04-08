# -*- coding: utf-8 -*-
"""
商品相关API
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
from database import db

router = APIRouter()


# ============ 响应模型 ============

class CategoryResponse(BaseModel):
    """分类响应"""
    id: int
    name: str
    parent_id: int
    icon: Optional[str]
    sort_order: int


class BrandResponse(BaseModel):
    """品牌响应"""
    id: int
    name: str
    logo: Optional[str]
    description: Optional[str]


class ProductResponse(BaseModel):
    """商品响应"""
    id: int
    name: str
    category_id: int
    brand_id: int
    cover_image: str
    images: list
    description: str
    deposit: float
    daily_rent: float
    single_rent: float
    month_card_rent: float
    stock: int
    sizes: list
    colors: list
    is_hot: bool
    is_new: bool
    view_count: int
    rent_count: int


class OutfitResponse(BaseModel):
    """搭配响应"""
    id: int
    name: str
    image: str
    description: str
    product_ids: list


# ============ 分类API ============

@router.get("/categories")
async def get_categories(parent_id: Optional[int] = 0):
    """
    获取分类列表
    """
    categories = db.execute_query(
        "SELECT * FROM categories WHERE parent_id = %s ORDER BY sort_order ASC, id ASC",
        (parent_id,)
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": [
            {
                "id": cat['id'],
                "name": cat['name'],
                "parent_id": cat['parent_id'],
                "icon": cat['icon'],
                "sort_order": cat['sort_order']
            }
            for cat in categories
        ]
    }


# ============ 品牌API ============

@router.get("/brands")
async def get_brands():
    """
    获取品牌列表
    """
    brands = db.execute_query(
        "SELECT * FROM brands ORDER BY sort_order ASC, id ASC"
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": [
            {
                "id": brand['id'],
                "name": brand['name'],
                "logo": brand['logo'],
                "description": brand['description']
            }
            for brand in brands
        ]
    }


@router.get("/brands/{brand_id}")
async def get_brand(brand_id: int):
    """
    获取品牌详情
    """
    brand = db.execute_one(
        "SELECT * FROM brands WHERE id = %s",
        (brand_id,)
    )

    if not brand:
        raise HTTPException(status_code=404, detail="品牌不存在")

    # 获取该品牌下的商品
    products = db.execute_query(
        "SELECT * FROM products WHERE brand_id = %s AND status = 1 ORDER BY id DESC",
        (brand_id,)
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": brand['id'],
            "name": brand['name'],
            "logo": brand['logo'],
            "description": brand['description'],
            "products": [
                {
                    "id": p['id'],
                    "name": p['name'],
                    "cover_image": p['cover_image'],
                    "daily_rent": float(p['daily_rent']),
                    "single_rent": float(p['single_rent']),
                    "deposit": float(p['deposit'])
                }
                for p in products
            ]
        }
    }


# ============ 商品API ============

@router.get("/products")
async def get_products(
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    keyword: Optional[str] = None,
    is_hot: Optional[bool] = None,
    available_date: Optional[str] = None,  # YYYY-MM-DD format
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    获取商品列表
    支持按日期筛选可用商品
    """
    # 构建查询条件
    conditions = ["p.status = 1"]
    params = []

    if category_id:
        conditions.append("p.category_id = %s")
        params.append(category_id)

    if brand_id:
        conditions.append("p.brand_id = %s")
        params.append(brand_id)

    if keyword:
        conditions.append("p.name LIKE %s")
        params.append(f"%{keyword}%")

    if is_hot is not None:
        conditions.append("p.is_hot = %s")
        params.append(is_hot)

    # 如果指定日期，筛选未预订的商品
    if available_date:
        conditions.append("r.id IS NULL")
        join_clause = "LEFT JOIN reservations r ON p.id = r.product_id AND r.reserved_date = %s"
        params.append(available_date)
    else:
        join_clause = ""

    where_clause = " AND ".join(conditions)

    # 查询总数
    count_sql = f"SELECT COUNT(*) as total FROM products p {join_clause} WHERE {where_clause}"
    total_result = db.execute_one(count_sql, tuple(params))
    total = total_result['total'] if total_result else 0

    # 查询商品列表
    offset = (page - 1) * page_size
    list_sql = f"""
        SELECT p.* FROM products p
        {join_clause}
        WHERE {where_clause}
        ORDER BY p.is_hot DESC, p.id DESC
        LIMIT %s OFFSET %s
    """
    params.extend([page_size, offset])

    products = db.execute_query(list_sql, tuple(params))

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "list": [
                {
                    "id": p['id'],
                    "name": p['name'],
                    "cover_image": p['cover_image'],
                    "daily_rent": float(p['daily_rent']),
                    "single_rent": float(p['single_rent']),
                    "month_card_rent": float(p['month_card_rent']),
                    "deposit": float(p['deposit']),
                    "stock": p['stock'],
                    "is_hot": p['is_hot'],
                    "is_new": p['is_new'],
                    "view_count": p['view_count'],
                    "rent_count": p['rent_count']
                }
                for p in products
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/products/hot")
async def get_hot_products(limit: int = Query(10, ge=1, le=50)):
    """
    获取热门商品
    """
    products = db.execute_query(
        """SELECT * FROM products
           WHERE status = 1 AND is_hot = 1
           ORDER BY rent_count DESC, view_count DESC
           LIMIT %s""",
        (limit,)
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": [
            {
                "id": p['id'],
                "name": p['name'],
                "cover_image": p['cover_image'],
                "daily_rent": float(p['daily_rent']),
                "single_rent": float(p['single_rent']),
                "deposit": float(p['deposit']),
                "is_hot": p['is_hot']
            }
            for p in products
        ]
    }


@router.get("/products/new")
async def get_new_products(limit: int = Query(10, ge=1, le=50)):
    """
    获取新品商品
    """
    products = db.execute_query(
        """SELECT * FROM products
           WHERE status = 1 AND is_new = 1
           ORDER BY created_at DESC
           LIMIT %s""",
        (limit,)
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": [
            {
                "id": p['id'],
                "name": p['name'],
                "cover_image": p['cover_image'],
                "daily_rent": float(p['daily_rent']),
                "single_rent": float(p['single_rent']),
                "deposit": float(p['deposit']),
                "is_new": p['is_new']
            }
            for p in products
        ]
    }


@router.get("/products/{product_id}")
async def get_product(product_id: int, token: Optional[str] = None):
    """
    获取商品详情
    """
    product = db.execute_one(
        "SELECT * FROM products WHERE id = %s AND status = 1",
        (product_id,)
    )

    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 增加浏览量
    db.execute_update(
        "UPDATE products SET view_count = view_count + 1 WHERE id = %s",
        (product_id,)
    )

    # 如果用户已登录，记录浏览历史
    if token:
        # TODO: 验证token，获取user_id
        user_id = 1  # 模拟
        # 检查是否已记录
        exists = db.execute_one(
            "SELECT id FROM browsing_history WHERE user_id = %s AND product_id = %s",
            (user_id, product_id)
        )
        if not exists:
            db.execute_insert(
                "INSERT INTO browsing_history (user_id, product_id, created_at) VALUES (%s, %s, NOW())",
                (user_id, product_id)
            )

    # 解析JSON字段
    try:
        images = json.loads(product['images']) if product['images'] else []
        sizes = json.loads(product['sizes']) if product['sizes'] else []
        colors = json.loads(product['colors']) if product['colors'] else []
    except:
        images = []
        sizes = []
        colors = []

    # 获取商品评价
    reviews = db.execute_query(
        """SELECT r.*, u.nickname, u.avatar
           FROM reviews r
           LEFT JOIN users u ON r.user_id = u.id
           WHERE r.product_id = %s
           ORDER BY r.created_at DESC
           LIMIT 10""",
        (product_id,)
    )

    # 获取搭配推荐
    outfits = db.execute_query(
        """SELECT * FROM outfits
           WHERE product_ids LIKE %s
           ORDER BY id DESC
           LIMIT 5""",
        (f"%{product_id}%",)
    )

    # 获取同类推荐
    similar_products = db.execute_query(
        """SELECT id, name, cover_image, daily_rent, single_rent, deposit
           FROM products
           WHERE category_id = %s AND id != %s AND status = 1
           ORDER BY rent_count DESC
           LIMIT 6""",
        (product['category_id'], product_id)
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": product['id'],
            "name": product['name'],
            "category_id": product['category_id'],
            "brand_id": product['brand_id'],
            "cover_image": product['cover_image'],
            "images": images,
            "description": product['description'],
            "deposit": float(product['deposit']),
            "daily_rent": float(product['daily_rent']),
            "single_rent": float(product['single_rent']),
            "month_card_rent": float(product['month_card_rent']),
            "stock": product['stock'],
            "sizes": sizes,
            "colors": colors,
            "is_hot": product['is_hot'],
            "is_new": product['is_new'],
            "view_count": product['view_count'],
            "rent_count": product['rent_count'],
            "reviews": [
                {
                    "id": r['id'],
                    "rating": r['rating'],
                    "content": r['content'],
                    "images": json.loads(r['images']) if r['images'] else [],
                    "is_anonymous": r['is_anonymous'],
                    "user": {
                        "nickname": r['nickname'] if not r['is_anonymous'] else "匿名用户",
                        "avatar": r['avatar'] if not r['is_anonymous'] else ""
                    },
                    "created_at": r['created_at'].isoformat() if r['created_at'] else None
                }
                for r in reviews
            ],
            "outfits": [
                {
                    "id": o['id'],
                    "name": o['name'],
                    "image": o['image'],
                    "description": o['description'],
                    "product_ids": json.loads(o['product_ids']) if o['product_ids'] else []
                }
                for o in outfits
            ],
            "similar_products": similar_products
        }
    }


# ============ 搭配API ============

@router.get("/outfits")
async def get_outfits(limit: int = Query(20, ge=1, le=100)):
    """
    获取搭配列表
    """
    outfits = db.execute_query(
        "SELECT * FROM outfits ORDER BY id DESC LIMIT %s",
        (limit,)
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": [
            {
                "id": o['id'],
                "name": o['name'],
                "image": o['image'],
                "description": o['description'],
                "product_ids": json.loads(o['product_ids']) if o['product_ids'] else []
            }
            for o in outfits
        ]
    }


# ============ 收藏API ============

@router.post("/favorites/{product_id}")
async def add_favorite(product_id: int, token: str):
    """
    添加收藏
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 检查商品是否存在
    product = db.execute_one(
        "SELECT id FROM products WHERE id = %s",
        (product_id,)
    )
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 检查是否已收藏
    exists = db.execute_one(
        "SELECT id FROM favorites WHERE user_id = %s AND product_id = %s",
        (user_id, product_id)
    )
    if exists:
        return {
            "code": 0,
            "message": "已收藏"
        }

    # 添加收藏
    db.execute_insert(
        "INSERT INTO favorites (user_id, product_id, created_at) VALUES (%s, %s, NOW())",
        (user_id, product_id)
    )

    return {
        "code": 0,
        "message": "收藏成功"
    }


@router.delete("/favorites/{product_id}")
async def remove_favorite(product_id: int, token: str):
    """
    取消收藏
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    db.execute_update(
        "DELETE FROM favorites WHERE user_id = %s AND product_id = %s",
        (user_id, product_id)
    )

    return {
        "code": 0,
        "message": "取消成功"
    }


@router.get("/favorites")
async def get_favorites(
    token: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    获取收藏列表
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询总数
    count_sql = "SELECT COUNT(*) as total FROM favorites WHERE user_id = %s"
    total_result = db.execute_one(count_sql, (user_id,))
    total = total_result['total'] if total_result else 0

    # 查询收藏列表
    offset = (page - 1) * page_size
    list_sql = """
        SELECT f.*, p.name, p.cover_image, p.daily_rent, p.single_rent, p.deposit, p.stock
        FROM favorites f
        LEFT JOIN products p ON f.product_id = p.id
        WHERE f.user_id = %s
        ORDER BY f.created_at DESC
        LIMIT %s OFFSET %s
    """
    favorites = db.execute_query(list_sql, (user_id, page_size, offset))

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "list": [
                {
                    "id": f['id'],
                    "product_id": f['product_id'],
                    "name": f['name'],
                    "cover_image": f['cover_image'],
                    "daily_rent": float(f['daily_rent']) if f['daily_rent'] else 0,
                    "single_rent": float(f['single_rent']) if f['single_rent'] else 0,
                    "deposit": float(f['deposit']) if f['deposit'] else 0,
                    "stock": f['stock'],
                    "created_at": f['created_at'].isoformat() if f['created_at'] else None
                }
                for f in favorites
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }
