// pages/index/index.js
const app = getApp()
const productApi = require('../../utils/api').productApi
const subscriptionApi = require('../../utils/api').subscriptionApi

Page({
  data: {
    selectedDate: null,
    startDate: '', // 今天
    endDate: '',   // 今天 + 30天
    // 轮播图 - 使用色块代替图片
    banners: [
      { id: 1, product_id: 1, title: '新品上市', subtitle: '春季限定租衣优惠' },
      { id: 2, product_id: 2, title: '会员专享', subtitle: '月卡会员首月半价' },
      { id: 3, product_id: 3, title: '品牌联动', subtitle: '知名设计师入驻' }
    ],

    // 分类 - 使用 Emoji
    categories: [
      { id: 1, name: '礼服', emoji: '👗', gradient: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)' },
      { id: 2, name: '常服', emoji: '👕', gradient: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)' },
      { id: 3, name: '配饰', emoji: '💎', gradient: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)' },
      { id: 4, name: '鞋包', emoji: '👜', gradient: 'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)' },
      { id: 5, name: '3件套餐', emoji: '🎁', gradient: 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)' }
    ],

    // 热门商品
    hotProducts: [],

    // 新品商品
    newProducts: [],

    // 搭配推荐
    outfits: [],

    // 品牌
    brands: [],

    // 分页
    page: 1,
    page_size: 10,
    hasMore: true,
    loading: false
  },

  onLoad() {
    this.initDateRange()
    this.loadData()
  },

  // 初始化日期范围
  initDateRange() {
    const now = new Date()
    const startDate = app.formatDate(now)
    const future = new Date()
    future.setDate(now.getDate() + 30)
    const endDate = app.formatDate(future)
    
    // 如果全局已经选过日期，同步到当前页
    const selectedDate = app.globalData.selectedDate || startDate

    this.setData({
      startDate,
      endDate,
      selectedDate
    })
    
    if (!app.globalData.selectedDate) {
      app.globalData.selectedDate = startDate
    }
  },

  onShow() {
    // 检查登录状态
    this.checkLogin()
    // 刷新订阅信息
    this.loadSubscription()
  },

  // 日期切换处理
  onDateChange(e) {
    const date = e.detail.value
    this.setData({
      selectedDate: date
    })
    app.globalData.selectedDate = date
    // 重新加载数据（根据日期过滤）
    this.loadData()
  },

  // 分类点击处理
  onCategoryTap(e) {
    const id = e.currentTarget.dataset.id
    if (id === 5) {
      wx.navigateTo({
        url: '/pages/package/package'
      })
    } else {
      wx.navigateTo({
        url: `/pages/category/category?id=${id}`
      })
    }
  },

  // 检查登录
  checkLogin() {
    if (!app.globalData.token) {
      app.wechatLogin()
        .then(res => {
          this.loadData()
        })
        .catch(err => {
          console.error('登录失败', err)
        })
    }
  },

  // 加载订阅信息
  loadSubscription() {
    subscriptionApi.getActiveSubscription()
      .then(res => {
        if (res.data) {
          this.setData({
            activeSubscription: res.data
          })
        }
      })
      .catch(err => {
        console.error('获取订阅失败', err)
      })
  },

  // 加载数据
  loadData() {
    this.getProductData()
    this.getOutfitData()
    this.getBrandData()
  },

  // 获取商品数据
  getProductData() {
    this.setData({ loading: true })

    const dateParams = { available_date: this.data.selectedDate }

    // 获取热门商品
    productApi.getHotProducts(8, dateParams)
      .then(res => {
        this.setData({
          hotProducts: res.data
        })
      })
      .catch(err => {
        console.error('获取热门商品失败', err)
      })

    // 获取新品商品
    productApi.getNewProducts(8, dateParams)
      .then(res => {
        this.setData({
          newProducts: res.data,
          loading: false
        })
      })
      .catch(err => {
        console.error('获取新品商品失败', err)
      })
  },

  // 获取搭配数据
  getOutfitData() {
    productApi.getOutfits(4)
      .then(res => {
        this.setData({
          outfits: res.data
        })
      })
      .catch(err => {
        console.error('获取搭配失败', err)
      })
  },

  // 获取品牌数据
  getBrandData() {
    productApi.getBrands()
      .then(res => {
        this.setData({
          brands: res.data
        })
      })
      .catch(err => {
        console.error('获取品牌失败', err)
      })
  },

  // 搜索
  onSearch() {
    wx.navigateTo({
      url: '/pages/category/category?search=1'
    })
  },

  // 分类点击
  onCategoryTap(e) {
    const id = e.currentTarget.dataset.id
    if (id === 5) {
      wx.navigateTo({
        url: '/pages/package/package'
      })
      return
    }
    wx.navigateTo({
      url: `/pages/category/category?category_id=${id}`
    })
  },

  // 轮播图点击
  onBannerTap(e) {
    const productId = e.currentTarget.dataset.product
    wx.navigateTo({
      url: `/pages/detail/detail?id=${productId}`
    })
  },

  // 商品点击
  onProductTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    })
  },

  // 搭配点击
  onOutfitTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/product/product?outfit_id=${id}`
    })
  },

  // 品牌点击
  onBrandTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/product/product?brand_id=${id}`
    })
  },

  // 更多点击
  onMoreTap(e) {
    const type = e.currentTarget.dataset.type
    if (type === 'hot') {
      wx.navigateTo({
        url: '/pages/product/product?type=hot'
      })
    } else if (type === 'new') {
      wx.navigateTo({
        url: '/pages/product/product?type=new'
      })
    }
  },

  // 搭配更多点击
  onOutfitMoreTap() {
    wx.navigateTo({
      url: '/pages/product/product?type=outfit'
    })
  },

  // 品牌更多点击
  onBrandMoreTap() {
    wx.navigateTo({
      url: '/pages/product/product?type=brand'
    })
  },

  // 加载更多
  onLoadMore() {
    if (!this.data.hasMore || this.data.loading) return

    this.setData({
      loading: true,
      page: this.data.page + 1
    })

    productApi.getProducts({
      page: this.data.page,
      page_size: this.data.page_size
    })
      .then(res => {
        const newProducts = res.data.list
        if (newProducts.length < this.data.page_size) {
          this.setData({
            hasMore: false,
            loading: false,
            newProducts: [...this.data.newProducts, ...newProducts]
          })
        } else {
          this.setData({
            loading: false,
            newProducts: [...this.data.newProducts, ...newProducts]
          })
        }
      })
      .catch(err => {
        console.error('加载更多失败', err)
        this.setData({
          loading: false
        })
      })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.setData({
      page: 1,
      hasMore: true,
      newProducts: [],
      loading: false
    })
    this.loadData()
    setTimeout(() => {
      wx.stopPullDownRefresh()
    }, 1000)
  }
})
