import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import nprogress from 'nprogress';
import 'nprogress/nprogress.css';
import { setupPermissionGuard } from '@/utils/permission';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/user/home'
  },
  {
    path: '/user',
    component: () => import('@/layouts/UserLayout.vue'),
    redirect: '/user/home',
    children: [
      { path: 'home', name: 'UserHome', component: () => import('@/views/user/home/index.vue') },
      { path: 'editor', name: 'UserEditor', component: () => import('@/views/user/article/editor.vue'), meta: { requiresAuth: true } },
      { path: 'article/:id', name: 'UserArticleDetail', component: () => import('@/views/user/article/detail.vue') },
      { path: 'forum', name: 'UserForum', component: () => import('@/views/user/forum/index.vue') },
      { path: 'game', name: 'UserGame', component: () => import('@/views/user/game/index.vue') },
      { path: 'ranking', name: 'UserRanking', component: () => import('@/views/user/ranking/index.vue') },
      { 
        path: 'profile', 
        name: 'UserProfile', 
        component: () => import('@/views/user/profile/index.vue'),
        meta: { requiresAuth: true }
      },
      { 
        path: 'chat', 
        name: 'UserChat', 
        component: () => import('@/views/user/chat/index.vue'),
        meta: { requiresAuth: true }
      },
      { 
        path: 'friends', 
        name: 'UserFriends', 
        component: () => import('@/views/user/friends/index.vue'),
        meta: { requiresAuth: true }
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/admin/dashboard',
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/views/admin/dashboard/index.vue') },
      { path: 'user-manage', name: 'AdminUserManage', component: () => import('@/views/admin/user-manage/index.vue') },
      { path: 'article-review', name: 'AdminArticleReview', component: () => import('@/views/admin/article-review/index.vue') },
      { path: 'category', name: 'AdminCategory', component: () => import('@/views/admin/category/index.vue') },
      { path: 'system', name: 'AdminSystem', component: () => import('@/views/admin/system/index.vue') }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Use extracted permission guard
setupPermissionGuard(router);

router.beforeEach(() => {
  nprogress.start();
});

router.afterEach(() => {
  nprogress.done();
});

export default router;
