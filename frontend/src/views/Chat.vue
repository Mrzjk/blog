<template>
  <div class="chat-page">
    <section class="page-hero">
      <div class="page-hero__title">
        <span class="page-hero__eyebrow">消息</span>
        <h1>与好友私信交流</h1>
        <p>在这里与好友进行私密对话，分享想法和观点。</p>
      </div>
    </section>

    <div class="chat-container glass-card">
      <aside class="friend-list">
        <div class="friend-list__top">
          <h3 class="section-title">好友列表</h3>
          <p class="muted">添加好友后才能发送私信</p>
        </div>
        <div class="friend-request">
          <el-input v-model="searchQuery" placeholder="搜索用户名..." size="large" @input="searchUsers" />
        </div>
        <div v-if="searchResults.length" class="friend-items">
          <button
            v-for="user in searchResults"
            :key="user.id"
            class="friend-item"
            @click="addFriend(user.id)"
          >
            <div>
              <strong>{{ user.username }}</strong>
              <span class="muted">ID: {{ user.id }}</span>
            </div>
            <el-button size="small" type="primary">添加</el-button>
          </button>
        </div>
        <div v-if="friends.length" class="friend-items">
          <h4 class="section-title">我的好友</h4>
          <button
            v-for="friend in friends"
            :key="friend.id"
            class="friend-item"
            :class="{ active: activeFriend?.id === friend.id }"
            @click="activeFriend = friend"
          >
            <div>
              <strong>{{ friend.username }}</strong>
              <span class="muted">ID: {{ friend.id }}</span>
            </div>
            <span v-if="friend.online" class="online-dot"></span>
          </button>
        </div>
        <el-empty v-else description="暂无好友，搜索添加一个吧" />
      </aside>

      <section class="chat-box" v-if="activeFriend">
        <div class="chat-header">
          <div>
            <h3>{{ activeFriend.username }}</h3>
            <span class="muted">{{ activeFriend.online ? '在线' : '离线' }}</span>
          </div>
          <span class="pill">实时消息</span>
        </div>
        <div class="messages">
          <div
            v-for="(msg, index) in currentMessages"
            :key="index"
            class="message-wrapper"
            :class="{ 'message-wrapper--self': msg.isMe }"
          >
            <div class="message">
              <span>{{ msg.content }}</span>
            </div>
          </div>
          <el-empty v-if="!currentMessages.length" description="还没有消息，开始聊天吧" />
        </div>
        <div class="input-area">
          <el-input
            v-model="inputMsg"
            type="textarea"
            :rows="3"
            resize="none"
            placeholder="输入消息..."
            @keyup.enter.exact.prevent="send"
          />
          <el-button type="primary" size="large" @click="send">发送</el-button>
        </div>
      </section>
      <div v-else class="empty-chat">
        <div>
          <h3 class="section-title">选择好友开始聊天</h3>
          <p class="muted">从左侧选择好友，或者搜索添加新的好友</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '../store/chat'
import { useUserStore } from '../store/user'
import request from '../utils/request'
import { ElMessage } from 'element-plus'

const chatStore = useChatStore()
const userStore = useUserStore()
const friends = ref([])
const activeFriend = ref(null)
const inputMsg = ref('')
const searchQuery = ref('')
const searchResults = ref([])
const currentMessages = computed(() => {
  if (!activeFriend.value) {
    return []
  }
  return chatStore.messages[activeFriend.value.id] || []
})

const fetchFriends = async () => {
  try {
    const { data } = await request.get('/chat/friends')
    friends.value = data
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '获取好友失败')
  }
}

const searchUsers = async () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }
  try {
    const { data } = await request.get(`/auth/?q=${searchQuery.value}`)
    searchResults.value = data.filter(u => u.id !== userStore.user?.id)
  } catch (e) {
    console.error('搜索用户失败', e)
  }
}

const addFriend = async (friendId) => {
  try {
    await request.post('/chat/friends/request', { friend_id: friendId })
    ElMessage.success('好友请求已发送')
    searchQuery.value = ''
    searchResults.value = []
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '发送失败')
  }
}

const fetchMessages = async (friendId) => {
  try {
    const { data } = await request.get(`/chat/messages/${friendId}`)
    chatStore.messages[friendId] = data.map(msg => ({
      ...msg,
      isMe: msg.sender_id === userStore.user.id
    }))
  } catch (e) {
    console.error('获取消息失败', e)
  }
}

watch(activeFriend, (newFriend) => {
  if (newFriend) {
    fetchMessages(newFriend.id)
  }
})

onMounted(() => {
  chatStore.connectWs()
  fetchFriends()
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
.chat-container {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  min-height: 75vh;
  overflow: hidden;
}

.friend-list {
  display: flex;
  flex-direction: column;
  padding: 24px;
  border-right: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.friend-list__top {
  margin-bottom: 16px;
}

.friend-request {
  margin-bottom: 16px;
}

.friend-items {
  display: grid;
  gap: 8px;
}

.friend-items h4 {
  margin-top: 16px;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.friend-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 14px;
  border: 1px solid transparent;
  border-radius: 12px;
  background: var(--bg-card);
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.friend-item strong {
  display: block;
  margin-bottom: 4px;
  font-size: 14px;
}

.friend-item.active,
.friend-item:hover {
  border-color: var(--accent-blue);
  background: var(--bg-hover);
}

.online-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
}

.chat-box {
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.chat-header h3 {
  margin: 0 0 6px;
  font-size: 18px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: var(--bg-primary);
}

.message-wrapper {
  margin-bottom: 14px;
  display: flex;
}

.message-wrapper--self {
  justify-content: flex-end;
}

.message {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.5;
}

.message-wrapper--self .message {
  background: var(--accent-blue);
  color: #fff;
}

.input-area {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
}

.empty-chat {
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

@media (max-width: 980px) {
  .chat-container {
    grid-template-columns: 1fr;
  }

  .friend-list {
    border-right: 0;
    border-bottom: 1px solid var(--border-color);
    max-height: 300px;
    overflow-y: auto;
  }

  .input-area {
    grid-template-columns: 1fr;
  }
}
</style>
