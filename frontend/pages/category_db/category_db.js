const productApi = require('../../utils/api').productApi

Page({
  data: {
    parents: [],
    activeId: 0,
    activeName: '',
    children: [],
    loading: false
  },

  onLoad() {
    this.loadParents()
  },

  loadParents() {
    this.setData({ loading: true })
    productApi.getCategories(0)
      .then(res => {
        const list = (res && res.code === 0 && res.data) ? res.data : []
        const first = list[0] || {}
        this.setData({
          parents: list,
          activeId: first.id || 0,
          activeName: first.name || '',
          loading: false
        }, () => {
          if (first.id) this.loadChildren(first.id)
        })
      })
      .catch(err => {
        console.error(err)
        this.setData({ loading: false })
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
  },

  loadChildren(parentId) {
    this.setData({ loading: true, children: [] })
    productApi.getCategories(parentId)
      .then(res => {
        const list = (res && res.code === 0 && res.data) ? res.data : []
        this.setData({ children: list, loading: false })
      })
      .catch(err => {
        console.error(err)
        this.setData({ loading: false })
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
  },

  onParentTap(e) {
    const id = e.currentTarget.dataset.id
    const parent = this.data.parents.find(p => p.id === id) || {}
    this.setData({ activeId: id, activeName: parent.name || '' }, () => this.loadChildren(id))
  },

  goToProducts(e) {
    const id = e.currentTarget.dataset.id
    const name = e.currentTarget.dataset.name || ''
    wx.navigateTo({ url: `/pages/category_products/list/list?category_id=${id}&category_name=${encodeURIComponent(name)}` })
  }
})
