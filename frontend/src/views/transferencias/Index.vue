<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth.js'
import { getTransferencias, cancelarTransferencia } from '../../services/transferencias.js'

const router = useRouter()
const auth   = useAuthStore()

const transferencias = ref([])
const loading        = ref(false)
const error          = ref('')

// ── Filters & sort ─────────────────────────────────────────────────────
const search       = ref('')
const activePreset = ref('mes')
const customStart  = ref('')
const customEnd    = ref('')
const sort         = ref({ key: 'data_pedido', dir: 'desc' })

const PRESETS = [
  { key: 'hoje',          label: 'Hoje' },
  { key: 'semana',        label: 'Esta semana' },
  { key: 'mes',           label: 'Este mês' },
  { key: 'personalizado', label: 'Personalizado' },
]

function toDateStr(d) { return d.toISOString().slice(0, 10) }

function getDateRange() {
  const now   = new Date()
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

function sortValue(t, key) {
  if (key === 'data_pedido') return (t.data_pedido || '').slice(0, 10)
  if (key === 'peca')        return (t.peca?.nome || '').toLowerCase()
  if (key === 'origem')      return (t.loja_origem?.nome || '').toLowerCase()
  if (key === 'destino')     return (t.loja_destino?.nome || '').toLowerCase()
  if (key === 'quantidade')  return t.quantidade ?? 0
  return (t[key] ?? '').toString().toLowerCase()
}

const filtered = computed(() => {
  const { start, end } = getDateRange()
  const q = search.value.trim().toLowerCase()

  let items = transferencias.value

  if (start) items = items.filter(t => (t.data_pedido || '').slice(0, 10) >= start)
  if (end)   items = items.filter(t => (t.data_pedido || '').slice(0, 10) <= end)

  if (q) {
    items = items.filter(t =>
      (t.numero          || '').toLowerCase().includes(q) ||
      (t.peca?.nome      || '').toLowerCase().includes(q) ||
      (t.peca?.referencia|| '').toLowerCase().includes(q) ||
      (t.loja_origem?.nome  || '').toLowerCase().includes(q) ||
      (t.loja_destino?.nome || '').toLowerCase().includes(q)
    )
  }

  const { key, dir } = sort.value
  return [...items].sort((a, b) => {
    const va = sortValue(a, key)
    const vb = sortValue(b, key)
    if (va < vb) return dir === 'asc' ? -1 : 1
    if (va > vb) return dir === 'asc' ? 1  : -1
    return 0
  })
})

const isFiltered = computed(() =>
  search.value.trim() !== '' ||
  sort.value.key !== 'data_pedido' ||
  sort.value.dir !== 'desc'
)

function toggleSort(key) {
  if (sort.value.key === key) {
    sort.value = { key, dir: sort.value.dir === 'asc' ? 'desc' : 'asc' }
  } else {
    sort.value = { key, dir: key === 'data_pedido' ? 'desc' : 'asc' }
  }
}

function sortIcon(key) {
  if (sort.value.key !== key) return '↕'
  return sort.value.dir === 'asc' ? '↑' : '↓'
}

function clearFilters() {
  search.value = ''
  sort.value   = { key: 'data_pedido', dir: 'desc' }
}

// ── Estado chip colors ─────────────────────────────────────────────────
const ESTADO_COLOR = {
  PENDENTE:  { bg: '#fef9c3', color: '#854d0e' },
  ACEITE:    { bg: '#dbeafe', color: '#1e40af' },
  CONCLUIDA: { bg: '#dcfce7', color: '#166534' },
  RECUSADO:  { bg: '#fee2e2', color: '#991b1b' },
  CANCELADO: { bg: '#f1f5f9', color: '#64748b' },
}
function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('pt-PT')
}

// ── Data loading ────────────────────────────────────────────────────────
async function loadTransferencias() {
  loading.value = true
  try {
    const r = await getTransferencias({ page_size: 200 })
    transferencias.value = r.data ?? []
  } catch { error.value = 'Erro ao carregar transferências.' }
  finally { loading.value = false }
}

async function cancelar(id) {
  if (!confirm('Cancelar este pedido?')) return
  await cancelarTransferencia(id)
  await loadTransferencias()
}

const minhaLoja = computed(() => auth.getCurrentUser?.loja_id)

