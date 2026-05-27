<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth.js'
import { useWorkshopStore } from '../store/workshop.js'
import { useNotificationsStore } from '../store/notifications.js'

const auth = useAuthStore()
const workshop = useWorkshopStore()
const notif = useNotificationsStore()
const route = useRoute()

const isMecanico = computed(() => auth.getCurrentUser?.perfil === 'MECANICO')
const hasActiveOS = computed(() => workshop.hasActiveOS)
const notifCount = computed(() => notif.count)

const TABS = [
  { to: '/oficina',           label: 'Ordens' },
  { to: '/oficina/ativa',     label: 'Activa' },
  { to: '/oficina/historico', label: 'Histórico' },
  { to: '/stock',             label: 'Stock' },
  { to: '/notificacoes',      label: 'Notif.' },
  { to: '/conta',             label: 'Conta' },
]

function isActive(tab) {
  if (tab.to === '/oficina') return route.path === '/oficina'
  if (tab.to === '/oficina/ativa') {
    return route.path === '/oficina/ativa' ||
      (route.path.startsWith('/oficina/') &&
       route.path !== '/oficina/historico' &&
       route.path !== '/oficina')
  }
  return route.path.startsWith(tab.to)
}
</script>

<template>
  <nav v-if="isMecanico" class="mobile-nav">
    <RouterLink
      v-for="tab in TABS"
      :key="tab.to"
      :to="tab.to"
      class="tab"
      :class="{ 'tab--active': isActive(tab) }"
    >
      <!-- Ordens: list -->
      <svg v-if="tab.to === '/oficina'" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
      </svg>

      <!-- Activa: clock with active dot -->
      <div v-else-if="tab.to === '/oficina/ativa'" class="icon-wrap">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 15"/>
        </svg>
        <span v-if="hasActiveOS" class="dot" />
      </div>

      <!-- Histórico: calendar -->
      <svg v-else-if="tab.to === '/oficina/historico'" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
        <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
        <line x1="3" y1="10" x2="21" y2="10"/>
      </svg>

      <!-- Stock: box -->
      <svg v-else-if="tab.to === '/stock'" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="21 8 21 21 3 21 3 8"/>
        <rect x="1" y="3" width="22" height="5"/>
        <line x1="10" y1="12" x2="14" y2="12"/>
      </svg>

      <!-- Conta: person -->
      <svg v-else-if="tab.to === '/conta'" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
        <circle cx="12" cy="7" r="4"/>
      </svg>

      <!-- Notif: bell with badge -->
      <div v-else class="icon-wrap">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
        <span v-if="notifCount > 0" class="badge">{{ notifCount > 99 ? '99+' : notifCount }}</span>
      </div>

      <span class="label">{{ tab.label }}</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.mobile-nav {
  display: none;
}

@media (max-width: 1280px) {
  .mobile-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 64px;
    background: #1e293b;
    border-top: 1px solid rgba(255,255,255,0.08);
    z-index: 500;
    padding-bottom: env(safe-area-inset-bottom, 0px);
  }
}

.tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  text-decoration: none;
  color: #64748b;
  transition: color 0.15s;
  -webkit-tap-highlight-color: transparent;
  min-width: 0;
}
.tab:hover { text-decoration: none; }
.tab--active { color: #1abc9c; }

.icon-wrap {
  position: relative;
  display: inline-flex;
}
.icon {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
}
.dot {
  position: absolute;
  top: -1px;
  right: -3px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #1abc9c;
  border: 2px solid #1e293b;
}
.badge {
  position: absolute;
  top: -4px;
  right: -10px;
  background: #ef4444;
  color: #fff;
  font-size: 0.58rem;
  font-weight: 700;
  padding: 0.05rem 0.3rem;
  border-radius: 99px;
  line-height: 1.5;
  min-width: 16px;
  text-align: center;
}
.label {
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  line-height: 1;
}
</style>
