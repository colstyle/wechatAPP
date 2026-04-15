/**
 * 分类与探索 — 店主可编辑的分类配置
 * =============================================
 * 修改说明：
 *   - groups: 左侧导航分组
 *     · id: 唯一标识（英文，不重复）
 *     · name: 左栏显示名称
 *     · emoji: 左栏小图标（emoji字符，可替换）
 *   - items: 每组下的宫格项目
 *     · id: 唯一标识
 *     · name: 宫格显示名称
 *     · emoji: 宫格大图标
 *     · color: 渐变主色（可用CSS颜色）
 *     · page: 跳转的页面路径（相对pages/）
 *     · badge: 角标文字（如'热'/'新'/'折'，不需要则填''）
 * =============================================
 */

module.exports = [
  {
    id: 'service',
    name: '服务咨询',
    emoji: '💬',
    items: [
      {
        id: 'deposit',
        name: '押金及注意事项',
        emoji: '📋',
        color: '#7E8C8D',
        page: '/pages/channel/deposit/deposit',
        badge: ''
      },
      {
        id: 'kefu',
        name: '客服',
        emoji: '🤝',
        color: '#5B7FA6',
        page: '/pages/chat/chat',
        badge: ''
      },
      {
        id: 'photo',
        name: '约拍',
        emoji: '📸',
        color: '#8E6BA8',
        page: '/pages/channel/photo/photo',
        badge: '新'
      },
      {
        id: 'makeup',
        name: '化妆造型',
        emoji: '💄',
        color: '#C5658A',
        page: '/pages/channel/makeup/makeup',
        badge: ''
      }
    ]
  },
  {
    id: 'special',
    name: '特惠活动',
    emoji: '🏷',
    items: [
      {
        id: 'sale999',
        name: '9.9特惠/微瑕',
        emoji: '🔥',
        color: '#E85D5D',
        page: '/pages/channel/sale999/sale999',
        badge: '热'
      },
      {
        id: 'activity599',
        name: '活动59.9二件',
        emoji: '🎉',
        color: '#E87B3A',
        page: '/pages/channel/activity599/activity599',
        badge: '折'
      }
    ]
  },
  {
    id: 'outwear',
    name: '外套开衫',
    emoji: '🧥',
    items: [
      {
        id: 'cardigan',
        name: '开衫/外套',
        emoji: '🧣',
        color: '#8B7355',
        page: '/pages/channel/cardigan/cardigan',
        badge: ''
      }
    ]
  },
  {
    id: 'bycolor',
    name: '按颜色找',
    emoji: '🎨',
    items: [
      {
        id: 'blue',
        name: '蓝色系服装',
        emoji: '💙',
        color: '#4A90D9',
        page: '/pages/channel/color_blue/color_blue',
        badge: ''
      },
      {
        id: 'white',
        name: '白色系服装',
        emoji: '🤍',
        color: '#B0A99A',
        page: '/pages/channel/color_white/color_white',
        badge: ''
      },
      {
        id: 'yellow',
        name: '黄色系服装',
        emoji: '💛',
        color: '#D4A827',
        page: '/pages/channel/color_yellow/color_yellow',
        badge: ''
      },
      {
        id: 'purple',
        name: '紫色系服装',
        emoji: '💜',
        color: '#8E44AD',
        page: '/pages/channel/color_purple/color_purple',
        badge: ''
      },
      {
        id: 'green',
        name: '绿色系服装',
        emoji: '💚',
        color: '#27AE60',
        page: '/pages/channel/color_green/color_green',
        badge: ''
      },
      {
        id: 'pink',
        name: '粉红色系服装',
        emoji: '🩷',
        color: '#E91E8C',
        page: '/pages/channel/color_pink/color_pink',
        badge: '美'
      }
    ]
  },
  {
    id: 'accessory',
    name: '饰品配件',
    emoji: '💍',
    items: [
      {
        id: 'jewelry',
        name: '项链头饰',
        emoji: '📿',
        color: '#C5A059',
        page: '/pages/channel/jewelry/jewelry',
        badge: ''
      },
      {
        id: 'hat_bag',
        name: '帽子包包',
        emoji: '👜',
        color: '#9B7653',
        page: '/pages/channel/hat_bag/hat_bag',
        badge: ''
      },
      {
        id: 'undergarment',
        name: '胸贴/安全裤',
        emoji: '🩲',
        color: '#A0707A',
        page: '/pages/channel/undergarment/undergarment',
        badge: ''
      }
    ]
  }
]
