# 小时光租衣舍 — 开发主计划 & 测试计划

> **项目编号**：007/100  
> **技术栈**：FastAPI + MySQL + 微信小程序原生 + DeepSeek/Gemini  
> **最后更新**：2026-04-13  
> **配合文档**：[需求文档 PRD](./PRD.md) · [设计方案 DESIGN](./DESIGN.md)

---

## 📦 一、整体进度总览

| Phase | 主题 | 关键内容 | 状态 |
|---|---|---|---|
| Phase 1 | 核心业务逻辑 | 24h计时、3件套餐、订单状态机 | ✅ 完成 |
| Phase 2 | 店主管理与支付框架 | 订单管理、退押/扣费、微信支付框架 | ✅ 完成 |
| Phase 3 | MVP 精简与闭环 | 核心流程贯通，非核心功能入口隐藏 | ✅ 完成 |
| Phase 4 | 身份与权限调试 | Mock openid、role(1/2) 权限分流 | ✅ 完成 |
| Phase 5 | 高奢审美重构 | 莫兰迪UI、沉浸导航、原子组件库 | ✅ 完成 |
| **Phase 6** | **工程规范化（进行中）** | **多环境、安全加固、全局错误处理** | 🚀 进行中 |
| Phase 7 | 数据解耦与JSON化 | 静态数据抽离，为后端接口对接准备 | ⏳ 规划 |
| Phase 8 | 目录规范化 | 前后端目录整理、组件补全 | ⏳ 规划 |
| Phase 9 | Git规范 & CI | 分支策略、提交规范 | ⏳ 规划 |
| Phase 10 | 上线前验收 | 逐项检查清单，切换生产环境 | ⏳ 规划 |

---

## ✅ 二、已完成工作详情（Phase 1-5）

### Phase 1：核心业务逻辑

- [x] 数据库：`reservations` 表日期锁定，订单逾期字段支持
- [x] `order.py`：`create_order`（套餐逻辑）、`pickup_order`（24h倒计时）、`return_order`（申请归还）、逾期时长计算
- [x] `product.py`：按日期筛选，已预定衣物在列表中过滤

### Phase 2：店主管理与支付框架

- [x] 后端新增 `role` 字段区分管理员
- [x] 全量订单查询 API（支持搜索与状态筛选）
- [x] 店主端前端：订单列表、订单详情（退押 / 扣费 / 换款）
- [x] 微信支付 V3 框架封装（签名验证、退款调用链路），当前为模拟模式

### Phase 3：MVP 精简与闭环

- [x] 用户端核心闭环：选日期 → 选衣 → 下单 → 支付（模拟）→ 取衣（24h计时）→ 还衣 → 待审核
- [x] 店主端核心闭环：全量订单 → 退押/扣费
- [x] 非核心功能（收藏、评价、搭配、订阅）入口隐藏，代码保留

### Phase 4：身份与权限调试

- [x] Mock 固定身份：设置页填写 `mockOpenid` → 点击"重新登录"可固定账号
  - 普通用户：`user_1`
  - 管理员：`admin_1`
- [x] 权限分流：role `1/user` → 用户端，`2/admin` → 店主端自动跳转
- [x] 套餐商品管理（店主可配置哪些衣物参与套餐）

### Phase 5：高奢审美与架构重构

- [x] `theme.wxss` 设计变量系统（莫兰迪色系）
- [x] `app.wxss` 全站基础样式重构（卡片/Glassmorphism）
- [x] `cp-nav-bar` 组件（沉浸式自定义导航，支持透明渐变）
- [x] `cp-product-card` 组件（3:4 比例、骨架屏、价格右下角悬浮）
- [x] 胶囊按钮位置计算（`getNavBarData`），适配 iOS/Android 安全区
- [x] 全站 Emoji 替换为线条矢量图标

---

## 🚀 三、进行中：Phase 6 — 工程规范化

> **目标**：消除安全隐患，建立多环境体系，达到"可交付"标准。

### 6.1 安全加固（🔴 优先级最高）

