# 小时光租衣舍 — 多环境策略设计

> **文档版本**：v1.0  
> **更新日期**：2026-04-13  
> **配合文档**：`docs/PRD.md` · `plan.md`

---

## 一、环境定义

| 环境 | 标识 | 用途 | 对应 Git 分支 | 微信小程序版本 |
|---|---|---|---|---|
| **开发环境** | `dev` | 开发者本机调试，允许 mock 数据 | `dev` | 开发版（微信开发者工具）|
| **测试环境** | `test` | 开发者自测完毕后，供测试组/产品组体验 | `test` | 体验版（扫描体验码）|
| **生产环境** | `prod` | 正式上线，面向真实用户 | `main` | 正式版（小程序商店）|

---

## 二、前端环境切换设计

### 2.1 核心原理：官方 envVersion API（零侵入）

微信小程序提供官方 API 自动识别当前运行环境，**无需手动修改代码**：

```javascript
const { envVersion } = wx.getAccountInfoSync().miniProgram
// 'develop' → 开发版（微信开发者工具打开）
// 'trial'   → 体验版（扫描体验码，对应 test 环境）
// 'release' → 正式版（小程序商店发布，对应 prod 环境）
```

### 2.2 env.js 实现（需新建）

**路径**：`frontend/config/env.js`

```javascript
// frontend/config/env.js
// 多环境配置 — 自动根据微信小程序运行版本切换，无需手动改代码

const { envVersion } = wx.getAccountInfoSync().miniProgram

const ENV_MAP = {
  develop: {
    ENV:        'dev',
    apiBase:    'http://192.168.43.79:8000',  // 本机局域网 IP（可在设置页覆盖）
    enableMock: true,    // 允许 mockOpenid 固定身份
    enableLog:  true,    // 开启控制台日志
  },
  trial: {
    ENV:        'test',
    apiBase:    'http://YOUR_TEST_SERVER:8000', // 测试服务器地址（上线前填写）
    enableMock: true,    // 测试阶段仍允许 mock，方便测试组切换身份
    enableLog:  true,
  },
  release: {
    ENV:        'prod',
    apiBase:    'https://api.yourdomain.com',  // 正式域名，必须 HTTPS
    enableMock: false,   // 生产环境禁止 mock
    enableLog:  false,   // 关闭控制台日志
  },
}

const config = ENV_MAP[envVersion] || ENV_MAP.develop

module.exports = config
```

> [!IMPORTANT]
> `envVersion` 由微信平台自动注入，开发者无需手动设置任何标志位。切换环境只需通过微信开发者工具「上传」到对应版本即可。

### 2.3 app.js 改造（需修改）

**路径**：`frontend/app.js`

```javascript
// app.js 顶部引入
const envConfig = require('./config/env.js')

App({
  // 从环境配置读取，不再硬编码
  apiBase: envConfig.apiBase,

  onLaunch() {
    // 开发环境：允许从存储中读取手动覆盖的 apiBase（方便真机测试换 IP）
    if (envConfig.ENV === 'dev') {
      const savedApiBase = wx.getStorageSync('apiBase')
      if (savedApiBase) this.apiBase = savedApiBase
    }
    // 生产环境：强制使用配置中的 apiBase，忽略本地存储
    this.globalData.apiBase = this.apiBase
    // ...
  }
})
```

### 2.4 各环境功能差异矩阵

| 功能 | dev（开发版）| test（体验版）| prod（正式版）|
|---|---|---|---|
| apiBase 来源 | `env.js` 配置 / 设置页可覆盖 | `env.js` 配置（不可覆盖）| `env.js` 配置（不可覆盖）|
| Mock openid | ✅ 允许 | ✅ 允许（测试组用）| ❌ 禁止 |
| 控制台日志 | ✅ 输出 | ✅ 输出 | ❌ 关闭 |
| apiBase 协议 | `http://` 可用 | `http://` 可用 | 必须 `https://` |
| 设置页入口 | ✅ 显示 | ✅ 显示（只读）| ❌ 隐藏 |
| 微信域名校验 | 关闭校验（开发者工具设置）| 关闭校验 | **强制校验**（必须在公众平台配置）|