onMounted(loadTransferencias)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Transferências</h1>
    </div>

    <div>
      <p v-if="error" class="msg-error">{{ error }}</p>
      <template v-else>

        <!-- Period presets -->
        <div class="preset-bar">
          <button
            v-for="p in PRESETS" :key="p.key"
            :class="['preset-btn', { active: activePreset === p.key }]"
            @click="activePreset = p.key"
          >{{ p.label }}</button>
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
            placeholder="Pesquisar por número, peça, loja…"
          />
          <button v-if="isFiltered" class="btn btn--ghost btn--sm" @click="clearFilters">Limpar</button>
          <span class="result-count">{{ filtered.length }} resultado{{ filtered.length !== 1 ? 's' : '' }}</span>
        </div>

        <div v-if="loading" class="msg-loading">A carregar...</div>
        <p v-else-if="filtered.length === 0" class="msg-empty">Sem transferências para o período selecionado.</p>

        <table v-else class="tbl">
          <thead><tr>
            <th class="th-sort" @click="toggleSort('numero')">
              Número <span class="sort-icon">{{ sortIcon('numero') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('estado')">
              Estado <span class="sort-icon">{{ sortIcon('estado') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('peca')">
              Peça <span class="sort-icon">{{ sortIcon('peca') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('quantidade')">
              Qtd <span class="sort-icon">{{ sortIcon('quantidade') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('origem')">
              Origem <span class="sort-icon">{{ sortIcon('origem') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('destino')">
              Destino <span class="sort-icon">{{ sortIcon('destino') }}</span>
            </th>
            <th class="th-sort" @click="toggleSort('data_pedido')">
              Data <span class="sort-icon">{{ sortIcon('data_pedido') }}</span>
            </th>
            <th></th>
          </tr></thead>
          <tbody>
            <tr v-for="t in filtered" :key="t.id" class="tbl-row" @click="router.push(`/transferencias/${t.id}`)">
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
      </template>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 1.5rem 2rem; }
.page-header { margin-bottom: 1.25rem; }
.page-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0; }

/* Period presets */
.preset-bar { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.preset-btn { padding: 0.4rem 1rem; border: 1px solid #d1d5db; border-radius: 999px; background: #fff; font-size: 0.84rem; font-weight: 500; color: #374151; cursor: pointer; transition: background 0.15s, border-color 0.15s, color 0.15s; }
.preset-btn:hover { background: #f3f4f6; }
.preset-btn.active { background: #1abc9c; border-color: #1abc9c; color: #fff; font-weight: 600; }

.custom-range { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; }
.custom-range input { width: auto; }
.range-sep { font-size: 0.875rem; color: #6b7280; }

/* Toolbar */
.toolbar { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }
.search-input { padding: 0.5rem 0.9rem; border: 1px solid #d1d5db; border-radius: 8px; font-size: 0.875rem; color: #374151; background: #fff; outline: none; max-width: 360px; width: 100%; }
.search-input:focus { border-color: #1abc9c; box-shadow: 0 0 0 3px rgba(26,188,156,0.12); }
.result-count { margin-left: auto; font-size: 0.82rem; color: #9ca3af; }

/* Table */
.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 6px rgba(0,0,0,0.07); overflow: hidden; }
.tbl { width: 100%; border-collapse: collapse; font-size: 0.875rem; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.tbl th { padding: 0.65rem 1rem; text-align: left; font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid #e2e8f0; background: #f8fafc; user-select: none; }
.tbl td { padding: 0.75rem 1rem; border-bottom: 1px solid #f1f5f9; color: #374151; }
.tbl tbody tr:last-child td { border-bottom: none; }
.tbl-row { cursor: pointer; transition: background 0.1s; }
.tbl-row:hover { background: #f0fdf9; }

.th-sort { cursor: pointer; }
.th-sort:hover { background: #f0fdf4; color: #374151; }
.sort-icon { margin-left: 0.25rem; opacity: 0.6; font-size: 0.7rem; }

.mono { font-family: monospace; font-size: 0.82rem; }
.chip { display: inline-block; padding: 0.2rem 0.55rem; border-radius: 99px; font-size: 0.72rem; font-weight: 600; }
.row-actions { display: flex; gap: 0.4rem; }

.msg-empty, .msg-loading { padding: 2rem; text-align: center; font-size: 0.9rem; color: #9ca3af; }
.msg-error { padding: 2rem; text-align: center; color: #dc2626; }

.btn { padding: 0.5rem 1.1rem; border-radius: 7px; font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; transition: opacity 0.15s; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--ghost { background: #f1f5f9; color: #374151; border: 1px solid #d1d5db; }
.btn--sm { padding: 0.3rem 0.7rem; font-size: 0.8rem; }
.btn:hover { opacity: 0.85; }
</style>
