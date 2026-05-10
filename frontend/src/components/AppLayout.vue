<script setup>
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import { useSessionTimeout } from '../composables/useSessionTimeout.js'

useSessionTimeout()
</script>

<template>
  <div class="app-layout">
    <AppHeader />
    <div class="app-container">
      <AppSidebar />
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f4f7f6;
}

.app-container {
  display: flex;
  flex-grow: 1;
  overflow: hidden;
}

.main-content {
  flex-grow: 1;
  padding: 2rem;
  overflow-y: auto;
}
</style>
