-- ============================================================
-- 数据库迁移脚本 001 — 订单商品快照字段
-- 版本：Phase 6 工程规范化
-- 日期：2026-04-13
-- 说明：为 order_items 表新增商品价格/押金快照字段
--       解耦历史订单与商品主表，防止修改商品价格导致历史金额错乱
-- 执行：mysql -u root -p celestial_dev < 001_add_order_snapshot_fields.sql
-- ============================================================

-- 检查并添加 snapshot_price 字段（商品下单时的日租金快照）
ALTER TABLE order_items
  ADD COLUMN IF NOT EXISTS snapshot_price DECIMAL(10,2) NOT NULL DEFAULT 0.00
    COMMENT '下单时的商品日租金快照（与商品表解耦）'
  AFTER product_image;

-- 检查并添加 snapshot_deposit 字段（商品下单时的押金快照）
ALTER TABLE order_items
  ADD COLUMN IF NOT EXISTS snapshot_deposit DECIMAL(10,2) NOT NULL DEFAULT 0.00
    COMMENT '下单时的商品押金快照（与商品表解耦）'
  AFTER snapshot_price;

-- 回填存量数据：用 products 表当前值填充（历史数据只能近似，无法精确还原）
UPDATE order_items oi
  JOIN products p ON oi.product_id = p.id
SET
  oi.snapshot_price   = COALESCE(oi.rent_price, p.daily_rent, 0),
  oi.snapshot_deposit = COALESCE(oi.deposit, p.deposit, 0)
WHERE oi.snapshot_price = 0 AND oi.snapshot_deposit = 0;

-- 验证
SELECT
  COUNT(*) AS total_items,
  SUM(CASE WHEN snapshot_price > 0 THEN 1 ELSE 0 END) AS filled_items
FROM order_items;
