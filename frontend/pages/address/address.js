// pages/address/address.js
const app = getApp()
const userApi = require('../../utils/api').userApi

Page({
  data: {
    addresses: [],
    loading: false
  },

  onLoad() {
    this.loadAddresses()
  },

  onShow() {
    this.loadAddresses()
  },

  // 加载地址列表
  loadAddresses() {
    this.setData({ loading: true })

    userApi.getAddresses()
      .then(res => {
        this.setData({
          addresses: res.data,
          loading: false
        })
      })
      .catch(err => {
        console.error('获取地址失败', err)
        this.setData({ loading: false })
      })
  },

  // 地址详情
  onAddressTap(e) {
    const id = e.currentTarget.dataset.id
    // 可选：显示详情弹窗
  },

  // 设为默认
  onSetDefault(e) {
    const id = e.currentTarget.dataset.id
    userApi.setDefaultAddress(id)
      .then(() => {
        wx.showToast({ title: '设置成功', icon: 'success' })
        this.loadAddresses()
      })
      .catch(err => {
        console.error('设置失败', err)
      })
  },

  // 编辑地址
  onEdit(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/address/edit?id=${id}`
    })
  },

  // 删除地址
  onDelete(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '删除地址',
      content: '确定要删除这个地址吗？',
      success: (res) => {
        if (res.confirm) {
          userApi.deleteAddress(id)
            .then(() => {
              wx.showToast({ title: '删除成功', icon: 'success' })
              this.loadAddresses()
            })
            .catch(err => {
              console.error('删除失败', err)
            })
        }
      }
    })
  },

  // 添加地址
  onAdd() {
    wx.navigateTo({
      url: '/pages/address/edit'
    })
  }
})
