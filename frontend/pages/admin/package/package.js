const app = getApp()
const adminApi = require('../../../utils/api').adminApi

Page({
  data: {
    products: [],
    keyword: '',
    eligible: null,
    page: 1,
    page_size: 20,
    hasMore: true,
    loading: false,
    refreshing: false
  },

  onLoad() {
    app.ensureLogin()
      .then(() => {
        const userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo') || {}
        if (!(userInfo.role === 'admin' || userInfo.role === '2' || userInfo.role === 2)) {
          wx.showToast({ title: '无权限访问', icon: 'none' })
          setTimeout(() => {
            wx.switchTab({ url: '/pages/profile/profile' })
          }, 300)
          return
        }
        this.loadProducts()
      })
      .catch(() => {
        wx.showToast({ title: '请先登录', icon: 'none' })
      })
  },

  buildParams(page) {
    const params = { page, page_size: this.data.page_size }
    if (this.data.keyword) params.keyword = this.data.keyword
    if (this.data.eligible !== null) params.eligible = this.data.eligible
    return params
  },

  loadProducts(isLoadMore = false) {
    if (this.data.loading) return
    if (isLoadMore && !this.data.hasMore) return

    const page = isLoadMore ? this.data.page + 1 : 1
    this.setData({ loading: true })

    adminApi.getPackageProducts(this.buildParams(page))
      .then(res => {
        const list = (res.data && res.data.list) ? res.data.list : []
        this.setData({
          products: isLoadMore ? [...this.data.products, ...list] : list,
          page,
          hasMore: list.length === this.data.page_size,
          loading: false,
          refreshing: false
        })
      })
      .catch(() => {
        this.setData({ loading: false, refreshing: false })
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
  },

  onToggle(e) {
    const id = e.currentTarget.dataset.id
    const checked = e.detail.value
    const idx = this.data.products.findIndex(p => p.id === id)
    if (idx < 0) return

    const products = [...this.data.products]
    const prev = products[idx].is_package_eligible
    products[idx].is_package_eligible = checked
    this.setData({ products })

    adminApi.setPackageEligible(id, checked)
      .catch(() => {
        products[idx].is_package_eligible = prev
        this.setData({ products })
        wx.showToast({ title: '更新失败', icon: 'none' })
      })
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearch() {
    this.setData({ page: 1, hasMore: true, products: [] }, () => this.loadProducts())
  },

  clearSearch() {
    this.setData({ keyword: '', page: 1, hasMore: true, products: [] }, () => this.loadProducts())
  },

  setEligibleFilter(e) {
    const val = e.currentTarget.dataset.eligible
    let eligible = null
    if (val === true || val === 'true') eligible = true
    if (val === false || val === 'false') eligible = false
    this.setData({ eligible, page: 1, hasMore: true, products: [] }, () => this.loadProducts())
  },

  onRefresh() {
    this.setData({ refreshing: true, page: 1, hasMore: true }, () => this.loadProducts())
  },

  onLoadMore() {
    this.loadProducts(true)
  }
})
