const app = getApp()
const orderApi = require('../../../utils/api').orderApi
const util = require('../../../utils/util')

Page({
  data: {
    orderId: null,
    order: null,
    loading: false,
    countdown: '',
    timer: null
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ orderId: parseInt(options.id) })
      this.loadOrder()
    }
  },

  onUnload() {
    this.clearTimer()
  },

  clearTimer() {
    if (this.data.timer) {
      clearInterval(this.data.timer)
      this.setData({ timer: null })
    }
  },

  startCountdown() {
    this.clearTimer()
    if (!this.data.order || this.data.order.status !== 2 || !this.data.order.expected_return_time) return

    const expectedTime = new Date(this.data.order.expected_return_time).getTime()
    
    const updateCountdown = () => {
      const now = new Date().getTime()
      const diff = expectedTime - now
      
      if (diff <= 0) {
        this.setData({ countdown: '已到期' })
        this.clearTimer()
        return
      }
      
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diff % (1000 * 60)) / 1000)
      
      this.setData({
        countdown: `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
      })
    }

    updateCountdown()
    const timer = setInterval(updateCountdown, 1000)
    this.setData({ timer })
  },

  loadOrder() {
    this.setData({ loading: true })
    orderApi.getOrder(this.data.orderId)
      .then(res => {
        const order = res.data
        order.statusText = util.orderStatusMap[order.status] || '未知'
        order.rentalTypeText = util.rentalTypeMap[order.rental_type] || '未知'
        this.setData({ order, loading: false })
        if (order.status === 2) {
          this.startCountdown()
        }
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