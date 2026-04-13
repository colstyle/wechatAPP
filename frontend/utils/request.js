// frontend/utils/request.js

const request = function (url, method = 'GET', data = {}, needAuth = true, retryAuth = true) {
  const app = getApp()
  if (!app.apiBase || typeof app.apiBase !== 'string' || !/^https?:\/\//.test(app.apiBase)) {
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
    if (needAuth && app.globalData.token) {
      header['Authorization'] = `Bearer ${app.globalData.token}`
    }

    wx.request({
      url: app.apiBase + url,
      method: method,
      data: data,
      header: header,
      success: (res) => {
        if (res.statusCode === 200) {
          if (res.data.code === 0) {
            resolve(res.data)
          } else {
            // == 统一错误日志 ==
            console.error(`[API 业务异常] ${method} ${url}`, res.data)
            
            // 未登录，尝试重新登录
            if (res.data.code === 401) {
              app.wechatLogin()
                .then(() => {
                  // 重新请求
                  request(url, method, data, needAuth, false).then(resolve).catch(reject)
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
          console.warn(`[API 鉴权失效] ${method} ${url}`)
          app.globalData.token = null
          app.globalData.userInfo = null
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          app.wechatLogin()
            .then(() => {
              request(url, method, data, needAuth, false).then(resolve).catch(reject)
            })
            .catch(reject)
        } else {
          // == 统一错误日志 ==
          console.error(`[API HTTP 错误] ${res.statusCode} ${method} ${url}`, res.data)
          wx.showToast({
            title: '网络请求失败',
            icon: 'none'
          })
          reject({ message: '网络请求失败', statusCode: res.statusCode, data: res.data })
        }
      },
      fail: (err) => {
        // == 统一错误日志 ==
        console.error(`[API 网络异常] ${method} ${url}`, err)
        if (!app.globalData._apiBaseWarned) {
          app.globalData._apiBaseWarned = true
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
}

module.exports = request
