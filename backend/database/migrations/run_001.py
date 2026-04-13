"""
数据库迁移脚本 001 — 订单商品快照字段
执行方式: cd backend && python database/migrations/run_001.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.connection import db


def column_exists(table, column):
    """检查字段是否已存在"""
    result = db.execute_one(
        """SELECT COUNT(*) as cnt
           FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = %s
             AND COLUMN_NAME = %s""",
        (table, column)
    )
    return (result['cnt'] if result else 0) > 0


print("=== Migration 001: order_items snapshot fields ===\n")
errors = 0

# --- 1. snapshot_price ---
if column_exists('order_items', 'snapshot_price'):
    print("  [SKIP] snapshot_price already exists")
else:
    try:
        db.execute_update(
            "ALTER TABLE order_items ADD COLUMN snapshot_price DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER product_image",
            ()
        )
        print("  [OK]   Added snapshot_price")
    except Exception as e:
        print(f"  [ERR]  snapshot_price: {e}")
        errors += 1

# --- 2. snapshot_deposit ---
if column_exists('order_items', 'snapshot_deposit'):
    print("  [SKIP] snapshot_deposit already exists")
else:
    try:
        db.execute_update(
            "ALTER TABLE order_items ADD COLUMN snapshot_deposit DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER snapshot_price",
            ()
        )
        print("  [OK]   Added snapshot_deposit")
    except Exception as e:
        print(f"  [ERR]  snapshot_deposit: {e}")
        errors += 1

# --- 3. 回填存量数据 ---
try:
    db.execute_update(
        """UPDATE order_items oi
           JOIN products p ON oi.product_id = p.id
           SET
             oi.snapshot_price   = COALESCE(oi.rent_price, p.daily_rent, 0),
             oi.snapshot_deposit = COALESCE(oi.deposit, p.deposit, 0)
           WHERE oi.snapshot_price = 0 AND oi.snapshot_deposit = 0""",
        ()
    )
    print("  [OK]   Backfilled existing rows")
except Exception as e:
    print(f"  [ERR]  Backfill: {e}")
    errors += 1

# --- 验证 ---
try:
    result = db.execute_one(
        "SELECT COUNT(*) as total FROM order_items WHERE snapshot_price > 0"
    )
    filled = result['total'] if result else 0
    print(f"\n  Rows with snapshot data: {filled}")
except Exception as e:
    print(f"\n  [WARN] Verify failed: {e}")

status = "DONE" if errors == 0 else f"DONE with {errors} error(s)"
print(f"\n=== {status} ===")
