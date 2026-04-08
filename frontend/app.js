// app.js
App({
  // API基础地址
  apiBase: 'http://127.0.0.1:8000',

  // 全局数据
  globalData: {
    token: null,
    userInfo: null,
    activeSubscription: null
  },

  onLaunch() {
    // 检查登录状态
    this.checkLogin()
  },

  // 检查登录状态
  checkLogin() {
    const token = wx.getStorageSync('token')
    if (token) {
      this.globalData.token = token
      this.getUserInfo()
      this.getActiveSubscription()
    }
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

  // 获取激活中的订阅
  getActiveSubscription() {
    return this.request('/api/subscription/active', 'GET')
      .then(res => {
        if (res.code === 0) {
          this.globalData.activeSubscription = res.data
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
            this.request('/api/user/login', 'POST', { code: res.code })
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
  request(url, method = 'GET', data = {}, needAuth = true) {
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
                    this.request(url, method, data, needAuth).then(resolve).catch(reject)
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
          } else {
            reject({ message: '网络请求失败' })
          }
        },
        fail: (err) => {
          wx.showToast({
            title: '网络异常',
            icon: 'none'
          })
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
