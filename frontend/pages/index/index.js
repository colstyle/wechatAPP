const app = getApp()
const productApi = require('../../utils/api').productApi

Page({
  data: {
    selectedDate: null,
    startDate: '',
    endDate: '',
    categories: [
      { id: 1, name: '礼服',    iconPath: '/images/category-dress.png',     bgColor: 'rgba(197,160,89,0.10)' },
      { id: 2, name: '常服',    iconPath: '/images/category-casual.png',    bgColor: 'rgba(142,151,117,0.10)' },
      { id: 3, name: '配饰',    iconPath: '/images/category-accessory.png', bgColor: 'rgba(184,150,122,0.10)' },
      { id: 4, name: '鞋包',    iconPath: '/images/category-bag.png',       bgColor: 'rgba(122,143,166,0.10)' },
      { id: 5, name: '3件套餐', iconPath: '/images/category-package.png',   bgColor: 'rgba(197,160,89,0.18)' }
    ],
    products: [],
    page: 1,
    page_size: 10,
    hasMore: true,
    loading: false,
    loadError: false
  },

  onLoad() {
    this.initDateRange()
    this.loadData()
  },

  onShow() {
    this.checkLogin()
  },

  initDateRange() {
    const now = new Date()
    const startDate = app.formatDate(now)
    const future = new Date()
    future.setDate(now.getDate() + 30)
    const endDate = app.formatDate(future)
    const selectedDate = app.globalData.selectedDate || startDate

    this.setData({ startDate, endDate, selectedDate })
    if (!app.globalData.selectedDate) {
      app.globalData.selectedDate = startDate
    }
  },

  onDateChange(e) {
    const date = e.detail.value
    this.setData({ selectedDate: date })
    app.globalData.selectedDate = date
    this.loadData()
  },

  checkLogin() {
    if (!app.globalData.token) {
      app.wechatLogin().catch(() => {})
    }
  },

  loadData() {
    this.setData({ page: 1, hasMore: true, products: [], loadError: false })
    this.loadProducts()
  },

  loadProducts(isLoadMore = false) {
    if (this.data.loading) return
    if (isLoadMore && !this.data.hasMore) return

    this.setData({ loading: true })
    const page = isLoadMore ? this.data.page + 1 : 1

    productApi.getProducts({
      page,
      page_size: this.data.page_size,
      available_date: this.data.selectedDate
    }).then(res => {
      const list = (res.data && res.data.list) ? res.data.list : []
      this.setData({
        products: isLoadMore ? this.data.products.concat(list) : list,
        page,
        hasMore: list.length === this.data.page_size,
        loading: false,
        loadError: false
      })
    }).catch(() => {
      this.setData({ loading: false, loadError: true })
    })
  },

  onCategoryTap(e) {
    const id = e.currentTarget.dataset.id
    if (id === 5) {
      wx.navigateTo({ url: '/pages/package/package' })
      return
    }
    wx.navigateTo({ url: `/pages/category/category?category_id=${id}` })
  },

  onProductTap(e) {
    const id = (e.detail && e.detail.id) || e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` })
  },

  onLoadMore() {
    this.loadProducts(true)
  },

  onPullDownRefresh() {
    this.loadData()
    setTimeout(() => wx.stopPullDownRefresh(), 300)
  }
})
