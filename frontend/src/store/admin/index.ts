import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAdminStore = defineStore('admin', () => {
  const dashboardStats = ref<any>(null);

  // Future admin state here
  
  return {
    dashboardStats
  };
});