- [ ] **微信登录修复**：`backend/app/api/user.py` 的 `login()` 函数，从哈希 code 改为真实调用 `jscode2session` API 获取 openid
  - 涉及文件：`backend/app/api/user.py`
- [x] **密钥迁移**：`settings.py` 中的 `JWT_SECRET_KEY`、`DB_PASSWORD` 不留默认值，强制从 `.env` 读取 ✅
  - 涉及文件：`backend/config/settings.py`
- [x] **微信登录修复**：`backend/app/api/user.py` 的 `login()` 函数，从哈希 code 改为真实调用 `jscode2session` API ✅
- [ ] **生产 CORS 限制**：`CORS_ORIGINS` 生产环境改为 `["https://servicewechat.com"]`（prod 启动时配置）

### 6.1.1 P0 业务安全修复（已完成）

- [x] **订单商品快照**：`order.py` 下单时固化 `snapshot_price` / `snapshot_deposit`，修改商品价格不影响历史订单 ✅
- [x] **套餐服务端校验**：防重复选/非资格商品进套餐，前端禁用 = 形同虚设问题已解决 ✅
- [x] **数据库迁移**：`backend/database/migrations/001_add_order_snapshot_fields.sql` 已生成 ✅

### 6.2 多环境配置体系

> 📄 **完整设计文档**：[docs/ENV.md](./docs/ENV.md)（已创建，覆盖前端/后端/Git分支完整设计）

- [x] 环境设计文档 `docs/ENV.md` 已建立（dev/test/prod 三套策略）
- [x] `frontend/config/env.js` 已新建（envVersion 自动识别）
- [x] `backend/.env.example` 已更新
- [x] `frontend/app.js` 重构：已接入 `config/env.js`，移除硬编码 IP ✅
- [x] `backend/config/settings.py` 改造：支持 `APP_ENV` 动态加载，密钥字段无默认值 ✅
- [x] 新建 `backend/.env.test`：填写测试服务器地址（无真实密钥，可提交 git） ✅

### 6.3 全局错误处理

- [x] **后端**：新建 `backend/app/middleware/error_handler.py`，注册全局异常处理器 ✅
- [x] **后端**：所有路由的响应统一为 `{code, message, data}` 格式，不直接抛出 500 ✅
- [x] **前端**：`frontend/utils/request.js`（从 app.js 中抽离 `request` 方法），增加统一错误日志 ✅

### 6.4 API 版本控制

- [x] 所有路由前缀从 `/api/xxx` 改为 `/api/v1/xxx` ✅
- [x] 前端 `api.js` 和 `app.js` 同步更新所有请求路径 ✅

### 6.5 .gitignore 补全

- [x] 根目录 `.gitignore` 已补充 `backend/.env`、`backend/.env.prod` ✅

---

## ⏳ 四、规划中任务（Phase 7-10）

### Phase 7：数据解耦与 JSON 化

- [x] 新建 `frontend/data/` 目录 ✅
- [x] 抽离静态配置数据： ✅
  - `categories.json`（服装分类）
  - `packages.json`（套餐配置）
  - `faq.json`（AI客服常见问题）
- [x] FAQ 功能已在 `chat` 页面通过 `require` 引入并完成本地快速联想回复，降低 API 请求频率 ✅

### Phase 8：前后端目录规范化

**前端新增**：
- [x] `frontend/config/env.js`（多环境） ✅
- [x] `frontend/data/`（静态数据） ✅
- [x] `frontend/components/cp-countdown/`（24h环形倒计时） ✅
- [x] `frontend/components/cp-empty/`（空状态组件） ✅
- [x] `frontend/utils/request.js`（从 app.js 中拆出） ✅
- [x] `frontend/utils/auth.js`（前端 token/权限工具） ✅
- [x] `frontend/pages/admin/inventory/`（库存管理：商品列表/新增/编辑，对应 PRD F23） ✅
- [x] 将 `pages/address`、`pages/appointment`、`pages/review`、`pages/subscribe`、`pages/product` 移入 `pages/_inactive/` ✅

