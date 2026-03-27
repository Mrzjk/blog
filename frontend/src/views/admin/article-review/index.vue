<template>
  <div class="article-manage">
    <el-card>
      <template #header>
        <div class="header-actions">
          <el-form :inline="true" :model="searchForm">
            <el-form-item label="搜索文章">
              <el-input v-model="searchForm.keyword" placeholder="标题/内容" clearable @keyup.enter="fetchArticles" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchArticles">搜索</el-button>
            </el-form-item>
          </el-form>
        </div>
      </template>

      <el-table :data="articles" v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="文章标题" show-overflow-tooltip />
        <el-table-column prop="author.username" label="作者" width="120" />
        <el-table-column prop="category.name" label="分类" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发布时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="handlePreview(row)">查看</el-button>
            <el-button v-if="row.status !== 'published'" size="small" type="success" @click="handleUpdateStatus(row, 'published')">发布</el-button>
            <el-button v-if="row.status !== 'draft'" size="small" type="warning" @click="handleUpdateStatus(row, 'draft')">设为草稿</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="size"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @current-change="fetchArticles"
          @size-change="fetchArticles"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { getArticleList, updateArticleStatus, deleteArticle } from '@/api/admin';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router';

const router = useRouter();

const articles = ref<any[]>([]);
const loading = ref(false);
const page = ref(1);
const size = ref(10);
const total = ref(0);

const searchForm = reactive({
  keyword: ''
});

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    published: 'success',
    draft: 'info',
    disabled: 'danger'
  };
  return map[status] || 'info';
};

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    published: '已发布',
    draft: '草稿',
    disabled: '已禁用'
  };
  return map[status] || status;
};

const fetchArticles = async () => {
  loading.value = true;
  try {
    const { data } = await getArticleList({ page: page.value, size: size.value, search: searchForm.keyword });
    
    // Support both paginated format and raw array
    if (data && typeof data === 'object') {
      if (Array.isArray(data)) {
        articles.value = data;
        total.value = data.length;
      } else if (Array.isArray(data.items)) {
        articles.value = data.items;
        total.value = data.total || data.items.length;
      } else {
        articles.value = [];
        total.value = 0;
      }
    } else {
      articles.value = [];
      total.value = 0;
    }
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handlePreview = (row: any) => {
  // Go to article detail page
  window.open(`/user/article/${row.id}`, '_blank');
};

const handleUpdateStatus = async (row: any, status: string) => {
  try {
    await updateArticleStatus(row.id, status);
    ElMessage.success('状态更新成功');
    fetchArticles();
  } catch (error) {
    // handled
  }
};

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除文章《${row.title}》吗？此操作不可恢复`, '警告', { type: 'error' });
    await deleteArticle(row.id);
    ElMessage.success('文章已删除');
    fetchArticles();
  } catch (error) {
    // cancel
  }
};

onMounted(() => {
  fetchArticles();
});
</script>

<style scoped>
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
