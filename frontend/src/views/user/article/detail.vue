<template>
  <div class="article-detail-container">
    <div class="article-detail" v-if="article">
      <el-card class="glass-card mb-4">
        <h1 class="title">{{ article.title }}</h1>
        <div class="meta">
          <span class="author">
            <div class="mini-avatar">{{ article.author?.username?.charAt(0).toUpperCase() || 'U' }}</div>
            {{ article.author?.username }}
          </span>
          <span class="time">{{ new Date(article.created_at).toLocaleString() }}</span>
          <span class="views"><el-icon><View /></el-icon> {{ article.views }} 阅读</span>
          
          <el-button 
            size="small" 
            :type="article.is_liked ? 'primary' : 'default'" 
            :plain="!article.is_liked" 
            @click="toggleLike"
            class="like-btn"
          >
            <el-icon><Star /></el-icon>
            {{ article.is_liked ? '已赞' : '点赞' }} ({{ article.likes }})
          </el-button>
        </div>
        
        <div class="tags" v-if="article.tags?.length || article.category || article.type || article.status === 'draft'">
          <el-tag v-if="article.status === 'draft'" size="small" type="danger" effect="dark" class="mr-2 category-tag">
            <el-icon><Warning /></el-icon> 审核中
          </el-tag>
          <el-tag v-if="article.type === 'forum'" size="small" type="warning" effect="dark" class="mr-2 category-tag">
            <el-icon><ChatDotSquare /></el-icon> 帖子
          </el-tag>
          <el-tag v-else size="small" type="success" effect="dark" class="mr-2 category-tag">
            <el-icon><Document /></el-icon> 博客
          </el-tag>
          <el-tag v-if="article.category" size="small" type="info" effect="dark" class="mr-2 category-tag">
            <el-icon><Menu /></el-icon> {{ article.category.name }}
          </el-tag>
          <el-tag v-for="tag in article.tags" :key="tag.id" size="small" effect="plain" class="mr-2">
            #{{ tag.name }}
          </el-tag>
        </div>
        
        <div class="article-actions" v-if="isAuthorOrAdmin">
          <el-button type="primary" size="small" plain :icon="Edit" @click="handleEditArticle">编辑</el-button>
          <el-button type="danger" size="small" plain :icon="Delete" @click="handleDeleteArticle">删除</el-button>
        </div>
        
        <el-divider />
        <div class="content markdown-body" v-html="article.content"></div>
      </el-card>

      <!-- 评论区 -->
      <el-card class="glass-card comment-section" id="comments">
        <template #header>
          <div class="comment-header">
            <el-icon><ChatDotRound /></el-icon>
            <span>评论 ({{ comments.length }})</span>
          </div>
        </template>
        
        <!-- Main Comment Input Area (Only visible when not replying) -->
        <div class="comment-input-area" v-if="!replyTo">
          <div class="user-avatar" v-if="userStore.token">
            {{ userStore.userInfo?.username?.charAt(0).toUpperCase() || 'U' }}
          </div>
          <div class="user-avatar guest" v-else>
            <el-icon><User /></el-icon>
          </div>
          
          <div class="input-wrapper">
            <el-input 
              v-model="commentContent" 
              type="textarea" 
              :rows="3" 
              placeholder="写下你的评论..." 
              @focus="checkAuth"
            />
            <div class="input-actions">
              <el-button type="primary" :disabled="!commentContent.trim()" @click="submitComment">发表评论</el-button>
            </div>
          </div>
        </div>
        
        <el-divider v-if="comments.length > 0" />
        
        <div class="comment-list" v-loading="commentLoading">
          <el-empty v-if="comments.length === 0" description="暂无评论，快来抢沙发吧！" />
          
          <div v-for="comment in topLevelComments" :key="comment.id" class="comment-item">
            <div class="comment-avatar" @click="goToUserProfile(comment.author?.id)" style="cursor: pointer">
              {{ comment.author?.username?.charAt(0).toUpperCase() || 'U' }}
            </div>
            <div class="comment-main">
              <div class="comment-meta">
                <span class="comment-author" @click="goToUserProfile(comment.author?.id)" style="cursor: pointer">{{ comment.author?.username }}</span>
                <span class="muted author-level" style="font-size: 12px; margin-left: 4px;">Lv.{{ comment.author?.level || 1 }}</span>
                <span class="comment-time">{{ new Date(comment.created_at).toLocaleString() }}</span>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
              <div class="comment-actions">
                <span class="action-btn" @click="handleReply(comment, undefined, comment.id)">
                  <el-icon><ChatLineSquare /></el-icon> 回复
                </span>
                <span class="action-btn delete-btn" v-if="canDelete(comment)" @click="handleDeleteComment(comment.id)">
                  <el-icon><Delete /></el-icon> 删除
                </span>
              </div>

              <!-- Reply Input Area (Follows the top-level comment) -->
              <div class="reply-input-container" v-if="activeReplyCommentId === comment.id">
                <div class="input-wrapper">
                  <el-input 
                    v-model="commentContent" 
                    type="textarea" 
                    :rows="2" 
                    :placeholder="`回复 @${comment.author?.username}...`" 
                    autofocus
                  />
                  <div class="input-actions mt-2">
                    <el-button size="small" @click="cancelReply">取消</el-button>
                    <el-button type="primary" size="small" :disabled="!commentContent.trim()" @click="submitComment">发表</el-button>
                  </div>
                </div>
              </div>
              
              <!-- 子评论 (平铺展示) -->
              <div class="replies" v-if="getReplies(comment.id).length > 0">
                <div v-for="reply in getReplies(comment.id)" :key="reply.id" class="reply-item">
                  <div class="reply-avatar" @click="goToUserProfile(reply.author?.id)" style="cursor: pointer">
                    {{ reply.author?.username?.charAt(0).toUpperCase() || 'U' }}
                  </div>
                  <div class="reply-main">
                    <div class="reply-meta">
                      <span class="reply-author" @click="goToUserProfile(reply.author?.id)" style="cursor: pointer">{{ reply.author?.username }}</span>
                      <span class="muted author-level" style="font-size: 11px; margin-left: 2px;">Lv.{{ reply.author?.level || 1 }}</span>
                      <span class="reply-target" v-if="reply.reply_to_user">
                        回复 <span class="target-name">@{{ reply.reply_to_user }}</span>
                      </span>
                      <span class="reply-time">{{ new Date(reply.created_at).toLocaleString() }}</span>
                    </div>
                    <div class="reply-content">{{ reply.content }}</div>
                    <div class="comment-actions">
                      <span class="action-btn" @click="handleReply(comment, reply.author?.username, reply.id)">
                        <el-icon><ChatLineSquare /></el-icon> 回复
                      </span>
                      <span class="action-btn delete-btn" v-if="canDelete(reply)" @click="handleDeleteComment(reply.id)">
                        <el-icon><Delete /></el-icon> 删除
                      </span>
                    </div>

                    <!-- Reply Input Area for Sub-comment (Follows the sub-comment) -->
                    <div class="reply-input-container sub-reply-input" v-if="activeReplyCommentId === reply.id">
                      <div class="input-wrapper">
                        <el-input 
                          v-model="commentContent" 
                          type="textarea" 
                          :rows="2" 
                          :placeholder="`回复 @${replyTargetUser}...`" 
                          autofocus
                        />
                        <div class="input-actions mt-2">
                          <el-button size="small" @click="cancelReply">取消</el-button>
                          <el-button type="primary" size="small" :disabled="!commentContent.trim()" @click="submitComment">发表</el-button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { getArticleDetail } from '@/api/article';
