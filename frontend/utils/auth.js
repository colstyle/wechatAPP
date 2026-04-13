// frontend/utils/auth.js
const app = getApp()

const auth = {
  // 获取当前 Token
  getToken() {
    return wx.getStorageSync('token') || null
  },

  // 是否已登录
  isLoggedIn() {
    return !!this.getToken()
  },

  // 获取用户信息
  getUserInfo() {
    return wx.getStorageSync('userInfo') || null
  },

  // 检查是否具有某种角色 (例如: 'admin')
  hasRole(role) {
    const userInfo = this.getUserInfo()
    if (!userInfo) return false
    // 后端有时传 admin 为 '2'，需兼容
    if (role === 'admin') {
      return userInfo.role === 'admin' || userInfo.role === '2' || userInfo.role === 2
    }
    return String(userInfo.role) === String(role)
  },

  // 执行登出操作清理本地缓存
  logout() {
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
    if (app && app.globalData) {
      app.globalData.token = null
      app.globalData.userInfo = null
    }
  },

  // 更新本地缓存的 UserInfo
  updateUserInfo(newInfo) {
    let current = this.getUserInfo() || {}
    current = { ...current, ...newInfo }
    wx.setStorageSync('userInfo', current)
    if (app && app.globalData) {
      app.globalData.userInfo = current
    }
  }
}

module.exports = auth
