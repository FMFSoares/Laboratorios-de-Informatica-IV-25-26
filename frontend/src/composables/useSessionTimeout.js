import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth.js'

const MIN = 60 * 1000

const IDLE_TIMEOUTS = {
  ADMINISTRADOR: 60 * MIN,
  GERENTE_LOJA:  60 * MIN,
  RECECIONISTA:  60 * MIN,
  MECANICO:      null,
}

const WARNING_BEFORE = 5 * MIN

const EVENTS = ['mousemove', 'keydown', 'click', 'touchstart']

export const sessionWarning = ref(false)
export const sessionSecondsLeft = ref(0)

export function useSessionTimeout() {
  const authStore = useAuthStore()
  const router    = useRouter()

  let warnTimer  = null
  let logoutTimer = null
  let countdownInterval = null

  const perfil  = authStore.getCurrentUser?.perfil
  const timeout = IDLE_TIMEOUTS[perfil] ?? null

  if (timeout === null) return { sessionWarning, sessionSecondsLeft, stayLoggedIn: () => {} }

  function doLogout() {
    clearAll()
    sessionWarning.value = false
    authStore.logout()
    router.push({ name: 'Login' })
  }

  function showWarning() {
    sessionWarning.value = true
    sessionSecondsLeft.value = Math.floor(WARNING_BEFORE / 1000)
    countdownInterval = setInterval(() => {
      sessionSecondsLeft.value -= 1
      if (sessionSecondsLeft.value <= 0) clearInterval(countdownInterval)
    }, 1000)
    logoutTimer = setTimeout(doLogout, WARNING_BEFORE)
  }

  function clearAll() {
    clearTimeout(warnTimer)
    clearTimeout(logoutTimer)
    clearInterval(countdownInterval)
  }

  const reset = () => {
    if (sessionWarning.value) return
    clearAll()
    warnTimer = setTimeout(showWarning, timeout - WARNING_BEFORE)
  }

  function stayLoggedIn() {
    clearAll()
    sessionWarning.value = false
    warnTimer = setTimeout(showWarning, timeout - WARNING_BEFORE)
  }

  onMounted(() => {
    EVENTS.forEach(e => window.addEventListener(e, reset, { passive: true }))
    reset()
  })

  onUnmounted(() => {
    clearAll()
    EVENTS.forEach(e => window.removeEventListener(e, reset))
  })

  return { sessionWarning, sessionSecondsLeft, stayLoggedIn }
}
