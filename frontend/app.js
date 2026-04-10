// app.js
App({
  // API基础地址 (电脑局域网 IP，供真机真机测试用)
  apiBase: 'http://192.168.43.79:8000',

  // 全局数据
  globalData: {
    token: null,
    userInfo: null,
    selectedDate: null, // 用户选择的租赁日期 (YYYY-MM-DD)
    apiBase: null,
    _apiBaseWarned: false,
    _loginPromise: null,
    _adminAutoRouted: false
  },

  onLaunch() {
    // 获取系统信息与胶囊按钮位置（用于自定义导航栏）
    this.getNavBarData()

    const savedApiBase = wx.getStorageSync('apiBase')
    if (savedApiBase) {
      this.apiBase = savedApiBase
      this.globalData.apiBase = savedApiBase
    } else {
      this.globalData.apiBase = this.apiBase
    }
    this.globalData.token = null
    this.globalData.userInfo = null
    this.ensureLogin(true)
      .then(() => {
        const userInfo = this.globalData.userInfo || {}
        if ((userInfo.role === 'admin' || userInfo.role === '2' || userInfo.role === 2) && !this.globalData._adminAutoRouted) {
          this.globalData._adminAutoRouted = true
          setTimeout(() => {
            wx.reLaunch({ url: '/pages/admin/orders/orders' })
          }, 0)
        }
      })
      .catch(() => {})
  },

  setApiBase(apiBase) {
    let value = (apiBase || '').trim()
    if (!value) return
    if (value.endsWith('/')) value = value.slice(0, -1)
    this.apiBase = value
    this.globalData.apiBase = value
    wx.setStorageSync('apiBase', value)
  },

  // 检查登录状态
  checkLogin() {
    return this.ensureLogin()
  },

  ensureLogin(forceLogin = false) {
    if (this.globalData._loginPromise) return this.globalData._loginPromise

    const cachedToken = this.globalData.token || wx.getStorageSync('token')
    if (cachedToken) this.globalData.token = cachedToken

    const hasToken = !!this.globalData.token
    if (hasToken && !forceLogin) {
      this.globalData._loginPromise = this.getUserInfo()
        .then(res => {
          if (res && res.code === 0) {
            this.globalData.userInfo = res.data
            wx.setStorageSync('userInfo', res.data)
          }
          return res
        })
        .finally(() => {
          this.globalData._loginPromise = null
        })
      return this.globalData._loginPromise
    }

    this.globalData._loginPromise = this.wechatLogin()
      .then(res => {
        if (res && res.code === 0) {
          this.globalData.userInfo = res.data.user
          wx.setStorageSync('userInfo', res.data.user)
        }
        return res
      })
      .finally(() => {
        this.globalData._loginPromise = null
      })
    return this.globalData._loginPromise
  },

  // 获取用户信息
  getUserInfo() {
    return this.request('/api/user/profile', 'GET')
      .then(res => {
        if (res.code === 0) {
          this.globalData.userInfo = res.data
        }
        return res
      })
  },

  // 微信登录
  wechatLogin() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (res) => {
          if (res.code) {
            const payload = { code: res.code }
            const mockOpenid = wx.getStorageSync('mockOpenid')
            if (mockOpenid) payload.mock_openid = String(mockOpenid).trim()
            this.request('/api/user/login', 'POST', payload)
              .then(response => {
                if (response.code === 0) {
                  this.globalData.token = response.data.token
                  this.globalData.userInfo = response.data.user
                  wx.setStorageSync('token', response.data.token)
                  wx.setStorageSync('userInfo', response.data.user)
                  resolve(response)
                } else {
                  reject(response)
                }
              })
              .catch(err => reject(err))
          } else {
            reject({ message: '获取code失败' })
          }
        },
        fail: reject
      })
    })
  },

  // 统一请求方法
  request(url, method = 'GET', data = {}, needAuth = true, retryAuth = true) {
    if (!this.apiBase || typeof this.apiBase !== 'string' || !/^https?:\/\//.test(this.apiBase)) {
      wx.showToast({
        title: '请先在设置页配置后端地址',
        icon: 'none'
      })
      return Promise.reject({ message: 'API_BASE_NOT_SET' })
    }

    return new Promise((resolve, reject) => {
      const header = {
        'content-type': 'application/json'
      }

      // 添加token
      if (needAuth && this.globalData.token) {
        header['Authorization'] = `Bearer ${this.globalData.token}`
      }

      wx.request({
        url: this.apiBase + url,
        method: method,
        data: data,
        header: header,
        success: (res) => {
          if (res.statusCode === 200) {
            if (res.data.code === 0) {
              resolve(res.data)
            } else {
              // 未登录，尝试重新登录
              if (res.data.code === 401) {
                this.wechatLogin()
                  .then(() => {
                    // 重新请求
                    this.request(url, method, data, needAuth, false).then(resolve).catch(reject)
                  })
                  .catch(reject)
              } else {
                wx.showToast({
                  title: res.data.message || '请求失败',
                  icon: 'none'
                })
                reject(res.data)
              }
            }
          } else if (res.statusCode === 401 && retryAuth) {
            this.globalData.token = null
            this.globalData.userInfo = null
            wx.removeStorageSync('token')
            wx.removeStorageSync('userInfo')
            this.wechatLogin()
              .then(() => {
                this.request(url, method, data, needAuth, false).then(resolve).catch(reject)
              })
              .catch(reject)
          } else {
            wx.showToast({
              title: '网络请求失败',
              icon: 'none'
            })
            reject({ message: '网络请求失败', statusCode: res.statusCode, data: res.data })
          }
        },
        fail: (err) => {
          if (!this.globalData._apiBaseWarned) {
            this.globalData._apiBaseWarned = true
            wx.showToast({
              title: '网络异常，请检查后端地址',
              icon: 'none'
            })
          } else {
            wx.showToast({
              title: '网络异常',
              icon: 'none'
            })
          }
          reject(err)
        }
      })
    })
  },

  // 上传图片
  uploadImage(filePath) {
    return new Promise((resolve, reject) => {
      wx.uploadFile({
        url: this.apiBase + '/api/upload/image',
        filePath: filePath,
        name: 'file',
        header: {
          'Authorization': `Bearer ${this.globalData.token}`
        },
        success: (res) => {
          const data = JSON.parse(res.data)
          if (data.code === 0) {
            resolve(data.data.url)
          } else {
            reject(data)
          }
        },
        fail: reject
      })
    })
  },

  // 格式化日期
  formatDate(dateStr) {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  },

  // 格式化日期时间
  formatDateTime(dateStr) {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hour = String(date.getHours()).padStart(2, '0')
    const minute = String(date.getMinutes()).padStart(2, '0')
    return `${year}-${month}-${day} ${hour}:${minute}`
  },

  // 获取自定义导航栏所需的基础数据（使用新 API，避免 getSystemInfoSync 废弃警告）
  getNavBarData() {
    try {
      const windowInfo = wx.getWindowInfo()           // 替代 getSystemInfoSync
      const menuButtonInfo = wx.getMenuButtonBoundingClientRect()

      const statusBarHeight = windowInfo.statusBarHeight
      const menuTop    = menuButtonInfo.top
      const menuHeight = menuButtonInfo.height

      // 导航栏总高度 = (胶囊上边距 - 状态栏高度) × 2 + 胶囊高度 + 状态栏高度
      const navBarHeight = (menuTop - statusBarHeight) * 2 + menuHeight + statusBarHeight

      this.globalData.navBarData = {
        statusBarHeight,
        navBarHeight,
        menuTop,
        menuHeight,
        windowWidth: windowInfo.windowWidth
      }
    } catch (e) {
      // 降级兜底，避免旧设备异常崩溃
      this.globalData.navBarData = {
        statusBarHeight: 44,
        navBarHeight: 88,
        menuTop: 48,
        menuHeight: 32,
        windowWidth: 375
      }
    }
  }
})
