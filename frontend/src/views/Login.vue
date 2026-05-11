<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

const authStore = useAuthStore()
const router = useRouter()

async function handleLogin() {
  errorMessage.value = ''
  isLoading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push({ name: 'Dashboard' })
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Credenciais inválidas. Tente novamente.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-box">
      <div class="brand">DLMCare</div>
      <p class="brand-sub">Gestão de oficina de trotinetes</p>

      <form @submit.prevent="handleLogin" class="form">
        <div class="field">
          <label for="email">Email</label>
          <input
            id="email"
            type="email"
            v-model="email"
            required
            autocomplete="username"
            placeholder="exemplo@dlmcare.pt"
          />
        </div>

        <div class="field">
          <label for="password">Password</label>
          <input
            id="password"
            type="password"
            v-model="password"
            required
            autocomplete="current-password"
            placeholder="••••••••"
          />
        </div>

        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

        <button type="submit" class="btn-submit" :disabled="isLoading">
          {{ isLoading ? 'A entrar...' : 'Entrar' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f4f7f6;
  padding: 1rem;
}

.login-box {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  padding: 2.5rem 2rem;
  width: 100%;
  max-width: 380px;
}

.brand {
  font-size: 1.75rem;
  font-weight: 800;
  color: #1abc9c;
  letter-spacing: -0.03em;
  margin-bottom: 0.25rem;
}
.brand-sub {
  font-size: 0.825rem;
  color: #9ca3af;
  margin-bottom: 2rem;
}

.form { display: flex; flex-direction: column; gap: 1rem; }

.field { display: flex; flex-direction: column; }

.error {
  color: #dc2626;
  font-size: 0.85rem;
  text-align: center;
  margin: 0;
}

.btn-submit {
  width: 100%;
  padding: 0.75rem;
  background: #1abc9c;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  margin-top: 0.5rem;
}
.btn-submit:hover:not(:disabled) { opacity: 0.88; }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
