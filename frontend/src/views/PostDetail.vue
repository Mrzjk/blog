<template>
  <div v-if="post" class="detail-page">
    <section class="page-hero">
      <div class="page-hero__title">
        <span class="page-hero__eyebrow">文章</span>
        <h1>{{ post.title }}</h1>
        <p>{{ post.author?.username }} · {{ formatDate(post.created_at) }} · {{ post.views }} 次阅读</p>
      </div>
      <div v-if="canDeletePost" class="page-hero__actions">
        <el-button type="danger" @click="deletePost" plain>删除文章</el-button>
      </div>
    </section>

    <article class="detail-article glass-card">
      <div v-if="post.cover_image" class="detail-article__cover">
        <img :src="post.cover_image" alt="cover" />
      </div>
      <MdPreview :modelValue="post.content" class="detail-article__content" />
      <div v-if="post.tags?.length" class="detail-article__tags">
        <span v-for="tag in post.tags" :key="tag.id" class="tag-pill">#{{ tag.name }}</span>
      </div>
      <div class="detail-article__footer">
        <div class="stat-group">
          <button class="action-btn" :class="{ 'is-active': post.is_liked }" @click="likePost">
            {{ post.is_liked ? '♥ 已赞' : '♡ 点赞' }}
            <span class="count">{{ post.likes }}</span>
          </button>
          <button class="action-btn" :class="{ 'is-active': post.is_bookmarked }" @click="bookmarkPost">
            {{ post.is_bookmarked ? '★ 已收藏' : '☆ 收藏' }}
          </button>
        </div>
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

      <div class="comment-editor" v-if="userStore.isAuthenticated">
        <el-input
          v-model="newComment"
          type="textarea"
          :rows="4"
          resize="none"
          placeholder="写下你的评论..."
        />
        <el-button type="primary" size="large" @click="submitComment()">发布评论</el-button>
      </div>
      <div v-else class="comment-login-hint">
        <p>登录后可发表评论</p>
        <el-button type="primary" @click="router.push('/login')">去登录</el-button>
      </div>

      <div v-if="post.comments?.length" class="comment-list">
        <CommentItem
          v-for="comment in paginatedComments"
          :key="comment.id"
          :comment="comment"
          :all-comments="post.comments"
          :is-authenticated="userStore.isAuthenticated"
          :current-user="userStore.user"
          @reply="handleReply"
          @delete="deleteComment"
          @addFriend="addFriend"
        />

        <div v-if="totalComments > pageSize" class="pagination-container">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="totalComments"
            :page-size="pageSize"
            v-model:current-page="currentPage"
            @current-change="handlePageChange"
          />
        </div>

        <el-dialog v-model="showReplyDialog" :title="'回复 @' + replyToUsername" width="500px">
          <el-input
            v-model="replyContent"
            type="textarea"
            :rows="4"
            resize="none"
            placeholder="写下你的回复..."
          />
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="showReplyDialog = false">取消</el-button>
              <el-button type="primary" @click="submitComment(activeReplyId)">回复</el-button>
            </span>
          </template>
        </el-dialog>
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
import { useRoute, useRouter } from 'vue-router'
import request from '../utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../store/user'
import CommentItem from '../components/CommentItem.vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const post = ref(null)
const newComment = ref('')
const replyContent = ref('')
const activeReplyId = ref(null)
const replyToUsername = ref('')
const showReplyDialog = ref(false)

const rootComments = computed(() => (post.value?.comments || []).filter(comment => !comment.parent_id))

const currentPage = ref(1)
const pageSize = 10
const totalComments = computed(() => rootComments.value.length)

const paginatedComments = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return rootComments.value.slice(start, start + pageSize)
})

const handlePageChange = (page) => {
  currentPage.value = page
}

const canDeletePost = computed(() => {
  if (!userStore.isAuthenticated || !post.value) return false
  const user = userStore.user
  return post.value.author_id === user.id || user.role?.name === 'admin'
})

const fetchPostDetail = async () => {
  try {
    const { data } = await request.get(`/posts/${route.params.id}`)
    post.value = data
  } catch (error) {
    ElMessage.error('获取文章失败')
  }
}

