<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getOrdensServico } from '../../services/ordensServico.js'
import DataTable from '../../components/ui/DataTable.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'

const router = useRouter()

const ordens = ref([])
const loading = ref(false)

const filtroEstado = ref('')
const filtroAtraso = ref(false)
const filtroDataInicio = ref('')
const filtroDataFim = ref('')
const search = ref('')

const sortKey = ref('numero')
const sortDir = ref('asc')

const ESTADOS = [
  { value: '', label: 'Todos os estados' },
  { value: 'PENDENTE', label: 'Pendente' },
  { value: 'EM_DIAGNOSTICO', label: 'Em Diagnóstico' },
  { value: 'EM_REPARACAO', label: 'Em Reparação' },
  { value: 'AGUARDA_PECAS', label: 'Aguarda Peças' },
  { value: 'CONCLUIDA', label: 'Concluída' },
  { value: 'FATURADA', label: 'Faturada' },
  { value: 'CANCELADA', label: 'Cancelada' },
]

const PRIORIDADE_ORDER = { BAIXA: 0, NORMAL: 1, ALTA: 2, URGENTE: 3 }

const columns = [
  { key: 'numero',                label: 'Número',    sortable: true },
  { key: 'cliente_nome',          label: 'Cliente',   sortable: true },
  { key: 'trotinete_numero_serie',label: 'Trotinete', sortable: true },
  { key: 'estado',                label: 'Estado',    sortable: true },
  { key: 'mecanico_nome',         label: 'Mecânico',  sortable: true },
  { key: 'prioridade',            label: 'Prioridade',sortable: true },
  { key: 'data_entrada',          label: 'Entrada',   sortable: true },
  { key: 'em_atraso',             label: 'Atraso',    sortable: true },
]

const PRIORIDADE_LABELS = {
  BAIXA:   { label: 'Baixa',   color: '#6b7280' },
  NORMAL:  { label: 'Normal',  color: '#374151' },
  ALTA:    { label: 'Alta',    color: '#d97706' },
  URGENTE: { label: 'Urgente', color: '#dc2626' },
}

function sortValue(item, key) {
  if (key === 'prioridade') return PRIORIDADE_ORDER[item.prioridade] ?? 0
  if (key === 'em_atraso')  return item.minutos_em_atraso ?? 0
  if (key === 'data_entrada') return new Date(item.data_entrada || 0).getTime()
  return (item[key] ?? '').toString().toLowerCase()
}

const filteredOrdens = computed(() => {
  const q = search.value.trim().toLowerCase()
  const base = q
    ? ordens.value.filter(o =>
        (o.numero || '').toLowerCase().includes(q) ||
        (o.cliente_nome || '').toLowerCase().includes(q) ||
        (o.trotinete_numero_serie || '').toLowerCase().includes(q)
      )
    : ordens.value

  return [...base].sort((a, b) => {
    const va = sortValue(a, sortKey.value)
    const vb = sortValue(b, sortKey.value)
    if (va < vb) return sortDir.value === 'asc' ? -1 : 1
    if (va > vb) return sortDir.value === 'asc' ? 1 : -1
    return 0
  })
})

function handleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

async function fetch() {
  loading.value = true
  try {
    const params = { page: 1, page_size: 100 }
    if (filtroEstado.value)     params.estado     = filtroEstado.value
    if (filtroAtraso.value)     params.em_atraso  = true
    if (filtroDataInicio.value) params.data_inicio = filtroDataInicio.value
    if (filtroDataFim.value)    params.data_fim    = filtroDataFim.value
    const { data } = await getOrdensServico(params)
    ordens.value = data.data
  } catch {
    ordens.value = []
  } finally {
    loading.value = false
  }
}

function applyFilters() { fetch() }

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
  search.value = ''
  sortKey.value = 'numero'
  sortDir.value = 'asc'
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
      <input
        v-model="search"
        class="search-input"
        type="search"
        placeholder="Pesquisar por número, cliente ou trotinete…"
      />
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
      :rows="filteredOrdens"
      :loading="loading"
      :total="filteredOrdens.length"
      :page="1"
      :page-size="filteredOrdens.length || 1"
      :clickable="true"
      :sort-key="sortKey"
      :sort-dir="sortDir"
      row-key="id"
      empty-title="Nenhuma ordem de serviço"
      empty-message="Ajuste os filtros ou crie uma nova ordem de serviço."
      @sort="handleSort"
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
      <template #cell-mecanico_nome="{ value, row }">
        <span v-if="['EM_DIAGNOSTICO','EM_REPARACAO'].includes(row.estado) && value" class="mecanico-chip">{{ value }}</span>
        <span v-else-if="value" class="mecanico-dim">{{ value }}</span>
        <span v-else class="dim">—</span>
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

.search-input {
  padding: 0.55rem 0.9rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #374151;
  background: #fff;
  outline: none;
  min-width: 240px;
}
.search-input:focus {
  border-color: #1abc9c;
  box-shadow: 0 0 0 3px rgba(26,188,156,0.15);
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
.mecanico-chip {
  background: #ecfdf5; color: #065f46;
  border: 1px solid #6ee7b7;
  font-size: 0.78rem; font-weight: 600;
  padding: 0.15rem 0.55rem; border-radius: 999px;
  white-space: nowrap;
}
.mecanico-dim { font-size: 0.85rem; color: #6b7280; }
.dim { color: #d1d5db; font-size: 0.85rem; }

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
