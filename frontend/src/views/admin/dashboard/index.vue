<template>
  <div class="dashboard" v-loading="loading">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="title">总用户数</div>
            <div class="value">{{ stats.total_users }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="title">文章总数</div>
            <div class="value">{{ stats.total_posts }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="title">今日新增用户</div>
            <div class="value text-success">{{ stats.new_users_today }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="title">待审核文章</div>
            <div class="value text-warning">{{ stats.pending_review_posts }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="mt-4" header="近期动态">
      <el-empty description="暂无图表数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getDashboardStats } from '@/api/admin';

const loading = ref(false);
const stats = ref({
  total_users: 0,
  total_posts: 0,
  new_users_today: 0,
  pending_review_posts: 0
});

const fetchStats = async () => {
  loading.value = true;
  try {
    const { data } = await getDashboardStats();
    stats.value = data;
  } catch (error) {
    console.error('Failed to fetch dashboard stats', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchStats();
});
</script>

<style scoped>
.stat-card {
  text-align: center;
}
.title {
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}
.value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}
.text-success {
  color: #67c23a;
}
.text-warning {
  color: #e6a23c;
}
.mt-4 {
  margin-top: 20px;
}
</style>
