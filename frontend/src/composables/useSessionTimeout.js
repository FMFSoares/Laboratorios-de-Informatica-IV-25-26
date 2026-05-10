import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth.js'

const TIMEOUT_MS = 60 * 60 * 1000 // 60 minutes (RNF08)

export function useSessionTimeout() {
  const authStore = useAuthStore()
  const router = useRouter()
  let timer = null

  const reset = () => {
    clearTimeout(timer)
    timer = setTimeout(() => {
      authStore.logout()
      router.push({ name: 'Login' })
    }, TIMEOUT_MS)
  }

  const EVENTS = ['mousemove', 'keypress', 'touchstart', 'click']

  onMounted(() => {
    EVENTS.forEach((e) => window.addEventListener(e, reset, { passive: true }))
    reset()
  })

  onUnmounted(() => {
    clearTimeout(timer)
    EVENTS.forEach((e) => window.removeEventListener(e, reset))
  })
}
