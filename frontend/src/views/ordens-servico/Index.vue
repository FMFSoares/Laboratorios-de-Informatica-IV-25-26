<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getOrdensServico } from '../../services/ordensServico.js'
import DataTable from '../../components/ui/DataTable.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'

const router = useRouter()

const ordens = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)

const filtroEstado = ref('')
const filtroAtraso = ref(false)
const filtroDataInicio = ref('')
const filtroDataFim = ref('')

const ESTADOS = [
  { value: '', label: 'Todos os estados' },
  { value: 'PENDENTE', label: 'Pendente' },
  { value: 'EM_DIAGNOSTICO', label: 'Em Diagnóstico' },
  { value: 'AGUARDA_APROVACAO', label: 'Aguarda Aprovação' },
  { value: 'EM_REPARACAO', label: 'Em Reparação' },
  { value: 'AGUARDA_PECAS', label: 'Aguarda Peças' },
  { value: 'CONCLUIDA', label: 'Concluída' },
  { value: 'FATURADA', label: 'Faturada' },
  { value: 'CANCELADA', label: 'Cancelada' },
]

const columns = [
  { key: 'numero', label: 'Número' },
  { key: 'cliente_nome', label: 'Cliente' },
  { key: 'trotinete_numero_serie', label: 'Trotinete' },
  { key: 'estado', label: 'Estado' },
  { key: 'prioridade', label: 'Prioridade' },
  { key: 'data_entrada', label: 'Entrada' },
  { key: 'em_atraso', label: 'Atraso' },
]

const PRIORIDADE_LABELS = {
  BAIXA: { label: 'Baixa', color: '#6b7280' },
  NORMAL: { label: 'Normal', color: '#374151' },
  ALTA: { label: 'Alta', color: '#d97706' },
  URGENTE: { label: 'Urgente', color: '#dc2626' },
}

async function fetch() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (filtroEstado.value) params.estado = filtroEstado.value
    if (filtroAtraso.value) params.em_atraso = true
    if (filtroDataInicio.value) params.data_inicio = filtroDataInicio.value
    if (filtroDataFim.value) params.data_fim = filtroDataFim.value
    const { data } = await getOrdensServico(params)
    ordens.value = data.data
    total.value = data.total
  } catch {
    ordens.value = []
  } finally {
    loading.value = false
  }
}

function applyFilters() { page.value = 1; fetch() }
watch(page, fetch)

let pollInterval
onMounted(() => {
  fetch()
  pollInterval = setInterval(fetch, 30000)
})
onUnmounted(() => clearInterval(pollInterval))

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('pt-PT') : '—'
}

function resetFilters() {
  filtroEstado.value = ''
  filtroAtraso.value = false
  filtroDataInicio.value = ''
  filtroDataFim.value = ''
  page.value = 1
  fetch()
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1>Ordens de Serviço</h1>
      <button class="btn btn--primary" @click="router.push('/ordens-servico/nova')">+ Nova OS</button>
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <select v-model="filtroEstado" @change="applyFilters">
        <option v-for="e in ESTADOS" :key="e.value" :value="e.value">{{ e.label }}</option>
      </select>
      <input type="date" v-model="filtroDataInicio" @change="applyFilters" title="Data de entrada — a partir de" />
      <input type="date" v-model="filtroDataFim" @change="applyFilters" title="Data de entrada — até" />
      <label class="atraso-check">
        <input type="checkbox" v-model="filtroAtraso" @change="applyFilters" />
        <span>Só em atraso</span>
      </label>
      <button class="btn btn--ghost btn--sm" @click="resetFilters">Limpar</button>
    </div>

    <DataTable
      :columns="columns"
      :rows="ordens"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="20"
      :clickable="true"
      row-key="id"
      empty-title="Nenhuma ordem de serviço"
      empty-message="Ajuste os filtros ou crie uma nova ordem de serviço."
      @update:page="page = $event"
      @row-click="router.push(`/ordens-servico/${$event.id}`)"
    >
      <template #cell-numero="{ value }">
        <span class="mono">{{ value }}</span>
      </template>
      <template #cell-cliente_nome="{ value }">{{ value || '—' }}</template>
      <template #cell-trotinete_numero_serie="{ value }">
        <span class="mono">{{ value || '—' }}</span>
      </template>
      <template #cell-estado="{ value }">
        <StatusBadge :estado="value" />
      </template>
      <template #cell-prioridade="{ value }">
        <span :style="{ color: PRIORIDADE_LABELS[value]?.color, fontWeight: 600 }">
          {{ PRIORIDADE_LABELS[value]?.label || value }}
        </span>
      </template>
      <template #cell-data_entrada="{ value }">{{ fmt(value) }}</template>
      <template #cell-em_atraso="{ row }">
        <span v-if="row.em_atraso" class="atraso-badge" :title="`${row.minutos_em_atraso} min acima da média`">
          ⚠ +{{ row.minutos_em_atraso }}min
        </span>
        <span v-else class="ok-badge">✓</span>
      </template>
    </DataTable>
  </div>
</template>

<style scoped>
.page { padding: 2rem; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}
.filter-bar select,
.filter-bar input[type="date"] {
  width: auto;
}

.atraso-check {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.875rem;
  color: #374151;
  cursor: pointer;
  white-space: nowrap;
  margin-bottom: 0;
}
.atraso-check input { width: auto; }

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.btn:hover { opacity: 0.85; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--ghost { background: transparent; border: 1px solid #d1d5db; color: #374151; }
.btn--sm { padding: 0.4rem 0.8rem; font-size: 0.825rem; }

.mono { font-family: 'Courier New', monospace; font-size: 0.85rem; }

.atraso-badge {
  background: #fef3c7;
  color: #92400e;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  white-space: nowrap;
}
.ok-badge { color: #6b7280; font-size: 0.85rem; }
</style>
