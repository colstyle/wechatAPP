import os

base_dir = r'e:\AIProjects\202604@wechatAPP\frontend\components\cp-empty'
os.makedirs(base_dir, exist_ok=True)

# index.js
with open(os.path.join(base_dir, 'cp-empty.js'), 'w', encoding='utf-8') as f:
    f.write('Component({\n  properties: {\n    text: { type: String, value: "暂无数据" },\n    subText: { type: String, value: "" }\n  }\n})')

# index.wxml
with open(os.path.join(base_dir, 'cp-empty.wxml'), 'w', encoding='utf-8') as f:
    f.write('''<view class="cp-empty">
  <view class="empty-icon"><view class="circle"></view><view class="line"></view></view>
  <view class="empty-text">{{text}}</view>
  <view class="empty-sub" wx:if="{{subText}}">{{subText}}</view>
</view>''')

# index.wxss
with open(os.path.join(base_dir, 'cp-empty.wxss'), 'w', encoding='utf-8') as f:
    f.write('''.cp-empty { padding: 120rpx 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.empty-icon { position: relative; width: 100rpx; height: 100rpx; margin-bottom: 24rpx; }
.empty-icon .circle { width: 80rpx; height: 80rpx; border: 4rpx solid #EAEAEA; border-radius: 50%; position: absolute; top: 0; left: 10rpx; }
.empty-icon .line { width: 40rpx; height: 4rpx; background: #C5A059; position: absolute; bottom: 10rpx; right: 10rpx; transform: rotate(45deg); padding:0; border-radius:4rpx;}
.empty-text { font-size: 28rpx; color: #999; margin-bottom: 8rpx; }
.empty-sub { font-size: 24rpx; color: #BBB; }
''')

# index.json
with open(os.path.join(base_dir, 'cp-empty.json'), 'w', encoding='utf-8') as f:
    f.write('{\n  "component": true\n}')

print('cp-empty component created.')
