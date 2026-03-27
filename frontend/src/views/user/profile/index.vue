<template>
  <div class="profile-page fade-in-up">
    <div class="profile-header glass-card">
      <div class="user-info-section">
        <el-avatar :size="80" class="profile-avatar">
          {{ userStore.userInfo?.username?.charAt(0).toUpperCase() || 'U' }}
        </el-avatar>
        <div class="user-details">
          <h2>{{ userStore.userInfo?.username }}</h2>
          <p class="user-email">{{ userStore.userInfo?.email }}</p>
          
          <div class="level-progress" v-if="userStore.userInfo">
            <div class="level-info">
              <span class="level-badge">Lv.{{ userStore.userInfo?.level || 1 }}</span>
              <span class="exp-text">{{ userStore.userInfo?.exp || 0 }} / {{ getNextLevelExp(userStore.userInfo?.level || 1) }} EXP</span>
            </div>
            <el-progress 
              :percentage="getExpPercentage(userStore.userInfo?.level || 1, userStore.userInfo?.exp || 0)" 
              :show-text="false" 
              :stroke-width="8"
              color="var(--accent-primary)"
            />
          </div>

          <div class="user-stats">
            <span><strong>{{ posts.length }}</strong> 文章</span>
            <el-divider direction="vertical" />
            <span><strong>{{ bookmarks.length }}</strong> 收藏</span>
          </div>
        </div>
      </div>
    </div>

    <div class="profile-content">
      <el-tabs v-model="activeTab" type="border-card" class="profile-tabs glass-card">
        <el-tab-pane label="个人信息" name="info">
          <div class="info-form-container">
            <el-form label-width="100px" style="max-width: 500px;" @submit.prevent="handleUpdateInfo">
              <el-form-item label="用户名">
                <el-input v-model="infoForm.username" />
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="infoForm.email" />
              </el-form-item>
              <el-form-item label="修改密码">
                <el-input type="password" v-model="infoForm.password" placeholder="不修改请留空" show-password />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleUpdateInfo" :loading="updating">保存修改</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="我的文章" name="articles">
          <el-empty v-if="posts.length === 0" description="暂无文章" />
          <div class="article-list" v-else>
            <el-card 
              v-for="post in posts" 
              :key="post.id" 
              class="profile-article-card mb-3" 
              shadow="hover"
              @click="$router.push(`/user/article/${post.id}`)"
            >
              <div class="article-info">
                <h3>
                  {{ post.title }}
                  <el-tag v-if="post.status === 'draft'" size="small" type="warning" style="margin-left: 8px;">审核中</el-tag>
                </h3>
                <p class="summary">{{ post.content?.substring(0, 100).replace(/<[^>]+>/g, '') }}...</p>
                <div class="meta">
                  <span>{{ new Date(post.created_at).toLocaleDateString() }}</span>
                  <span class="meta-item"><el-icon><View /></el-icon> {{ post.views }}</span>
                  <span class="meta-item"><el-icon><Star /></el-icon> {{ post.likes }}</span>
                </div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="我的收藏" name="bookmarks">
          <el-empty v-if="bookmarks.length === 0" description="暂无收藏" />
          <div class="article-list" v-else>
            <el-card 
              v-for="post in bookmarks" 
              :key="post.id" 
              class="profile-article-card mb-3" 
              shadow="hover"
              @click="$router.push(`/user/article/${post.id}`)"
            >
              <div class="article-info">
                <h3>
                  {{ post.title }}
                  <el-tag v-if="post.status === 'draft'" size="small" type="warning" style="margin-left: 8px;">审核中</el-tag>
                </h3>
                <p class="summary">{{ post.content?.substring(0, 100).replace(/<[^>]+>/g, '') }}...</p>
                <div class="meta">
                  <span>{{ new Date(post.created_at).toLocaleDateString() }}</span>
                  <span class="meta-item"><el-icon><View /></el-icon> {{ post.views }}</span>
                  <span class="meta-item"><el-icon><Star /></el-icon> {{ post.likes }}</span>
                </div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/store/user';
