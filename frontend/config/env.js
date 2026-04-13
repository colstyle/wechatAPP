// frontend/config/env.js
// 多环境配置 — 利用微信官方 API 自动识别运行版本，无需手动切换代码
//
// envVersion 对应关系：
//   'develop' → 开发版（微信开发者工具）     → dev
//   'trial'   → 体验版（扫描体验二维码）     → test
//   'release' → 正式版（小程序商店）         → prod

const { envVersion } = wx.getAccountInfoSync().miniProgram
const systemInfo = wx.getSystemInfoSync()
const isDevTools = systemInfo.platform === 'devtools'

// 局域网 IP (仅用于真机调试)
const LOCAL_IP = '192.168.43.79'
// 本地回环 (仅用于模拟器，最稳定)
const LOCALHOST = '127.0.0.1'

const ENV_MAP = {
  develop: {
    ENV:        'dev',
    apiBase:    'https://xiaoshiguang-245804-5-1421670163.sh.run.tcloudbase.com',
    imgBase:    'https://xiaoshiguang-245804-5-1421670163.sh.run.tcloudbase.com/static/images',
    enableMock: true,
    enableLog:  true,
  },
  trial: {
    ENV:        'test',
    apiBase:    'https://xiaoshiguang-245804-5-1421670163.sh.run.tcloudbase.com',
    imgBase:    'https://xiaoshiguang-245804-5-1421670163.sh.run.tcloudbase.com/static/images',
    enableMock: true,
    enableLog:  true,
  },
  release: {
    ENV:        'prod',
    apiBase:    'https://xiaoshiguang-245804-5-1421670163.sh.run.tcloudbase.com',
    imgBase:    'https://xiaoshiguang-245804-5-1421670163.sh.run.tcloudbase.com/static/images',
    enableMock: false,
    enableLog:  false,
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
