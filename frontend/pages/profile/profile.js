// pages/profile/profile.js
const app = getApp()
const orderApi = require('../../utils/api').orderApi

Page({
  data: {
    userInfo: {},
    orderStats: {
      pendingPickup: 0,
      renting: 0,
      pendingAudit: 0
    }
  },

  onLoad() {
    this.checkLogin()
  },

  onShow() {
    if (app.globalData.token) {
      this.loadUserInfo()
      this.loadOrderStats()
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
      getStatusCount(1),
      getStatusCount(2),
      getStatusCount(4)
    ]).then(([pendingPickup, renting, pendingAudit]) => {
      this.setData({
        orderStats: {
          pendingPickup,
          renting,
          pendingAudit
        }
      })
    })
  },

  // 登录处理
  handleLogin() {
    if (app.globalData.token) return
    wx.showLoading({ title: '登录中...' })
    app.wechatLogin()
      .then(() => {
        wx.hideLoading()
        this.loadUserInfo()
        this.loadOrderStats()
      })
      .catch(() => {
        wx.hideLoading()
        wx.showToast({ title: '登录失败', icon: 'none' })
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
      1: '待取衣',
      2: '租赁中',
      4: '待审核'
    }
    wx.navigateTo({
      url: `/pages/orders/orders?status=${status}&title=${statusText[status]}`
    })
  },

  onServiceTap() {
    wx.navigateTo({ url: '/pages/chat/chat' })
  },

  // 店主管理
  onAdminTap() {
    wx.navigateTo({
      url: '/pages/admin/orders/orders'
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
          // 更新页面
          this.setData({
            userInfo: {},
            orderStats: {
              pendingPickup: 0,
              renting: 0,
              pendingAudit: 0
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
