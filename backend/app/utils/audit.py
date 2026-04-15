# -*- coding: utf-8 -*-
from typing import Optional, Any, Dict
import json

from database import db


def write_order_audit(
    order_id: int,
    action: str,
    operator_role: Optional[str] = None,
    operator_id: Optional[int] = None,
    request_id: Optional[str] = None,
    amount: Optional[float] = None,
    reason: Optional[str] = None,
    before_status: Optional[int] = None,
    after_status: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    extra_json = None
    if extra is not None:
        try:
            extra_json = json.dumps(extra, ensure_ascii=False)
        except Exception:
            extra_json = None

    try:
        db.execute_insert(
            """INSERT INTO order_audit_logs
               (order_id, action, operator_role, operator_id, request_id, amount, reason, before_status, after_status, extra_json, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
            (
                order_id,
                action,
                operator_role,
                operator_id,
                request_id,
                amount,
                reason,
                before_status,
                after_status,
                extra_json,
            ),
        )
    except Exception:
        return
