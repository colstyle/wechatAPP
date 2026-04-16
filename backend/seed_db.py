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
        # 清理旧数据
        db.execute_update("DELETE FROM order_items")
        db.execute_update("DELETE FROM orders")
        db.execute_update("DELETE FROM products")
        db.execute_update("DELETE FROM categories")
        db.execute_update("ALTER TABLE categories AUTO_INCREMENT = 1")
        db.execute_update("ALTER TABLE products AUTO_INCREMENT = 1")

        # 1. 插入要求的所有分类
        category_names = [
            "押金押金及注意事项", "约拍", "化妆", 
            "开衫/外套", "蓝色系服装", "白色系服装", 
            "黄色系服装", "紫色系服装", "绿色系服装", 
            "粉红色系服装", "项链头饰", "帽子包包", "胸贴/安全裤"
        ]

        cat_map = {}
        for idx, name in enumerate(category_names):
            # 将前三个归为服务类图标，其余匹配颜色和品类
            icon = "service" if idx < 3 else "dress"
            cat_id = db.execute_insert(
                "INSERT INTO categories (name, icon, sort_order) VALUES (%s, %s, %s)",
                (name, icon, idx + 1)
            )
            cat_map[name] = cat_id

        # 2. 插入商品
        products = [
            # ==== 前三个“类似通知” ====
            {
                "name": "租赁须知与押金明细 (必读)",
                "category": "押金押金及注意事项",
                "price": 0.00,
                "description": "详细租赁说明，破坏赔偿明细，下单即视为同意。",
                "main_image": "https://img1.baidu.com/it/u=189035111,3651586715&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500"
            },
            {
                "name": "精装外景约拍服务 (1小时)",
                "category": "约拍",
                "price": 199.00,
                "description": "摄影师一对一外景跟拍，包含5张精修，底片全送。",
                "main_image": "https://img0.baidu.com/it/u=3000673479,2191942004&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500"
            },
            {
                "name": "舞会/晚宴 精致妆容定制",
                "category": "化妆",
                "price": 128.00,
                "description": "全套彩妆+简单盘发，国际大牌化妆品，不脱妆。",
                "main_image": "https://img1.baidu.com/it/u=4194451000,1236113941&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500"
            },
            
            # ==== 服装类 & 饰品类 (每个分类2-3个) ====
            # 开衫/外套
            {"name": "法式长款纯色风衣", "category": "开衫/外套", "price": 45.0, "main_image": "https://img1.baidu.com/it/u=1576403061,960161491&fm=253"},
            {"name": "复古慵懒风针织开衫", "category": "开衫/外套", "price": 35.0, "main_image": "https://img0.baidu.com/it/u=702334057,2112447990&fm=253"},
            {"name": "机车款百搭短皮衣", "category": "开衫/外套", "price": 50.0, "main_image": "https://img2.baidu.com/it/u=2333465171,2089228498&fm=253"},

            # 蓝色系
            {"name": "克莱因蓝挂脖礼服裙", "category": "蓝色系服装", "price": 88.0, "main_image": "https://img2.baidu.com/it/u=3317774910,246473177&fm=253"},
            {"name": "浅蓝碎花森系连衣裙", "category": "蓝色系服装", "price": 40.0, "main_image": "https://img1.baidu.com/it/u=2298910086,1832009212&fm=253"},

            # 白色系
            {"name": "初恋白月光纯白流苏裙", "category": "白色系服装", "price": 60.0, "main_image": "https://img0.baidu.com/it/u=574510364,1881745423&fm=253"},
            {"name": "法式优雅真丝白衬衫", "category": "白色系服装", "price": 30.0, "main_image": "https://img2.baidu.com/it/u=840333791,3799638779&fm=253"},

            # 黄色系
            {"name": "阳光明媚姜黄吊带裙", "category": "黄色系服装", "price": 55.0, "main_image": "https://img1.baidu.com/it/u=4194451000,1236113941&fm=253"},
            {"name": "复古法式鹅黄赫本裙", "category": "黄色系服装", "price": 75.0, "main_image": "https://img1.baidu.com/it/u=375053075,3480072671&fm=253"},
            
            # 紫色系
            {"name": "梦幻香芋紫网纱长裙", "category": "紫色系服装", "price": 80.0, "main_image": "https://img1.baidu.com/it/u=2298910086,1832009212&fm=253"},
            {"name": "葡萄紫辣妹紧身包臀裙", "category": "紫色系服装", "price": 45.0, "main_image": "https://img2.baidu.com/it/u=670188732,3602123547&fm=253"},

            # 绿色系
            {"name": "薄荷绿清新森林风长裙", "category": "绿色系服装", "price": 50.0, "main_image": "https://img1.baidu.com/it/u=400977465,3044009590&fm=253"},
            {"name": "墨绿丝绒高级晚宴服", "category": "绿色系服装", "price": 120.0, "main_image": "https://img0.baidu.com/it/u=4194451000,1236113941&fm=253"},
            
            # 粉红色系
            {"name": "桃花粉甜美公主蓬蓬裙", "category": "粉红色系服装", "price": 85.0, "main_image": "https://img1.baidu.com/it/u=189035111,3651586715&fm=253"},
            {"name": "裸粉色质感缎面修身裙", "category": "粉红色系服装", "price": 95.0, "main_image": "https://img0.baidu.com/it/u=3000673479,2191942004&fm=253"},

            # 项链头饰
            {"name": "珍珠复古锁骨链", "category": "项链头饰", "price": 15.0, "main_image": "https://img1.baidu.com/it/u=1576403061,960161491&fm=253"},
            {"name": "亮钻闪耀皇冠发箍", "category": "项链头饰", "price": 20.0, "main_image": "https://img2.baidu.com/it/u=670188732,3602123547&fm=253"},
            {"name": "黑丝绒蝴蝶结发带", "category": "项链头饰", "price": 10.0, "main_image": "https://img1.baidu.com/it/u=4194451000,1236113941&fm=253"},

            # 帽子包包
            {"name": "法式宽檐优雅草帽", "category": "帽子包包", "price": 18.0, "main_image": "https://img0.baidu.com/it/u=574510364,1881745423&fm=253"},
            {"name": "香风链条格子迷你包", "category": "帽子包包", "price": 25.0, "main_image": "https://img1.baidu.com/it/u=189035111,3651586715&fm=253"},

            # 胸贴/安全裤
            {"name": "一次性医用硅胶隐形胸贴", "category": "胸贴/安全裤", "price": 15.0, "main_image": "https://img1.baidu.com/it/u=1801725350,2276587399&fm=253"},
            {"name": "冰丝无痕防走光安全裤", "category": "胸贴/安全裤", "price": 10.0, "main_image": "https://img2.baidu.com/it/u=3317774910,246473177&fm=253"},
        ]

        # 执行插入
        for p in products:
            cat_name = p.pop("category")
            cat_id = cat_map.get(cat_name)
            
            # 补全缺省字段
            desc = p.get("description", "百搭精选单品，让你的每段时光都闪耀。")
            deposit = p.get("price") * 3 if p.get("price") > 0 else 0
            
            db.execute_insert(
                """INSERT INTO products (name, category_id, main_image, price, deposit, description, sizes, colors, status, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
                (p["name"], cat_id, p["main_image"], p["price"], deposit, desc, '["S", "M"]', '["默认"]', 1)
            )

        print(f"数据注入成功！已生成 {len(category_names)} 个分类和 {len(products)} 个测试商品。")

    except Exception as e:
        print(f"致命错误，注入失败: {e}")
        db.rollback()

if __name__ == "__main__":
    seed_data()
