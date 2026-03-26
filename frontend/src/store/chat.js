import { defineStore } from 'pinia'
import { useUserStore } from './user'
import { ref } from 'vue'
import { wsBaseURL } from '../utils/request'
import request from '../utils/request'

export const useChatStore = defineStore('chat', () => {
  const ws = ref(null)
  const messages = ref({})
  const notifications = ref([])
  const unreadMessagesCount = ref(0)
  const unreadNotificationsCount = ref(0)
  let heartbeatTimer = null
  let reconnectTimer = null

  function connectWs() {
    const userStore = useUserStore()
    if (!userStore.token || ws.value?.readyState === WebSocket.OPEN) return

    try {
      const wsUrl = import.meta.env.VITE_WS_URL || `ws://127.0.0.1:8001/api/v1/chat/ws/${userStore.token}`
      ws.value = new WebSocket(wsUrl)

      ws.value.onopen = () => {
        startHeartbeat()
        stopReconnectTimer()
      }

      ws.value.onmessage = event => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'chat') {
            const selfId = userStore.user?.id
            const friendId = data.sender_id === selfId ? data.receiver_id : data.sender_id
            if (!friendId) return
            if (!messages.value[friendId]) messages.value[friendId] = []
            const exists = messages.value[friendId].some(m => m.id === data.id)
            if (!exists) {
              messages.value[friendId].push({
                ...data,
                isMe: data.sender_id === selfId
              })
              if (data.sender_id !== selfId) {
                unreadMessagesCount.value++
              }
            }
          } else if (data.type === 'ack') {
            const selfId = userStore.user?.id
            for (const friendId in messages.value) {
              const pending = messages.value[friendId].findIndex(
                m => m.temp_id === data.temp_id && m.isMe && !m.id
              )
              if (pending !== -1) {
                messages.value[friendId][pending].id = data.id
                messages.value[friendId][pending].created_at = data.created_at
                break
              }
            }
          } else if (data.type === 'notification') {
            notifications.value.push(data)
            unreadNotificationsCount.value++
          } else if (data.type === 'error') {
            console.error('Chat error:', data.content)
          }
        } catch (e) {
          console.error('Failed to parse message', e)
        }
      }

      ws.value.onclose = () => {
        stopHeartbeat()
        ws.value = null
        if (userStore.token) {
          startReconnectTimer()
        }
      }

      ws.value.onerror = error => {
        console.error('WebSocket error', error)
      }
    } catch (e) {
      console.error('Failed to connect WebSocket', e)
      startReconnectTimer()
    }
  }

  function startHeartbeat() {
    stopHeartbeat()
    heartbeatTimer = setInterval(() => {
      if (ws.value && ws.value.readyState === WebSocket.OPEN) {
        ws.value.send(JSON.stringify({ action: 'heartbeat' }))
        updateExp()
      }
    }, 60000)
  }

  function stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  function startReconnectTimer() {
    stopReconnectTimer()
    reconnectTimer = setTimeout(() => {
      connectWs()
    }, 3000)
  }

  function stopReconnectTimer() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  function updateExp() {
    request.post('/auth/heartbeat').catch(() => {})
  }

  function sendMessage(receiverId, content) {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      const userStore = useUserStore()
      const tempId = `temp_${Date.now()}_${Math.random().toString(36).slice(2)}`
      if (!messages.value[receiverId]) messages.value[receiverId] = []
      messages.value[receiverId].push({
        type: 'chat',
        temp_id: tempId,
        sender_id: userStore.user?.id,
        receiver_id: receiverId,
        content,
        created_at: new Date().toISOString(),
        isMe: true
      })
      ws.value.send(JSON.stringify({
        action: 'send_message',
        receiver_id: receiverId,
        content,
        temp_id: tempId
      }))
      return true
    }
    return false
  }

  function disconnect() {
    stopHeartbeat()
    stopReconnectTimer()
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
  }

  function clearUnreadMessages() {
    unreadMessagesCount.value = 0
  }

  function clearUnreadNotifications() {
    unreadNotificationsCount.value = 0
  }

  return {
    ws,
    messages,
    notifications,
    unreadMessagesCount,
    unreadNotificationsCount,
    connectWs,
    disconnect,
    sendMessage,
    clearUnreadMessages,
    clearUnreadNotifications
  }
})
