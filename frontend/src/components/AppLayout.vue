<script setup>
import AppSidebar from './AppSidebar.vue'
import { useSessionTimeout } from '../composables/useSessionTimeout.js'

useSessionTimeout()
</script>

<template>
  <div class="app-layout">
    <AppSidebar />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  background: #f4f7f6;
}

.main-content {
  flex: 1;
  overflow-y: auto;
}
</style>
