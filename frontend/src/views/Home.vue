<template>
  <div class="home-page">
    <section class="page-hero">
      <div class="page-hero__title">
        <span class="page-hero__eyebrow">内容流</span>
        <h1>发现精彩内容</h1>
        <p>探索来自创作者的深度见解与灵感故事，每一个想法都值得被看见。</p>
      </div>
    </section>

    <section class="home-grid">
      <el-card class="composer glass-card" shadow="never">
        <template #header>
          <div class="composer__header">
            <div>
              <p class="muted">开始创作</p>
              <h3 class="section-title">发布新文章</h3>
            </div>
          </div>
        </template>
        <el-input v-model="newPost.title" size="large" placeholder="文章标题" class="composer__title" />
        <el-input
          v-model="newPost.content"
          type="textarea"
          :rows="8"
          resize="none"
          placeholder="写下你的想法..."
        />
        <div class="composer__actions">
          <span class="muted">简洁写作，专注内容</span>
          <el-button type="primary" size="large" :loading="publishing" @click="publishPost">发布文章</el-button>
        </div>
      </el-card>

      <section class="feed">
        <div class="feed__header">
          <h3 class="section-title">最新文章</h3>
          <span class="pill">{{ posts.length }} 篇</span>
        </div>
        <div v-if="posts.length" class="feed__list">
          <article
            v-for="post in posts"
            :key="post.id"
            class="feed-card glass-card"
            @click="router.push(`/post/${post.id}`)"
          >
            <div class="feed-card__meta">
              <span>{{ post.author?.username || '匿名作者' }}</span>
              <span>{{ formatDate(post.created_at) }}</span>
            </div>
            <h2>{{ post.title }}</h2>
            <p>{{ excerpt(post.content) }}</p>
            <div class="feed-card__footer">
              <div class="feed-card__stats">
                <span class="stat-item">👁 {{ post.views }} 阅读</span>
                <button class="inline-action" @click.stop="likePost(post.id)">♥ {{ post.likes }} 点赞</button>
              </div>
              <span class="feed-card__link">阅读全文 →</span>
            </div>
          </article>
        </div>
        <el-empty v-else description="还没有文章，成为第一个创作者吧" />
      </section>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { ElMessage } from 'element-plus'

const router = useRouter()
const posts = ref([])
const newPost = ref({ title: '', content: '' })
const publishing = ref(false)

const fetchPosts = async () => {
  try {
    const { data } = await request.get('/posts/')
    posts.value = data
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '获取文章列表失败')
  }
}

const publishPost = async () => {
  if (!newPost.value.title || !newPost.value.content) {
    return ElMessage.warning('请填写标题和内容')
  }
  publishing.value = true
  try {
    await request.post('/posts/', newPost.value)
    ElMessage.success('发布成功')
    newPost.value = { title: '', content: '' }
    await fetchPosts()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发布失败')
  } finally {
    publishing.value = false
  }
}

const likePost = async id => {
  try {
    const { data } = await request.post(`/posts/${id}/like`)
    const post = posts.value.find(item => item.id === id)
    if (post) {
      post.likes = data.likes_count
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '点赞失败')
  }
}

const excerpt = content => (content || '').slice(0, 200) + ((content || '').length > 200 ? '...' : '')
const formatDate = value => new Date(value).toLocaleDateString('zh-CN')

onMounted(fetchPosts)
</script>

<style scoped>
.home-grid {
  display: grid;
  grid-template-columns: minmax(320px, 400px) minmax(0, 1fr);
  gap: 32px;
  align-items: start;
}

.composer {
  position: sticky;
  top: 88px;
  padding: 4px;
}

.composer__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 0 4px;
}

.composer__title {
  margin-bottom: 12px;
}

.composer__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 16px;
}

.feed__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.feed__list {
  display: grid;
  gap: 20px;
}

.feed-card {
  padding: 28px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.feed-card:hover {
  border-color: var(--accent-blue);
  transform: translateY(-2px);
}

.feed-card__meta,
.feed-card__footer,
.feed-card__stats {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.feed-card__meta {
  color: var(--text-muted);
  font-size: 13px;
}

.feed-card h2 {
  margin: 14px 0 12px;
  font-size: 24px;
  font-weight: 600;
  line-height: 1.3;
}

.feed-card p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.feed-card__footer {
  margin-top: 20px;
}

.feed-card__link {
  color: var(--accent-blue);
  font-weight: 600;
  font-size: 14px;
}

.inline-action {
  border: 0;
  background: transparent;
  color: var(--accent-blue);
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.inline-action:hover {
  background: rgba(59, 130, 246, 0.1);
}

.stat-item {
  color: var(--text-muted);
  font-size: 13px;
}

@media (max-width: 1024px) {
  .home-grid {
    grid-template-columns: 1fr;
  }

  .composer {
    position: static;
  }
}

@media (max-width: 720px) {
  .composer__actions,
  .feed__header,
  .feed-card__footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
