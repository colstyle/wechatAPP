// pages/category/category.js
const productApi = require('../../utils/api').productApi

Page({
  data: {
    categories: [],
    activeCategoryId: '',
    products: [],
    keyword: '',
    isSearching: false,
    isAdmin: false
  },

  onLoad() {
    const auth = require('../../utils/auth')
    this.setData({ isAdmin: auth.hasRole('admin') })
    this.loadCategories()
  },

  onShow() {
    // 每次页面展示时重新检测管理员身份（登录切换后生效）
    const app = getApp()
    const userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo') || {}
    const isAdmin = userInfo.role === 'admin' || userInfo.role === '2' || userInfo.role === 2
    this.setData({ isAdmin })
    if (this.data.isSearching) {
      this.clearSearch()
    }
  },

  loadCategories() {
    productApi.getCategories().then(res => {
      const categories = res.data || []
      this.setData({ categories })
      if (categories.length > 0) {
        this.setData({ activeCategoryId: categories[0].id })
        this.loadProducts(categories[0].id)
      }
    }).catch(err => console.error(err))
  },

  loadProducts(categoryId) {
    wx.showLoading({ title: '加载中' })
    productApi.getProducts({ category_id: categoryId, page_size: 100 }).then(res => {
      wx.hideLoading()
      this.setData({
        products: res.data.list || [],
        isSearching: false
      })
    }).catch(() => wx.hideLoading())
  },

  onGroupTap(e) {
    const cid = e.currentTarget.dataset.id
    if (this.data.activeCategoryId === cid) return
    this.setData({
      activeCategoryId: cid,
      keyword: '',
      isSearching: false
    })
    this.loadProducts(cid)
  },

  onProductTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` })
  },

  onSearchInput(e) {
    const keyword = e.detail.value.trim()
    this.setData({ keyword })
    if (!keyword) {
      this.setData({ isSearching: false })
      if (this.data.activeCategoryId) {
        this.loadProducts(this.data.activeCategoryId)
      }
    }
  },

  onSearchConfirm(e) {
    const keyword = (e.detail.value || '').trim()
    if (!keyword) return
    wx.showLoading({ title: '搜索中' })
    productApi.getProducts({ keyword, page_size: 100 }).then(res => {
      wx.hideLoading()
      this.setData({
        products: res.data.list || [],
        isSearching: true,
        activeCategoryId: ''
      })
    }).catch(() => wx.hideLoading())
  },

  clearSearch() {
    this.setData({ keyword: '', isSearching: false })
    if (this.data.categories.length > 0) {
      const firstCat = this.data.categories[0].id
      this.setData({ activeCategoryId: firstCat })
      this.loadProducts(firstCat)
    }
  },

  goToInventory() {
    wx.navigateTo({ url: '/pages/admin/catalog/inventory/inventory' })
  },

  goToPackage() {
    wx.navigateTo({ url: '/pages/admin/package/package' })
  }
})
