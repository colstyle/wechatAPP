# -*- coding: utf-8 -*-
"""
数据库全量初始化与检查脚本
"""
import sys
import os

# 将项目根目录添加到 python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import db

def run_init_sql():
    print("开始执行全量数据库初始化...")
    sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "init.sql")
    
    if not os.path.exists(sql_path):
        print(f"错误：找不到初始化文件 {sql_path}")
        return False

    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 按分号分割 SQL 语句
    raw_statements = sql_content.split(';')
    
    success_count = 0
    fail_count = 0
    
    for raw_stmt in raw_statements:
        # 处理每一行，去掉注释
        lines = raw_stmt.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('--') or line.startswith('#'):
                continue
            clean_lines.append(line)
        
        stmt = " ".join(clean_lines).strip()
        
        if not stmt:
            continue
            
        try:
            # 过滤掉 CREATE DATABASE 和 USE 语句
            if stmt.upper().startswith("CREATE DATABASE") or stmt.upper().startswith("USE "):
                continue
                
            db.execute_update(stmt)
            success_count += 1
        except Exception as e:
            # 忽略表已存在的错误 (MySQL Error 1050)
            if "already exists" in str(e).lower() or "1050" in str(e):
                success_count += 1
            else:
                print(f"执行失败: {stmt[:50]}...")
                print(f"错误信息: {str(e)}")
                fail_count += 1

    print(f"初始化完成！成功: {success_count}, 失败: {fail_count}")
    return fail_count == 0

def check_and_fix_fields():
    print("\n检查并补全缺失字段...")
    
    # 1. 检查 users 表 role 字段
    try:
        db.execute_update("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' COMMENT '角色: user/admin'")
        print("已补全 users.role 字段")
    except: pass

    # 2. 检查 orders 表字段
    fields = [
        ("pickup_time", "DATETIME COMMENT '取衣时间'"),
        ("expected_return_time", "DATETIME COMMENT '应还时间'"),
        ("return_time", "DATETIME COMMENT '实际还衣时间'"),
        ("refund_amount", "DECIMAL(10, 2) DEFAULT 0 COMMENT '退款金额'"),
        ("refund_time", "DATETIME COMMENT '退款时间'"),
        ("remark", "TEXT COMMENT '备注'"),
        ("rental_type", "INT DEFAULT 1 COMMENT '租赁类型: 1按天 5套餐'"),
        ("overdue_duration", "INT DEFAULT 0 COMMENT '逾期时长(小时)'")
    ]
    
    for field, definition in fields:
        try:
            db.execute_update(f"ALTER TABLE orders ADD COLUMN {field} {definition}")
            print(f"已补全 orders.{field} 字段")
        except: pass

    print("字段检查完成！")

if __name__ == "__main__":
    if run_init_sql():
        check_and_fix_fields()
    else:
        print("\n初始化过程中出现错误，请检查数据库连接配置。")
