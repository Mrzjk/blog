<template>
  <div class="chat-container fade-in-up">
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <el-icon><ChatDotRound /></el-icon> 消息列表
      </div>
      <div class="friend-list">
        <el-empty v-if="friends.length === 0" description="暂无消息" :image-size="60" />
        <div 
          v-else
          class="friend-item" 
          v-for="friend in friends" 
          :key="friend.id"
          :class="{ active: currentFriend?.id === friend.id }"
          @click="selectFriend(friend)"
        >
          <el-badge :is-dot="friend.unread_count > 0" class="item-badge">
            <el-avatar :size="40" class="avatar" @click.stop="goToUserProfile(friend.id)" style="cursor: pointer">{{ friend.username.charAt(0).toUpperCase() }}</el-avatar>
          </el-badge>
          <div class="friend-info-col">
            <div class="name">
              <span @click.stop="goToUserProfile(friend.id)" style="cursor: pointer">{{ friend.username }}</span>
              <span class="muted author-level" style="font-size: 12px; margin-left: 2px;">Lv.{{ friend.level || 1 }}</span>
              <span :class="['status-dot', friend.online ? 'online' : 'offline']"></span>
            </div>
            <div class="last-msg">{{ friend.last_message || '暂无消息' }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="chat-main">
      <template v-if="currentFriend">
        <div class="chat-header">
          <div class="header-user" @click="goToUserProfile(currentFriend?.id)" style="cursor: pointer">
            <el-avatar :size="32">{{ currentFriend.username.charAt(0).toUpperCase() }}</el-avatar>
            <span>{{ currentFriend.username }}</span>
            <span class="muted author-level" style="font-size: 12px; margin-left: 4px;">Lv.{{ currentFriend.level || 1 }}</span>
            <span :class="['status-text', currentFriend.online ? 'online' : 'offline']">
              {{ currentFriend.online ? '在线' : '离线' }}
            </span>
          </div>
          <div class="header-actions">
            <el-button type="danger" link @click="handleClearMessages">清空记录</el-button>
          </div>
        </div>
        
        <div class="chat-messages" ref="messagesContainer">
          <el-empty v-if="messages.length === 0" description="开始聊天吧~" :image-size="100" />
          <div 
            v-else
            v-for="msg in messages" 
            :key="msg.id || msg.temp_id" 
            class="message-item"
            :class="{ sent: msg.sender_id === userStore.user?.id }"
          >
            <el-avatar :size="36" class="msg-avatar" v-if="msg.sender_id !== userStore.user?.id" @click="goToUserProfile(currentFriend?.id)" style="cursor: pointer">
              {{ currentFriend.username.charAt(0).toUpperCase() }}
            </el-avatar>
            
            <div class="msg-content">
              <div class="msg-time" v-if="msg.sender_id !== userStore.user?.id">
                <span class="msg-sender-name" @click="goToUserProfile(currentFriend?.id)" style="cursor: pointer">{{ currentFriend.username }}</span> 
                <span class="muted author-level" style="font-size: 11px; margin-right: 8px;">Lv.{{ currentFriend.level || 1 }}</span>
                {{ formatDate(msg.created_at) }}
              </div>
              <div class="msg-time" v-else>
                {{ formatDate(msg.created_at) }}
              </div>
              <div class="bubble">{{ msg.content }}</div>
            </div>
            
            <el-avatar :size="36" class="msg-avatar" v-if="msg.sender_id === userStore.user?.id" @click="goToUserProfile(userStore.user?.id)" style="cursor: pointer">
              {{ userStore.user?.username.charAt(0).toUpperCase() }}
            </el-avatar>
          </div>
        </div>
        
        <div class="chat-input">
          <el-input 
            v-model="inputMessage" 
            type="textarea" 
            :rows="3" 
            placeholder="输入消息，按 Enter 发送，Shift + Enter 换行" 
            resize="none"
            @keydown.enter.prevent="handleKeydown"
          />
          <div class="input-actions">
            <span class="hint">按 Enter 发送</span>
            <el-button type="primary" class="send-btn" @click="sendMessage" :disabled="!inputMessage.trim()">
              发送 <el-icon class="el-icon--right"><Position /></el-icon>
            </el-button>
          </div>
        </div>
      </template>
      <div v-else class="no-chat-selected">
        <el-icon class="huge-icon"><ChatLineRound /></el-icon>
        <p>选择一个好友开始聊天</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/store/user';
import { ChatDotRound, ChatLineRound, Position } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getFriends, getMessages, clearMessages } from '@/api/chat';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const friends = ref<any[]>([]);
const currentFriend = ref<any>(null);
const messages = ref<any[]>([]);
const inputMessage = ref('');
const messagesContainer = ref<HTMLElement | null>(null);

let ws: WebSocket | null = null;

const loadFriends = async () => {
  try {
    const { data } = await getFriends();
    friends.value = data;
    
    // Select friend from route query
    const queryId = route.query.id;
    if (queryId && friends.value.length > 0) {
      const friend = friends.value.find(f => f.id === Number(queryId));
      if (friend) {
        selectFriend(friend);
      }
    }
  } catch (error) {
    console.error(error);
  }
};

const selectFriend = async (friend: any) => {
  currentFriend.value = friend;
  friend.unread_count = 0; // Clear unread badge
  try {
    const { data } = await getMessages(friend.id);
    messages.value = data;
    scrollToBottom();
  } catch (error) {
    console.error(error);
  }
};

const handleClearMessages = () => {
  if (!currentFriend.value) return;
  ElMessageBox.confirm('确定要清空与该好友的聊天记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await clearMessages(currentFriend.value.id);
      messages.value = [];
      ElMessage.success('已清空');
    } catch (error) {
      ElMessage.error('清空失败');
    }
  }).catch(() => {});
};

