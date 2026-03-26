<template>
  <div class="profile-page">
    <!-- <section class="page-hero">
      <div class="page-hero__title">
        <span class="page-hero__eyebrow">我的</span>
        <h1>个人主页</h1>
        <p>管理你的个人资料，设置头像和简介。</p>
      </div>
    </section> -->

    <div class="profile-grid">
      <el-card class="profile-summary glass-card" shadow="never">
        <div class="profile-summary__avatar">{{ userInitial }}</div>
        <h2>{{ userStore.user?.username }}</h2>
        <p class="muted">{{ form.bio || '添加一句简介吧' }}</p>
        <div class="profile-stats">
          <div class="profile-stat">
            <strong>Lv.{{ userStore.user?.level || 1 }}</strong>
            <span>当前等级</span>
          </div>
          <div class="profile-stat">
            <strong>{{ userStore.user?.exp || 0 }}</strong>
            <span>经验值</span>
          </div>
        </div>
      </el-card>

      <div class="profile-content">
        <div class="profile-actions-top">
          <el-button type="primary" size="large" @click="router.push('/editor')">
            <el-icon><EditPen /></el-icon> 写文章
          </el-button>
        </div>
        <el-tabs v-model="activeTab">
          <el-tab-pane label="添加用户" name="add_user">
            <div class="mb-6">
              <el-input 
                v-model="searchQuery" 
                placeholder="搜索用户名添加好友..." 
                size="large" 
                @input="searchUsers" 
                clearable 
                prefix-icon="Search" 
                class="search-input w-full max-w-md" 
              />
            </div>
            
            <div v-if="searchResults.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="user in searchResults"
                :key="user.id"
                class="glass-card p-4 flex items-center justify-between"
              >
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-lg bg-tertiary flex items-center justify-center text-secondary font-bold text-lg border border-border">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </div>
                  <div class="flex flex-col text-left">
                    <strong class="text-primary">{{ user.username }}</strong>
                    <span class="muted text-xs font-mono">ID: {{ user.id }}</span>
                  </div>
                </div>
                <el-button type="primary" plain @click="addFriend(user.id)">添加好友</el-button>
              </div>
            </div>
            <el-empty v-else-if="searchQuery" description="未找到匹配的用户" />
            <el-empty v-else description="输入用户名搜索添加好友" :image-size="100" />
          </el-tab-pane>

          <el-tab-pane label="我的文章" name="posts">
            <div v-if="loadingPosts" class="feed__list">
              <el-skeleton :rows="5" animated v-for="i in 3" :key="i" class="glass-card" style="padding: 20px; margin-bottom: 16px;" />
            </div>
            <div v-else-if="userPosts.length" class="feed__list">
              <article v-for="post in paginatedUserPosts" :key="post.id" class="feed-card glass-card" @click="router.push(`/post/${post.id}`)">
                <div class="feed-card__header">
                  <span class="feed-card__date">{{ formatDate(post.created_at) }}</span>
                </div>
                <div class="feed-card__content">
                  <h2>{{ post.title }}</h2>
                  <p>{{ excerpt(post.content) }}</p>
                </div>
                <div class="feed-card__footer">
                  <div class="feed-card__stats">
                    <span class="stat-item">👁 {{ post.views }} 阅读</span>
                    <span class="stat-item">♥ {{ post.likes }} 点赞</span>
                  </div>
                </div>
              </article>
              
              <!-- 文章分页 -->
              <div class="pagination-container" v-if="userPosts.length > postsPageSize">
                <el-pagination
                  background
                  layout="prev, pager, next"
                  :total="userPosts.length"
                  :page-size="postsPageSize"
                  v-model:current-page="postsCurrentPage"
                  @current-change="handlePostsPageChange"
                />
              </div>
            </div>
            <el-empty v-else description="还没有发布过文章" />
          </el-tab-pane>
          <el-tab-pane label="我的评论" name="comments">
            <div v-if="loadingComments" class="feed__list">
              <el-skeleton :rows="3" animated v-for="i in 3" :key="i" class="glass-card" style="padding: 20px; margin-bottom: 16px;" />
            </div>
            <div v-else-if="userComments.length" class="comment-list">
              <div v-for="comment in userComments" :key="comment.id" class="comment-item glass-card" @click="router.push(`/post/${comment.post_id}`)">
                <div class="comment-meta">
                  <span class="muted">评论于文章《{{ comment.post?.title || '未知文章' }}》</span>
                  <span class="muted">{{ formatDate(comment.created_at) }}</span>
                </div>
                <p class="comment-content">{{ comment.content }}</p>
              </div>
            </div>
            <el-empty v-else description="还没有发表过评论" />
          </el-tab-pane>
          <el-tab-pane label="个人设置" name="settings">
            <el-card class="profile-form glass-card" shadow="never">
              <template #header>
                <div class="profile-form__header">
                  <div>
                    <p class="muted">编辑资料</p>
                    <h3 class="section-title">基本信息</h3>
                  </div>
                  <el-button type="primary" size="large" :loading="saving" @click="saveProfile">保存修改</el-button>
                </div>
              </template>

              <el-form :model="form" label-position="top">
                <el-form-item label="用户名">
                  <el-input v-model="form.username" size="large" />
                </el-form-item>
                <el-form-item label="邮箱">
                  <el-input v-model="form.email" size="large" />
                </el-form-item>
                <el-form-item label="个人简介">
                  <el-input v-model="form.bio" type="textarea" :rows="4" resize="none" placeholder="介绍一下自己" />
                </el-form-item>
                <el-form-item label="生日">
                  <el-date-picker v-model="form.birthday" type="date" placeholder="选择生日" size="large" style="width: 100%" />
                </el-form-item>
                <el-form-item label="修改密码">
                  <el-input v-model="form.password" type="password" size="large" show-password placeholder="不修改请留空" />
                </el-form-item>
              </el-form>
            </el-card>
          </el-tab-pane>
          
          <el-tab-pane v-if="isAdmin" label="分类管理" name="categories">
            <el-card class="glass-card" shadow="never">
              <div class="category-manager">
                <div class="category-add">
                  <el-input v-model="newCategoryName" placeholder="新分类名称" style="width: 200px" />
                  <el-input v-model="newCategoryDesc" placeholder="分类描述" style="width: 300px; margin-left: 10px;" />
                  <el-button type="primary" style="margin-left: 10px;" @click="addCategory">添加</el-button>
                </div>
                <el-table :data="categories" style="width: 100%; margin-top: 20px;">
                  <el-table-column prop="id" label="ID" width="80" />
                  <el-table-column prop="name" label="名称" width="150" />
                  <el-table-column prop="description" label="描述" />
                  <el-table-column label="操作" width="120">
                    <template #default="scope">
                      <el-button size="small" type="danger" @click="deleteCategory(scope.row.id)">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import request from '../utils/request'
