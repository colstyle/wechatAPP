// pages/detail/detail.js
const app = getApp()
const productApi = require('../../utils/api').productApi
const orderApi = require('../../utils/api').orderApi
const subscriptionApi = require('../../utils/api').subscriptionApi

Page({
  data: {
    productId: 0,
    product: {},
    images: [],
    selectedSize: '',
    selectedColor: '',
    isFavorite: false,
    outfits: [],
    reviews: { list: [], summary: null, total: 0 },
    activeSubscription: null,

    // 租赁弹窗
    showRentModal: false,
    rentalType: 1, // 1按天 2按次 3订阅
    rentDays: 3,
    customDays: '',
    calculatedRent: 0,
    calculatedTotal: 0
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ productId: parseInt(options.id) })
      this.loadProduct()
      this.loadSubscription()
    }
  },

  onShow() {
    this.loadSubscription()
  },

  // 加载商品详情
  loadProduct() {
    productApi.getProduct(this.data.productId)
      .then(res => {
        this.setData({
          product: res.data,
          images: res.data.images
        })
        this.calculatePrice()
      })
      .catch(err => {
        console.error('获取商品详情失败', err)
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
      })
  },

  // 加载订阅信息
  loadSubscription() {
    subscriptionApi.getActiveSubscription()
      .then(res => {
        this.setData({
          activeSubscription: res.data
        })
      })
      .catch(err => {
        console.error('获取订阅信息失败', err)
      })
  },

  // 图片点击预览
  onImageTap(e) {
    const index = e.currentTarget.dataset.index
    wx.previewImage({
      current: this.data.images[index],
      urls: this.data.images
    })
  },

  // 收藏/取消收藏
  onToggleFavorite() {
    if (this.data.isFavorite) {
      productApi.removeFavorite(this.data.productId)
        .then(() => {
          this.setData({ isFavorite: false })
          wx.showToast({ title: '已取消收藏', icon: 'none' })
        })
    } else {
      productApi.addFavorite(this.data.productId)
        .then(() => {
          this.setData({ isFavorite: true })
          wx.showToast({ title: '收藏成功', icon: 'none' })
        })
    }
  },

  // 选择尺码
  onSelectSize(e) {
    this.setData({ selectedSize: e.currentTarget.dataset.size })
  },

  // 选择颜色
  onSelectColor(e) {
    this.setData({ selectedColor: e.currentTarget.dataset.color })
  },

  // 搭配点击
  onOutfitTap(e) {
    const id = e.currentTarget.dataset.id
    // 跳转到搭配详情页或商品列表页
    wx.navigateTo({
      url: `/pages/product/product?outfit_id=${id}`
    })
  },

  // 更多评价
  onMoreReviews() {
    wx.navigateTo({
      url: `/pages/review/review?product_id=${this.data.productId}`
    })
  },

  // 评价图片点击
  onReviewImageTap(e) {
    const images = e.currentTarget.dataset.images
    const index = e.currentTarget.dataset.index
    wx.previewImage({
      current: images[index],
      urls: images
    })
  },

  // 获取评分百分比
  getRatingPercent(star) {
    const summary = this.data.reviews.summary
    if (!summary || summary.total_reviews === 0) return 0
    const key = `rating_${star}`
    const count = summary[key] || 0
    return Math.round((count / summary.total_reviews) * 100)
  },

  // 获取评分数
  getRatingCount(star) {
    const summary = this.data.reviews.summary
    if (!summary) return 0
    const key = `rating_${star}`
    return summary[key] || 0
  },

  // 客服
  onContact() {
    wx.showModal({
      title: '联系客服',
      content: '请拨打客服电话: 400-123-4567',
      showCancel: false
    })
  },

  // 分享
  onShare() {
    wx.showShareMenu()
  },

  // 预约试穿
  onTrial() {
    wx.navigateTo({
      url: `/pages/appointment/appointment?product_id=${this.data.productId}`
    })
  },

  // 订阅下单
  onSubscribe() {
    if (!this.data.activeSubscription) {
      wx.showToast({ title: '请先购买订阅', icon: 'none' })
      return
    }

    wx.navigateTo({
      url: `/pages/orders/confirm?product_id=${this.data.productId}&type=subscription&subscription_id=${this.data.activeSubscription.id}`
    })
  },

  // 立即租用
  onRent() {
    if (!this.data.selectedSize) {
      wx.showToast({ title: '请选择尺码', icon: 'none' })
      return
    }

    this.setData({ showRentModal: true })
    this.calculatePrice()
  },

  // 关闭租赁弹窗
  onCloseRentModal() {
    this.setData({ showRentModal: false })
  },

  // 选择租赁类型
  onSelectRentalType(e) {
    const type = parseInt(e.currentTarget.dataset.type)
    this.setData({ rentalType: type })
    this.calculatePrice()
  },

  // 选择天数
  onSelectDays(e) {
    this.setData({ rentDays: e.currentTarget.dataset.days })
    this.calculatePrice()
  },

  // 自定义天数输入
  onCustomDaysInput(e) {
    this.setData({ customDays: e.detail.value })
  },

  // 计算价格
  calculatePrice() {
    const product = this.data.product
    const rentalType = this.data.rentalType
    let rent = 0

    if (rentalType === 1) {
      // 按天租赁
      const days = this.data.customDays || this.data.rentDays
      rent = parseFloat(product.daily_rent) * parseInt(days)
    } else if (rentalType === 2) {
      // 单次租赁
      rent = parseFloat(product.single_rent)
    } else if (rentalType === 3) {
      // 月卡租赁
      rent = parseFloat(product.month_card_rent)
    }

    const total = rent + parseFloat(product.deposit)

    this.setData({
      calculatedRent: rent.toFixed(2),
      calculatedTotal: total.toFixed(2)
    })
  },

  // 确认租赁
  onConfirmRent() {
    if (!this.data.selectedSize) {
      wx.showToast({ title: '请选择尺码', icon: 'none' })
      return
    }

    const type = this.data.rentalType
    let url = ''

    if (type === 1) {
      // 按天租赁
      const days = this.data.customDays || this.data.rentDays
      url = `/pages/orders/confirm?product_id=${this.data.productId}&type=daily&days=${days}&size=${this.data.selectedSize}&color=${this.data.selectedColor}`
    } else if (type === 2) {
      // 单次租赁
      url = `/pages/orders/confirm?product_id=${this.data.productId}&type=single&size=${this.data.selectedSize}&color=${this.data.selectedColor}`
    } else if (type === 3) {
      // 月卡租赁（跳转到购买订阅页面）
      url = '/pages/subscribe/subscribe'
    }

    this.setData({ showRentModal: false })
    wx.navigateTo({ url })
  }
})
