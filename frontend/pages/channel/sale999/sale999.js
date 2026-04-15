// pages/channel/sale999/sale999.js
// 9.9特惠/微瑕 频道页

const app = getApp()
const productApi = require('../../../utils/api').productApi

Page({
  data: {
    title: '9.9特惠/微瑕',
    emoji: '🔥',
    accentColor: '#E85D5D',
    desc: '超值特惠，微瑕不影响美丽\n低价好物，等你来挑！',
    products: [],
    loading: true,
    hasMore: true,
    page: 1,
    page_size: 20
  },

  onLoad() {
    this.loadProducts()
  },

  loadProducts(isMore = false) {
    if (this.data.loading && isMore) return
    this.setData({ loading: true })
    const page = isMore ? this.data.page + 1 : 1
    productApi.getProducts({
      page,
      page_size: this.data.page_size,
      keyword: '特惠'
    }).then(res => {
      const list = (res.data && res.data.list) ? res.data.list : []
      this.setData({
        products: isMore ? this.data.products.concat(list) : list,
        page,
        hasMore: list.length >= this.data.page_size,
        loading: false
      })
    }).catch(() => {
      this.setData({ loading: false })
    })
  },

  onProductTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` })
  },

  onReachBottom() {
    if (this.data.hasMore) this.loadProducts(true)
  },

  onPullDownRefresh() {
    this.setData({ page: 1, hasMore: true, products: [] })
    this.loadProducts()
    setTimeout(() => wx.stopPullDownRefresh(), 800)
  }
})
