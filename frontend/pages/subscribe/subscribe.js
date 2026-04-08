// pages/subscribe/subscribe.js
const app = getApp()
const subscriptionApi = require('../../utils/api').subscriptionApi

Page({
  data: {
    packages: [],
    activeSubscription: null,
    selectedPackage: null
  },

  onLoad() {
    this.loadPackages()
    this.loadActiveSubscription()
  },

  onShow() {
    this.loadActiveSubscription()
  },

  // 加载订阅套餐
  loadPackages() {
    subscriptionApi.getPackages()
      .then(res => {
        this.setData({ packages: res.data })
      })
      .catch(err => {
        console.error('获取套餐失败', err)
      })
  },

  // 加载当前订阅
  loadActiveSubscription() {
    subscriptionApi.getActiveSubscription()
      .then(res => {
        if (res.data) {
          this.setData({
            activeSubscription: res.data
          })
        }
      })
      .catch(err => {
        console.error('获取订阅失败', err)
      })
  },

  // 选择套餐
  onPackageTap(e) {
    const id = e.currentTarget.dataset.id
    this.setData({ selectedPackage: id })
  },

  // 获取套餐价格
  getPackagePrice() {
    if (!this.data.selectedPackage) return '0'
    const pkg = this.data.packages.find(p => p.id === this.data.selectedPackage)
    return pkg ? pkg.price : '0'
  },

  // 订阅
  onSubscribe() {
    if (!this.data.selectedPackage) {
      wx.showToast({ title: '请选择订阅套餐', icon: 'none' })
      return
    }

    wx.showModal({
      title: '确认订阅',
      content: `确定要订阅这个套餐吗？`,
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '处理中...' })

          subscriptionApi.buySubscription(this.data.selectedPackage)
            .then(res => {
              wx.hideLoading()
              wx.showToast({ title: '订阅成功', icon: 'success' })
              this.loadActiveSubscription()
              this.setData({ selectedPackage: null })
            })
            .catch(err => {
              wx.hideLoading()
              wx.showToast({ title: '订阅失败', icon: 'none' })
            })
        }
      }
    })
  }
})
