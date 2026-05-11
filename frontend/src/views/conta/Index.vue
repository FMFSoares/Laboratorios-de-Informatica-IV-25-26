<script setup>
import { useAuthStore } from '../../store/auth.js'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const user = auth.getCurrentUser

const PERFIL_LABEL = {
  ADMINISTRADOR: 'Administrador',
  GERENTE_LOJA: 'Gerente de Loja',
  RECECIONISTA: 'Rececionista',
  MECANICO: 'Mecânico',
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1>Conta</h1>
      <p class="sub">Informações do perfil e sessão actual.</p>
    </div>

    <div class="card" v-if="user">
      <div class="card-top">
        <div class="avatar">{{ user.nome?.charAt(0).toUpperCase() }}</div>
        <div class="identity">
          <span class="identity-name">{{ user.nome }}</span>
          <span class="identity-role">{{ PERFIL_LABEL[user.perfil] ?? user.perfil }}</span>
        </div>
      </div>

      <div class="divider" />

      <div class="info-grid">
        <div class="info-item" v-if="user.email">
          <span class="info-label">Email</span>
          <span class="info-value">{{ user.email }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Perfil</span>
          <span class="info-value">{{ PERFIL_LABEL[user.perfil] ?? user.perfil }}</span>
        </div>
        <div class="info-item" v-if="user.loja_nome">
          <span class="info-label">Loja</span>
          <span class="info-value">{{ user.loja_nome }}</span>
        </div>
        <div class="info-item" v-if="user.id">
          <span class="info-label">ID de utilizador</span>
          <span class="info-value mono">#{{ user.id }}</span>
        </div>
      </div>

      <div class="divider" />

      <button class="btn btn--danger" @click="logout">Terminar sessão</button>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 2rem;
  max-width: 520px;
  margin: 0 auto;
}

.page-header { margin-bottom: 2rem; }
h1 { margin-bottom: 0.25rem; }
.sub { font-size: 0.875rem; color: #6b7280; }

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card-top {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #1abc9c;
  color: #fff;
  font-size: 1.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.identity { display: flex; flex-direction: column; gap: 0.2rem; }
.identity-name { font-size: 1.15rem; font-weight: 700; color: #111827; }
.identity-role { font-size: 0.825rem; color: #6b7280; }

.divider { height: 1px; background: #f3f4f6; }

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}
.info-item { display: flex; flex-direction: column; gap: 0.2rem; }
.info-label { font-size: 0.72rem; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; }
.info-value { font-size: 0.9rem; font-weight: 500; color: #111827; }
.mono { font-family: 'Courier New', monospace; font-size: 0.85rem; }

.btn {
  padding: 0.65rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  align-self: flex-start;
}
.btn:hover { opacity: 0.85; }
.btn--danger { background: #dc2626; color: #fff; }
</style>