const handleKeydown = (e: KeyboardEvent) => {
  if (e.shiftKey) {
    // allow newline
    return;
  }
  sendMessage();
};

const sendMessage = () => {
  if (!inputMessage.value.trim() || !currentFriend.value || !ws) return;
  
  const tempId = Date.now().toString();
  const msgContent = inputMessage.value.trim();
  
  // Optimistic update
  messages.value.push({
    temp_id: tempId,
    sender_id: userStore.user?.id,
    receiver_id: currentFriend.value.id,
    content: msgContent,
    created_at: new Date().toISOString()
  });
  
  scrollToBottom();
  
  ws.send(JSON.stringify({
    action: 'send_message',
    receiver_id: currentFriend.value.id,
    content: msgContent,
    temp_id: tempId
  }));
  
  inputMessage.value = '';
  
  // Update friend's last message
  const fIndex = friends.value.findIndex(f => f.id === currentFriend.value.id);
  if (fIndex > -1) {
    friends.value[fIndex].last_message = msgContent;
    // Move to top
    const f = friends.value.splice(fIndex, 1)[0];
    friends.value.unshift(f);
  }
};

const initWebSocket = () => {
  const token = localStorage.getItem('token');
  if (!token) return;
  
  // Use current host or configure via env
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = import.meta.env.VITE_API_BASE_URL 
    ? import.meta.env.VITE_API_BASE_URL.replace('http', 'ws').replace('/api/v1', '')
    : `${protocol}//${window.location.host}`;
    
  // Since we use proxy in vite, we connect to /ws directly if in dev
  const wsUrl = import.meta.env.DEV 
    ? `ws://127.0.0.1:8001/api/v1/chat/ws/${token}`
    : `${host}/api/v1/chat/ws/${token}`;
    
  ws = new WebSocket(wsUrl);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'chat') {
      if (currentFriend.value && data.sender_id === currentFriend.value.id) {
        messages.value.push(data);
        scrollToBottom();
      } else {
        // Update unread count
        const fIndex = friends.value.findIndex(f => f.id === data.sender_id);
        if (fIndex > -1) {
          friends.value[fIndex].unread_count = (friends.value[fIndex].unread_count || 0) + 1;
          friends.value[fIndex].last_message = data.content;
          // Move to top
          const f = friends.value.splice(fIndex, 1)[0];
          friends.value.unshift(f);
        } else {
          loadFriends(); // Reload to get new friend if not in list
        }
      }
    } else if (data.type === 'ack') {
      // Replace temp msg with real id if needed
      const msgIndex = messages.value.findIndex(m => m.temp_id === data.temp_id);
      if (msgIndex > -1) {
        messages.value[msgIndex].id = data.id;
      }
    }
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

const formatDate = (dateStr: string) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}-${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
};

const goToUserProfile = (userId: number | undefined) => {
  if (userId) {
    router.push(`/user/${userId}`);
  }
};

onMounted(() => {
  loadFriends();
  initWebSocket();
});

onUnmounted(() => {
  if (ws) {
    ws.close();
  }
});
</script>

<style scoped>
.chat-container {
  display: flex;
  height: calc(100vh - 100px);
  max-width: 1200px;
  margin: 0 auto;
  background: var(--bg-primary);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.chat-sidebar {
  width: 280px;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
}

.sidebar-header {
  padding: 20px;
  font-weight: bold;
  font-size: 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
}

.friend-list {
  flex: 1;
  overflow-y: auto;
}

.friend-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  cursor: pointer;
  transition: background-color 0.3s;
  border-bottom: 1px solid var(--border-color);
}

.friend-item:hover {
  background-color: var(--bg-hover);
}

.friend-item.active {
  background-color: var(--bg-hover);
  border-left: 4px solid var(--accent-primary);
  padding-left: 16px;
}

.item-badge {
  margin-right: 12px;
}

.avatar {
  background-color: var(--accent-primary);
  color: white;
}

.friend-info-col {
  flex: 1;
  overflow: hidden;
}

.name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.online {
  background-color: #67c23a;
  box-shadow: 0 0 4px #67c23a;
}

.status-dot.offline {
  background-color: #909399;
}

.last-msg {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.chat-header {
  padding: 15px 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  font-size: 16px;
}

.status-text {
  font-size: 12px;
  font-weight: normal;
  padding: 2px 8px;
  border-radius: 10px;
}

.status-text.online {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.status-text.offline {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.chat-messages {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: var(--bg-secondary);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 80%;
}

.message-item.sent {
  align-self: flex-end;
  flex-direction: row;
}

.msg-avatar {
  background-color: var(--accent-primary);
}

.msg-content {
  display: flex;
  flex-direction: column;
}

.message-item.sent .msg-content {
  align-items: flex-end;
}

.msg-time {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.msg-sender-name {
  color: var(--text-secondary);
  font-weight: 500;
}

.bubble {
  padding: 12px 16px;
  border-radius: 12px;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}

.message-item.sent .bubble {
  background-color: var(--accent-primary);
  color: white;
  border-top-right-radius: 4px;
}

.message-item:not(.sent) .bubble {
  border-top-left-radius: 4px;
}

.chat-input {
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.chat-input :deep(.el-textarea__inner) {
  border: none;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px;
  box-shadow: none;
}

.chat-input :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px var(--accent-primary);
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 12px;
  gap: 16px;
}

.hint {
  font-size: 12px;
  color: var(--text-muted);
}

.send-btn {
  border-radius: 20px;
  padding: 8px 24px;
}

.no-chat-selected {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: var(--text-muted);
  background-color: var(--bg-secondary);
}

.huge-icon {
  font-size: 64px;
  margin-bottom: 16px;
  color: var(--border-color);
}
</style>
