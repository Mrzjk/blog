<template>
  <article class="feed-card glass-card" @click="router.push(`/post/${post.id}`)">
    <div class="feed-card__header">
      <el-popover placement="bottom-start" :width="280" trigger="hover" @show="$emit('load-user-stats', post.author?.id)">
        <template #reference>
          <div class="feed-card__author" @click.stop>
            <div class="author-avatar" @click="goToUserProfile(post.author?.id)" style="cursor: pointer">{{ post.author?.username?.charAt(0)?.toUpperCase() || 'U' }}</div>
            <div class="author-info">
              <span class="author-name" @click="goToUserProfile(post.author?.id)" style="cursor: pointer">{{ post.author?.username }}</span>
              <div class="level-indicator">
                <span class="muted author-level">Lv.{{ post.author?.level || 1 }}</span>
                <el-progress 
                  v-if="post.author?.exp !== undefined"
                  :percentage="getExpPercentage(post.author.level, post.author.exp)" 
                  :show-text="false" 
                  :stroke-width="4"
                  class="level-progress-mini"
                  color="var(--accent-primary)"
                />
              </div>
            </div>
          </div>
        </template>
        <div class="user-popover" v-if="post.author">
          <div class="user-popover__header">
            <div class="author-avatar author-avatar--large">{{ post.author.username?.charAt(0)?.toUpperCase() }}</div>
            <div>
              <strong>{{ post.author.username }}</strong>
              <p class="muted">{{ post.author.bio || '暂无简介' }}</p>
            </div>
          </div>
          <div class="user-popover__stats">
            <div class="stat-box">
              <strong>{{ userStats[post.author.id]?.followers || 0 }}</strong>
              <span class="muted">粉丝</span>
            </div>
            <div class="stat-box">
              <strong>{{ userStats[post.author.id]?.following || 0 }}</strong>
              <span class="muted">关注</span>
            </div>
            <div class="stat-box">
              <strong>{{ userStats[post.author.id]?.posts || 0 }}</strong>
              <span class="muted">文章</span>
            </div>
          </div>
          <div class="user-popover__actions">
            <el-button v-if="isAuthenticated && currentUser?.id !== post.author.id" type="primary" size="small" @click="$emit('friend-action', post.author.id)">
              {{ friendStatus[post.author.id] === 'accepted' ? '解除好友' : friendStatus[post.author.id] === 'pending_sent' ? '请求已发送' : friendStatus[post.author.id] === 'pending_received' ? '同意请求' : '加好友' }}
            </el-button>
            <el-button v-if="isAuthenticated && currentUser?.id !== post.author.id" size="small" @click="router.push('/chat')">私信</el-button>
            <el-button v-if="!isAuthenticated" type="primary" size="small" @click="router.push('/login')">登录查看</el-button>
          </div>
        </div>
      </el-popover>
      <span class="feed-card__date">{{ formatDate(post.created_at) }}</span>
    </div>

    <div class="feed-card__content">
      <div v-if="post.cover_image" class="feed-card__cover">
        <img :src="post.cover_image" alt="cover" loading="lazy" />
      </div>
      <h2>{{ post.title }}</h2>
      <p>{{ excerpt(post.content) }}</p>
      
      <div class="feed-card__meta">
        <el-tag v-if="post.category" size="small" type="warning" effect="light" class="category-tag">
          {{ post.category.name }}
        </el-tag>
        <el-tag v-for="tag in post.tags" :key="tag.id" size="small" effect="plain">
          {{ tag.name }}
        </el-tag>
      </div>
    </div>

    <div class="feed-card__footer">
      <div class="feed-card__stats">
        <span class="stat-item"><el-icon><View /></el-icon> {{ post.views }}</span>
        <span class="stat-item"><el-icon><ChatLineRound /></el-icon> {{ post.comments?.length || 0 }}</span>
        <button v-if="isAuthenticated" class="inline-action" :class="{ 'is-active': post.is_liked }" @click.stop="$emit('like', post)">
          <el-icon><Star v-if="!post.is_liked" /><StarFilled v-else /></el-icon> {{ post.likes }}
        </button>
        <span v-else class="stat-item" @click.stop="router.push('/login')"><el-icon><Star /></el-icon> {{ post.likes }}</span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { View, ChatLineRound, Star, StarFilled } from '@element-plus/icons-vue'

const router = useRouter()

const props = defineProps({
  post: {
    type: Object,
    required: true
  },
  userStats: {
    type: Object,
    default: () => ({})
  },
  friendStatus: {
    type: Object,
    default: () => ({})
  },
  isAuthenticated: {
    type: Boolean,
    default: false
  },
  currentUser: {
    type: Object,
    default: null
  }
})

defineEmits(['load-user-stats', 'friend-action', 'like'])

const excerpt = content => (content || '').slice(0, 150) + ((content || '').length > 150 ? '...' : '')
const formatDate = value => {
  const date = new Date(value)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  if (diff < 2592000) return `${Math.floor(diff / 86400)}天前`
  
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const getExpPercentage = (level, exp) => {
  level = level || 1;
  exp = exp || 0;
  let expToCurrentLevel = 0;
  for (let i = 1; i < level; i++) {
    expToCurrentLevel += i * 10;
  }
  
  const expForNextLevel = level * 10;
  const currentLevelExp = exp - expToCurrentLevel;
  
  const percentage = (currentLevelExp / expForNextLevel) * 100;
  return Math.min(100, Math.max(0, percentage));
};

const goToUserProfile = (userId) => {
  if (userId) {
    router.push(`/user/${userId}`)
  }
}
</script>

<style scoped>
.feed-card {
  padding: 20px;
  margin-bottom: 16px;
  cursor: pointer;
  background: var(--bg-card);
  border-radius: 12px;
}

.feed-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.feed-card__author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  font-size: 15px;
  color: var(--text-primary);
}

.author-level {
  font-size: 12px;
}

.level-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.level-progress-mini {
  width: 60px;
}

.feed-card__date {
  color: var(--text-muted);
  font-size: 13px;
}

.feed-card__cover {
  margin: 0 -20px 16px;
  max-height: 240px;
  overflow: hidden;
}

.feed-card__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.feed-card:hover .feed-card__cover img {
  transform: scale(1.02);
}

.feed-card__content h2 {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 700;
  line-height: 1.4;
  color: var(--text-primary);
}

.feed-card__content p {
  margin: 0 0 16px;
  color: var(--text-secondary);
  font-size: 15px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.feed-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.tag-pill {
  font-size: 12px;
  color: var(--accent-blue);
  background: rgba(255, 122, 69, 0.1);
  padding: 4px 10px;
  border-radius: 4px;
}

.feed-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.feed-card__stats {
  display: flex;
  align-items: center;
  gap: 24px;
}

.stat-item, .inline-action {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-muted);
  font-size: 14px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.inline-action:hover {
  color: var(--accent-blue);
}

.inline-action.is-active {
  color: var(--accent-blue);
}

/* User Popover Styles */
.user-popover {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.user-popover__header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar--large {
  width: 48px;
  height: 48px;
  font-size: 20px;
}

.user-popover__header p {
  margin: 4px 0 0;
  font-size: 13px;
}

.user-popover__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  text-align: center;
  background: var(--bg-tertiary);
  padding: 12px;
  border-radius: 8px;
}

.stat-box strong {
  display: block;
  font-size: 16px;
  color: var(--text-primary);
}

.stat-box span {
  font-size: 12px;
}

.user-popover__actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}
</style>