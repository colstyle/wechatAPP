# 小时光租衣舍 — 设计方案文档

> **文档版本**：v1.0  
> **更新日期**：2026-04-13  
> **设计师**：待定  
> **配合文档**：`docs/PRD.md`

---

## 一、设计理念

### 品牌定位

**「小时光」**——温柔、仪式感、值得信赖的高性价比租衣体验。

> 设计关键词：**莫兰迪 / 高奢 / 克制 / 沉浸式 / 仪式感**

---

## 二、视觉设计系统（Design Tokens）

### 2.1 色彩体系

所有设计变量统一在 `frontend/styles/theme.wxss` 中定义：

> [!IMPORTANT]
> 微信小程序 WXSS 支持 CSS 自定义属性，但选择器必须用 `page { }` 而非 `:root { }`（后者无效）。当前代码已正确使用 `page`，文档统一以此为准。

```css
/* ===== 色彩 ===== */
page {
  /* 主背景：燕麦白，比纯白更有质感 */
  --bg-oatmeal: #FDFCF9;
  /* 卡片背景 */
  --bg-card: #FFFFFF;
  /* 主色：哑光黑，用于标题、主文字 */
  --color-ebony: #1C1C1C;
  /* 辅色：哑光金，用于价格、主按钮、重要标签 */
  --color-gold: #C5A059;
  /* 中性色：灰绿，用于辅助信息、次要按钮 */
  --color-sage: #8E9775;
  /* 浅色文字层 */
  --color-muted: #9A9A9A;
  /* 边框：极轻微分隔线 */
  --border-soft: rgba(28, 28, 28, 0.06);
  /* 成功色 */
  --color-success: #6B8F71;
  /* 警告色 */
  --color-warning: #D4A84B;
  /* 错误色 */
  --color-error: #B56B6B;
}
```

#### 色彩使用规范

| 色值 | 用途 |
|---|---|
| `--color-ebony` `#1C1C1C` | H1标题、主按钮文字、重要数据 |
| `--color-gold` `#C5A059` | 价格数字、主操作按钮、tabBar选中态 |
| `--color-sage` `#8E9775` | 次要按钮、标签文字、辅助说明 |
| `--bg-oatmeal` `#FDFCF9` | 全局页面背景 |
| `--color-muted` `#9A9A9A` | 时间戳、占位文字 |

### 2.2 字体体系

```css
/* ===== 字体 ===== */
page {
  /* 用于英文/数字：PingFang SC Light 层叠回退 */
  --font-display: -apple-system, "PingFang SC", "Helvetica Neue", sans-serif;
  
  /* 字号层级 */
  --text-xl:   36rpx;  /* 页面主标题 H1 */
  --text-lg:   30rpx;  /* 卡片标题、重要数据 */
  --text-md:   28rpx;  /* 正文（默认） */
  --text-sm:   24rpx;  /* 辅助说明、标签 */
  --text-xs:   22rpx;  /* 时间戳、版权信息 */
  
  /* 字重 */
  --font-bold:   600;
  --font-medium: 400;
  --font-light:  300;
}
```

### 2.3 间距与圆角

```css
page {
  /* 间距单位（基于8px栅格） */
  --spacing-xs:  8rpx;
  --spacing-sm:  16rpx;
  --spacing-md:  24rpx;
  --spacing-lg:  32rpx;
  --spacing-xl:  48rpx;
  
  /* 圆角 */
  --radius-sm:   8rpx;   /* 小标签 */
  --radius-md:   16rpx;  /* 卡片 */
  --radius-lg:   24rpx;  /* 底部弹窗 */
  --radius-full: 100rpx; /* 胶囊按钮 */
}
```

### 2.4 阴影系统

> [!WARNING]
> 微信小程序不支持 `backdrop-filter: blur()`，Glassmorphism 原生无法实现。统一降级为「高透明度实色」方案，视觉上仍有质感且零兼容风险。

```css
page {
  /* 卡片阴影 */
  --shadow-card: 0 4rpx 24rpx rgba(28, 28, 28, 0.06);
  --shadow-float: 0 8rpx 40rpx rgba(28, 28, 28, 0.12);
  
  /* 底栏「磨砂」降级方案（替代 glassmorphism） */
  --bar-bg: rgba(253, 252, 249, 0.96);  /* 高透明度实色，接近毛玻璃视觉 */
  --bar-border: 1rpx solid rgba(28, 28, 28, 0.06);
}
/* 用法：background: var(--bar-bg); border-top: var(--bar-border); */
```

---

## 三、页面设计规范

### 3.1 导航栏（自定义 NavBar）

**组件**：`components/cp-nav-bar/`

```
┌─────────────────────────────────────┐
│  ← [状态栏]                  [胶囊]    │  statusBarHeight
├─────────────────────────────────────┤
│     ← 返回   [页面标题/LOGO]           │  navBarInnerHeight
└─────────────────────────────────────┘
```

- **首页**：透明背景 + LOGO 文字「小时光」（哑光金）
- **内页**：白底 + 「← 返回」+ 页面标题（居中）
- **颜色**：沉浸式首页透明渐变，滚动后过渡到白底

### 3.2 TabBar

```
[首页]    [分类]    [订单]    [我的]
  ⌂        ≡        📋        🧑
```

**配色**：
- 未选中：灰绿色线条图标（`--color-sage`）
- 选中：金/黑双色填充（`--color-gold`）

**图标规格**：40×40px，PNG，背景透明，线条宽度 2px。

### 3.3 商品卡片（cp-product-card）

