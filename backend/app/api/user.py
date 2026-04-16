# -*- coding: utf-8 -*-
"""
用户相关API
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import hashlib
import time
import json
import httpx
from database import db
from app.utils.auth import create_access_token, get_current_user
from config import settings

router = APIRouter()


# ============ 请求模型 ============

class LoginRequest(BaseModel):
    """登录请求"""
    code: str  # 微信登录code
    mock_openid: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    """更新用户信息请求"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None




# ============ 响应模型 ============

class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    openid: str
    nickname: Optional[str]
    avatar_url: Optional[str]
    phone: Optional[str]
    role: str
    created_at: datetime




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
    openid = None
    if settings.DEBUG and request.mock_openid:
        openid = request.mock_openid.strip()
        
    if not openid:
        if not request.code:
            raise HTTPException(status_code=400, detail="code不能为空")
            
        # 真实调用微信 jscode2session API
        if settings.WECHAT_APP_ID == "your-wechat-app-id" and settings.DEBUG:
            # 本地开发未配置真实的 AppID 时，回退使用 hash（仅限 DEBUG 环境）
            openid = hashlib.md5(request.code.encode()).hexdigest()
        else:
            url = "https://api.weixin.qq.com/sns/jscode2session"
            params = {
                "appid": settings.WECHAT_APP_ID,
                "secret": settings.WECHAT_APP_SECRET,
                "js_code": request.code,
                "grant_type": "authorization_code"
            }
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, params=params)
                data = resp.json()
                
            if "errcode" in data and data["errcode"] != 0:
                raise HTTPException(status_code=400, detail=f"微信登录失败: {data.get('errmsg')}")
                
            openid = data.get("openid")
            if not openid:
                raise HTTPException(status_code=400, detail="获取微信openid失败")

    # 查询用户是否存在
    user = db.execute_one("SELECT * FROM users WHERE openid = %s", (openid,))

    desired_role = None
    if settings.DEBUG and openid.startswith("admin_"):
        desired_role = "2"

    if user:
        # 更新最后登录时间
        if desired_role and str(user.get("role")) != desired_role:
            db.execute_update(
                "UPDATE users SET role = %s, updated_at = NOW() WHERE id = %s",
                (desired_role, user['id'])
            )
        else:
            db.execute_update(
                "UPDATE users SET updated_at = NOW() WHERE id = %s",
                (user['id'],)
            )
    else:
        # 创建新用户
        role = desired_role or "1"
        user_id = db.execute_insert(
            """INSERT INTO users (openid, nickname, avatar_url, role, created_at, updated_at)
               VALUES (%s, %s, %s, %s, NOW(), NOW())""",
            (openid, f"用户{openid[:6]}", "", role)
        )
        user = db.execute_one("SELECT * FROM users WHERE id = %s", (user_id,))

    token = create_access_token(user['id'])

    return {
        "code": 0,
        "message": "登录成功",
        "data": {
            "token": token,
            "user": {
                "id": user['id'],
                "openid": user['openid'],
                "nickname": user['nickname'],
                "avatar_url": user['avatar_url'],
                "phone": user['phone'],
                "role": user.get('role', 'user'),
                "created_at": user['created_at'].isoformat() if user['created_at'] else None
            }
        }
    }


@router.get("/profile")
async def get_profile(authorization: Optional[str] = Header(None)):
    """
    获取用户信息
    """
    user = get_current_user(authorization)

    # 移除敏感信息
    user.pop('id_card', None)

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": user['id'],
            "openid": user['openid'],
            "nickname": user['nickname'],
            "avatar_url": user['avatar_url'],
            "phone": user['phone'],
            "role": user.get('role', 'user'),
            "created_at": user['created_at'].isoformat() if user['created_at'] else None
        }
    }


@router.post("/profile")
async def update_profile(request: UpdateProfileRequest, authorization: Optional[str] = Header(None)):
    """
    更新用户信息
    """
    user = get_current_user(authorization)
    user_id = user['id']

    # 构建更新语句
    update_fields = []
    params = []

    if request.nickname is not None:
        update_fields.append("nickname = %s")
        params.append(request.nickname)
    if request.avatar_url is not None:
        update_fields.append("avatar_url = %s")
        params.append(request.avatar_url)
    if request.phone is not None:
        update_fields.append("phone = %s")
        params.append(request.phone)
    if update_fields:
        update_fields.append("updated_at = NOW()")
        params.append(user_id)

        sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        db.execute_update(sql, tuple(params))

    return {
        "code": 0,
        "message": "更新成功"
    }


