// utils/api.js

const app = getApp()

// 用户相关API
const userApi = {
  // 微信登录
  login: (code) => {
    return app.request('/api/v1/user/login', 'POST', { code })
  },

  // 获取用户信息
  getProfile: () => {
    return app.request('/api/v1/user/profile', 'GET')
  },

  // 更新用户信息
  updateProfile: (data) => {
    return app.request('/api/v1/user/profile', 'POST', data)
  },

  // 获取地址列表
  getAddresses: () => {
    return app.request('/api/v1/user/addresses', 'GET')
  },

  // 创建地址
  createAddress: (data) => {
    return app.request('/api/v1/user/addresses', 'POST', data)
  },

  // 更新地址
  updateAddress: (id, data) => {
    return app.request(`/api/v1/user/addresses/${id}`, 'PUT', data)
  },

  // 删除地址
  deleteAddress: (id) => {
    return app.request(`/api/v1/user/addresses/${id}`, 'DELETE')
  },

  // 设置默认地址
  setDefaultAddress: (id) => {
    return app.request(`/api/v1/user/addresses/${id}/default`, 'POST')
  }
}

// 商品相关API
const productApi = {
  // 获取分类列表
  getCategories: (parentId = 0) => {
    return app.request(`/api/v1/product/categories?parent_id=${parentId}`, 'GET')
  },

  // 获取品牌列表
  getBrands: () => {
    return app.request('/api/v1/product/brands', 'GET')
  },

  // 获取品牌详情
  getBrand: (id) => {
    return app.request(`/api/v1/product/brands/${id}`, 'GET')
  },

  // 获取商品列表
  getProducts: (params) => {
    return app.request('/api/v1/product/products', 'GET', params)
  },

  // 获取热门商品
  getHotProducts: (limit = 10, params = {}) => {
    return app.request(`/api/v1/product/products/hot?limit=${limit}`, 'GET', params)
  },

  // 获取新品商品
  getNewProducts: (limit = 10, params = {}) => {
    return app.request(`/api/v1/product/products/new?limit=${limit}`, 'GET', params)
  },

  // 获取商品详情
  getProduct: (id) => {
    return app.request(`/api/v1/product/products/${id}`, 'GET')
  },

  // 获取搭配列表
  getOutfits: (limit = 20) => {
    return app.request(`/api/v1/product/outfits?limit=${limit}`, 'GET')
  },

  // 添加收藏
  addFavorite: (productId) => {
    return app.request(`/api/v1/product/favorites/${productId}`, 'POST')
  },

  // 取消收藏
  removeFavorite: (productId) => {
    return app.request(`/api/v1/product/favorites/${productId}`, 'DELETE')
  },

  // 获取收藏列表
  getFavorites: (page = 1, pageSize = 20) => {
    return app.request(`/api/v1/product/favorites?page=${page}&page_size=${pageSize}`, 'GET')
  }
}

// 订单相关API
const orderApi = {
  // 创建订单
  createOrder: (data) => {
    return app.request('/api/v1/order/orders', 'POST', data)
  },

  // 获取订单列表
  getOrders: (params) => {
    return app.request('/api/v1/order/orders', 'GET', params)
  },

  // 获取订单详情
  getOrder: (id) => {
    return app.request(`/api/v1/order/orders/${id}`, 'GET')
  },

  // 支付订单
  payOrder: (id) => {
    return app.request(`/api/v1/order/orders/${id}/pay`, 'POST')
  },

  // 取衣确认
  pickupOrder: (id) => {
    return app.request(`/api/v1/order/orders/${id}/pickup`, 'POST', { remark: '用户已取衣' })
  },

  // 取消订单
  cancelOrder: (id) => {
    return app.request(`/api/v1/order/orders/${id}/cancel`, 'POST')
  },

  // 确认收货
  receiveOrder: (id) => {
    return app.request(`/api/v1/order/orders/${id}/receive`, 'POST')
  },

  // 申请归还
  returnOrder: (id, remark) => {
    return app.request(`/api/v1/order/orders/${id}/return`, 'POST', { remark })
  }
}

