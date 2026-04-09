# -*- coding: utf-8 -*-
"""
数据库种子数据导入脚本 - 为测试提供基础数据
"""
import sys
import os
import json

# 将项目根目录添加到 python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import db

def seed():
    print("开始导入种子数据...")
    
    # 1. 清理旧数据 (注意外键约束顺序)
    print("正在清理旧数据...")
    try:
        db.execute_update("SET FOREIGN_KEY_CHECKS = 0")
        db.execute_update("TRUNCATE TABLE order_items")
        db.execute_update("TRUNCATE TABLE orders")
        db.execute_update("TRUNCATE TABLE reservations")
        db.execute_update("TRUNCATE TABLE products")
        db.execute_update("TRUNCATE TABLE brands")
        db.execute_update("TRUNCATE TABLE categories")
        db.execute_update("SET FOREIGN_KEY_CHECKS = 1")
    except Exception as e:
        print(f"清理数据失败: {str(e)}")

    # 2. 插入分类
    print("正在插入分类...")
    categories = [
        (1, "连衣裙", 0, "https://picsum.photos/200/200?random=1", 1),
        (2, "上装", 0, "https://picsum.photos/200/200?random=2", 2),
        (3, "下装", 0, "https://picsum.photos/200/200?random=3", 3),
        (4, "外套", 0, "https://picsum.photos/200/200?random=4", 4),
        (5, "配饰", 0, "https://picsum.photos/200/200?random=5", 5)
    ]
    for cat in categories:
        db.execute_insert(
            "INSERT INTO categories (id, name, parent_id, icon, sort_order) VALUES (%s, %s, %s, %s, %s)",
            cat
        )

    # 3. 插入品牌
    print("正在插入品牌...")
    brands = [
        (1, "小时光原创", "https://picsum.photos/100/100?random=11", "高品质原创设计租赁品牌", 1),
        (2, "瑞典之光", "https://picsum.photos/100/100?random=12", "北欧简约风格，注重舒适感", 2),
        (3, "巴黎之约", "https://picsum.photos/100/100?random=13", "法式浪漫复古系列", 3)
    ]
    for brand in brands:
        db.execute_insert(
            "INSERT INTO brands (id, name, logo, description, sort_order) VALUES (%s, %s, %s, %s, %s)",
            brand
        )

    # 4. 插入商品
    print("正在插入商品...")
    try:
        col = db.execute_one("SHOW COLUMNS FROM products LIKE %s", ("is_package_eligible",))
        if not col:
            db.execute_update("ALTER TABLE products ADD COLUMN is_package_eligible BOOLEAN DEFAULT FALSE")
    except Exception:
        pass
    products = [
        # (name, category_id, brand_id, cover_image, deposit, daily_rent, single_rent, stock, is_hot, is_new, is_package_eligible)
        ("赫本风小黑裙", 1, 1, "https://picsum.photos/400/600?random=21", 200, 35, 50, 5, 1, 0, 1),
        ("法式碎花长裙", 1, 3, "https://picsum.photos/400/600?random=22", 150, 30, 45, 8, 1, 0, 1),
        ("莫兰迪色针织衫", 2, 1, "https://picsum.photos/400/600?random=23", 80, 15, 25, 10, 0, 0, 1),
        ("简约真丝白衬衫", 2, 3, "https://picsum.photos/400/600?random=24", 120, 25, 35, 6, 0, 1, 1),
        ("复古高腰牛仔裤", 3, 1, "https://picsum.photos/400/600?random=25", 100, 20, 30, 7, 0, 0, 0),
        ("学院风百褶半身裙", 3, 2, "https://picsum.photos/400/600?random=26", 90, 18, 28, 9, 0, 0, 1),
        ("英伦风驼色风衣", 4, 1, "https://picsum.photos/400/600?random=27", 300, 55, 80, 4, 1, 1, 0),
        ("丝绒复古西装外套", 4, 3, "https://picsum.photos/400/600?random=28", 250, 45, 70, 5, 0, 0, 0),
        ("珍珠手工项链", 5, 1, "https://picsum.photos/400/600?random=29", 50, 10, 15, 15, 0, 0, 0),
        ("复古羊毛贝雷帽", 5, 2, "https://picsum.photos/400/600?random=30", 60, 10, 15, 12, 0, 0, 0)
    ]
    
    sizes = json.dumps(["S", "M", "L", "F"])
    colors = json.dumps(["黑色", "白色", "卡其色", "复古蓝"])
    
    for p in products:
        db.execute_insert(
            """INSERT INTO products (name, category_id, brand_id, cover_image, images, description, 
               deposit, daily_rent, single_rent, stock, sizes, colors, is_hot, is_new, is_package_eligible, status, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW())""",
            (p[0], p[1], p[2], p[3], json.dumps([p[3]]), f"{p[0]}的高品质展示描述内容", 
             p[4], p[5], p[6], p[7], sizes, colors, p[8], p[9], p[10])
        )

    print("种子数据导入完成！")

if __name__ == "__main__":
    seed()
