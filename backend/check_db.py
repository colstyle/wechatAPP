# -*- coding: utf-8 -*-
"""
数据库初始化与检查脚本
"""
import sys
import os

# 将项目根目录添加到 python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import db

def check_and_init():
    print("开始检查数据库结构...")
    
    # 1. 检查 users 表
    print("检查 users 表...")
    try:
        # 尝试增加 role 字段
        db.execute_update("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' COMMENT '角色: user/admin'")
        print("已成功为 users 表增加 role 字段")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("users 表已存在 role 字段")
        else:
            print(f"检查 users 表失败: {str(e)}")

    # 2. 检查 reservations 表
    print("检查 reservations 表...")
    try:
        db.execute_query("SELECT 1 FROM reservations LIMIT 1")
        print("reservations 表已存在")
    except Exception as e:
        if "Table" in str(e) and "doesn't exist" in str(e):
            print("正在创建 reservations 表...")
            create_reservations_sql = """
            CREATE TABLE IF NOT EXISTS reservations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL COMMENT '商品ID',
                reserved_date DATE NOT NULL COMMENT '预定日期',
                order_id INT COMMENT '关联订单ID',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                INDEX idx_product_date (product_id, reserved_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品日期预定表';
            """
            db.execute_update(create_reservations_sql)
            print("reservations 表创建成功")
        else:
            print(f"检查 reservations 表失败: {str(e)}")

    # 3. 检查 orders 表字段
    print("检查 orders 表字段...")
    fields_to_add = [
        ("pickup_time", "DATETIME COMMENT '取衣时间'"),
        ("expected_return_time", "DATETIME COMMENT '应还时间'"),
        ("return_time", "DATETIME COMMENT '实际还衣时间'"),
        ("refund_amount", "DECIMAL(10, 2) DEFAULT 0 COMMENT '退款金额'"),
        ("refund_time", "DATETIME COMMENT '退款时间'"),
        ("remark", "TEXT COMMENT '备注'"),
        ("rental_type", "INT DEFAULT 1 COMMENT '租赁类型: 1按天 5套餐'")
    ]
    
    for field, definition in fields_to_add:
        try:
            db.execute_update(f"ALTER TABLE orders ADD COLUMN {field} {definition}")
            print(f"已成功为 orders 表增加 {field} 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                # print(f"orders 表已存在 {field} 字段")
                pass
            else:
                print(f"增加 {field} 字段失败: {str(e)}")

    # 4. 检查所有基础表是否存在
    print("检查所有基础表是否存在...")
    tables_to_check = [
        "categories", "brands", "products", "product_skus", "product_images", 
        "users", "user_addresses", "orders", "order_items", "reservations", 
        "subscriptions", "user_subscriptions", "appointments", "reviews"
    ]
    for table in tables_to_check:
        try:
            db.execute_query(f"SELECT 1 FROM {table} LIMIT 1")
            print(f"表 {table} 已存在")
        except Exception as e:
            if "Table" in str(e) and "doesn't exist" in str(e):
                print(f"警告：表 {table} 不存在！请运行 database/init.sql 初始化数据库。")
            else:
                print(f"检查表 {table} 失败: {str(e)}")

    print("数据库检查与初始化完成！")

if __name__ == "__main__":
    check_and_init()
