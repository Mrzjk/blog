<template>
  <el-config-provider>
    <AppShell>
      <router-view />
    </AppShell>
  </el-config-provider>
</template>

<script setup>
import AppShell from './components/AppShell.vue'
</script>
