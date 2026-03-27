<template>
  <div class="forum-page fade-in-up">
    <el-card class="glass-card">
      <template #header>
        <div class="forum-header">
          <h2><el-icon><ChatDotSquare /></el-icon> 论坛社区</h2>
          <el-button type="primary" @click="$router.push('/user/editor')">发布帖子</el-button>
        </div>
      </template>
      
      <el-table :data="posts" style="width: 100%" v-loading="loading" class="forum-table">
        <el-table-column label="标题" min-width="400">
          <template #default="{ row }">
            <div class="post-title-cell" @click="$router.push(`/user/article/${row.id}`)">
              <span class="title-text">{{ row.title }}</span>
              <el-tag size="small" v-if="row.category" type="info" class="ml-2">{{ row.category.name }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="author.username" label="作者" width="120" />
        <el-table-column label="互动" width="150">
          <template #default="{ row }">
            <div class="interaction-stats">
              <span title="浏览"><el-icon><View /></el-icon> {{ row.views }}</span>
              <span title="点赞"><el-icon><Star /></el-icon> {{ row.likes }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="发布时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="size"
          :total="total"
          background
          layout="total, prev, pager, next"
          @current-change="fetchPosts"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ChatDotSquare, View, Star } from '@element-plus/icons-vue';
import { getArticleList } from '@/api/article';

const posts = ref<any[]>([]);
const loading = ref(false);
const page = ref(1);
const size = ref(15);
const total = ref(0);

const fetchPosts = async () => {
  loading.value = true;
  try {
    const { data } = await getArticleList({
      skip: (page.value - 1) * size.value,
      limit: size.value,
      type: 'forum'
    });
    posts.value = data.items || [];
    total.value = data.total || 0;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchPosts();
});
</script>

<style scoped>
.forum-page {
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.forum-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forum-header h2 {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.post-title-cell {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.title-text {
  font-weight: 500;
  color: var(--text-primary);
  transition: color 0.3s;
}

.post-title-cell:hover .title-text {
  color: var(--accent-primary);
}

.ml-2 {
  margin-left: 8px;
}

.interaction-stats {
  display: flex;
  gap: 12px;
  color: var(--text-secondary);
}

.interaction-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.forum-table {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
}
</style>
