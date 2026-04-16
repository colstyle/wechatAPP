-- 数据库初始化脚本 - 小时光租衣舍 (Phase 11 最终版)

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 1. 用户表 (移除繁琐个人信息)
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `openid` VARCHAR(128) NOT NULL UNIQUE COMMENT '微信OpenID',
  `nickname` VARCHAR(128) DEFAULT NULL COMMENT '微信昵称',
  `avatar_url` VARCHAR(255) DEFAULT NULL COMMENT '头像',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
  `role` TINYINT DEFAULT 1 COMMENT '角色: 1-普通用户, 2-店主',
  `status` TINYINT DEFAULT 1 COMMENT '状态: 1-正常, 0-禁用',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 门店型录分类表
CREATE TABLE IF NOT EXISTS `categories` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL,
  `icon` VARCHAR(255) DEFAULT NULL,
  `sort_order` INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 衣服商品表
CREATE TABLE IF NOT EXISTS `products` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(128) NOT NULL COMMENT '衣服名称',
  `category_id` INT DEFAULT NULL COMMENT '分类ID',
  `main_image` VARCHAR(255) DEFAULT NULL COMMENT '主图',
  `images` JSON DEFAULT NULL COMMENT '轮播图列表',
  `price` DECIMAL(10, 2) NOT NULL COMMENT '单日租金',
  `deposit` DECIMAL(10, 2) DEFAULT 0.00 COMMENT '押金',
  `description` TEXT COMMENT '详细说明',
  `sizes` JSON DEFAULT NULL COMMENT '可选尺码: ["S", "M", "L"]',
  `colors` JSON DEFAULT NULL COMMENT '可选颜色',
  `stock` INT DEFAULT 1 COMMENT '库存数量',
  `rent_count` INT DEFAULT 0 COMMENT '租用次数',
  `status` TINYINT DEFAULT 1 COMMENT '1-上架, 0-下架',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 预约表 (核心：到店选衣/试衣)
CREATE TABLE IF NOT EXISTS `appointments` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `product_id` INT DEFAULT NULL COMMENT '意向商品 (可选)',
  `appoint_date` DATE NOT NULL COMMENT '预约日期',
  `time_slot` VARCHAR(50) NOT NULL COMMENT '预约时间段: 10:00-11:00',
  `num_people` INT DEFAULT 1 COMMENT '人数',
  `status` TINYINT DEFAULT 1 COMMENT '1-已预约, 2-已到店, 0-已取消',
  `remark` VARCHAR(255) DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 订单表 (完全移除配送地址相关的复杂外键)
CREATE TABLE IF NOT EXISTS `orders` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `order_sn` VARCHAR(64) NOT NULL UNIQUE COMMENT '订单号',
  `user_id` INT NOT NULL,
  `rental_type` TINYINT DEFAULT 1 COMMENT '租赁类型: 1-按天, 3-订阅, 5-套餐',
  `total_amount` DECIMAL(10, 2) NOT NULL COMMENT '实付总额',
  `total_deposit` DECIMAL(10, 2) DEFAULT 0.00 COMMENT '押金总额',
  `total_rent` DECIMAL(10, 2) DEFAULT 0.00 COMMENT '租金总额',
  `status` TINYINT DEFAULT 0 COMMENT '0-待支付, 1-待取衣, 2-租赁中, 3-逾期, 4-待审核, 5-已取消, 7-已完成',
  `payment_time` DATETIME DEFAULT NULL,
  `pickup_time` DATETIME DEFAULT NULL COMMENT '取衣时间',
  `expected_return_time` DATETIME DEFAULT NULL COMMENT '应还时间',
  `return_time` DATETIME DEFAULT NULL COMMENT '实际归还时间',
  `start_date` DATE DEFAULT NULL COMMENT '起租日期',
  `end_date` DATE DEFAULT NULL COMMENT '截止日期',
  `rent_days` INT DEFAULT 1,
  `remark` VARCHAR(255) DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 订单细节 (快照存档)
