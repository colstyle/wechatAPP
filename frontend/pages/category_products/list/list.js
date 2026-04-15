const app = getApp()
const productApi = require('../../../utils/api').productApi

Page({
  data: {
    title: '分类商品',
    categoryId: 0,
    selectedDate: '',
    products: [],
    page: 1,
    page_size: 10,
    hasMore: true,
    loading: false
  },

  onLoad(options) {
    const categoryId = parseInt(options.category_id || '0', 10) || 0
    const title = options.category_name ? decodeURIComponent(options.category_name) : '分类商品'
    const selectedDate = app.globalData.selectedDate || ''
    this.setData({ categoryId, title, selectedDate }, () => this.loadData())
  },

  loadData() {
    this.setData({ page: 1, hasMore: true, products: [] }, () => this.loadProducts(false))
  },

  loadProducts(isLoadMore) {
    if (this.data.loading) return
    if (isLoadMore && !this.data.hasMore) return
    const page = isLoadMore ? this.data.page + 1 : 1
    this.setData({ loading: true })
    productApi.getProducts({
      page,
      page_size: this.data.page_size,
      category_id: this.data.categoryId,
      available_date: this.data.selectedDate || undefined
    }).then(res => {
      const list = (res && res.code === 0 && res.data && res.data.list) ? res.data.list : []
      this.setData({
        products: isLoadMore ? this.data.products.concat(list) : list,
        page,
        hasMore: list.length === this.data.page_size,
        loading: false
      })
    }).catch(err => {
      console.error(err)
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    })
  },

  onLoadMore() {
    this.loadProducts(true)
  },

  onProductTap(e) {
    const id = (e.detail && e.detail.id) || e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` })
  },

  pickDate() {
    wx.navigateTo({ url: '/pages/index/index' })
  }
})