**后端新增**：
- [x] `backend/app/middleware/`（错误处理、日志） ✅
- [x] `backend/database/migrations/`（数据库变更记录） ✅
- [x] 清理 `taro-main/` 空壳目录 ✅

### Phase 9：服务器配置与自动部署 (开发-测试-正式环境流转)

**前端流转机制**：
- [x] `env.js` 根据微信工具自动判断版本（开发/体验/正式）切换 HTTP 终点。
- [ ] CI/CD：配合微信 MiniProgram CI 构建脚本，实现推送到 Git 特定分支后自动上传发版。

**后端与运维基建**：
- [ ] **域名与部署**：
      - 申请商用域名备案（国内上线强制）。
      - 服务器配置 Nginx 反向代理，并申请 SSL 证书（小程序访问强制要求 `https://`）。
- [ ] **物理环境隔离**：
      - 在服务器上建立对应的独立数据库实例：`celestial_dev` / `celestial_test` / `celestial_prod`。
      - 确保 `prod` 环境数据库挂载云盘快照或每日增量备份（Daily Backup）。
- [ ] **进程守护**：
      - 使用 `Gunicorn + Uvicorn` 并在 `Systemd` / `Supervisor` 托管下执行后台 Python 生产级进程。
- [ ] **微信官方校验**：
      - 将正式版本域名加入微信小程序后台的「服务器域名 -> 合法 request 域名白名单」。

### Phase 10：上线前最终验收清单 (Checklist)

**安全与权限查漏补缺**：
- [x] 🔐 `JWT_SECRET_KEY` 已从环境变量注入，无默认值
- [x] 🔐 微信登录使用真实 `jscode2session` 接口
- [x] 🔐 数据库密码不出现在代码仓库
- [x] 🔑 店主端所有接口均校验 role=admin（前端拦截 + 后端双重）
- [x] 🌐 `prod` 环境 `DEBUG=False`，`mock_openid` 功能自动降权失效
- [ ] 🔐 后端 `CORS_ORIGINS` 配置已从通配符 `*` 缩紧限制为微信服务域名

**外部接入真实性替换**：
- [ ] 💳 **微信支付闭环**：以 V3 证书对接 `WechatPay`，替换代码内的“模拟支付成功”，实装退押金、提现的原路返回链路。
- [ ] 🤖 **大模型正式 API**：将测试用的 `sk-test-xxx` 置换为包月/充值账户密钥，并配置超时/余额不足降级的硬编码回复方案。
- [ ] 🔓 **智能锁接入（可选进阶）**：对接到店自提的蓝牙/网络 TTLock。

**上架政策合规**：
- [ ] 📋 **用户协议与隐私**：小程序提供《用户协议与隐私政策》页面。
- [ ] 📋 **功能权限声明**：在微信后台注册声明收集 `昵称`、`头像`、`手机号`、`地理位置`（如适用）的用途。
- [ ] 📱 真机（iOS + Android）全流程点击无白屏报错测试，生成公测报告。

---

## 🧪 五、测试计划

> 原 `test_plan.md` 内容已整合于此。

### 5.1 测试环境准备

```bash
# 1. 初始化/检查数据库
cd backend
python check_db.py

# 2. 启动后端服务
python main.py

# 3. 身份提权（SQL）
UPDATE users SET role = 'admin' WHERE id = 1;

# 4. Mock 登录（小程序设置页）
# 普通用户：填写 mockOpenid = user_1
# 管理员：填写 mockOpenid = admin_1
```

### 5.2 用户端核心流程测试

#### T01 — 日期优先筛选

| # | 测试项 | 预期结果 | 状态 |
|---|---|---|---|
| T01-1 | 进入首页，日期选择是否强制弹出 | 弹出全屏日历，商品列表不显示 | ⬜ 待测 |
| T01-2 | 手动预订某衣物至日期A → 刷新 | 该衣物在日期A的列表中消失 | ⬜ 待测 |

#### T02 — 3件69.9元套餐

