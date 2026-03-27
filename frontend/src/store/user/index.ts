import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { getUserInfo } from '@/api/user';

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<any>(null);
  const token = ref<string | null>(localStorage.getItem('token'));
  
  // Auth modal state
  const isAuthModalVisible = ref(false);
  const authModalTab = ref('login'); // 'login' | 'register'

  const isAdmin = ref<boolean>(false);

  // ── Backward-compatible aliases (used by old components) ──
  const user = computed(() => userInfo.value);
  const isAuthenticated = computed(() => Boolean(token.value));

  // ── Backward-compatible methods (used by old components) ──
  const setUser = (newUser: any) => {
    userInfo.value = newUser;
    if (newUser?.role?.name === 'admin') {
      isAdmin.value = true;
    }
  };

  const clearAuth = () => {
    userInfo.value = null;
    token.value = null;
    isAdmin.value = false;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  // ── New API ──
  const fetchUserInfo = async () => {
    try {
      const { data } = await getUserInfo();
      userInfo.value = data;
      isAdmin.value = data.role?.name === 'admin';
      localStorage.setItem('user', JSON.stringify(data));
      return data;
    } catch (error) {
      clearAuth();
      throw error;
    }
  };

  const logout = () => {
    clearAuth();
  };

  const openAuthModal = (tab: 'login' | 'register' = 'login') => {
    authModalTab.value = tab;
    isAuthModalVisible.value = true;
  };

  const closeAuthModal = () => {
    isAuthModalVisible.value = false;
  };

  return {
    userInfo,
    token,
    isAdmin,
    user,
    isAuthenticated,
    isAuthModalVisible,
    authModalTab,
    setUser,
    clearAuth,
    fetchUserInfo,
    logout,
    openAuthModal,
    closeAuthModal
  };
});