CREATE TABLE IF NOT EXISTS `order_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `order_id` INT NOT NULL,
  `product_id` INT NOT NULL,
  `product_name` VARCHAR(128) NOT NULL,
  `product_image` VARCHAR(255) DEFAULT NULL,
  `price` DECIMAL(10, 2) NOT NULL COMMENT '下单时单日租金',
  `deposit` DECIMAL(10, 2) NOT NULL COMMENT '下单时押金',
  `size` VARCHAR(20) DEFAULT NULL,
  `color` VARCHAR(20) DEFAULT NULL,
  `quantity` INT DEFAULT 1,
  FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. 门店基本信息表 (保留：用户需要知道店在哪)
CREATE TABLE IF NOT EXISTS `store_profiles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `owner_user_id` INT NOT NULL,
  `store_name` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(20) DEFAULT NULL,
  `address` VARCHAR(255) DEFAULT NULL,
  `latitude` DECIMAL(10, 7) DEFAULT NULL,
  `longitude` DECIMAL(10, 7) DEFAULT NULL,
  `open_hours` VARCHAR(100) DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`owner_user_id`) REFERENCES `users`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. 门店探索页配置表
CREATE TABLE IF NOT EXISTS `store_explore_configs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `owner_user_id` INT NOT NULL,
  `config_json` JSON DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`owner_user_id`) REFERENCES `users`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. 商品预订表 (用于锁定使用日期)
CREATE TABLE IF NOT EXISTS `reservations` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `product_id` INT NOT NULL,
  `reserved_date` DATE NOT NULL,
  `order_id` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_product_date` (`product_id`, `reserved_date`),
  FOREIGN KEY (`product_id`) REFERENCES `products`(`id`),
  FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. 商品评价表
CREATE TABLE IF NOT EXISTS `reviews` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `product_id` INT NOT NULL,
  `order_id` INT DEFAULT NULL,
  `rating` TINYINT NOT NULL DEFAULT 5,
  `content` TEXT,
  `images` JSON DEFAULT NULL,
  `is_anonymous` TINYINT(1) DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`),
  FOREIGN KEY (`product_id`) REFERENCES `products`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. 订单审计表 (操作日志)
CREATE TABLE IF NOT EXISTS `order_audit` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `order_id` INT NOT NULL,
  `action` VARCHAR(50) NOT NULL,
  `operator_role` VARCHAR(20) NOT NULL,
  `operator_id` INT DEFAULT NULL,
  `request_id` VARCHAR(64) DEFAULT NULL,
  `amount` DECIMAL(10, 2) DEFAULT NULL,
  `reason` VARCHAR(255) DEFAULT NULL,
  `before_status` TINYINT DEFAULT NULL,
  `after_status` TINYINT DEFAULT NULL,
  `extra` JSON DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. 订阅套餐与记录表
CREATE TABLE IF NOT EXISTS `subscription_packages` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL,
  `price` DECIMAL(10, 2) NOT NULL,
  `days` INT NOT NULL,
  `max_times` INT NOT NULL COMMENT '可用次数(0为无限制)',
  `description` VARCHAR(255) DEFAULT NULL,
  `is_active` TINYINT(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `subscriptions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `subscription_no` VARCHAR(64) NOT NULL UNIQUE,
  `package_id` INT NOT NULL,
  `start_date` DATE NOT NULL,
  `end_date` DATE NOT NULL,
  `remaining_times` INT NOT NULL,
  `status` TINYINT DEFAULT 1 COMMENT '1-有效, 3-已取消',
  `payment_time` DATETIME DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;

-- 注入演示数据 (可选)
INSERT INTO `categories` (`name`, `icon`, `sort_order`) VALUES ('所有', 'category-all', 1);
INSERT INTO `categories` (`name`, `icon`, `sort_order`) VALUES ('连衣裙', 'category-dress', 2);
INSERT INTO `categories` (`name`, `icon`, `sort_order`) VALUES ('汉服', 'category-hanfu', 3);
