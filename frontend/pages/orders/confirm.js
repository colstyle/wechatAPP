// pages/orders/confirm.js
const app = getApp()
const productApi = require('../../utils/api').productApi
const orderApi = require('../../utils/api').orderApi

Page({
  data: {
    rentalType: 1,
    startDate: '',
    todayDate: '',
    rentDays: 1,
    items: [],
    displayItems: [],
    calculatedRent: '0.00',
    calculatedDeposit: '0.00',
    calculatedTotal: '0.00',
    remark: ''
  },

  onLoad(options) {
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    const todayDate = `${year}-${month}-${day}`

    const checkoutOrder = app.globalData.checkoutOrder || null
    const startDate = (checkoutOrder && checkoutOrder.start_date) ? checkoutOrder.start_date : (app.globalData.selectedDate || todayDate)

    if (checkoutOrder && Array.isArray(checkoutOrder.items) && checkoutOrder.items.length > 0) {
      const items = checkoutOrder.items.map(it => ({
        product_id: it.product_id,
        size: it.size || '',
        color: it.color || '',
        quantity: it.quantity || 1
      }))
      const rentDays = checkoutOrder.items[0].rental_days || this.data.rentDays

      this.setData({
        rentalType: checkoutOrder.rental_type || 1,
        startDate,
        todayDate,
        rentDays,
        items
      })
    } else if (options.product_id) {
      const rentalType = options.type === 'single' ? 2 : 1
      const rentDays = options.days ? parseInt(options.days) : 1
      const size = options.size ? decodeURIComponent(options.size) : ''
      const color = options.color ? decodeURIComponent(options.color) : ''
      this.setData({
        rentalType,
        startDate,
        todayDate,
        rentDays,
        items: [{
          product_id: parseInt(options.product_id),
          size,
          color,
          quantity: 1
        }]
      })
    } else {
      wx.showToast({ title: '订单信息缺失', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 300)
      return
    }

    this.loadProductsForItems()
  },

  loadProductsForItems() {
    const items = this.data.items || []
    if (!items.length) return

    const tasks = items.map(it => productApi.getProduct(it.product_id))
    Promise.all(tasks)
      .then(results => {
        const products = results.map(r => r.data)
        const displayItems = items.map((it, idx) => ({
          product: products[idx],
          size: it.size,
          color: it.color,
          quantity: it.quantity
        }))
        this.setData({ displayItems })
        if (this.data.rentalType === 5) {
          const invalid = (displayItems || []).find(it => !(it.product && it.product.is_package_eligible))
          if (invalid && invalid.product) {
            wx.showToast({ title: '包含非套餐衣物', icon: 'none' })
            setTimeout(() => wx.navigateBack(), 300)
            return
          }
        }
        this.calculatePrice()
      })
      .catch(err => {
        console.error('获取商品失败', err)
        wx.showToast({ title: '获取商品失败', icon: 'none' })
      })
  },

  // 计算价格
  calculatePrice() {
    const displayItems = this.data.displayItems || []
    if (!displayItems.length) return

    const rentalType = this.data.rentalType
    const first = displayItems[0].product || {}

    let rent = 0
    if (rentalType === 5) {
      rent = 69.90
    } else if (rentalType === 1) {
      rent = parseFloat(first.price || first.daily_rent || 0) * (this.data.rentDays || 1)
    } else if (rentalType === 2) {
      rent = parseFloat(first.single_rent || (parseFloat(first.price || first.daily_rent || 0) * 3 * 0.8))
    } else if (rentalType === 3) {
      rent = parseFloat(first.month_card_rent || 0)
    }

    const deposit = displayItems.reduce((sum, it) => {
      return sum + parseFloat((it.product && it.product.deposit) || 0) * (it.quantity || 1)
    }, 0)

    const total = rent + deposit

    this.setData({
      calculatedRent: rent.toFixed(2),
      calculatedDeposit: deposit.toFixed(2),
      calculatedTotal: total.toFixed(2)
    })
  },

  // 选择日期
  onDateChange(e) {
    this.setData({ startDate: e.detail.value })
  },

  // 备注输入
  onRemarkInput(e) {
    this.setData({ remark: e.detail.value })
  },

  // 提交订单
  onSubmit() {
    if ([1, 2, 5].includes(this.data.rentalType) && !this.data.startDate) {
      wx.showToast({ title: '请选择使用日期', icon: 'none' })
      return
    }
    if (this.data.rentalType === 5 && (!this.data.items || this.data.items.length !== 3)) {
      wx.showToast({ title: '套餐需选满3件', icon: 'none' })
      return
    }

    wx.showModal({
      title: '确认订单',
      content: '确认提交订单吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '提交中...' })
          const done = () => {
            try { wx.hideLoading() } catch (e) {}
          }

          const orderData = {
            rental_type: this.data.rentalType,
            items: (this.data.items || []).map(it => ({
              product_id: it.product_id,
              size: it.size,
              color: it.color,
              quantity: it.quantity || 1
            })),
            remark: this.data.remark
          }

          if ([1, 2, 5].includes(this.data.rentalType)) {
            orderData.start_date = this.data.startDate
          }
          if (this.data.rentalType === 1) {
            orderData.rent_days = this.data.rentDays
          }

          orderApi.createOrder(orderData)
            .then(res => {
              done()
              wx.navigateTo({
                url: `/pages/pay/pay?order_id=${res.data.order_id}`
              })
            })
            .catch(err => {
              done()
              wx.showToast({ title: (err && err.message) ? err.message : '创建订单失败', icon: 'none' })
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
      3: '订阅租赁',
      5: '3件69.9套餐'
    }
    return map[this.data.rentalType] || '未知'
  }
})
