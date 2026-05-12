import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getOrdensServico } from '../services/ordensServico.js'
import { useAuthStore } from './auth.js'

export const useWorkshopStore = defineStore('workshop', () => {
  const hasActiveOS = ref(false)

  function set(val) {
    hasActiveOS.value = val
  }

  async function refresh() {
    const auth = useAuthStore()
    const user = auth.getCurrentUser
    if (user?.perfil !== 'MECANICO') return
    try {
      const { data } = await getOrdensServico({ mecanico_id: user.id, page_size: 100 })
      hasActiveOS.value = data.data.some(o => o.tem_timer_ativo)
    } catch { /* ignore */ }
  }

  return { hasActiveOS, set, refresh }
})
