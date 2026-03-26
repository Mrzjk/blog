<template>
  <div class="shell">
    <header v-if="!isAuthPage" class="shell-header">
      <div class="shell-header__inner">
        <RouterLink class="brand" to="/">
          <span class="brand-mark">B</span>
          <div>
            <strong>博客社区</strong>
            <span>分享知识，连接世界</span>
          </div>
        </RouterLink>
        <nav class="shell-nav">
          <a href="#" @click.prevent="navigate('/')" :class="linkClass('/')">
            <el-icon class="nav-icon"><Document /></el-icon> 博客
          </a>
          <a href="#" @click.prevent="navigate('/entertainment')" :class="linkClass('/entertainment')">
            <el-icon class="nav-icon"><VideoPlay /></el-icon> 娱乐
          </a>
          <a href="#" v-if="userStore.isAuthenticated" @click.prevent="navigate('/chat')" :class="linkClass('/chat')">
            <el-icon class="nav-icon"><ChatDotRound /></el-icon> 好友
            <el-badge v-if="chatStore.unreadMessagesCount > 0" :value="chatStore.unreadMessagesCount" class="nav-badge" :max="99" />
          </a>
          <a href="#" v-if="userStore.isAuthenticated" @click.prevent="navigate('/notifications')" :class="linkClass('/notifications')">
            <el-icon class="nav-icon"><Bell /></el-icon> 通知
            <el-badge v-if="chatStore.unreadNotificationsCount > 0" :value="chatStore.unreadNotificationsCount" class="nav-badge" :max="99" />
          </a>
          <a href="#" v-if="userStore.isAuthenticated" @click.prevent="navigate('/profile')" :class="linkClass('/profile')">
            <el-icon class="nav-icon"><User /></el-icon> 我的
          </a>
        </nav>
        <div class="shell-actions">
          <div class="search-bar">
            <el-input 
              v-model="searchQuery" 
              placeholder="搜索文章..." 
              prefix-icon="Search" 
              class="search-input" 
              @keyup.enter="handleSearch" 
            />
          </div>
          <el-popover v-if="userStore.user" placement="bottom" trigger="hover" :width="260">
            <template #reference>
              <div class="user-chip">
                <span class="user-chip__avatar">{{ userInitial }}</span>
                <div>
                  <strong>{{ userStore.user.username }}</strong>
                  <span>Lv.{{ userStore.user.level || 1 }}</span>
                </div>
              </div>
            </template>
            <div class="xp-pop">
              <div class="xp-pop__top">
                <div>
                  <strong>{{ userStore.user.username }}</strong>
                  <div class="muted">等级 Lv.{{ userStore.user.level || 1 }}</div>
                </div>
                <span class="pill">+1 经验/10分钟</span>
              </div>
              <el-progress :percentage="xpPercentage" :stroke-width="10" :show-text="false" />
              <div class="xp-pop__meta">
                <span>{{ xpCurrent }}/{{ xpNeed }} 经验</span>
                <span class="muted">升级所需</span>
              </div>
            </div>
          </el-popover>
          <button class="ghost-btn" @click="logout">退出登录</button>
        </div>
      </div>
    </header>
    <main :class="['shell-main', { 'shell-main--auth': isAuthPage }]">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { useChatStore } from '../store/chat'
import { Search, Document, VideoPlay, ChatDotRound, Bell, User } from '@element-plus/icons-vue'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const chatStore = useChatStore()
const searchQuery = ref('')

const navigate = (path) => {
  router.push(path)
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/', query: { search: searchQuery.value.trim() } })
    searchQuery.value = ''
  }
}

let expTimer = null

const isAuthPage = computed(() => ['/login', '/register'].includes(route.path))
const userInitial = computed(() => userStore.user?.username?.charAt(0)?.toUpperCase() || 'U')

const expPerLevel = (level) => 10 * (2 ** (Math.max(1, level) - 1))
const expStartForLevel = (level) => {
  let total = 0
  for (let l = 1; l < level; l += 1) {
    total += expPerLevel(l)
  }
  return total
}

const xpNeed = computed(() => {
  const level = userStore.user?.level || 1
  return expPerLevel(level)
})

const xpCurrent = computed(() => {
  const level = userStore.user?.level || 1
  const exp = userStore.user?.exp || 0
  return Math.max(0, exp - expStartForLevel(level))
})

const xpPercentage = computed(() => {
  const need = xpNeed.value || 1
  const current = xpCurrent.value
  return Math.max(0, Math.min(100, Math.round((current / need) * 100)))
})

