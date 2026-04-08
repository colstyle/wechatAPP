// pages/orders/orders.js
const app = getApp()
const orderApi = require('../../utils/api').orderApi
const util = require('../../utils/util')

Page({
  data: {
    status: null,
    title: '我的订单',
    orders: [],
    loading: false,
    page: 1,
    page_size: 20,
    hasMore: true
  },

  onLoad(options) {
    if (options.status) {
      this.setData({
        status: parseInt(options.status),
        title: options.title || '我的订单'
      })
    }
    wx.setNavigationBarTitle({
      title: this.data.title
    })
  },

  onShow() {
    if (app.globalData.token) {
      this.loadOrders()
    }
  },

  // 加载订单列表
  loadOrders() {
    if (this.data.loading || !this.data.hasMore) return

    this.setData({ loading: true })

    const params = {
      page: this.data.page,
      page_size: this.data.page_size
    }

    if (this.data.status !== null) {
      params.status = this.data.status
    }

    orderApi.getOrders(params)
      .then(res => {
        const fetchedOrders = res.data.list.map(item => ({
          ...item,
          statusText: util.orderStatusMap[item.status] || '未知'
        }))
        const newOrders = this.data.page === 1 ? fetchedOrders : [...this.data.orders, ...fetchedOrders]
        const hasMore = res.data.list.length >= this.data.page_size

        this.setData({
          orders: newOrders,
          hasMore: hasMore,
          loading: false
        })
      })
      .catch(err => {
        console.error('获取订单失败', err)
        this.setData({ loading: false })
      })
  },

  // 订单详情
  onOrderTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/order/detail/detail?id=${id}`
    })
  },

  // 支付订单
  onPayTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/pay/pay?order_id=${id}`
    })
  },

  // 确认收货
  onReceiveTap(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认收货',
      content: '确认已收到商品吗？',
      success: (res) => {
        if (res.confirm) {
          orderApi.receiveOrder(id)
            .then(() => {
              wx.showToast({ title: '确认成功', icon: 'success' })
              this.refreshOrders()
            })
            .catch(err => {
              console.error('确认收货失败', err)
            })
        }
      }
    })
  },

  // 申请归还
  onReturnTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/orders/return?order_id=${id}`
    })
  },

  // 取消订单
  onCancelTap(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '取消订单',
      content: '确定要取消这个订单吗？',
      success: (res) => {
        if (res.confirm) {
          orderApi.cancelOrder(id)
            .then(() => {
              wx.showToast({ title: '取消成功', icon: 'success' })
              this.refreshOrders()
            })
            .catch(err => {
              console.error('取消订单失败', err)
            })
        }
      }
    })
  },

  // 刷新订单
  refreshOrders() {
    this.setData({
      page: 1,
      hasMore: true,
      orders: []
    })
    this.loadOrders()
  },

  // 加载更多
  onLoadMore() {
    if (!this.data.hasMore || this.data.loading) return

    this.setData({
      page: this.data.page + 1
    })
    this.loadOrders()
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.setData({
      page: 1,
      hasMore: true,
      orders: []
    })
    this.loadOrders()
    setTimeout(() => {
      wx.stopPullDownRefresh()
    }, 1000)
  }
})
