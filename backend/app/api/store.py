# -*- coding: utf-8 -*-
"""
门店公开信息 & 分类与探索配置
"""
from fastapi import APIRouter, Header
from typing import Optional
import json

from database import db
from app.utils.auth import get_current_user, require_admin


router = APIRouter()


def _get_owner_id_from_auth(authorization: Optional[str]) -> Optional[int]:
    if not authorization:
        return None
    try:
        user = get_current_user(authorization)
        if str(user.get("role")) in ("admin", "2"):
            return int(user["id"])
    except Exception:
        return None
    return None


@router.get("/profile")
async def get_store_profile(owner_user_id: Optional[int] = None, authorization: Optional[str] = Header(None)):
    owner_id = owner_user_id or _get_owner_id_from_auth(authorization)
    if not owner_id:
        row = db.execute_one(
            """SELECT store_name, phone, address, latitude, longitude, open_hours
               FROM store_profiles
               ORDER BY id ASC
               LIMIT 1"""
        )
    else:
        row = db.execute_one(
            """SELECT store_name, phone, address, latitude, longitude, open_hours
               FROM store_profiles
               WHERE owner_user_id = %s
               LIMIT 1""",
            (owner_id,)
        )

    if not row:
        return {"code": 0, "message": "获取成功", "data": None}

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "store_name": row.get("store_name"),
            "phone": row.get("phone"),
            "address": row.get("address"),
            "latitude": float(row["latitude"]) if row.get("latitude") is not None else None,
            "longitude": float(row["longitude"]) if row.get("longitude") is not None else None,
            "open_hours": row.get("open_hours"),
        },
    }


@router.get("/explore-config")
async def get_explore_config(owner_user_id: Optional[int] = None, authorization: Optional[str] = Header(None)):
    owner_id = owner_user_id or _get_owner_id_from_auth(authorization)
    if not owner_id:
        row = db.execute_one(
            "SELECT config_json FROM store_explore_configs ORDER BY id ASC LIMIT 1"
        )
    else:
        row = db.execute_one(
            "SELECT config_json FROM store_explore_configs WHERE owner_user_id = %s LIMIT 1",
            (owner_id,)
        )

    if not row or not row.get("config_json"):
        return {"code": 0, "message": "获取成功", "data": []}

    value = row.get("config_json")
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            value = []

    if not isinstance(value, list):
        value = []

    return {"code": 0, "message": "获取成功", "data": value}


@router.get("/admin/profile")
async def admin_get_store_profile(authorization: Optional[str] = Header(None)):
    admin = require_admin(authorization)
    owner_id = int(admin["id"])
    row = db.execute_one(
        """SELECT store_name, phone, address, latitude, longitude, open_hours
           FROM store_profiles
           WHERE owner_user_id = %s
           LIMIT 1""",
        (owner_id,)
    )
    if not row:
        return {"code": 0, "message": "获取成功", "data": None}
    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "store_name": row.get("store_name"),
            "phone": row.get("phone"),
            "address": row.get("address"),
            "latitude": float(row["latitude"]) if row.get("latitude") is not None else None,
            "longitude": float(row["longitude"]) if row.get("longitude") is not None else None,
            "open_hours": row.get("open_hours"),
        },
    }


@router.put("/admin/profile")
async def admin_upsert_store_profile(payload: dict, authorization: Optional[str] = Header(None)):
    admin = require_admin(authorization)
    owner_id = int(admin["id"])

    store_name = (payload.get("store_name") or "").strip() or None
    phone = (payload.get("phone") or "").strip() or None
    address = (payload.get("address") or "").strip() or None
    open_hours = (payload.get("open_hours") or "").strip() or None
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")

    row = db.execute_one("SELECT id FROM store_profiles WHERE owner_user_id = %s", (owner_id,))
    if row:
        db.execute_update(
            """UPDATE store_profiles
               SET store_name = %s, phone = %s, address = %s, latitude = %s, longitude = %s, open_hours = %s
               WHERE owner_user_id = %s""",
            (store_name, phone, address, latitude, longitude, open_hours, owner_id)
        )
    else:
        db.execute_insert(
            """INSERT INTO store_profiles (owner_user_id, store_name, phone, address, latitude, longitude, open_hours, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())""",
            (owner_id, store_name, phone, address, latitude, longitude, open_hours)
        )

    return {"code": 0, "message": "保存成功"}


@router.get("/admin/explore-config")
async def admin_get_explore_config(authorization: Optional[str] = Header(None)):
    admin = require_admin(authorization)
    owner_id = int(admin["id"])
    row = db.execute_one(
        "SELECT config_json FROM store_explore_configs WHERE owner_user_id = %s LIMIT 1",
        (owner_id,)
    )
    if not row or not row.get("config_json"):
        return {"code": 0, "message": "获取成功", "data": []}

    value = row.get("config_json")
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            value = []
    if not isinstance(value, list):
        value = []
    return {"code": 0, "message": "获取成功", "data": value}


@router.put("/admin/explore-config")
async def admin_put_explore_config(payload: dict, authorization: Optional[str] = Header(None)):
    admin = require_admin(authorization)
    owner_id = int(admin["id"])
    value = payload.get("groups")
    if value is None:
        value = payload.get("data")

    if not isinstance(value, list):
        value = []

    config_str = json.dumps(value, ensure_ascii=False)
    row = db.execute_one("SELECT id FROM store_explore_configs WHERE owner_user_id = %s", (owner_id,))
    if row:
        db.execute_update(
            "UPDATE store_explore_configs SET config_json = %s WHERE owner_user_id = %s",
            (config_str, owner_id)
        )
    else:
        db.execute_insert(
            "INSERT INTO store_explore_configs (owner_user_id, config_json, created_at) VALUES (%s, %s, NOW())",
            (owner_id, config_str)
        )
    return {"code": 0, "message": "保存成功"}

