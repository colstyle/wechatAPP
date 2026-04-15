// pages/channel/activity599/activity599.js
const app = getApp()
const productApi = require('../../../utils/api').productApi

Page({
  data: {
    title: '活动59.9二件',
    emoji: '🎉',
    accentColor: '#E87B3A',
    desc: '',
    products: [],
    loading: true,
    hasMore: true,
    page: 1,
    page_size: 20
  },

  onLoad() { this.loadProducts() },

  loadProducts(isMore = false) {
    if (this.data.loading && isMore) return
    this.setData({ loading: true })
    const page = isMore ? this.data.page + 1 : 1
    productApi.getProducts({ page, page_size: this.data.page_size, keyword: '活动' })
      .then(res => {
        const list = (res.data && res.data.list) ? res.data.list : []
        this.setData({
          products: isMore ? this.data.products.concat(list) : list,
          page, hasMore: list.length >= this.data.page_size, loading: false
        })
      }).catch(() => this.setData({ loading: false }))
  },

  onProductTap(e) {
    wx.navigateTo({ url: '/pages/detail/detail?id=' + e.currentTarget.dataset.id })
  },

  onReachBottom() { if (this.data.hasMore) this.loadProducts(true) },

  onPullDownRefresh() {
    this.setData({ page: 1, hasMore: true, products: [] })
    this.loadProducts()
    setTimeout(() => wx.stopPullDownRefresh(), 800)
  }
})
