// pages/pay/pay.js
const app = getApp()
const orderApi = require('../../utils/api').orderApi

Page({
  data: {
    orderId: null,
    order: null,
    selectedPayment: 'wechat'
  },

  onLoad(options) {
    if (options.order_id) {
      this.setData({ orderId: parseInt(options.order_id) })
      this.loadOrder()
    }
  },

  // 加载订单
  loadOrder() {
    orderApi.getOrder(this.data.orderId)
      .then(res => {
        const order = res.data
        order.rentalTypeText = this.getRentalTypeText(order.rental_type)
        this.setData({ order })
      })
      .catch(err => {
        console.error('获取订单失败', err)
        wx.showToast({ title: '获取订单失败', icon: 'none' })
      })
  },

  // 获取租赁类型文本
  getRentalTypeText(type) {
    const map = {
      1: '按天租赁',
      2: '单次租赁',
      3: '订阅租赁'
    }
    return map[type] || '未知'
  },

  // 选择支付方式
  onPaymentTap(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ selectedPayment: type })
  },

  // 支付
  onPay() {
    if (!this.data.selectedPayment) {
      wx.showToast({ title: '请选择支付方式', icon: 'none' })
      return
    }

    wx.showLoading({ title: '支付中...' })

    orderApi.payOrder(this.data.orderId)
      .then(res => {
        wx.hideLoading()
        wx.showToast({ title: '支付成功', icon: 'success' })
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      })
      .catch(err => {
        wx.hideLoading()
        wx.showToast({ title: '支付失败', icon: 'none' })
      })
  }
})