---

## 三、后端环境切换设计

### 3.1 文件结构

```
backend/
├── .env              ← 本地开发 (dev)，写入 .gitignore，不提交
├── .env.example      ← 所有变量的占位模板，提交 git（供参考）
├── .env.test         ← 测试环境模板，提交 git（值为示例/占位，无真实密钥）
└── .env.prod         ← 生产环境真实配置，写入 .gitignore，绝不提交
                        （通过服务器环境变量或 CI/CD Secret 注入）
```

### 3.2 .env 各环境关键差异

| 变量 | dev | test | prod |
|---|---|---|---|
| `APP_ENV` | `dev` | `test` | `prod` |
| `DEBUG` | `True` | `True` | `False` |
| `DB_HOST` | `127.0.0.1` | `test-db-server` | `prod-db-server` |
| `DB_NAME` | `celestial_dev` | `celestial_test` | `celestial_prod` |
| `JWT_SECRET_KEY` | 任意字符串 | 任意字符串（不同于 prod）| **随机高强度密钥，绝不共享** |
| `CORS_ORIGINS` | `["*"]` | `["*"]` | `["https://servicewechat.com"]` |
| `WECHAT_APP_ID` | mock 值 | 真实 AppID | 真实 AppID |
| `AI_SERVICE_TYPE` | `deepseek` | `deepseek` | `deepseek` |

### 3.3 settings.py 改造（需修改）

**路径**：`backend/config/settings.py`

```python
import os
from pydantic_settings import BaseSettings

# 通过系统环境变量 APP_ENV 决定加载哪个 .env 文件
_APP_ENV = os.getenv("APP_ENV", "dev")
_ENV_FILE_MAP = {
    "dev":  ".env",
    "test": ".env.test",
    "prod": ".env.prod",
}
_env_file = _ENV_FILE_MAP.get(_APP_ENV, ".env")

class Settings(BaseSettings):
    # 环境标识
    APP_ENV: str = "dev"               # dev | test | prod
    DEBUG: bool = True

    # 核心配置（无默认值的字段，强制从 .env 读取）
    DB_PASSWORD: str                   # 无默认值，必须配置
    JWT_SECRET_KEY: str                # 无默认值，必须配置

    # 其余字段保留默认值（允许开发时快速启动）
    APP_NAME: str = "小时光租衣舍"
    # ...

    class Config:
        env_file = _env_file           # 动态加载对应环境文件
        case_sensitive = True

settings = Settings()

# 环境相关的衍生判断
IS_DEV  = settings.APP_ENV == "dev"
IS_TEST = settings.APP_ENV == "test"
IS_PROD = settings.APP_ENV == "prod"
```

### 3.4 启动命令

```bash
# 开发环境（默认）
python main.py

# 测试环境
APP_ENV=test python main.py

# 生产环境
APP_ENV=prod python main.py

# Windows PowerShell 写法
$env:APP_ENV="test"; python main.py
```

### 3.5 环境相关行为差异

| 行为 | dev | test | prod |
|---|---|---|---|
| `mock_openid` 登录 | ✅ 允许 | ✅ 允许 | ❌ 强制关闭 |
| uvicorn `reload` | ✅ 开启 | ❌ 关闭 | ❌ 关闭 |
| FastAPI 文档 `/docs` | ✅ 开放 | ✅ 开放 | ❌ 关闭 |
| CORS `*` 通配 | ✅ | ✅ | ❌ 仅限微信域名 |
| 错误详情返回前端 | ✅ 返回堆栈 | ✅ 返回摘要 | ❌ 仅返回通用错误 |
| 数据库 | `celestial_dev` | `celestial_test` | `celestial_prod` |

---

## 四、Git 分支 ↔ 环境映射

```
main   (prod)  ──────────────────────────────────── 禁止直接 push，只接受 PR
  ↑
test   (test)  ────────── 开发完成后合并到此，提供体验版供测试组验收
  ↑
dev    (dev)   ────────── 日常开发分支，所有 feature/* fix/* 合并到此

feature/xxx ─┐
fix/xxx     ─┤──→ dev → test → main
refactor/xxx─┘
```

