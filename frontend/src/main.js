import { createApp } from 'vue';
import { createPinia } from 'pinia';
import './style.css';
import App from './App.vue';
import router from './router';
import { useAuthStore } from './store/auth';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// Inicializa o store de autenticação para verificar tokens existentes
const authStore = useAuthStore();
authStore.initializeAuth();

app.mount('#app');
