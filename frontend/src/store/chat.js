import { defineStore } from 'pinia'
import { useUserStore } from './user'
import { ref } from 'vue'
import { wsBaseURL } from '../utils/request'

export const useChatStore = defineStore('chat', () => {
  const ws = ref(null)
  const messages = ref({})
  const notifications = ref([])

  function connectWs() {
    const userStore = useUserStore()
    if (!userStore.token || ws.value?.readyState === WebSocket.OPEN) return

    ws.value = new WebSocket(`${wsBaseURL}/api/v1/chat/ws/${userStore.token}`)

    ws.value.onopen = () => {}

    ws.value.onmessage = event => {
      const data = JSON.parse(event.data)
      if (data.type === 'chat') {
        const friendId = data.sender_id
        if (!messages.value[friendId]) {
          messages.value[friendId] = []
        }
        messages.value[friendId].push(data)
      } else if (data.type === 'notification') {
        notifications.value.push(data)
      }
    }

    ws.value.onclose = () => {
      if (userStore.token) {
        setTimeout(() => connectWs(), 3000)
      }
    }
  }

  function sendMessage(receiverId, content) {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify({
        action: 'send_message',
        receiver_id: receiverId,
        content: content
      }))
      if (!messages.value[receiverId]) messages.value[receiverId] = []
      messages.value[receiverId].push({ sender_id: useUserStore().user.id, content, isMe: true })
    }
  }

  function disconnect() {
    ws.value?.close()
    ws.value = null
  }

  return { ws, messages, notifications, connectWs, sendMessage, disconnect }
})
