// pages/orders/confirm.js
const app = getApp()
const productApi = require('../../utils/api').productApi
const orderApi = require('../../utils/api').orderApi

Page({
  data: {
    productId: null,
    type: 'daily',
    rentDays: 3,
    size: '',
    color: '',
    product: {},
    selectedAddress: null,
    rentalType: 1,
    startDate: '',
    todayDate: '',
    calculatedRent: 0,
    calculatedTotal: 0,
    remark: ''
  },

  onLoad(options) {
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    const todayDate = `${year}-${month}-${day}`

    if (options.product_id) {
      this.setData({ productId: parseInt(options.product_id) })
    }
    if (options.type) {
      const type = options.type
      let rentalType = 1
      if (type === 'daily') {
        rentalType = 1
      } else if (type === 'single') {
        rentalType = 2
      } else if (type === 'subscription') {
        rentalType = 3
      }
      this.setData({ type, rentalType })
    }
    if (options.days) {
      this.setData({ rentDays: parseInt(options.days) })
    }
    if (options.size) {
      this.setData({ size: decodeURIComponent(options.size) })
    }
    if (options.color) {
      this.setData({ color: decodeURIComponent(options.color) })
    }

    this.setData({ startDate: todayDate, todayDate })
    this.loadProduct()
    this.loadDefaultAddress()
  },

  // 加载商品
  loadProduct() {
    productApi.getProduct(this.data.productId)
      .then(res => {
        this.setData({ product: res.data })
        this.calculatePrice()
      })
      .catch(err => {
        console.error('获取商品失败', err)
        wx.showToast({ title: '获取商品失败', icon: 'none' })
      })
  },

  // 加载默认地址
  loadDefaultAddress() {
    const userApi = require('../../utils/api').userApi
    userApi.getAddresses()
      .then(res => {
        const defaultAddress = res.data.find(addr => addr.is_default)
        if (defaultAddress) {
          this.setData({ selectedAddress: defaultAddress })
          this.calculatePrice()
        }
      })
      .catch(err => {
        console.error('获取地址失败', err)
      })
  },

  // 计算价格
  calculatePrice() {
    const product = this.data.product
    let rent = 0

    if (this.data.rentalType === 1) {
      // 按天租赁
      rent = parseFloat(product.daily_rent) * this.data.rentDays
    } else if (this.data.rentalType === 2) {
      // 单次租赁
      rent = parseFloat(product.single_rent)
    } else if (this.data.rentalType === 3) {
      // 订阅租赁
      rent = parseFloat(product.month_card_rent)
    }

    const deposit = parseFloat(product.deposit || 0)
    const total = rent + deposit

    this.setData({
      calculatedRent: rent.toFixed(2),
      calculatedTotal: total.toFixed(2)
    })
  },

  // 选择日期
  onDateChange(e) {
    this.setData({ startDate: e.detail.value })
  },

  // 地址选择
  onAddressTap() {
    wx.navigateTo({
      url: `/pages/address/address?select=1`
    })
  },

  // 备注输入
  onRemarkInput(e) {
    this.setData({ remark: e.detail.value })
  },

  // 提交订单
  onSubmit() {
    if (!this.data.selectedAddress) {
      wx.showToast({ title: '请选择收货地址', icon: 'none' })
      return
    }

    if ([1, 2].includes(this.data.rentalType) && !this.data.startDate) {
      wx.showToast({ title: '请选择使用日期', icon: 'none' })
      return
    }

    wx.showModal({
      title: '确认订单',
      content: '确认提交订单吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '提交中...' })

          const orderData = {
            rental_type: this.data.rentalType,
            items: [{
              product_id: this.data.productId,
              size: this.data.size,
              color: this.data.color,
              quantity: 1
            }],
            address_id: this.data.selectedAddress.id,
            remark: this.data.remark
          }

          if ([1, 2].includes(this.data.rentalType)) {
            orderData.start_date = this.data.startDate
          }
          if (this.data.rentalType === 1) {
            orderData.rent_days = this.data.rentDays
          }

          orderApi.createOrder(orderData)
            .then(res => {
              wx.hideLoading()
              wx.navigateTo({
                url: `/pages/pay/pay?order_id=${res.data.order_id}`
              })
            })
            .catch(err => {
              wx.hideLoading()
              wx.showToast({ title: '创建订单失败', icon: 'none' })
            })
        }
      }
    })
  },

  // 租赁类型文本
  get rentalTypeText() {
    const map = {
      1: '按天租赁',
      2: '单次租赁',
      3: '订阅租赁'
    }
    return map[this.data.rentalType] || '未知'
  }
})
