const app = getApp()
const orderApi = require('../../../utils/api').orderApi
const util = require('../../../utils/util')

Page({
  data: {
    orderId: null,
    order: null,
    loading: false
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ orderId: parseInt(options.id) })
      this.loadOrder()
    }
  },

  loadOrder() {
    this.setData({ loading: true })
    orderApi.getOrder(this.data.orderId)
      .then(res => {
        const order = res.data
        order.statusText = util.orderStatusMap[order.status] || '未知'
        order.rentalTypeText = util.rentalTypeMap[order.rental_type] || '未知'
        this.setData({ order, loading: false })
      })
      .catch(err => {
        this.setData({ loading: false })
        console.error('获取订单详情失败', err)
        wx.showToast({ title: '获取订单详情失败', icon: 'none' })
      })
  },

  onPickupTap() {
    if (!this.data.order) return
    wx.showModal({
      title: '确认取衣',
      content: '确认已到店取衣并开始24小时租赁吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '提交中...' })
          orderApi.pickupOrder(this.data.orderId)
            .then(() => {
              wx.hideLoading()
              wx.showToast({ title: '取衣成功', icon: 'success' })
              this.loadOrder()
            })
            .catch(err => {
              wx.hideLoading()
              console.error('取衣失败', err)
              wx.showToast({ title: '取衣失败', icon: 'none' })
            })
        }
      }
    })
  },

  onReturnTap() {
    if (!this.data.order) return
    wx.showModal({
      title: '申请还衣',
      content: '确认申请还衣吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '提交中...' })
          orderApi.returnOrder(this.data.orderId, '用户申请还衣')
            .then(() => {
              wx.hideLoading()
              wx.showToast({ title: '申请成功', icon: 'success' })
              this.loadOrder()
            })
            .catch(err => {
              wx.hideLoading()
              console.error('申请归还失败', err)
              wx.showToast({ title: '申请归还失败', icon: 'none' })
            })
        }
      }
    })
  },

  onCancelTap() {
    if (!this.data.order) return
    wx.showModal({
      title: '取消订单',
      content: '确认取消此订单吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '提交中...' })
          orderApi.cancelOrder(this.data.orderId)
            .then(() => {
              wx.hideLoading()
              wx.showToast({ title: '取消成功', icon: 'success' })
              this.loadOrder()
            })
            .catch(err => {
              wx.hideLoading()
              console.error('取消失败', err)
              wx.showToast({ title: '取消失败', icon: 'none' })
            })
        }
      }
    })
  }
})