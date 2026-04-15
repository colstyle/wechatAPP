// pages/category/category.js
// 分类与探索 — 由后端配置驱动，默认空，店主可在分类页进入编辑

Page({
  data: {
    groups: [],          // 左侧分组列表
    activeGroupId: '',   // 当前激活分组id
    activeItems: [],     // 当前分组的宫格项目
    keyword: '',         // 搜索关键字
    filteredItems: [],   // 搜索过滤后的结果
    isSearching: false,  // 是否处于搜索模式
    isAdmin: false
  },

  onLoad() {
    const auth = require('../../utils/auth')
    this.setData({ isAdmin: auth.hasRole('admin') })
    this.loadConfig()
  },

  onShow() {
    // 每次显示时重置搜索状态
    if (this.data.isSearching) {
      this.clearSearch()
    }
  },

  // 初始化配置数据
  initConfig() {
    const groups = this.data.groups || []
    const firstGroup = groups[0] || {}
    this.setData({
      activeGroupId: firstGroup.id || '',
      activeItems: firstGroup.items || []
    })
  },

  loadConfig() {
    const storeApi = require('../../utils/api').storeApi
    storeApi.getExploreConfig()
      .then(res => {
        const groups = (res && res.code === 0 && Array.isArray(res.data)) ? res.data : []
        this.setData({ groups }, () => this.initConfig())
      })
      .catch(() => {
        this.setData({ groups: [] }, () => this.initConfig())
      })
  },

  // 左侧分组点击
  onGroupTap(e) {
    const gid = e.currentTarget.dataset.id
    const group = this.data.groups.find(g => g.id === gid)
    if (!group) return
    this.setData({
      activeGroupId: gid,
      activeItems: group.items || [],
      keyword: '',
      isSearching: false,
      filteredItems: []
    })
  },

  // 宫格项目点击 — 直接跳转到对应页面
  onItemTap(e) {
    const page = e.currentTarget.dataset.page
    if (!page) return

    // 客服页是tabBar页面，用switchTab；其他用navigateTo
    const tabPages = ['/pages/index/index', '/pages/category/category', '/pages/order/order', '/pages/profile/profile']
    if (tabPages.includes(page)) {
      wx.switchTab({ url: page })
    } else {
      wx.navigateTo({ url: page })
    }
  },

  // 搜索输入
  onSearchInput(e) {
    const keyword = e.detail.value.trim()
    this.setData({ keyword })
    if (!keyword) {
      this.setData({ isSearching: false, filteredItems: [] })
      return
    }
    this.doSearch(keyword)
  },

  // 搜索确认
  onSearchConfirm(e) {
    const keyword = (e.detail.value || '').trim()
    if (!keyword) {
      this.clearSearch()
      return
    }
    this.doSearch(keyword)
  },

  // 执行搜索（跨所有分组查找）
  doSearch(keyword) {
    const allItems = []
    ;(this.data.groups || []).forEach(g => {
      ;(g.items || []).forEach(item => {
        allItems.push({ ...item, _groupName: g.name })
      })
    })
    const filtered = allItems.filter(item =>
      item.name.includes(keyword) || (item._groupName && item._groupName.includes(keyword))
    )
    this.setData({ isSearching: true, filteredItems: filtered })
  },

  // 清除搜索
  clearSearch() {
    const group = this.data.groups.find(g => g.id === this.data.activeGroupId)
    this.setData({
      keyword: '',
      isSearching: false,
      filteredItems: [],
      activeItems: group ? group.items : []
    })
  },

  onEditTap() {
    if (!this.data.isAdmin) return
    wx.navigateTo({ url: '/pages/category_explore_edit/edit' })
  }
})
