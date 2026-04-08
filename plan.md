Plan: Enhance Clothing Rental Mini-Program with Date-Based Reservations and Taro Refactor
Refactor existing WeChat mini-program frontend using Taro for cross-platform compatibility, enhance backend with date-based inventory locking, automatic status transitions, WeChat Pay integration (test mode), TTLock door lock integration, and deposit management. Ensure full 24-hour self-service rental flow with automatic inventory and status management, preserving code for future official merchant switch.

Steps

Database Schema Extensions (1-2 days): Extend MySQL schema to support date-based reservations, door lock passwords, and enhanced order tracking. Add fields to orders table (start_date, pickup_time, expected_return_time, door_lock_password, overdue_duration). Create reservations table for date-specific product locking. Update init.sql and connection logic.
Backend Business Logic Enhancements (3-5 days): Implement date-based product availability queries. Update order creation to lock dates on payment. Integrate WeChat Pay (test merchant) for unified orders and callbacks. Add TTLock API for generating/sending door passwords. Implement automatic status transitions (e.g., overdue checks on order access). Add deposit refund/deduction logic. Create admin APIs for order management, product CRUD, and deposit operations.
Frontend Refactor with Taro (4-6 days): Set up Taro project targeting WeChat mini-program. Migrate existing pages to Taro components, improving code reusability. Enhance date selection with calendar picker. Add missing UI features: better order confirmation with date selection, order details with status actions (pickup/return), admin interface pages (if mini-program based).
Integration and Testing (2-3 days): Integrate TTLock API (mock initially if API details unavailable). Conduct end-to-end testing for user flows (reservation, payment, pickup, return). Test concurrent bookings for inventory consistency. Validate payment callbacks and status auto-transitions.
Deployment and Validation (1-2 days): Deploy backend to test environment. Build and deploy Taro mini-program. Perform manual testing on real devices, focusing on payment and door lock flows. Ensure no regressions in existing features.
Relevant files

init.sql — Extend schema for reservations and order fields.
order.py — Enhance order creation, payment, status logic.
product.py — Add date-based availability queries.
settings.py — Add WeChat Pay and TTLock API configs (test keys).
frontend (entire) — Refactor to Taro structure, update pages like appointment/, orders/confirm/, add admin pages.
New: frontend/src/pages/admin/ — Admin interface for order/product management.
Verification

Unit tests for backend APIs (date locking, status transitions).
Integration tests for payment flow (mock WeChat Pay).
End-to-end user flow tests: Select date → Reserve → Pay → Receive password → Pickup → Return → Deposit refund.
Concurrent booking tests to ensure no double-bookings.
Manual validation: Test on WeChat dev tools and real devices, verify TTLock password generation (if API available).
Decisions

Use WeChat Pay test merchant for all payments; code structured to switch to official by updating config keys.
Refactor frontend to Taro for future cross-platform (H5, App), starting with WeChat mini-program target.
Admin interface as additional mini-program pages (simpler than separate web app).
TTLock integration: Generate passwords on payment success; store in order, send via SMS (deferred) or in-app.
Automatic status: Check on order access; add background job for cleanup if needed.
Deposits: Track in orders; refunds via WeChat Pay API.
Further Considerations

TTLock API details: Need API key, lock IDs, password generation rules — clarify integration requirements.
Admin interface scope: Full CRUD for products/orders, or minimal (confirm returns, manage deposits)?
Performance: Optimize date-based queries; consider caching for availability.
SMS integration: Deferred, but plan API hooks for sending passwords/notifications.





我现在有一个之前做的不完善的。你要不先解析这个项目（E:\AIProjects\202604@wechatAPP\backend和E:\AIProjects\202604@wechatAPP\frontend）。在制定计划。然后再可以基于这个开发，再加上taro。

Taro 不是一个“成品应用”或“业务框架”，而是一个跨端开发工具。它的核心价值在于：
跨端兼容：让你用一套 React/Vue 代码，编译成微信小程序、H5、App 等多个平台。无需为每个端写重复代码。
脚手架和基础工具：提供项目初始化（taro init）、路由管理、组件库（Taro UI）、状态管理等基础功能。
不提供业务逻辑：Taro 不内置任何业务功能（如电商、支付、用户管理）。它只是一个“开发环境”，类似 React 或 Vue 的脚手架。