```
┌────────────────┐
│                │ ← 图片区，固定 3:4 比例
│    [图片]      │
│                │
├────────────────┤
│ 品牌 · 款式名   │ ← text-sm, color-muted
│ 连衣裙 L       │ ← text-md, color-ebony, bold
│ ¥9.9/天 押¥99  │ ← ¥ 用 color-gold, 押 用 color-muted
│ [套餐标签]     │ ← 仅参与套餐时显示绿色小徽章
└────────────────┘
```

**Skeleton 骨架屏**：加载时显示动态渐变占位块。

### 3.4 全屏日历（仪式感选日期）

- 全屏遮罩 + 中心卡片（radius-lg）
- 月份显示、左右箭头切换
- 今日高亮：`color-gold` 圆形背景
- 已选日期：`color-ebony` 实心圆
- 不可选（过去日期）：`color-muted` 半透明
- 底部「确认日期」按钮：哑光金实心

### 3.5 24小时倒计时（环形仪表盘）

```
      ┌──────────────┐
      │  ╭───────╮   │
      │  │ 18:30 │   │ ← 剩余时长（大字）
      │  │  :24  │   │
      │  ╰───────╯   │
      │  剩余租赁时间  │
      └──────────────┘
```

- **实现方式**：WXML 文本节点 + CSS `clip-path` / `border` 模拟环形（**不用 Canvas**）
  - `setInterval` 每秒更新 `{ h, m, s }` 三个数字，`setData` 开销极低
  - 进度环用 CSS 旋转渐变实现，无 Canvas 重绘压力
  - 离开页面时必须 `clearInterval`，避免内存泄漏
- **颜色规则**：
  - 剩余 > 2h：`color-sage` 灰绿
  - 剩余 ≤ 2h：`color-warning` 琥珀
  - 已逾期：`color-error` 暗红 + 闪烁动效

### 3.6 底部操作栏（吸底）

```
┌─────────────────────────────────┐
│  总计：¥169.9        [立即预定]   │ ← 高透明实色背景
└─────────────────────────────────┘
```

- 背景：`var(--bar-bg)`（`rgba(253,252,249,0.96)`）+ `border-top: var(--bar-border)`
- 按钮：`--color-ebony` 实心圆角，tap 有 scale(0.97) 微缩回弹效果

---

## 四、交互规范

### 4.1 微动效

| 场景 | 动效 | 时长 |
|---|---|---|
| 页面进入 | 从下向上 fade-in 20rpx | 300ms |
| 卡片 tap | scale(0.97) → 回弹 | 150ms |
| 按钮 Loading | 旋转圈圈替换文字 | 持续 |
| 模态弹窗出现 | 从下滑入 + 背景遮罩淡入 | 250ms |
| 倒计时颜色切换 | 颜色渐变过渡 | 500ms |

### 4.2 Toast / Loading 规范

```javascript
// 统一使用这三种方式，不允许直接在业务代码中调用 wx.showToast
showSuccess('操作成功')   // 绿色 ✓
showError('操作失败')     // 红色 ✗（自动显示具体原因）
showLoading('加载中...')  // 转圈 loading
```

### 4.3 空状态

统一使用 `cp-empty` 组件：
- 插图：极简线条图（与业务场景相关）
- 文字：主文案 + 操作引导文字
- 按钮（可选）：引导用户操作

---

## 五、数据数据接口约定（前后端约定）

### 5.1 统一响应格式

所有接口返回格式统一：

```json
{
  "code": 0,
  "message": "成功",
  "data": {}
}
```

| code 值 | 含义 |
|---|---|
| `0` | 成功 |
| `400` | 请求参数错误 |
| `401` | 未登录/Token过期 |
| `403` | 权限不足 |
| `404` | 资源不存在 |
| `500` | 服务器内部错误 |

### 5.2 静态数据 JSON 规范

位于 `frontend/data/`，格式约定：

```json
// categories.json 示例
{
  "version": "1.0",
  "updatedAt": "2026-04-13",
  "data": [
    { "id": 1, "name": "连衣裙", "icon": "dress", "sort": 1 },
    { "id": 2, "name": "大衣", "icon": "coat", "sort": 2 }
  ]
}
```

> 当后端接口就绪后，直接将 `require('./data/xxx.json')` 替换为 API 调用即可。

### 5.3 图片规格

| 用途 | 宽高比 | 建议分辨率 | 格式 |
|---|---|---|---|
| 商品主图 | 3:4 | 600×800px | WebP/JPG |
| 商品缩略图 | 1:1 | 200×200px | WebP/JPG |
| 搭配参考图 | 4:5 | 800×1000px | WebP/JPG |
| TabBar 图标 | 1:1 | 80×80px | PNG（透明背景） |
| 品牌 Logo | 3:1 | 240×80px | PNG（透明背景） |

---

## 六、文件结构（设计交付物）

```
frontend/
├── styles/
│   └── theme.wxss        ← 全局设计变量（唯一真相来源）
├── components/
│   ├── cp-nav-bar/       ← 自定义导航栏
│   ├── cp-product-card/  ← 商品卡片
│   ├── cp-countdown/     ← 环形倒计时
│   └── cp-empty/         ← 空状态组件
└── images/
    └── tabbar/
        ├── home.png      ← 首页图标（未选）
        ├── home-active.png
        ├── category.png
        ├── category-active.png
        ├── orders.png
        ├── orders-active.png
        ├── profile.png
        └── profile-active.png
```

---

## 七、可访问性与适配

- **安全区适配**：所有页面底部操作栏需 `padding-bottom: env(safe-area-inset-bottom)`
- **文字可读性**：文字与背景对比度 ≥ 4.5:1（WCAG AA）
- **触控目标**：所有可点击元素最小高度 ≥ 88rpx
- **图片懒加载**：`<image lazy-load="{{true}}">` 全站开启

---

*本文档由设计组维护，变更需同步研发组 `theme.wxss` 和组件实现。*
