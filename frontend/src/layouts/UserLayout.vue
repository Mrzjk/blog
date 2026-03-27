<template>
  <div class="user-layout">
    <Navbar />
    <main class="main-content">
      <router-view />
    </main>
    <footer class="footer">
      <p>&copy; 2026 BlogSystem. All rights reserved. Crafted with ❤️</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import Navbar from '@/components/user/Navbar.vue';
</script>

<style scoped>
.user-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--bg-secondary); /* A slightly darker warm background for the main layout to let cards pop */
}

.main-content {
  flex: 1;
  padding: 24px 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.footer {
  text-align: center;
  padding: 30px 20px;
  color: var(--text-muted);
  font-size: 14px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-card);
  margin-top: 40px;
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px 12px;
  }
}
</style>
