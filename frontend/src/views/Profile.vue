<template>
  <div class="profile-page">
    <section class="page-hero">
      <div class="page-hero__title">
        <span class="page-hero__eyebrow">我的</span>
        <h1>个人主页</h1>
        <p>管理你的个人资料，设置头像和简介。</p>
      </div>
    </section>

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

      <el-card class="profile-form glass-card" shadow="never">
        <template #header>
          <div class="profile-form__header">
            <div>
              <p class="muted">编辑资料</p>
              <h3 class="section-title">个人设置</h3>
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
          <el-form-item label="修改密码">
            <el-input v-model="form.password" type="password" size="large" show-password placeholder="不修改请留空" />
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useUserStore } from '../store/user'
import request from '../utils/request'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const saving = ref(false)
const form = ref({
  username: '',
  email: '',
  bio: '',
  password: ''
})
const userInitial = computed(() => userStore.user?.username?.charAt(0)?.toUpperCase() || 'U')

onMounted(() => {
  if (userStore.user) {
    form.value.username = userStore.user.username
    form.value.email = userStore.user.email
    form.value.bio = userStore.user.bio || ''
  }
})

const saveProfile = async () => {
  saving.value = true
  try {
    const updateData = {
      username: form.value.username,
      email: form.value.email,
      bio: form.value.bio
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

.profile-stat {
  padding: 16px 12px;
  border-radius: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
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
