const app = getApp()
const auth = require('../../../../utils/auth')
const adminApi = require('../../../../utils/api').adminApi

Page({
  data: {
    parentId: 0,
    parentName: '',
    navTitle: '分类管理',
    categories: [],
    loading: false,
    showEditor: false,
    editorMode: 'create',
    form: {
      id: null,
      name: '',
      icon: ''
    },
    saving: false
  },

  onLoad(options) {
    app.ensureLogin()
      .then(() => {
        if (!auth.hasRole('admin')) {
          wx.showToast({ title: '无权限访问', icon: 'none' })
          setTimeout(() => wx.switchTab({ url: '/pages/profile/profile' }), 300)
          return
        }

        const parentId = parseInt(options.parent_id || '0', 10) || 0
        const parentName = options.parent_name ? decodeURIComponent(options.parent_name) : ''
        const navTitle = parentId === 0 ? '分类管理' : `子分类`
        this.setData({ parentId, parentName, navTitle }, () => this.loadCategories())
      })
      .catch(() => {
        wx.showToast({ title: '请先登录', icon: 'none' })
        setTimeout(() => wx.switchTab({ url: '/pages/profile/profile' }), 300)
      })
  },

  loadCategories() {
    if (this.data.loading) return
    this.setData({ loading: true })
    adminApi.getCategories(this.data.parentId)
      .then(res => {
        const list = (res && res.code === 0 && res.data) ? res.data : []
        this.setData({ categories: list, loading: false })
      })
      .catch(err => {
        console.error(err)
        this.setData({ loading: false })
        wx.showToast({ title: '加载失败', icon: 'none' })
      })
  },

  openCreate() {
    this.setData({
      showEditor: true,
      editorMode: 'create',
      form: { id: null, name: '', icon: '' }
    })
  },

  openEdit(e) {
    const { id, name, icon } = e.currentTarget.dataset
    this.setData({
      showEditor: true,
      editorMode: 'edit',
      form: { id, name: name || '', icon: icon || '' }
    })
  },

  closeEditor() {
    if (this.data.saving) return
    this.setData({ showEditor: false })
  },

  onNameInput(e) {
    this.setData({ 'form.name': (e.detail.value || '').trimStart() })
  },

  onIconInput(e) {
    this.setData({ 'form.icon': (e.detail.value || '').trimStart() })
  },

  saveCategory() {
    if (this.data.saving) return
    const name = (this.data.form.name || '').trim()
    const icon = (this.data.form.icon || '').trim()
    if (!name) {
      wx.showToast({ title: '请输入分类名称', icon: 'none' })
      return
    }

    this.setData({ saving: true })
    const req = this.data.editorMode === 'create'
      ? adminApi.createCategory({ name, icon: icon || null, parent_id: this.data.parentId })
      : adminApi.updateCategory(this.data.form.id, { name, icon: icon || null })

    req.then(res => {
      if (res && res.code === 0) {
        wx.showToast({ title: '保存成功', icon: 'success' })
        this.setData({ showEditor: false, saving: false })
        this.loadCategories()
      } else {
        this.setData({ saving: false })
      }
    }).catch(err => {
      console.error(err)
      this.setData({ saving: false })
      wx.showToast({ title: (err && err.message) || '保存失败', icon: 'none' })
    })
  },

  onDelete(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '删除后不可恢复，确定继续？',
      success: (res) => {
        if (!res.confirm) return
        adminApi.deleteCategory(id)
          .then(r => {
            if (r && r.code === 0) {
              wx.showToast({ title: '已删除', icon: 'success' })
              this.loadCategories()
            }
          })
          .catch(err => {
            wx.showToast({ title: err && err.message ? err.message : '删除失败', icon: 'none' })
          })
      }
    })
  },

  enterChildren(e) {
    const id = e.currentTarget.dataset.id
    const name = e.currentTarget.dataset.name || ''
    wx.navigateTo({
      url: `/pages/admin/category/list/list?parent_id=${id}&parent_name=${encodeURIComponent(name)}`
    })
  },

  moveUp(e) {
    const idx = Number(e.currentTarget.dataset.index)
    if (idx <= 0) return
    const list = this.data.categories.slice()
    const tmp = list[idx - 1]
    list[idx - 1] = list[idx]
    list[idx] = tmp
    this.setData({ categories: list }, () => this.persistOrder())
  },

  moveDown(e) {
    const idx = Number(e.currentTarget.dataset.index)
    const list = this.data.categories.slice()
    if (idx >= list.length - 1) return
    const tmp = list[idx + 1]
    list[idx + 1] = list[idx]
    list[idx] = tmp
    this.setData({ categories: list }, () => this.persistOrder())
  },

  persistOrder() {
    const orderedIds = this.data.categories.map(c => c.id)
    adminApi.reorderCategories(this.data.parentId, orderedIds)
      .then(() => {})
      .catch(() => wx.showToast({ title: '排序保存失败', icon: 'none' }))
  }
})
