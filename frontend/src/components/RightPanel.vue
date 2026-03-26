<template>
  <aside class="right-panel">
    <el-card class="hot-card glass-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon class="text-danger"><DataLine /></el-icon>
          <h3 class="section-title">热门文章 Top 5</h3>
        </div>
      </template>
      <div class="hot-list">
        <div v-for="(post, index) in hotPosts" :key="post.id" class="hot-item" @click="router.push(`/post/${post.id}`)">
          <span class="hot-rank" :class="`rank-${index + 1}`">{{ index + 1 }}</span>
          <div class="hot-info">
            <h4>{{ post.title }}</h4>
            <div class="hot-meta">
              <span>{{ post.author?.username }}</span>
              <span class="dot">·</span>
              <span><el-icon><Star /></el-icon> {{ post.likes }}</span>
              <span class="dot">·</span>
              <span><el-icon><View /></el-icon> {{ post.views }}</span>
            </div>
          </div>
        </div>
        <el-empty v-if="!hotPosts.length" description="暂无热门文章" :image-size="60" />
      </div>
    </el-card>

    <el-card class="tag-card glass-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon class="text-primary"><CollectionTag /></el-icon>
          <h3 class="section-title">热门标签</h3>
        </div>
      </template>
      <div class="tag-cloud">
        <button
          v-for="tag in tags"
          :key="tag.name"
          class="cloud-tag"
          :class="{ 'is-active': selectedTag === tag.name }"
          @click="$emit('select-tag', tag.name)"
        >
          {{ tag.name }}
          <span class="tag-count">{{ tag.count }}</span>
        </button>
      </div>
    </el-card>

    <el-card class="notice-card glass-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon class="text-warning"><Bell /></el-icon>
          <h3 class="section-title">社区公告</h3>
        </div>
      </template>
      <div class="notice-content">
        <p>欢迎来到全新的博客社区！🎉</p>
        <p>我们刚刚进行了重大升级，带来了全新的暖色系视觉体验和多项功能优化：</p>
        <ul>
          <li>✨ 现代化的三栏响应式布局</li>
          <li>📝 沉浸式的 Markdown 编辑器</li>
          <li>💬 支持无限层级的树形评论区</li>
          <li>🔔 实时的消息与通知推送</li>
        </ul>
        <p class="muted mt-2">祝您在这里创作愉快！</p>
      </div>
    </el-card>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { DataLine, CollectionTag, Bell, Star, View } from '@element-plus/icons-vue'

const router = useRouter()

defineProps({
  hotPosts: {
    type: Array,
    default: () => []
  },
  tags: {
    type: Array,
    default: () => []
  },
  selectedTag: {
    type: String,
    default: ''
  }
})

defineEmits(['select-tag'])
</script>

<style scoped>
.right-panel {
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 88px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header .el-icon {
  font-size: 20px;
}

.text-danger { color: #f56c6c; }
.text-primary { color: var(--accent-blue); }
.text-warning { color: #e6a23c; }

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

/* 热门列表样式 */
.hot-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hot-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.hot-item:hover {
  background: var(--bg-hover);
}

.hot-rank {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-muted);
  width: 24px;
  text-align: center;
  font-style: italic;
}

.hot-rank.rank-1 { color: #f56c6c; font-size: 20px; }
.hot-rank.rank-2 { color: #ff8c00; font-size: 18px; }
.hot-rank.rank-3 { color: #e6a23c; font-size: 18px; }

.hot-info {
  flex: 1;
  min-width: 0;
}

.hot-info h4 {
  margin: 0 0 6px;
  font-size: 14px;
  line-height: 1.4;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.hot-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.dot {
  margin: 0 2px;
}

/* 标签云样式 */
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.cloud-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cloud-tag:hover {
  border-color: var(--accent-blue);
  color: var(--accent-blue);
  transform: translateY(-1px);
}

.cloud-tag.is-active {
  background: var(--accent-blue);
  border-color: var(--accent-blue);
  color: #fff;
}

.tag-count {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
}

.cloud-tag.is-active .tag-count {
  background: rgba(255, 255, 255, 0.2);
}

/* 公告样式 */
.notice-content {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.notice-content p {
  margin: 0 0 8px;
}

.notice-content ul {
  margin: 0 0 8px;
  padding-left: 20px;
}

.notice-content li {
  margin-bottom: 4px;
}

.mt-2 {
  margin-top: 12px;
}
</style>