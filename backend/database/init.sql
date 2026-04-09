-- 租衣服电商系统 - 数据库初始化脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS Celestial_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE Celestial_db;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    openid VARCHAR(100) UNIQUE COMMENT '微信openid',
    nickname VARCHAR(50) COMMENT '昵称',
    avatar VARCHAR(500) COMMENT '头像URL',
    phone VARCHAR(20) COMMENT '手机号',
    real_name VARCHAR(50) COMMENT '真实姓名',
    id_card VARCHAR(20) COMMENT '身份证号',
    height INT COMMENT '身高(cm)',
    weight INT COMMENT '体重(kg)',
    bust INT COMMENT '胸围',
    waist INT COMMENT '腰围',
    hips INT COMMENT '臀围',
    role VARCHAR(20) DEFAULT 'user' COMMENT '角色: user/admin',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_openid (openid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 收货地址表
CREATE TABLE IF NOT EXISTS addresses (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '地址ID',
    user_id INT NOT NULL COMMENT '用户ID',
    receiver_name VARCHAR(50) COMMENT '收货人',
    receiver_phone VARCHAR(20) COMMENT '手机号',
    province VARCHAR(50) COMMENT '省',
    city VARCHAR(50) COMMENT '市',
    district VARCHAR(50) COMMENT '区',
    detail_address VARCHAR(200) COMMENT '详细地址',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否默认',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_is_default (user_id, is_default),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收货地址表';

-- 分类表
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '分类ID',
    name VARCHAR(50) COMMENT '分类名称',
    parent_id INT DEFAULT 0 COMMENT '父分类ID',
    icon VARCHAR(500) COMMENT '图标URL',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分类表';

-- 品牌表
CREATE TABLE IF NOT EXISTS brands (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '品牌ID',
    name VARCHAR(50) COMMENT '品牌名称',
    logo VARCHAR(500) COMMENT 'LOGO URL',
    description TEXT COMMENT '品牌介绍',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='品牌表';

-- 商品表
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '商品ID',
    name VARCHAR(100) COMMENT '商品名称',
    category_id INT COMMENT '分类ID',
    brand_id INT COMMENT '品牌ID',
    cover_image VARCHAR(500) COMMENT '封面图',
    images JSON COMMENT '图片列表',
    description TEXT COMMENT '商品描述',
    deposit DECIMAL(10,2) DEFAULT 0.00 COMMENT '押金',
    daily_rent DECIMAL(10,2) DEFAULT 0.00 COMMENT '日租金',
    single_rent DECIMAL(10,2) DEFAULT 0.00 COMMENT '单次租金',
    month_card_rent DECIMAL(10,2) DEFAULT 0.00 COMMENT '月卡租金',
    stock INT DEFAULT 1 COMMENT '库存',
    sizes JSON COMMENT '可选尺码',
    colors JSON COMMENT '可选颜色',
    is_hot BOOLEAN DEFAULT FALSE COMMENT '是否热门',
    is_new BOOLEAN DEFAULT FALSE COMMENT '是否新品',
    status TINYINT DEFAULT 1 COMMENT '状态(0下架1上架)',
    view_count INT DEFAULT 0 COMMENT '浏览量',
    rent_count INT DEFAULT 0 COMMENT '租赁次数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_category_id (category_id),
    INDEX idx_brand_id (brand_id),
    INDEX idx_is_hot (is_hot),
    INDEX idx_status (status),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- 商品搭配表
CREATE TABLE IF NOT EXISTS outfits (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '搭配ID',
    name VARCHAR(100) COMMENT '搭配名称',
    image VARCHAR(500) COMMENT '搭配图',
    description TEXT COMMENT '搭配说明',
    product_ids JSON COMMENT '包含的商品ID列表',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品搭配表';

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '订单ID',
    order_no VARCHAR(50) UNIQUE COMMENT '订单号',
    user_id INT NOT NULL COMMENT '用户ID',
    rental_type TINYINT DEFAULT 1 COMMENT '租赁类型(1按天2按次3订阅4单品租赁5套餐租赁)',
    total_rent DECIMAL(10,2) DEFAULT 0.00 COMMENT '租金总额',
    total_deposit DECIMAL(10,2) DEFAULT 0.00 COMMENT '押金总额',
    total_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '总金额',
    rent_days INT DEFAULT 0 COMMENT '租赁天数',
    start_date DATE COMMENT '开始日期',
    end_date DATE COMMENT '结束日期',
    pickup_time DATETIME COMMENT '取衣时间',
    expected_return_time DATETIME COMMENT '预期归还时间',
    door_lock_password VARCHAR(50) COMMENT '门锁密码',
    overdue_duration INT DEFAULT 0 COMMENT '逾期时长(小时)',
    address_id INT COMMENT '地址ID',
    status TINYINT DEFAULT 0 COMMENT '状态(0待支付1已支付待取衣2租赁中3逾期4已归还5已取消6退款中7已完成)',
    payment_time DATETIME COMMENT '支付时间',
    ship_time DATETIME COMMENT '发货时间',
    receive_time DATETIME COMMENT '收货时间',
    return_time DATETIME COMMENT '归还时间',
    refund_time DATETIME COMMENT '退款时间',
    refund_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '退款金额',
    remark VARCHAR(500) COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_order_no (order_no),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (address_id) REFERENCES addresses(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 订单商品表
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '订单商品ID',
    order_id INT NOT NULL COMMENT '订单ID',
    product_id INT NOT NULL COMMENT '商品ID',
    product_name VARCHAR(100) COMMENT '商品名称',
    product_image VARCHAR(500) COMMENT '商品图片',
    size VARCHAR(20) COMMENT '尺码',
    color VARCHAR(50) COMMENT '颜色',
    rent_price DECIMAL(10,2) DEFAULT 0.00 COMMENT '租金',
    deposit DECIMAL(10,2) DEFAULT 0.00 COMMENT '押金',
    quantity INT DEFAULT 1 COMMENT '数量',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单商品表';

-- 日期预订表
CREATE TABLE IF NOT EXISTS reservations (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '预订ID',
    product_id INT NOT NULL COMMENT '商品ID',
    reserved_date DATE NOT NULL COMMENT '预订日期',
    order_id INT NOT NULL COMMENT '订单ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_product_date (product_id, reserved_date),
    INDEX idx_order_id (order_id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日期预订表';

-- 订阅会员表
CREATE TABLE IF NOT EXISTS subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '会员ID',
    user_id INT NOT NULL COMMENT '用户ID',
    subscription_no VARCHAR(50) UNIQUE COMMENT '订阅号',
    package_id INT COMMENT '套餐ID',
    start_date DATE COMMENT '开始日期',
    end_date DATE COMMENT '结束日期',
    remaining_times INT DEFAULT 0 COMMENT '剩余次数',
    status TINYINT DEFAULT 0 COMMENT '状态(0未激活1激活中2已过期3已取消)',
    payment_time DATETIME COMMENT '支付时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_subscription_no (subscription_no),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订阅会员表';

-- 订阅套餐表
CREATE TABLE IF NOT EXISTS subscription_packages (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '套餐ID',
    name VARCHAR(50) COMMENT '套餐名称',
    price DECIMAL(10,2) DEFAULT 0.00 COMMENT '价格',
    days INT DEFAULT 30 COMMENT '有效天数',
    max_times INT DEFAULT 0 COMMENT '最大次数(0表示无限次)',
    description TEXT COMMENT '描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订阅套餐表';

-- 预约试穿表
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '预约ID',
    user_id INT NOT NULL COMMENT '用户ID',
    product_id INT NOT NULL COMMENT '商品ID',
    appointment_date DATE COMMENT '预约日期',
    appointment_time VARCHAR(20) COMMENT '预约时间',
    status TINYINT DEFAULT 0 COMMENT '状态(0待确认1已确认2已完成3已取消)',
    remark VARCHAR(500) COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_appointment_date (appointment_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预约试穿表';

-- 评价表
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评价ID',
    user_id INT NOT NULL COMMENT '用户ID',
    product_id INT NOT NULL COMMENT '商品ID',
    order_id INT COMMENT '订单ID',
    rating TINYINT COMMENT '评分(1-5)',
    content TEXT COMMENT '评价内容',
    images JSON COMMENT '图片列表',
    is_anonymous BOOLEAN DEFAULT FALSE COMMENT '是否匿名',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_order_id (order_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评价表';

-- 浏览记录表
CREATE TABLE IF NOT EXISTS browsing_history (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    product_id INT NOT NULL COMMENT '商品ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='浏览记录表';

-- 收藏表
CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '收藏ID',
    user_id INT NOT NULL COMMENT '用户ID',
    product_id INT NOT NULL COMMENT '商品ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_user_product (user_id, product_id),
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏表';
