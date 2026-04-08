// utils/util.js

const formatTime = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()

  return `${[year, month, day].map(formatNumber).join('/')} ${[hour, minute, second].map(formatNumber).join(':')}`
}

const formatDate = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()

  return `${[year, month, day].map(formatNumber).join('-')}`
}

const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : `0${n}`
}

// 格式化价格
const formatPrice = price => {
  return '¥' + parseFloat(price || 0).toFixed(2)
}

// 格式化数量
const formatCount = count => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万'
  } else if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'k'
  }
  return count
}

// 订单状态文本
const orderStatusMap = {
  0: '待支付',
  1: '待发货',
  2: '租赁中',
  3: '待归还',
  4: '已归还',
  5: '已取消',
  6: '已完成'
}

const orderStatusClassMap = {
  0: 'text-warning',
  1: 'text-primary',
  2: 'text-success',
  3: 'text-warning',
  4: 'text-info',
  5: 'text-muted',
  6: 'text-success'
}

// 租赁类型文本
const rentalTypeMap = {
  1: '按天租赁',
  2: '单次租赁',
  3: '订阅租赁'
}

// 预约状态文本
const appointmentStatusMap = {
  0: '待确认',
  1: '已确认',
  2: '已完成',
  3: '已取消'
}

// 节流函数
const throttle = (fn, delay) => {
  let timer = null
  return function(...args) {
    if (timer) return
    timer = setTimeout(() => {
      fn.apply(this, args)
      timer = null
    }, delay)
  }
}

// 防抖函数
const debounce = (fn, delay) => {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

// 深拷贝
const deepClone = obj => {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj)
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (typeof obj === 'object') {
    const clone = {}
    for (let key in obj) {
      if (obj.hasOwnProperty(key)) {
        clone[key] = deepClone(obj[key])
      }
    }
    return clone
  }
}

// 生成唯一ID
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

// URL参数解析
const parseUrlParams = url => {
  const params = {}
  const queryString = url.split('?')[1]
  if (!queryString) return params

  queryString.split('&').forEach(item => {
    const [key, value] = item.split('=')
    params[decodeURIComponent(key)] = decodeURIComponent(value)
  })
  return params
}

// 对象转URL参数
const objectToUrlParams = obj => {
  return Object.keys(obj)
    .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(obj[key]))
    .join('&')
}

// 本地存储封装
const storage = {
  get(key) {
    try {
      const value = wx.getStorageSync(key)
      return value ? JSON.parse(value) : null
    } catch (e) {
      return null
    }
  },
  set(key, value) {
    try {
      wx.setStorageSync(key, JSON.stringify(value))
      return true
    } catch (e) {
      return false
    }
  },
  remove(key) {
    wx.removeStorageSync(key)
  },
  clear() {
    wx.clearStorageSync()
  }
}

// 星星生成函数 - 用于模板中显示评分
const getStarsString = (rating) => {
  if (!rating || rating < 1) return ''
  const stars = '⭐'.repeat(rating)
  return stars
}

// WXS 工具函数 - 用于模板中调用
const getStars = (rating) => {
  var stars = '⭐'
  for (var i = 1; i < rating; i++) {
    stars += '⭐'
  }
  return stars
}

module.exports = {
  formatTime,
  formatDate,
  formatNumber,
  formatPrice,
  formatCount,
  orderStatusMap,
  orderStatusClassMap,
  rentalTypeMap,
  appointmentStatusMap,
  throttle,
  debounce,
  deepClone,
  generateId,
  parseUrlParams,
  objectToUrlParams,
  storage,
  getStarsString,
  // WXS 导出
  getStars
}
