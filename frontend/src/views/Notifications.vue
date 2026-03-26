<template>
  <div class="notifications-page">
    <!-- <section class="page-hero">
      <div class="page-hero__title">
        <span class="page-hero__eyebrow">通知</span>
        <h1>你的互动消息</h1>
        <p>在这里查看点赞、评论和好友申请通知，及时了解与读者的互动。</p>
      </div>
    </section> -->

    <section class="notifications-board glass-card">
      <div class="notifications-board__header">
        <div>
          <p class="muted">活动动态</p>
          <h3 class="section-title">我的通知</h3>
        </div>
        <span class="pill">{{ notifications.length }} 条</span>
      </div>

      <div v-if="notifications.length" class="notification-list">
        <article v-for="item in paginatedNotifications" :key="item.id" class="notification-item">
          <div class="notification-item__marker" :class="`notification-item__marker--${item.type}`"></div>
          <div class="notification-item__body" :class="{ 'notification-item__body--read': item.is_read }">
            <div class="notification-item__meta">
              <el-tag size="small" :type="getTagType(item.type)" effect="dark">{{ getTagLabel(item.type) }}</el-tag>
              <span class="muted time-text">{{ formatTime(item.created_at) }}</span>
              <span class="status-badge" :class="item.is_read ? 'status-read' : 'status-unread'">{{ item.is_read ? '已读' : '未读' }}</span>
            </div>
            <p>{{ item.content }}</p>
          </div>
          <div v-if="item.type === 'friend_request' && !item.is_read" class="notification-item__action">
            <el-button type="primary" size="small" @click="acceptFriend(item)">同意添加</el-button>
            <el-button type="danger" size="small" plain @click="rejectFriend(item)">拒绝</el-button>
          </div>
          <div v-if="item.type === 'friend_request' && item.is_read" class="notification-item__action">
            <el-tag size="small" type="info">已处理</el-tag>
          </div>
        </article>
        
        <!-- 分页 -->
        <div class="pagination-container" v-if="notifications.length > pageSize">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="notifications.length"
            background
            layout="prev, pager, next"
            class="tech-pagination"
            @current-change="handlePageChange"
          />
        </div>
      </div>
      <el-empty v-else description="暂无系统通知" :image-size="100" class="opacity-50" />
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import request from '../utils/request'
import { ElMessage } from 'element-plus'
import { useChatStore } from '../store/chat'

const chatStore = useChatStore()
const notifications = ref([])

// 分页状态
const currentPage = ref(1)
const pageSize = ref(10)

const paginatedNotifications = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return notifications.value.slice(start, end)
})

const handlePageChange = (page) => {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const formatTime = (timeStr) => {
  if (!timeStr) return '未知时间'
  const date = new Date(timeStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const fetchNotifications = async () => {
  try {
    const { data } = await request.get('/chat/notifications')
    notifications.value = data
  } catch (e) {
    console.error(e)
    ElMessage.error(e.response?.data?.detail || '获取通知失败')
  }
}

const acceptFriend = async (notification) => {
  try {
    await request.put(`/chat/friend-request/${notification.sender_id}/accept`)
    ElMessage.success('已同意好友请求')
    fetchNotifications()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

const rejectFriend = async (notification) => {
  try {
    await request.put(`/chat/friend-request/${notification.sender_id}/reject`)
    ElMessage.warning('已拒绝好友请求')
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
  chatStore.clearUnreadNotifications()
})
</script>

<style scoped>
.notifications-board {
  padding: 28px;
  max-width: 800px;
  margin: 0 auto;
}

.notifications-board__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.notification-list {
  display: grid;
  gap: 16px;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border-radius: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.notification-item:hover {
  transform: translateY(-2px);
  border-color: rgba(56, 189, 248, 0.4);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.notification-item__marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex: 0 0 auto;
  box-shadow: 0 0 10px currentColor;
}

.notification-item__marker--like_post {
  background: #ef4444;
  color: rgba(239, 68, 68, 0.5);
}

.notification-item__marker--comment {
  background: var(--accent-blue);
  color: rgba(56, 189, 248, 0.5);
}

.notification-item__marker--friend_request {
  background: #f59e0b;
  color: rgba(245, 158, 11, 0.5);
}

.notification-item__body {
  flex: 1;
}

.notification-item__body--read {
  opacity: 0.6;
}

.notification-item__meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.time-text {
  font-size: 12px;
  font-family: 'SF Mono', Consolas, monospace;
}

.status-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.status-unread {
  color: var(--accent-blue);
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.2);
}

.status-read {
  color: var(--text-muted);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
}

.notification-item__body p {
  margin: 0;
  color: var(--text-primary);
  font-size: 15px;
  line-height: 1.6;
}

.notification-item__action {
  display: flex;
  gap: 8px;
  align-items: center;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-bottom: 16px;
}

@media (max-width: 720px) {
  .notifications-board__header,
  .notification-item {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
