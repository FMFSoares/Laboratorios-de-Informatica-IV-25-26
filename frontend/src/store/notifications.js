import { defineStore } from 'pinia'
import { ref } from 'vue'
import { countNaoLidas, getNotificacoes, marcarLida, marcarTodasLidas, apagarUma, apagarTodas } from '../services/notificacoes.js'

export const useNotificationsStore = defineStore('notifications', () => {
  const count = ref(0)
  const notifications = ref([])

  async function fetchCount() {
    try {
      const data = await countNaoLidas()
      count.value = data.nao_lidas ?? 0
    } catch {}
  }

  async function fetchAll(params = {}) {
    try {
      const data = await getNotificacoes(params)
      notifications.value = data.data ?? []
      count.value = notifications.value.filter(n => !n.lida).length
    } catch {}
  }

  async function markRead(id) {
    await marcarLida(id)
    const n = notifications.value.find(n => n.id === id)
    if (n) n.lida = true
    count.value = notifications.value.filter(n => !n.lida).length
  }

  async function markAllRead() {
    await marcarTodasLidas()
    notifications.value.forEach(n => (n.lida = true))
    count.value = 0
  }

  async function deleteOne(id) {
    try { await apagarUma(id) } catch {}
    notifications.value = notifications.value.filter(n => n.id !== id)
    count.value = notifications.value.filter(n => !n.lida).length
  }

  async function clearAll() {
    try { await apagarTodas() } catch {}
    notifications.value = []
    count.value = 0
  }

  return { count, notifications, fetchCount, fetchAll, markRead, markAllRead, deleteOne, clearAll }
})
