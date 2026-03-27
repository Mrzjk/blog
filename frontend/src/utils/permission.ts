import type { Router } from 'vue-router';
import { useUserStore } from '@/store/user';
import { ElMessage } from 'element-plus';

export function setupPermissionGuard(router: Router) {
  router.beforeEach(async (to, from, next) => {
    const userStore = useUserStore();
    const token = localStorage.getItem('token');

    // If going to login page, redirect to home and open modal
    if (to.path === '/login') {
      if (!token) {
        userStore.openAuthModal('login');
      }
      return next('/user/home');
    }

    // Require Auth Check
    if (to.meta.requiresAuth || to.path.startsWith('/admin')) {
      if (!token) {
        ElMessage.warning('请先登录');
        userStore.openAuthModal('login');
        if (from.name === undefined) {
          return next('/user/home');
        }
        return next(false);
      }

      // Ensure user info is loaded if not already
      if (!userStore.userInfo) {
        try {
          await userStore.fetchUserInfo();
        } catch {
          // Token invalid, clear and redirect
          userStore.logout();
          ElMessage.warning('登录已过期，请重新登录');
          userStore.openAuthModal('login');
          if (from.name === undefined) {
            return next('/user/home');
          }
          return next(false);
        }
      }

      // Require Admin Check
      if (to.path.startsWith('/admin') && !userStore.isAdmin) {
        ElMessage.error('需要管理员权限');
        return next('/user/home');
      }
    }

    next();
  });
}
