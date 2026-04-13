import os

base_dir = r'e:\AIProjects\202604@wechatAPP\frontend\components\cp-countdown'
os.makedirs(base_dir, exist_ok=True)

# index.js
with open(os.path.join(base_dir, 'cp-countdown.js'), 'w', encoding='utf-8') as f:
    f.write('''Component({
  properties: {
    hoursLeft: { type: Number, value: 0 },
    totalHours: { type: Number, value: 24 }
  },
  data: { degrees: 0 },
  observers: {
    'hoursLeft, totalHours': function(h, t) {
      if (t <= 0) return;
      let p = h / t;
      if (p < 0) p = 0;
      if (p > 1) p = 1;
      this.setData({ degrees: parseInt(360 * p) });
    }
  }
})''')

# index.wxml
with open(os.path.join(base_dir, 'cp-countdown.wxml'), 'w', encoding='utf-8') as f:
    f.write('''<view class="cp-countdown">
  <view class="circle-wrap">
    <view class="circle-left" style="transform: rotate({{degrees > 180 ? degrees - 180 : 0}}deg);"></view>
    <view class="circle-right" style="transform: rotate({{degrees > 180 ? 180 : degrees}}deg);"></view>
    <view class="circle-inner">
      <text class="num">{{hoursLeft}}</text>
      <text class="unit">h</text>
    </view>
  </view>
</view>''')

# index.wxss
with open(os.path.join(base_dir, 'cp-countdown.wxss'), 'w', encoding='utf-8') as f:
    f.write('''.cp-countdown { display: inline-block; position: relative; width: 80rpx; height: 80rpx; }
.circle-wrap { width: 100%; height: 100%; background: #F0F0F0; border-radius: 50%; position: relative; }
.circle-right, .circle-left { width: 50%; height: 100%; position: absolute; top: 0; transform-origin: right center; background: #C5A059; border-radius: 80rpx 0 0 80rpx; left: 0; }
.circle-right { transform-origin: left center; border-radius: 0 80rpx 80rpx 0; left: 50%; }
.circle-inner { width: 68rpx; height: 68rpx; background: #fff; border-radius: 50%; position: absolute; top: 6rpx; left: 6rpx; display: flex; align-items: baseline; justify-content: center; z-index: 10; padding-top: 14rpx; box-sizing: border-box; }
.num { font-size: 28rpx; font-weight: bold; color: #C5A059; }
.unit { font-size: 18rpx; color: #C5A059; margin-left: 2rpx; }
''')

# index.json
with open(os.path.join(base_dir, 'cp-countdown.json'), 'w', encoding='utf-8') as f:
    f.write('{\n  "component": true\n}')

print('cp-countdown component created.')