继续吧。同时我要告诉你：
1-没有营业执照 = 你写的电商小程序 = 只能自己看，不能收钱、不能上线经营、用户不能付款。用 测试商户号 把 支付功能完整跑通
代码 100% 保留，等你办执照后 一键切换正式商户号
开发、测试、演示 完全不受影响。
2-信息发生到手机上这个功能不着急。可以后续开发再用。
3-着重完善业务功能：
一、文档说明
本文档为青岛单人自助租衣小程序完整功能需求，所有功能需全部实现，全程无需店主手动修改衣服状态、库存、预定信息，系统自动完成流转，适配24小时无人自助运营，不影响店主主业工作。
二、基础核心规则
1.租赁时长：统一固定24小时，不支持分时、半天租赁，不支持自定义时长。
2.时间计算逻辑：用户自主选择使用日期（提前预定），租赁开始时间为用户点击「我已取衣」时间，到期时间=取衣时间+24小时。
3.衣服全状态自动切换：
￮可租赁：无预定、未被租用，正常可下单
￮已预定：被用户提前锁定日期，他人不可选
￮租赁中：用户取衣后，不可被重复下单
￮已逾期：超过24小时未归还，衣服仍保持租赁中
￮已归还：店主确认还衣后，自动恢复可租赁状态
三、用户端完整操作流程
（一）提前预定流程（核心功能）
1.用户进入小程序，优先选择使用日期，系统自动筛选该日期可预约衣服。
2.选择租赁方式：单品租赁/3件套餐租赁。
3.挑选对应可租赁衣服，确认订单信息。
4.支付租金+对应押金，支付成功后，系统自动锁定该衣服所选日期，状态变为「已预定」，所选日期内他人无法选中、下单。
5.系统自动对接TTLock（通通锁），发送门店限时自助开门密码。
6.用户到店自助试穿、取衣，点击「我已取衣」，衣服状态由「已预定」自动变为「租赁中」，开始24小时计时。
7.租期内归还衣服，点击「我已还衣」，等待店主核验。
8.店主核验无误，确认还衣，衣服自动恢复可租赁状态，开放全日期预约。
（二）单品租赁流程
1.选择使用日期→挑选可租赁单品→支付租金+单品押金。
2.后续取衣、计时、还衣流程同上，取衣后单品自动变为租赁中，还衣后自动解锁。
（三）套餐租赁流程（租3件69.9元）
1.新增固定套餐：3件特惠套餐 69.9元/24小时，租金固定69.9元，不可更改。
2.用户选择使用日期，自选3件可租赁衣服，未预定、可预约衣服方可选择。
3.押金计算：按所选3件衣服押金自动叠加，生成总押金金额。
4.支付成功后，3件衣服同时锁定所选日期，状态变为「已预定」。
5.取衣后3件衣服同步变为「租赁中」，还衣确认后同步恢复可租赁状态。
四、押金管理规则
1.收取规则：单品按对应单品押金收取，套餐按所选衣物押金自动叠加收取。
2.退还规则：店主核验衣物无损坏、无逾期，后台一键原路全额退还押金。
3.扣款规则：衣物出现污渍、破损、配件丢失，或逾期未归还，店主可在后台手动选择扣款原因、输入扣款金额，扣除对应押金后，退还剩余押金。
五、全部特殊情况处理规则
1.预定/支付后取消订单
￮用户未取衣，可申请取消订单，租金+押金全额原路退还。
￮订单取消后，衣服对应预定日期锁定自动解除，状态恢复可租赁，已发密码自动作废。
2.预定后未按时取衣
￮超过使用日期24小时未取衣，订单标记「逾期未取」，衣服日期锁定自动解除，恢复可预约。
￮店主可根据实际情况，自主决定是否扣除部分押金。
3.逾期未归还衣物
￮超过24小时租期未还衣，订单状态变为「已逾期」，衣服保持租赁中，不可被他人租用。
￮系统自动统计逾期时长，不自动扣费，由店主核验后手动扣除押金。
4.提前归还衣物
￮支持用户24小时租期内提前归还，租金不予退还，还衣核验流程不变。
5.现场试穿后换款
￮用户到店试穿后可更换同价位可租赁衣服，需提前告知店主。
￮由店主在后台手动修改订单衣物，原衣物自动释放、恢复可租赁，新换衣物自动锁定，租金押金系统自动重新核算。
6.密码异常问题
￮密码过期、无法开门，店主可在后台重新发送新限时密码，旧密码自动失效，不影响订单及衣服状态。
7.同日衣物争抢问题
￮同一日期、同一件衣服，仅支持一单预定，先支付成功先锁定，未支付订单不锁定库存，杜绝重复租用。
六、店主后台功能要求
1.衣物管理：新增/编辑衣物，填写编号、图片、租金、押金、尺码，查看衣物全状态。
2.订单管理：查看所有订单详情、预定日期、取衣时间、到期时间、逾期状态、订单类型。
3.一键操作：确认还衣、一键退还押金、手动修改订单衣物、重新发送/作废开门密码。
4.押金管理：查看押金收取、退还、扣款记录，支持全额退、部分扣押金操作。
5.库存管理：系统自动同步库存、预定状态，无需人工手动调整。
七、系统对接要求
1.支付对接：接入微信支付，支持租金、押金支付，押金原路退款功能。
八、核心需求总结
实现按日期提前预定、单日单衣仅一单、支付自动锁定库存、状态自动切换、套餐自助下单、押金自动核算与灵活退还，全程无人值守，店主仅需线上处理换款、线下核验衣物、操作退押，无需人工干预系统流程。


