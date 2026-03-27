<template>
  <header class="navbar glass-nav">
    <div class="nav-container">
      <div class="header-left">
        <div class="logo" @click="$router.push('/user/home')">
          <span class="logo-icon">🔥</span> BlogSystem
        </div>
        <nav class="nav">
          <router-link to="/user/home">首页 (Blog)</router-link>
          <router-link to="/user/forum">论坛 (Forum)</router-link>
          <router-link to="/user/game">娱乐 (Game)</router-link>
          <router-link to="/user/ranking">排行 (Ranking)</router-link>
        </nav>
      </div>

      <div class="header-center">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文章"
          class="search-input"
          :prefix-icon="Search"
          @keyup.enter="handleSearch"
          clearable
        />
      </div>

      <div class="header-right">
        <el-button type="primary" plain class="write-btn" @click="handleWrite">
          <el-icon><Edit /></el-icon> 写文章
        </el-button>
        <template v-if="userStore.token">
          <el-dropdown v-if="userStore.userInfo" trigger="hover">
            <div class="user-profile">
              <div class="author-avatar small-avatar">{{ userStore.userInfo.username.charAt(0).toUpperCase() }}</div>
              <span class="username">{{ userStore.userInfo.username }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="user-dropdown">
                <el-dropdown-item @click="$router.push('/user/profile')">
                  <el-icon><User /></el-icon> 个人主页
                </el-dropdown-item>
                <el-dropdown-item @click="$router.push('/user/profile?tab=articles')">
                  <el-icon><Document /></el-icon> 我的博客
                </el-dropdown-item>
                <el-dropdown-item @click="$router.push('/user/friends')">
                  <el-icon><Connection /></el-icon> 好友列表
                </el-dropdown-item>
                <el-dropdown-item @click="$router.push('/user/chat')">
                  <el-icon><ChatDotRound /></el-icon> 消息中心 <el-badge v-if="unread" is-dot class="ml-1" />
                </el-dropdown-item>
                <el-dropdown-item v-if="userStore.isAdmin" @click="$router.push('/admin/dashboard')" divided>
                  <el-icon><Setting /></el-icon> 管理后台
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <span v-else>加载中...</span>
        </template>
        <template v-else>
          <el-button class="login-btn" type="primary" @click="userStore.openAuthModal('login')">登录 / 注册</el-button>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '@/store/user';
import { useRouter } from 'vue-router';
import { Search, User, Document, Connection, ChatDotRound, Setting, SwitchButton, Edit } from '@element-plus/icons-vue';

const userStore = useUserStore();
const router = useRouter();
const searchQuery = ref('');
const unread = ref(false); // Mock unread state

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/user/home', query: { search: searchQuery.value } });
  } else {
    router.push('/user/home');
  }
};

const handleWrite = () => {
  if (!userStore.token) {
    userStore.openAuthModal('login');
  } else {
    router.push('/user/editor');
  }
};

const handleLogout = () => {
  userStore.logout();
  router.push('/user/home');
};
</script>

<style scoped>
.navbar {
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
  width: 100%;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 40px;
}

.logo {
  font-size: 22px;
  font-weight: 800;
  cursor: pointer;
  color: var(--accent-primary);
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 24px;
}

.nav {
  display: flex;
  gap: 24px;
}

.nav a {
  text-decoration: none;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 15px;
  transition: all 0.3s ease;
  position: relative;
}

.nav a::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background-color: var(--accent-primary);
  transition: width 0.3s ease;
}

.nav a:hover {
  color: var(--accent-primary);
}

.nav a:hover::after,
.nav a.router-link-active::after {
  width: 100%;
}

.nav a.router-link-active {
  color: var(--accent-primary);
  font-weight: 600;
}

.header-center {
  flex: 1;
  max-width: 320px;
  margin: 0 40px;
}

.search-input {
  --el-input-border-radius: 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.write-btn {
  border-radius: 20px !important;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 20px;
  transition: background-color 0.3s ease;
}

.user-profile:hover {
  background-color: var(--bg-hover);
}

.small-avatar {
  width: 32px;
  height: 32px;
  font-size: 14px;
}

.username {
  font-weight: 500;
  color: var(--text-primary);
}

.login-btn {
  border-radius: 20px !important;
  padding: 8px 24px;
}

.user-dropdown .el-dropdown-menu__item {
  padding: 10px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ml-1 {
  margin-left: 4px;
}

@media (max-width: 768px) {
  .nav, .header-center {
    display: none;
  }
}
</style>
