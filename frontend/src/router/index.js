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
    redirect: () => {
      const auth = useAuthStore()
      const perfil = auth.getCurrentUser?.perfil
      if (perfil === 'MECANICO') return '/oficina/ativa'
      if (perfil === 'RECECIONISTA') return '/ordens-servico'
      return '/dashboard'
    },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA'] },
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
        meta: { roles: ['ADMINISTRADOR', 'RECECIONISTA', 'GERENTE_LOJA'] },
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
        path: 'oficina/historico',
        name: 'OficinaHistorico',
        component: () => import('../views/oficina/Historico.vue'),
        meta: { roles: ['MECANICO', 'ADMINISTRADOR'] },
      },
      {
        path: 'oficina/:id',
        name: 'OficinaDetalhe',
        component: () => import('../views/oficina/Detail.vue'),
        meta: { roles: ['MECANICO', 'ADMINISTRADOR'] },
      },

      // ── Stock ────────────────────────────────────────────────
      {
        path: 'stock',
        name: 'Stock',
        component: () => import('../views/stock/Index.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'MECANICO'] },
      },
      {
        path: 'pecas/:id',
        name: 'PecaDetalhe',
        component: () => import('../views/pecas/Detail.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'MECANICO'] },
      },

      // ── Faturas ─────────────────────────────────────────────
      {
        path: 'faturas',
        name: 'Faturas',
        component: () => import('../views/faturas/Index.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
      },
      {
        path: 'faturas/:id',
        name: 'FaturaDetalhe',
        component: () => import('../views/faturas/Detail.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
      },

      // ── Utilizadores ─────────────────────────────────────────
      {
        path: 'utilizadores',
        name: 'Utilizadores',
        component: () => import('../views/utilizadores/Index.vue'),
        meta: { roles: ['ADMINISTRADOR'] },
      },
      {
        path: 'utilizadores/:id',
        name: 'UtilizadorDetalhe',
        component: () => import('../views/utilizadores/Detail.vue'),
        meta: { roles: ['ADMINISTRADOR'] },
      },

      // ── Lojas ────────────────────────────────────────────────
      {
        path: 'lojas',
        name: 'Lojas',
        component: () => import('../views/lojas/Index.vue'),
        meta: { roles: ['ADMINISTRADOR'] },
      },
      {
        path: 'lojas/:id',
        name: 'LojaDetalhe',
        component: () => import('../views/lojas/Detail.vue'),
        meta: { roles: ['ADMINISTRADOR'] },
      },

      // ── Catálogo de Peças ─────────────────────────────────────
      {
        path: 'pecas',
        name: 'CatalogoPecas',
        component: () => import('../views/pecas/Index.vue'),
        meta: { roles: ['ADMINISTRADOR'] },
      },

      // ── Trotinetes ───────────────────────────────────────────
      {
        path: 'trotinetes',
        name: 'Trotinetes',
        component: () => import('../views/trotinetes/Index.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
      },
      {
        path: 'trotinetes/:id',
        name: 'TrotineteDetalhe',
        component: () => import('../views/trotinetes/Detail.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
      },

      // ── Catálogo de Serviços ─────────────────────────────────
      {
        path: 'servicos',
        name: 'Servicos',
        component: () => import('../views/servicos/Index.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
      },
      {
        path: 'servicos/:id',
        name: 'ServicoDetalhe',
        component: () => import('../views/servicos/Detail.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'] },
      },

      // ── Auditoria ────────────────────────────────────────────
      {
        path: 'auditoria',
        name: 'Auditoria',
        component: () => import('../views/auditoria/Index.vue'),
        meta: { roles: ['ADMINISTRADOR'] },
      },

      // ── Salários ─────────────────────────────────────────────
      {
        path: 'salarios',
        name: 'Salarios',
        component: () => import('../views/salarios/Index.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA'] },
      },

      // ── Transferências ───────────────────────────────────────
      {
        path: 'transferencias',
        name: 'Transferencias',
        component: () => import('../views/transferencias/Index.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA'] },
      },
      {
        path: 'transferencias/:id',
        name: 'TransferenciaDetalhe',
        component: () => import('../views/transferencias/Detalhe.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA'] },
      },

      // ── Notificações ─────────────────────────────────────────
      {
        path: 'notificacoes',
        name: 'Notificacoes',
        component: () => import('../views/notificacoes/Index.vue'),
        meta: { roles: ['ADMINISTRADOR', 'GERENTE_LOJA', 'MECANICO'] },
      },

      // ── Conta ────────────────────────────────────────────────
      {
        path: 'conta',
        name: 'Conta',
        component: () => import('../views/conta/Index.vue'),
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: () => {
    const auth = useAuthStore()
    const perfil = auth.getCurrentUser?.perfil
    if (perfil === 'MECANICO') return '/oficina/ativa'
    if (perfil === 'RECECIONISTA') return '/ordens-servico'
    return '/dashboard'
  }},
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
      const perfil = authStore.getCurrentUser?.perfil
      if (perfil === 'MECANICO') return next('/oficina/ativa')
      if (perfil === 'RECECIONISTA') return next('/ordens-servico')
      return next('/dashboard')
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
      if (perfil === 'MECANICO') return next('/oficina/ativa')
      if (perfil === 'RECECIONISTA') return next('/ordens-servico')
      return next('/dashboard')
    }
  }

  next()
})

export default router
