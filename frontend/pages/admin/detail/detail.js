const app = getApp()
const orderApi = require('../../../utils/api').orderApi
const adminApi = require('../../../utils/api').adminApi
const util = require('../../../utils/util')

Page({
  data: {
    orderId: null,
    order: null,
    loading: false,
    showModal: false,
    modalTitle: '',
    modalAmount: '',
    modalReason: '',
    modalType: '' // 'refund' or 'deduct'
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ orderId: parseInt(options.id) })
      this.loadOrder()
    }
  },

  loadOrder() {
    this.setData({ loading: true })
    orderApi.getOrder(this.data.orderId)
      .then(res => {
        const order = res.data
        order.statusText = util.orderStatusMap[order.status] || '未知'
        this.setData({ order, loading: false })
      })
      .catch(err => {
        this.setData({ loading: false })
        console.error('获取订单详情失败', err)
        wx.showToast({ title: '获取订单详情失败', icon: 'none' })
      })
  },

  onRefund() {
    this.setData({
      showModal: true,
      modalTitle: '一键退押金',
      modalAmount: this.data.order.total_deposit,
      modalReason: '店主确认无误，原路退还押金',
      modalType: 'refund'
    })
  },

  onDeduct() {
    this.setData({
      showModal: true,
      modalTitle: '手动扣除押金',
      modalAmount: '',
      modalReason: '',
      modalType: 'deduct'
    })
  },

  onUpdateItems() {
    wx.showToast({ title: '换款功能开发中...', icon: 'none' })
  },

  closeModal() {
    this.setData({ showModal: false })
  },

  onModalAmountInput(e) {
    this.setData({ modalAmount: e.detail.value })
  },

  onModalReasonInput(e) {
    this.setData({ modalReason: e.detail.value })
  },

  confirmModal() {
    const { orderId, modalType, modalAmount, modalReason } = this.data
    
    if (!modalAmount || isNaN(modalAmount)) {
      wx.showToast({ title: '请输入有效金额', icon: 'none' })
      return
    }

    wx.showLoading({ title: '提交中...' })

    const apiCall = modalType === 'refund' 
      ? adminApi.refundOrder(orderId, parseFloat(modalAmount), modalReason)
      : adminApi.deductDeposit(orderId, parseFloat(modalAmount), modalReason)

    apiCall.then(res => {
      wx.hideLoading()
      if (res.code === 0) {
        wx.showToast({ title: '操作成功', icon: 'success' })
        this.closeModal()
        this.loadOrder()
      } else {
        wx.showToast({ title: res.message || '操作失败', icon: 'none' })
      }
    }).catch(err => {
      wx.hideLoading()
      console.error('操作失败', err)
      wx.showToast({ title: '网络请求失败', icon: 'none' })
    })
  }
})
