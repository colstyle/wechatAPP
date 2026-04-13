const app = getApp()
const faqData = require('../../data/faq.json')

Page({
  data: {
    messages: [
      { id: 1, role: 'assistant', content: '您好！我是您的智能租衣助手，有什么可以帮您的吗？' }
    ],
    faqs: faqData,
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
  },

  onFaqTap(e) {
    if (this.data.loading) return
    const id = e.currentTarget.dataset.id
    const faq = this.data.faqs.find(f => f.id === id)
    if (!faq) return

    const userMsg = { id: Date.now(), role: 'user', content: faq.question }
    this.setData({
      messages: [...this.data.messages, userMsg],
      lastMessageId: `msg-${userMsg.id}`
    })

    // FAQ 问题直接本地回复，无需调用后端，节省 token
    setTimeout(() => {
      const aiMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: faq.answer
      }
      this.setData({
        messages: [...this.data.messages, aiMsg],
        lastMessageId: `msg-${aiMsg.id}`
      })
    }, 500)
  }
})
