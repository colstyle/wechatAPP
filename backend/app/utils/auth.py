# -*- coding: utf-8 -*-
from typing import Optional
from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import jwt, JWTError

from config import settings
from database import db


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def _extract_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    value = authorization.strip()
    if not value:
        return None
    if value.lower().startswith("bearer "):
        token = value[7:].strip()
        return token or None
    return value


def get_current_user(authorization: Optional[str]) -> dict:
    token = _extract_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="未登录")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="登录已失效")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="登录已失效")

    try:
        user_id = int(sub)
    except Exception:
        raise HTTPException(status_code=401, detail="登录已失效")

    user = db.execute_one("SELECT * FROM users WHERE id = %s", (user_id,))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def require_admin(authorization: Optional[str]) -> dict:
    user = get_current_user(authorization)
    role = user.get("role")
    if str(role) not in ("admin", "2"):
        raise HTTPException(status_code=403, detail="无权限")
    return user
