# -*- coding: utf-8 -*-
"""
商品相关API
"""
from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
from database import db
from app.utils.auth import get_current_user, require_admin

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

class ProductSaveRequest(BaseModel):
    name: str
    category_id: int = 0
    brand_id: int = 0
    cover_image: str
    images: list = []
    description: str = ""
    deposit: float = 0.0
    daily_rent: float = 0.0
    single_rent: float = 0.0
    month_card_rent: float = 0.0
    stock: int = 1
    sizes: list = []
    colors: list = []
    is_hot: bool = False
    is_new: bool = False
    is_package_eligible: bool = False
    status: int = 1


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
    package_only: Optional[bool] = None,
    available_date: Optional[str] = None,  # YYYY-MM-DD format
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    获取商品列表
    支持按日期筛选可用商品
    """
    # 构建查询条件
    # 如果不仅查询上架商品，可以通过 admin 传参，但为安全起见，非 admin 强制 status=1
    conditions = []
    
    # 鉴权判断，如果没带Token或不是admin，强制status=1
    is_admin = False
    if authorization:
        try:
            from app.utils.auth import _extract_token, jwt, settings
            token = _extract_token(authorization)
            if token:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                user_id = int(payload.get("sub"))
                user = db.execute_one("SELECT role FROM users WHERE id = %s", (user_id,))
                if user and str(user.get("role")) in ("admin", "2"):
                    is_admin = True
        except Exception:
            pass

    if not is_admin:
        conditions.append("p.status = 1")
    else:
        # 管理员也可以通过status参数筛选
        # 如果需要的话，可以接收status参数。当前暂定返回非硬删除的所有商品
        conditions.append("p.status IN (0, 1)")

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

    if package_only:
        conditions.append("p.is_package_eligible = 1")

    # 如果指定日期，筛选未预订的商品 (reservations 记录必须排除)
    # 如果指定日期，筛选该日期未预订的商品
    if available_date:
        # 子查询排除在指定日期已被预订的商品
        conditions.append("p.id NOT IN (SELECT product_id FROM reservations WHERE reserved_date = %s)")
        params.append(available_date)
    
    where_clause = " AND ".join(conditions)

    # 查询总数
    count_sql = f"SELECT COUNT(*) as total FROM products p WHERE {where_clause}"
    total_result = db.execute_one(count_sql, tuple(params))
    total = total_result['total'] if total_result else 0

    # 查询商品列表
    offset = (page - 1) * page_size
    list_sql = f"""
        SELECT p.* FROM products p
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
                    "is_package_eligible": bool(p.get('is_package_eligible')),
                    "status": p.get('status', 1),
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
async def get_hot_products(
    limit: int = Query(10, ge=1, le=50),
    available_date: Optional[str] = None
):
    """
    获取热门商品
    """
    conditions = ["status = 1", "is_hot = 1"]
    params = []

    if available_date:
        conditions.append("id NOT IN (SELECT product_id FROM reservations WHERE reserved_date = %s)")
        params.append(available_date)

    where_clause = " AND ".join(conditions)
    params.append(limit)

    products = db.execute_query(
        f"""SELECT * FROM products
           WHERE {where_clause}
           ORDER BY rent_count DESC, view_count DESC
           LIMIT %s""",
        tuple(params)
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
async def get_new_products(
    limit: int = Query(10, ge=1, le=50),
    available_date: Optional[str] = None
):
    """
    获取新品商品
    """
    conditions = ["status = 1", "is_new = 1"]
    params = []

    if available_date:
        conditions.append("id NOT IN (SELECT product_id FROM reservations WHERE reserved_date = %s)")
        params.append(available_date)

    where_clause = " AND ".join(conditions)
    params.append(limit)

    products = db.execute_query(
        f"""SELECT * FROM products
           WHERE {where_clause}
           ORDER BY created_at DESC
           LIMIT %s""",
        tuple(params)
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
async def get_product(product_id: int, authorization: Optional[str] = Header(None)):
    """
    获取商品详情
    """
    # TODO: 从 authorization 解析 token 并获取 user_id
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
    if authorization:
        # TODO: 从 authorization 解析 token 并获取 user_id
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
            "status": product.get('status', 1),
            "is_package_eligible": bool(product.get('is_package_eligible')),
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


# ============ 商品管理API (仅管理员) ============

@router.post("/products")
async def create_product(request: ProductSaveRequest, authorization: Optional[str] = Header(None)):
    """新增商品"""
    require_admin(authorization)
    
    images_str = json.dumps(request.images, ensure_ascii=False)
    sizes_str = json.dumps(request.sizes, ensure_ascii=False)
    colors_str = json.dumps(request.colors, ensure_ascii=False)
    
    product_id = db.execute_insert(
        """INSERT INTO products 
           (name, category_id, brand_id, cover_image, images, description, 
            deposit, daily_rent, single_rent, month_card_rent, stock, 
            sizes, colors, is_hot, is_new, is_package_eligible, status, created_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
        (request.name, request.category_id, request.brand_id, request.cover_image, images_str, request.description,
         request.deposit, request.daily_rent, request.single_rent, request.month_card_rent, request.stock,
         sizes_str, colors_str, int(request.is_hot), int(request.is_new), int(request.is_package_eligible), request.status)
    )
    return {"code": 0, "message": "添加成功", "data": {"id": product_id}}


@router.put("/products/{product_id}")
async def update_product(product_id: int, request: ProductSaveRequest, authorization: Optional[str] = Header(None)):
    """编辑商品"""
    require_admin(authorization)
    
    product = db.execute_one("SELECT id FROM products WHERE id = %s", (product_id,))
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
        
    images_str = json.dumps(request.images, ensure_ascii=False)
    sizes_str = json.dumps(request.sizes, ensure_ascii=False)
    colors_str = json.dumps(request.colors, ensure_ascii=False)
    
    db.execute_update(
        """UPDATE products SET 
           name=%s, category_id=%s, brand_id=%s, cover_image=%s, images=%s, description=%s,
           deposit=%s, daily_rent=%s, single_rent=%s, month_card_rent=%s, stock=%s,
           sizes=%s, colors=%s, is_hot=%s, is_new=%s, is_package_eligible=%s, status=%s
           WHERE id = %s""",
        (request.name, request.category_id, request.brand_id, request.cover_image, images_str, request.description,
         request.deposit, request.daily_rent, request.single_rent, request.month_card_rent, request.stock,
         sizes_str, colors_str, int(request.is_hot), int(request.is_new), int(request.is_package_eligible), request.status,
         product_id)
    )
    return {"code": 0, "message": "更新成功"}


@router.delete("/products/{product_id}")
async def delete_product(product_id: int, authorization: Optional[str] = Header(None)):
    """删除商品：关联了订单只能软删除（下架），无关联直接硬删除"""
    require_admin(authorization)
    
    product = db.execute_one("SELECT id FROM products WHERE id = %s", (product_id,))
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
        
    has_orders = db.execute_one("SELECT id FROM order_items WHERE product_id = %s LIMIT 1", (product_id,))
    if has_orders:
        # 有关联订单，执行软删除：状态置为 0(下架)
        db.execute_update("UPDATE products SET status = 0 WHERE id = %s", (product_id,))
        return {"code": 0, "message": "该商品有关联订单，已做下架处理。"}
    else:
        # 无关联订单，硬删除
        db.execute_update("DELETE FROM products WHERE id = %s", (product_id,))
        # 清理关联的收藏记录、预约记录等
        db.execute_update("DELETE FROM favorites WHERE product_id = %s", (product_id,))
        db.execute_update("DELETE FROM reservations WHERE product_id = %s", (product_id,))
        return {"code": 0, "message": "商品及相关记录已永久删除。"}


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
async def add_favorite(product_id: int, authorization: Optional[str] = Header(None)):
    """
    添加收藏
    """
    user = get_current_user(authorization)
    user_id = user['id']

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
async def remove_favorite(product_id: int, authorization: Optional[str] = Header(None)):
    """
    取消收藏
    """
    user = get_current_user(authorization)
    user_id = user['id']

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
    authorization: Optional[str] = Header(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    获取收藏列表
    """
    user = get_current_user(authorization)
    user_id = user['id']

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
