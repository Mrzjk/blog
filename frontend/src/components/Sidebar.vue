<template>
  <aside class="sidebar">
    <el-card v-if="userStore.isAuthenticated" class="user-card glass-card" shadow="never">
      <div class="user-profile">
        <div class="author-avatar author-avatar--xl">{{ userStore.user.username?.charAt(0)?.toUpperCase() }}</div>
        <h3 class="user-name">{{ userStore.user.username }}</h3>
        <p class="user-bio muted">{{ userStore.user.bio || '这个人很懒，什么都没写~' }}</p>
        <span class="level-badge">Lv.{{ userStore.user.level }}</span>
      </div>
      <div class="user-stats">
        <div class="stat-item">
          <strong>{{ userStats?.posts || 0 }}</strong>
          <span>文章</span>
        </div>
        <div class="stat-item">
          <strong>{{ userStats?.followers || 0 }}</strong>
          <span>粉丝</span>
        </div>
        <div class="stat-item">
          <strong>{{ userStats?.following || 0 }}</strong>
          <span>关注</span>
        </div>
      </div>
    </el-card>

    <el-card v-else class="login-card glass-card" shadow="never">
      <h3 class="welcome-title">欢迎来到博客社区</h3>
      <p class="muted">登录后可发布文章、点赞评论、与作者互动</p>
      <el-button type="primary" size="large" class="w-full mt-4" @click="router.push('/login')">登录 / 注册</el-button>
    </el-card>

    <nav class="side-nav glass-card">
      <div class="nav-item active">
        <el-icon><House /></el-icon> 首页发现
      </div>
      <div class="nav-item">
        <el-icon><Collection /></el-icon> 文章分类
      </div>
      <div class="nav-item">
        <el-icon><PriceTag /></el-icon> 热门标签
      </div>
      <div class="nav-item" @click="router.push('/chat')">
        <el-icon><User /></el-icon> 我的好友
      </div>
    </nav>

    <el-button 
      v-if="userStore.isAuthenticated" 
      type="primary" 
      size="large" 
      class="publish-btn" 
      @click="router.push('/editor')"
    >
      <el-icon><EditPen /></el-icon> 写文章
    </el-button>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { House, Collection, PriceTag, User, EditPen } from '@element-plus/icons-vue'

const router = useRouter()

defineProps({
  userStore: {
    type: Object,
    required: true
  },
  userStats: {
    type: Object,
    default: () => ({})
  }
})
</script>

<style scoped>
.sidebar {
  width: 240px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 88px;
}

.user-card {
  text-align: center;
  padding-top: 10px;
}

.user-profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.author-avatar--xl {
  width: 64px;
  height: 64px;
  font-size: 24px;
  margin-bottom: 8px;
}

.user-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.user-bio {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.level-badge {
  display: inline-block;
  padding: 2px 10px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  color: white;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  margin-top: 4px;
}

.user-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-item strong {
  font-size: 18px;
  color: var(--text-primary);
}

.stat-item span {
  font-size: 12px;
  color: var(--text-muted);
}

.login-card {
  text-align: center;
  padding: 20px 10px;
}

.welcome-title {
  margin: 0 0 12px;
  font-size: 18px;
  color: var(--text-primary);
}

.w-full {
  width: 100%;
}

.mt-4 {
  margin-top: 16px;
}

.side-nav {
  padding: 12px;
  border-radius: 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--accent-blue);
}

.nav-item.active {
  background: rgba(255, 122, 69, 0.1);
  color: var(--accent-blue);
}

.nav-item .el-icon {
  font-size: 18px;
}

.publish-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(255, 122, 69, 0.3);
  transition: transform 0.2s, box-shadow 0.2s;
}

.publish-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 122, 69, 0.4);
}
</style>