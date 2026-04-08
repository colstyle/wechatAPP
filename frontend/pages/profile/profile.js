// pages/profile/profile.js
const app = getApp()
const orderApi = require('../../utils/api').orderApi
const subscriptionApi = require('../../utils/api').subscriptionApi

Page({
  data: {
    userInfo: {},
    activeSubscription: null,
    orderStats: {
      pending: 0,
      shipping: 0,
      renting: 0,
      returning: 0
    }
  },

  onLoad() {
    this.checkLogin()
  },

  onShow() {
    if (app.globalData.token) {
      this.loadUserInfo()
      this.loadOrderStats()
      this.loadSubscription()
    }
  },

  // 检查登录
  checkLogin() {
    if (!app.globalData.token) {
      this.setData({ userInfo: {} })
    }
  },

  // 加载用户信息
  loadUserInfo() {
    app.getUserInfo()
      .then(res => {
        this.setData({ userInfo: res.data })
      })
      .catch(err => {
        console.error('获取用户信息失败', err)
      })
  },

  // 加载订单统计
  loadOrderStats() {
    const getStatusCount = (status) => {
      return orderApi.getOrders({ status: status })
        .then(res => res.data.list.length)
        .catch(() => 0)
    }

    Promise.all([
      getStatusCount(0),
      getStatusCount(1),
      getStatusCount(2),
      getStatusCount(3)
    ]).then(([pending, shipping, renting, returning]) => {
      this.setData({
        orderStats: {
          pending,
          shipping,
          renting,
          returning
        }
      })
    })
  },

  // 加载订阅信息
  loadSubscription() {
    subscriptionApi.getActiveSubscription()
      .then(res => {
        this.setData({ activeSubscription: res.data })
      })
      .catch(err => {
        console.error('获取订阅信息失败', err)
      })
  },

  // 登录处理
  handleLogin() {
    // 已登录，跳转到设置页面
    if (app.globalData.token) {
      wx.navigateTo({
        url: '/pages/settings/settings'
      })
      return
    }

    // 执行微信登录
    wx.showLoading({ title: '登录中...' })

    wx.login({
      success: (res) => {
        if (res.code) {
          // 调用后端登录接口
          wx.request({
            url: 'http://127.0.0.1:8000/api/user/login',
            method: 'POST',
            data: {
              code: res.code
            },
            success: (loginRes) => {
              wx.hideLoading()
              if (loginRes.data.code === 0) {
                const { token, user_info } = loginRes.data.data

                // 保存token和用户信息
                app.globalData.token = token
                app.globalData.userInfo = user_info

                // 保存到本地存储
                wx.setStorageSync('token', token)
                wx.setStorageSync('userInfo', user_info)

                // 更新页面数据
                this.setData({ userInfo: user_info })

                // 加载订单和订阅信息
                this.loadOrderStats()
                this.loadSubscription()

                wx.showToast({
                  title: '登录成功',
                  icon: 'success'
                })
              } else {
                wx.showToast({
                  title: loginRes.data.message || '登录失败',
                  icon: 'none'
                })
              }
            },
            fail: () => {
              wx.hideLoading()
              wx.showToast({
                title: '网络错误，请稍后重试',
                icon: 'none'
              })
            }
          })
        } else {
          wx.hideLoading()
          wx.showToast({
            title: '获取登录凭证失败',
            icon: 'none'
          })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({
          title: '登录失败，请稍后重试',
          icon: 'none'
        })
      }
    })
  },

  // 个人信息
  onProfileTap() {
    if (!app.globalData.token) {
      this.handleLogin()
    } else {
      wx.navigateTo({
        url: '/pages/settings/settings'
      })
    }
  },

  // 订单列表
  onOrdersTap(e) {
    const status = e.currentTarget.dataset.status
    const statusText = {
      0: '待付款',
      1: '待发货',
      2: '租赁中',
      3: '待归还'
    }
    wx.navigateTo({
      url: `/pages/orders/orders?status=${status}&title=${statusText[status]}`
    })
  },

  // 收货地址
  onAddressTap() {
    wx.navigateTo({
      url: '/pages/address/address'
    })
  },

  // 预约试穿
  onAppointmentTap() {
    wx.navigateTo({
      url: '/pages/appointment/appointment'
    })
  },

  // 订阅管理
  onSubscribeTap() {
    wx.navigateTo({
      url: '/pages/subscribe/subscribe'
    })
  },

  // 收藏列表
  onFavoritesTap() {
    wx.navigateTo({
      url: '/pages/favorites/favorites'
    })
  },

  // 评价列表
  onReviewsTap() {
    wx.navigateTo({
      url: '/pages/review/review?type=my'
    })
  },

  // 意见反馈
  onFeedbackTap() {
    wx.showModal({
      title: '意见反馈',
      content: '请通过客服电话联系我们: 400-123-4567',
      showCancel: false
    })
  },

  // 设置
  onSettingsTap() {
    wx.navigateTo({
      url: '/pages/settings/settings'
    })
  },

  // 退出登录
  onLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除本地存储
          wx.clearStorageSync()
          // 清除全局数据
          app.globalData.token = null
          app.globalData.userInfo = null
          app.globalData.activeSubscription = null
          // 更新页面
          this.setData({
            userInfo: {},
            activeSubscription: null,
            orderStats: {
              pending: 0,
              shipping: 0,
              renting: 0,
              returning: 0
            }
          })
          wx.showToast({
            title: '已退出登录',
            icon: 'none'
          })
        }
      }
    })
  }
})