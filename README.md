<div align="center">

# 👗 小时光租衣舍 (Time Capsule Clothing Rental)

**24小时自助租衣小程序。日期锁定、套餐优惠、AI智能客服。**

![Project Status](https://img.shields.io/badge/状态-Phase%201%20完成-brightgreen?style=flat-square)
![Platform](https://img.shields.io/badge/平台-WeChat%20Mini%20Program%20%7C%20FastAPI-blue?style=flat-square)
![Tech Stack](https://img.shields.io/badge/技术栈-FastAPI%20%2B%20MySQL%20%2B%20DeepSeek-blueviolet?style=flat-square)

</div>

---

## ✨ 核心特性

- 📅 **日期优先预约** — 强制用户先选日期再看衣服，确保库存实时锁定，杜绝超卖。
- 🎁 **3件69.9套餐** — 灵活的套餐逻辑，固定租金+阶梯押金，自动计算最优组合。
- ⏱️ **24h 精准租赁** — 以“取衣”动作激活计时器，前端实时倒计时，后端自动计算逾期。
- 🤖 **AI 智能客服** — 集成 DeepSeek-V3/Gemini，预置业务知识库，提供 7x24h 咨询服务。
- 🔐 **自助开门对接** — 支付成功自动下发 TTLock 动态密码，实现全程无人值守。
- 💰 **极简退押逻辑** — 店主端一键原路退还押金，支持因逾期或损毁手动扣费。

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
# 启动服务
python main.py
```

#### 2. 前端配置 (WeChat)
- 使用微信开发者工具打开 `frontend` 目录。
- 修改 `utils/api.js` 中的 `BASE_URL` 指向您的后端地址。

---

## 📂 项目结构
```
202604@wechatAPP/
├── backend/                ← FastAPI 后端
│   ├── app/api/           ← 业务逻辑 (order, product, ai, admin...)
│   ├── config/            ← 系统配置 (DeepSeek API Key, DB...)
│   └── database/          ← SQL 脚本与连接池
├── frontend/               ← 微信小程序前端
│   ├── pages/             ← 业务页面 (index, package, chat, order...)
│   └── utils/             ← API 封装与工具类
└── README/                 ← 项目文档与更新日志
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
| Phase 2 | 系统集成 (Pending) | TTLock 真实对接、微信支付 V3 | ⏳ 规划中 |

---

## 📄 许可证

MIT License · **小时光租衣舍** © 2026
