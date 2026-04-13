// pages/admin/inventory/list/list.js
const app = getApp()
const { productApi, adminApi } = require('../../../../utils/api')

Page({
  data: {
    products: [],
    keyword: '',
    page: 1,
    page_size: 20,
    hasMore: true,
    loading: false,
    refreshing: false
  },

  onShow() {
    this.setData({ page: 1, hasMore: true, products: [] }, () => {
      this.loadProducts()
    })
  },

  loadProducts(isLoadMore = false) {
    if (this.data.loading) return
    
    this.setData({ loading: true })
    const { keyword, page, page_size } = this.data
    const currentPage = isLoadMore ? page + 1 : 1

    const params = {
      page: currentPage,
      page_size
    }
    if (keyword) params.keyword = keyword

    productApi.getProducts(params).then(res => {
      if (res.code === 0) {
        const list = res.data.list
        this.setData({
          products: isLoadMore ? [...this.data.products, ...list] : list,
          page: currentPage,
          hasMore: list.length === page_size,
          loading: false,
          refreshing: false
        })
      }
    }).catch(err => {
      console.error('加载商品失败', err)
      this.setData({ loading: false, refreshing: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    })
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearch() {
    this.setData({ products: [], page: 1, hasMore: true }, () => {
      this.loadProducts()
    })
  },

  onRefresh() {
    this.setData({ refreshing: true, page: 1, hasMore: true }, () => {
      this.loadProducts()
    })
  },

  onLoadMore() {
    if (this.data.hasMore) {
      this.loadProducts(true)
    }
  },

  goToAdd() {
    wx.navigateTo({ url: '/pages/admin/inventory/edit/edit' })
  },

  goToEdit(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/admin/inventory/edit/edit?id=${id}` })
  },

  onDelete(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '操作确认',
      content: '确定要删除或下架该商品吗？若有关联订单，将被自动处理为下架。',
      confirmColor: '#D32F2F',
      success: (res) => {
        if (res.confirm) {
          adminApi.deleteProduct(id).then(res => {
            if (res.code === 0) {
              wx.showToast({ title: res.message, icon: 'none', duration: 2500 })
              this.onSearch() // 刷新列表
            }
          })
        }
      }
    })
  }
})