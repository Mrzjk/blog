<template>
  <div class="chat-page">
    <div class="chat-container">
      <!-- Sidebar / Friend List -->
      <aside class="friend-list">
        <div class="friend-list__top">
          <h3 class="section-title">好友列表</h3>
        </div>
        
        <div class="friend-list-scroll">
          <div v-if="friends.length" class="friend-items">
            <button
              v-for="friend in friends"
              :key="friend.id"
              class="friend-item"
              :class="{ active: activeFriend?.id === friend.id }"
              @click="activeFriend = friend"
            >
              <div class="flex items-center gap-3 w-full">
                <div class="relative">
                  <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-accent to-accent-purple text-white flex items-center justify-center font-bold text-lg shadow-sm">
                    {{ friend.username.charAt(0).toUpperCase() }}
                  </div>
                  <span v-if="friend.online" class="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-green-500 border-2 border-card rounded-full shadow-[0_0_8px_rgba(34,197,94,0.5)]"></span>
                </div>
                <div class="friend-info">
                  <div class="friend-info-top">
                    <strong class="truncate text-[15px]">{{ friend.username }}</strong>
                    <span class="muted time-small whitespace-nowrap" v-if="friend.last_message_time">{{ formatTime(friend.last_message_time) }}</span>
                  </div>
                  <div class="friend-info-bottom">
                    <span class="muted truncate-msg">{{ friend.last_message || '暂无消息' }}</span>
                    <el-badge v-if="friend.unread_count > 0" :value="friend.unread_count" class="chat-badge" />
                  </div>
                </div>
              </div>
            </button>
          </div>
          <el-empty v-else description="暂无好友，去个人主页搜索添加吧" class="opacity-50" :image-size="80" />
        </div>
      </aside>

      <!-- Main Chat Area -->
      <main class="chat-box" v-if="activeFriend">
        <header class="chat-header">
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-accent to-accent-purple text-white flex items-center justify-center text-lg font-bold shadow-md">
              {{ activeFriend.username.charAt(0).toUpperCase() }}
            </div>
            <div>
              <h3 class="text-lg font-bold m-0 leading-tight">{{ activeFriend.username }}</h3>
              <span class="text-xs flex items-center gap-1.5 mt-0.5" :class="activeFriend.online ? 'text-green-500' : 'text-muted'">
                <span class="w-2 h-2 rounded-full" :class="activeFriend.online ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-gray-500'"></span>
                {{ activeFriend.online ? '在线' : '离线' }}
              </span>
            </div>
          </div>
          <div class="flex gap-2">
            <el-dropdown trigger="click" @command="handleCommand">
              <el-button circle plain>
                <el-icon><More /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="clear_history">
                    <el-icon><Delete /></el-icon> 清空聊天记录
                  </el-dropdown-item>
                  <el-dropdown-item command="delete_session" divided class="text-danger">
                    <el-icon><Close /></el-icon> 删除会话
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </header>
        
        <div class="messages-container" ref="messagesContainer">
          <div class="messages-inner">
            <div class="text-center my-6">
              <span class="text-xs text-muted bg-tertiary px-3 py-1 rounded-full border border-border">这是您与 {{ activeFriend.username }} 的聊天记录</span>
            </div>
            
            <div
              v-for="(msg, index) in currentMessages"
              :key="index"
              class="message-row"
              :class="{ 'message-row--self': msg.isMe }"
            >
              <div class="message-avatar hidden md:flex" v-if="!msg.isMe">
                <div class="w-8 h-8 rounded-md bg-gradient-to-br from-accent to-accent-purple text-white flex items-center justify-center font-bold text-xs shadow-sm">
                  {{ activeFriend.username.charAt(0).toUpperCase() }}
                </div>
              </div>
              
              <div class="message-content">
                <div class="message-meta" v-if="!msg.isMe">
                  <span class="font-medium text-sm text-primary">{{ activeFriend.username }}</span>
                  <span class="text-xs text-muted ml-2">{{ formatTime(msg.created_at || Date.now()) }}</span>
                </div>
                <div class="message-meta justify-end" v-else>
                  <span class="text-xs text-muted mr-2">{{ formatTime(msg.created_at || Date.now()) }}</span>
                  <span class="font-medium text-sm text-primary">我</span>
                </div>
                
                <div class="message-bubble group relative">
                  <p class="m-0 whitespace-pre-wrap break-words leading-relaxed">{{ msg.content }}</p>
                  
                  <!-- Delete Action -->
                  <div class="absolute top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity"
                       :class="msg.isMe ? '-left-10' : '-right-10'">
                    <el-button 
                      type="danger" 
                      circle 
                      plain 
                      size="small"
                      class="!p-1.5"
                      @click="deleteSingleMessage(msg)"
                      title="删除单条消息"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
              
              <div class="message-avatar hidden md:flex" v-if="msg.isMe">
                <div class="w-8 h-8 rounded-md bg-tertiary border border-border text-primary flex items-center justify-center font-bold text-xs">
                  我
                </div>
              </div>
            </div>
          </div>
          <el-empty v-if="!currentMessages.length" description="打个招呼吧" :image-size="100" class="mt-20 opacity-50" />
        </div>
        
        <div class="input-wrapper">
          <div class="input-container glass-input">
            <el-input
              v-model="inputMsg"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 6 }"
              resize="none"
              placeholder="给好友发送消息..."
              @keyup.enter.exact.prevent="send"
              class="gpt-input"
            />
            <div class="input-actions">
              <el-button 
                type="primary" 
                class="send-btn" 
                :disabled="!inputMsg.trim()"
                @click="send"
              >
                <el-icon><Promotion /></el-icon>
              </el-button>
            </div>
          </div>
          <p class="input-hint text-xs text-muted text-center mt-2 font-mono">按 Enter 发送，Shift + Enter 换行</p>
        </div>
      </main>
      
      <main v-else class="empty-chat flex flex-col items-center justify-center bg-card/50">
        <div class="w-24 h-24 mb-6 rounded-full bg-tertiary border border-border flex items-center justify-center text-4xl text-muted shadow-inner">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <h2 class="text-2xl font-bold text-primary mb-2">Trae Chat</h2>
        <p class="text-muted text-sm max-w-sm text-center">选择左侧好友开始聊天</p>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useChatStore } from '../store/chat'
