import { defineStore } from 'pinia';
import api from '../services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
    user: JSON.parse(localStorage.getItem('user_data')) || null,
    isAuthenticated: !!localStorage.getItem('access_token'),
  }),

  getters: {
    // Retorna true se o utilizador estiver autenticado
    getIsAuthenticated: (state) => state.isAuthenticated,
    // Retorna os dados do utilizador autenticado
    getCurrentUser: (state) => state.user,
    // Retorna o token de acesso
    getToken: (state) => state.token,
  },

  actions: {
    /**
     * Tenta autenticar o utilizador com email e password.
     * @param {string} email
     * @param {string} password
     * @returns {Promise<void>}
     */
    async login(email, password) {
      try {
        const response = await api.post('/auth/login', { email, password });
        const { access_token, user } = response.data;

        this.token = access_token;
        this.user = user;
        this.isAuthenticated = true;

        // Armazena o token e os dados do utilizador no localStorage para persistência
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user_data', JSON.stringify(user));

        return response.data;
      } catch (error) {
        this.logout(); // Garante que o estado de autenticação é limpo em caso de erro
        throw error; // Propaga o erro para o componente que chamou
      }
    },

    /**
     * Limpa o estado de autenticação e remove os dados do localStorage.
     */
    logout() {
      this.token = null;
      this.user = null;
      this.isAuthenticated = false;
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_data');
    },

    /**
     * Inicializa o estado de autenticação ao carregar a aplicação.
     * Verifica se existe um token no localStorage.
     */
    initializeAuth() {
      this.isAuthenticated = !!this.token;
    },
  },
});