const likePost = async () => {
  if (!userStore.isAuthenticated) {
    return router.push('/login')
  }
  try {
    const { data } = await request.post(`/posts/${post.value.id}/like`)
    post.value.likes = data.likes_count
    post.value.is_liked = data.is_liked
    ElMessage.success(data.is_liked ? '点赞成功' : '已取消点赞')
  } catch (error) {
    ElMessage.error('点赞失败')
  }
}

const bookmarkPost = async () => {
  if (!userStore.isAuthenticated) {
    return router.push('/login')
  }
  try {
    const { data } = await request.post(`/posts/${post.value.id}/bookmark`)
    post.value.is_bookmarked = data.is_bookmarked
    ElMessage.success(data.is_bookmarked ? '已收藏' : '已取消收藏')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleReply = (commentId, username) => {
  activeReplyId.value = commentId
  replyToUsername.value = username
  replyContent.value = ''
  showReplyDialog.value = true
}

const addFriend = async (friendId) => {
  try {
    await request.post(`/chat/friend-request/${friendId}`)
    ElMessage.success('好友请求已发送')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '发送好友请求失败')
  }
}

const deleteComment = async (commentId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await request.delete(`/posts/comments/${commentId}`)
    ElMessage.success('评论已删除')
    fetchPostDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const deletePost = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这篇文章吗？删除后不可恢复。', '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'error'
    })
    
    await request.delete(`/posts/${post.value.id}`)
    ElMessage.success('文章已删除')
    router.push('/')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const submitComment = async (parentId = null) => {
  const content = parentId ? replyContent.value : newComment.value
  if (!content.trim()) return
  
  try {
    await request.post('/posts/comments', {
      post_id: post.value.id,
      content: content,
      parent_id: parentId
    })
    ElMessage.success('评论成功')
    if (parentId) {
      replyContent.value = ''
      activeReplyId.value = null
      showReplyDialog.value = false
    } else {
      newComment.value = ''
    }
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
  border: 1px solid var(--border-color);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.detail-article__cover {
  margin: -40px -40px 30px -40px;
  border-radius: 12px 12px 0 0;
  overflow: hidden;
  position: relative;
}

.detail-article__cover::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 30%;
  background: linear-gradient(to top, var(--bg-card), transparent);
}

.detail-article__cover img {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.detail-article__cover:hover img {
  transform: scale(1.02);
}

.detail-article__content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-primary);
  background: transparent !important;
}

.detail-article__footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.stat-group {
  display: flex;
  gap: 16px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.action-btn:hover {
  border-color: var(--accent-blue);
  color: var(--accent-blue);
  background: rgba(56, 189, 248, 0.05);
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.1);
}

.action-btn.is-active {
  background: rgba(56, 189, 248, 0.15);
  border-color: var(--accent-blue);
  color: var(--accent-blue);
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
}

.detail-article__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 12px;
  border-radius: 6px;
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.2);
  color: var(--accent-blue);
  font-size: 12px;
  font-weight: 600;
  font-family: 'SF Mono', Consolas, monospace;
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

.comment-login-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 32px;
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px dashed var(--border-color);
  margin-bottom: 28px;
}

.comment-login-hint p {
  margin: 0;
  color: var(--text-muted);
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

.comment-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.link-btn {
  border: 0;
  background: transparent;
  color: var(--accent-blue);
  cursor: pointer;
  font-size: 13px;
  padding: 0;
}

.link-btn:hover {
  text-decoration: underline;
}

.link-btn.danger {
  color: #ef4444;
}

.reply-editor {
  margin-top: 16px;
  display: grid;
  gap: 12px;
}

.reply-editor__actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.comment-replies {
  margin-top: 16px;
  display: grid;
  gap: 12px;
  padding-left: 24px;
  border-left: 2px solid var(--border-color);
}

.comment-reply {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
}

.comment-card p,
.comment-reply p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.detail-loading {
  max-width: 800px;
  margin: 40px auto;
  padding: 40px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
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