const linkClass = (path) => ['shell-link', { 'shell-link--active': route.path === path }]

const logout = () => {
  userStore.logout()
  router.push('/login')
}

const tickExp = async () => {
  if (!userStore.isAuthenticated) return
  try {
    const { data } = await request.post('/auth/heartbeat')
    if (userStore.user) {
      userStore.setUser({ ...userStore.user, exp: data.exp, level: data.level })
    }
  } catch {
  }
}

onMounted(() => {
  if (!userStore.isAuthenticated) return
  tickExp()
  expTimer = setInterval(tickExp, 60000)
})

onUnmounted(() => {
  if (expTimer) {
    clearInterval(expTimer)
    expTimer = null
  }
})
</script>

<style scoped>
.shell {
  min-height: 100vh;
}

.shell-header {
  position: sticky;
  top: 16px;
  z-index: 100;
  margin: 0 auto 24px auto;
  max-width: 1440px;
  width: calc(100% - 32px);
  background: rgba(28, 33, 43, 0.75);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.3), 0 1px 3px rgba(0,0,0,0.1);
  border-radius: 24px;
  transition: all 0.3s ease;
}

.shell-header__inner {
  height: 64px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
}

.search-bar {
  width: 240px;
  margin-right: 16px;
}

.search-input :deep(.el-input__wrapper) {
  background-color: rgba(30, 36, 48, 0.6);
  border-radius: 100px;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
}

.search-input :deep(.el-input__wrapper):hover,
.search-input :deep(.el-input__wrapper.is-focus) {
  background-color: var(--bg-secondary);
  border-color: var(--accent-blue);
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  color: var(--text-primary);
  text-decoration: none;
}

.brand strong,
.user-chip strong {
  display: block;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.brand span,
.user-chip span {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  color: #fff;
  font-weight: 700;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
}

.user-chip__avatar {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  color: #fff;
  font-weight: 600;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(56, 189, 248, 0.2);
}

.shell-nav {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px;
  border-radius: 100px;
  background: rgba(30, 36, 48, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1), 0 4px 12px rgba(0,0,0,0.2);
  backdrop-filter: blur(10px);
}

.shell-link {
  padding: 8px 20px;
  border-radius: 100px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.nav-icon {
  font-size: 18px;
  opacity: 0.8;
  transition: opacity 0.3s, transform 0.3s;
}

.shell-link:hover .nav-icon {
  opacity: 1;
  transform: scale(1.1);
}

.nav-badge {
  position: absolute;
  top: -6px;
  right: -10px;
}

.nav-badge :deep(.el-badge__content) {
  background-color: var(--text-danger);
  border: none;
  font-weight: 600;
}

.shell-link:hover {
  color: var(--accent-blue);
  background: var(--bg-hover);
}

.shell-link--active {
  color: #fff;
  background: rgba(56, 189, 248, 0.2);
  border: 1px solid rgba(56, 189, 248, 0.5);
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
}

.shell-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 12px 4px 4px;
  border-radius: 100px;
  background: rgba(30, 36, 48, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.user-chip:hover {
  transform: translateY(-2px);
  background: var(--bg-secondary);
  border-color: var(--accent-blue);
  box-shadow: 0 6px 16px rgba(56, 189, 248, 0.15);
}

.user-chip__avatar {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  color: #fff;
  font-weight: 600;
  font-size: 14px;
}

.ghost-btn {
  height: 38px;
  padding: 0 18px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 100px;
  background: rgba(30, 36, 48, 0.5);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.ghost-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--accent-blue);
  color: var(--accent-blue);
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
  transform: translateY(-1px);
}

.xp-pop {
  display: grid;
  gap: 14px;
}

.xp-pop__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.xp-pop__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--text-secondary);
  font-size: 13px;
}

.shell-main {
  width: min(1440px, calc(100% - 48px));
  margin: 0 auto;
  padding: 0 0 80px;
}

.shell-main--auth {
  width: 100%;
  padding: 0;
}

@media (max-width: 960px) {
  .shell-header {
    position: static;
  }
  
  .shell-header__inner {
    flex-wrap: wrap;
    height: auto;
    padding: 16px;
    gap: 16px;
  }

  .shell-nav {
    order: 3;
    width: 100%;
    justify-content: center;
    overflow-x: auto;
  }

  .shell-actions {
    margin-left: auto;
  }
}

@media (max-width: 720px) {
  .shell-actions {
    width: 100%;
    justify-content: space-between;
  }

  .ghost-btn {
    padding: 0 12px;
  }
}
</style>
