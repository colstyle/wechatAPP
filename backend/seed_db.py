# -*- coding: utf-8 -*-
import os
import sys
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db

def seed_data():
    print("开始执行【测试案例1】数据注入...")
    
    try:
        # === 紧急修复数据库字段偏移（兼容 Phase 10 到 11 的升级）===
        print("检查并执行表结构升级...")
        try:
            db.execute_update("ALTER TABLE products CHANGE cover_image main_image VARCHAR(255) DEFAULT NULL")
        except Exception:
            pass
        try:
            db.execute_update("ALTER TABLE products CHANGE daily_rent price DECIMAL(10,2) NOT NULL")
        except Exception:
            pass
        # ========================================================

        # 1. 清理旧数据
        print("清理历史数据...")
        db.execute_update("DELETE FROM order_items")
        db.execute_update("DELETE FROM orders")
        db.execute_update("DELETE FROM products")
        db.execute_update("DELETE FROM categories")
        db.execute_update("DELETE FROM store_explore_configs")
        db.execute_update("ALTER TABLE categories AUTO_INCREMENT = 1")
        db.execute_update("ALTER TABLE products AUTO_INCREMENT = 1")
        db.execute_update("ALTER TABLE store_explore_configs AUTO_INCREMENT = 1")

        # 2. 插入要求的所有分类 (库存总管中的分类)
        category_names = [
            "押金押金及注意事项", "约拍", "化妆", 
            "开衫/外套", "蓝色系服装", "白色系服装", 
            "黄色系服装", "紫色系服装", "绿色系服装", 
            "粉红色系服装", "项链头饰", "帽子包包", "胸贴/安全裤"
        ]

        cat_map = {}
        for idx, name in enumerate(category_names):
            icon = "service" if idx < 3 else "dress"
            cat_id = db.execute_insert(
                "INSERT INTO categories (name, icon, sort_order) VALUES (%s, %s, %s)",
                (name, icon, idx + 1)
            )
            cat_map[name] = cat_id

        # 3. 构建【分类与探索】页面所需要的 JSON 结构数据并注入
        # 这就是保证前端“分类页”不是空的关键
        explore_config = [
            {
                "id": "group_service",
                "name": "租赁与服务",
                "items": [
                    {"id": "item1", "name": "押金与须知", "icon": "📝", "page": "/pages/category/category"},
                    {"id": "item2", "name": "摄影约拍", "icon": "📷", "page": "/pages/category/category"},
                    {"id": "item3", "name": "专业化妆", "icon": "💄", "page": "/pages/category/category"}
                ]
            },
            {
                "id": "group_clothing",
                "name": "色彩服装",
                "items": [
                    {"id": "item4", "name": "蓝色系", "icon": "🦋", "page": "/pages/category/category"},
                    {"id": "item5", "name": "白色系", "icon": "🕊️", "page": "/pages/category/category"},
                    {"id": "item6", "name": "黄色系", "icon": "🌻", "page": "/pages/category/category"},
                    {"id": "item7", "name": "紫色系", "icon": "🔮", "page": "/pages/category/category"},
                    {"id": "item8", "name": "绿色系", "icon": "🍀", "page": "/pages/category/category"},
                    {"id": "item9", "name": "粉红色系", "icon": "🌸", "page": "/pages/category/category"},
                    {"id": "item10", "name": "开衫/外套", "icon": "🧥", "page": "/pages/category/category"}
                ]
            },
            {
                "id": "group_accessories",
                "name": "首饰与配件",
                "items": [
                    {"id": "item11", "name": "项链头饰", "icon": "👑", "page": "/pages/category/category"},
                    {"id": "item12", "name": "帽子包包", "icon": "👜", "page": "/pages/category/category"},
                    {"id": "item13", "name": "胸贴/安全裤", "icon": "👙", "page": "/pages/category/category"}
                ]
            }
        ]
        
        # 默认强行赋给 admin (通常 id 是 1)
        db.execute_insert(
            "INSERT INTO store_explore_configs (owner_user_id, config_json) VALUES (%s, %s)",
            (1, json.dumps(explore_config, ensure_ascii=False))
        )

        
        # 4. 生成统一稳定的假图前缀 (防止微信内防盗链加载不出)
        base_img = "https://dummyimage.com/600x600/fcfaf8/2b2b2b.png&text="
        
        # 5. 插入商品
        products = [
            # ==== 前三个“类似通知” ====
            {"name": "租赁须知与押金明细(必读)", "category": "押金押金及注意事项", "price": 0.0},
            {"name": "精装外景约拍服务", "category": "约拍", "price": 199.0},
            {"name": "晚装精致妆容定制", "category": "化妆", "price": 128.0},
            
            # ==== 服装类 & 饰品类 (每个分类2-3个) ====
            {"name": "法式长款纯色风衣", "category": "开衫/外套", "price": 45.0},
            {"name": "复古慵懒风针织开衫", "category": "开衫/外套", "price": 35.0},
            {"name": "机车款百搭短皮衣", "category": "开衫/外套", "price": 50.0},

            {"name": "克莱因蓝挂脖礼服裙", "category": "蓝色系服装", "price": 88.0},
            {"name": "浅蓝碎花森系连衣裙", "category": "蓝色系服装", "price": 40.0},
            {"name": "深海蓝丝绒长晚礼服", "category": "蓝色系服装", "price": 120.0},

            {"name": "初恋白月光纯白流苏裙", "category": "白色系服装", "price": 60.0},
            {"name": "法式优雅真丝白衬衫", "category": "白色系服装", "price": 30.0},

            {"name": "阳光明媚姜黄吊带裙", "category": "黄色系服装", "price": 55.0},
            {"name": "复古法式鹅黄赫本裙", "category": "黄色系服装", "price": 75.0},
            
            {"name": "梦幻香芋紫网纱长裙", "category": "紫色系服装", "price": 80.0},
            {"name": "葡萄紫辣妹紧身包臀裙", "category": "紫色系服装", "price": 45.0},

            {"name": "薄荷绿清新森林风长裙", "category": "绿色系服装", "price": 50.0},
            {"name": "黑绿丝绒高级晚宴服", "category": "绿色系服装", "price": 120.0},
            
            {"name": "桃花粉甜美公主蓬蓬裙", "category": "粉红色系服装", "price": 85.0},
            {"name": "裸粉色质感缎面修身裙", "category": "粉红色系服装", "price": 95.0},

            {"name": "珍珠复古锁骨链", "category": "项链头饰", "price": 15.0},
            {"name": "亮钻闪耀皇冠发箍", "category": "项链头饰", "price": 20.0},
            {"name": "黑丝绒蝴蝶结发带", "category": "项链头饰", "price": 10.0},

            {"name": "法式宽檐优雅草帽", "category": "帽子包包", "price": 18.0},
            {"name": "香风链条格子迷你包", "category": "帽子包包", "price": 25.0},

            {"name": "一次性医用硅胶隐形胸贴", "category": "胸贴/安全裤", "price": 15.0},
            {"name": "冰丝无痕防走光安全裤", "category": "胸贴/安全裤", "price": 10.0},
        ]

        print(f"注入 {len(products)} 个测试商品...")

        for p in products:
            cat_name = p.pop("category")
            cat_id = cat_map.get(cat_name)
            price = p["price"]
            
            # 使用商品名称构建占位图以避免防盗链
            img_url = base_img + p["name"]
            
            # 由于后端要求 images 是带结构的数组，主图保持一致
            images = json.dumps([img_url], ensure_ascii=False)
            
            # 补全缺省字段
            desc = "这是系统为您自动生成的测试商品数据描述。"
            deposit = price * 3 if price > 0 else 0
            
            db.execute_insert(
                """INSERT INTO products (name, category_id, main_image, images, price, deposit, description, sizes, colors, status, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
                (p["name"], cat_id, img_url, images, price, deposit, desc, '["均码"]', '["原色"]', 1)
            )

        print(f"所有数据注入成功！您可以打开小程序查看。")

    except Exception as e:
        print(f"致命错误，注入失败: {e}")
        db.rollback()

if __name__ == "__main__":
    seed_data()