| # | 测试项 | 预期结果 | 状态 |
|---|---|---|---|
| T02-1 | 选择0-2件时点击下单 | 按钮禁用，无法提交 | ⬜ 待测 |
| T02-2 | 尝试选第4件 | 弹出"套餐仅限3件"提示 | ⬜ 待测 |
| T02-3 | 选满3件确认订单 | 总额 = 69.9 + 3件押金之和 | ⬜ 待测 |

#### T03 — 24小时租赁计时

| # | 测试项 | 预期结果 | 状态 |
|---|---|---|---|
| T03-1 | 点击「我已取衣」 | 订单状态 "待取衣" → "租赁中"，计时开始显示 | ⬜ 待测 |
| T03-2 | 详情页倒计时显示 | 秒级刷新，环形仪表盘正常显示 | ⬜ 待测 |
| T03-3 | 点击「我已还衣」 | 计时停止，状态变为"待审核" | ⬜ 待测 |

#### T04 — AI 智能客服

| # | 测试项 | 预期结果 | 状态 |
|---|---|---|---|
| T04-1 | 询问"套餐多少钱" | AI 准确回答 69.9 元及规则 | ⬜ 待测 |
| T04-2 | 询问"怎么取衣服" | AI 描述到店取衣步骤 | ⬜ 待测 |
| T04-3 | 切换 AI_SERVICE_TYPE | DeepSeek / Gemini 均能正常响应 | ⬜ 待测 |

### 5.3 店主端管理流程测试

#### T10 — 订单全量检索

| # | 测试项 | 预期结果 | 状态 |
|---|---|---|---|
| T10-1 | 普通用户身份进入个人中心 | 不显示"店铺管理"入口 | ⬜ 待测 |
| T10-2 | 管理员身份登录 | 自动跳转至店主端，"全部订单"正确显示 | ⬜ 待测 |
| T10-3 | 按状态筛选订单 | 数据过滤准确 | ⬜ 待测 |
| T10-4 | 搜索用户昵称/订单号后4位 | 精准定位订单 | ⬜ 待测 |

#### T11 — 财务结算操作

| # | 测试项 | 预期结果 | 状态 |
|---|---|---|---|
| T11-1 | 一键退押（待审核订单） | 订单状态 → "已完成"，退款金额正确 | ⬜ 待测 |
| T11-2 | 手动扣费（输入金额+原因） | 退款总额 = 押金 - 扣费额，备注显示 | ⬜ 待测 |
| T11-3 | 扣费后查看订单详情 | 操作备注信息正确显示 | ⬜ 待测 |

#### T12 — 换款操作

| # | 测试项 | 预期结果 | 状态 |
|---|---|---|---|
| T12-1 | 针对"待取衣"订单修改衣物ID | 订单押金随之更新 | ⬜ 待测 |

### 5.4 边界与安全测试

| # | 测试项 | 预期结果 | 状态 |
|---|---|---|---|
| S01 | 同一衣物同一日期并发下单 | 数据库事务保证唯一，只有一个订单创建成功 | ⬜ 待测 |
| S02 | 手动拼接 URL 访问管理员页 | 后端鉴权拦截，返回 403 | ⬜ 待测 |
| S03 | 运行 `python check_db.py` | 15张核心表均已成功创建 | ⬜ 待测 |
| S04 | Token 过期后发起请求 | 自动触发重新登录，用户无感知 | ⬜ 待测 |

---

## 📋 六、外部系统对接（待执行）

| 系统 | 状态 | 说明 |
|---|---|---|
| **微信真实登录**（jscode2session） | ❌ 未接入 | 当前用 MD5 哈希，上线必须接入 |
| **微信支付 V3** | 🔲 框架就绪 | 证书未配置，模拟支付中 |
| **TTLock 智能锁** | 🔲 接口预留 | `door_lock_password` 字段保留，暂不调用 |

---

*此文件取代原 `plan.md` 和 `test_plan.md`，两者内容已合并并去重。*  
*如需查看历史 Phase 记录，见 `README/` 目录。*
