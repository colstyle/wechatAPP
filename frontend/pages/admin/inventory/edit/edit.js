// pages/admin/inventory/edit/edit.js
const app = getApp()
const { productApi, adminApi } = require('../../../../utils/api')

Page({
  data: {
    id: null,
    formData: {
      name: '',
      category_id: '',
      brand_id: '',
      cover_image: '',
      images: [],
      description: '',
      deposit: '',
      daily_rent: '',
      single_rent: '',
      stock: '1',
      is_hot: false,
      is_new: false,
      is_package_eligible: false,
      status: 1
    },
    submitting: false
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ id: parseInt(options.id) })
      this.loadProduct(options.id)
    }
  },

  loadProduct(id) {
    wx.showLoading({ title: '加载中' })
    productApi.getProduct(id).then(res => {
      wx.hideLoading()
      if (res.code === 0) {
        const p = res.data
        // 将封面图加入 images 第一个，如果 images 为空
        let images = p.images || []
        if (images.length === 0 && p.cover_image) {
          images = [p.cover_image]
        }
        
        this.setData({
          formData: {
            name: p.name,
            category_id: String(p.category_id),
            brand_id: String(p.brand_id),
            cover_image: p.cover_image,
            images: images,
            description: p.description || '',
            deposit: String(p.deposit),
            daily_rent: String(p.daily_rent),
            single_rent: String(p.single_rent || ''),
            stock: String(p.stock),
            is_hot: !!p.is_hot,
            is_new: !!p.is_new,
            is_package_eligible: !!p.is_package_eligible,
            status: p.status !== undefined ? p.status : 1
          }
        })
      }
    }).catch(() => {
      wx.hideLoading()
      wx.showToast({ title: '加载商品失败', icon: 'none' })
    })
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({
      [`formData.${field}`]: e.detail.value
    })
  },

  onSwitch(e) {
    const field = e.currentTarget.dataset.field
    let val = e.detail.value
    if (field === 'status') {
      val = val ? 1 : 0
    }
    this.setData({
      [`formData.${field}`]: val
    })
  },

  onChooseImage() {
    const remain = 5 - this.data.formData.images.length
    if (remain <= 0) {
      wx.showToast({ title: '最多上传5张图片', icon: 'none' })
      return
    }
    wx.chooseMedia({
      count: remain,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFiles = res.tempFiles
        this.uploadImages(tempFiles)
      }
    })
  },

  uploadImages(tempFiles) {
    wx.showLoading({ title: '上传中', mask: true })
    const promises = tempFiles.map(file => app.uploadImage(file.tempFilePath))
    
    Promise.all(promises).then(urls => {
      wx.hideLoading()
      const newImages = [...this.data.formData.images, ...urls]
      this.setData({
        'formData.images': newImages
      })
    }).catch(err => {
      wx.hideLoading()
      wx.showToast({ title: '图片上传失败', icon: 'none' })
    })
  },

  onRemoveImage(e) {
    const index = e.currentTarget.dataset.index
    const images = this.data.formData.images
    images.splice(index, 1)
    this.setData({
      'formData.images': images
    })
  },

  onSubmit() {
    const fd = this.data.formData
    // 校验
    if (!fd.name.trim()) return wx.showToast({ title: '请输入商品名称', icon: 'none' })
    if (!fd.category_id) return wx.showToast({ title: '请输入分类ID', icon: 'none' })
    if (!fd.brand_id) return wx.showToast({ title: '请输入品牌ID', icon: 'none' })
    if (!fd.daily_rent) return wx.showToast({ title: '请输入日租金', icon: 'none' })
    if (!fd.deposit) return wx.showToast({ title: '请输入押金', icon: 'none' })
    if (fd.images.length === 0) return wx.showToast({ title: '请至少上传一张图片', icon: 'none' })

    const payload = {
      name: fd.name.trim(),
      category_id: parseInt(fd.category_id) || 0,
      brand_id: parseInt(fd.brand_id) || 0,
      cover_image: fd.images[0], // 首张图作为封面
      images: fd.images,
      description: fd.description.trim(),
      deposit: parseFloat(fd.deposit) || 0,
      daily_rent: parseFloat(fd.daily_rent) || 0,
      single_rent: parseFloat(fd.single_rent) || 0,
      month_card_rent: 0,
      stock: parseInt(fd.stock) || 1,
      sizes: [],
      colors: [],
      is_hot: !!fd.is_hot,
      is_new: !!fd.is_new,
      is_package_eligible: !!fd.is_package_eligible,
      status: fd.status
    }

    this.setData({ submitting: true })

    const requestObj = this.data.id 
      ? adminApi.updateProduct(this.data.id, payload)
      : adminApi.createProduct(payload)

    requestObj.then(res => {
      this.setData({ submitting: false })
      if (res.code === 0) {
        wx.showToast({ title: '保存成功', icon: 'success' })
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      }
    }).catch(err => {
      this.setData({ submitting: false })
      wx.showToast({ title: err.message || '保存失败', icon: 'none' })
    })
  }
})