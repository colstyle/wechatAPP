Component({
  properties: {
    title: { type: String, value: '暂无记录' },
    description: { type: String, value: '这里还没有发现任何内容' },
    actionText: { type: String, value: '' },
    padding: { type: Boolean, value: false }
  },
  methods: {
    onActionTap() {
      this.triggerEvent('action')
    }
  }
})