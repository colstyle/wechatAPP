// pages/order/order.js
const app = getApp()
const orderApi = require('../../utils/api').orderApi

Page({
  data: {
    orderStats: {
      renting: 0,
      returning: 0
    }
  },

  onLoad() {
    this.checkLogin()
  },

  onShow() {
    if (app.globalData.token) {
      this.loadOrderStats()
    }
  },

  // 检查登录
  checkLogin() {
    if (!app.globalData.token) {
      app.wechatLogin()
        .then(() => {
          this.loadOrderStats()
        })
        .catch(err => {
          console.error('登录失败', err)
        })
    }
  },

  // 加载订单统计
  loadOrderStats() {
    const getStatusCount = (status) => {
      return orderApi.getOrders({ status: status })
        .then(res => res.data.list.length)
        .catch(() => 0)
    }

    Promise.all([
      getStatusCount(2), // 租赁中
      getStatusCount(3)  // 待归还
    ]).then(([renting, returning]) => {
      this.setData({
        orderStats: {
          renting,
          returning
        }
      })
    })
  },

  // 查看订单列表
  onOrdersTap(e) {
    const status = e.currentTarget.dataset.status
    const statusText = {
      0: '待付款',
      1: '待发货',
      2: '租赁中',
      3: '待归还',
      4: '已归还',
      5: '已取消',
      6: '已完成'
    }
    wx.navigateTo({
      url: `/pages/orders/orders?status=${status}&title=${statusText[status]}`
    })
  },

  // 租衣服
  onRentTap() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  },

  // 预约试穿
  onAppointmentTap() {
    wx.navigateTo({
      url: '/pages/appointment/appointment'
    })
  },

  // 会员订阅
  onSubscribeTap() {
    wx.navigateTo({
      url: '/pages/subscribe/subscribe'
    })
  },

  // 收货地址
  onAddressTap() {
    wx.navigateTo({
      url: '/pages/address/address'
    })
  }
})
