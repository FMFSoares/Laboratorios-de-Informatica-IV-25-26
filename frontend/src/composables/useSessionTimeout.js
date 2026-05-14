import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth.js'

const MIN = 60 * 1000

// Timeout per profile. Set to null to disable for that profile.
// To enable mechanics later, replace null with a duration (e.g. 8 * 60 * MIN).
const IDLE_TIMEOUTS = {
  ADMINISTRADOR: 60 * MIN,
  GERENTE_LOJA:  60 * MIN,
  RECECIONISTA:  60 * MIN,
  MECANICO:      null,
}

const EVENTS = ['mousemove', 'keydown', 'click', 'touchstart']

export function useSessionTimeout() {
  const authStore = useAuthStore()
  const router    = useRouter()
  let timer = null

  const perfil  = authStore.getCurrentUser?.perfil
  const timeout = IDLE_TIMEOUTS[perfil] ?? null

  if (timeout === null) return  // profile has no timeout — do nothing

  const reset = () => {
    clearTimeout(timer)
    timer = setTimeout(() => {
      authStore.logout()
      router.push({ name: 'Login' })
    }, timeout)
  }

  onMounted(() => {
    EVENTS.forEach(e => window.addEventListener(e, reset, { passive: true }))
    reset()
  })

  onUnmounted(() => {
    clearTimeout(timer)
    EVENTS.forEach(e => window.removeEventListener(e, reset))
  })
}
