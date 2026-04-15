// pages/settings/settings.js
const app = getApp()
const ALLOWED_API_BASES = [
  'https://www.celestialaiplus.com',
  'https://7469-time-capsule-surver-7cya285298de-1421670163.tcb.qcloud.la',
  'https://tcb-api.tencentcloudapi.com'
]

function normalizeApiBase(raw) {
  let value = String(raw || '').trim()
  if (!value) return ''
  if (value.endsWith('/')) value = value.slice(0, -1)
  return value
}

function isHttpsBase(value) {
  return /^https:\/\/[^/\s]+$/i.test(value)
}

function isDevTools() {
  try {
    const info = wx.getSystemInfoSync()
    return info && info.platform === 'devtools'
  } catch (e) {
    return false
  }
}

function isDevEnv() {
  try {
    const gd = (app && app.globalData) ? app.globalData : {}
    return gd && gd.ENV === 'dev'
  } catch (e) {
    return false
  }
}

Page({
  data: {
    userInfo: {},
    apiBase: '',
    mockOpenid: ''
  },

  onLoad() {
    const savedApiBase = normalizeApiBase(wx.getStorageSync('apiBase') || app.apiBase)
    const mockOpenid = wx.getStorageSync('mockOpenid') || ''
    this.setData({ apiBase: savedApiBase, mockOpenid })
  },

  onShow() {
    if (app.globalData.token) {
      this.setData({ userInfo: app.globalData.userInfo || {} })
    } else {
      this.setData({ userInfo: {} })
    }
  },

  // 头像点击
  onAvatarTap() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]
        // TODO: 上传头像
        wx.showToast({ title: '功能开发中', icon: 'none' })
      }
    })
  },

  // 个人信息
  onProfileTap() {
    wx.navigateTo({
      url: '/pages/profile/edit'
    })
  },

  // 我的尺码
  onSizeTap() {
    wx.navigateTo({
      url: '/pages/size/size'
    })
  },

  // 关于我们
  onAboutTap() {
    wx.showModal({
      title: '关于小时光租衣舍',
      content: '小时光租衣舍 - 专业的服装租赁平台\n\n提供按天、按次、订阅等多种租赁方式，让时尚触手可及。',
      showCancel: false
    })
  },

  onApiBaseInput(e) {
    this.setData({ apiBase: e.detail.value })
  },

  onMockOpenidInput(e) {
    this.setData({ mockOpenid: e.detail.value })
    wx.setStorageSync('mockOpenid', e.detail.value)
  },

  useMockUser() {
    this.setData({ mockOpenid: 'user_1' })
    wx.setStorageSync('mockOpenid', 'user_1')
  },

  useMockAdmin() {
    this.setData({ mockOpenid: 'admin_1' })
    wx.setStorageSync('mockOpenid', 'admin_1')
  },

  reLogin() {
    wx.showLoading({ title: '登录中...' })
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
    app.globalData.token = null
    app.globalData.userInfo = null
    app.ensureLogin(true)
      .then(() => {
        wx.hideLoading()
        this.setData({ userInfo: app.globalData.userInfo || {} })
        wx.showToast({ title: '已切换', icon: 'success' })
      })
      .catch(() => {
        wx.hideLoading()
        wx.showToast({ title: '登录失败', icon: 'none' })
      })
  },

  saveApiBase() {
    const apiBase = normalizeApiBase(this.data.apiBase)
    if (!apiBase) {
      wx.showToast({ title: '请输入后端地址', icon: 'none' })
      return
    }
    if (!(isDevEnv() && isDevTools())) {
      if (!isHttpsBase(apiBase)) {
        wx.showToast({ title: '小程序仅支持 HTTPS 域名', icon: 'none' })
        return
      }
      if (!ALLOWED_API_BASES.includes(apiBase)) {
        wx.showToast({ title: '不在合法域名白名单', icon: 'none' })
        return
      }
    }
    app.setApiBase(apiBase)
    this.setData({ apiBase })
    wx.showToast({ title: '已保存', icon: 'success' })
  },

  testApiBase() {
    const apiBase = normalizeApiBase(this.data.apiBase)
    if (!apiBase) {
      wx.showToast({ title: '请输入后端地址', icon: 'none' })
      return
    }
    if (!(isDevEnv() && isDevTools())) {
      if (!isHttpsBase(apiBase)) {
        wx.showToast({ title: '小程序仅支持 HTTPS 域名', icon: 'none' })
        return
      }
      if (!ALLOWED_API_BASES.includes(apiBase)) {
        wx.showToast({ title: '不在合法域名白名单', icon: 'none' })
        return
      }
    }
    wx.showLoading({ title: '测试中...' })
    wx.request({
      url: apiBase + '/health',
      method: 'GET',
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200 && res.data && res.data.status === 'ok') {
          wx.showToast({ title: '连接正常', icon: 'success' })
        } else {
          wx.showToast({ title: '连接失败', icon: 'none' })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({ title: '连接失败', icon: 'none' })
      }
    })
  }
})