import { useUserStore } from '../store/user'
import request from '../utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { More, Promotion, ChatDotRound, Delete, Close } from '@element-plus/icons-vue'

const chatStore = useChatStore()
const userStore = useUserStore()
const friends = ref([])
const activeFriend = ref(null)
const inputMsg = ref('')
const messagesContainer = ref(null)

const currentMessages = computed(() => {
  if (!activeFriend.value) {
    return []
  }
  return chatStore.messages[activeFriend.value.id] || []
})

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(currentMessages, (newMessages) => {
  scrollToBottom()
  
  // Update local friend list last message
  if (activeFriend.value && newMessages.length > 0) {
    const lastMsg = newMessages[newMessages.length - 1]
    const friend = friends.value.find(f => f.id === activeFriend.value.id)
    if (friend) {
      friend.last_message = lastMsg.content
      friend.last_message_time = lastMsg.created_at
    }
  }
}, { deep: true })

const fetchFriends = async () => {
  try {
    const { data } = await request.get('/chat/friends')
    friends.value = data
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '获取好友失败')
  }
}

const fetchMessages = async (friendId) => {
  try {
    const { data } = await request.get(`/chat/messages/${friendId}`)
    chatStore.messages[friendId] = data.map(msg => ({
      ...msg,
      isMe: msg.sender_id === userStore.user.id
    }))
    
    // Clear local unread count for this friend
    const friend = friends.value.find(f => f.id === friendId)
    if (friend) {
      friend.unread_count = 0
    }
  } catch (e) {
    console.error('获取消息失败', e)
  }
}

