// pages/review/review.js
const app = getApp()
const productApi = require('../../utils/api').productApi
const reviewApi = require('../../utils/api').reviewApi
const util = require('../../utils/util.js')

Page({
  data: {
    type: 'product',
    productId: null,
    orderId: null,
    product: null,
    reviews: [],
    rating: 0,
    content: '',
    images: [],
    isAnonymous: false,
    loading: false,
    page: 1,
    page_size: 20,
    hasMore: true
  },

  onLoad(options) {
    if (options.type) {
      this.setData({ type: options.type })
    }
    if (options.product_id) {
      this.setData({ productId: parseInt(options.product_id) })
      this.loadProduct()
    }
    if (options.order_id) {
      this.setData({ orderId: parseInt(options.order_id) })
    }

    if (this.data.type === 'my') {
      this.loadMyReviews()
    }
  },

  loadProduct() {
    productApi.getProduct(this.data.productId)
      .then(res => {
        this.setData({ product: res.data })
      })
      .catch(err => {
        console.error('获取商品失败', err)
      })
  },

  loadMyReviews() {
    if (this.data.loading || !this.data.hasMore) return

    this.setData({ loading: true })

    reviewApi.getMyReviews(this.data.page, this.data.page_size)
      .then(res => {
        const reviewsWithStars = res.data.list.map(item => ({
          ...item,
          ratingStars: util.getStarsString(item.rating)
        }))

        const newReviews = this.data.page === 1 ? reviewsWithStars : [...this.data.reviews, ...reviewsWithStars]

        const hasMore = res.data.list.length >= this.data.page_size

        this.setData({
          reviews: newReviews,
          hasMore: hasMore,
          loading: false
        })
      })
      .catch(err => {
        console.error('获取评价失败', err)
        this.setData({ loading: false })
      })
  },

  onRatingTap(e) {
    const rating = e.currentTarget.dataset.rating
    this.setData({ rating })
  },

  onContentInput(e) {
    this.setData({ content: e.detail.value })
  },

  onImageUpload(e) {
    const index = e.currentTarget.dataset.index
    if (this.data.images[index]) return

    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]
        const newImages = [...this.data.images]
        newImages[index] = tempFilePath
        this.setData({ images: newImages })
      }
    })
  },

  onRemoveImage(e) {
    const index = e.currentTarget.dataset.index
    const newImages = [...this.data.images]
    newImages[index] = ''
    this.setData({ images: newImages })
  },

  onAnonymousTap() {
    this.setData({ isAnonymous: !this.data.isAnonymous })
  },

  onSubmit() {
    if (!this.data.rating) {
      wx.showToast({ title: '请选择评分', icon: 'none' })
      return
    }
    if (!this.data.content.trim()) {
      wx.showToast({ title: '请输入评价内容', icon: 'none' })
      return
    }

    const reviewData = {
      product_id: this.data.productId,
      rating: this.data.rating,
      content: this.data.content,
      images: this.data.images.filter(img => img),
      is_anonymous: this.data.isAnonymous
    }

    if (this.data.orderId) {
      reviewData.order_id = this.data.orderId
    }

    wx.showLoading({ title: '提交中...' })

    reviewApi.createReview(reviewData)
      .then(res => {
        wx.hideLoading()
        wx.showToast({ title: '评价成功', icon: 'success' })
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      })
      .catch(err => {
        wx.hideLoading()
        wx.showToast({ title: '评价失败', icon: 'none' })
      })
  },

  onReviewTap(e) {
    const id = e.currentTarget.dataset.id
  },

  onImageTap(e) {
    const images = e.currentTarget.dataset.images
    const index = e.currentTarget.dataset.index
    wx.previewImage({
      current: images[index],
      urls: images
    })
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading && this.data.type === 'my') {
      this.setData({ page: this.data.page + 1 })
      this.loadMyReviews()
    }
  }
})
