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
const search = ref('')

const ESTADOS_AVALIACAO = ['PENDENTE', 'EM_DIAGNOSTICO']
const ESTADOS_REPARACAO = ['EM_REPARACAO', 'AGUARDA_PECAS']

const PRIORIDADE_ORDER = { BAIXA: 0, NORMAL: 1, ALTA: 2, URGENTE: 3 }
const PRIORIDADE_COLORS = { BAIXA: '#6b7280', NORMAL: '#374151', ALTA: '#d97706', URGENTE: '#dc2626' }

const avalSort = ref({ key: 'numero', dir: 'asc' })
const repSort  = ref({ key: 'numero', dir: 'asc' })

function sortValue(item, key) {
  if (key === 'prioridade') return PRIORIDADE_ORDER[item.prioridade] ?? 0
  if (key === 'data_entrada') return new Date(item.data_entrada || 0).getTime()
  return (item[key] ?? '').toString().toLowerCase()
}

function applySort(arr, { key, dir }) {
  return [...arr].sort((a, b) => {
    const va = sortValue(a, key)
    const vb = sortValue(b, key)
    if (va < vb) return dir === 'asc' ? -1 : 1
    if (va > vb) return dir === 'asc' ? 1 : -1
    return 0
  })
}

function matchSearch(o) {
  if (!search.value.trim()) return true
  const q = search.value.trim().toLowerCase()
  return (
    (o.numero || '').toLowerCase().includes(q) ||
    (o.cliente_nome || '').toLowerCase().includes(q) ||
    (o.trotinete_numero_serie || '').toLowerCase().includes(q)
  )
}

const avaliacao = computed(() => {
  const filtered = ordens.value.filter(o => ESTADOS_AVALIACAO.includes(o.estado) && !o.tem_timer_ativo && matchSearch(o))
  return applySort(filtered, avalSort.value)
})

const reparacao = computed(() => {
  const filtered = ordens.value.filter(o => ESTADOS_REPARACAO.includes(o.estado) && !o.tem_timer_ativo && matchSearch(o))
  return applySort(filtered, repSort.value)
})

function toggleSort(section, key) {
  const s = section === 'aval' ? avalSort : repSort
  if (s.value.key === key) {
    s.value = { key, dir: s.value.dir === 'asc' ? 'desc' : 'asc' }
  } else {
    s.value = { key, dir: 'asc' }
  }
}

function sortIcon(sort, key) {
  if (sort.key !== key) return '↕'
  return sort.dir === 'asc' ? '↑' : '↓'
}

const isFiltered = computed(() =>
  search.value.trim() !== '' ||
  avalSort.value.key !== 'numero' || avalSort.value.dir !== 'asc' ||
  repSort.value.key  !== 'numero' || repSort.value.dir  !== 'asc'
)

function clearSearch() {
  search.value = ''
  avalSort.value = { key: 'numero', dir: 'asc' }
  repSort.value  = { key: 'numero', dir: 'asc' }
}

let pollInterval

async function fetch() {
  loading.value = true
  try {
    const { data } = await getOrdensServico({ page_size: 100 })
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

function handleRowClick(os) {
  router.push(`/oficina/${os.id}`)
}

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

    <div class="toolbar">
      <input
        v-model="search"
        class="search-input"
        type="search"
        placeholder="Pesquisar por número, cliente ou trotinete…"
      />
      <button v-if="isFiltered" class="btn btn--ghost btn--sm" @click="clearSearch">Limpar</button>
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
            <th class="th-sort" @click="toggleSort('aval', 'numero')">
              Número <span class="sort-icon">{{ sortIcon(avalSort, 'numero') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('aval', 'trotinete_numero_serie')">
              Trotinete <span class="sort-icon">{{ sortIcon(avalSort, 'trotinete_numero_serie') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('aval', 'cliente_nome')">
              Cliente <span class="sort-icon">{{ sortIcon(avalSort, 'cliente_nome') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('aval', 'estado')">
              Estado <span class="sort-icon">{{ sortIcon(avalSort, 'estado') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('aval', 'prioridade')">
              Prioridade <span class="sort-icon">{{ sortIcon(avalSort, 'prioridade') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('aval', 'data_entrada')">
              Entrada <span class="sort-icon">{{ sortIcon(avalSort, 'data_entrada') }}</span>
            </th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="o in avaliacao"
            :key="o.id"
            class="row"
            @click="handleRowClick(o)"
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
            <th class="th-sort" @click="toggleSort('rep', 'numero')">
              Número <span class="sort-icon">{{ sortIcon(repSort, 'numero') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('rep', 'trotinete_numero_serie')">
              Trotinete <span class="sort-icon">{{ sortIcon(repSort, 'trotinete_numero_serie') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('rep', 'cliente_nome')">
              Cliente <span class="sort-icon">{{ sortIcon(repSort, 'cliente_nome') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('rep', 'estado')">
              Estado <span class="sort-icon">{{ sortIcon(repSort, 'estado') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('rep', 'prioridade')">
              Prioridade <span class="sort-icon">{{ sortIcon(repSort, 'prioridade') }}</span>
            </th>
            <th>Timer</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="o in reparacao"
            :key="o.id"
            class="row"
            @click="handleRowClick(o)"
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
.page-header { margin-bottom: 1.25rem; }
.page-header h1 { margin-bottom: 0.25rem; }
.sub { font-size: 0.85rem; color: #6b7280; }

.toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
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

.search-input {
  width: 100%;
  max-width: 420px;
  padding: 0.55rem 0.9rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #374151;
  background: #fff;
  outline: none;
}
.search-input:focus {
  border-color: #1abc9c;
  box-shadow: 0 0 0 3px rgba(26,188,156,0.15);
}

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
.table th { font-size: 0.72rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.04em; padding: 0.75rem 1rem; border-bottom: 1px solid #e5e7eb; text-align: left; background: #f9fafb; user-select: none; }
.table td { padding: 0.85rem 1rem; border-bottom: 1px solid #f3f4f6; color: #374151; }
.table tbody tr:last-child td { border-bottom: none; }

.th-sort { cursor: pointer; }
.th-sort:hover { background: #f0fdf4; color: #374151; }

.sort-icon { margin-left: 0.25rem; opacity: 0.6; font-size: 0.7rem; }

.row { cursor: pointer; transition: background 0.1s; }
.row:hover { background: #f0fdf4; }

.mono { font-family: 'Courier New', monospace; font-size: 0.82rem; }
.atraso-badge { background: #fef3c7; color: #92400e; font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.5rem; border-radius: 999px; }
.timer-on { color: #1abc9c; font-weight: 700; font-size: 0.82rem; }
.timer-off { color: #9ca3af; font-size: 0.82rem; }

</style>
