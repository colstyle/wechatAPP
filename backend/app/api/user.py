# -*- coding: utf-8 -*-
"""
用户相关API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import hashlib
import time
import json
from database import db

router = APIRouter()


# ============ 请求模型 ============

class LoginRequest(BaseModel):
    """登录请求"""
    code: str  # 微信登录code


class UpdateProfileRequest(BaseModel):
    """更新用户信息请求"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    id_card: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    bust: Optional[int] = None
    waist: Optional[int] = None
    hips: Optional[int] = None


class AddressCreateRequest(BaseModel):
    """创建地址请求"""
    receiver_name: str
    receiver_phone: str
    province: str
    city: str
    district: str
    detail_address: str
    is_default: bool = False


class AddressUpdateRequest(BaseModel):
    """更新地址请求"""
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    detail_address: Optional[str] = None
    is_default: Optional[bool] = None


# ============ 响应模型 ============

class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    openid: str
    nickname: Optional[str]
    avatar: Optional[str]
    phone: Optional[str]
    real_name: Optional[str]
    height: Optional[int]
    weight: Optional[int]
    created_at: datetime


class AddressResponse(BaseModel):
    """地址信息响应"""
    id: int
    receiver_name: str
    receiver_phone: str
    province: str
    city: str
    district: str
    detail_address: str
    is_default: bool


# ============ 工具函数 ============

def generate_token(user_id: int) -> str:
    """生成token"""
    # 简单的token生成，生产环境建议使用JWT
    payload = f"{user_id}:{int(time.time())}"
    return hashlib.sha256(payload.encode()).hexdigest()


# ============ 用户API ============

@router.post("/login", response_model=dict)
async def login(request: LoginRequest):
    """
    微信登录
    """
    # TODO: 调用微信API获取openid
    # 这里先用模拟的方式，实际需要请求微信服务器
    # openid = get_wechat_openid(request.code)

    # 模拟openid（实际需要替换为真实微信API调用）
    openid = hashlib.md5(request.code.encode()).hexdigest()

    # 查询用户是否存在
    user = db.execute_one("SELECT * FROM users WHERE openid = %s", (openid,))

    if user:
        # 更新最后登录时间
        db.execute_update(
            "UPDATE users SET updated_at = NOW() WHERE id = %s",
            (user['id'],)
        )
    else:
        # 创建新用户
        user_id = db.execute_insert(
            """INSERT INTO users (openid, nickname, avatar, created_at, updated_at)
               VALUES (%s, %s, %s, NOW(), NOW())""",
            (openid, f"用户{openid[:6]}", "")
        )
        user = db.execute_one("SELECT * FROM users WHERE id = %s", (user_id,))

    # 生成token
    token = generate_token(user['id'])

    return {
        "code": 0,
        "message": "登录成功",
        "data": {
            "token": token,
            "user": {
                "id": user['id'],
                "openid": user['openid'],
                "nickname": user['nickname'],
                "avatar": user['avatar'],
                "phone": user['phone'],
                "real_name": user['real_name'],
                "height": user['height'],
                "weight": user['weight'],
                "created_at": user['created_at'].isoformat() if user['created_at'] else None
            }
        }
    }


@router.get("/profile")
async def get_profile(token: str):
    """
    获取用户信息
    """
    # TODO: 验证token，获取user_id
    # 这里简化处理，从token解析user_id
    user_id = 1  # 模拟

    user = db.execute_one("SELECT * FROM users WHERE id = %s", (user_id,))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 移除敏感信息
    user.pop('id_card', None)

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": user['id'],
            "openid": user['openid'],
            "nickname": user['nickname'],
            "avatar": user['avatar'],
            "phone": user['phone'],
            "real_name": user['real_name'],
            "height": user['height'],
            "weight": user['weight'],
            "bust": user['bust'],
            "waist": user['waist'],
            "hips": user['hips'],
            "created_at": user['created_at'].isoformat() if user['created_at'] else None
        }
    }


