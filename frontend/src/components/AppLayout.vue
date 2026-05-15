<script setup>
import AppSidebar from './AppSidebar.vue'
import { useSessionTimeout } from '../composables/useSessionTimeout.js'

const { sessionWarning, sessionSecondsLeft, stayLoggedIn } = useSessionTimeout()
</script>

<template>
  <div class="app-layout">
    <AppSidebar />
    <main class="main-content">
      <router-view />
    </main>
  </div>

  <Teleport to="body">
    <div v-if="sessionWarning" class="timeout-overlay">
      <div class="timeout-dialog">
        <div class="timeout-icon">⏱</div>
        <h2 class="timeout-title">Sessão prestes a expirar</h2>
        <p class="timeout-body">
          A sua sessão vai terminar em <strong>{{ sessionSecondsLeft }}</strong> segundo{{ sessionSecondsLeft !== 1 ? 's' : '' }} por inatividade.
        </p>
        <div class="timeout-actions">
          <button class="btn btn--primary" @click="stayLoggedIn">Continuar sessão</button>
        </div>
      </div>
    </div>
  </Teleport>
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

.timeout-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.timeout-dialog {
  background: #fff;
  border-radius: 12px;
  padding: 2.5rem 2rem;
  width: 100%;
  max-width: 380px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
}

.timeout-icon { font-size: 2.5rem; margin-bottom: 1rem; }
.timeout-title { font-size: 1.1rem; font-weight: 700; color: #111827; margin-bottom: 0.75rem; }
.timeout-body { font-size: 0.9rem; color: #6b7280; line-height: 1.6; margin-bottom: 1.5rem; }
.timeout-body strong { color: #dc2626; font-size: 1rem; }

.timeout-actions { display: flex; justify-content: center; }

.btn {
  padding: 0.65rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}
.btn:hover { opacity: 0.85; }
.btn--primary { background: #1abc9c; color: #fff; }
</style>
