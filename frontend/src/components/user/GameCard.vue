<template>
  <div class="game-card glass-card">
    <div class="game-card__cover" :style="{ backgroundImage: `url(${game.cover_image || '/default-game.jpg'})` }">
      <div v-if="!game.is_active" class="game-card__offline-overlay">已下线</div>
    </div>
    <div class="game-card__content">
      <h3 class="game-title">{{ game.name }}</h3>
      <p class="game-desc muted">{{ game.description || '暂无简介' }}</p>
      <div class="game-actions">
        <el-button type="primary" :disabled="!game.is_active" @click="playGame">
          开始游戏
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  game: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['play'])

const playGame = () => {
  if (props.game.is_active) {
    emit('play', props.game)
  }
}
</script>

<style scoped>
.game-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.game-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.game-card__cover {
  height: 160px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.game-card__offline-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
}

.game-card__content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.game-title {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 600;
}

.game-desc {
  font-size: 14px;
  margin: 0 0 16px;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.game-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
