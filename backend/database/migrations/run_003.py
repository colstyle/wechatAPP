"""
数据库迁移脚本 003 — 门店信息与分类探索配置
执行方式: cd backend && python database/migrations/run_003.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.connection import db


def table_exists(table):
    result = db.execute_one(
        """SELECT COUNT(*) as cnt
           FROM information_schema.TABLES
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = %s""",
        (table,)
    )
    return (result['cnt'] if result else 0) > 0


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


print("=== Migration 003: store profiles & explore config ===\n")
errors = 0

if not table_exists("store_profiles"):
    try:
        db.execute_update(
            """CREATE TABLE store_profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                owner_user_id INT NOT NULL,
                store_name VARCHAR(100) NULL,
                phone VARCHAR(20) NULL,
                address VARCHAR(200) NULL,
                latitude DECIMAL(10,6) NULL,
                longitude DECIMAL(10,6) NULL,
                open_hours VARCHAR(100) NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_owner_user_id (owner_user_id),
                INDEX idx_owner_user_id (owner_user_id),
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
            ()
        )
        print("  [OK]   Created store_profiles")
    except Exception as e:
        print(f"  [ERR]  store_profiles: {e}")
        errors += 1
else:
    print("  [SKIP] store_profiles already exists")

if not table_exists("store_explore_configs"):
    try:
        db.execute_update(
            """CREATE TABLE store_explore_configs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                owner_user_id INT NOT NULL,
                config_json JSON NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_owner_user_id (owner_user_id),
                INDEX idx_owner_user_id (owner_user_id),
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
            ()
        )
        print("  [OK]   Created store_explore_configs")
    except Exception as e:
        print(f"  [ERR]  store_explore_configs: {e}")
        errors += 1
else:
    print("  [SKIP] store_explore_configs already exists")

if not column_exists("categories", "updated_at"):
    try:
        db.execute_update(
            "ALTER TABLE categories ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            ()
        )
        print("  [OK]   Added categories.updated_at")
    except Exception as e:
        print(f"  [WARN] categories.updated_at: {e}")
else:
    print("  [SKIP] categories.updated_at already exists")

status = "DONE" if errors == 0 else f"DONE with {errors} error(s)"
print(f"\n=== {status} ===")

