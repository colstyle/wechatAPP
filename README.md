<div align="center">
  <img src="https://img.icons8.com/isometric/512/dress.png" alt="TimeCapsule" width="120" />
  <h1>👗 小时光租衣舍 (Time Capsule)</h1>
  <p><strong>旗舰级 24 小时自助租衣小程序。日期预约、套餐优惠、AI 客服、高奢视觉。</strong></p>

  <p>
    <a href="#-快速启动"><strong>🚀 快速启动</strong></a> &middot;
    <a href="README/deployment_diary.md"><strong>📖 部署指南</strong></a> &middot;
    <a href="https://github.com/colstyle/wechatAPP"><strong>🔗 GitHub</strong></a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/状态-Phase%2011%20服务器部署完成-success?style=flat-square" alt="Status" />
    <img src="https://img.shields.io/badge/平台-WeChat%20MP-blue?style=flat-square" alt="Platform" />
    <img src="https://img.shields.io/badge/后端-FastAPI-green?style=flat-square" alt="Backend" />
    <img src="https://img.shields.io/badge/部署-Docker-blueviolet?style=flat-square" alt="Deployment" />

  </p>
</div>

---

## 📢 项目动态与开发编时史 (News & Changelog)

### 🚀 24 小时：服务器生产环境大冲刺
- **2026-04-14 14:30** ✅ **全链路通电**：手机真机扫码测试成功，正式打通 `https://www.celestialaiplus.com`。解决了小程序端由于缓存导致的域名不合法假警报。
- **2026-04-14 10:00** 🔒 **HTTPS 攻坚战**：通过 Nginx Proxy Manager (Port 81) 一键申请 Let's Encrypt 证书，实现了 80/443 端口自动跳转 HTTPS，满足微信最严准入标准。
- **2026-04-14 09:00** 🧬 **数据整备**：完成 `v1.0.0` 种子数据注入，批量修复了由于迁移导致的图片 404 死链，解决字符编码乱码问题。
- **2026-04-13 23:00** 🐳 **Docker 部署**：完成 `FastAPI` + `MySQL 5.7` 的容器化编排。利用云服务器内网源（Tencent/Aliyun）加速拉取镜像，解决服务器网络“卡脖子”难题。
- **2026-04-13 15:00** 🛡️ **架构转轨（弃用云托管）**：因微信云托管 VPC 隔离导致数据库 `Timeout 2003`，果断拍板将其剥离，转向自主可控的独立 Ubuntu 服务器。

### 🛠️ 早期：从 0 到 1 的地基工程
- **2026-04-12** ✨ **店主权力加冕**：店主管理端 (Admin) 核心逻辑联调完毕，支持管理员在手机端直接加减库存、处理退押金。
- **2026-04-11** 📅 **算法闭环**：基于共享日历的“租期预约”算法上线，同步实现“3件69.9”等套餐最优原路费用计算模型。
- **2026-04-10** 🎨 **品牌觉醒**：莫兰迪色系 UI 全面覆盖。引入沉浸式胶囊导航与 `cp-empty` 占位组件，从“框架”蜕变为“产品”。

<details>
<summary>查看更早期的诞生足迹</summary>

- **2026-04-09** 🤖 AI 客服集成：接入 DeepSeek/Gemini 实现业务咨询自动化。
- **2026-04-08** 🌱 种子萌芽：项目初始化，确立 Python FastAPI + 原生小程序的轻量化路线。
</details>

## 🛒 核心功能清单

### 👥 针对租客（用户端）
1. **智能租期预约**：像订酒店一样选衣服。日历直接显示有货日期，系统自动算租金，到期前自动提醒。
2. **灵活选购方案**：支持单件精租，也支持“3件69.9”等套餐，系统自动识别最省钱的组合。
3. **快速筛选搜索**：支持按分类、关键词精准找衣服，还能看到“店长推荐”和最新到货。
4. **一键联系与导航**：内置门店电话一键拨打，支持直接拉起地图导航到店。
5. **个人中心管理**：实时追踪订单状态（待取货、租赁中、待结清），支持收藏心仪衣物。
6. **AI 客服**：24小时在线解答尺码选择、租衣流程等常见问题。

### 🧑‍💼 针对店主（管理端）
1. **移动办公舱**：无需电脑，店主在手机上登录管理员账号即可管理全店。
2. **极简库存管理**：拍张照就能上架新衣服，随时随地修改租金、押金和库存数量。
3. **订单全局掌控**：查看全店预约订单，处理用户还衣、延期扣费及一键退还押金。
4. **穿搭灵感预设**：支持设置“店长推荐”位和分类权重，引导用户选择热门款式。
5. **店主私域 AI 客服**：支持店主上传专属“知识库”（比如特定衣服的洗护说明、店铺 ## 📂 详细目录结构
---

## ⚙️ 幕后技术支柱
- **自动识别网络环境**：一套前端代码通吃。系统会自动判断当前是“电脑调试”、“手机体验”还是“正式线上”状态，自动帮你连到对应的后端地址，再也不用手动来回改代码了。
- **极致加载优化**：高清大图全部挂在服务器，小程序主包极小，扫码秒开不转圈。
- **权限安全护航**：严格的店主/用户身份验证，普通用户即便扫到后台地址也进不去。

---

## 🚀 启动指引

