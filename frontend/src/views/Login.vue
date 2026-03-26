<template>
  <div class="auth-page">
    <div class="auth-panel auth-panel--brand">
      <div class="brand-badge">博客社区</div>
      <h1>分享知识，连接世界</h1>
      <p>一个现代化的博客平台，支持文章发布、评论互动、好友私聊和实时通知。</p>
      <ul class="brand-points">
        <li>简洁优雅的阅读与写作体验</li>
        <li>实时通知与好友私信</li>
        <li>个人主页与成长体系</li>
      </ul>
    </div>
    <el-card class="auth-panel auth-panel--form" shadow="never">
      <div class="auth-header">
        <div>
          <p class="eyebrow">{{ isLogin ? '欢迎回来' : '创建账号' }}</p>
          <h2>{{ isLogin ? '登录到你的账号' : '注册并开始创作' }}</h2>
        </div>
        <el-segmented v-model="mode" :options="modeOptions" />
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleSubmit">
        <el-form-item v-if="!isLogin" label="邮箱" prop="email">
          <el-input v-model.trim="form.email" size="large" placeholder="your@email.com" />
        </el-form-item>
        <el-form-item :label="isLogin ? '用户名或邮箱' : '用户名'" prop="username">
          <el-input v-model.trim="form.username" size="large" placeholder="输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" size="large" type="password" show-password placeholder="至少 6 位密码" />
        </el-form-item>
        <el-form-item v-if="!isLogin" label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" size="large" type="password" show-password placeholder="再次输入密码" />
        </el-form-item>
        <el-button class="submit-btn" type="primary" size="large" :loading="submitting" @click="handleSubmit">
          {{ isLogin ? '立即登录' : '创建账号' }}
        </el-button>
      </el-form>
      <div class="auth-footer">
        <span>{{ isLogin ? '还没有账号？' : '已经有账号？' }}</span>
        <button class="switch-btn" @click="toggleMode">{{ isLogin ? '去注册' : '去登录' }}</button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import request from '../utils/request'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const mode = ref('login')
const isLogin = computed(() => mode.value === 'login')
const submitting = ref(false)
const modeOptions = [
  { label: '登录', value: 'login' },
  { label: '注册', value: 'register' }
]
const form = ref({ username: '', password: '', email: '', confirmPassword: '' })

const rules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] }
  ],
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 3, message: '至少 3 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirmPassword: [
    {
      validator: (_, value, callback) => {
        if (isLogin.value) {
          callback()
          return
        }
        if (!value) {
          callback(new Error('请再次输入密码'))
          return
        }
        if (value !== form.value.password) {
          callback(new Error('两次输入的密码不一致'))
          return
        }
        callback()
      },
      trigger: 'blur'
    }
  ]
}

const resetForm = () => {
  form.value = { username: '', password: '', email: '', confirmPassword: '' }
  formRef.value?.clearValidate()
}

const toggleMode = () => {
  mode.value = isLogin.value ? 'register' : 'login'
  resetForm()
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) {
    return
  }
  submitting.value = true
  try {
    if (isLogin.value) {
      const formData = new FormData()
      formData.append('username', form.value.username)
      formData.append('password', form.value.password)
      const { data } = await request.post('/auth/login', formData)
      userStore.setToken(data.access_token)
      userStore.setUser(data.user)
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      const { data } = await request.post('/auth/register', {
        username: form.value.username,
        password: form.value.password,
        email: form.value.email
      })
      userStore.setUser(data)
      const loginFormData = new FormData()
      loginFormData.append('username', form.value.username)
      loginFormData.append('password', form.value.password)
      const loginResult = await request.post('/auth/login', loginFormData)
      userStore.setToken(loginResult.data.access_token)
      userStore.setUser(loginResult.data.user)
      ElMessage.success('注册并登录成功')
      router.push('/')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 48px;
  padding: 48px;
  min-height: 100vh;
  background: var(--bg-primary);
}

.auth-panel {
  border-radius: 20px;
}

.auth-panel--brand {
  width: 440px;
  padding: 48px;
  color: var(--text-primary);
}

.auth-panel--brand h1 {
  margin: 16px 0;
  font-size: 42px;
  line-height: 1.1;
  letter-spacing: -0.03em;
  font-weight: 700;
}

.auth-panel--brand p {
  margin: 0 0 28px;
  font-size: 16px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.brand-badge {
  display: inline-flex;
  padding: 8px 16px;
  border-radius: 8px;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: var(--accent-blue);
  font-size: 13px;
  font-weight: 600;
}

.brand-points {
  margin: 0;
  padding: 0;
  list-style: none;
}

.brand-points li {
  margin-bottom: 14px;
  color: var(--text-secondary);
  font-size: 15px;
  padding-left: 20px;
  position: relative;
}

.brand-points li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: var(--accent-blue);
}

.auth-panel--form {
  width: 440px;
  padding: 32px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
}

.auth-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 28px;
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--text-muted);
  font-size: 13px;
  letter-spacing: 0.05em;
}

.auth-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 24px;
  font-weight: 600;
}

.submit-btn {
  width: 100%;
  height: 48px;
  margin-top: 8px;
}

.auth-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
  color: var(--text-muted);
}

.switch-btn {
  border: 0;
  padding: 0;
  background: transparent;
  color: var(--accent-blue);
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 980px) {
  .auth-page {
    flex-direction: column;
    padding: 24px;
    gap: 24px;
  }

  .auth-panel--brand,
  .auth-panel--form {
    width: 100%;
    max-width: 480px;
  }

  .auth-panel--brand {
    padding: 24px;
  }

  .auth-panel--brand h1 {
    font-size: 32px;
  }
}
</style>
