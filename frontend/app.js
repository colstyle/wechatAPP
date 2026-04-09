// app.js
App({
  // API基础地址
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
    const value = (apiBase || '').trim()
    if (!value) return
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
  }
})
