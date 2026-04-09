const app = getApp()
const productApi = require('../../utils/api').productApi

Page({
  data: {
    selectedDate: null,
    startDate: '',
    endDate: '',
    categories: [
      { id: 1, name: '礼服', emoji: '👗', gradient: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)' },
      { id: 2, name: '常服', emoji: '👕', gradient: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)' },
      { id: 3, name: '配饰', emoji: '💎', gradient: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)' },
      { id: 4, name: '鞋包', emoji: '👜', gradient: 'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)' },
      { id: 5, name: '3件套餐', emoji: '🎁', gradient: 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)' }
    ],
    products: [],
    page: 1,
    page_size: 10,
    hasMore: true,
    loading: false
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
    this.setData({ page: 1, hasMore: true, products: [] })
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
        loading: false
      })
    }).catch(() => {
      this.setData({ loading: false })
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
    const id = e.currentTarget.dataset.id
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
