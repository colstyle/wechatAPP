// pages/settings/settings.js
const app = getApp()

Page({
  data: {
    userInfo: {}
  },

  onLoad() {
    this.checkLogin()
  },

  onShow() {
    if (app.globalData.token) {
      this.setData({ userInfo: app.globalData.userInfo || {} })
    }
  },

  // 检查登录
  checkLogin() {
    if (!app.globalData.token) {
      app.wechatLogin()
        .then(() => {
          this.setData({ userInfo: app.globalData.userInfo || {} })
        })
        .catch(err => {
          console.error('登录失败', err)
        })
    }
  },

  // 头像点击
  onAvatarTap() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]
        // TODO: 上传头像
        wx.showToast({ title: '功能开发中', icon: 'none' })
      }
    })
  },

  // 个人信息
  onProfileTap() {
    wx.navigateTo({
      url: '/pages/profile/edit'
    })
  },

  // 我的尺码
  onSizeTap() {
    wx.navigateTo({
      url: '/pages/size/size'
    })
  },

  // 关于我们
  onAboutTap() {
    wx.showModal({
      title: '关于小时光租衣舍',
      content: '小时光租衣舍 - 专业的服装租赁平台\n\n提供按天、按次、订阅等多种租赁方式，让时尚触手可及。',
      showCancel: false
    })
  }
})