import { useUserStore } from '@/store/user';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '@/utils/request';
import { View, Star, ChatDotRound, ChatLineSquare, Delete, User, Menu, Edit, Document, Warning } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const article = ref<any>(null);
const comments = ref<any[]>([]);
const commentContent = ref('');
const commentLoading = ref(false);
const replyTo = ref<any>(null); // 保存被回复的顶级评论对象
const replyTargetUser = ref<string>(''); // 保存被回复的具体用户名
const activeReplyCommentId = ref<number | null>(null); // 保存当前激活的回复框所属的具体评论ID（一级或二级）

const topLevelComments = computed(() => {
  return comments.value.filter(c => !c.parent_id);
});

const isAuthorOrAdmin = computed(() => {
  if (!userStore.token || !article.value) return false;
  return userStore.userInfo?.id === article.value.author_id || userStore.isAdmin;
});

const handleEditArticle = () => {
  router.push({ path: '/user/editor', query: { id: article.value.id } });
};

const handleDeleteArticle = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这篇文章吗？此操作不可恢复！', '高危操作', { 
      type: 'error',
      confirmButtonText: '确定删除',
      cancelButtonText: '取消'
    });
    await request.delete(`/posts/${article.value.id}`);
    ElMessage.success('文章已删除');
    router.replace('/user/home');
  } catch (e) {
    // cancelled or error
  }
};

const getReplies = (parentId: number) => {
  return comments.value.filter(c => c.parent_id === parentId);
};

const checkAuth = () => {
  if (!userStore.token) {
    userStore.openAuthModal('login');
  }
};

const fetchDetail = async () => {
  try {
    const { data } = await getArticleDetail(route.params.id as string);
    article.value = data;
    comments.value = data.comments || [];
  } catch (error) {
    // handled
  }
};

