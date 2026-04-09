# -*- coding: utf-8 -*-
"""
预约试穿相关API
"""
from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, timedelta
from database import db

router = APIRouter()


# ============ 请求模型 ============

class CreateAppointmentRequest(BaseModel):
    """创建预约请求"""
    product_id: int
    appointment_date: str  # 格式: YYYY-MM-DD
    appointment_time: str  # 格式: HH:MM
    remark: Optional[str] = None


class UpdateAppointmentRequest(BaseModel):
    """更新预约请求"""
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    remark: Optional[str] = None


# ============ 预约API ============

@router.post("/appointments")
async def create_appointment(request: CreateAppointmentRequest, authorization: Optional[str] = Header(None)):
    """
    创建预约
    """
    # TODO: 从 authorization 解析 token 并获取 user_id
    user_id = 1

    # 检查商品是否存在
    product = db.execute_one(
        "SELECT * FROM products WHERE id = %s AND status = 1",
        (request.product_id,)
    )
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 检查预约日期是否有效
    try:
        appointment_date = datetime.strptime(request.appointment_date, '%Y-%m-%d').date()
    except:
        raise HTTPException(status_code=400, detail="日期格式不正确，应为YYYY-MM-DD")

    today = date.today()
    if appointment_date < today:
        raise HTTPException(status_code=400, detail="预约日期不能早于今天")

    # 检查时间段是否有效
    valid_times = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00']
    if request.appointment_time not in valid_times:
        raise HTTPException(status_code=400, detail="预约时间无效，可选时间: " + ", ".join(valid_times))

    # 检查该时间段是否已被预约
    exists = db.execute_one(
        """SELECT id FROM appointments
           WHERE product_id = %s AND appointment_date = %s AND appointment_time = %s AND status IN (0, 1)
           LIMIT 1""",
        (request.product_id, request.appointment_date, request.appointment_time)
    )
    if exists:
        raise HTTPException(status_code=400, detail="该时间段已被预约")

    # 创建预约
    appointment_id = db.execute_insert(
        """INSERT INTO appointments (user_id, product_id, appointment_date, appointment_time, remark, status, created_at)
           VALUES (%s, %s, %s, %s, %s, %s, NOW())""",
        (user_id, request.product_id, request.appointment_date, request.appointment_time, request.remark, 0)
    )

    return {
        "code": 0,
        "message": "预约成功",
        "data": {
            "appointment_id": appointment_id,
            "appointment_date": request.appointment_date,
            "appointment_time": request.appointment_time
        }
    }


