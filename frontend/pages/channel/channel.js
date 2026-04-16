const app = getApp()
const auth = require('../../utils/auth.js')

Page({
  data: {
    type: '',
    title: '专属频道',
    productList: [],
    loading: false,
    page: 1,
    hasMore: true
  },

  onLoad(options) {
    const type = options.type || 'default';
    this.setData({ type });
    
    // Set dynamic page title
    const typeMap = {
      'sale999': '9.9 特惠体验',
      'activity599': '59.9 两件套餐',
      'color_blue': '蓝色系风格',
      'color_white': '白色梦幻',
      'color_yellow': '明黄活力',
      'color_purple': '紫色优雅'
      // 更多映射...
    };
    
    if (typeMap[type]) {
      this.setData({ title: typeMap[type] });
    }

    this.fetchChannelProducts(true);
  },

  fetchChannelProducts(refresh = false) {
    if (!refresh && !this.data.hasMore) return;
    if (this.data.loading) return;

    this.setData({ loading: true });
    let pageNum = refresh ? 1 : this.data.page + 1;

    // Use specific endpoint logic based on 'type' or just generic get_products with keyword/category
    // For now, let's use the generic products endpoint and pass type as keyword just as a fallback
    app.request('/api/v1/product/products', 'GET', {
      keyword: this.data.type, // Replace this with exact category_id logic if needed
      page: pageNum,
      page_size: 10
    }).then(res => {
      const list = res.data.list || [];
      const total = res.data.total || 0;
      
      this.setData({
        productList: refresh ? list : this.data.productList.concat(list),
        page: pageNum,
        hasMore: this.data.productList.length + list.length < total,
        loading: false
      });
    }).catch(() => {
      this.setData({ loading: false });
    });
  },

  onReachBottom() {
    this.fetchChannelProducts(false);
  },

  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` });
  }
})