// 订阅相关API
const subscriptionApi = {
  // 获取套餐列表
  getPackages: () => {
    return app.request('/api/v1/subscription/packages', 'GET')
  },

  // 获取套餐详情
  getPackage: (id) => {
    return app.request(`/api/v1/subscription/packages/${id}`, 'GET')
  },

  // 购买订阅
  buySubscription: (packageId) => {
    return app.request('/api/v1/subscription/subscribe', 'POST', { package_id: packageId })
  },

  // 获取订阅列表
  getSubscriptions: (params) => {
    return app.request('/api/v1/subscription/subscriptions', 'GET', params)
  },

  // 获取激活中的订阅
  getActiveSubscription: () => {
    return app.request('/api/v1/subscription/subscriptions/active', 'GET')
  },

  // 取消订阅
  cancelSubscription: (id) => {
    return app.request(`/api/subscription/subscriptions/${id}/cancel`, 'POST')
  },

  // 使用订阅创建订单
  createSubscriptionOrder: (data) => {
    return app.request('/api/v1/subscription/orders/subscription', 'POST', data)
  }
}

// 预约相关API
const appointmentApi = {
  // 创建预约
  createAppointment: (data) => {
    return app.request('/api/v1/appointment/appointments', 'POST', data)
  },

  // 获取预约列表
  getAppointments: (params) => {
    return app.request('/api/v1/appointment/appointments', 'GET', params)
  },

  // 获取预约详情
  getAppointment: (id) => {
    return app.request(`/api/v1/appointment/appointments/${id}`, 'GET')
  },

  // 更新预约
  updateAppointment: (id, data) => {
    return app.request(`/api/v1/appointment/appointments/${id}`, 'PUT', data)
  },

  // 取消预约
  cancelAppointment: (id) => {
    return app.request(`/api/v1/appointment/appointments/${id}`, 'DELETE')
  },

  // 获取可预约时间段
  getAvailableTimes: (productId, date) => {
    return app.request(`/api/v1/appointment/appointments/available-times?product_id=${productId}&appointment_date=${date}`, 'GET')
  }
}

// 评价相关API
const reviewApi = {
  // 创建评价
  createReview: (data) => {
    return app.request('/api/v1/review/reviews', 'POST', data)
  },

  // 获取商品评价列表
  getReviews: (productId, page = 1, pageSize = 20) => {
    return app.request(`/api/v1/review/reviews?product_id=${productId}&page=${page}&page_size=${pageSize}`, 'GET')
  },

  // 获取评价详情
  getReview: (id) => {
    return app.request(`/api/v1/review/reviews/${id}`, 'GET')
  },

  // 获取我的评价列表
  getMyReviews: (page = 1, pageSize = 20) => {
    return app.request(`/api/v1/review/reviews/my?page=${page}&page_size=${pageSize}`, 'GET')
  },

  // 删除评价
  deleteReview: (id) => {
    return app.request(`/api/v1/review/reviews/${id}`, 'DELETE')
  }
}

// 店主管理相关API
const adminApi = {
  // 获取全量订单
  getOrders: (params) => {
    return app.request('/api/v1/admin/orders', 'GET', params)
  },

  // 获取订单详情
  getOrder: (id) => {
    return app.request(`/api/v1/admin/orders/${id}`, 'GET')
  },

  // 退押金
  refundOrder: (orderId, amount, reason) => {
    return app.request('/api/v1/admin/refund', 'POST', { order_id: orderId, amount, reason })
  },

  // 扣押金
  deductDeposit: (orderId, amount, reason) => {
    return app.request('/api/v1/admin/deduct', 'POST', { order_id: orderId, amount, reason })
  },

  // 修改订单商品 (换款)
  updateOrderItems: (orderId, items) => {
    return app.request('/api/v1/admin/update-items', 'POST', { order_id: orderId, items })
  },

  // 套餐商品管理
  getPackageProducts: (params) => {
    return app.request('/api/v1/admin/package/products', 'GET', params)
  },

  setPackageEligible: (productId, isPackageEligible) => {
    return app.request(`/api/v1/admin/package/products/${productId}`, 'PUT', { is_package_eligible: !!isPackageEligible })
  },

  // === 服装库存管理 ===
  createProduct: (data) => {
    return app.request('/api/v1/product/products', 'POST', data)
  },
  
  updateProduct: (id, data) => {
    return app.request(`/api/v1/product/products/${id}`, 'PUT', data)
  },

  deleteProduct: (id) => {
    return app.request(`/api/v1/product/products/${id}`, 'DELETE')
  }
}

module.exports = {
  userApi,
  productApi,
  orderApi,
  subscriptionApi,
  appointmentApi,
  reviewApi,
  adminApi
}
