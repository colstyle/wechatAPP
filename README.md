<div align="center">

# 👗 小时光租衣舍 (Time Capsule Clothing Rental)

**24小时自助租衣小程序。日期锁定、套餐优惠、AI智能客服。**

![Project Status](https://img.shields.io/badge/状态-Phase%203%20MVP-yellow?style=flat-square)
![Platform](https://img.shields.io/badge/平台-WeChat%20Mini%20Program%20%7C%20FastAPI-blue?style=flat-square)
![Tech Stack](https://img.shields.io/badge/技术栈-FastAPI%20%2B%20MySQL%20%2B%20DeepSeek-blueviolet?style=flat-square)

</div>

---

## ✨ 核心特性

- 📅 **日期优先预约** — 强制用户先选日期再看衣服，确保库存实时锁定，杜绝超卖。
- 🎁 **3件69.9套餐** — 灵活的套餐逻辑，固定租金+阶梯押金，自动计算最优组合。
- ⏱️ **24h 精准租赁** — 以“取衣”动作激活计时器，前端实时倒计时，后端自动计算逾期。
- 🤖 **AI 智能客服** — 集成 DeepSeek-V3/Gemini，预置业务知识库，提供 7x24h 咨询服务。
- 💰 **极简退押逻辑** — 店主端一键原路退还押金，支持因逾期或损毁手动扣费。

## ✅ 当前版本能力

- 🏪 **线下自助取衣** — 下单流程不依赖收货地址，适配到店自助取还。
- 💳 **支付流程** — 内置支付页面与支付成功状态流转（当前为模拟支付）。
- 🧑‍💼 **店主端管理** — 管理端订单列表/详情，支持退押金与手动扣费。

---

## 🚀 开发者指南

### 环境要求

| 工具 | 用途 | 建议版本 |
|------|------|---------|
| **Python** | FastAPI 后端开发 | ≥ 3.9 |
| **MySQL** | 数据持久化 | ≥ 5.7 |
| **微信开发者工具** | 小程序前端开发 | 最新稳定版 |
| **OpenAI SDK** | DeepSeek 接入 | 最新版 |

### 快速启动

#### 1. 后端配置 (FastAPI)
```bash
cd backend
pip install -r requirements.txt
# 复制并配置 .env 文件
cp .env.example .env
# 检查并初始化数据库
python check_db.py
# 启动服务
python main.py
```

#### 2. 前端配置 (WeChat)
- 使用微信开发者工具打开 `frontend` 目录。
- 修改 [frontend/app.js](file:///e:\AIProjects\202604@wechatAPP\frontend\app.js) 中的 `apiBase` 指向您的后端地址。

---

## 📂 项目结构
```
202604@wechatAPP/
├── backend/                            ← FastAPI 后端
│   ├── app/
│   │   ├── api/                        ← 业务路由层
│   │   │   ├── admin.py                ← 店主端：订单检索/退押/扣费/换款
│   │   │   ├── ai.py                   ← AI 客服 (DeepSeek/Gemini)
│   │   │   ├── appointment.py          ← 预约相关
│   │   │   ├── order.py                ← 下单/支付/取衣/还衣/订单查询
│   │   │   ├── product.py              ← 商品/分类/品牌/收藏等
│   │   │   ├── review.py               ← 评价体系
│   │   │   ├── subscription.py         ← 订阅/套餐相关
│   │   │   └── user.py                 ← 登录/用户资料/地址等
│   │   └── utils/
│   │       └── wechat_pay.py           ← 微信支付 V3 框架封装（可模拟）
│   ├── config/
│   │   └── settings.py                 ← 系统配置（DB、AI、CORS等）
│   ├── database/
│   │   ├── connection.py               ← 数据库连接与封装
│   │   └── init.sql                    ← 初始化建表脚本
│   ├── check_db.py                     ← 初始化/自检数据库表结构
│   ├── seed_db.py                      ← 测试数据种子脚本
│   ├── main.py                         ← 后端启动入口
│   └── requirements.txt                ← Python 依赖
├── frontend/                           ← 微信小程序前端（原生）
│   ├── app.js                          ← 全局请求封装/登录态
│   ├── utils/
│   │   ├── api.js                      ← API 封装（user/product/order/admin等）
│   │   └── util.js                     ← 通用工具（状态文案、时间格式化等）
│   └── pages/
│       ├── index/                      ← 首页：选日期/商品列表
│       ├── category/                   ← 分类
│       ├── detail/                     ← 商品详情：立即预定/客服入口
│       ├── orders/                     ← 下单确认/订单列表
│       ├── order/                      ← 订单详情：取衣/还衣/倒计时
│       ├── pay/                        ← 支付页（先模拟）
│       ├── chat/                       ← AI 客服
│       ├── profile/                    ← 我的
│       └── admin/                      ← 店主端：订单列表/订单详情
└── README/                             ← 项目文档与阶段说明
```
#### 3. Git 常用命令
```bash
# 查看状态
git status
# 提交代码
git add .
git commit -m "feat: 描述你的改动"
# 推送至远程仓库
git push origin main
# 拉取最新代码
git pull origin main
```
---

## 🛠️ 技术栈清单

- **Backend**: FastAPI, SQLAlchemy, Pydantic, OpenAI SDK
- **Frontend**: WeChat Mini Program 原生框架
- **AI**: DeepSeek-V3, Google Gemini 1.5 Flash
- **Database**: MySQL 5.7+

---

## 📅 更新日志 (Phases)

| 阶段 | 标题 | 主要功能 | 状态 |
|---|---|---|---|
| Phase 1 | [业务逻辑与AI基座](./README/20260409_Phase1_BusinessLogic_AI.md) | 24h计时、3件套餐、DeepSeek接入 | ✅ 完成 |
| Phase 2 | [店主管理与支付框架](./README/20260409_Phase2_Admin_Payment.md) | 店主订单管理、微信支付V3框架 | ✅ 完成 |
| Phase 3 | [MVP 精简与闭环](./README/20260409_Phase3_MVP_Simplification.md) | 日期选衣、下单、支付（模拟）、取衣/还衣、店主退押/扣费 | 🚧 进行中 |

---

## 📄 许可证

MIT License · **小时光租衣舍** © 2026