import { ElMessage } from 'element-plus';
import { View, Star } from '@element-plus/icons-vue';
import { updateUserInfo } from '@/api/user';
import { getUserPosts, getUserBookmarks } from '@/api/article';

const route = useRoute();
const userStore = useUserStore();

const activeTab = ref('info');
const posts = ref<any[]>([]);
const bookmarks = ref<any[]>([]);
const updating = ref(false);

const infoForm = ref({
  username: '',
  email: '',
  password: ''
});

watch(() => userStore.userInfo, (newVal) => {
  if (newVal) {
    infoForm.value.username = newVal.username;
    infoForm.value.email = newVal.email;
  }
}, { immediate: true });

watch(() => route.query.tab, (newTab) => {
  if (newTab && typeof newTab === 'string') {
    activeTab.value = newTab;
  }
}, { immediate: true });

const loadUserContent = async () => {
  if (!userStore.userInfo) return;
  try {
    const [postsRes, bookmarksRes] = await Promise.all([
      getUserPosts(userStore.userInfo.id),
      getUserBookmarks(userStore.userInfo.id)
    ]);
    posts.value = postsRes.data;
    bookmarks.value = bookmarksRes.data;
  } catch (error) {
    console.error(error);
  }
};

const getNextLevelExp = (level: number) => {
  let totalExp = 0;
  for (let i = 1; i <= level; i++) {
    totalExp += i * 10;
  }
  return totalExp;
};

const getExpPercentage = (level: number, exp: number) => {
  let expToCurrentLevel = 0;
  for (let i = 1; i < level; i++) {
    expToCurrentLevel += i * 10;
  }
  
  const expForNextLevel = level * 10;
  const currentLevelExp = exp - expToCurrentLevel;
  
  const percentage = (currentLevelExp / expForNextLevel) * 100;
  return Math.min(100, Math.max(0, percentage));
};

const handleUpdateInfo = async () => {
  if (!infoForm.value.username || !infoForm.value.email) {
    ElMessage.warning('用户名和邮箱不能为空');
    return;
  }
  
  updating.value = true;
  try {
    const data: any = {
      username: infoForm.value.username,
      email: infoForm.value.email
    };
    if (infoForm.value.password) {
      data.password = infoForm.value.password;
    }
    
    await updateUserInfo(data);
    ElMessage.success('个人信息更新成功');
    infoForm.value.password = ''; // clear password field
    await userStore.fetchUserInfo(); // reload info
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '更新失败');
  } finally {
    updating.value = false;
  }
};

onMounted(async () => {
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo();
  }
  loadUserContent();
});
</script>

<style scoped>
.profile-page {
  max-width: 1000px;
  margin: 0 auto;
  animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.profile-header {
  padding: 40px;
  border-radius: 12px;
  margin-bottom: 24px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
}

.user-info-section {
  display: flex;
  align-items: center;
  gap: 30px;
}

.profile-avatar {
  background-color: var(--accent-primary);
  font-size: 32px;
  border: 4px solid var(--bg-secondary);
}

.user-details h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: var(--text-primary);
}

.level-progress {
  width: 100%;
  max-width: 300px;
  margin: 8px 0 16px 0;
}

.level-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.level-badge {
  background: var(--accent-primary);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.exp-text {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: monospace;
}

.user-email {
  color: var(--text-secondary);
  margin: 0 0 16px 0;
}

.user-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  color: var(--text-secondary);
  font-size: 14px;
}

.user-stats strong {
  color: var(--text-primary);
  font-size: 16px;
}

.profile-tabs {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.info-form-container {
  padding: 20px;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 10px;
}

.profile-article-card {
  cursor: pointer;
  border-radius: 8px;
  transition: transform 0.3s;
}

.profile-article-card:hover {
  transform: translateY(-2px);
}

.article-info h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: var(--text-primary);
  transition: color 0.3s;
  display: flex;
  align-items: center;
}

.profile-article-card:hover .article-info h3 {
  color: var(--accent-primary);
}

.summary {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 16px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  display: flex;
  gap: 20px;
  color: var(--text-muted);
  font-size: 13px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

@media (max-width: 768px) {
  .user-info-section {
    flex-direction: column;
    text-align: center;
  }
}
</style>
