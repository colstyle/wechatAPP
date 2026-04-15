const app = getApp()
const auth = require('../../utils/auth')
const storeApi = require('../../utils/api').storeApi

function makeId(prefix) {
  const s = String(Date.now()) + String(Math.floor(Math.random() * 10000))
  return `${prefix}_${s}`
}

Page({
  data: {
    groups: [],
    saving: false
  },

  onLoad() {
    app.ensureLogin()
      .then(() => {
        if (!auth.hasRole('admin')) {
          wx.showToast({ title: '无权限访问', icon: 'none' })
          setTimeout(() => wx.switchTab({ url: '/pages/profile/profile' }), 300)
          return
        }
        this.load()
      })
      .catch(() => {
        wx.showToast({ title: '请先登录', icon: 'none' })
        setTimeout(() => wx.switchTab({ url: '/pages/profile/profile' }), 300)
      })
  },

  load() {
    storeApi.adminGetExploreConfig()
      .then(res => {
        const groups = (res && res.code === 0 && Array.isArray(res.data)) ? res.data : []
        this.setData({ groups })
      })
      .catch(() => {})
  },

  addGroup() {
    const groups = this.data.groups.slice()
    groups.push({ id: makeId('g'), name: '新分组', emoji: '📌', items: [] })
    this.setData({ groups })
  },

  editGroup(e) {
    const idx = Number(e.currentTarget.dataset.index)
    const g = (this.data.groups[idx] || {})
    wx.showModal({
      title: '编辑分组名称',
      editable: true,
      placeholderText: '分组名称',
      content: g.name || '',
      success: (res) => {
        if (!res.confirm) return
        const name = (res.content || '').trim()
        if (!name) return
        const groups = this.data.groups.slice()
        groups[idx] = { ...groups[idx], name }
        this.setData({ groups })
      }
    })
  },

  deleteGroup(e) {
    const idx = Number(e.currentTarget.dataset.index)
    wx.showModal({
      title: '确认删除分组',
      content: '删除后不可恢复，确定继续？',
      success: (res) => {
        if (!res.confirm) return
        const groups = this.data.groups.slice()
        groups.splice(idx, 1)
        this.setData({ groups })
      }
    })
  },

  moveGroupUp(e) {
    const idx = Number(e.currentTarget.dataset.index)
    if (idx <= 0) return
    const groups = this.data.groups.slice()
    const tmp = groups[idx - 1]
    groups[idx - 1] = groups[idx]
    groups[idx] = tmp
    this.setData({ groups })
  },

  moveGroupDown(e) {
    const idx = Number(e.currentTarget.dataset.index)
    const groups = this.data.groups.slice()
    if (idx >= groups.length - 1) return
    const tmp = groups[idx + 1]
    groups[idx + 1] = groups[idx]
    groups[idx] = tmp
    this.setData({ groups })
  },

  addItem(e) {
    const gIndex = Number(e.currentTarget.dataset.index)
    const groups = this.data.groups.slice()
    const g = groups[gIndex]
    if (!g) return
    const items = (g.items || []).slice()
    items.push({ id: makeId('i'), name: '新入口', emoji: '➡️', color: '#C5A059', page: '/pages/index/index', badge: '' })
    groups[gIndex] = { ...g, items }
    this.setData({ groups })
  },

  editItem(e) {
    const gIndex = Number(e.currentTarget.dataset.gindex)
    const iIndex = Number(e.currentTarget.dataset.iindex)
    const g = this.data.groups[gIndex]
    const it = g && g.items ? g.items[iIndex] : null
    if (!it) return
    wx.showModal({
      title: '编辑入口名称',
      editable: true,
      placeholderText: '入口名称',
      content: it.name || '',
      success: (res) => {
        if (!res.confirm) return
        const name = (res.content || '').trim()
        if (!name) return
        const groups = this.data.groups.slice()
        const items = (groups[gIndex].items || []).slice()
        items[iIndex] = { ...items[iIndex], name }
        groups[gIndex] = { ...groups[gIndex], items }
        this.setData({ groups })
      }
    })
  },

  deleteItem(e) {
    const gIndex = Number(e.currentTarget.dataset.gindex)
    const iIndex = Number(e.currentTarget.dataset.iindex)
    wx.showModal({
      title: '确认删除入口',
      content: '删除后不可恢复，确定继续？',
      success: (res) => {
        if (!res.confirm) return
        const groups = this.data.groups.slice()
        const items = (groups[gIndex].items || []).slice()
        items.splice(iIndex, 1)
        groups[gIndex] = { ...groups[gIndex], items }
        this.setData({ groups })
      }
    })
  },

  moveItemUp(e) {
    const gIndex = Number(e.currentTarget.dataset.gindex)
    const iIndex = Number(e.currentTarget.dataset.iindex)
    if (iIndex <= 0) return
    const groups = this.data.groups.slice()
    const items = (groups[gIndex].items || []).slice()
    const tmp = items[iIndex - 1]
    items[iIndex - 1] = items[iIndex]
    items[iIndex] = tmp
    groups[gIndex] = { ...groups[gIndex], items }
    this.setData({ groups })
  },

  moveItemDown(e) {
    const gIndex = Number(e.currentTarget.dataset.gindex)
    const iIndex = Number(e.currentTarget.dataset.iindex)
    const groups = this.data.groups.slice()
    const items = (groups[gIndex].items || []).slice()
    if (iIndex >= items.length - 1) return
    const tmp = items[iIndex + 1]
    items[iIndex + 1] = items[iIndex]
    items[iIndex] = tmp
    groups[gIndex] = { ...groups[gIndex], items }
    this.setData({ groups })
  },

  save() {
    if (this.data.saving) return
    this.setData({ saving: true })
    storeApi.adminSaveExploreConfig(this.data.groups)
      .then(res => {
        if (res && res.code === 0) {
          wx.showToast({ title: '已保存', icon: 'success' })
          setTimeout(() => {
            wx.navigateBack()
          }, 300)
        } else {
          this.setData({ saving: false })
        }
      })
      .catch(() => {
        this.setData({ saving: false })
        wx.showToast({ title: '保存失败', icon: 'none' })
      })
  }
})

