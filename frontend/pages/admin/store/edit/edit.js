const app = getApp()
const auth = require('../../../../utils/auth')
const storeApi = require('../../../../utils/api').storeApi

Page({
  data: {
    form: {
      store_name: '',
      phone: '',
      address: '',
      open_hours: '',
      latitude: '',
      longitude: ''
    },
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
    storeApi.adminGetProfile()
      .then(res => {
        if (res && res.code === 0 && res.data) {
          const d = res.data
          this.setData({
            form: {
              store_name: d.store_name || '',
              phone: d.phone || '',
              address: d.address || '',
              open_hours: d.open_hours || '',
              latitude: d.latitude != null ? String(d.latitude) : '',
              longitude: d.longitude != null ? String(d.longitude) : ''
            }
          })
        }
      })
      .catch(() => {})
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    const val = e.detail.value
    this.setData({ [`form.${field}`]: val })
  },

  onSave() {
    if (this.data.saving) return
    const f = this.data.form || {}
    const payload = {
      store_name: (f.store_name || '').trim(),
      phone: (f.phone || '').trim(),
      address: (f.address || '').trim(),
      open_hours: (f.open_hours || '').trim(),
      latitude: f.latitude !== '' ? Number(f.latitude) : null,
      longitude: f.longitude !== '' ? Number(f.longitude) : null
    }
    this.setData({ saving: true })
    storeApi.adminSaveProfile(payload)
      .then(res => {
        if (res && res.code === 0) {
          wx.showToast({ title: '已保存', icon: 'success' })
        }
        this.setData({ saving: false })
      })
      .catch(() => {
        this.setData({ saving: false })
        wx.showToast({ title: '保存失败', icon: 'none' })
      })
  }
})
