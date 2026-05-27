import axios from 'axios';
import { useAuthStore } from '../store/auth';

// Define a base URL para a API.
// Usa a variável de ambiente VITE_API_BASE_URL se definida, caso contrário, usa '/api/v1'.
// A variável de ambiente é configurada no .env do frontend, conforme docs/setup_inicial.txt.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de requisição para adicionar o token JWT
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    // Adiciona o token apenas se não for a rota de login e se houver um token
    if (authStore.token && !config.url.endsWith('/auth/login')) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor de resposta para tratar erros de autenticação (401)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore();
      authStore.logout();
      // Import router lazily to avoid circular dependency
      import('../router/index.js').then(({ default: router }) => {
        router.push('/login');
      });
    }
    return Promise.reject(error);
  }
);

export default api;
