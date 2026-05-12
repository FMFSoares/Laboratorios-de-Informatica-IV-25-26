<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getFaturas } from '../../services/faturas.js'
import DataTable from '../../components/ui/DataTable.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'

const router = useRouter()

const faturas = ref([])
const loading = ref(false)

const search        = ref('')
const filtroEstado  = ref('')
const filtroInicio  = ref('')
const filtroFim     = ref('')
const sortKey       = ref('data_emissao')
const sortDir       = ref('desc')

const ESTADOS = [
  { value: '',        label: 'Todos os estados' },
  { value: 'EMITIDA', label: 'Emitida' },
  { value: 'ANULADA', label: 'Anulada' },
]

const columns = [
  { key: 'numero',          label: 'Número',      sortable: true },
  { key: 'cliente_nome',    label: 'Cliente',      sortable: true },
  { key: 'cliente_nif',     label: 'NIF',          sortable: true },
  { key: 'valor_final',     label: 'Valor',        sortable: true },
  { key: 'data_emissao',    label: 'Emissão',      sortable: true },
  { key: 'estado',          label: 'Estado',       sortable: true },
]

function sortValue(item, key) {
  if (key === 'data_emissao') return new Date(item.data_emissao || 0).getTime()
  if (key === 'valor_final')  return item.valor_final ?? 0
  return (item[key] ?? '').toString().toLowerCase()
}

const filteredFaturas = computed(() => {
  const q = search.value.trim().toLowerCase()

  let items = faturas.value

  if (filtroEstado.value)
    items = items.filter(f => f.estado === filtroEstado.value)

  if (filtroInicio.value)
    items = items.filter(f => (f.data_emissao || '').slice(0, 10) >= filtroInicio.value)

  if (filtroFim.value)
    items = items.filter(f => (f.data_emissao || '').slice(0, 10) <= filtroFim.value)

  if (q)
    items = items.filter(f =>
      (f.numero       || '').toLowerCase().includes(q) ||
      (f.cliente_nome || '').toLowerCase().includes(q) ||
      (f.cliente_nif  || '').toLowerCase().includes(q)
    )

  return [...items].sort((a, b) => {
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
    sortDir.value = key === 'data_emissao' ? 'desc' : 'asc'
  }
}

function resetFilters() {
  search.value       = ''
  filtroEstado.value = ''
  filtroInicio.value = ''
  filtroFim.value    = ''
  sortKey.value      = 'data_emissao'
  sortDir.value      = 'desc'
}

async function fetch() {
  loading.value = true
  try {
    const { data } = await getFaturas({ page_size: 100 })
    faturas.value = data.data
  } catch {
    faturas.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetch)

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('pt-PT') : '—'
}

function fmtEur(v) {
  return v != null ? `${Number(v).toFixed(2)} €` : '—'
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1>Faturas</h1>
    </div>

    <div class="filter-bar">
      <input
        v-model="search"
        class="search-input"
        type="search"
        placeholder="Pesquisar por número, cliente ou NIF…"
      />
      <select v-model="filtroEstado">
        <option v-for="e in ESTADOS" :key="e.value" :value="e.value">{{ e.label }}</option>
      </select>
      <input type="date" v-model="filtroInicio" title="Emissão a partir de" />
      <input type="date" v-model="filtroFim"    title="Emissão até" />
      <button class="btn btn--ghost btn--sm" @click="resetFilters">Limpar</button>
    </div>

    <DataTable
      :columns="columns"
      :rows="filteredFaturas"
      :loading="loading"
      :total="filteredFaturas.length"
      :page="1"
      :page-size="filteredFaturas.length || 1"
      :clickable="true"
      :sort-key="sortKey"
      :sort-dir="sortDir"
      row-key="id"
      empty-title="Nenhuma fatura encontrada"
      empty-message="Ajuste os filtros ou emita uma fatura a partir de uma OS concluída."
      @sort="handleSort"
      @row-click="router.push(`/faturas/${$event.id}`)"
    >
      <template #cell-numero="{ value }">
        <span class="mono">{{ value }}</span>
      </template>
      <template #cell-valor_final="{ value }">
        <span class="valor">{{ fmtEur(value) }}</span>
      </template>
      <template #cell-data_emissao="{ value }">{{ fmt(value) }}</template>
      <template #cell-estado="{ value }">
        <StatusBadge :estado="value" />
      </template>
    </DataTable>
  </div>
</template>

<style scoped>
.page { padding: 2rem; }

.page-header {
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
.filter-bar input[type="date"] { width: auto; }

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
.btn--ghost { background: transparent; border: 1px solid #d1d5db; color: #374151; }
.btn--sm { padding: 0.4rem 0.8rem; font-size: 0.825rem; }

.mono  { font-family: 'Courier New', monospace; font-size: 0.85rem; }
.valor { font-weight: 600; color: #111827; }
</style>
