<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getOrdensServico } from '../../services/ordensServico.js'
import { useAuthStore } from '../../store/auth.js'
import StatusBadge from '../../components/ui/StatusBadge.vue'

const router = useRouter()
const auth = useAuthStore()

const ordens = ref([])
const loading = ref(false)

const ESTADOS_AVALIACAO = ['PENDENTE', 'EM_DIAGNOSTICO']
const ESTADOS_REPARACAO = ['EM_REPARACAO', 'AGUARDA_PECAS']

const avaliacao = computed(() => ordens.value.filter(o => ESTADOS_AVALIACAO.includes(o.estado) && !o.tem_timer_ativo))
const reparacao = computed(() => ordens.value.filter(o => ESTADOS_REPARACAO.includes(o.estado) && !o.tem_timer_ativo))

const PRIORIDADE_COLORS = { BAIXA: '#6b7280', NORMAL: '#374151', ALTA: '#d97706', URGENTE: '#dc2626' }

let pollInterval

async function fetch() {
  loading.value = true
  try {
    const { data } = await getOrdensServico({
      page_size: 100,
    })
    ordens.value = data.data
  } catch {
    ordens.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetch()
  pollInterval = setInterval(fetch, 30000)
})
onUnmounted(() => clearInterval(pollInterval))

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('pt-PT') : '—'
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>Oficina</h1>
        <p class="sub">As suas ordens de serviço</p>
      </div>
    </div>

    <!-- Avaliação -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Avaliação</h2>
        <span class="section-count">{{ avaliacao.length }}</span>
      </div>

      <div v-if="loading && ordens.length === 0" class="loading-msg">A carregar...</div>

      <p v-else-if="avaliacao.length === 0" class="empty-msg">Nenhuma trotinete por avaliar.</p>

      <table v-else class="table">
        <thead>
          <tr>
            <th>Número</th>
            <th>Trotinete</th>
            <th>Cliente</th>
            <th>Estado</th>
            <th>Prioridade</th>
            <th>Entrada</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="o in avaliacao"
            :key="o.id"
            class="row"
            @click="router.push(`/oficina/${o.id}`)"
          >
            <td class="mono">{{ o.numero }}</td>
            <td class="mono">{{ o.trotinete_numero_serie || '—' }}</td>
            <td>{{ o.cliente_nome || '—' }}</td>
            <td><StatusBadge :estado="o.estado" /></td>
            <td>
              <span :style="{ color: PRIORIDADE_COLORS[o.prioridade], fontWeight: 600 }">
                {{ o.prioridade }}
              </span>
            </td>
            <td>{{ fmt(o.data_entrada) }}</td>
            <td>
              <span v-if="o.em_atraso" class="atraso-badge">⚠ +{{ o.minutos_em_atraso }}min</span>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Reparação -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Reparação</h2>
        <span class="section-count">{{ reparacao.length }}</span>
      </div>

      <div v-if="loading && ordens.length === 0" class="loading-msg">A carregar...</div>

      <p v-else-if="reparacao.length === 0" class="empty-msg">Nenhuma trotinete em reparação.</p>

      <table v-else class="table">
        <thead>
          <tr>
            <th>Número</th>
            <th>Trotinete</th>
            <th>Cliente</th>
            <th>Estado</th>
            <th>Prioridade</th>
            <th>Timer</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="o in reparacao"
            :key="o.id"
            class="row"
            @click="router.push(`/oficina/${o.id}`)"
          >
            <td class="mono">{{ o.numero }}</td>
            <td class="mono">{{ o.trotinete_numero_serie || '—' }}</td>
            <td>{{ o.cliente_nome || '—' }}</td>
            <td><StatusBadge :estado="o.estado" /></td>
            <td>
              <span :style="{ color: PRIORIDADE_COLORS[o.prioridade], fontWeight: 600 }">
                {{ o.prioridade }}
              </span>
            </td>
            <td>
              <span v-if="o.tem_timer_ativo" class="timer-on">● a correr</span>
              <span v-else class="timer-off">parado</span>
            </td>
            <td>
              <span v-if="o.em_atraso" class="atraso-badge">⚠ +{{ o.minutos_em_atraso }}min</span>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
.page { padding: 2rem; }
.page-header { margin-bottom: 2rem; }
.page-header h1 { margin-bottom: 0.25rem; }
.sub { font-size: 0.85rem; color: #6b7280; }

.section { margin-bottom: 2.5rem; }

.section-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e5e7eb;
}
.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}
.section-count {
  background: #e5e7eb;
  color: #374151;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
}

.loading-msg { color: #6b7280; font-size: 0.875rem; padding: 1rem 0; }
.empty-msg { color: #9ca3af; font-size: 0.875rem; padding: 1rem 0; }

.table { width: 100%; border-collapse: collapse; font-size: 0.875rem; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.table th { font-size: 0.72rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.04em; padding: 0.75rem 1rem; border-bottom: 1px solid #e5e7eb; text-align: left; background: #f9fafb; }
.table td { padding: 0.85rem 1rem; border-bottom: 1px solid #f3f4f6; color: #374151; }
.table tbody tr:last-child td { border-bottom: none; }

.row { cursor: pointer; transition: background 0.1s; }
.row:hover { background: #f0fdf4; }

.mono { font-family: 'Courier New', monospace; font-size: 0.82rem; }
.atraso-badge { background: #fef3c7; color: #92400e; font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.5rem; border-radius: 999px; }
.timer-on { color: #1abc9c; font-weight: 700; font-size: 0.82rem; }
.timer-off { color: #9ca3af; font-size: 0.82rem; }
</style>
