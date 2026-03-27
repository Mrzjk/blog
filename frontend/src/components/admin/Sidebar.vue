<template>
  <div class="sidebar">
    <el-menu
      :default-active="$route.path"
      class="el-menu-vertical"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
      :collapse="isCollapse"
    >
      <el-menu-item index="/admin/dashboard">
        <el-icon><DataLine /></el-icon>
        <template #title>控制台</template>
      </el-menu-item>
      <el-menu-item index="/admin/user-manage">
        <el-icon><User /></el-icon>
        <template #title>用户管理</template>
      </el-menu-item>
      <el-menu-item index="/admin/article-review">
        <el-icon><Document /></el-icon>
        <template #title>文章管理</template>
      </el-menu-item>
      <el-menu-item index="/admin/category">
        <el-icon><Collection /></el-icon>
        <template #title>文章类型管理</template>
      </el-menu-item>
      <el-menu-item index="/admin/system">
        <el-icon><Setting /></el-icon>
        <template #title>系统设置</template>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { DataLine, User, Document, Collection, Setting } from '@element-plus/icons-vue';

defineProps<{
  isCollapse: boolean
}>();
</script>

<style scoped>
.sidebar {
  background-color: #304156;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.el-menu-vertical {
  border-right: none;
  flex: 1;
}

.el-menu-vertical:not(.el-menu--collapse) {
  width: 220px;
}
</style>
