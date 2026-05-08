<script setup>
import { useAuthStore } from '../store/auth';

const authStore = useAuthStore();
</script>

<template>
  <div class="dashboard-container">
    <h1>Dashboard</h1>
    <p>Bem-vindo ao seu painel de controlo da DLMCare, {{ authStore.getCurrentUser?.nome || authStore.getCurrentUser?.email }}!</p>

    <div class="stats-grid">
      <!-- Placeholders para widgets do dashboard -->
      <div class="stat-card">
        <h3>Ordens de Serviço Ativas</h3>
        <p class="stat-number">12</p>
      </div>
      <div class="stat-card">
        <h3>Faturação (Mês)</h3>
        <p class="stat-number">€ 3,842.50</p>
      </div>
      <div class="stat-card">
        <h3>Peças em Alerta de Stock</h3>
        <p class="stat-number">3</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  /* O padding já é dado pelo .main-content no AppLayout */
}

.dashboard-container h1 {
  margin-bottom: 1rem;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.stat-card {
  background: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.stat-card .stat-number {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #1abc9c;
}
</style>
