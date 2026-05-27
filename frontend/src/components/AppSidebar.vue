<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth.js'
import { useWorkshopStore } from '../store/workshop.js'
import { useNotificationsStore } from '../store/notifications.js'

const authStore = useAuthStore()
const router = useRouter()
const workshop = useWorkshopStore()
const notifStore = useNotificationsStore()

const PERFIL_LABEL = {
  ADMINISTRADOR: 'Administrador',
  GERENTE_LOJA: 'Gerente de Loja',
  RECECIONISTA: 'Rececionista',
  MECANICO: 'Mecânico',
}

let pollInterval
onMounted(() => {
  workshop.refresh()
  pollInterval = setInterval(workshop.refresh, 30000)
  const perfil = authStore.getCurrentUser?.perfil
  if (['ADMINISTRADOR', 'GERENTE_LOJA', 'MECANICO'].includes(perfil)) {
    notifStore.fetchCount()
    pollInterval = setInterval(() => {
      workshop.refresh()
      notifStore.fetchCount()
    }, 30000)
  }
})
onUnmounted(() => clearInterval(pollInterval))

const hasActiveOS = computed(() => workshop.hasActiveOS)
const notifCount  = computed(() => notifStore.count)

function logout() {
  authStore.logout()
  router.push('/login')
}

const ALL_NAV = [
  // ── Non-mechanic ──────────────────────────────────────────
  { label: 'Dashboard',          to: '/dashboard',       roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
  { label: 'Clientes',           to: '/clientes',        roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
  { label: 'Trotinetes',         to: '/trotinetes',      roles: ['ADMINISTRADOR', 'GERENTE_LOJA'] },
  { label: 'Ordens de Serviço',  to: '/ordens-servico',  roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
  { label: 'Catálogo Peças',    to: '/pecas',           roles: ['ADMINISTRADOR'] },
  { label: 'Inventário',         to: '/stock',           roles: ['GERENTE_LOJA'] },
  { label: 'Transferências',     to: '/transferencias',  roles: ['ADMINISTRADOR', 'GERENTE_LOJA'] },
  { label: 'Notificações',       to: '/notificacoes',    roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'MECANICO'], badge: true },
  { label: 'Faturas',            to: '/faturas',         roles: ['ADMINISTRADOR', 'GERENTE_LOJA'] },
  { label: 'Catálogo Serviços', to: '/servicos',        roles: ['ADMINISTRADOR', 'GERENTE_LOJA'] },
  { label: 'Utilizadores',       to: '/utilizadores',    roles: ['ADMINISTRADOR'] },
  { label: 'Lojas',              to: '/lojas',           roles: ['ADMINISTRADOR'] },
  { label: 'Auditoria',          to: '/auditoria',       roles: ['ADMINISTRADOR'] },

  // ── Mecânico ──────────────────────────────────────────────
  { label: 'OS Activa',          to: '/oficina/ativa',      roles: ['MECANICO'] },
  { label: 'Ordens de Serviço',  to: '/oficina',            roles: ['MECANICO'] },
  { label: 'Histórico',          to: '/oficina/historico',  roles: ['MECANICO'] },
  { label: 'Inventário',         to: '/stock',              roles: ['MECANICO'] },
]

const navItems = computed(() => {
  const perfil = authStore.getCurrentUser?.perfil
  if (!perfil) return []
  return ALL_NAV.filter(item => item.roles.includes(perfil))
})

const user = computed(() => authStore.getCurrentUser)
const userInitial = computed(() => user.value?.nome?.charAt(0).toUpperCase() ?? '?')
const userRole = computed(() => PERFIL_LABEL[user.value?.perfil] ?? user.value?.perfil ?? '')
</script>

<template>
  <aside class="sidebar">
    <!-- Brand -->
    <div class="sidebar-brand">
      <span class="brand-text">DLMCare</span>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <ul>
        <li v-for="item in navItems" :key="item.to">
          <RouterLink :to="item.to" class="nav-link">
            <span class="nav-label">{{ item.label }}</span>
            <span v-if="item.to === '/oficina/ativa' && hasActiveOS" class="active-dot" />
            <span v-if="item.badge && notifCount > 0" class="notif-badge">{{ notifCount > 99 ? '99+' : notifCount }}</span>
          </RouterLink>
        </li>
      </ul>
    </nav>

    <!-- User footer -->
    <div class="sidebar-footer">
      <RouterLink to="/conta" class="user-row">
        <div class="user-avatar">{{ userInitial }}</div>
        <div class="user-info">
          <span class="user-name">{{ user?.nome }}</span>
          <span class="user-role">{{ userRole }}</span>
        </div>
      </RouterLink>
      <button class="logout-btn" title="Terminar sessão" @click="logout">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 240px;
  background: #1e293b;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 100vh;
  overflow: hidden;
}

/* Brand */
.sidebar-brand {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}
.brand-text {
  font-size: 1.2rem;
  font-weight: 800;
  color: #1abc9c;
  letter-spacing: -0.02em;
}

/* Nav */
.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 0;
}
.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 1.5rem;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0;
  transition: background 0.15s, color 0.15s;
  position: relative;
}
.nav-link:hover {
  background: rgba(255,255,255,0.05);
  color: #e2e8f0;
  text-decoration: none;
}
.router-link-active {
  background: rgba(26, 188, 156, 0.12);
  color: #1abc9c;
  font-weight: 600;
}
.router-link-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #1abc9c;
  border-radius: 0 2px 2px 0;
}

.active-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #1abc9c;
  flex-shrink: 0;
}
.router-link-active .active-dot {
  background: #1abc9c;
}
.notif-badge {
  background: #ef4444;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.1rem 0.4rem;
  border-radius: 99px;
  flex-shrink: 0;
  line-height: 1.4;
}

/* User footer */
.sidebar-footer {
  border-top: 1px solid rgba(255,255,255,0.06);
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.user-row {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  min-width: 0;
  padding: 0.4rem 0.5rem;
  border-radius: 8px;
  transition: background 0.15s;
}
.user-row:hover {
  background: rgba(255,255,255,0.05);
  text-decoration: none;
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #1abc9c;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.user-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.user-role {
  font-size: 0.72rem;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.4rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s, color 0.15s;
}
.logout-btn:hover {
  background: rgba(220, 38, 38, 0.1);
  color: #f87171;
}
</style>
