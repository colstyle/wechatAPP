// components/cp-skeleton/cp-skeleton.js
Component({
  properties: {
    type: { type: String, value: 'rect' }, // rect | circle | line
    width: { type: String, value: '100%' },
    height: { type: String, value: '32rpx' },
    margin: { type: String, value: '0' },
    radius: { type: String, value: '8rpx' },
    animate: { type: Boolean, value: true }
  }
})
