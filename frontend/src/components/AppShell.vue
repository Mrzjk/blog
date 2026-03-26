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
          <RouterLink to="/" :class="linkClass('/')">首页</RouterLink>
          <RouterLink to="/chat" :class="linkClass('/chat')">消息</RouterLink>
          <RouterLink to="/notifications" :class="linkClass('/notifications')">通知</RouterLink>
          <RouterLink to="/profile" :class="linkClass('/profile')">我的</RouterLink>
        </nav>
        <div class="shell-actions">
          <div class="user-chip" v-if="userStore.user">
            <span class="user-chip__avatar">{{ userInitial }}</span>
            <div>
              <strong>{{ userStore.user.username }}</strong>
              <span>Lv.{{ userStore.user.level || 1 }}</span>
            </div>
          </div>
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
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isAuthPage = computed(() => route.path === '/login')
const userInitial = computed(() => userStore.user?.username?.charAt(0)?.toUpperCase() || 'U')

const linkClass = (path) => ['shell-link', { 'shell-link--active': route.path === path }]

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.shell {
  min-height: 100vh;
}

.shell-header {
  position: sticky;
  top: 0;
  z-index: 20;
  backdrop-filter: blur(16px);
  background: rgba(10, 10, 10, 0.85);
  border-bottom: 1px solid var(--border-color);
}

.shell-header__inner {
  width: min(1200px, calc(100% - 48px));
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 14px 0;
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
  font-size: 14px;
  font-weight: 600;
}

.brand span,
.user-chip span {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
}

.brand-mark,
.user-chip__avatar {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  color: #fff;
  font-weight: 700;
  font-size: 18px;
}

.shell-nav {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px;
  border-radius: 12px;
  background: var(--bg-secondary);
}

.shell-link {
  padding: 10px 18px;
  border-radius: 10px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.shell-link:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.shell-link--active {
  color: #fff;
  background: var(--accent-blue);
}

.shell-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px 6px 6px;
  border-radius: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

.user-chip__avatar {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  font-size: 14px;
}

.ghost-btn {
  height: 38px;
  padding: 0 18px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ghost-btn:hover {
  border-color: var(--accent-blue);
  color: var(--accent-blue);
}

.shell-main {
  width: min(1200px, calc(100% - 48px));
  margin: 0 auto;
  padding: 32px 0 80px;
}

.shell-main--auth {
  width: 100%;
  padding: 0;
}

@media (max-width: 960px) {
  .shell-header__inner {
    flex-wrap: wrap;
  }

  .shell-nav {
    order: 3;
    width: 100%;
    justify-content: center;
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