import { ElMessage } from 'element-plus'
import { EditPen, Search } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const saving = ref(false)
const activeTab = ref('posts')
const userPosts = ref([])
const userComments = ref([])
const loadingPosts = ref(false)
const loadingComments = ref(false)

// 搜索用户相关
const searchQuery = ref('')
const searchResults = ref([])

const searchUsers = async () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }
  try {
    const { data } = await request.get(`/auth/?q=${searchQuery.value}`)
    searchResults.value = data.filter(u => u.id !== userStore.user?.id)
  } catch (e) {
    console.error('搜索用户失败', e)
  }
}

const addFriend = async (friendId) => {
  try {
    await request.post(`/chat/friend-request/${friendId}`)
    ElMessage.success('好友请求已发送')
    searchQuery.value = ''
    searchResults.value = []
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '发送失败')
  }
}

// 文章分页状态
const postsCurrentPage = ref(1)
const postsPageSize = ref(5)

const paginatedUserPosts = computed(() => {
  const start = (postsCurrentPage.value - 1) * postsPageSize.value
  const end = start + postsPageSize.value
  return userPosts.value.slice(start, end)
})

const handlePostsPageChange = (page) => {
  postsCurrentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const form = ref({
  username: '',
  email: '',
  bio: '',
  birthday: null,
  password: ''
})
const userInitial = computed(() => userStore.user?.username?.charAt(0)?.toUpperCase() || 'U')
const isAdmin = computed(() => userStore.user?.role?.name === 'admin')

const categories = ref([])
const newCategoryName = ref('')
const newCategoryDesc = ref('')

const fetchCategories = async () => {
  if (!isAdmin.value) return
  try {
    const { data } = await request.get('/categories/')
    categories.value = data
  } catch (error) {
    ElMessage.error('获取分类失败')
  }
}

const addCategory = async () => {
  if (!newCategoryName.value) return
  try {
    await request.post('/categories/', {
      name: newCategoryName.value,
      description: newCategoryDesc.value
    })
    ElMessage.success('分类添加成功')
    newCategoryName.value = ''
    newCategoryDesc.value = ''
    fetchCategories()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const deleteCategory = async (id) => {
  try {
    await request.delete(`/categories/${id}`)
    ElMessage.success('分类删除成功')
    fetchCategories()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const loadUserContent = async () => {
  if (!userStore.user) return
  
  loadingPosts.value = true
  try {
    const { data } = await request.get(`/posts/user/${userStore.user.id}`)
    userPosts.value = data
  } catch (error) {
    ElMessage.error('获取文章失败')
  } finally {
    loadingPosts.value = false
  }

  loadingComments.value = true
  try {
    const { data } = await request.get(`/posts/user/${userStore.user.id}/comments`)
    userComments.value = data
  } catch (error) {
    ElMessage.error('获取评论失败')
  } finally {
    loadingComments.value = false
  }
}

const excerpt = content => (content || '').slice(0, 100) + ((content || '').length > 100 ? '...' : '')
const formatDate = value => new Date(value).toLocaleDateString('zh-CN')

onMounted(() => {
  if (userStore.user) {
    form.value.username = userStore.user.username || ''
    form.value.email = userStore.user.email || ''
    form.value.bio = userStore.user.bio || ''
    
    if (userStore.user.birthday) {
      const d = new Date(userStore.user.birthday)
      form.value.birthday = isNaN(d.getTime()) ? null : d
    } else {
      form.value.birthday = null
    }

    loadUserContent()
    if (isAdmin.value) {
      fetchCategories()
    }
  }
})

const saveProfile = async () => {
  saving.value = true
  try {
    const updateData = {
      username: form.value.username,
      email: form.value.email,
      bio: form.value.bio,
      birthday: form.value.birthday ? new Date(form.value.birthday).toISOString() : null
    }
    if (form.value.password) {
      updateData.password = form.value.password
    }

    const { data } = await request.put('/auth/me', updateData)
    userStore.setUser(data)
    ElMessage.success('资料已更新')
    form.value.password = ''
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.search-input :deep(.el-input__wrapper) {
  background-color: var(--bg-card);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  box-shadow: none;
  transition: all 0.3s ease;
}

.search-input :deep(.el-input__wrapper):hover,
.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.2);
}

.profile-grid {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 24px;
}

.profile-summary,
.profile-form {
  padding: 28px;
}

.profile-summary {
  text-align: center;
}

.profile-summary__avatar {
  display: grid;
  place-items: center;
  width: 88px;
  height: 88px;
  margin: 0 auto 18px;
  border-radius: 24px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  color: #fff;
  font-size: 32px;
  font-weight: 700;
}

.profile-summary h2 {
  margin: 0 0 10px;
  font-size: 24px;
  font-weight: 600;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 24px;
}

.profile-actions-top {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.profile-stat {
  padding: 16px 12px;
  border-radius: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-bottom: 16px;
}

.profile-stat strong {
  display: block;
  margin-bottom: 4px;
  font-size: 24px;
  font-weight: 600;
}

.profile-stat span {
  color: var(--text-muted);
  font-size: 12px;
}

.profile-content {
  display: flex;
  flex-direction: column;
}

.feed-card {
  padding: 20px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.feed-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.feed-card__header {
  margin-bottom: 12px;
}

.feed-card__date {
  color: var(--text-muted);
  font-size: 13px;
}

.feed-card__content h2 {
  margin: 0 0 8px;
  font-size: 18px;
  color: var(--text-primary);
}

.feed-card__content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
}

.feed-card__footer {
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.feed-card__stats {
  display: flex;
  gap: 16px;
  color: var(--text-muted);
  font-size: 13px;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  padding: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.comment-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.comment-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.comment-content {
  margin: 0;
  color: var(--text-primary);
  line-height: 1.6;
}

.profile-form__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

@media (max-width: 960px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>
