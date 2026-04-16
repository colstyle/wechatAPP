# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime
from decimal import Decimal
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db

def seed_data():
    print("开始注入『小时光租衣舍』业务演示数据...")
    
    try:
        # 1. 清理旧数据 (按照外键依赖反向清理)
        db.execute_update("DELETE FROM order_items")
        db.execute_update("DELETE FROM orders")
        db.execute_update("DELETE FROM products")
        db.execute_update("DELETE FROM categories")
        db.execute_update("ALTER TABLE categories AUTO_INCREMENT = 1")
        db.execute_update("ALTER TABLE products AUTO_INCREMENT = 1")

        # 2. 插入分类
        categories = [
            # 咨询服务类
            {"name": "咨询服务", "icon": "service", "sort": 1},
            {"name": "特惠活动", "icon": "gift", "sort": 2},
            # 服装色系类
            {"name": "开衫/外套", "icon": "coat", "sort": 3},
            {"name": "蓝色系服装", "icon": "color-blue", "sort": 4},
            {"name": "白色系服装", "icon": "color-white", "sort": 5},
            {"name": "黄色系服装", "icon": "color-yellow", "sort": 6},
            {"name": "紫色系服装", "icon": "color-purple", "sort": 7},
            {"name": "绿色系服装", "icon": "color-green", "sort": 8},
            {"name": "粉红色系服装", "icon": "color-pink", "sort": 9},
            # 配饰周边
            {"name": "项链头饰", "icon": "jewelry", "sort": 10},
            {"name": "帽子包包", "icon": "bag", "sort": 11},
            {"name": "胸贴/安全裤", "icon": "inner", "sort": 12},
        ]

        cat_map = {}
        for cat in categories:
            cat_id = db.execute_insert(
                "INSERT INTO categories (name, icon, sort_order) VALUES (%s, %s, %s)",
                (cat["name"], cat["icon"], cat["sort"])
            )
            cat_map[cat["name"]] = cat_id

        # 3. 插入商品示例
        products = [
            # 咨询服务与押金 (虚拟商品形式展示)
            {
                "name": "押金及租赁注意事项 (必读)",
                "category": "咨询服务",
                "price": 0.00,
                "deposit": 0.00,
                "description": "点击查看小时光租衣舍详细租赁协议、押金退还流程及衣物损坏赔偿标准。",
                "main_image": "https://img1.baidu.com/it/u=189035111,3651586715&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500",
                "status": 1
            },
            {
                "name": "专业约拍服务 (一小时精修)",
                "category": "咨询服务",
                "price": 199.00,
                "deposit": 0.00,
                "description": "专业摄影师跟拍，含5张精修图，底片全送。让美照记录你的小时光。",
                "main_image": "https://img0.baidu.com/it/u=3000673479,2191942004&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500",
                "status": 1
            },
            # 特惠活动
            {
                "name": "全场通用 9.9 特惠体验券",
                "category": "特惠活动",
                "price": 9.90,
                "deposit": 0.00,
                "description": "特惠专区专用，仅限指定单品体验。",
                "main_image": "https://img2.baidu.com/it/u=317586548,2285141695&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500",
                "status": 1
            },
            {
                "name": "活动 59.9 元两件套餐 (限时)",
                "category": "特惠活动",
                "price": 59.90,
                "deposit": 100.00,
                "description": "从指定专区任选两件，租期24小时。超值闺蜜装首选！",
                "main_image": "https://img1.baidu.com/it/u=1801725350,2276587399&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500",
                "status": 1
            },
            # 色系服装 - 紫色
            {
                "name": "梦幻薰衣草 紫色法式长裙",
                "category": "紫色系服装",
                "price": 88.00,
                "deposit": 200.00,
                "description": "优雅深紫，显白神器。适合生日宴、晚会。尺码：S/M/L。",
                "main_image": "https://img1.baidu.com/it/u=2298910086,1832009212&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=667",
                "sizes": ["S", "M", "L"],
                "colors": ["紫色"]
            },
            # 色系服装 - 蓝色
            {
                "name": "克莱因蓝 现代简约吊带裙",
                "category": "蓝色系服装",
                "price": 68.00,
                "deposit": 150.00,
                "description": "饱和度拉满的蓝色，出片率极高。面料亲肤舒适。",
                "main_image": "https://img0.baidu.com/it/u=3124151703,1657805177&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=750",
                "sizes": ["S", "M"],
                "colors": ["蓝色"]
            },
            # 配饰 - 其它
            {
                "name": "隐形胸贴 (肤色/一次性)",
                "category": "胸贴/安全裤",
                "price": 15.00,
                "deposit": 0.00,
                "description": "礼服必备神器，粘性持久，防过敏设计。",
                "main_image": "https://img1.baidu.com/it/u=2523214582,3416035973&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500",
                "status": 1
            }
        ]

        for p in products:
            cat_name = p.pop("category")
            cat_id = cat_map.get(cat_name)
            
            sizes_json = json.dumps(p.get("sizes", ["均码"]), ensure_ascii=False)
            colors_json = json.dumps(p.get("colors", ["默认"]), ensure_ascii=False)
            
            db.execute_insert(
                """INSERT INTO products (name, category_id, main_image, price, deposit, description, sizes, colors, status, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
                (p["name"], cat_id, p["main_image"], p["price"], p["deposit"], p["description"], sizes_json, colors_json, 1)
            )

        print(f"数据注入成功！已录入 {len(categories)} 个分类和 {len(products)} 个演示商品。")

    except Exception as e:
        print(f"注入失败: {e}")
        db.rollback()

if __name__ == "__main__":
    seed_data()
