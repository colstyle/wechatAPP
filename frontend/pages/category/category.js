// pages/category/category.js
const app = getApp()
const productApi = require('../../utils/api').productApi

Page({
  data: {
    keyword: '',
    categories: [],
    subCategories: [],
    products: [],
    selectedCategory: null,
    selectedSubCategory: null,
    loading: false,
    page: 1,
    page_size: 20,
    hasMore: true
  },

  onLoad(options) {
    // 获取分类参数
    if (options.category_id) {
      this.setData({ selectedCategory: parseInt(options.category_id) })
    }
    if (options.keyword) {
      this.setData({ keyword: decodeURIComponent(options.keyword) })
    }

    this.loadCategories()
    this.loadData()
  },

  // 加载分类
  loadCategories() {
    productApi.getCategories(0)
      .then(res => {
        this.setData({ categories: res.data })
        if (!this.data.selectedCategory && res.data.length > 0) {
          this.setData({ selectedCategory: res.data[0].id })
          this.loadSubCategories(res.data[0].id)
        }
      })
      .catch(err => {
        console.error('获取分类失败', err)
      })
  },

  // 加载子分类
  loadSubCategories(categoryId) {
    productApi.getCategories(categoryId)
      .then(res => {
        this.setData({ subCategories: res.data })
      })
      .catch(err => {
        console.error('获取子分类失败', err)
      })
  },

  // 加载商品数据
  loadData() {
    if (this.data.loading || !this.data.hasMore) return

    this.setData({ loading: true })

    const params = {
      page: this.data.page,
      page_size: this.data.page_size
    }

    if (this.data.selectedCategory) {
      params.category_id = this.data.selectedCategory
    }
    if (this.data.selectedSubCategory) {
      params.category_id = this.data.selectedSubCategory
    }
    if (this.data.keyword) {
      params.keyword = this.data.keyword
    }

    productApi.getProducts(params)
      .then(res => {
        const newProducts = this.data.page === 1 ? res.data.list : [...this.data.products, ...res.data.list]
        const hasMore = res.data.list.length >= this.data.page_size

        this.setData({
          products: newProducts,
          hasMore: hasMore,
          loading: false
        })
      })
      .catch(err => {
        console.error('获取商品失败', err)
        this.setData({ loading: false })
      })
  },

  // 分类点击
  onCategoryTap(e) {
    const id = e.currentTarget.dataset.id
    this.setData({
      selectedCategory: id,
      selectedSubCategory: null,
      products: [],
      page: 1,
      hasMore: true
    })
    this.loadSubCategories(id)
    this.loadData()
  },

  // 子分类点击
  onSubCategoryTap(e) {
    const id = e.currentTarget.dataset.id
    this.setData({
      selectedSubCategory: id,
      products: [],
      page: 1,
      hasMore: true
    })
    this.loadData()
  },

  // 商品点击
  onProductTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    })
  },

  // 搜索
  onSearchConfirm(e) {
    const keyword = e.detail.value
    this.setData({
      keyword: keyword,
      products: [],
      page: 1,
      hasMore: true
    })
    this.loadData()
  },

  // 上拉加载更多
  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.setData({ page: this.data.page + 1 })
      this.loadData()
    }
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.setData({
      page: 1,
      hasMore: true,
      products: []
    })
    this.loadData()
    setTimeout(() => {
      wx.stopPullDownRefresh()
    }, 1000)
  }
})
