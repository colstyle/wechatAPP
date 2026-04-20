// pages/admin/catalog/inventory/inventory.js
const { adminApi, productApi } = require('../../../../utils/api')

Page({
  data: {
    activeTab: 'category',
    // 分类
    categories: [],
    // 商品
    products: [],
    keyword: '',
    filterCatId: 0,
    page: 1,
    page_size: 30,
    hasMore: true,
    loading: false,
    // 拖拽状态
    dragging: false,
    dragIdx: -1,
    overIdx: -1,
    _dragStartY: 0,
    _itemHeight: 120 // rpx 转 px 后约 120 * screenWidth/750
  },

  onShow() {
    this.loadCategories()
    if (this.data.activeTab === 'product') {
      this.loadProducts()
    }
  },

  // ====== Tab ======
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({ activeTab: tab }, () => {
      if (tab === 'product') {
        this.setData({ products: [], page: 1, hasMore: true })
        this.loadProducts()
      }
    })
  },

  // ====== 分类 ======
  loadCategories() {
    adminApi.getCategories().then(res => {
      if (res.code === 0) this.setData({ categories: res.data || [] })
    }).catch(err => console.error(err))
  },

  onAddCategory() {
    wx.showModal({
      title: '新增分类',
      placeholderText: '请输入分类名称',
      editable: true,
      success: (res) => {
        if (res.confirm && (res.content || '').trim()) {
          adminApi.createCategory({ name: res.content.trim() }).then(() => {
            wx.showToast({ title: '已创建', icon: 'success' })
            this.loadCategories()
          }).catch(err => {
            wx.showToast({ title: err.message || '创建失败', icon: 'none' })
          })
        }
      }
    })
  },

  onEditCategory(e) {
    const { id, name } = e.currentTarget.dataset
    wx.showModal({
      title: '修改分类名',
      editable: true,
      content: name,
      success: (res) => {
        if (res.confirm && (res.content || '').trim()) {
          adminApi.updateCategory(id, { name: res.content.trim() }).then(() => {
            wx.showToast({ title: '已更新', icon: 'success' })
            this.loadCategories()
          }).catch(err => {
            wx.showToast({ title: err.message || '更新失败', icon: 'none' })
          })
        }
      }
    })
  },

  onDeleteCategory(e) {
    const { id, name } = e.currentTarget.dataset
    wx.showModal({
      title: `删除分类 "${name}" ?`,
      content: '分类下有商品时无法删除，请先移除商品。',
      confirmColor: '#D32F2F',
      success: (res) => {
        if (res.confirm) {
          adminApi.deleteCategory(id).then(() => {
            wx.showToast({ title: '已删除', icon: 'success' })
            this.loadCategories()
          }).catch(err => {
            wx.showToast({ title: err.message || '删除失败', icon: 'none' })
          })
        }
      }
    })
  },

  // ====== 分类拖拽排序（touch 事件模拟） ======
  onDragStart(e) {
    const idx = e.currentTarget.dataset.index
    const touch = e.touches[0]
    this.setData({ dragging: true, dragIdx: idx, overIdx: idx, _dragStartY: touch.clientY })
  },

  onDragMove(e) {
    if (!this.data.dragging) return
    const touch = e.touches[0]
    const deltaY = touch.clientY - this.data._dragStartY
    const itemH = 110 * wx.getSystemInfoSync().windowWidth / 750
    const newIdx = Math.max(0, Math.min(
      this.data.categories.length - 1,
      this.data.dragIdx + Math.round(deltaY / itemH)
    ))
    if (newIdx !== this.data.overIdx) {
      this.setData({ overIdx: newIdx })
    }
  },

  onDragEnd() {
    if (!this.data.dragging) return
    const { dragIdx, overIdx, categories } = this.data
    if (dragIdx !== overIdx) {
      const arr = [...categories]
      const [moved] = arr.splice(dragIdx, 1)
      arr.splice(overIdx, 0, moved)
      this.setData({ categories: arr, dragging: false, dragIdx: -1, overIdx: -1 })
      // 持久化排序
      adminApi.reorderCategories(0, arr.map(c => c.id)).catch(() => {
        wx.showToast({ title: '排序保存失败', icon: 'none' })
      })
    } else {
      this.setData({ dragging: false, dragIdx: -1, overIdx: -1 })
    }
  },

  // ====== 商品 ======
  loadProducts(isLoadMore = false) {
    if (this.data.loading) return
    this.setData({ loading: true })
    const { keyword, filterCatId, page, page_size } = this.data
    const currentPage = isLoadMore ? page + 1 : 1
    const params = { page: currentPage, page_size }
    if (keyword) params.keyword = keyword
    if (filterCatId) params.category_id = filterCatId

    productApi.getProducts(params).then(res => {
      if (res.code === 0) {
        const list = res.data.list || []
        this.setData({
          products: isLoadMore ? [...this.data.products, ...list] : list,
          page: currentPage,
          hasMore: list.length === page_size,
          loading: false
        })
      }
    }).catch(() => {
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    })
  },

  onFilterCat(e) {
    const id = e.currentTarget.dataset.id
    this.setData({ filterCatId: id, products: [], page: 1, hasMore: true }, () => {
      this.loadProducts()
    })
  },

  onSearchInput(e) { this.setData({ keyword: e.detail.value }) },
  onSearch() {
    this.setData({ products: [], page: 1, hasMore: true }, () => this.loadProducts())
  },

  onLoadMore() {
    if (this.data.hasMore) this.loadProducts(true)
  },

  onAddProduct() {
    wx.navigateTo({ url: '/pages/admin/inventory/edit/edit' })
  },

  onEditProduct(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/admin/inventory/edit/edit?id=${id}` })
  },

  onDeleteProduct(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除商品？',
      content: '若有关联订单，自动降为下架处理。',
      confirmColor: '#D32F2F',
      success: (res) => {
        if (res.confirm) {
          adminApi.deleteProduct(id).then(r => {
            wx.showToast({ title: r.message || '已处理', icon: 'none' })
            this.onSearch()
          }).catch(err => {
            wx.showToast({ title: err.message || '删除失败', icon: 'none' })
          })
        }
      }
    })
  },

  // ====== 商品拖拽排序 ======
  onProductDragStart(e) {
    const idx = e.currentTarget.dataset.index
    const touch = e.touches[0]
    this.setData({ dragging: true, dragIdx: idx, overIdx: idx, _dragStartY: touch.clientY })
  },

  onProductDragMove(e) {
    if (!this.data.dragging) return
    const touch = e.touches[0]
    const deltaY = touch.clientY - this.data._dragStartY
    const itemH = 130 * wx.getSystemInfoSync().windowWidth / 750
    const newIdx = Math.max(0, Math.min(
      this.data.products.length - 1,
      this.data.dragIdx + Math.round(deltaY / itemH)
    ))
    if (newIdx !== this.data.overIdx) this.setData({ overIdx: newIdx })
  },

  onProductDragEnd() {
    if (!this.data.dragging) return
    const { dragIdx, overIdx, products } = this.data
    if (dragIdx !== overIdx) {
      const arr = [...products]
      const [moved] = arr.splice(dragIdx, 1)
      arr.splice(overIdx, 0, moved)
      this.setData({ products: arr, dragging: false, dragIdx: -1, overIdx: -1 })
      // 持久化
      adminApi.reorderProducts(arr.map(p => p.id)).catch(() => {
        wx.showToast({ title: '排序保存失败', icon: 'none' })
      })
    } else {
      this.setData({ dragging: false, dragIdx: -1, overIdx: -1 })
    }
  }
})
