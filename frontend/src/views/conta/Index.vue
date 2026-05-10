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
    <h1>Conta</h1>
    <p class="sub">Informações da sua sessão actual.</p>

    <div class="card" v-if="user">
      <div class="avatar">{{ user.nome?.charAt(0).toUpperCase() }}</div>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">Nome</span>
          <span class="info-value">{{ user.nome }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Perfil</span>
          <span class="info-value">{{ PERFIL_LABEL[user.perfil] ?? user.perfil }}</span>
        </div>
        <div class="info-item" v-if="user.loja_nome">
          <span class="info-label">Loja</span>
          <span class="info-value">{{ user.loja_nome }}</span>
        </div>
      </div>
      <button class="btn btn--danger" @click="logout">Terminar sessão</button>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 2rem; max-width: 480px; }
h1 { margin-bottom: 0.25rem; }
.sub { font-size: 0.875rem; color: #6b7280; margin-bottom: 2rem; }

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  text-align: center;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #1abc9c;
  color: #fff;
  font-size: 2rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info-grid { display: flex; flex-direction: column; gap: 0.75rem; width: 100%; }
.info-item { display: flex; flex-direction: column; gap: 0.15rem; }
.info-label { font-size: 0.72rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }
.info-value { font-size: 1rem; color: #111827; font-weight: 500; }

.btn { padding: 0.65rem 1.5rem; border: none; border-radius: 6px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: opacity 0.15s; width: 100%; }
.btn:hover { opacity: 0.85; }
.btn--danger { background: #dc2626; color: #fff; }
</style>
