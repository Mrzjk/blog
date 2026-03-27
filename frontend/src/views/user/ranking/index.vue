<template>
  <div class="ranking-page">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="ranking-card" header="阅读排行榜">
          <div v-for="(item, index) in readRankings" :key="index" class="ranking-item">
            <span class="rank-num" :class="{ 'top-3': index < 3 }">{{ index + 1 }}</span>
            <span class="rank-title">{{ item.title }}</span>
            <span class="rank-count">{{ item.views }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="ranking-card" header="点赞排行榜">
          <div v-for="(item, index) in likeRankings" :key="index" class="ranking-item">
            <span class="rank-num" :class="{ 'top-3': index < 3 }">{{ index + 1 }}</span>
            <span class="rank-title">{{ item.title }}</span>
            <span class="rank-count">{{ item.likes }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="ranking-card" header="活跃用户榜">
          <div v-for="(item, index) in userRankings" :key="index" class="ranking-item">
            <span class="rank-num" :class="{ 'top-3': index < 3 }">{{ index + 1 }}</span>
            <span class="rank-title">{{ item.username }}</span>
            <span class="rank-count">Lv.{{ item.level || 1 }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import request from '@/utils/request';

const readRankings = ref<any[]>([]);
const likeRankings = ref<any[]>([]);
const userRankings = ref<any[]>([]);

onMounted(async () => {
  try {
    const { data: hotPosts } = await request.get('/posts/hot?limit=10');
    readRankings.value = [...hotPosts].sort((a, b) => b.views - a.views);
    likeRankings.value = [...hotPosts].sort((a, b) => b.likes - a.likes);
    
    const { data: hotUsers } = await request.get('/auth/ranking?limit=10');
    userRankings.value = hotUsers;
  } catch (error) {
    console.error(error);
  }
});
</script>

<style scoped>
.ranking-page {
  padding: 20px 0;
}
.ranking-card {
  height: 100%;
}
.ranking-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px dashed var(--border-color);
}
.ranking-item:last-child {
  border-bottom: none;
}
.rank-num {
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: 4px;
  margin-right: 12px;
  font-weight: bold;
  font-size: 14px;
}
.rank-num.top-3 {
  background-color: var(--accent-primary);
  color: white;
}
.rank-num.top-3:nth-child(1) {
  background-color: #f56c6c;
}
.rank-num.top-3:nth-child(2) {
  background-color: #e6a23c;
}
.rank-num.top-3:nth-child(3) {
  background-color: #67c23a;
}
.rank-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
}
.rank-title:hover {
  color: var(--accent-primary);
}
.rank-count {
  margin-left: 12px;
  color: var(--text-muted);
  font-size: 13px;
}
</style>