现在继续分析现有后端业务逻辑，确认订单和衣物状态字段是否支持无人自助全流程。

正在确认数据库表结构，判断现有订单/商品字段是否支持24小时自助租赁逻辑。

已确认当前表结构未支持日期锁定与取衣时间记录，下一步补充关键表字段和订单流程。

现在检查前端现有订单页面是否有取衣/还衣入口，以便补全业务流程。

正在定位订单详情页路径，确认前端现有交互入口。

继续搜索前端订单详情页面文件。

继续确认前端订单确认页面和现有下单入口，以便结合业务流程改造。

已发现核心缺失：订单表缺少取衣、预期归还、门锁密码字段。先补齐数据库定义。

已定位订单模块入口，准备补入业务核心辅助函数。

订单创建逻辑将改为按使用日期锁定商品，并切换为按日期可用量检查。

Edited
order.py+40-22
订单创建后续改为按日期库存锁定，不再直接扣减全局库存。

准备更新取消订单逻辑，支持已支付订单取消并记录全额退款。

Edited
order.py+9-15
继续完善归还申请与门锁密码管理。

订单详情与列表将显示新增的取衣/归还/门锁状态字段。

追加过期预定自动释放逻辑，确保访问订单时先清理逾期未取情形。

正在补充支付回调后订单状态与门锁密码生成。

需要更新商品查询接口，按选择日期返回可预约商品。

已经完成业务和可用性补充，接下来检查后端语法是否正确。

继续检查前端订单确认页，确认是否需要补上使用日期字段。

前端订单确认页必须传 start_date 给后端，否则新规则会失败。现在把日期选择加上。



🧪 测试策略
Phase 1: 环境准备 (1-2天)
数据库环境

部署测试数据库
导入初始商品数据
配置测试用户账号
微信配置

设置小程序测试版本
配置微信支付沙箱环境
获取测试AppID和密钥
后端部署

部署FastAPI服务到测试环境
配置环境变量
验证API接口可用性
Phase 2: 功能测试 (3-4天)
2.1 用户流程测试
注册登录：微信授权 → 用户信息存储 → Token管理
商品浏览：列表加载 → 详情查看 → 搜索筛选
订单创建：日期选择 → 商品添加 → 费用计算 → 订单提交
2.2 支付流程测试
统一下单：订单支付请求 → 微信支付参数生成
支付回调：微信回调处理 → 订单状态更新 → 业务逻辑执行
支付结果：成功跳转 → 失败处理 → 订单详情显示
2.3 订单管理测试
订单列表：分页加载 → 状态筛选 → 订单搜索
订单详情：完整信息显示 → 操作按钮可用性
状态流转：自动状态转换 → 手动操作验证
2.4 库存管理测试
日期库存：预订时锁定 → 过期自动释放
并发处理：多用户同时预订 → 库存一致性
边界情况：库存不足 → 预订失败处理
Phase 3: 异常测试 (1-2天)
网络异常：请求超时 → 重试机制
支付异常：支付失败 → 订单回滚
数据异常：无效输入 → 错误处理
并发冲突：库存竞争 → 事务处理
Phase 4: 性能和兼容性测试 (1天)
响应时间：API响应 < 2秒
小程序兼容性：不同微信版本测试
数据量测试：大量订单处理

✅ 验收标准
 所有核心业务流程正常运行
 支付成功率 > 95%
 用户操作响应时间 < 2秒
 无影响核心功能的bug
 库存管理逻辑正确
 订单状态流转准确


管理员后端界面（订单管理、用户管理等）


 🚨 风险识别
微信支付集成：需要真机测试，沙箱环境可能不完全模拟生产
小程序审核：首次提交可能需要多次审核
库存并发：高并发预订可能出现竞争条件
日期逻辑：跨日期的租赁逻辑需要仔细验证


实现的功能：
 微信支付集成（统一下单 + 回调处理）
 日期-based预订系统（库存锁定 + 自动过期）
 订单状态自动转换（0-7状态流转）
 押金管理（退还/扣除逻辑）
 前端订单确认和详情页面
 用户认证和商品管理基础功能
 管理员后端界面（订单管理、用户管理等）
 完整的端到端测试验证