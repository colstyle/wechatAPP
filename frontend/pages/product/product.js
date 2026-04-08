// pages/product/product.js
const app = getApp()
const productApi = require('../../utils/api').productApi

Page({
  data: {
    type: '',
    brandId: null,
    outfitId: null,
    categoryId: null,
    products: [],
    loading: false,
    page: 1,
    page_size: 20,
    hasMore: true
  },

  onLoad(options) {
    // 获取参数
    if (options.type) {
      this.setData({ type: options.type })
    }
    if (options.brand_id) {
      this.setData({ brandId: parseInt(options.brand_id) })
    }
    if (options.outfit_id) {
      this.setData({ outfitId: parseInt(options.outfit_id) })
    }
    if (options.category_id) {
      this.setData({ categoryId: parseInt(options.category_id) })
    }

    this.loadData()
  },

  // 加载商品数据
  loadData() {
    if (this.data.loading || !this.data.hasMore) return

    this.setData({ loading: true })

    const params = {
      page: this.data.page,
      page_size: this.data.page_size
    }

    // 根据类型加载数据
    if (this.data.type === 'hot') {
      productApi.getHotProducts(20)
        .then(res => {
          this.setData({
            products: res.data,
            hasMore: false,
            loading: false
          })
        })
        .catch(err => {
          console.error('获取热门商品失败', err)
          this.setData({ loading: false })
        })
    } else if (this.data.type === 'new') {
      productApi.getNewProducts(20)
        .then(res => {
          this.setData({
            products: res.data,
            hasMore: false,
            loading: false
          })
        })
        .catch(err => {
          console.error('获取新品失败', err)
          this.setData({ loading: false })
        })
    } else {
      // 品牌或分类商品
      if (this.data.brandId) {
        params.brand_id = this.data.brandId
      }
      if (this.data.categoryId) {
        params.category_id = this.data.categoryId
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
    }
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

  // 排序
  onSortTap() {
    wx.showActionSheet({
      itemList: ['默认排序', '租金从低到高', '租金从高到低'],
      success: (res) => {
        console.log('选择排序', res.tapIndex)
        // TODO: 实现排序逻辑
      }
    })
  },

  // 商品点击
  onProductTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    })
  },

  // 加载更多
  onLoadMore() {
    if (!this.data.hasMore || this.data.loading) return

    this.setData({
      page: this.data.page + 1
    })
    this.loadData()
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
