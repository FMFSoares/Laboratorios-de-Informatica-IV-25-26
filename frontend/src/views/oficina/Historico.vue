<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getOrdensServico } from '../../services/ordensServico.js'
import { useAuthStore } from '../../store/auth.js'
import StatusBadge from '../../components/ui/StatusBadge.vue'

const router = useRouter()
const auth = useAuthStore()

const ordens = ref([])
const loading = ref(false)

const search = ref('')
const activePreset = ref('mes')
const customStart = ref('')
const customEnd = ref('')
const sort = ref({ key: 'data_efetiva', dir: 'desc' })

const TERMINAL_ESTADOS = ['CONCLUIDA', 'FATURADA', 'CANCELADA']
const PRIORIDADE_ORDER = { BAIXA: 0, NORMAL: 1, ALTA: 2, URGENTE: 3 }
const PRIORIDADE_COLORS = { BAIXA: '#6b7280', NORMAL: '#374151', ALTA: '#d97706', URGENTE: '#dc2626' }

const PRESETS = [
  { key: 'hoje',         label: 'Hoje' },
  { key: 'semana',       label: 'Esta semana' },
  { key: 'mes',          label: 'Este mês' },
  { key: 'personalizado',label: 'Personalizado' },
]

function toDateStr(d) {
  return d.toISOString().slice(0, 10)
}

function getDateRange() {
  const now = new Date()
  const today = toDateStr(now)
  if (activePreset.value === 'hoje') return { start: today, end: today }
  if (activePreset.value === 'semana') {
    const d = new Date(now)
    const day = d.getDay()
    d.setDate(d.getDate() - (day === 0 ? 6 : day - 1))
    return { start: toDateStr(d), end: today }
  }
  if (activePreset.value === 'mes') {
    const first = new Date(now.getFullYear(), now.getMonth(), 1)
    return { start: toDateStr(first), end: today }
  }
  return { start: customStart.value, end: customEnd.value }
}

function effectiveDate(o) {
  return (o.data_conclusao || o.data_entrada || '').slice(0, 10)
}

function sortValue(o, key) {
  if (key === 'data_efetiva') return effectiveDate(o)
  if (key === 'data_entrada') return (o.data_entrada || '').slice(0, 10)
  if (key === 'prioridade')   return PRIORIDADE_ORDER[o.prioridade] ?? 0
  return (o[key] ?? '').toString().toLowerCase()
}

const historico = computed(() => {
  const { start, end } = getDateRange()
  const q = search.value.trim().toLowerCase()

  let items = ordens.value.filter(o => TERMINAL_ESTADOS.includes(o.estado))

  if (start) items = items.filter(o => effectiveDate(o) >= start)
  if (end)   items = items.filter(o => effectiveDate(o) <= end)

  if (q) {
    items = items.filter(o =>
      (o.numero || '').toLowerCase().includes(q) ||
      (o.cliente_nome || '').toLowerCase().includes(q) ||
      (o.trotinete_numero_serie || '').toLowerCase().includes(q)
    )
  }

  const { key, dir } = sort.value
  return [...items].sort((a, b) => {
    const va = sortValue(a, key)
    const vb = sortValue(b, key)
    if (va < vb) return dir === 'asc' ? -1 : 1
    if (va > vb) return dir === 'asc' ? 1 : -1
    return 0
  })
})

const isFiltered = computed(() =>
  search.value.trim() !== '' ||
  sort.value.key !== 'data_efetiva' ||
  sort.value.dir !== 'desc'
)

function toggleSort(key) {
  if (sort.value.key === key) {
    sort.value = { key, dir: sort.value.dir === 'asc' ? 'desc' : 'asc' }
  } else {
    sort.value = { key, dir: key === 'data_efetiva' ? 'desc' : 'asc' }
  }
}

function sortIcon(key) {
  if (sort.value.key !== key) return '↕'
  return sort.value.dir === 'asc' ? '↑' : '↓'
}

function clearSearch() {
  search.value = ''
  sort.value = { key: 'data_efetiva', dir: 'desc' }
}

