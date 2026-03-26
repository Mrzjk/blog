<template>
  <div class="games-page fade-in-up">
    <!-- <div class="page-hero">
      <div class="page-hero__title">
        <span class="page-hero__eyebrow">Entertainment</span>
        <h1>娱乐中心</h1>
        <p>在这里放松一下，游玩我们精选的小游戏，记录你的辉煌战绩。</p>
      </div>
      <div v-if="isAdmin" class="admin-actions">
        <el-button type="primary" @click="showAddGame = true">添加游戏</el-button>
      </div>
    </div> -->

    <div class="games-layout">
      <!-- 游戏列表 -->
      <main class="games-main">
        <h2 class="section-title">所有游戏</h2>
        <div class="games-grid" v-if="games.length > 0">
          <GameCard 
            v-for="game in games" 
            :key="game.id" 
            :game="game" 
            @play="handlePlay" 
          />
        </div>
        <el-empty v-else description="暂无游戏" />
      </main>

      <!-- 战绩侧边栏 -->
      <aside class="games-sidebar">
        <el-card class="glass-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon class="text-accent"><Trophy /></el-icon>
              <h3 class="section-title">我的战绩</h3>
            </div>
          </template>
          
          <div v-if="!userStore.isAuthenticated" class="login-prompt">
            <p class="muted">登录后查看游戏战绩</p>
            <el-button type="primary" @click="router.push('/login')">去登录</el-button>
          </div>
          <div v-else-if="histories.length > 0" class="history-list">
            <div v-for="item in histories" :key="item.id" class="history-item">
              <div class="history-game">{{ item.game?.name }}</div>
              <div class="history-score">分数: <strong>{{ item.score }}</strong></div>
              <div class="history-time muted">{{ formatDate(item.played_at) }}</div>
            </div>
          </div>
          <el-empty v-else description="暂无战绩" :image-size="60" />
        </el-card>
      </aside>
    </div>

    <!-- 游戏弹窗 (简单模拟) -->
    <el-dialog v-model="playDialog" :title="currentGame?.name" width="800px" center @close="endGame">
      <div class="game-container">
        <iframe v-if="currentGame?.url" :src="currentGame.url" frameborder="0" class="game-iframe"></iframe>
        <div v-else class="game-placeholder">
          <h3>{{ currentGame?.name }}</h3>
          <p>这是一个模拟的游戏界面</p>
          <div class="mock-actions">
            <el-button @click="mockScore += 10">得分 +10</el-button>
            <p>当前得分: {{ mockScore }}</p>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="endGame">结束游戏</el-button>
        <el-button type="primary" @click="saveHistory" :loading="saving">保存战绩</el-button>
      </template>
    </el-dialog>

    <!-- 添加游戏弹窗 (Admin) -->
    <el-dialog v-model="showAddGame" title="添加新游戏" width="500px">
      <el-form :model="newGame" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="newGame.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="newGame.description" />
        </el-form-item>
        <el-form-item label="URL">
          <el-input v-model="newGame.url" placeholder="游戏链接或留空使用模拟" />
        </el-form-item>
        <el-form-item label="封面图">
          <el-input v-model="newGame.cover_image" placeholder="封面图片链接" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="newGame.is_active" active-text="上线" inactive-text="下线" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddGame = false">取消</el-button>
        <el-button type="primary" @click="submitNewGame">确认</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessage } from 'element-plus'
import { Trophy } from '@element-plus/icons-vue'
import GameCard from '../components/GameCard.vue'
import request from '../utils/request'

const router = useRouter()
const userStore = useUserStore()

const games = ref([])
const histories = ref([])

const playDialog = ref(false)
const currentGame = ref(null)
const mockScore = ref(0)
const startTime = ref(0)
const saving = ref(false)

const showAddGame = ref(false)
const newGame = ref({
  name: '',
  description: '',
  url: '',
  cover_image: '',
  is_active: true
})

const isAdmin = computed(() => {
  return userStore.user?.role?.name === 'admin'
})

const fetchGames = async () => {
  try {
    const { data } = await request.get('/games/')
    games.value = data
  } catch (error) {
    ElMessage.error('获取游戏列表失败')
  }
}

const fetchHistories = async () => {
  if (!userStore.isAuthenticated) return
  try {
    const { data } = await request.get(`/games/history/user/${userStore.user.id}`)
    histories.value = data
  } catch (error) {
    // silently fail
  }
}

const handlePlay = (game) => {
  if (!userStore.isAuthenticated) {
    ElMessage.warning('请先登录再进行游戏')
    router.push('/login')
    return
  }
  currentGame.value = game
  mockScore.value = 0
  startTime.value = Date.now()
  playDialog.value = true
}

const endGame = () => {
  playDialog.value = false
  currentGame.value = null
}

const saveHistory = async () => {
  if (!currentGame.value) return
  saving.value = true
  const duration = Math.floor((Date.now() - startTime.value) / 1000)
  try {
    await request.post('/games/history', {
      game_id: currentGame.value.id,
      score: mockScore.value,
      duration: duration
    })
    ElMessage.success('战绩保存成功！')
    fetchHistories()
    endGame()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const submitNewGame = async () => {
  try {
    await request.post('/games/', newGame.value)
    ElMessage.success('添加成功')
    showAddGame.value = false
    fetchGames()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}-${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

onMounted(() => {
  fetchGames()
  fetchHistories()
})
</script>

<style scoped>
.games-page {
  animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.games-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
}

.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.games-sidebar {
  position: sticky;
  top: 88px;
  height: max-content;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.text-accent {
  color: var(--accent-blue);
}

.login-prompt {
  text-align: center;
  padding: 20px 0;
}

.login-prompt p {
  margin-bottom: 12px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  padding: 12px;
  border-radius: 8px;
  background: var(--bg-tertiary);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-game {
  font-weight: 600;
  font-size: 14px;
}

.history-score {
  font-size: 13px;
  color: var(--accent-blue);
}

.history-time {
  font-size: 12px;
}

.game-container {
  width: 100%;
  height: 500px;
  background: #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
}

.game-iframe {
  width: 100%;
  height: 100%;
}

.game-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 20px;
}

.mock-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

@media (max-width: 900px) {
  .games-layout {
    grid-template-columns: 1fr;
  }
  
  .games-sidebar {
    position: static;
  }
}
</style>
