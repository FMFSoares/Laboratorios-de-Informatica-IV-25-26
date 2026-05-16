<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../store/auth.js'
import { getTransferencias, cancelarTransferencia } from '../../services/transferencias.js'
import { getPedidosPeca, responderPedidoPeca } from '../../services/pedidosPeca.js'

const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

const activeTab      = ref(route.query.tab === 'pedidos' ? 'pedidos' : 'transferencias')
const transferencias = ref([])
const pedidos        = ref([])
const loading        = ref(false)
const error          = ref('')

const ESTADO_COLOR = {
  PENDENTE:  { bg: '#fef9c3', color: '#854d0e' },
  ACEITE:    { bg: '#dbeafe', color: '#1e40af' },
  CONCLUIDA: { bg: '#dcfce7', color: '#166534' },
  RECUSADO:  { bg: '#fee2e2', color: '#991b1b' },
  CANCELADO: { bg: '#f1f5f9', color: '#64748b' },
}
const ESTADO_PP_COLOR = {
  PENDENTE: { bg: '#fef9c3', color: '#854d0e' },
  APROVADO: { bg: '#dcfce7', color: '#166534' },
  RECUSADO: { bg: '#fee2e2', color: '#991b1b' },
}

function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('pt-PT')
}

async function loadTransferencias() {
  loading.value = true
  try {
    const r = await getTransferencias({ page_size: 50 })
    transferencias.value = r.data ?? []
  } catch (e) { error.value = 'Erro ao carregar transferências.' }
  finally { loading.value = false }
}

async function loadPedidos() {
  try {
    const r = await getPedidosPeca({ page_size: 50 })
    pedidos.value = r.data ?? []
  } catch {}
}

async function cancelar(id) {
  if (!confirm('Cancelar este pedido?')) return
  await cancelarTransferencia(id)
  await loadTransferencias()
}

async function responderPedido(id, aprovar) {
  await responderPedidoPeca(id, { aprovar })
  await loadPedidos()
}

const minhaLoja = computed(() => auth.getCurrentUser?.loja_id)

onMounted(async () => {
  await Promise.all([loadTransferencias(), loadPedidos()])
})
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Transferências</h1>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button :class="['tab', { 'tab--active': activeTab === 'transferencias' }]" @click="activeTab = 'transferencias'">
        Transferências
      </button>
      <button :class="['tab', { 'tab--active': activeTab === 'pedidos' }]" @click="activeTab = 'pedidos'">
        Pedidos de Peça
      </button>
    </div>

    <!-- Transferências tab -->
    <div v-if="activeTab === 'transferencias'" class="card">
      <p v-if="error" class="msg-error">{{ error }}</p>
      <p v-else-if="loading" class="msg-loading">A carregar...</p>
      <p v-else-if="transferencias.length === 0" class="msg-empty">Sem transferências.</p>
      <table v-else class="tbl">
        <thead><tr>
          <th>Número</th><th>Estado</th><th>Peça</th><th>Qtd</th>
          <th>Origem</th><th>Destino</th><th>Data</th><th></th>
        </tr></thead>
        <tbody>
          <tr v-for="t in transferencias" :key="t.id" class="tbl-row" @click="router.push(`/transferencias/${t.id}`)">
            <td class="mono">{{ t.numero }}</td>
            <td>
              <span class="chip" :style="ESTADO_COLOR[t.estado]">{{ t.estado }}</span>
            </td>
            <td>{{ t.peca?.nome }}</td>
            <td>{{ t.quantidade }}</td>
            <td>{{ t.loja_origem?.nome }}</td>
            <td>{{ t.loja_destino?.nome }}</td>
            <td>{{ fmtDate(t.data_pedido) }}</td>
            <td @click.stop>
              <button
                v-if="t.estado === 'PENDENTE' && t.loja_destino?.id === minhaLoja"
                class="btn btn--sm btn--ghost"
                @click="cancelar(t.id)"
              >Cancelar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pedidos de Peça tab -->
    <div v-else class="card">
      <p v-if="pedidos.length === 0" class="msg-empty">Sem pedidos de peça.</p>
      <table v-else class="tbl">
        <thead><tr>
          <th>Estado</th><th>Peça</th><th>Qtd</th><th>OS</th><th>Mecânico</th><th>Data</th><th></th>
        </tr></thead>
        <tbody>
          <tr v-for="p in pedidos" :key="p.id">
            <td><span class="chip" :style="ESTADO_PP_COLOR[p.estado]">{{ p.estado }}</span></td>
            <td>{{ p.peca?.nome }}</td>
            <td>{{ p.quantidade }}</td>
            <td class="mono">{{ p.ordem_servico?.numero }}</td>
            <td>{{ p.mecanico?.nome }}</td>
            <td>{{ fmtDate(p.data_pedido) }}</td>
            <td v-if="p.estado === 'PENDENTE'">
              <div class="row-actions">
                <button class="btn btn--sm btn--primary" @click="responderPedido(p.id, true)">Aprovar</button>
                <button class="btn btn--sm btn--ghost" @click="responderPedido(p.id, false)">Recusar</button>
              </div>
            </td>
            <td v-else></td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<style scoped>
.page { padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; }
.page-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0; }

.tabs { display: flex; gap: 0; margin-bottom: 1rem; border-bottom: 2px solid #e2e8f0; }
.tab { padding: 0.55rem 1.25rem; background: none; border: none; cursor: pointer; font-size: 0.875rem; font-weight: 500; color: #64748b; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: color 0.15s, border-color 0.15s; }
.tab--active { color: #1abc9c; border-bottom-color: #1abc9c; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 6px rgba(0,0,0,0.07); overflow: hidden; }
.tbl { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.tbl th { padding: 0.65rem 1rem; text-align: left; font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
.tbl td { padding: 0.75rem 1rem; border-bottom: 1px solid #f1f5f9; color: #374151; }
.tbl-row { cursor: pointer; transition: background 0.1s; }
.tbl-row:hover { background: #f8fafc; }
.mono { font-family: monospace; font-size: 0.82rem; }
.chip { display: inline-block; padding: 0.2rem 0.55rem; border-radius: 99px; font-size: 0.72rem; font-weight: 600; }
.row-actions { display: flex; gap: 0.4rem; }
.msg-empty, .msg-loading, .msg-error { padding: 2rem; text-align: center; font-size: 0.9rem; color: #9ca3af; }
.msg-error { color: #dc2626; }

.btn { padding: 0.5rem 1.1rem; border-radius: 7px; font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; transition: opacity 0.15s; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--ghost { background: #f1f5f9; color: #374151; border: 1px solid #d1d5db; }
.btn--sm { padding: 0.3rem 0.7rem; font-size: 0.8rem; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

</style>