const toggleLike = async () => {
  if (!userStore.token) {
    return userStore.openAuthModal('login');
  }
  
  try {
    if (article.value.is_liked) {
      await request.delete(`/posts/${article.value.id}/like`);
      article.value.is_liked = false;
      article.value.likes = Math.max(0, article.value.likes - 1);
    } else {
      await request.post(`/posts/${article.value.id}/like`);
      article.value.is_liked = true;
      article.value.likes += 1;
    }
  } catch (error) {
    console.error(error);
  }
};

const handleReply = (comment: any, targetUser?: string, targetCommentId?: number) => {
  checkAuth();
  if (userStore.token) {
    replyTo.value = comment; // 始终挂载在顶级评论下
    replyTargetUser.value = targetUser || '';
    activeReplyCommentId.value = targetCommentId || comment.id; // 记录当前真正点击回复的哪一条评论
    commentContent.value = ''; // 清空之前的输入
  }
};

const cancelReply = () => {
  replyTo.value = null;
  replyTargetUser.value = '';
  activeReplyCommentId.value = null;
  commentContent.value = '';
};

const submitComment = async () => {
  if (!userStore.token) return userStore.openAuthModal('login');
  if (!commentContent.value.trim()) return ElMessage.warning('请输入评论内容');
  
  try {
    commentLoading.value = true;
    const payload = {
      content: commentContent.value,
      post_id: article.value.id,
      parent_id: replyTo.value ? replyTo.value.id : null,
      reply_to_user: replyTargetUser.value || null
    };
    
    await request.post('/posts/comments', payload);
    ElMessage.success('评论成功');
    commentContent.value = '';
    replyTo.value = null;
    replyTargetUser.value = '';
    activeReplyCommentId.value = null;
    await fetchDetail(); // Refresh to get new comment
  } catch (error) {
    console.error(error);
  } finally {
    commentLoading.value = false;
  }
};

const canDelete = (comment: any) => {
  if (!userStore.token) return false;
  return userStore.userInfo?.id === comment.author_id || userStore.isAdmin;
};

const handleDeleteComment = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '提示', { type: 'warning' });
    await request.delete(`/posts/comments/${id}`);
    ElMessage.success('删除成功');
    await fetchDetail();
  } catch (e) {
    // cancelled or error
  }
};

const goToUserProfile = (userId: number | undefined) => {
  if (userId) {
    router.push(`/user/${userId}`);
  }
};

onMounted(() => {
  fetchDetail();
});
</script>

<style scoped>
.article-detail-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px 0;
}

.title {
  font-size: 28px;
  text-align: center;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.meta {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 20px;
}

.author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mini-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 12px;
  font-weight: bold;
}

.views {
  display: flex;
  align-items: center;
  gap: 4px;
}

.tags {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 20px;
}

.category-tag {
  display: flex;
  align-items: center;
  gap: 4px;
}

.article-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 20px;
}

.content {
  line-height: 1.8;
  font-size: 16px;
  color: var(--text-primary);
  padding: 20px 0;
}

.mb-4 {
  margin-bottom: 20px;
}

.mr-2 {
  margin-right: 8px;
}

/* Comment Section */
.comment-section {
  border-radius: 12px;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.comment-input-area {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: white;
  display: grid;
  place-items: center;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
}

.user-avatar.guest {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.input-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.comment-item {
  display: flex;
  gap: 16px;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  display: grid;
  place-items: center;
  font-weight: bold;
  flex-shrink: 0;
}

.comment-main {
  flex: 1;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 16px;
}

.comment-item:last-child .comment-main {
  border-bottom: none;
  padding-bottom: 0;
}

.comment-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.comment-author {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 15px;
}

.comment-time {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: auto;
}

.comment-content {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 12px;
  white-space: pre-wrap;
  word-break: break-word;
}

.comment-actions {
  display: flex;
  gap: 16px;
  font-size: 13px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.3s;
}

.action-btn:hover {
  color: var(--accent-primary);
}

.action-btn.delete-btn:hover {
  color: var(--text-danger);
}

/* Replies */
.replies {
  margin-top: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reply-item {
  display: flex;
  gap: 12px;
}

.reply-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  display: grid;
  place-items: center;
  font-weight: bold;
  font-size: 12px;
  flex-shrink: 0;
}

.reply-main {
  flex: 1;
}

.reply-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.reply-author {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 13px;
}

.reply-target {
  font-size: 12px;
  color: var(--text-secondary);
}

.target-name {
  color: var(--accent-primary);
  font-weight: 500;
  cursor: pointer;
}

.reply-time {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: auto;
}

.reply-content {
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 8px;
}

.reply-input-container {
  margin-top: 12px;
  background: var(--bg-secondary);
  padding: 12px;
  border-radius: 8px;
}

.sub-reply-input {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
}

.mt-2 {
  margin-top: 8px;
}
</style>
