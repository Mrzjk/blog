<template>
  <div v-if="post" class="detail-page">
    <section class="page-hero">
      <div class="page-hero__title">
        <span class="page-hero__eyebrow">文章</span>
        <h1>{{ post.title }}</h1>
        <p>{{ post.author?.username }} · {{ formatDate(post.created_at) }} · {{ post.views }} 次阅读</p>
      </div>
    </section>

    <article class="detail-article glass-card">
      <div class="detail-article__content">{{ post.content }}</div>
      <div class="detail-article__footer">
        <span class="pill">♥ {{ post.likes }} 点赞</span>
        <el-button type="primary" size="large" @click="likePost">点赞支持</el-button>
      </div>
    </article>

    <section class="detail-comments glass-card">
      <div class="detail-comments__header">
        <div>
          <p class="muted">讨论区</p>
          <h3 class="section-title">评论区</h3>
        </div>
        <span class="pill">{{ post.comments?.length || 0 }} 条评论</span>
      </div>

      <div class="comment-editor">
        <el-input
          v-model="newComment"
          type="textarea"
          :rows="4"
          resize="none"
          placeholder="写下你的评论..."
        />
        <el-button type="primary" size="large" @click="submitComment">发布评论</el-button>
      </div>

      <div v-if="post.comments?.length" class="comment-list">
        <article v-for="comment in rootComments" :key="comment.id" class="comment-card">
          <div class="comment-card__header">
            <strong>{{ comment.author?.username }}</strong>
            <span class="muted">{{ formatDate(comment.created_at) }}</span>
          </div>
          <p>{{ comment.content }}</p>
          <div v-if="commentChildren(comment.id).length" class="comment-replies">
            <div v-for="reply in commentChildren(comment.id)" :key="reply.id" class="comment-reply">
              <div class="comment-card__header">
                <strong>{{ reply.author?.username }}</strong>
                <span class="muted">{{ formatDate(reply.created_at) }}</span>
              </div>
              <p>{{ reply.content }}</p>
            </div>
          </div>
        </article>
      </div>
      <el-empty v-else description="暂无评论，来发表第一条评论吧" />
    </section>
  </div>
  <div v-else class="detail-loading">
    <el-skeleton :rows="12" animated />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '../utils/request'
import { ElMessage } from 'element-plus'

const route = useRoute()
const post = ref(null)
const newComment = ref('')
const rootComments = computed(() => (post.value?.comments || []).filter(comment => !comment.parent_id))
const commentChildren = parentId => (post.value?.comments || []).filter(comment => comment.parent_id === parentId)

const fetchPostDetail = async () => {
  try {
    const { data } = await request.get(`/posts/${route.params.id}`)
    post.value = data
  } catch (error) {
    ElMessage.error('获取文章失败')
  }
}

const likePost = async () => {
  try {
    const { data } = await request.post(`/posts/${post.value.id}/like`)
    post.value.likes = data.likes_count
    ElMessage.success('点赞成功')
  } catch (error) {
    ElMessage.error('点赞失败')
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return
  try {
    await request.post('/posts/comments', {
      post_id: post.value.id,
      content: newComment.value
    })
    ElMessage.success('评论成功')
    newComment.value = ''
    fetchPostDetail()
  } catch (error) {
    ElMessage.error('评论失败')
  }
}

const formatDate = value => new Date(value).toLocaleString('zh-CN')

onMounted(fetchPostDetail)
</script>

<style scoped>
.detail-article,
.detail-comments {
  padding: 32px;
}

.detail-article__content {
  color: var(--text-secondary);
  font-size: 17px;
  line-height: 2;
  white-space: pre-wrap;
}

.detail-article__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.detail-comments {
  margin-top: 24px;
}

.detail-comments__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.comment-editor {
  display: grid;
  gap: 14px;
  margin-bottom: 28px;
}

.comment-list {
  display: grid;
  gap: 16px;
}

.comment-card,
.comment-reply {
  padding: 20px;
  border-radius: 12px;
  background: var(--bg-secondary);
}

.comment-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.comment-card p,
.comment-reply p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.comment-replies {
  display: grid;
  gap: 12px;
  margin-top: 16px;
  padding-left: 20px;
  border-left: 2px solid var(--border-color);
}

.detail-loading {
  max-width: 900px;
  margin: 0 auto;
  padding-top: 48px;
}

@media (max-width: 720px) {
  .detail-article__footer,
  .detail-comments__header,
  .comment-card__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