### 4.1 分支工作流

```bash
# 1. 从 dev 新建功能分支
git checkout dev
git checkout -b feature/inventory-management

# 2. 开发完成，提 PR 合并到 dev
git push origin feature/inventory-management
# → 在 GitHub/GitLab 创建 PR: feature/xxx → dev

# 3. dev 验证无误，合并到 test（提供体验版）
git checkout test
git merge dev
git push origin test
# → 微信开发者工具：上传为「体验版」，供测试组扫码

# 4. 测试通过，合并到 main（发布正式版）
git checkout main
git merge test
git push origin main
# → 微信开发者工具：提交审核 → 发布正式版
```

### 4.2 版本命名规范

```
tag 格式：v{major}.{minor}.{patch}-{env}
示例：
  v1.0.0          正式发布
  v1.1.0-beta     测试阶段
  v1.0.1          补丁修复
```

---

## 五、.gitignore 补全清单

在根目录 `.gitignore` 中确认以下条目存在：

```gitignore
# 环境配置（含密钥，禁止提交）
backend/.env
backend/.env.prod

# 可提交（仅含示例/占位值）
# backend/.env.example  → 提交
# backend/.env.test     → 提交（无真实密钥）

# 其他
node_modules/
backend/app.db
*.pyc
__pycache__/
.venv/
```

---

## 六、.env.example 完整模板

**路径**：`backend/.env.example`（需更新，补全所有变量）

```env
# ===== 环境标识 =====
APP_ENV=dev                         # dev | test | prod

# ===== 应用配置 =====
APP_NAME=小时光租衣舍
APP_VERSION=1.0.0
DEBUG=True                          # prod 环境必须改为 False

# ===== 数据库配置 =====
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=                        # 必填，无默认值
DB_NAME=celestial_dev               # dev:celestial_dev / test:celestial_test / prod:celestial_prod

# ===== JWT 配置 =====
JWT_SECRET_KEY=                     # 必填，无默认值，生产请使用随机高强度字符串
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080            # 7天

# ===== 微信小程序配置 =====
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret

# ===== 微信支付配置（prod 环境填真实值）=====
WECHAT_PAY_MCH_ID=
WECHAT_PAY_PRIVATE_KEY=
WECHAT_PAY_SERIAL_NO=
WECHAT_PAY_APIV3_KEY=

# ===== AI 配置 =====
AI_SERVICE_TYPE=deepseek            # deepseek | gemini
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
GEMINI_API_KEY=

# ===== CORS 配置 =====
# dev/test: ["*"]   prod: ["https://servicewechat.com"]
CORS_ORIGINS=["*"]

# ===== TTLock 智能锁（预留）=====
TTLOCK_CLIENT_ID=
TTLOCK_CLIENT_SECRET=
TTLOCK_ACCESS_TOKEN=
```

---

## 七、上线环境切换检查清单

> 每次从 test → main 合并前，必须逐项确认：

| 类别 | 检查项 | 负责人 |
|---|---|---|
| 前端 | `env.js` 中 `release.apiBase` 已配置为正式 HTTPS 域名 | 前端 |
| 前端 | 微信公众平台「服务器域名」已配置正式域名 | 运维 |
| 前端 | `release.enableMock = false` | 前端 |
| 后端 | `.env.prod` 中 `DEBUG=False` | 后端 |
| 后端 | `.env.prod` 中 `JWT_SECRET_KEY` 为随机高强度密钥 | 后端 |
| 后端 | `.env.prod` 中 `CORS_ORIGINS` 已限制 | 后端 |
| 后端 | `.env.prod` 中微信 AppID/Secret 为真实值 | 后端 |
| 后端 | 使用 `APP_ENV=prod python main.py` 启动 | 运维 |
| 数据库 | `celestial_prod` 数据库已初始化，`check_db.py` 通过 | 后端 |
| 数据库 | dev/test 数据已清空（无测试数据污染生产）| 后端 |

---

*本文档由研发 Lead 维护，每次环境调整后同步更新。*
