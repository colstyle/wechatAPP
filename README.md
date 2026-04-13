<div align="center">

# 👗 小时光租衣舍 (Time Capsule Clothing Rental)

**24小时自助租衣小程序。日期预约、套餐优惠、AI智能客服。**

![Project Status](https://img.shields.io/badge/状态-Phase%208%20全量架构收官-success?style=flat-square)
![Platform](https://img.shields.io/badge/平台-WeChat%20Mini%20Program%20%7C%20FastAPI-blue?style=flat-square)
![Tech Stack](https://img.shields.io/badge/技术栈-FastAPI%20%2B%20MySQL%20%2B%20DeepSeek-blueviolet?style=flat-square)
![Env](https://img.shields.io/badge/环境-dev%20%7C%20test%20%7C%20prod-lightgrey?style=flat-square)

</div>

---

## ✨ 核心特性

- 📅 **沉浸式预约体验** — 仪式感全屏日历选择，库存实时锁定，杜绝超卖。
- 🎁 **3件69.9套餐** — 固定租金 + 阶梯押金，自动计算最优组合。
- ⏲️ **可视化 24h 租赁** — 以取衣激活，环形倒计时精细化展示，后端自动计算逾期。
- 🤖 **AI 灵感客服** — 集成 DeepSeek-V3/Gemini，解答业务问题并提供穿搭灵感。
- 💎 **高奢视觉设计** — 莫兰迪色系、沉浸式自定义导航、Design Token 系统。

## ✅ 当前版本能力

- 🏪 **线下自助取衣** — 下单不依赖收货地址，适配到店自助取还。
- 💳 **支付流程** — 内置支付页面与状态流转（当前为模拟支付，v1.1 接入真实）。
- 🧑‍💼 **店主端管理** — 全量订单查询、退押金、手动扣费、换款、套餐配置。
- 📦 **库存可视化管控** — 实装了专属独立表单管理库存状况；关联订单时启用安全挂起的软删除以保障金融对账稳定性。
- 🧩 **身份与权限** — 完善 `auth.js`，通过 Token与用户 `role` 自动拦截跨权越界操作；支持 Mock 开发者免签直通调试。
- 🌐 **高防多环境引擎** — dev / test / prod 随微信编译配置动态平滑切换，搭配后端中间件的防报错机制全面兜底上线体验。

---

## 📚 项目文档索引

| 文档 | 路径 | 说明 |
|---|---|---|
| **产品需求文档** | [docs/PRD.md](./docs/PRD.md) | 功能需求 F01-F23、RBAC 权限、验收标准 |
| **设计方案** | [docs/DESIGN.md](./docs/DESIGN.md) | Design Tokens、组件规范、交互规范 |
| **多环境策略** | [docs/ENV.md](./docs/ENV.md) | dev/test/prod 配置、Git 分支映射、上线检查清单 |
| **开发与测试计划** | [docs/PLAN.md](./docs/PLAN.md) | Phase 进度总览、测试用例、外部对接清单 |
| **全栈架构大版本** | [README/](./README/) | 记录 Phase6-8 的历史重要决策及业务修正 (如快照制引入) |

---

## 🚀 快速启动

### 环境要求

| 工具 | 用途 | 建议版本 |
|---|---|---|
| **Python** | FastAPI 后端 | ≥ 3.9 |
| **MySQL** | 数据持久化 | ≥ 5.7 |
| **微信开发者工具** | 小程序前端调试 | 最新稳定版 |
| **OpenAI SDK** | DeepSeek / Gemini 接入 | 最新版 |

### 1. 后端启动（FastAPI）

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 复制环境配置（首次使用）
cp .env.example .env
# 编辑 .env，填写 DB_PASSWORD 和 JWT_SECRET_KEY

# 初始化数据库表结构
python check_db.py

# 启动服务（开发模式，自动热重载）
python main.py
```

> 多环境启动：`APP_ENV=test python main.py`（详见 [docs/ENV.md](./docs/ENV.md)）

### 2. 前端启动（微信小程序）

1. 用微信开发者工具打开 `frontend/` 目录。
2. 环境配置已**自动化**：工具打开即为 dev 环境，体验版为 test，正式版为 prod（无需手动修改代码）。
3. 如需覆盖开发环境 API 地址：在小程序「设置」页填写局域网 IP，如 `http://192.168.43.79:8000`。

### 3. 调试身份切换（Mock 登录）

> 仅在 dev / test 环境生效，prod 环境自动关闭。

在小程序「设置」页填写 `mockOpenid` 后点击「重新登录」：

| mockOpenid 值 | 身份 |
|---|---|
| `user_1` | 普通用户 |
| `admin_1` | 店主/管理员 |

---

## 📂 项目结构

```
202604@wechatAPP/
├── docs/                               ← 📚 项目正式文档（本次新建）
│   ├── PRD.md                          ← 产品需求文档 v1.1
│   ├── DESIGN.md                       ← 设计方案（Design Tokens/组件规范）
│   ├── ENV.md                          ← 多环境策略设计
│   └── PLAN.md                         ← 开发计划 & 测试计划（主计划文档）
├── backend/                            ← FastAPI 后端
│   ├── app/
│   │   ├── api/                        ← 业务路由层
│   │   │   ├── admin.py                ← 店主端：订单/退押/扣费/换款/库存管理
│   │   │   ├── ai.py                   ← AI 客服（DeepSeek/Gemini）
│   │   │   ├── order.py                ← 下单/支付/取衣/还衣/状态流转
│   │   │   ├── product.py              ← 商品/分类/品牌/库存 CRUD
│   │   │   ├── user.py                 ← 登录/用户资料
│   │   │   └── ...                     ← review/subscription/appointment（预留）
│   │   └── utils/
│   │       ├── auth.py                 ← JWT 鉴权 + require_admin 依赖
│   │       └── wechat_pay.py           ← 微信支付 V3 框架（模拟）
│   ├── config/
│   │   └── settings.py                 ← 多环境配置（APP_ENV 驱动）
│   ├── database/
│   │   ├── connection.py               ← 数据库连接封装
│   │   └── init.sql                    ← 初始化建表脚本
│   ├── .env.example                    ← 环境变量模板（可提交）
│   ├── .env.test                       ← 测试环境模板（可提交，无真实密钥）
│   ├── check_db.py                     ← 数据库自检/初始化
│   ├── seed_db.py                      ← 测试数据种子
│   └── main.py                         ← 后端启动入口
├── frontend/                           ← 微信小程序（原生）
│   ├── config/
│   │   └── env.js                      ← 🌐 多环境配置（envVersion 自动切换）
│   ├── styles/
│   │   └── theme.wxss                  ← Design Token 变量定义
│   ├── components/
│   │   ├── cp-nav-bar/                 ← 沉浸式自定义导航栏
│   │   └── cp-product-card/            ← 高级商品卡片（3:4/骨架屏）
│   ├── utils/
│   │   ├── api.js                      ← API 聚合层（user/product/order/admin）
│   │   └── util.js                     ← 通用工具函数
│   ├── pages/
│   │   ├── index/                      ← 首页：日历选日期 + 商品列表
│   │   ├── category/                   ← 分类浏览
│   │   ├── detail/                     ← 商品详情 + 立即预定
│   │   ├── orders/                     ← 我的订单列表 + 下单确认
│   │   ├── order/                      ← 订单详情：取衣/还衣/倒计时
│   │   ├── pay/                        ← 支付页（模拟）
│   │   ├── chat/                       ← AI 客服全屏对话
│   │   ├── profile/                    ← 个人中心
│   │   ├── settings/                   ← 开发者设置（dev/test 环境可见）
│   │   └── admin/                      ← 店主端：订单/库存/套餐管理
│   ├── app.js                          ← 全局登录态/请求封装
│   ├── app.json                        ← 页面注册/tabBar 配置
│   └── app.wxss                        ← 全局基础样式
├── README/                             ← 各阶段更新详细日志
├── .gitignore                          ← 含 .env / .env.prod 保护
├── plan.md                             ← （同 docs/PLAN.md，根目录快捷访问）
└── README.md                           ← 本文件
```

---

## 🛠️ 技术栈

| 层 | 技术 | 说明 |
|---|---|---|
| **前端** | 微信小程序原生 | WXML + WXSS + JS，无框架依赖 |
| **后端** | FastAPI + Uvicorn | Python 异步 Web 框架 |
| **数据库** | MySQL 5.7+ + PyMySQL | 手写 SQL，无 ORM 抽象层 |
| **鉴权** | JWT Bearer Token | `python-jose` 生成，7天有效期 |
| **AI** | DeepSeek-V3 / Gemini 1.5 | 通过 `AI_SERVICE_TYPE` 切换 |
| **支付** | 微信支付 V3 | 框架已就绪，当前为模拟模式 |

---

## 📅 Phase 进度总览

| 阶段 | 主题 | 核心内容 | 状态 |
|---|---|---|---|
| Phase 1 | [业务逻辑与AI基座](./README/20260409_Phase1_BusinessLogic_AI.md) | 24h计时、3件套餐、DeepSeek接入 | ✅ 完成 |
| Phase 2 | [店主管理与支付框架](./README/20260409_Phase2_Admin_Payment.md) | 店主订单管理、微信支付V3框架 | ✅ 完成 |
| Phase 3 | [MVP 精简与闭环](./README/20260409_Phase3_MVP_Simplification.md) | 选衣→下单→取衣→还衣 核心闭环 | ✅ 完成 |
| Phase 4 | [身份与权限调试](./README/20260409_Phase4_Identity_Role_Mock.md) | Mock身份、role权限分流 | ✅ 完成 |
| Phase 5 | [高奢审美与架构重构](./README/20260410_Phase5_Aesthetic_Refactor.md) | 莫兰迪UI、沉浸导航、原子组件库 | ✅ 完成 |
| **Phase 6** | **工程规范化** | **多环境、安全加固、全局错误处理** | 🚀 进行中 |
| Phase 7 | 数据解耦 | 静态 JSON 化，接口对接准备 | ⏳ 规划 |
| Phase 8 | 目录规范化 | 前后端目录整理、组件补全 | ⏳ 规划 |
| Phase 9-10 | Git规范 & 上线 | 分支策略、上线验收清单 | ⏳ 规划 |

> 详细任务列表见 [docs/PLAN.md](./docs/PLAN.md)

---

## 🌐 多环境说明

| 环境 | 触发方式 | API 地址 | Mock 登录 |
|---|---|---|---|
| **dev**（开发版）| 微信开发者工具打开 | 局域网 IP（设置页可改）| ✅ 允许 |
| **test**（体验版）| 上传为体验版后扫码 | 测试服务器（ENV.md 配置）| ✅ 允许 |
| **prod**（正式版）| 小程序商店发布版本 | 正式 HTTPS 域名 | ❌ 禁止 |

> 环境切换**全自动**，无需修改代码。详见 [docs/ENV.md](./docs/ENV.md)。

---

## 🔑 Git 工作流

```bash
# 日常开发（在 dev 分支）
git checkout dev
git checkout -b feature/your-feature
git add . && git commit -m "feat: 描述改动"
git push origin feature/your-feature
# → 发起 PR 合并到 dev

# 发布测试版（体验版）
git checkout test && git merge dev && git push origin test
# → 微信开发者工具上传为「体验版」

# 发布正式版
git checkout main && git merge test && git push origin main
# → 微信开发者工具提交审核 → 发布
```

提交信息规范：`feat:` / `fix:` / `refactor:` / `docs:` / `chore:`

---

## 📄 许可证

MIT License · **小时光租衣舍 007/100** © 2026
