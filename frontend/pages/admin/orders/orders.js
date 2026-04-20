const app = getApp()
const adminApi = require('../../../utils/api').adminApi

Page({
  data: {
    orders: [],
    currentStatus: null,
    keyword: '',
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
        this.loadOrders()
      })
      .catch(() => {
        wx.showToast({ title: '请先登录', icon: 'none' })
        setTimeout(() => {
          wx.switchTab({ url: '/pages/profile/profile' })
        }, 300)
      })
  },

  // 加载订单列表
  loadOrders(isLoadMore = false) {
    if (this.data.loading) return
    
    this.setData({ loading: true })
    const { currentStatus, keyword, page, page_size } = this.data
    const currentPage = isLoadMore ? page + 1 : 1

    const params = {
      page: currentPage,
      page_size
    }
    if (currentStatus !== null) params.status = currentStatus
    if (keyword) params.keyword = keyword

    adminApi.getOrders(params).then(res => {
      if (res.code === 0) {
        const list = res.data.list
        this.setData({
          orders: isLoadMore ? [...this.data.orders, ...list] : list,
          page: currentPage,
          hasMore: list.length === page_size,
          loading: false,
          refreshing: false
        })
      }
    }).catch(err => {
      console.error('加载订单失败', err)
      this.setData({ loading: false, refreshing: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    })
  },

  // 状态切换
  onStatusChange(e) {
    const status = e.currentTarget.dataset.status
    this.setData({
      currentStatus: status,
      orders: [],
      page: 1,
      hasMore: true
    }, () => {
      this.loadOrders()
    })
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  // 执行搜索
  onSearch() {
    this.setData({
      orders: [],
      page: 1,
      hasMore: true
    }, () => {
      this.loadOrders()
    })
  },

  // 清除搜索
  clearSearch() {
    this.setData({
      keyword: '',
      orders: [],
      page: 1,
      hasMore: true
    }, () => {
      this.loadOrders()
    })
  },

  // 下拉刷新
  onRefresh() {
    this.setData({
      refreshing: true,
      page: 1,
      hasMore: true
    }, () => {
      this.loadOrders()
    })
  },

  // 触底加载更多
  onLoadMore() {
    if (this.data.hasMore) {
      this.loadOrders(true)
    }
  },

  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/admin/detail/detail?id=${id}`
    })
  },

  goToCatalog() {
    wx.navigateTo({ url: '/pages/admin/catalog/catalog' })
  },

  goToInventoryManage() {
    wx.navigateTo({ url: '/pages/admin/inventory/list/list' })
  },

})