@router.post("/profile")
async def update_profile(request: UpdateProfileRequest, token: str):
    """
    更新用户信息
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 构建更新语句
    update_fields = []
    params = []

    if request.nickname is not None:
        update_fields.append("nickname = %s")
        params.append(request.nickname)
    if request.avatar is not None:
        update_fields.append("avatar = %s")
        params.append(request.avatar)
    if request.phone is not None:
        update_fields.append("phone = %s")
        params.append(request.phone)
    if request.real_name is not None:
        update_fields.append("real_name = %s")
        params.append(request.real_name)
    if request.id_card is not None:
        update_fields.append("id_card = %s")
        params.append(request.id_card)
    if request.height is not None:
        update_fields.append("height = %s")
        params.append(request.height)
    if request.weight is not None:
        update_fields.append("weight = %s")
        params.append(request.weight)
    if request.bust is not None:
        update_fields.append("bust = %s")
        params.append(request.bust)
    if request.waist is not None:
        update_fields.append("waist = %s")
        params.append(request.waist)
    if request.hips is not None:
        update_fields.append("hips = %s")
        params.append(request.hips)

    if update_fields:
        update_fields.append("updated_at = NOW()")
        params.append(user_id)

        sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        db.execute_update(sql, tuple(params))

    return {
        "code": 0,
        "message": "更新成功"
    }


# ============ 地址API ============

@router.get("/addresses")
async def get_addresses(token: str):
    """
    获取地址列表
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    addresses = db.execute_query(
        "SELECT * FROM addresses WHERE user_id = %s ORDER BY is_default DESC, id DESC",
        (user_id,)
    )

    return {
        "code": 0,
        "message": "获取成功",
        "data": [
            {
                "id": addr['id'],
                "receiver_name": addr['receiver_name'],
                "receiver_phone": addr['receiver_phone'],
                "province": addr['province'],
                "city": addr['city'],
                "district": addr['district'],
                "detail_address": addr['detail_address'],
                "is_default": addr['is_default']
            }
            for addr in addresses
        ]
    }


@router.post("/addresses")
async def create_address(request: AddressCreateRequest, token: str):
    """
    创建地址
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 如果设置为默认地址，先取消其他默认地址
    if request.is_default:
        db.execute_update(
            "UPDATE addresses SET is_default = FALSE WHERE user_id = %s",
            (user_id,)
        )

    # 创建新地址
    address_id = db.execute_insert(
        """INSERT INTO addresses (user_id, receiver_name, receiver_phone, province, city, district, detail_address, is_default, created_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
        (user_id, request.receiver_name, request.receiver_phone,
         request.province, request.city, request.district, request.detail_address, request.is_default)
    )

    return {
        "code": 0,
        "message": "创建成功",
        "data": {"id": address_id}
    }


@router.put("/addresses/{address_id}")
async def update_address(address_id: int, request: AddressUpdateRequest, token: str):
    """
    更新地址
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 检查地址是否属于该用户
    address = db.execute_one(
        "SELECT * FROM addresses WHERE id = %s AND user_id = %s",
        (address_id, user_id)
    )
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    # 如果设置为默认地址，先取消其他默认地址
    if request.is_default is True:
        db.execute_update(
            "UPDATE addresses SET is_default = FALSE WHERE user_id = %s",
            (user_id,)
        )

    # 构建更新语句
    update_fields = []
    params = []

    if request.receiver_name is not None:
        update_fields.append("receiver_name = %s")
        params.append(request.receiver_name)
    if request.receiver_phone is not None:
        update_fields.append("receiver_phone = %s")
        params.append(request.receiver_phone)
    if request.province is not None:
        update_fields.append("province = %s")
        params.append(request.province)
    if request.city is not None:
        update_fields.append("city = %s")
        params.append(request.city)
    if request.district is not None:
        update_fields.append("district = %s")
        params.append(request.district)
    if request.detail_address is not None:
        update_fields.append("detail_address = %s")
        params.append(request.detail_address)
    if request.is_default is not None:
        update_fields.append("is_default = %s")
        params.append(request.is_default)

    if update_fields:
        params.append(address_id)
        sql = f"UPDATE addresses SET {', '.join(update_fields)} WHERE id = %s"
        db.execute_update(sql, tuple(params))

    return {
        "code": 0,
        "message": "更新成功"
    }


@router.delete("/addresses/{address_id}")
async def delete_address(address_id: int, token: str):
    """
    删除地址
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 检查地址是否属于该用户
    address = db.execute_one(
        "SELECT * FROM addresses WHERE id = %s AND user_id = %s",
        (address_id, user_id)
    )
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    # 删除地址
    db.execute_update("DELETE FROM addresses WHERE id = %s", (address_id,))

    return {
        "code": 0,
        "message": "删除成功"
    }


@router.post("/addresses/{address_id}/default")
async def set_default_address(address_id: int, token: str):
    """
    设置默认地址
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 检查地址是否属于该用户
    address = db.execute_one(
        "SELECT * FROM addresses WHERE id = %s AND user_id = %s",
        (address_id, user_id)
    )
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    # 取消其他默认地址
    db.execute_update(
        "UPDATE addresses SET is_default = FALSE WHERE user_id = %s",
        (user_id,)
    )

    # 设置为默认地址
    db.execute_update(
        "UPDATE addresses SET is_default = TRUE WHERE id = %s",
        (address_id,)
    )

    return {
        "code": 0,
        "message": "设置成功"
    }
