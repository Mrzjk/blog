import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';

import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import * as ElementPlusIconsVue from '@element-plus/icons-vue';

import './style.css'; // global styles

const app = createApp(App);

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

app.use(store);
app.use(router);
app.use(ElementPlus);

import { useUserStore } from './store/user';
const userStore = useUserStore();

// Wait for router ready before mounting to ensure components can resolve current route properly
router.isReady().then(() => {
  // Clear token if it's invalid
  if (userStore.token) {
    userStore.fetchUserInfo().then(() => {
      app.mount('#app');
    }).catch(() => {
      localStorage.removeItem('token');
      userStore.token = null;
      app.mount('#app');
    });
  } else {
    app.mount('#app');
  }
});