async function fetch() {
  loading.value = true
  try {
    const mecanicoId = auth.getCurrentUser?.id
    const { data } = await getOrdensServico({ mecanico_id: mecanicoId, page_size: 100 })
    ordens.value = data.data
  } catch {
    ordens.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetch)

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('pt-PT') : '—'
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>Histórico</h1>
        <p class="sub">Ordens de serviço concluídas e canceladas</p>
      </div>
    </div>

    <!-- Period presets -->
    <div class="preset-bar">
      <button
        v-for="p in PRESETS"
        :key="p.key"
        :class="['preset-btn', { active: activePreset === p.key }]"
        @click="activePreset = p.key"
      >
        {{ p.label }}
      </button>
    </div>

    <!-- Custom date range -->
    <div v-if="activePreset === 'personalizado'" class="custom-range">
      <input type="date" v-model="customStart" />
      <span class="range-sep">até</span>
      <input type="date" v-model="customEnd" />
    </div>

    <!-- Search + clear -->
    <div class="toolbar">
      <input
        v-model="search"
        class="search-input"
        type="search"
        placeholder="Pesquisar por número, cliente ou trotinete…"
      />
      <button v-if="isFiltered" class="btn btn--ghost btn--sm" @click="clearSearch">Limpar</button>
      <span class="result-count">{{ historico.length }} resultado{{ historico.length !== 1 ? 's' : '' }}</span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-msg">A carregar...</div>

    <!-- Empty -->
    <p v-else-if="historico.length === 0" class="empty-msg">
      Nenhuma ordem de serviço encontrada para o período selecionado.
    </p>

    <!-- Table -->
    <table v-else class="table">
      <thead>
        <tr>
          <th class="th-sort" @click="toggleSort('numero')">
            Número <span class="sort-icon">{{ sortIcon('numero') }}</span>
          </th>
          <th class="th-sort" @click="toggleSort('trotinete_numero_serie')">
            Trotinete <span class="sort-icon">{{ sortIcon('trotinete_numero_serie') }}</span>
          </th>
          <th class="th-sort" @click="toggleSort('cliente_nome')">
            Cliente <span class="sort-icon">{{ sortIcon('cliente_nome') }}</span>
          </th>
          <th class="th-sort" @click="toggleSort('estado')">
            Estado <span class="sort-icon">{{ sortIcon('estado') }}</span>
          </th>
          <th class="th-sort" @click="toggleSort('prioridade')">
            Prioridade <span class="sort-icon">{{ sortIcon('prioridade') }}</span>
          </th>
          <th class="th-sort" @click="toggleSort('data_entrada')">
            Entrada <span class="sort-icon">{{ sortIcon('data_entrada') }}</span>
          </th>
          <th class="th-sort" @click="toggleSort('data_efetiva')">
            Conclusão <span class="sort-icon">{{ sortIcon('data_efetiva') }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="o in historico"
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
          <td>{{ fmt(o.data_conclusao) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.page { padding: 2rem; }
.page-header { margin-bottom: 1.25rem; }
.page-header h1 { margin-bottom: 0.25rem; }
.sub { font-size: 0.85rem; color: #6b7280; }

.preset-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.preset-btn {
  padding: 0.45rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 999px;
  background: #fff;
  font-size: 0.84rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.preset-btn:hover { background: #f3f4f6; }
.preset-btn.active {
  background: #1abc9c;
  border-color: #1abc9c;
  color: #fff;
  font-weight: 600;
}

.custom-range {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.custom-range input { width: auto; }
.range-sep { font-size: 0.875rem; color: #6b7280; }

.toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.search-input {
  padding: 0.55rem 0.9rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #374151;
  background: #fff;
  outline: none;
  max-width: 380px;
  width: 100%;
}
.search-input:focus {
  border-color: #1abc9c;
  box-shadow: 0 0 0 3px rgba(26,188,156,0.15);
}

.result-count {
  margin-left: auto;
  font-size: 0.82rem;
  color: #9ca3af;
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

.loading-msg { color: #6b7280; font-size: 0.875rem; padding: 1rem 0; }
.empty-msg { color: #9ca3af; font-size: 0.875rem; padding: 1rem 0; }

.table { width: 100%; border-collapse: collapse; font-size: 0.875rem; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.table th { font-size: 0.72rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.04em; padding: 0.75rem 1rem; border-bottom: 1px solid #e5e7eb; text-align: left; background: #f9fafb; user-select: none; }
.table td { padding: 0.85rem 1rem; border-bottom: 1px solid #f3f4f6; color: #374151; }
.table tbody tr:last-child td { border-bottom: none; }

.th-sort { cursor: pointer; }
.th-sort:hover { background: #f0fdf4; color: #374151; }

.sort-icon { margin-left: 0.25rem; opacity: 0.6; font-size: 0.7rem; }

.row { cursor: pointer; transition: background 0.1s; }
.row:hover { background: #f0fdf4; }

.mono { font-family: 'Courier New', monospace; font-size: 0.82rem; }
</style>
