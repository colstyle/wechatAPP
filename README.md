<div align="center">

# 👗 小时光租衣舍 (Time Capsule)

**旗舰级 24 小时自助租衣小程序。日期预约、套餐优惠、AI 穿搭、高奢视觉。**

![Project Status](https://img.shields.io/badge/状态-Phase%2010%20工业级闭环收官-success?style=flat-square)
![Platform](https://img.shields.io/badge/平台-WeChat%20Mini%20Program%20%7C%20FastAPI-blue?style=flat-square)
![Tech Stack](https://img.shields.io/badge/技术栈-FastAPI%20%2B%20MySQL%20%2B%20DeepSeek-blueviolet?style=flat-square)
![Package Size](https://img.shields.io/badge/包体积-仅_380KB_(静态外提)-brightgreen?style=flat-square)

</div>

---

## ✨ 核心特性

- 💎 **高奢莫兰迪视觉** — 行业领先的沉浸式黑金/莫兰迪色系设计，全自定义胶囊导航，极致平滑过渡。
- 📅 **智能排期体系** — 基于日历的实时档期选款，支持按单品、按套餐（3件69.9）灵活组合。
- ⏲️ **可视化租赁链路** — 环形倒计时实时追踪，动态计算租赁天数与预计归还时间，自动计算逾期。
- 🤖 **AI 穿搭灵感** — 集成 DeepSeek-V3/Gemini，提供 24h 业务咨询与专业服装搭配建议。
- 🧑‍💼 **旗舰级管理后台** — 店主专属管理舱，支持异主订单详情查阅、退押金、手动扣费、换款及库存实时监控。

## 🛠️ 工程亮点（工业级优化）

- 🚀 **源码体积突破** — 通过后端 FastAPI 静态挂载技术，将近 3MB 的高清 Banner 资源外提，使主包体积从超限降至 380KB，完美兼容真机调试。
- 🛡️ **权限安全隔离** — 实现了基于 Role 的严格鉴权，解决了管理员管理他人订单时的权限隔离与详情加载难题。
- 🌐 **全自动环境引擎** — 利用微信官方 API 自动识别 develop/trial/release 版本，实现 API 地址与静态资源库的无缝切换。
- 🎨 **组件化开发** — 封装了 `cp-nav-bar`（自定义导航）、`cp-empty`（高奢空状态）、`cp-product-card`（骨架屏同步）等原子组件。

---

## 🚀 快速启动

### 1. 后端启动 (FastAPI)
```bash
cd backend
# 1. 安装依赖 (Python 3.9+)
pip install -r requirements.txt
# 2. 配置环境变量
cp .env.example .env # 填写 DB、JWT 及 AI Key
# 3. 启动（默认 8000 端口）
python main.py
```

### 2. 前端启动 (微信小程序原生)
1. 使用**微信开发者工具**导入 `frontend/` 目录。
2. **真机调试配置**：
   - 确保手机与电脑在同一 WiFi 下。
   - 在 `frontend/config/env.js` 中将 `apiBase` 更新为你的电脑局域网 IP（如 `192.168.43.79`）。
   - 开发者工具设置中勾选「不校验合法域名」。

---

## 📂 项目结构

```
202604@wechatAPP/
├── backend/                            ← 后端框架
│   ├── app/
│   │   ├── api/                        ← 核心路由（user, product, order, admin...）
│   │   └── static/images/              ← [NEW] 远端高清大图资源仓
│   ├── config/settings.py               ← 多环境核心配置
│   └── main.py                         ← 入口（含静态资源挂载 Mount）
├── frontend/                           ← 前端原生小程序
│   ├── components/                     ← 原子组件库 (NavBar, Empty, Card...)
│   ├── config/env.js                   ← 环境自动化切换引擎
│   ├── pages/
│   │   ├── index/                      ← 首页 (日历选期/精选单品)
│   │   ├── admin/                      ← [PRO] 店主管理全功能模块
│   │   ├── order/                      ← 订单中心与 24h 追踪
│   │   └── profile/                    ← 个人中心 (含门店定位、拨号)
│   └── utils/api.js                    ← 工业级 API 聚合封装层
├── docs/                               ← 正式产品文档
└── README.md                           ← 本文件
```

---

## 📅 路线图 (Milestones)

| 阶段 | 状态 | 内容 |
|---|---|---|
| Phase 1-5 | ✅ 完成 | 业务闭环、AI 客服、黑金 UI、组件库建立 |
| Phase 6-9 | ✅ 完成 | 多环境工程化、静态资源库分离、管理员权限加固 |
| **Phase 10** | ✅ 完成 | **真机调试优化、门店定位联络、空状态美化、Git 同步** |
| Phase 11 | ⏳ 规划 | 微信支付 V3 实装、真实 OpenID 认证、隐私政策核验 |

---

## 📄 执照
MIT License · **小时光租衣舍 007/100** © 2026

<div align="center">
  <sub>使用 Antigravity AI 开发 · 高性能 · 高颜值 · 高可用</sub>
</div>
