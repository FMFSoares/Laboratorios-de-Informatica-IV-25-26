<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';

const authStore = useAuthStore();
const router = useRouter();

const handleLogout = () => {
  authStore.logout();
  router.push({ name: 'Login' });
};
</script>

<template>
  <header class="app-header">
    <div class="logo">
      <h1>DLMCare</h1>
    </div>
    <div class="user-info">
      <span>Olá, {{ authStore.getCurrentUser?.nome || 'Utilizador' }}</span>
      <button @click="handleLogout" class="logout-button">Sair</button>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  height: 60px;
  background-color: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.logo h1 {
  font-size: 1.5rem;
  color: #333;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info span {
  color: #555;
}

.logout-button {
  padding: 0.5rem 1rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.logout-button:hover {
  background-color: #c82333;
}
</style>
