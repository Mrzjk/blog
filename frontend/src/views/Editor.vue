<template>
  <div class="editor-page">
    <div class="editor-header">
      <el-input v-model="post.title" placeholder="输入文章标题..." class="title-input" />
      <div class="editor-actions">
        <el-select v-model="post.category_id" placeholder="选择分类" style="width: 150px">
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
        </el-select>
        <el-input v-model="tagsInput" placeholder="标签(使用英文;分隔)" style="width: 200px" />
        <el-button @click="router.push('/')">取消</el-button>
        <el-button type="primary" :loading="publishing" @click="publishPost">发布文章</el-button>
      </div>
    </div>
    
    <div class="editor-cover">
      <el-upload
        class="cover-uploader"
        action="/api/v1/posts/upload"
        :headers="uploadHeaders"
        :show-file-list="false"
        :on-success="handleCoverSuccess"
        :before-upload="beforeUpload"
      >
        <img v-if="post.cover_image" :src="post.cover_image" class="cover-image" />
        <div v-else class="upload-placeholder">
          <i class="el-icon-plus"></i> 添加封面图
        </div>
      </el-upload>
    </div>

    <MdEditor
      v-model="post.content"
      @onUploadImg="onUploadImg"
      class="md-editor-container"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { ElMessage } from 'element-plus'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

const router = useRouter()
const post = ref({
  title: '',
  content: '',
  cover_image: '',
  category_id: null
})
const tagsInput = ref('')
const publishing = ref(false)
const categories = ref([])

onMounted(async () => {
  try {
    const { data } = await request.get('/categories/')
    categories.value = data
  } catch (error) {
    console.error('获取分类失败', error)
  }
})

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
})

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
  }
  return isImage
}

const handleCoverSuccess = (res) => {
  post.value.cover_image = res.url
  ElMessage.success('封面上传成功')
}

const onUploadImg = async (files, callback) => {
  const res = await Promise.all(
    files.map(file => {
      return new Promise((resolve, reject) => {
        const formData = new FormData()
        formData.append('file', file)
        request.post('/posts/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }).then(({ data }) => resolve(data.url))
          .catch(err => reject(err))
      })
    })
  )
  callback(res)
}

const publishPost = async () => {
  if (!post.value.title || !post.value.content) {
    return ElMessage.warning('请填写标题和内容')
  }
  if (!post.value.category_id) {
    return ElMessage.warning('请选择文章分类')
  }
  publishing.value = true
  try {
    const tagNames = tagsInput.value
      .split(';')
      .map(v => v.trim())
      .filter(Boolean)
      .slice(0, 8)
    
    await request.post('/posts/', {
      title: post.value.title,
      content: post.value.content,
      cover_image: post.value.cover_image,
      category_id: post.value.category_id,
      status: post.value.status,
      tags: tagNames
    })
    ElMessage.success('保存成功')
    router.push('/')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发布失败')
  } finally {
    publishing.value = false
  }
}
</script>

<style scoped>
.editor-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: calc(100vh - 100px);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.title-input :deep(.el-input__wrapper) {
  box-shadow: none !important;
  background: transparent;
}

.title-input :deep(input) {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.editor-cover {
  width: 100%;
  height: 200px;
  border-radius: 12px;
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px dashed var(--border-color);
  transition: border-color 0.3s;
}

.editor-cover:hover {
  border-color: var(--accent-blue);
}

.cover-uploader {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-placeholder {
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 8px;
}

.md-editor-container {
  flex: 1;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}
</style>