# Phase 5: 高奢审美与架构重构 (Aesthetic & Architecture Refactor)

**日期**: 2026-04-10  
**目标**: 将项目从 MVP 原型彻底重构为具备“现代优雅 (Modern Elegant)”感的高端应用，并完成原子化组件架构。

---

## 🎨 视觉系统 (Design Tokens)

我们抛弃了默认的 UI 风格，建立了基于“莫兰迪”色系的视觉体系：

| 变量名 | 色值 | 用途 |
| :--- | :--- | :--- |
| **Oatmeal White** | `#FDFCF9` | 主背景色，温润如纸感 |
| **Matte Gold** | `#C5A059` | 强调色、按钮、选中态，体现高奢质感 |
| **Sage Green** | `#8E9775` | 辅助色、TabBar 未选中态，自然宁静 |
| **Ink Black** | `#1C1C1C` | 标题文本、主要文字，高对比度 |
| **Warm Gray** | `#B0A99A` | 辅助信息、描边、空状态图标 |

## 🏗️ 架构重构 (Atomic Components)

引入原子化组件开发模式，确保全站视觉一致性：

1.  **`cp-nav-bar` (沉浸式导航)**:
    *   动态计算胶囊位置，完美适配各种机型。
    *   支持透明、磨砂、实色三种背景模式。
    *   彻底解决顶部安全区域被系统遮挡的痛点。

2.  **`cp-product-card` (商品卡片)**:
    *   标准 3:4 比例布局。
    *   内置高质感 Shimmer 骨架屏加载动效。
    *   极简边框与微阴影，提升信息阅读舒适度。

## ✨ 页面重塑

全站所有页面清单与重构状态：

### 1. 核心用户页 (Core User Pages) - ✅ 已重构
- **首页 (`pages/index/index`)**: 沉浸式导航，莫兰迪分类图标，高质感搜索。
- **分类 (`pages/category/category`)**: 呼吸感布局，cp-product-card 接入，侧边栏优化。
- **商品详情 (`pages/detail/detail`)**: 沉浸式轮播图，磨砂底部栏，规格选择卡片化。
- **AI 客服 (`pages/chat/chat`)**: 磨砂输入背景，流线型气泡，AI 身份标识装饰。
- **我的 (`pages/profile/profile`)**: 卡片化数据速览（4宫格），纯 CSS 图标。
- **设置 (`pages/settings/settings`)**: 个人信息卡片，开发配置项整齐收纳。

### 2. 租赁与支付流程 (Order & Payment) - ✅ 已重构
- **下单确认 (`pages/orders/confirm`)**: 账单卡片化，流程引导清晰。
- **收银台 (`pages/pay/pay`)**: 绿色高亮支付按键，纯 CSS 微信图标。
- **订单落地页 (`pages/order/order`)**: 入口功能卡片化，纯 CSS 业务图标。

### 3. 管理员后台 (Admin Mode) - ✅ 部分重构
- **店主订单列表 (`pages/admin/orders/orders`)**: 接入自定义导航，订单信息卡片化。
- **店主订单详情 (`pages/admin/detail/detail`)**: *[待优化]* 当前保持基础功能布局。
- **店主套餐管理 (`pages/admin/package/package`)**: *[待优化]* 尚未统一莫兰迪风格。

### 4. 剩余功能页 (Other Features) - ⏳ 待统一
- **3件套餐挑选 (`pages/package/package`)**: 待接入沉浸导航与一致性卡片。
- **用户订单列表 (`pages/orders/orders`)**: 待从旧版列表迁移至卡片风格。
- **用户订单详情 (`pages/order/detail/detail`)**: 待接入可视化倒计时圆环。
- **预约系统 (`pages/appointment/appointment`)**: 待统一 UI。
- **会员订阅 (`pages/subscribe/subscribe`)**: 待美化。
- **评价系统 (`pages/review/review`)**: 待美化。
- **地址管理 (`pages/address/address`)**: 待美化。
- **商品库搜索 (`pages/product/product`)**: 已初步适配。

## 🛠️ 技术突破

-   **SVG 转 PNG 自动化**: 通过 `convert-icons.js` 脚本调用 Node.js `sharp` 库，将手工绘制的精细 SVG 批量渲染为 40x40/81x81 的高清晰 PNG，确保存储占用的同时保持极简风格。
-   **API 纠偏**: 修复 `wx.getSystemInfoSync` 等废弃 API 警告，兼容最新微信基础库。
-   **真机调试优化**: 自动探测局域网 IP 并同步至 `app.js`，实现“扫码即通”。

---

## 📸 视觉快照 (Highlights)

-   **图标系统**: 全面移除 Emoji，改用纯 CSS 绘制图标 + 定制 PNG 图标，确保全站审美不脱节。
-   **手绘 CSS 图标**: 包含衣架、时钟、日历、皇冠、对话气泡、设置齿轮等 10 余种矢量细节。

> [!NOTE]
> 本次重构不仅是视觉的升级，更是代码规范的升级。未来新增页面应优先复用 `components/` 库中的原子组件，严禁在页面级 CSS 中重复编写基础布局逻辑。
