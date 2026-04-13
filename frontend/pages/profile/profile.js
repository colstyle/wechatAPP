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
    },
    imgBase: app.imgBase
  },

  onLoad() {
    this.refreshUser()
  },

  onShow() {
    this.refreshUser()
  },

  refreshUser() {
    app.ensureLogin()
      .then(() => {
        const userInfo = app.globalData.userInfo || {}
        this.setData({ userInfo })
        this.loadOrderStats()
        this.maybeRouteAdmin(userInfo)
      })
      .catch(() => {
        this.setData({ userInfo: {} })
      })
  },

  maybeRouteAdmin(userInfo) {
    if (!userInfo || !(userInfo.role === 'admin' || userInfo.role === '2' || userInfo.role === 2)) return
    if (app.globalData._adminAutoRouted) return
    app.globalData._adminAutoRouted = true
    wx.navigateTo({ url: '/pages/admin/orders/orders' })
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
    if (app.globalData.token) {
      wx.navigateTo({ url: '/pages/settings/settings' })
      return
    }
    wx.showLoading({ title: '登录中...' })
    app.ensureLogin(true)
      .then(() => {
        wx.hideLoading()
        const userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo') || {}
        this.setData({ userInfo })
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

  onSettingsTap() {
    wx.navigateTo({ url: '/pages/settings/settings' })
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
  },

  // 一键拨号
  callStore() {
    wx.makePhoneCall({
      phoneNumber: '18661771101' // 真实店主联络
    })
  },

  // 打开地图 (模拟，实际发布时需配置坐标)
  openMap() {
    wx.showModal({
      title: '门店位置',
      content: '青岛市市北区青建太阳岛 2201室。点击确定可复制地址',
      confirmText: '复制地址',
      success: (res) => {
        if (res.confirm) {
          wx.setClipboardData({
            data: '青岛市市北区青建太阳岛 2201',
            success: () => wx.showToast({ title: '地址已复制', icon: 'none' })
          })
        }
      }
    })
  }
})
