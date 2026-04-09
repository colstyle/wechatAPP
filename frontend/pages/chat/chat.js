const app = getApp()

Page({
  data: {
    messages: [
      { id: 1, role: 'assistant', content: '您好！我是您的智能租衣助手，有什么可以帮您的吗？' }
    ],
    inputValue: '',
    loading: false,
    lastMessageId: ''
  },

  onInput(e) {
    this.setData({ inputValue: e.detail.value })
  },

  onSend() {
    if (!this.data.inputValue || this.data.loading) return

    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: this.data.inputValue
    }

    this.setData({
      messages: [...this.data.messages, userMsg],
      inputValue: '',
      loading: true,
      lastMessageId: `msg-${userMsg.id}`
    })

    // 调用后端 AI 接口
    app.request('/api/ai/chat', 'POST', { message: userMsg.content })
      .then(res => {
        const aiMsg = {
          id: Date.now() + 1,
          role: 'assistant',
          content: res.data.reply
        }
        this.setData({
          messages: [...this.data.messages, aiMsg],
          loading: false,
          lastMessageId: `msg-${aiMsg.id}`
        })
      })
      .catch(err => {
        console.error('AI 聊天失败', err)
        wx.showToast({ title: 'AI 暂时开小差了', icon: 'none' })
        this.setData({ loading: false })
      })
  }
})
