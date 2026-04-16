// frontend/utils/request.js

/**
 * 统一请求封装
 * 增加全局错误拦截、网络状态检查、以及生产环境友好的报错提示
 */
const request = function (url, method = 'GET', data = {}, needAuth = true, retryAuth = true) {
  const app = getApp()
  
  // 1. 基础配置校验
  if (!app.apiBase || typeof app.apiBase !== 'string' || !/^https?:\/\//.test(app.apiBase)) {
    wx.showToast({
      title: '后端地址配置异常',
      icon: 'none'
    })
    return Promise.reject({ message: 'API_BASE_NOT_SET' })
  }

  return new Promise((resolve, reject) => {
    // 2. 网络连通性预检
    wx.getNetworkType({
      success: (res) => {
        if (res.networkType === 'none') {
          wx.showToast({
            title: '网络不可用，请检查网络设置',
            icon: 'none'
          })
          reject({ message: 'NETWORK_NONE' })
          return
        }
      }
    })

    const header = {
      'content-type': 'application/json'
    }

    // 3. 身份令牌注入
    if (needAuth && app.globalData.token) {
      header['Authorization'] = `Bearer ${app.globalData.token}`
    }

    wx.request({
      url: app.apiBase + url,
      method: method,
      data: data,
      header: header,
      timeout: 15000, // 15秒超时
      success: (res) => {
        const { statusCode, data } = res

        // 4. 业务状态码处理
        if (statusCode === 200) {
          if (data.code === 0) {
            resolve(data)
          } else if (data.code === 401) {
            handleUnauthorized(url, method, data, needAuth, resolve, reject)
          } else {
            // 业务逻辑报错提示
            console.error(`[API 业务异常] ${method} ${url}`, data)
            wx.showToast({
              title: data.message || '请求服务忙',
              icon: 'none'
            })
            reject(data)
          }
        } 
        // 5. HTTP 状态码深度处理
        else if (statusCode === 401 && retryAuth) {
          handleUnauthorized(url, method, data, needAuth, resolve, reject)
        } 
        else if (statusCode === 500) {
          console.error(`[API 500 严重错误] ${method} ${url}`, data)
          wx.showModal({
            title: '服务暂时不可用',
            content: '小时光系统正在维护或遇到暂时性波动，请稍后再试。',
            showCancel: false,
            confirmColor: '#8E9775' // 莫兰迪色系主调
          })
          reject({ message: 'INTERNAL_SERVER_ERROR', statusCode: 500 })
        }
        else {
          console.error(`[API HTTP 错误] ${statusCode} ${method} ${url}`, data)
          wx.showToast({
            title: `请求错误 (${statusCode})`,
            icon: 'none'
          })
          reject({ message: 'HTTP_ERROR', statusCode })
        }
      },
      fail: (err) => {
        // 6. 网络异常处理
        console.error(`[API 网络异常/超时] ${method} ${url}`, err)
        wx.showToast({
          title: '连接超时，请检查网络后再试',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

/**
 * 处理鉴权失效
 */
function handleUnauthorized(url, method, data, needAuth, resolve, reject) {
  const app = getApp()
  console.warn(`[API 鉴权失效] 尝试静默刷新 Token`)
  
  app.globalData.token = null
  wx.removeStorageSync('token')
  
  app.wechatLogin()
    .then(() => {
      // 登录成功后重试原请求
      request(url, method, data, needAuth, false).then(resolve).catch(reject)
    })
    .catch(() => {
      // 登录彻底失败
      wx.showToast({ title: '登录状态已失效', icon: 'none' })
      reject({ message: 'UNAUTHORIZED' })
    })
}

module.exports = request
