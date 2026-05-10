<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../store/auth.js'

const authStore = useAuthStore()

const ALL_NAV = [
  // ── Non-mechanic ──────────────────────────────────────────
  {
    label: 'Dashboard',
    to: '/dashboard',
    roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'],
  },
  {
    label: 'Clientes',
    to: '/clientes',
    roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'],
  },
  {
    label: 'Ordens de Serviço',
    to: '/ordens-servico',
    roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'],
  },
  {
    label: 'Stock',
    to: '/stock',
    roles: ['ADMINISTRADOR', 'GERENTE_LOJA'],
  },
  {
    label: 'Faturas',
    to: '/faturas',
    roles: ['ADMINISTRADOR', 'GERENTE_LOJA'],
  },
  {
    label: 'Utilizadores',
    to: '/utilizadores',
    roles: ['ADMINISTRADOR'],
  },

  // ── Mecânico ──────────────────────────────────────────────
  {
    label: 'OS Activa',
    to: '/oficina/ativa',
    roles: ['MECANICO'],
  },
  {
    label: 'Ordens de Serviço',
    to: '/oficina',
    roles: ['MECANICO'],
  },
  {
    label: 'Inventário',
    to: '/stock',
    roles: ['MECANICO'],
  },
  {
    label: 'Conta',
    to: '/conta',
    roles: ['MECANICO'],
  },
]

const navItems = computed(() => {
  const perfil = authStore.getCurrentUser?.perfil
  if (!perfil) return []
  return ALL_NAV.filter((item) => item.roles.includes(perfil))
})
</script>

<template>
  <aside class="app-sidebar">
    <nav>
      <ul>
        <li v-for="item in navItems" :key="item.to">
          <RouterLink :to="item.to" class="nav-link">{{ item.label }}</RouterLink>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<style scoped>
.app-sidebar {
  width: 220px;
  background-color: #2c3e50;
  color: #ecf0f1;
  padding-top: 1rem;
  flex-shrink: 0;
}

nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-link {
  display: block;
  padding: 0.9rem 1.5rem;
  color: #bdc3c7;
  text-decoration: none;
  font-size: 0.9rem;
  transition: background-color 0.15s, color 0.15s;
}

.nav-link:hover {
  background-color: #34495e;
  color: #fff;
}

.router-link-active {
  background-color: #1abc9c;
  color: #fff;
}
</style>
