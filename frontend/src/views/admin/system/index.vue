<template>
  <div class="system-settings" v-loading="loading">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card header="系统设置" class="mb-4">
          <el-form label-width="120px" style="max-width: 600px;">
            <el-form-item label="网站名称">
              <el-input v-model="systemForm.siteName" />
            </el-form-item>
            <el-form-item label="允许注册">
              <el-switch v-model="systemForm.allowRegister" />
            </el-form-item>
            <el-form-item label="文章需要审核">
              <el-switch v-model="systemForm.requireReview" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSystemSettings" :loading="saving">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="发布全局公告">
          <el-form label-width="80px">
            <el-form-item label="公告标题">
              <el-input v-model="announcementForm.title" placeholder="请输入公告标题" />
            </el-form-item>
            <el-form-item label="公告内容">
              <el-input type="textarea" :rows="4" v-model="announcementForm.content" placeholder="请输入公告内容" />
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="publishAnnouncementHandler" :loading="publishing">发布公告</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { getSystemSettings, updateSystemSettings, publishAnnouncement } from '@/api/admin';

const loading = ref(false);
const saving = ref(false);
const publishing = ref(false);

const systemForm = reactive({
  siteName: 'Blog System',
  allowRegister: true,
  requireReview: true
});

const announcementForm = reactive({
  title: '',
  content: ''
});

onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await getSystemSettings();
    if (data) {
      Object.assign(systemForm, data);
    }
  } catch (error) {
    console.error('Failed to fetch settings', error);
  } finally {
    loading.value = false;
  }
});

const saveSystemSettings = async () => {
  saving.value = true;
  try {
    await updateSystemSettings(systemForm);
    ElMessage.success('系统设置已保存');
    // Keep local storage for parts of the app that rely on it before refactoring everything
    localStorage.setItem('systemSettings', JSON.stringify(systemForm));
  } catch (error) {
    console.error('Failed to save settings', error);
  } finally {
    saving.value = false;
  }
};

const publishAnnouncementHandler = async () => {
  if (!announcementForm.title || !announcementForm.content) {
    ElMessage.warning('请填写完整的公告信息');
    return;
  }
  
  publishing.value = true;
  try {
    await publishAnnouncement({
      title: announcementForm.title,
      content: announcementForm.content
    });
    ElMessage.success(`公告《${announcementForm.title}》已发布至所有用户`);
    announcementForm.title = '';
    announcementForm.content = '';
  } catch (error) {
    console.error('Failed to publish announcement', error);
  } finally {
    publishing.value = false;
  }
};
</script>

<style scoped>
.mb-4 {
  margin-bottom: 20px;
}
</style>
