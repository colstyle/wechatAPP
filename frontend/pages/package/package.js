const app = getApp()
const productApi = require('../../utils/api').productApi
const orderApi = require('../../utils/api').orderApi

Page({
  data: {
    selectedDate: '',
    products: [],
    selectedItems: [],
    totalRent: 69.9,
    totalDeposit: 0,
    totalAmount: 69.9,
    page: 1,
    page_size: 10,
    hasMore: true,
    loading: false
  },

  onLoad() {
    const selectedDate = app.globalData.selectedDate || app.formatDate(new Date())
    this.setData({
      selectedDate
    })
    this.loadProducts()
  },

  // 加载可用商品
  loadProducts(isLoadMore = false) {
    if (this.data.loading || (!isLoadMore && !this.data.hasMore)) return

    this.setData({ loading: true })

    const { selectedDate, page, page_size } = this.data
    const currentPage = isLoadMore ? page + 1 : 1

    productApi.getProducts({
      available_date: selectedDate,
      package_only: true,
      page: currentPage,
      page_size
    }).then(res => {
      if (res.code === 0) {
        const newProducts = res.data.list.map(p => ({
          ...p,
          selected: this.data.selectedItems.some(si => si.id === p.id),
          // 模拟占位符（实际项目中应由后端返回或使用真实图片）
          placeholder: p.category_id === 1 ? '👗' : p.category_id === 2 ? '👕' : '👠'
        }))

        this.setData({
          products: isLoadMore ? [...this.data.products, ...newProducts] : newProducts,
          page: currentPage,
          hasMore: newProducts.length === page_size,
          loading: false
        })
      }
    }).catch(err => {
      console.error('加载商品失败', err)
      this.setData({ loading: false })
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    })
  },

  // 切换选择
  toggleSelect(e) {
    const item = e.currentTarget.dataset.item
    const { selectedItems, products } = this.data
    const index = selectedItems.findIndex(si => si.id === item.id)

    if (index > -1) {
      // 取消选择
      selectedItems.splice(index, 1)
    } else {
      // 检查数量限制
      if (selectedItems.length >= 3) {
        wx.showToast({
          title: '套餐仅限3件衣物',
          icon: 'none'
        })
        return
      }
      // 添加选择
      selectedItems.push(item)
    }

    // 更新商品列表的选择状态
    const updatedProducts = products.map(p => ({
      ...p,
      selected: selectedItems.some(si => si.id === p.id)
    }))

    this.setData({
      selectedItems,
      products: updatedProducts
    })

    this.calculateTotal()
  },

  // 移除项目
  removeItem(e) {
    const id = e.currentTarget.dataset.id
    const { selectedItems, products } = this.data
    const index = selectedItems.findIndex(si => si.id === id)

    if (index > -1) {
      selectedItems.splice(index, 1)
      const updatedProducts = products.map(p => ({
        ...p,
        selected: selectedItems.some(si => si.id === p.id)
      }))
      this.setData({
        selectedItems,
        products: updatedProducts
      })
      this.calculateTotal()
    }
  },

  // 计算总价
  calculateTotal() {
    const { selectedItems, totalRent } = this.data
    const totalDeposit = selectedItems.reduce((sum, item) => sum + (item.deposit || 0), 0)
    const totalAmount = (totalRent + totalDeposit).toFixed(2)

    this.setData({
      totalDeposit: totalDeposit.toFixed(2),
      totalAmount
    })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.setData({
      page: 1,
      hasMore: true,
      selectedItems: []
    }, () => {
      this.loadProducts().then(() => {
        wx.stopPullDownRefresh()
      })
    })
  },

  // 触底加载
  onLoadMore() {
    if (this.data.hasMore) {
      this.loadProducts(true)
    }
  },

  // 提交订单
  onSubmit() {
    const { selectedItems, selectedDate } = this.data
    if (selectedItems.length !== 3) {
      wx.showToast({
        title: '请选满3件衣物',
        icon: 'none'
      })
      return
    }

    // 这里跳转到确认订单页，或者直接下单
    // 为了简化，我们这里直接跳转到 confirm 页面
    const orderItems = selectedItems.map(item => ({
      product_id: item.id,
      name: item.name,
      image: item.cover_image,
      deposit: item.deposit,
      rent: 0, // 套餐模式下单品租金记为0
      quantity: 1,
      size: 'F', // 默认均码
      color: '默认'
    }))

    // 存储到全局或跳转参数
    app.globalData.checkoutOrder = {
      rental_type: 5, // 套餐租赁
      items: orderItems,
      start_date: selectedDate,
      total_rent: 69.9,
      total_deposit: parseFloat(this.data.totalDeposit)
    }

    wx.navigateTo({
      url: '/pages/orders/confirm'
    })
  }
})