### 1. 开发阶段 (本地开发模式)
*   **后端**：
    ```bash
    cd backend
    pip install -r requirements.txt
    python main.py # API 默认运行在 127.0.0.1:8000
    ```
*   **前端**：微信开发者工具中勾选“不校验合法域名”。环境将自动切换为 `develop` 模式。

### 2. 测试阶段 (真机调试模式)
*   **后端**：确保局域网或公网 IP 可达。
*   **前端**：修改 `frontend/config/env.js` 中的 `apiBase`，指向开发机的局域网 IP。在工具栏使用“真机调试”，手机与电脑需在同一 Wi-Fi。

### 3. 发布阶段 (生产模式)
*   **后端**：
    ```bash
    cd ~/wechatAPP
    git pull origin test
    docker compose up -d --build
    ```
*   **前端**：确认 `env.js` 指向 `https://www.celestialaiplus.com`。并在微信后台完成域名加白名单。然后在工具中点击“上传”。

---

## 📂 详细目录结构

### 1. 后端项目 (backend/)
```text
backend/
├── app/
│   ├── api/                            ← 业务接口定义 (路由层)
│   │   ├── admin.py                    ← 店主管理与订单查询
│   │   ├── ai.py                       ← 24h 智能客服对话接口
│   │   ├── appointment.py              ← 试穿预约与档期查询
│   │   ├── order.py                    ← 租衣下单与计费引擎
│   │   ├── product.py                  ← 服装库存、分类与检索
│   │   ├── review.py                   ← 用户评价管理
│   │   ├── subscription.py             ← 月卡/套餐订阅体系
│   │   └── user.py                     ← 用户鉴权与角色分发
│   ├── core/                           ← 安全加密与拦截中间件
│   └── static/images/                  ← 静态资源库 (高清大图仓)
├── config/                             ← 系统核心配置中心
├── database/                           ← 数据库连接池与初始化 SQL
├── main.py                             ← 程序入口 (FastAPI)
├── Dockerfile                          ← 容器化打包描述
└── requirements.txt                    ← 依赖环境快照
```

### 2. 小程序项目 (frontend/)
```text
frontend/
├── components/                         ← 业务复用原子组件
│   ├── cp-empty/                       ← 莫兰迪风格占位图
│   ├── cp-nav-bar/                     ← 自定义沉浸式顶壳
│   └── cp-product-card/                ← 瀑布流商品展示卡
├── pages/                              ← 业务逻辑页面
│   ├── index/                          ← 首页看点
│   ├── category/                       ← 业务分类探索
│   ├── detail/                         ← 服装详情与选期
│   ├── chat/                           ← 智能客服对话窗口
│   ├── pay/                            ← 费用与押金收银台
│   ├── order/                          ← 下单确认页面
│   ├── orders/                         ← 历史订单追踪
│   ├── package/                        ← 优惠套餐选购
│   ├── profile/                        ← 个人中心
│   ├── admin/                          ← 店主移动控制台
│   └── settings/                       ← 系统设置与偏好
├── config/env.js                       ← 环境自动切换引擎
└── utils/api.js                        ← 统一请求封装库
```

### 3. 文档与辅助工具
```text
├── README/                             ← [核心] 运维与防坑实战手册
├── docs/                               ← 产品原型与交互文档
├── convert-icons.js                    ← 图标自动化转换工具
└── wechatAPP上线步骤.docx               ← 官方备案与提审辅助指南
```


## 📚 详细指南

### 🛠️ 部署与运维 (Operations)
- 👗 **[生产环境实战部署日记](./README/deployment_diary.md)** —— 包含架构可视化图表，以及从零配置服务器、Docker 与 HTTPS 的全记录。
- 📔 **[微信小程序上线全流程](./wechatAPP上线步骤.docx)** —— 官方备案、后台域名配置与正式提审指南。

### 📜 开发实战日志 (Development Steps)
<details>
<summary>点击展开 10 个阶段的开发全记录</summary>

- **[Phase 1: 业务逻辑与 AI 初步](./README/20260409_Phase1_BusinessLogic_AI.md)**
- **[Phase 2: 店主后台与支付模型](./README/20260409_Phase2_Admin_Payment.md)**
- **[Phase 3: MVP 核心功能精简优化](./README/20260409_Phase3_MVP_Simplification.md)**
- **[Phase 4: 身份验证与 Mock 联调](./README/20260409_Phase4_Identity_Role_Mock.md)**
- **[Phase 5: 莫兰迪色系全量视觉重构](./README/20260410_Phase5_Aesthetic_Refactor.md)**
- **[Phase 6-8: 架构升级与环境自动化](./README/20260413_Phase6_to_8_Architecture_Upgrade.md)**
- **[Phase 10: 体验版性能与稳定性优化](./README/20260413_Phase10_TrialReady_Optimization.md)**
</details>

### 🎨 产品设计与规范 (Design & Specs)
- 📝 **[PRD 产品需求文档](./docs/PRD.md)** —— 核心业务场景与功能定义。
- 📐 **[DESIGN 交互设计规范](./docs/DESIGN.md)** —— 莫兰迪视觉系统与 UI 组件准则。
- 🌏 **[ENV 多环境配置方案](./docs/ENV.md)** —— develop / trial / release 的自动化映射逻辑。
- 🗺️ **[PLAN 项目路线规划](./docs/PLAN.md)** —— 10天 项目起跑线的初步设想。

<br/>

<br/>

---
MIT License © 2026
