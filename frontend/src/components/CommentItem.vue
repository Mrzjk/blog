<template>
  <div class="comment-item" :class="{ 'is-reply': isReply }">
    <div class="comment-card__header">
      <div class="comment-author-info">
        <div class="author-avatar-small" @click="goToUserProfile(comment.author?.id)" style="cursor: pointer">{{ comment.author?.username?.charAt(0)?.toUpperCase() || 'U' }}</div>
        <strong @click="goToUserProfile(comment.author?.id)" style="cursor: pointer">{{ comment.author?.username }}</strong>
        <span class="muted author-level" style="font-size: 12px; margin-left: 4px;">Lv.{{ comment.author?.level || 1 }}</span>
        <span v-if="replyToUser" class="reply-to">回复 <span class="highlight">@{{ replyToUser }}</span></span>
      </div>
      <div class="comment-actions">
        <span class="muted">{{ formatDate(comment.created_at) }}</span>
        <button v-if="isAuthenticated && comment.author?.id !== currentUser?.id" class="link-btn" @click="$emit('addFriend', comment.author?.id)">添加好友</button>
        <button v-if="isAuthenticated" class="link-btn" @click="$emit('reply', comment.id, comment.author?.username)">回复</button>
        <button v-if="canDelete" class="link-btn danger" @click="$emit('delete', comment.id)">删除</button>
      </div>
    </div>
    <p class="comment-content">{{ comment.content }}</p>

    <!-- 平铺渲染所有子评论（仅顶级评论渲染） -->
    <div v-if="!isReply && descendants.length > 0" class="comment-children">
      <CommentItem
        v-for="child in descendants"
        :key="child.id"
        :comment="child"
        :all-comments="[]"
        :is-reply="true"
        :reply-to-user="child._replyToUser"
        :is-authenticated="isAuthenticated"
        :current-user="currentUser"
        @reply="(id, username) => $emit('reply', id, username)"
        @delete="id => $emit('delete', id)"
        @addFriend="id => $emit('addFriend', id)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  allComments: {
    type: Array,
    required: true
  },
  isReply: {
    type: Boolean,
    default: false
  },
  replyToUser: {
    type: String,
    default: ''
  },
  isAuthenticated: {
    type: Boolean,
    default: false
  },
  currentUser: {
    type: Object,
    default: null
  }
})

defineEmits(['reply', 'delete', 'addFriend'])

const descendants = computed(() => {
  if (props.isReply) return []
  
  const getDescendants = (commentId, replyToUsername, level) => {
    let result = []
    const directChildren = props.allComments.filter(c => c.parent_id === commentId)
    for (const child of directChildren) {
      result.push({
        ...child,
        _replyToUser: level > 1 ? replyToUsername : ''
      })
      result = result.concat(getDescendants(child.id, child.author?.username, level + 1))
    }
    return result
  }
  
  return getDescendants(props.comment.id, props.comment.author?.username, 1).sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
})

const canDelete = computed(() => {
  if (!props.isAuthenticated || !props.currentUser) return false
  return props.comment.author_id === props.currentUser.id || props.currentUser.role?.name === 'admin'
})

const formatDate = value => new Date(value).toLocaleString('zh-CN')

const goToUserProfile = (userId) => {
  if (userId) {
    router.push(`/user/${userId}`)
  }
}
</script>

<style scoped>
.comment-item {
  padding: 20px;
  border-radius: 12px;
  background: var(--bg-card);
  margin-bottom: 16px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.comment-item:hover {
  border-color: rgba(56, 189, 248, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.comment-item.is-reply {
  background: rgba(30, 36, 48, 0.4);
  margin-top: 12px;
  margin-bottom: 0;
  border-left: 3px solid var(--accent-blue);
  border-radius: 0 12px 12px 0;
  border-top: 1px solid transparent;
  border-right: 1px solid transparent;
  border-bottom: 1px solid transparent;
}

.comment-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.comment-author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar-small {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 600;
  font-size: 12px;
}

.reply-to {
  font-size: 13px;
  color: var(--text-muted);
}

.highlight {
  color: var(--accent-blue);
  font-weight: 500;
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

.comment-content {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 14px;
}

.comment-children {
  margin-top: 12px;
  padding-left: 12px;
}
</style>