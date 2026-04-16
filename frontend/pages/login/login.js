const app = getApp()

Page({
  data: {
    avatarUrl: '',
    defaultAvatar: 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg',
    nickname: '',
    submitting: false,
    redirectUrl: ''
  },

  onLoad(options) {
    if (options.redirect) {
      this.setData({
        redirectUrl: decodeURIComponent(options.redirect)
      })
    }
  },

  onChooseAvatar(e) {
    const { avatarUrl } = e.detail;
    // We should upload this temporary file to our server to get a real hosted url
    // For now, we will assume app.uploadImage exists and handles token
    wx.showLoading({ title: '上传头像中...' })
    app.uploadImage(avatarUrl).then(url => {
      this.setData({ avatarUrl: url })
      wx.hideLoading()
    }).catch(err => {
      wx.hideLoading()
      wx.showToast({ title: '头像上传失败', icon: 'none' })
      // Use temporary URL as fallback for local dev if needed
      if (app.globalData.ENV === 'dev') {
         this.setData({ avatarUrl: avatarUrl })
      }
    })
  },

  onInputNickname(e) {
    this.setData({
      nickname: e.detail.value
    })
  },

  onSubmit() {
    const { avatarUrl, nickname } = this.data;
    if (!avatarUrl || avatarUrl === this.data.defaultAvatar) {
      wx.showToast({ title: '请选择头像', icon: 'none' })
      return;
    }
    if (!nickname.trim()) {
      wx.showToast({ title: '请输入昵称', icon: 'none' })
      return;
    }

    this.setData({ submitting: true })
    app.request('/api/v1/user/profile', 'POST', {
      avatar_url: avatarUrl,
      nickname: nickname
    }).then(res => {
      if (res.code === 0) {
        wx.showToast({ title: '授权成功', icon: 'success' })
        // Update local userInfo
        app.globalData.userInfo = Object.assign({}, app.globalData.userInfo, {
          avatar_url: avatarUrl,
          nickname: nickname
        })
        wx.setStorageSync('userInfo', app.globalData.userInfo)
        
        setTimeout(() => {
          if (this.data.redirectUrl) {
            wx.redirectTo({ url: this.data.redirectUrl })
          } else {
            wx.navigateBack({
               fail: () => wx.switchTab({ url: '/pages/index/index' })
            })
          }
        }, 1500)
      } else {
        wx.showToast({ title: res.message || '保存失败', icon: 'none' })
        this.setData({ submitting: false })
      }
    }).catch(() => {
      this.setData({ submitting: false })
    })
  },

  onCancel() {
    wx.navigateBack({
      fail() {
        wx.switchTab({ url: '/pages/index/index' })
      }
    })
  }
})
