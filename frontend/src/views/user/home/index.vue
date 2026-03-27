<template>
  <div class="home-container">
    <!-- 左侧分类与标签 -->
    <aside class="sidebar-left">
      <el-card class="category-card mb-4" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Menu /></el-icon>
            <span>文章分类</span>
          </div>
        </template>
        <ul class="category-list">
          <li 
            :class="{ active: activeCategory === '' }" 
            @click="handleCategoryClick('')"
          >
            <span class="cat-name">全部文章</span>
            <span class="cat-count">{{ total }}</span>
          </li>
          <li 
            v-for="cat in categories" 
            :key="cat.id"
            :class="{ active: activeCategory === String(cat.id) }"
            @click="handleCategoryClick(cat.id)"
          >
            <span class="cat-name">{{ cat.name }}</span>
            <span class="cat-count">{{ cat.count || 0 }}</span>
          </li>
        </ul>
      </el-card>

      <el-card class="tag-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><CollectionTag /></el-icon>
            <span>热门标签</span>
          </div>
        </template>
        <div class="tags-cloud">
          <el-tag 
            v-for="tag in tags" 
            :key="tag.id" 
            class="cloud-tag"
            :effect="activeTag === String(tag.id) ? 'dark' : 'light'"
            :type="activeTag === String(tag.id) ? 'primary' : ''"
            round
            @click="handleTagClick(tag.id)"
          >
            {{ tag.name }} ({{ tag.count || 0 }})
          </el-tag>
        </div>
      </el-card>
    </aside>

    <!-- 右侧文章流 -->
    <main class="main-content">
      <div class="article-grid" v-loading="loading">
        <el-empty v-if="articles.length === 0" description="暂无文章" />
        
        <el-card 
          v-for="article in articles" 
          :key="article.id" 
          class="article-card glass-card" 
          shadow="hover" 
          @click="$router.push(`/user/article/${article.id}`)"
        >
          <div class="article-cover" v-if="article.cover_image">
            <el-image :src="article.cover_image" fit="cover" lazy>
              <template #error>
                <div class="image-slot">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
          </div>
          
          <div class="article-info">
            <h2 class="article-title">{{ article.title }}</h2>
            <p class="article-summary">{{ article.summary || article.content?.substring(0, 100).replace(/<[^>]+>/g, '') + '...' || '暂无摘要' }}</p>
            
            <div class="article-tags" v-if="article.tags?.length || article.category || article.type">
              <span class="category-text" v-if="article.type === 'forum'" style="color: #e6a23c; border-color: #f5dab1;">
                <el-icon><ChatDotSquare /></el-icon> 帖子
              </span>
              <span class="category-text" v-else style="color: #67c23a; border-color: #e1f3d8;">
                <el-icon><Document /></el-icon> 博客
              </span>
              <span class="category-text" v-if="article.category">
                <el-icon><Menu /></el-icon> {{ article.category.name }}
              </span>
              <span class="tag-text" v-for="tag in article.tags?.slice(0, 3) || []" :key="tag.id">#{{ tag.name }}</span>
            </div>
            
            <div class="article-meta-bottom">
              <div class="author-info">
                <div class="author-left">
                  <div class="mini-avatar">{{ article.author?.username?.charAt(0).toUpperCase() || 'U' }}</div>
                  <span class="author-name">{{ article.author?.username || '佚名' }}</span>
                </div>
                <span class="publish-time">{{ new Date(article.created_at).toLocaleDateString() }}</span>
              </div>
              <div class="stats-info">
                <span class="meta-item"><el-icon><View /></el-icon> {{ article.views || 0 }}</span>
                <span class="meta-item"><el-icon><Star /></el-icon> {{ article.likes || 0 }}</span>
                <span class="meta-item"><el-icon><ChatDotSquare /></el-icon> {{ article.comments_count || 0 }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>
      
      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="size"
          :page-sizes="[6, 12, 18, 24, 30]"
          :total="total"
          background
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="fetchArticles"
        />
      </div>

      <!-- 底部联系方式 -->
      <footer class="blog-footer">
        <div class="footer-content">
          <p>© 2026 Blog System. All rights reserved.</p>
          <div class="contact-info">
            <a href="mailto:contact@blog.com"><el-icon><Message /></el-icon> contact@blog.com</a>
            <el-divider direction="vertical" />
            <a href="#"><el-icon><Link /></el-icon> GitHub</a>
            <el-divider direction="vertical" />
            <a href="#"><el-icon><Position /></el-icon> Twitter</a>
          </div>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { getArticleList, getCategories, getHotArticles, getTags } from '@/api/article';
import { User, View, Star, Menu, CollectionTag, ChatDotSquare, Picture, Message, Link, Position, Document } from '@element-plus/icons-vue';

const route = useRoute();

const articles = ref<any[]>([]);
const categories = ref<any[]>([]);
const tags = ref<any[]>([]);

const loading = ref(false);
const page = ref(1);
const size = ref(6);
const total = ref(0);
const activeCategory = ref('');
const activeTag = ref('');
const searchQuery = ref('');

const fetchArticles = async () => {
  loading.value = true;
  try {
    const { data } = await getArticleList({
      skip: (page.value - 1) * size.value,
      limit: size.value,
      category_id: activeCategory.value || undefined,
      tag_id: activeTag.value || undefined,
      search: searchQuery.value || undefined,
      type: 'blog'
    });
    
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

const handleCategoryClick = (id: string | number) => {
  activeCategory.value = String(id);
  activeTag.value = ''; // Reset tag filter when category is clicked
  page.value = 1;
  fetchArticles();
};

const handleTagClick = (id: string | number) => {
  activeTag.value = String(id);
  activeCategory.value = ''; // Reset category filter when tag is clicked
  page.value = 1;
  fetchArticles();
};

const handleSizeChange = (newSize: number) => {
  size.value = newSize;
  page.value = 1; // Reset to first page when changing size
  fetchArticles();
};

const initData = async () => {
  try {
    const [catRes, tagRes] = await Promise.all([
      getCategories(),
      getTags()
    ]);
    categories.value = catRes.data || [];
    tags.value = tagRes.data || [];
  } catch (error) {
    console.error(error);
  }
};

watch(() => route.query.search, (newSearch) => {
  if (newSearch !== undefined) {
    searchQuery.value = newSearch as string;
    page.value = 1;
    fetchArticles();
  } else if (searchQuery.value) {
    searchQuery.value = '';
    page.value = 1;
    fetchArticles();
  }
});

onMounted(() => {
  if (route.query.search) {
    searchQuery.value = route.query.search as string;
  }
  initData();
  fetchArticles();
});
</script>

<style scoped>
.home-container {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
  align-items: start;
  max-width: 1200px;
  margin: 0 auto;
}

/* 通用卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: var(--text-primary);
}

.mb-4 { margin-bottom: 16px; }

/* 左侧栏 */
.sidebar-left .el-card {
  border-radius: 12px;
  border: none;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-secondary);
}

.category-list li:hover {
  background-color: var(--bg-hover);
  color: var(--accent-primary);
}

.category-list li.active {
  background-color: var(--accent-primary);
  color: #fff;
}

.cat-count {
  background: var(--bg-secondary);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: var(--text-muted);
}

.category-list li.active .cat-count {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.cloud-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.cloud-tag:hover {
  transform: scale(1.05);
}

/* 中间内容区 (瀑布流/小卡片风格) */
.main-content {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 100px);
}

.article-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  align-items: start;
}

.article-card {
  border-radius: 12px;
  padding: 0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background: var(--bg-primary);
  break-inside: avoid;
}

.article-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.article-card :deep(.el-card__body) {
  padding: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.article-cover {
  width: 100%;
  max-height: 200px;
  overflow: hidden;
  border-radius: 12px 12px 0 0;
}

.article-cover .el-image {
  width: 100%;
  height: 100%;
  transition: transform 0.5s ease;
}

.article-card:hover .article-cover .el-image {
  transform: scale(1.05);
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 32px;
}

.article-info {
  padding: 12px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.article-title {
  margin: 0 0 6px 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
  transition: color 0.3s;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-card:hover .article-title {
  color: var(--accent-primary);
}

.article-summary {
  color: var(--text-secondary);
  font-size: 12px;
  line-height: 1.5;
  margin: 0 0 10px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.article-tags {
  margin-bottom: 10px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}

.category-text {
  background: var(--bg-hover);
  color: var(--text-primary);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 2px;
  border: 1px solid var(--border-color);
}

.tag-text {
  background: var(--bg-hover);
  color: var(--accent-primary);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
}

.article-meta-bottom {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid var(--border-color);
  padding-top: 10px;
  margin-top: auto;
}

.author-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.author-left {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 12px;
}

.mini-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 10px;
  font-weight: bold;
}

.publish-time {
  color: var(--text-muted);
  font-size: 11px;
}

.stats-info {
  display: flex;
  justify-content: space-between;
  color: var(--text-muted);
  font-size: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-wrapper {
  margin-top: 32px;
  margin-bottom: 32px;
  display: flex;
  justify-content: center;
}

.blog-footer {
  margin-top: auto;
  padding: 24px 0;
  border-top: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 14px;
}

.footer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.contact-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.contact-info a {
  color: var(--text-secondary);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: color 0.3s;
}

.contact-info a:hover {
  color: var(--accent-primary);
}

/* 响应式 */
@media (max-width: 1024px) {
  .home-container {
    grid-template-columns: 200px 1fr;
  }
  .article-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .home-container {
    grid-template-columns: 1fr;
  }
  .sidebar-left {
    display: none;
  }
  .article-grid {
    grid-template-columns: 1fr;
  }
}
</style>
