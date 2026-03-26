<template>
  <div class="min-h-screen bg-primary py-6">
    <div class="w-full">
      <div class="flex flex-col lg:flex-row gap-6">
        
        <!-- 左侧栏 (1/4) -->
        <aside class="w-full lg:w-1/4 space-y-6 flex-shrink-0">
          
          <!-- 作者名片 -->
          <div class="bg-card rounded-2xl shadow-lg hover:shadow-xl transition-all p-5 border border-border flex flex-col items-center">
            <div class="w-20 h-20 rounded-full bg-gradient-to-br from-accent to-accent-purple text-white flex items-center justify-center text-3xl font-bold shadow-lg mb-4">
              J
            </div>
            <h2 class="text-xl font-bold text-primary mb-1">Jiku.Zhao</h2>
            <p class="text-sm text-muted mb-4">分享知识，连接世界</p>
            <div class="flex gap-4 text-sm w-full justify-center border-t border-border pt-4">
              <div class="text-center cursor-pointer hover:text-accent transition-colors">
                <div class="font-bold text-accent">{{ totalBlogs }}</div>
                <div class="text-muted text-xs">文章</div>
              </div>
              <div class="text-center cursor-pointer hover:text-accent transition-colors">
                <div class="font-bold text-accent">{{ tags.length }}</div>
                <div class="text-muted text-xs">标签</div>
              </div>
            </div>
          </div>
          
          <!-- 分类列表 -->
          <div class="bg-card rounded-2xl shadow-lg hover:shadow-xl transition-all p-5 border border-border">
            <h3 class="text-lg font-bold text-primary mb-4 flex items-center gap-2">
              <el-icon class="text-accent"><Folder /></el-icon> 博客分类
            </h3>
            <ul class="space-y-2">
              <li 
                v-for="cat in categories" 
                :key="cat.id"
                @click="selectCategory(cat)"
                class="flex justify-between items-center p-2 rounded-lg cursor-pointer transition-all duration-300"
                :class="activeCategory?.id === cat.id ? 'bg-accent/20 text-accent font-medium border border-accent/30' : 'hover:bg-hover text-secondary border border-transparent'"
              >
                <span>{{ cat.name }}</span>
                <span class="bg-tertiary text-muted text-xs py-1 px-2 rounded-md border border-border">{{ cat.count || Math.floor(Math.random() * 20) + 1 }}</span>
              </li>
              <li 
                v-if="activeCategory" 
                @click="clearFilters"
                class="text-sm text-muted hover:text-accent cursor-pointer mt-3 text-center transition-colors"
              >
                清除筛选
              </li>
            </ul>
          </div>

          <!-- 热门博客 (按浏览量/点赞排序) -->
          <div class="bg-card rounded-2xl shadow-lg hover:shadow-xl transition-all p-5 border border-border">
            <h3 class="text-lg font-bold text-primary mb-4 flex items-center gap-2">
              <el-icon class="text-danger"><TrendCharts /></el-icon> 热门博客
            </h3>
            <ul class="space-y-4">
              <li 
                v-for="(post, index) in hotPosts" 
                :key="post.id"
                @click="goToPost(post.id)"
                class="flex gap-3 cursor-pointer group p-2 rounded-lg hover:bg-hover transition-colors"
              >
                <span class="text-xl font-black italic" :class="index < 3 ? 'text-accent drop-shadow-md' : 'text-muted'">
                  {{ index + 1 }}
                </span>
                <div>
                  <h4 class="text-sm font-medium text-primary group-hover:text-accent transition-colors line-clamp-2 leading-snug">
                    {{ post.title }}
                  </h4>
                  <p class="text-xs text-muted mt-1.5 flex items-center gap-1 font-mono">
                    <el-icon><View /></el-icon> {{ post.views.toLocaleString() }}
                  </p>
                </div>
              </li>
            </ul>
          </div>

          <!-- 标签云 -->
          <div class="bg-card rounded-2xl shadow-lg hover:shadow-xl transition-all p-5 border border-border">
            <h3 class="text-lg font-bold text-primary mb-4 flex items-center gap-2">
              <el-icon class="text-accent-purple"><CollectionTag /></el-icon> 标签云
            </h3>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="tag in tags" 
                :key="tag.name"
                @click="selectTag(tag)"
                class="text-xs px-3 py-1.5 rounded-md cursor-pointer transition-all border font-medium tracking-wide"
                :class="activeTag?.name === tag.name ? 'bg-accent/20 text-accent border-accent shadow-[0_0_10px_rgba(56,189,248,0.2)]' : 'bg-tertiary text-secondary border-border hover:border-accent/50 hover:text-accent'"
              >
                #{{ tag.name }}
              </span>
            </div>
          </div>
          <!-- 社交链接 -->
          <div class="bg-card rounded-2xl shadow-lg hover:shadow-xl transition-all p-5 border border-border">
            <h3 class="text-lg font-bold text-primary mb-4 flex items-center gap-2">
              <el-icon class="text-accent"><Link /></el-icon> 关注我
            </h3>
            <div class="flex gap-3">
              <a href="#" class="w-10 h-10 rounded-full bg-tertiary flex items-center justify-center text-secondary hover:bg-accent hover:text-white transition-all shadow-sm">
                <el-icon><Position /></el-icon>
              </a>
              <a href="#" class="w-10 h-10 rounded-full bg-tertiary flex items-center justify-center text-secondary hover:bg-accent hover:text-white transition-all shadow-sm">
                <el-icon><Message /></el-icon>
              </a>
              <a href="#" class="w-10 h-10 rounded-full bg-tertiary flex items-center justify-center text-secondary hover:bg-accent hover:text-white transition-all shadow-sm">
                <el-icon><Star /></el-icon>
              </a>
            </div>
          </div>
        </aside>

        <!-- 右侧主内容区 (3/4) -->
        <main class="w-full lg:w-3/4 flex flex-col">
          
          <!-- 状态头 -->
          <div class="flex justify-between items-center mb-6 bg-card p-4 rounded-2xl shadow-md border border-border backdrop-blur-sm">
            <div class="text-secondary font-medium tracking-wide flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-accent animate-pulse"></div>
              <template v-if="activeCategory">
                分类：<span class="text-accent font-bold">{{ activeCategory.name }}</span>
              </template>
              <template v-else-if="activeTag">
                标签：<span class="text-accent font-bold">#{{ activeTag.name }}</span>
              </template>
              <template v-else>
                ALL_SYSTEM_LOGS // 全部博客
              </template>
            </div>
            <div class="text-sm text-muted font-mono">
              [FOUND: <span class="text-accent font-bold">{{ totalBlogs }}</span>]
            </div>
          </div>

          <!-- 博客网格 -->
          <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <el-skeleton v-for="i in 6" :key="i" animated class="bg-card rounded-2xl p-4 shadow-md border border-border">
              <template #template>
                <el-skeleton-item variant="image" class="w-full h-44 rounded-xl mb-4" style="--el-skeleton-color: var(--bg-tertiary); --el-skeleton-to-color: var(--border-color);" />
                <el-skeleton-item variant="p" class="w-3/4 h-5 mb-2" style="--el-skeleton-color: var(--bg-tertiary); --el-skeleton-to-color: var(--border-color);" />
                <el-skeleton-item variant="text" class="w-full h-4 mb-1" style="--el-skeleton-color: var(--bg-tertiary); --el-skeleton-to-color: var(--border-color);" />
                <el-skeleton-item variant="text" class="w-5/6 h-4 mb-4" style="--el-skeleton-color: var(--bg-tertiary); --el-skeleton-to-color: var(--border-color);" />
                <div class="flex justify-between">
                  <el-skeleton-item variant="text" class="w-1/3 h-4" style="--el-skeleton-color: var(--bg-tertiary); --el-skeleton-to-color: var(--border-color);" />
                  <el-skeleton-item variant="text" class="w-1/4 h-4" style="--el-skeleton-color: var(--bg-tertiary); --el-skeleton-to-color: var(--border-color);" />
                </div>
              </template>
            </el-skeleton>
          </div>

          <div v-else-if="paginatedBlogs.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <!-- 博客卡片 -->
            <div 
              v-for="post in paginatedBlogs" 
              :key="post.id"
              @click="goToPost(post.id)"
              class="bg-card rounded-2xl shadow-md border border-border overflow-hidden cursor-pointer transition-all duration-300 hover:-translate-y-1.5 hover:shadow-[0_8px_30px_rgba(0,0,0,0.5)] hover:border-accent/40 flex flex-col h-full group"
            >
              <!-- 封面 --> 
              <div class="h-44 overflow-hidden relative">
                <div class="absolute inset-0 bg-gradient-to-t from-bg-card to-transparent z-10 opacity-60"></div>
                <img 
                  :src="post.cover_image || 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80'" 
                  class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                  alt="cover"
                />
                <div v-if="post.category" class="absolute top-3 left-3 z-20 bg-black/60 backdrop-blur-md text-accent border border-accent/30 text-xs font-bold px-2.5 py-1 rounded-md shadow-lg">
                  {{ post.category.name }}
                </div>
              </div>
              
              <!-- 内容 -->
              <div class="p-5 flex flex-col flex-1 relative z-20 -mt-6 bg-card rounded-t-2xl">
                <h2 class="text-lg font-bold text-primary mb-2 line-clamp-2 leading-tight group-hover:text-accent transition-colors">
                  {{ post.title }}
                </h2>
                <p class="text-sm text-secondary line-clamp-3 mb-4 flex-1">
                  {{ post.content.replace(/[#*`>]/g, '').substring(0, 100) }}...
                </p>
                
                <!-- 标签 -->
                <div class="flex flex-wrap gap-1.5 mb-4">
                  <span v-for="tag in (post.tags || []).slice(0, 3)" :key="tag.id" class="text-[10px] bg-tertiary border border-border text-muted px-2 py-0.5 rounded-md font-mono tracking-wider">
                    #{{ tag.name }}
                  </span>
                </div>
                
                <!-- 底部元信息 -->
                <div class="flex items-center justify-between mt-auto pt-4 border-t border-border">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-accent to-accent-purple text-white flex items-center justify-center text-xs font-bold shadow-md">
                      {{ post.author?.username?.charAt(0).toUpperCase() || 'U' }}
                    </div>
                    <span class="text-xs text-secondary font-medium">{{ post.author?.username || 'SYS_ADMIN' }}</span>
                  </div>
                  <div class="flex items-center gap-3 text-xs text-muted font-mono">
                    <span class="flex items-center gap-1 hover:text-accent transition-colors"><el-icon><View /></el-icon> {{ post.views }}</span>
                    <span class="flex items-center gap-1 hover:text-accent transition-colors"><el-icon><Star /></el-icon> {{ post.likes }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <el-empty v-else description="404 NOT FOUND" class="bg-card rounded-2xl shadow-md py-16 border border-border" />

          <!-- 分页 -->
          <div class="mt-10 flex justify-center pb-8" v-if="totalBlogs > 0">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="totalBlogs"
              :hide-on-single-page="true"
              background
              layout="prev, pager, next"
              class="tech-pagination"
              @current-change="handlePageChange"
            />
          </div>


        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { Folder, TrendCharts, CollectionTag, View, Star, Link, Position, Message } from '@element-plus/icons-vue'

const router = useRouter()

// 状态
const loading = ref(true)
const allPosts = ref([])
const categories = ref([])
const hotPosts = ref([])
const tags = ref([])

const activeCategory = ref(null)
const activeTag = ref(null)

// 分页状态
const currentPage = ref(1)
const pageSize = ref(9)

// 计算过滤后的博客
const filteredBlogs = computed(() => {
  let result = allPosts.value
  if (activeCategory.value) {
    result = result.filter(post => post.category?.id === activeCategory.value.id)
  } else if (activeTag.value) {
    result = result.filter(post => post.tags?.some(t => t.name === activeTag.value.name))
  }
  return result
})

const totalBlogs = computed(() => filteredBlogs.value.length)

// 当前页数据
const paginatedBlogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredBlogs.value.slice(start, end)
})

// 方法
const goToPost = (id) => {
  router.push(`/post/${id}`)
}

const handlePageChange = (page) => {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const selectCategory = (cat) => {
  activeCategory.value = cat
  activeTag.value = null
  currentPage.value = 1
}

const selectTag = (tag) => {
  activeTag.value = tag
  activeCategory.value = null
  currentPage.value = 1
}

const clearFilters = () => {
  activeCategory.value = null
  activeTag.value = null
  currentPage.value = 1
}

// 初始化数据
const fetchData = async () => {
  loading.value = true
  try {
    // 捕获所有请求的异常，防止单点失败导致全部白屏
    const [postsRes, catsRes, hotRes, tagsRes] = await Promise.all([
      request.get('/posts/', { params: { limit: 100 } }).catch(e => { console.error("posts error", e); return { data: [] }; }),
      request.get('/categories/').catch(e => { console.error("categories error", e); return { data: [] }; }),
      request.get('/posts/hot', { params: { limit: 10 } }).catch(e => { console.error("hot posts error", e); return { data: [] }; }),
      request.get('/posts/tags').catch(e => { console.error("tags error", e); return { data: [] }; })
    ])
    
    allPosts.value = postsRes.data || []
    hotPosts.value = hotRes.data || []
    
    // tags API returns objects with name and count, or array of strings. Handle both.
    const tagsData = tagsRes.data || []
    tags.value = tagsData.map(t => typeof t === 'string' ? { name: t } : t)
    
    // 计算分类数量
    const cats = catsRes.data || []
    categories.value = cats.map(cat => {
      const count = allPosts.value.filter(p => p.category?.id === cat.id).length
      return { ...cat, count }
    })
    
  } catch (error) {
    console.error('获取首页数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.bg-primary {
  background-color: var(--bg-primary);
}
.bg-card {
  background-color: var(--bg-card);
}
.bg-tertiary {
  background-color: var(--bg-tertiary);
}
.border-border {
  border-color: var(--border-color);
}
.text-primary {
  color: var(--text-primary);
}
.text-secondary {
  color: var(--text-secondary);
}
.text-muted {
  color: var(--text-muted);
}
.text-accent {
  color: var(--accent-blue);
}
.bg-accent {
  background-color: var(--accent-blue);
}
.border-accent {
  border-color: var(--accent-blue);
}
.text-accent-purple {
  color: var(--accent-purple);
}
.text-danger {
  color: var(--text-danger);
}
.hover\:bg-hover:hover {
  background-color: var(--bg-hover);
}

/* 分页组件样式优化 */
:deep(.tech-pagination .el-pager li) {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 6px;
  transition: all 0.3s ease;
}
:deep(.tech-pagination .el-pager li:not(.is-disabled).is-active) {
  background-color: rgba(56, 189, 248, 0.1) !important;
  border-color: var(--accent-blue) !important;
  color: var(--accent-blue) !important;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
}
:deep(.tech-pagination .el-pager li:hover) {
  color: var(--accent-blue) !important;
  border-color: var(--accent-blue);
}
:deep(.tech-pagination button) {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 6px;
}
:deep(.tech-pagination button:hover:not(:disabled)) {
  color: var(--accent-blue);
  border-color: var(--accent-blue);
}
</style>
