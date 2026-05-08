<script setup>
import AppHeader from './AppHeader.vue';
import AppSidebar from './AppSidebar.vue';
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
  overflow: hidden; /* Previne que o conteúdo principal transborde o layout */
}

.main-content {
  flex-grow: 1;
  padding: 2rem;
  overflow-y: auto; /* Permite scroll dentro da área de conteúdo principal */
}
</style>
