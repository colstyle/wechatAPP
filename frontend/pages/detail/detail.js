const app = getApp()
const productApi = require('../../utils/api').productApi

Page({
  data: {
    productId: null,
    product: null,
    loading: true,
    selectedSize: '',
    selectedColor: '',
    showModal: false,
    rentalType: 1, // 1: 按天, 2: 单次(3天)
    rentalDays: 3,
    customDays: '',
    calculatedRent: 0,
    calculatedTotal: 0,
    colorMap: {
      '黑色': '#000000',
      '白色': '#ffffff',
      '红色': '#ff4d4f',
      '蓝色': '#1890ff',
      '黄色': '#ffec3d',
      '绿色': '#52c41a',
      '卡其色': '#d4b106',
      '复古蓝': '#003a8c'
    }
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ productId: parseInt(options.id) })
      this.loadProduct()
    }
  },

  // 加载商品详情
  loadProduct() {
    this.setData({ loading: true })
    productApi.getProduct(this.data.productId)
      .then(res => {
        if (res.code === 0) {
          const product = res.data
          // 确保 images 是数组
          if (typeof product.images === 'string') {
            product.images = JSON.parse(product.images)
          }
          // 确保 sizes 和 colors 是数组
          if (typeof product.sizes === 'string') {
            product.sizes = JSON.parse(product.sizes)
          }
          if (typeof product.colors === 'string') {
            product.colors = JSON.parse(product.colors)
          }

          this.setData({
            product,
            loading: false,
            selectedSize: product.sizes ? product.sizes[0] : '',
            selectedColor: product.colors ? product.colors[0] : ''
          })
          this.calculatePrice()
        }
      })
      .catch(err => {
        console.error('获取商品详情失败', err)
        this.setData({ loading: false })
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
  },

  // 选择规格
  selectSize(e) {
    this.setData({ selectedSize: e.currentTarget.dataset.size })
  },

  selectColor(e) {
    this.setData({ selectedColor: e.currentTarget.dataset.color })
  },

  // 租赁弹窗
  showRentalModal() {
    this.setData({ showModal: true })
    this.calculatePrice()
  },

  hideRentalModal() {
    this.setData({ showModal: false })
  },

  selectRentalType(e) {
    this.setData({ 
      rentalType: e.currentTarget.dataset.type,
      rentalDays: e.currentTarget.dataset.type === 2 ? 3 : this.data.rentalDays
    }, this.calculatePrice)
  },

  selectDays(e) {
    const days = e.currentTarget.dataset.days
    this.setData({ rentalDays: days }, this.calculatePrice)
  },

  onDaysInput(e) {
    const days = parseInt(e.detail.value) || 0
    this.setData({ customDays: e.detail.value }, () => {
      if (days > 0) {
        this.calculatePrice()
      }
    })
  },

  // 计算价格
  calculatePrice() {
    if (!this.data.product) return

    let rent = 0
    const { rentalType, rentalDays, customDays, product } = this.data

    if (rentalType === 1) {
      const days = rentalDays === 0 ? (parseInt(customDays) || 1) : rentalDays
      rent = (product.price || product.daily_rent || 0) * days
    } else {
      // 如果没有单次计费字段，默认按3天打8折计算
      rent = product.single_rent || (product.price || product.daily_rent || 0) * 3 * 0.8
    }

    this.setData({
      calculatedRent: rent.toFixed(2),
      calculatedTotal: (rent + (product.deposit || 0)).toFixed(2)
    })
  },

  // 提交订单
  submitOrder() {
    const { product, selectedSize, selectedColor, rentalType, rentalDays, customDays } = this.data
    const days = rentalType === 2 ? 3 : (rentalDays === 0 ? parseInt(customDays) : rentalDays)

    if (rentalType === 1 && !days) {
      wx.showToast({ title: '请输入租赁天数', icon: 'none' })
      return
    }

    const orderData = {
      product_id: product.id,
      name: product.name,
      image: product.main_image || product.cover_image,
      size: selectedSize,
      color: selectedColor,
      rental_type: rentalType,
      rental_days: days,
      rent: parseFloat(this.data.calculatedRent),
      deposit: product.deposit || 0
    }

    // 存储到全局，跳转到确认订单页
    app.globalData.checkoutOrder = {
      rental_type: rentalType,
      items: [orderData],
      total_rent: parseFloat(this.data.calculatedRent),
      total_deposit: product.deposit
    }

    wx.navigateTo({
      url: '/pages/orders/confirm'
    })
  },

  // 图片预览
  previewImage(e) {
    wx.previewImage({
      current: e.currentTarget.dataset.url,
      urls: this.data.product.images
    })
  },

  // 其他跳转
  goToHome() {
    wx.switchTab({ url: '/pages/index/index' })
  },

  contactService() {
    wx.navigateTo({ url: '/pages/chat/chat' })
  },

  goBack() {
    wx.navigateBack({ delta: 1 })
  }
  
})
