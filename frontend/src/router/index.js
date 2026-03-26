import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/Home.vue'), meta: { public: true } },
  { path: '/login', name: 'login', component: () => import('../views/Login.vue'), meta: { public: true } },
  { path: '/chat', name: 'chat', component: () => import('../views/Chat.vue') },
  { path: '/profile', name: 'profile', component: () => import('../views/Profile.vue') },
  { path: '/post/:id', name: 'post-detail', component: () => import('../views/PostDetail.vue'), meta: { public: true } },
  { path: '/editor', name: 'editor', component: () => import('../views/Editor.vue') },
  { path: '/notifications', name: 'notifications', component: () => import('../views/Notifications.vue') },
  { path: '/entertainment', name: 'entertainment', component: () => import('../views/Games.vue'), meta: { public: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (!to.meta.public && !userStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && userStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
