<template>
  <el-container class="admin-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar-container">
      <Sidebar :is-collapse="isCollapse" />
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <div class="logo">
            <span class="logo-icon">🔥</span> <span v-show="!isMobile">BlogAdmin</span>
          </div>
        </div>
        <div class="user-info">
          <el-dropdown trigger="click">
            <span class="el-dropdown-link">
              <el-avatar :size="32" class="admin-avatar">{{ userStore.userInfo?.username?.charAt(0).toUpperCase() || 'A' }}</el-avatar>
              <span class="admin-name" v-show="!isMobile">{{ userStore.userInfo?.username || 'Admin' }}</span>
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/user/home')">返回前台</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useUserStore } from '@/store/user';
import { useRouter } from 'vue-router';
import { ArrowDown, Fold, Expand } from '@element-plus/icons-vue';
import Sidebar from '@/components/admin/Sidebar.vue';

const userStore = useUserStore();
const router = useRouter();

const isCollapse = ref(false);
const isMobile = ref(false);

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768;
  isCollapse.value = isMobile.value;
};

onMounted(() => {
  checkMobile();
  window.addEventListener('resize', checkMobile);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile);
});

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value;
};

const handleLogout = () => {
  userStore.logout();
  router.push('/user/home');
};
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  background-color: var(--bg-secondary, #f5f7fa);
}

.sidebar-container {
  transition: width 0.3s ease;
  background-color: #304156;
  overflow: hidden;
}

.header {
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  padding: 0 20px;
  height: 60px;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
  transition: color 0.3s;
}

.collapse-btn:hover {
  color: var(--el-color-primary);
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  font-size: 24px;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.admin-avatar {
  background-color: var(--el-color-primary);
  color: #fff;
  font-weight: bold;
}

.admin-name {
  font-weight: 500;
  color: #333;
}
</style>
