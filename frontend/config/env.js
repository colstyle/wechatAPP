// frontend/config/env.js
// 多环境配置 — 利用微信官方 API 自动识别运行版本，无需手动切换代码
//
// envVersion 对应关系：
//   'develop' → 开发版（微信开发者工具）     → dev
//   'trial'   → 体验版（扫描体验二维码）     → test
//   'release' → 正式版（小程序商店）         → prod

const { envVersion } = wx.getAccountInfoSync().miniProgram

const ENV_MAP = {
  develop: {
    ENV:        'dev',
    apiBase:    'http://192.168.43.79:8000',   // 本机局域网 IP（可在设置页手动覆盖）
    enableMock: true,   // 允许 mockOpenid 固定调试身份
    enableLog:  true,   // 开启 console.log
  },
  trial: {
    ENV:        'test',
    apiBase:    'http://YOUR_TEST_SERVER:8000', // 测试服务器地址 ← 上线前填写
    enableMock: true,   // 测试阶段允许 mock，方便测试组切换身份
    enableLog:  true,
  },
  release: {
    ENV:        'prod',
    apiBase:    'https://api.yourdomain.com',   // 正式域名，必须 HTTPS ← 上线前填写
    enableMock: false,  // 生产环境严禁 mock
    enableLog:  false,  // 关闭控制台日志
  },
}

// 未知版本降级到 dev（避免真机调试崩溃）
const config = ENV_MAP[envVersion] || ENV_MAP.develop

// 开发调试：打印当前环境
if (config.enableLog) {
  console.log(`[ENV] 当前环境: ${config.ENV} (envVersion=${envVersion})`)
  console.log(`[ENV] API 地址: ${config.apiBase}`)
}

module.exports = config
