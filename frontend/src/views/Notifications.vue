<template>
  <div class="notifications-page">
    <section class="page-hero">
      <div class="page-hero__title">
        <span class="page-hero__eyebrow">通知</span>
        <h1>你的互动消息</h1>
        <p>在这里查看点赞、评论和好友申请通知，及时了解与读者的互动。</p>
      </div>
    </section>

    <section class="notifications-board glass-card">
      <div class="notifications-board__header">
        <div>
          <p class="muted">活动动态</p>
          <h3 class="section-title">我的通知</h3>
        </div>
        <span class="pill">{{ notifications.length }} 条</span>
      </div>

      <div v-if="notifications.length" class="notification-list">
        <article v-for="item in notifications" :key="item.id" class="notification-item">
          <div class="notification-item__marker" :class="`notification-item__marker--${item.type}`"></div>
          <div class="notification-item__body" :class="{ 'notification-item__body--read': item.is_read }">
            <div class="notification-item__meta">
              <el-tag size="small" :type="getTagType(item.type)">{{ getTagLabel(item.type) }}</el-tag>
              <span class="muted">{{ item.is_read ? '已处理' : '未读' }}</span>
            </div>
            <p>{{ item.content }}</p>
          </div>
          <div v-if="item.type === 'friend_request' && !item.is_read" class="notification-item__action">
            <el-button type="success" size="small" @click="acceptFriend(item)">同意</el-button>
          </div>
        </article>
      </div>
      <el-empty v-else description="暂无通知" />
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../utils/request'
import { ElMessage } from 'element-plus'

const notifications = ref([])

const fetchNotifications = async () => {
  try {
    const { data } = await request.get('/chat/notifications')
    notifications.value = data
  } catch (e) {
    ElMessage.error('获取通知失败')
  }
}

const acceptFriend = async (notification) => {
  try {
    await request.post(`/chat/friends/accept/${notification.sender_id}`)
    ElMessage.success('已同意好友请求')
    fetchNotifications()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

const getTagType = (type) => {
  const map = {
    'like_post': 'danger',
    'comment': 'primary',
    'friend_request': 'warning'
  }
  return map[type] || 'info'
}

const getTagLabel = (type) => {
  const map = {
    'like_post': '点赞',
    'comment': '评论',
    'friend_request': '好友申请'
  }
  return map[type] || '系统'
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.notifications-board {
  padding: 28px;
}

.notifications-board__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.notification-list {
  display: grid;
  gap: 12px;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px;
  border-radius: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

.notification-item__marker {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex: 0 0 auto;
}

.notification-item__marker--like_post {
  background: #ef4444;
}

.notification-item__marker--comment {
  background: var(--accent-blue);
}

.notification-item__marker--friend_request {
  background: #f59e0b;
}

.notification-item__body {
  flex: 1;
}

.notification-item__body--read {
  opacity: 0.5;
}

.notification-item__meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.notification-item__body p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
}

@media (max-width: 720px) {
  .notifications-board__header,
  .notification-item {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
