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
| Phase 10 | ✅ 完成 | 真机调试优化、门店定位联络、空状态美化、Git 同步 |
| **Phase 11** | 🚀 **进行中** | **服务器私有化部署、Docker 环境搭建、域名解析中** |
| Phase 12 | ⏳ 规划 | 微信支付 V3 实装、真实 OpenID 认证、上架版本审核 |

---

## 📜 开发实战日志 (Development Log)

记录“小时光租衣舍”从云端迁移到私有服务器的硬核历程：

1.  **[弃暗投明]**：由于微信云托管与云数据库存在 VPC 隔离（Timeout 2003），果断放弃傻逼微信组件，转向自主可控的 **腾讯云轻量服务器**。
2.  **[Docker 化]**：基于 `Docker` + `Docker-Compose` 重新打包后端与 MySQL，实现“一键搬家、永久稳定”。
3.  **[网络破局]**：通过配置国内镜像源（Tencent/Aliyun），解决了服务器拉取镜像慢、容器内 `apt-get` 挂掉的难题。
4.  **[数据回迁]**：成功在服务器初始化 15 张核心业务表，并手动植入了“夏日海鸥”女生系列开业数据。
5.  **[接口通电]**：成功通过 **IP:8000** 实现了外网与服务器数据库的首次通信！

---

## 🚀 上线冲刺清单 (Remaining Steps)

目前的“发动机”已经点火，距离手机端正式看到成品还差最后 4 步：

- [ ] **1. 全站 HTTPS (当前优先级最高)**
  - 动作：通过 Port 81 (Nginx Proxy Manager) 为 `celestialaiplus.com` 申请 SSL 证书并转发至 8000 端口。
  - 目的：满足微信小程序“必须使用 HTTPS 域名”的硬性规定。
- [ ] **2. 前端代码同步**
  - 动作：在 `frontend/config/env.js` 中将云托管地址修改为你的正式域名。
- [ ] **3. 微信后台备案**
  - 动作：登录微信公众平台，将 `https://celestialaiplus.com` 加入 `request 合法域名`。
- [ ] **4. 正式版本上传**
  - 动作：在开发者工具点击“上传”，进入审核队列。

---

## 🛠️ 保姆级上线操作指南 (Operation Guide)


我给你总结一下现在的终极战果：
✅ 全部搞定
服务器：110.40.168.138 ✅
域名：www.celestialaiplus.com 正常解析 ✅
后端：小时光租衣舍 v1.0.0 running ✅
访问：http://www.celestialaiplus.com 可以打开 ✅
数据库：有数据、接口能返回 ✅
端口：80 / 443 已开放 ✅

最终战果总结
服务器：正常运行 ✅
域名：www.celestialaiplus.com 解析正常 ✅
后端：「小时光租衣舍」running ✅
HTTPS 安全证书：已生效（带小锁） ✅
自动跳转：http → https ✅
如果你在操作中感到困惑，请严格执行以下步骤：

### 第一步：域名“指路” (DNS 解析)
1. 登录腾讯云，进入 **DNS 解析 DNSPod**。
2. 为 `celestialaiplus.com` 添加 A 记录，指向你的服务器 IP `110.40.168.138`。
3. **关键验证**: 在电脑终端运行 `ping celestialaiplus.com`。
   - 看到 `来自 110.40.168.138 的回复` -> **成功 ✅**
   - 看到 `198.18.x.x` -> **失败 ❌** (请关闭电脑上的梯子/VPN再试)。

### 第二步：网关“守门” (Nginx Proxy Manager)
1. 访问 `http://110.40.168.138:81`。
2. 初始账号：`admin@example.com` / `changeme`。
3. 进入 **Proxy Hosts -> Add Proxy Host**:
   - **Domain Names**: `celestialaiplus.com`
   - **Forward Port**: `8000`
   - **Forward IP**: `127.0.0.1`
4. 切换到 **SSL 标签页**:
   - 下拉选 `Request a new SSL Certificate`
   - 勾选 `Force SSL` 和 `Agree Terms`。
   - 点击 **Save**。

### 第三步：前端“通电” (微信端)
1. 修改 `frontend/config/env.js`:
   ```javascript
   const config = {
     apiBase: 'https://celestialaiplus.com', // 必须是 https
     // ...
   }
   ```
2. 登录 **微信公众平台**, 进入“开发管理 -> 开发设置 -> 服务器域名”。
3. 在 `request 合法域名` 处填入 `https://celestialaiplus.com`。

1. 买服务器（腾讯云轻量 Ubuntu）
操作
买轻量应用服务器，选 Ubuntu
放通防火墙：22、80、443、8000
记下公网 IP：110.40.168.138
目的
拥有一台 24 小时在线的 “远程电脑”
运行小程序后端 + 数据库
2. 买域名并解析（celestialaiplus.com）
操作
买域名
DNS 添加 2 条 A 记录：
www → 你的服务器 IP
@ → 你的服务器 IP
ping 验证通了
目的
用好记的域名代替难记的 IP
让微信 / 浏览器能找到你的服务器
3. 部署后端（FastAPI + MySQL）
操作
上传代码到服务器
导入数据库 init.sql
启动后端：端口 8000
访问 IP:8000 看到 JSON 接口
目的
让小程序的接口真正运行起来
4. 安装 Nginx（反向代理）
操作
apt install nginx
配置域名指向 127.0.0.1:8000
重启 Nginx
目的
把域名流量转发给后端
实现用域名访问，不用带端口
支持 HTTPS
5. 申请 HTTPS（免费证书）
操作
apt install certbot python3-certbot-nginx
certbot --nginx -d www.celestialaiplus.com
选择自动跳转 HTTPS
目的
给域名加安全锁
微信小程序强制要求必须 HTTPS
6. 微信小程序后台配置
操作
开发设置 → request 合法域名
填入：https://www.celestialaiplus.com
目的
让微信允许你的小程序访问接口
7. 小程序前端改接口
操作
baseURL 改为
https://www.celestialaiplus.com
目的
前端正式连接线上后端
✅ 最终成果（你现在已经全部达成）
https://www.celestialaiplus.com
返回：
{"app":"小时光租衣舍","version":"1.0.0","status":"running"}
服务器 ✅
域名 ✅
解析 ✅
后端 ✅
数据库 ✅
Nginx ✅
HTTPS ✅
微信可访问 ✅
小程序可上线 ✅

---

## 📄 执照
MIT License · **小时光租衣舍 007/100** © 2026

<div align="center">
  <sub>使用 Antigravity AI 开发 · 高性能 · 高颜值 · 高可用</sub>
</div>
