<template>
  <div class="friends-page fade-in-up">
    <el-row :gutter="24">
      <!-- 左侧：我的好友 -->
      <el-col :span="16">
        <el-card class="glass-card friend-list-card" shadow="never">
          <template #header>
            <div class="header">
              <div class="header-left">
                <el-icon><Connection /></el-icon>
                <span>我的好友 ({{ friends.length }})</span>
              </div>
              <el-input 
                v-model="searchFriendQuery" 
                placeholder="搜索已有好友..." 
                style="width: 200px" 
                :prefix-icon="Search"
                clearable
              />
            </div>
          </template>
          
          <el-empty v-if="filteredFriends.length === 0" description="暂无好友，快去添加吧~" />
          
          <el-row :gutter="20" v-else>
            <el-col :span="8" v-for="friend in filteredFriends" :key="friend.id" class="mb-4">
              <el-card shadow="hover" class="friend-card">
                <div class="friend-info">
                  <el-avatar :size="60" class="avatar">{{ friend.username.charAt(0).toUpperCase() }}</el-avatar>
                  <div class="name">
                    {{ friend.username }}
                    <span :class="['status-dot', friend.online ? 'online' : 'offline']" :title="friend.online ? '在线' : '离线'"></span>
                  </div>
                  <div class="last-msg" v-if="friend.last_message">
                    {{ friend.last_message.substring(0, 15) }}...
                  </div>
                </div>
                <div class="actions">
                  <el-button type="primary" size="small" @click="goToChat(friend.id)">发消息</el-button>
                  <el-button type="danger" size="small" plain @click="handleRemoveFriend(friend.id)">删除</el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <!-- 右侧：添加好友 & 通知 -->
      <el-col :span="8">
        <el-card class="glass-card mb-4" shadow="never">
          <template #header>
            <div class="header">
              <div class="header-left">
                <el-icon><UserPlus /></el-icon>
                <span>添加好友</span>
              </div>
            </div>
          </template>
          <div class="add-friend-section">
            <el-input
              v-model="searchUserQuery"
              placeholder="输入用户名搜索用户"
              :prefix-icon="Search"
              @keyup.enter="handleSearchUsers"
              clearable
            >
              <template #append>
                <el-button :icon="Search" @click="handleSearchUsers" />
              </template>
            </el-input>

            <div class="search-results" v-if="searchedUsers.length > 0">
              <div class="result-item" v-for="user in searchedUsers" :key="user.id">
                <div class="user-info-mini">
                  <el-avatar :size="30">{{ user.username.charAt(0).toUpperCase() }}</el-avatar>
                  <span>{{ user.username }}</span>
                </div>
                <el-button type="primary" size="small" plain @click="handleAddFriend(user.id)">添加</el-button>
              </div>
            </div>
            <div v-else-if="hasSearched" class="no-results">
              <el-empty description="未找到用户" :image-size="60" />
            </div>
          </div>
        </el-card>

        <el-card class="glass-card" shadow="never">
          <template #header>
            <div class="header">
              <div class="header-left">
                <el-icon><Bell /></el-icon>
                <span>通知中心</span>
              </div>
            </div>
          </template>
          <div class="notifications-list">
            <el-empty v-if="notifications.length === 0" description="暂无通知" :image-size="60" />
            <div 
              v-else 
              v-for="notif in notifications" 
              :key="notif.id" 
              class="notification-item"
            >
              <div class="notif-content">{{ notif.content }}</div>
              <div class="notif-time">{{ new Date(notif.created_at).toLocaleString() }}</div>
              
              <div class="notif-actions" v-if="notif.type === 'friend_request'">
                <el-button type="primary" size="small" @click="handleAcceptRequest(notif.sender_id)">同意</el-button>
                <el-button size="small" @click="handleRejectRequest(notif.sender_id)">拒绝</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Connection, Search, UserPlus, Bell } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '@/utils/request';
import { 
  getFriends, 
  getNotifications, 
  sendFriendRequest, 
  acceptFriendRequest, 
  rejectFriendRequest,
  removeFriend
} from '@/api/chat';

const router = useRouter();

const friends = ref<any[]>([]);
const notifications = ref<any[]>([]);
const searchFriendQuery = ref('');
const searchUserQuery = ref('');
const searchedUsers = ref<any[]>([]);
const hasSearched = ref(false);

const filteredFriends = computed(() => {
  if (!searchFriendQuery.value) return friends.value;
  return friends.value.filter(f => 
    f.username.toLowerCase().includes(searchFriendQuery.value.toLowerCase())
  );
});

const loadFriends = async () => {
  try {
    const { data } = await getFriends();
    friends.value = data;
  } catch (error) {
    console.error(error);
  }
};

const loadNotifications = async () => {
  try {
    const { data } = await getNotifications();
    notifications.value = data;
  } catch (error) {
    console.error(error);
  }
};

const handleSearchUsers = async () => {
  if (!searchUserQuery.value.trim()) return;
  hasSearched.value = true;
  try {
    const { data } = await request.get('/auth/', { params: { q: searchUserQuery.value } });
    searchedUsers.value = data;
  } catch (error) {
    console.error(error);
  }
};

const handleAddFriend = async (userId: number) => {
  try {
    await sendFriendRequest(userId);
    ElMessage.success('好友请求已发送');
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '发送请求失败');
  }
};

const handleAcceptRequest = async (senderId: number) => {
  try {
    await acceptFriendRequest(senderId);
    ElMessage.success('已同意添加好友');
    loadFriends();
    loadNotifications();
  } catch (error) {
    ElMessage.error('操作失败');
  }
};

const handleRejectRequest = async (senderId: number) => {
  try {
    await rejectFriendRequest(senderId);
    ElMessage.success('已拒绝请求');
    loadNotifications();
  } catch (error) {
    ElMessage.error('操作失败');
  }
};

const handleRemoveFriend = (friendId: number) => {
  ElMessageBox.confirm('确定要解除好友关系吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await removeFriend(friendId);
      ElMessage.success('已解除好友关系');
      loadFriends();
    } catch (error) {
      ElMessage.error('操作失败');
    }
  }).catch(() => {});
};

const goToChat = (friendId: number) => {
  router.push({ path: '/user/chat', query: { id: friendId } });
};

onMounted(() => {
  loadFriends();
  loadNotifications();
});
</script>

<style scoped>
.friends-page {
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  font-size: 16px;
  color: var(--text-primary);
}

.mb-4 {
  margin-bottom: 20px;
}

.friend-card {
  text-align: center;
  border-radius: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.friend-card:hover {
  transform: translateY(-5px);
}

.friend-info {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar {
  background-color: var(--accent-primary);
  font-size: 24px;
}

.name {
  margin-top: 10px;
  font-weight: bold;
  color: var(--text-primary);
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
  margin-top: 8px;
  height: 18px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.add-friend-section {
  padding-bottom: 10px;
}

.search-results {
  margin-top: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid var(--border-color);
}

.result-item:last-child {
  border-bottom: none;
}

.user-info-mini {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}

.notifications-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
}

.notification-item:last-child {
  border-bottom: none;
}

.notif-content {
  color: var(--text-primary);
  font-size: 14px;
  margin-bottom: 6px;
}

.notif-time {
  color: var(--text-muted);
  font-size: 12px;
  margin-bottom: 8px;
}

.notif-actions {
  display: flex;
  gap: 8px;
}
</style>
