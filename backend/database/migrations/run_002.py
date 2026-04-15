"""
数据库迁移脚本 002 — 审计表、预订唯一约束、退款幂等字段
执行方式: cd backend && python database/migrations/run_002.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.connection import db


def column_exists(table, column):
    result = db.execute_one(
        """SELECT COUNT(*) as cnt
           FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = %s
             AND COLUMN_NAME = %s""",
        (table, column)
    )
    return (result['cnt'] if result else 0) > 0


def index_exists(table, index_name):
    result = db.execute_one(
        """SELECT COUNT(*) as cnt
           FROM information_schema.STATISTICS
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = %s
             AND INDEX_NAME = %s""",
        (table, index_name)
    )
    return (result['cnt'] if result else 0) > 0


def table_exists(table):
    result = db.execute_one(
        """SELECT COUNT(*) as cnt
           FROM information_schema.TABLES
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = %s""",
        (table,)
    )
    return (result['cnt'] if result else 0) > 0


print("=== Migration 002: audit table & idempotency & reservation unique ===\n")
errors = 0

if not column_exists('orders', 'last_refund_no'):
    try:
        db.execute_update(
            "ALTER TABLE orders ADD COLUMN last_refund_no VARCHAR(64) NULL AFTER refund_amount",
            ()
        )
        print("  [OK]   Added orders.last_refund_no")
    except Exception as e:
        print(f"  [ERR]  orders.last_refund_no: {e}")
        errors += 1
else:
    print("  [SKIP] orders.last_refund_no already exists")

if not column_exists('orders', 'last_refund_action'):
    try:
        db.execute_update(
            "ALTER TABLE orders ADD COLUMN last_refund_action VARCHAR(16) NULL AFTER last_refund_no",
            ()
        )
        print("  [OK]   Added orders.last_refund_action")
    except Exception as e:
        print(f"  [ERR]  orders.last_refund_action: {e}")
        errors += 1
else:
    print("  [SKIP] orders.last_refund_action already exists")

if not table_exists('order_audit_logs'):
    try:
        db.execute_update(
            """CREATE TABLE order_audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                action VARCHAR(32) NOT NULL,
                operator_role VARCHAR(16) NULL,
                operator_id INT NULL,
                request_id VARCHAR(64) NULL,
                amount DECIMAL(10,2) NULL,
                reason VARCHAR(500) NULL,
                before_status INT NULL,
                after_status INT NULL,
                extra_json JSON NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_order_id (order_id),
                INDEX idx_request_id (request_id),
                INDEX idx_action_created (action, created_at),
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
            ()
        )
        print("  [OK]   Created order_audit_logs")
    except Exception as e:
        print(f"  [ERR]  order_audit_logs: {e}")
        errors += 1
else:
    print("  [SKIP] order_audit_logs already exists")

if not index_exists('reservations', 'uk_product_date'):
    try:
        dup = db.execute_query(
            """SELECT product_id, reserved_date, COUNT(*) as cnt
               FROM reservations
               GROUP BY product_id, reserved_date
               HAVING cnt > 1
               LIMIT 1""",
            ()
        )
        if dup:
            print("  [ERR]  reservations has duplicate (product_id, reserved_date); abort adding UNIQUE KEY uk_product_date")
            errors += 1
        else:
            db.execute_update(
                "ALTER TABLE reservations ADD UNIQUE KEY uk_product_date (product_id, reserved_date)",
                ()
            )
            print("  [OK]   Added UNIQUE KEY reservations.uk_product_date")
    except Exception as e:
        print(f"  [ERR]  reservations.uk_product_date: {e}")
        errors += 1
else:
    print("  [SKIP] reservations.uk_product_date already exists")

status = "DONE" if errors == 0 else f"DONE with {errors} error(s)"
print(f"\n=== {status} ===")
