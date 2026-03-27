<template>
  <transition name="modal-fade">
    <div v-if="userStore.isAuthModalVisible" class="auth-modal-mask" @click.self="userStore.closeAuthModal">
      <div class="auth-card glass-card">
        <el-button class="close-btn" :icon="Close" circle plain @click="userStore.closeAuthModal" />
        <div class="auth-header">
          <div class="logo">
            <span class="logo-icon">🔥</span> BlogSystem
          </div>
          <p class="subtitle">欢迎来到我们的社区</p>
        </div>

        <el-tabs v-model="userStore.authModalTab" class="auth-tabs" @tab-change="resetForms">
          <el-tab-pane label="登录" name="login">
            <transition name="fade-slide" mode="out-in">
              <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-position="top" @keyup.enter="handleLogin">
                <el-form-item label="用户名 / 邮箱" prop="username">
                  <el-input v-model="loginForm.username" placeholder="请输入用户名或邮箱" :prefix-icon="User" size="large" />
                </el-form-item>
                <el-form-item label="密码" prop="password">
                  <el-input type="password" v-model="loginForm.password" placeholder="请输入密码" show-password :prefix-icon="Lock" size="large" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" class="submit-btn" :loading="loading" size="large" @click="handleLogin">登录</el-button>
                </el-form-item>
              </el-form>
            </transition>
          </el-tab-pane>

          <el-tab-pane label="注册" name="register">
            <transition name="fade-slide" mode="out-in">
              <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-position="top" @keyup.enter="handleRegister">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="registerForm.username" placeholder="起个响亮的名字" :prefix-icon="User" size="large" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="registerForm.email" placeholder="请输入真实邮箱" :prefix-icon="Message" size="large" />
                </el-form-item>
                <el-form-item label="密码" prop="password">
                  <el-input type="password" v-model="registerForm.password" placeholder="至少6位密码" show-password :prefix-icon="Lock" size="large" />
                </el-form-item>
                <el-form-item label="确认密码" prop="confirmPassword">
                  <el-input type="password" v-model="registerForm.confirmPassword" placeholder="请再次输入密码" show-password :prefix-icon="Lock" size="large" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" class="submit-btn" :loading="loading" size="large" @click="handleRegister">注册账号</el-button>
                </el-form-item>
              </el-form>
            </transition>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { login, register } from '@/api/user';
import { useUserStore } from '@/store/user';
import { ElMessage } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { User, Lock, Message, Close } from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const loading = ref(false);

const loginFormRef = ref<FormInstance>();
const registerFormRef = ref<FormInstance>();

const loginForm = reactive({
  username: '',
  password: ''
});

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致!'));
  } else {
    callback();
  }
};

const loginRules = reactive<FormRules>({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
});

const registerRules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
});

const resetForms = () => {
  loginFormRef.value?.resetFields();
  registerFormRef.value?.resetFields();
};

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const { data } = await login({
          username: loginForm.username,
          password: loginForm.password
        });
        localStorage.setItem('token', data.access_token);
        userStore.token = data.access_token;
        await userStore.fetchUserInfo();
        
        ElMessage.success('登录成功');
        userStore.closeAuthModal();
        
        const redirect = route.query.redirect as string;
        if (redirect) {
          router.push(redirect);
        }
      } catch (error) {
        // error handled in interceptor
      } finally {
        loading.value = false;
      }
    }
  });
};

const handleRegister = async () => {
  if (!registerFormRef.value) return;
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        await register({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password
        });
        ElMessage.success('注册成功，正在为您自动登录...');
        
        // Auto login after register
        const { data } = await login({
          username: registerForm.username,
          password: registerForm.password
        });
        localStorage.setItem('token', data.access_token);
        userStore.token = data.access_token;
        await userStore.fetchUserInfo();
        
        userStore.closeAuthModal();
      } catch (error) {
        // error handled in interceptor
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
.auth-modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.auth-card {
  position: relative;
  width: 100%;
  max-width: 440px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  border-radius: 24px;
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  border: none;
  background: transparent;
  color: var(--text-muted);
}

.close-btn:hover {
  color: var(--accent-primary);
  background: var(--bg-hover);
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  font-size: 28px;
  font-weight: 800;
  color: var(--accent-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 8px;
}

.logo-icon {
  font-size: 32px;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 15px;
}

.auth-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: var(--border-color);
}

.auth-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  padding: 0 20px;
}

.submit-btn {
  width: 100%;
  margin-top: 10px;
  font-size: 16px;
  border-radius: 12px !important;
  height: 48px;
}

/* Modal 整体过渡动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
  backdrop-filter: blur(0px);
}

.modal-fade-enter-from .auth-card,
.modal-fade-leave-to .auth-card {
  transform: scale(0.95) translateY(20px);
  opacity: 0;
}

/* Tab 切换过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