const formatTime = (timeStr) => {
  const date = new Date(timeStr)
  return `${date.getMonth() + 1}-${date.getDate()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const deleteSingleMessage = async (msg) => {
  try {
    await request.delete(`/chat/messages/single/${msg.id}`)
    
    // Remove from local store
    if (activeFriend.value) {
      chatStore.messages[activeFriend.value.id] = chatStore.messages[activeFriend.value.id].filter(m => m.id !== msg.id)
      
      // Update last message in friend list if we deleted the last one
      const currentMsgs = chatStore.messages[activeFriend.value.id]
      const friend = friends.value.find(f => f.id === activeFriend.value.id)
      if (friend) {
        if (currentMsgs.length > 0) {
          const newLastMsg = currentMsgs[currentMsgs.length - 1]
          friend.last_message = newLastMsg.content
          friend.last_message_time = newLastMsg.created_at
        } else {
          friend.last_message = null
          friend.last_message_time = null
        }
      }
    }
    
    ElMessage.success('已删除单条消息')
  } catch (e) {
    ElMessage.error('删除消息失败')
  }
}

const handleCommand = async (command) => {
  if (!activeFriend.value) return
  
  if (command === 'clear_history') {
    try {
      await ElMessageBox.confirm('确定要清空与该好友的聊天记录吗？清空后不可恢复（对方的记录不受影响）。', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })
      await request.delete(`/chat/messages/${activeFriend.value.id}`)
      chatStore.messages[activeFriend.value.id] = []
      ElMessage.success('聊天记录已清空')
      fetchFriends() // Refresh last message in list
    } catch (e) {
      if (e !== 'cancel') {
        ElMessage.error('清空失败')
      }
    }
  } else if (command === 'delete_session') {
    try {
      await ElMessageBox.confirm('确定要删除与该好友的会话吗？这将清空记录并在列表中隐藏（对方不受影响）。', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })
      await request.delete(`/chat/messages/${activeFriend.value.id}`)
      chatStore.messages[activeFriend.value.id] = []
      activeFriend.value = null
      ElMessage.success('会话已删除')
      fetchFriends() // Refresh list to remove from history (since last message is gone)
    } catch (e) {
      if (e !== 'cancel') {
        ElMessage.error('删除失败')
      }
    }
  }
}

watch(activeFriend, (newFriend) => {
  if (newFriend) {
    fetchMessages(newFriend.id)
    scrollToBottom()
  }
})

onMounted(() => {
  chatStore.connectWs()
  fetchFriends()
  chatStore.clearUnreadMessages()
})

onUnmounted(() => {
  chatStore.disconnect()
})

const send = () => {
  if (!inputMsg.value.trim() || !activeFriend.value) return
  chatStore.sendMessage(activeFriend.value.id, inputMsg.value)
  inputMsg.value = ''
}
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 100px);
  padding: 20px;
  max-width: 1440px;
  margin: 0 auto;
}

.chat-container {
  display: flex;
  height: 100%;
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.friend-list {
  width: 320px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
  background: rgba(22, 27, 34, 0.5);
  flex-shrink: 0;
  height: 100%;
}

.friend-list-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px 16px;
  /* Add custom scrollbar for friend list */
  scrollbar-width: thin;
  scrollbar-color: rgba(56, 189, 248, 0.2) transparent;
}

.friend-list-scroll::-webkit-scrollbar {
  width: 4px;
}

.friend-list-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.friend-list-scroll::-webkit-scrollbar-thumb {
  background: rgba(56, 189, 248, 0.2);
  border-radius: 10px;
}

.friend-list-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(56, 189, 248, 0.5);
}

.friend-list__top {
  padding: 20px 20px 10px;
}

.friend-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 12px;
  border: 1px solid transparent;
  border-radius: 12px;
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 4px;
}

.friend-item:hover {
  background: var(--bg-hover);
}

.friend-item.active {
  background: var(--bg-tertiary);
  border-color: var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.friend-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.friend-info-top,
.friend-info-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.truncate-msg {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
}

.chat-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--bg-primary);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-card);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 24px;
  scroll-behavior: smooth;
}

.messages-inner {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-bottom: 24px;
}

.message-row {
  display: flex;
  gap: 16px;
  width: 100%;
}

.message-row--self {
  justify-content: flex-end;
}

.message-content {
  display: flex;
  flex-direction: column;
  max-width: 80%;
}

.message-row--self .message-content {
  align-items: flex-end;
}

.message-meta {
  display: flex;
  align-items: baseline;
  margin-bottom: 6px;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  font-size: 15px;
  line-height: 1.6;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.message-row--self .message-bubble {
  background: var(--accent-blue);
  color: #0f111a;
  border-color: var(--accent-blue);
  border-bottom-right-radius: 4px;
}

.message-row:not(.message-row--self) .message-bubble {
  border-top-left-radius: 4px;
}

.input-wrapper {
  padding: 0 24px 24px;
  background: linear-gradient(180deg, transparent, var(--bg-primary) 20%);
}

.input-container {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 8px 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.input-container:focus-within {
  border-color: var(--accent-blue);
  box-shadow: 0 4px 20px rgba(56, 189, 248, 0.15);
}

.gpt-input :deep(.el-textarea__inner) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 8px 40px 8px 8px;
  color: var(--text-primary);
  font-size: 15px;
  line-height: 1.5;
}

.gpt-input :deep(.el-textarea__inner:focus) {
  box-shadow: none !important;
}

.input-actions {
  position: absolute;
  right: 12px;
  bottom: 12px;
}

.send-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-chat {
  flex: 1;
}

@media (max-width: 768px) {
  .chat-page {
    height: calc(100vh - 60px);
  }
  
  .chat-container {
    flex-direction: column;
    border-radius: 0;
    border-left: none;
    border-right: none;
  }

  .friend-list {
    width: 100%;
    max-height: 30vh;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }

  .message-content {
    max-width: 90%;
  }
}
</style>
