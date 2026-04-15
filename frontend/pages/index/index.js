const app = getApp()
const productApi = require('../../utils/api').productApi

Page({
  data: {
    selectedDate: null,
    startDate: '',
    endDate: '',
    products: [],
    page: 1,
    page_size: 10,
    hasMore: true,
    loading: false,
    loadError: false,
    imgBase: app.imgBase
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

  goToCategory() {
    wx.navigateTo({ url: '/pages/category_db/category_db' })
  },

  goToPackage() {
    wx.navigateTo({ url: '/pages/package/package' })
  },

  onStoreServiceTap() {
    wx.openLocation({
      latitude: 36.09689,
      longitude: 120.37053,
      name: '小时光租衣舍',
      address: '青岛市市北区青建太阳岛',
      scale: 18
    })
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
  },

  onResetDate() {
    this.setData({
      selectedDate: this.data.todayDate
    }, () => {
      this.loadData()
    })
  }
})
