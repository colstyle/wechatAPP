// components/cp-product-card/cp-product-card.js
Component({
  properties: {
    product: { type: Object, value: {} }
  },

  data: {
    loading: true,
    loaded: false
  },

  methods: {
    onTap() {
      this.triggerEvent('tap', { id: this.properties.product.id })
    },

    onImgLoad() {
      this.setData({ loading: false, loaded: true })
    },

    onImgError() {
      this.setData({ loading: false, loaded: true })
    }
  }
})
