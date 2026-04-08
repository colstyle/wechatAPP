// pages/appointment/appointment.js
const app = getApp()
const appointmentApi = require('../../utils/api').appointmentApi
const productApi = require('../../utils/api').productApi

Page({
  data: {
    productId: null,
    selectedProduct: null,
    dates: [],
    selectedDate: null,
    times: ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00'],
    selectedTime: null,
    availableTimes: [],
    remark: ''
  },

  onLoad(options) {
    if (options.product_id) {
      this.setData({ productId: parseInt(options.product_id) })
      this.loadProduct()
    }
    this.generateDates()
  },

  // 生成日期
  generateDates() {
    const dates = []
    const today = new Date()
    for (let i = 0; i < 14; i++) {
      const date = new Date(today)
      date.setDate(today.getDate() + i)
      const month = String(date.getMonth() + 1) + '月'
      const day = String(date.getDate())
      dates.push({
        date: date,
        day: day,
        month: month,
        value: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
      })
    }
    this.setData({ dates })
  },

  // 加载商品
  loadProduct() {
    productApi.getProduct(this.data.productId)
      .then(res => {
        this.setData({ selectedProduct: res.data })
      })
      .catch(err => {
        console.error('获取商品失败', err)
      })
  },

  // 选择商品
  onProductSelect() {
    wx.navigateTo({
      url: `/pages/product/product?type=recent`
    })
  },

  // 选择日期
  onDateTap(e) {
    const date = e.currentTarget.dataset.date
    this.setData({
      selectedDate: date.value,
      selectedTime: null
    })
    this.loadAvailableTimes(date.value)
  },

  // 加载可用时间
  loadAvailableTimes(date) {
    if (!this.data.productId) return

    appointmentApi.getAvailableTimes(this.data.productId, date)
      .then(res => {
        this.setData({ availableTimes: res.data.available_times })
      })
      .catch(err => {
        console.error('获取可用时间失败', err)
      })
  },

  // 选择时间
  onTimeTap(e) {
    const time = e.currentTarget.dataset.time
    this.setData({ selectedTime: time })
  },

  // 备注输入
  onRemarkInput(e) {
    this.setData({ remark: e.detail.value })
  },

  // 提交预约
  onSubmit() {
    if (!this.data.selectedProduct) {
      wx.showToast({ title: '请选择商品', icon: 'none' })
      return
    }
    if (!this.data.selectedDate) {
      wx.showToast({ title: '请选择日期', icon: 'none' })
      return
    }
    if (!this.data.selectedTime) {
      wx.showToast({ title: '请选择时间', icon: 'none' })
      return
    }

    wx.showModal({
      title: '确认预约',
      content: `确认在${this.data.selectedDate} ${this.data.selectedTime}预约试穿吗？`,
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '提交中...' })

          appointmentApi.createAppointment({
            product_id: this.data.productId,
            appointment_date: this.data.selectedDate,
            appointment_time: this.data.selectedTime,
            remark: this.data.remark
          })
            .then(res => {
              wx.hideLoading()
              wx.showToast({ title: '预约成功', icon: 'success' })
              setTimeout(() => {
                wx.navigateBack()
              }, 1500)
            })
            .catch(err => {
              wx.hideLoading()
              wx.showToast({ title: '预约失败', icon: 'none' })
            })
        }
      }
    })
  }
})
