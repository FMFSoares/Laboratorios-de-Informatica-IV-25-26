<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '../../store/notifications.js'

const store = useNotificationsStore()
const router = useRouter()

let pollInterval
onUnmounted(() => clearInterval(pollInterval))

const TIPO_LABEL = {
  PEDIDO_PECA:             'Pedido de Peça',
  PEDIDO_TRANSFERENCIA:    'Pedido de Transferência',
  TRANSFERENCIA_ACEITE:    'Transferência Aceite',
  TRANSFERENCIA_RECUSADA:  'Transferência Recusada',
  TRANSFERENCIA_CONCLUIDA: 'Transferência Concluída',
  PECA_APROVADA:           'Peça Aprovada',
  PECA_RECUSADA:           'Peça Recusada',
  OS_ESTADO_ALTERADO:      'Estado de OS Alterado',
  STOCK_MINIMO:            'Stock Mínimo Atingido',
  OS_ATRASO:               'OS em Atraso',
  FATURA_EMITIDA:          'Fatura Emitida',
}

const TIPO_COLOR = {
  PEDIDO_PECA:             '#f59e0b',
  PEDIDO_TRANSFERENCIA:    '#3b82f6',
  TRANSFERENCIA_ACEITE:    '#1abc9c',
  TRANSFERENCIA_RECUSADA:  '#ef4444',
  TRANSFERENCIA_CONCLUIDA: '#10b981',
  PECA_APROVADA:           '#1abc9c',
  PECA_RECUSADA:           '#ef4444',
  OS_ESTADO_ALTERADO:      '#8b5cf6',
  STOCK_MINIMO:            '#f97316',
  OS_ATRASO:               '#ef4444',
  FATURA_EMITIDA:          '#0ea5e9',
}

function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('pt-PT', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' })
}

async function handleClick(n) {
  if (!n.lida) await store.markRead(n.id)
  if (n.referencia_tipo === 'pedido_transferencia' && n.referencia_id)
    router.push(`/transferencias/${n.referencia_id}`)
  else if (n.referencia_tipo === 'ordem_servico' && n.referencia_id)
    router.push(`/ordens-servico/${n.referencia_id}`)
  else if (n.referencia_tipo === 'peca' && n.referencia_id)
    router.push(`/pecas/${n.referencia_id}`)
  else if (n.referencia_tipo === 'fatura' && n.referencia_id)
    router.push(`/faturas/${n.referencia_id}`)
}

onMounted(() => {
  store.fetchAll({ page_size: 50 })
  pollInterval = setInterval(() => store.fetchAll({ page_size: 50 }), 15000)
})
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Notificações</h1>
      <div class="header-actions">
        <button v-if="store.count > 0" class="btn btn--ghost" @click="store.markAllRead">
          Marcar todas como lidas
        </button>
        <button v-if="store.notifications.length > 0" class="btn btn--ghost btn--danger" @click="store.clearAll">
          Limpar
        </button>
      </div>
    </div>

    <div class="card">
      <div v-if="store.notifications.length === 0" class="empty">
        Sem notificações.
      </div>

      <div
        v-for="n in store.notifications"
        :key="n.id"
        class="notif-row"
        :class="{ 'notif-row--unread': !n.lida, 'notif-row--clickable': n.referencia_id }"
        @click="handleClick(n)"
      >
        <div class="notif-dot" :style="{ background: TIPO_COLOR[n.tipo] || '#94a3b8' }" />
        <div class="notif-body">
          <div class="notif-top">
            <span class="notif-tipo" :style="{ color: TIPO_COLOR[n.tipo] || '#94a3b8' }">
              {{ TIPO_LABEL[n.tipo] || n.tipo }}
            </span>
            <span class="notif-date">{{ fmtDate(n.data_criacao) }}</span>
          </div>
          <div class="notif-title">{{ n.titulo }}</div>
          <div class="notif-msg">{{ n.mensagem }}</div>
        </div>
        <div v-if="!n.lida" class="notif-unread-badge" />
        <button class="notif-delete" title="Apagar" @click.stop="store.deleteOne(n.id)">✕</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 1.5rem 2rem; max-width: 860px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; }
.page-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0; }
.header-actions { display: flex; gap: 0.5rem; }
.btn { padding: 0.45rem 1rem; border-radius: 7px; font-size: 0.85rem; font-weight: 500; cursor: pointer; border: 1px solid #d1d5db; background: #fff; color: #374151; transition: background 0.15s; }
.btn:hover { background: #f3f4f6; }
.btn--danger { border-color: #fca5a5; color: #dc2626; }
.btn--danger:hover { background: #fff5f5; }
.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 6px rgba(0,0,0,0.07); overflow: hidden; }
.empty { padding: 2.5rem; text-align: center; color: #9ca3af; font-size: 0.9rem; }
.notif-row { display: flex; align-items: flex-start; gap: 0.75rem; padding: 1rem 1.25rem; border-bottom: 1px solid #f1f5f9; transition: background 0.1s; }
.notif-row:last-child { border-bottom: none; }
.notif-row--unread { background: #f8faff; }
.notif-row--clickable { cursor: pointer; }
.notif-row--clickable:hover { background: #f0fdf9; }
.notif-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 0.4rem; }
.notif-body { flex: 1; min-width: 0; }
.notif-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.15rem; }
.notif-tipo { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.notif-date { font-size: 0.75rem; color: #9ca3af; }
.notif-title { font-size: 0.9rem; font-weight: 600; color: #1e293b; margin-bottom: 0.2rem; }
.notif-msg { font-size: 0.85rem; color: #64748b; line-height: 1.5; }
.notif-unread-badge { width: 8px; height: 8px; border-radius: 50%; background: #1abc9c; flex-shrink: 0; margin-top: 0.4rem; }
.notif-delete { flex-shrink: 0; background: none; border: none; color: #cbd5e1; font-size: 0.8rem; line-height: 1; padding: 0.25rem 0.4rem; border-radius: 4px; cursor: pointer; transition: color 0.15s, background 0.15s; }
.notif-delete:hover { color: #ef4444; background: #fef2f2; }
</style>
