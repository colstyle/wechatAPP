// pages/admin/catalog/catalog.js
const { adminApi } = require('../../../utils/api')

Page({
  data: {
    categories: []
  },

  onShow() {
    this.loadCategories()
  },

  loadCategories() {
    adminApi.getCategories().then(res => {
      if (res.code === 0) {
        this.setData({ categories: res.data || [] })
      }
    }).catch(err => console.error(err))
  },

  goToInventory() {
    wx.navigateTo({ url: '/pages/admin/catalog/inventory/inventory' })
  },

  goToPackage() {
    wx.navigateTo({ url: '/pages/admin/package/package' })
  }
})