@router.get("/appointments")
async def get_appointments(
    status: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    authorization: Optional[str] = Header(None)
):
    """
    获取预约列表
    """
    # TODO: 从 authorization 解析 token 并获取 user_id
    user_id = 1

    # 构建查询条件
    conditions = ["a.user_id = %s"]
    params = [user_id]

    if status is not None:
        conditions.append("a.status = %s")
        params.append(status)

    where_clause = " AND ".join(conditions)

    # 查询总数
    count_sql = f"SELECT COUNT(*) as total FROM appointments a WHERE {where_clause}"
    total_result = db.execute_one(count_sql, tuple(params))
    total = total_result['total'] if total_result else 0

    # 查询预约列表
    offset = (page - 1) * page_size
    list_sql = f"""
        SELECT a.*, p.name as product_name, p.cover_image, p.daily_rent
        FROM appointments a
        LEFT JOIN products p ON a.product_id = p.id
        WHERE {where_clause}
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        LIMIT %s OFFSET %s
    """
    params.extend([page_size, offset])

    appointments = db.execute_query(list_sql, tuple(params))

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "list": [
                {
                    "id": a['id'],
                    "product_id": a['product_id'],
                    "product_name": a['product_name'],
                    "product_image": a['cover_image'],
                    "product_daily_rent": float(a['daily_rent']) if a['daily_rent'] else 0,
                    "appointment_date": a['appointment_date'].isoformat() if a['appointment_date'] else None,
                    "appointment_time": a['appointment_time'],
                    "status": a['status'],
                    "status_text": get_status_text(a['status']),
                    "remark": a['remark'],
                    "created_at": a['created_at'].isoformat() if a['created_at'] else None
                }
                for a in appointments
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/appointments/{appointment_id}")
async def get_appointment(appointment_id: int, token: str):
    """
    获取预约详情
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询预约
    appointment = db.execute_one(
        """SELECT a.*, p.name as product_name, p.cover_image, p.description, p.daily_rent,
           p.single_rent, p.deposit, p.sizes, p.colors
           FROM appointments a
           LEFT JOIN products p ON a.product_id = p.id
           WHERE a.id = %s AND a.user_id = %s""",
        (appointment_id, user_id)
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")

    # 解析JSON字段
    try:
        import json
        sizes = json.loads(appointment['sizes']) if appointment['sizes'] else []
        colors = json.loads(appointment['colors']) if appointment['colors'] else []
    except:
        sizes = []
        colors = []

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": appointment['id'],
            "product_id": appointment['product_id'],
            "product": {
                "name": appointment['product_name'],
                "cover_image": appointment['cover_image'],
                "description": appointment['description'],
                "daily_rent": float(appointment['daily_rent']) if appointment['daily_rent'] else 0,
                "single_rent": float(appointment['single_rent']) if appointment['single_rent'] else 0,
                "deposit": float(appointment['deposit']) if appointment['deposit'] else 0,
                "sizes": sizes,
                "colors": colors
            },
            "appointment_date": appointment['appointment_date'].isoformat() if appointment['appointment_date'] else None,
            "appointment_time": appointment['appointment_time'],
            "status": appointment['status'],
            "status_text": get_status_text(appointment['status']),
            "remark": appointment['remark'],
            "created_at": appointment['created_at'].isoformat() if appointment['created_at'] else None
        }
    }


@router.put("/appointments/{appointment_id}")
async def update_appointment(
    appointment_id: int,
    request: UpdateAppointmentRequest,
    token: str
):
    """
    更新预约
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询预约
    appointment = db.execute_one(
        "SELECT * FROM appointments WHERE id = %s AND user_id = %s",
        (appointment_id, user_id)
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")

    if appointment['status'] != 0:
        raise HTTPException(status_code=400, detail="只能修改待确认的预约")

    # 构建更新语句
    update_fields = []
    params = []

    if request.appointment_date is not None:
        # 检查日期格式
        try:
            new_date = datetime.strptime(request.appointment_date, '%Y-%m-%d').date()
            today = date.today()
            if new_date < today:
                raise HTTPException(status_code=400, detail="预约日期不能早于今天")
            update_fields.append("appointment_date = %s")
            params.append(request.appointment_date)
        except:
            raise HTTPException(status_code=400, detail="日期格式不正确，应为YYYY-MM-DD")

    if request.appointment_time is not None:
        # 检查时间段是否有效
        valid_times = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00']
        if request.appointment_time not in valid_times:
            raise HTTPException(status_code=400, detail="预约时间无效，可选时间: " + ", ".join(valid_times))
        update_fields.append("appointment_time = %s")
        params.append(request.appointment_time)

    if request.remark is not None:
        update_fields.append("remark = %s")
        params.append(request.remark)

    if update_fields:
        params.append(appointment_id)
        sql = f"UPDATE appointments SET {', '.join(update_fields)} WHERE id = %s"
        db.execute_update(sql, tuple(params))

    return {
        "code": 0,
        "message": "更新成功"
    }


@router.delete("/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: int, token: str):
    """
    取消预约
    """
    # TODO: 验证token，获取user_id
    user_id = 1  # 模拟

    # 查询预约
    appointment = db.execute_one(
        "SELECT * FROM appointments WHERE id = %s AND user_id = %s",
        (appointment_id, user_id)
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")

    if appointment['status'] in [2, 3]:
        raise HTTPException(status_code=400, detail="无法取消已完成或已取消的预约")

    # 更新状态为已取消
    db.execute_update(
        "UPDATE appointments SET status = 3 WHERE id = %s",
        (appointment_id,)
    )

    return {
        "code": 0,
        "message": "取消成功"
    }


@router.get("/appointments/available-times")
async def get_available_times(
    product_id: int,
    appointment_date: str
):
    """
    获取可预约时间段
    """
    # 检查商品是否存在
    product = db.execute_one(
        "SELECT * FROM products WHERE id = %s AND status = 1",
        (product_id,)
    )
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 检查日期格式
    try:
        appointment_date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
    except:
        raise HTTPException(status_code=400, detail="日期格式不正确，应为YYYY-MM-DD")

    # 所有可能的时间段
    all_times = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00']

    # 获取已预约的时间段
    booked = db.execute_query(
        """SELECT appointment_time FROM appointments
           WHERE product_id = %s AND appointment_date = %s AND status IN (0, 1)""",
        (product_id, appointment_date)
    )

    booked_times = [b['appointment_time'] for b in booked]

    # 可用时间段
    available_times = [t for t in all_times if t not in booked_times]

    return {
        "code": 0,
        "message": "获取成功",
        "data": {
            "date": appointment_date,
            "available_times": available_times,
            "booked_times": booked_times
        }
    }


@router.post("/appointments/{appointment_id}/confirm")
async def confirm_appointment(appointment_id: int, token: str):
    """
    确认预约（管理员接口）
    """
    # 查询预约
    appointment = db.execute_one(
        "SELECT * FROM appointments WHERE id = %s",
        (appointment_id,)
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")

    if appointment['status'] != 0:
        raise HTTPException(status_code=400, detail="预约状态不正确")

    # 更新状态为已确认
    db.execute_update(
        "UPDATE appointments SET status = 1 WHERE id = %s",
        (appointment_id,)
    )

    return {
        "code": 0,
        "message": "确认成功"
    }


@router.post("/appointments/{appointment_id}/complete")
async def complete_appointment(appointment_id: int, token: str):
    """
    完成预约（管理员接口）
    """
    # 查询预约
    appointment = db.execute_one(
        "SELECT * FROM appointments WHERE id = %s",
        (appointment_id,)
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")

    if appointment['status'] != 1:
        raise HTTPException(status_code=400, detail="预约状态不正确")

    # 更新状态为已完成
    db.execute_update(
        "UPDATE appointments SET status = 2 WHERE id = %s",
        (appointment_id,)
    )

    return {
        "code": 0,
        "message": "标记为完成"
    }


def get_status_text(status: int) -> str:
    """获取状态文本"""
    status_map = {
        0: "待确认",
        1: "已确认",
        2: "已完成",
        3: "已取消"
    }
    return status_map.get(status, "未知")
