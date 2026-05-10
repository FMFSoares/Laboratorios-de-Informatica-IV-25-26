import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

import LoginView from '../views/Login.vue'
import AppLayout from '../components/AppLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
      },

      // ── Clientes ───────────────────────────────────────────
      {
        path: 'clientes',
        name: 'Clientes',
        component: () => import('../views/clientes/Index.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
      },
      {
        path: 'clientes/:id',
        name: 'ClienteDetalhe',
        component: () => import('../views/clientes/Detail.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
      },

      // ── Ordens de Serviço ───────────────────────────────────
      {
        path: 'ordens-servico',
        name: 'OrdensServico',
        component: () => import('../views/ordens-servico/Index.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
      },
      {
        path: 'ordens-servico/nova',
        name: 'OrdemServicoNova',
        component: () => import('../views/ordens-servico/Create.vue'),
        meta: { roles: ['ADMINISTRADOR', 'RECECIONISTA'] },
      },
      {
        path: 'ordens-servico/:id',
        name: 'OrdemServicoDetalhe',
        component: () => import('../views/ordens-servico/Detail.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
      },

      // ── Oficina (Mecânico) ──────────────────────────────────
      {
        path: 'oficina',
        name: 'Oficina',
        component: () => import('../views/oficina/Index.vue'),
        meta: { roles: ['MECANICO', 'ADMINISTRADOR'] },
      },
      {
        path: 'oficina/ativa',
        name: 'OficinaAtiva',
        component: () => import('../views/oficina/Ativa.vue'),
        meta: { roles: ['MECANICO', 'ADMINISTRADOR'] },
      },
      {
        path: 'oficina/:id',
        name: 'OficinaDetalhe',
        component: () => import('../views/oficina/Detalhe.vue'),
        meta: { roles: ['MECANICO', 'ADMINISTRADOR'] },
      },

      // ── Stock ────────────────────────────────────────────────
      {
        path: 'stock',
        name: 'Stock',
        component: () => import('../views/stock/Index.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'MECANICO'] },
      },

      // ── Faturas ─────────────────────────────────────────────
      {
        path: 'faturas',
        name: 'Faturas',
        component: () => import('../views/faturas/Index.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA'] },
      },

      // ── Utilizadores ─────────────────────────────────────────
      {
        path: 'utilizadores',
        name: 'Utilizadores',
        component: () => import('../views/utilizadores/Index.vue'),
        meta: { roles: ['ADMINISTRADOR'] },
      },

      // ── Conta ────────────────────────────────────────────────
      {
        path: 'conta',
        name: 'Conta',
        component: () => import('../views/conta/Index.vue'),
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth === false) {
    // Public route — redirect authenticated users away from login
    if (to.name === 'Login' && authStore.getIsAuthenticated) {
      return next({ name: 'Dashboard' })
    }
    return next()
  }

  // All other routes require auth
  if (!authStore.getIsAuthenticated) {
    return next({ name: 'Login' })
  }

  // RBAC: if route declares allowed roles, enforce them
  if (to.meta.roles) {
    const perfil = authStore.getCurrentUser?.perfil
    if (!to.meta.roles.includes(perfil)) {
      return next(perfil === 'MECANICO' ? '/oficina' : '/dashboard')
    }
  }

  next()
})

export default router
