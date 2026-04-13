// components/cp-nav-bar/cp-nav-bar.js
const app = getApp()

Component({
  options: {
    multipleSlots: true
  },
  properties: {
    // 页面标题
    title: { type: String, value: '' },
    // 是否显示返回按钮
    showBack: { type: Boolean, value: true },
    // 背景样式："transparent" | "white" | "blur" | 任意 CSS 背景值
    bg: { type: String, value: 'white' },
    // 标题颜色：auto（根据 bg 自动）| "dark" | "light"
    titleTheme: { type: String, value: 'auto' }
  },

  data: {
    navBarData: { navBarHeight: 88, statusBarHeight: 44 },
    bgStyle: 'rgba(255,255,255,1)',
    titleColor: '#1C1C1C',
    titleStyle: ''
  },

  lifetimes: {
    attached() {
      const navBarData = app.globalData.navBarData || {
        navBarHeight: 88,
        statusBarHeight: 44
      }
      this.setData({ navBarData })
      this._applyTheme()
    }
  },

  observers: {
    'bg': function () {
      this._applyTheme()
    }
  },

  methods: {
    _applyTheme() {
      const bg = this.properties.bg
      let bgStyle = 'rgba(255,255,255,1)'
      let titleColor = '#1C1C1C'
      let titleStyle = ''

      if (bg === 'transparent') {
        bgStyle = 'transparent'
      } else if (bg === 'blur') {
        bgStyle = 'rgba(255,255,255,0.72)'
      } else if (bg === 'white') {
        bgStyle = 'rgba(253,252,249,1)'
      } else {
        bgStyle = bg
      }

      const theme = this.properties.titleTheme
      if (theme === 'light') {
        titleColor = '#FFFFFF'
        titleStyle = 'light'
      } else if (theme === 'dark') {
        titleColor = '#1C1C1C'
        titleStyle = ''
      }

      this.setData({ bgStyle, titleColor, titleStyle })
    },

    onBack() {
      const pages = getCurrentPages()
      if (pages.length > 1) {
        wx.navigateBack({ delta: 1 })
      } else {
        wx.reLaunch({ url: '/pages/index/index' })
      }
    }
  }
})
