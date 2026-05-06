import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../store/auth';

import LoginView from '../views/Login.vue';
import DashboardView from '../views/Dashboard.vue';
import AppLayout from '../components/AppLayout.vue';

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
        component: DashboardView,
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Global Navigation Guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.getIsAuthenticated) {
    next({ name: 'Login' }); // Redireciona para login se a rota é protegida e o utilizador não está autenticado
  } else if (to.name === 'Login' && authStore.getIsAuthenticated) {
    next({ name: 'Dashboard' }); // Redireciona para dashboard se já autenticado e tentar ir para login
  } else {
    next(); // Permite o acesso
  }
});

export default router;
