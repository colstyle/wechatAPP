<div align="center">

# 🚀 100 APP 量产计划

**一套脚手架，三个平台。让创意到 APP 的落地只需一个下午。**

![100APP计划](https://img.shields.io/badge/100%20APP%20计划-004%20%2F%20100-ff6b6b?style=flat-square&logo=rocket)
![作者](https://img.shields.io/badge/作者-小石谈什么记-blueviolet?style=flat-square)
[![Platform](https://img.shields.io/badge/平台-Web%20%7C%20Windows%20%7C%20Android-blue?style=flat-square)](.)
[![Stack](https://img.shields.io/badge/技术栈-Next.js%20%2B%20Tauri%202%20%2B%20Capacitor-blueviolet?style=flat-square)](.)
[![Apps](https://img.shields.io/badge/已发布-5-brightgreen?style=flat-square)](./_docs/APP_CATALOG.md)

</div>

---

## ✨ 核心特性

- 🚀 **一键量产** — `create-app.ps1` 自动编号并生成 Web/Windows/Android 完备骨架。
- 🎨 **统一审美** — 基于 Design Tokens 的设计系统，改 3 个变量即可换整套 APP 主题。
- 📱 **多端覆盖** — Next.js 静态导出，Tauri 负责桌面端，Capacitor 负责移动端，**一份代码，三端共享**。
- 📤 **自动发布** — `github-push.ps1` 集成 Token 认证，一行命令将 APP 代码同步到 GitHub。
- 🏗️ **产物集成** — `collect-dist.ps1` 自动收集各端构建产物（.exe / .apk / .msi）到统一目录。
- 🦀 **极致效率** — 所有 Rust 编译共用同一缓存池，彻底解决 Windows 文件锁冲突，增量编译秒出结果。

---

## 🚀 开发者指南

### 环境要求

| 工具 | 用途 | 建议版本 |
|------|------|---------|
| **Node.js** | Next.js 前端开发 | ≥ 20.x |
| **Rust** | Tauri 桌面端构建 | ≥ 1.80.x |
| **JDK 21** | Android 构建环境 | 已安装 (Microsoft OpenJDK) |
| **Android Studio** | Android SDK & 调试 | 已安装 |

### 生产管理命令

```powershell
# 1. 批量生产新 APP
.\_scripts\create-app.ps1 -Name "my-app" -Type desktop -DisplayName "我的应用"

### 2. 跨平台同步与调试

在运行下述命令前，**必须先进入对应的 APP 目录**并确保依赖已安装：

```powershell
# 第一步：进入你想要调试的应用目录
cd apps\004-nfc-fortune

# 第二步：安装该应用的依赖
npm install

# 第三步：按需启动平台预览
npm run dev           # Web 预览 (浏览器访问 localhost:3000)
npm run tauri:dev     # Windows 桌面窗口调试
npm run android:sync  # [Android同步] 将前端代码同步到安卓项目
npm run android:open  # [Android调试] 打开 Android Studio 进行真机/模拟器预览
```

> **注意**：首次运行 `tauri:dev` 会下载 Rust 依赖，耗时较长；Android 调试需要提前在 Android Studio 完成 SDK 下载。

### 4. 代码推送 (GitHub 跨仓库自动化同步)

为了实现量产，项目基于应用编号提供了一键同步脚本，支持自动寻址和令牌安全隔离。

```powershell
# A. 按编号推送 (自动推导 URL: https://github.com/colstyle/004-nfc-fortune)
.\_scripts\github-push.ps1 "004"

# B. 到指定远程仓库 (强力推送并替换)
.\_scripts\github-push.ps1 "004" "https://github.com/XXX" -Force

# C. 一键同步所有 APP (批量运维模式)
.\_scripts\github-push.ps1 -All

# D. 使用安全令牌 (环境变量)
$env:GITHUB_TOKEN="ghp_xxx"; .\_scripts\github-push.ps1 "004"
```

> **安全提示**：脚本会自动在推送完成后移除本地配置中的 Token，确保开发者环境的长期安全。

---

## 📂 项目结构
```
202604@APPs/
├── apps/                       ← [重点] 业务 APP 存放区
│   ├── 001-aa-calculator/      ← 🍽️ AA 计算器
│   ├── 002-screenshot-formatter/ ← 🖼️ 截图格式助手
│   ├── 003-smart-kf/           ← 🤖 智能客服助手
│   └── 004-nfc-fortune/        ← 🔮 灵犀运势 (Hot!)
├── _templates/                 ← 三种量产模板 (Web/Mobile/Desktop)
├── _shared/                    ← 跨项目共享的设计系统与 Logic Hooks
├── _scripts/                   ← 自动化工具箱 (量产/收集/推送)
└── _docs/                      ← 知识库 (目录总表/设计规范)

```

---

## 🛠️ 技术栈清单

- **Runtime**: Next.js 15+ (App Router)
- **Styling**: Vanilla CSS (Tokens-based)
- **Desktop**: Tauri 2.0 (Rust)
- **Mobile**: Capacitor 8 (Android)
- **Hardware**: Native NFC Support (@capgo/capacitor-nfc)
- **Design Author**: [小石谈什么记](#)

---

## 📱 已发布应用

| 编号 | 名称 | 描述 | 发布状态 | 发布时间 | 预览 |
|---|---|---|---|---|---|
| #001 | [AA 计算器](./apps/001-aa-calculator) | 🍽️ 聚餐分账工具，支持人均/自定义 | ✅ Stable | 2026-04-04 14:45 | [GitHub](https://github.com/colstyle/001-aa-calculator) |
| #002 | [截图格式助手](./apps/002-screenshot-formatter) | OCR 识别 / 模板化导出 | ✅ Stable | 2026-04-04 16:20 | [GitHub](https://github.com/colstyle/002-screenshot-formatter) |
| #003 | [智能客服助手](./apps/003-smart-kf) | 机器人资产保护 / BYOK | 🧪 Beta | 2026-04-04 18:30 | [GitHub](https://github.com/colstyle/003-smart-kf) |
| #004 | [灵犀运势](./apps/004-nfc-fortune) | 🔮 NFC 触碰测运 / AI 跨端 | 🧪 Beta | 2026-04-04 23:40 | [GitHub](https://github.com/colstyle/004-nfc-fortune) |
| #005 | [快递取件码](./apps/005-express-pickup) | 📦 智能短信识别 / 取件清单 | 🧪 Beta | 2026-04-05 09:20 | [GitHub](https://github.com/colstyle/005-express-pickup) |

> 详情见：[APP 目录总表](./_docs/APP_CATALOG.md)

---

## 📄 许可证

MIT License · **小石谈什么记** © 2026
