<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useAuthStore } from '../../store/auth.js'
import { getAuditoria } from '../../services/auditoria.js'
import { getLojas } from '../../services/lojas.js'

const auth = useAuthStore()
const isAdmin = computed(() => auth.getCurrentUser?.perfil === 'ADMINISTRADOR')

const registos  = ref([])
const lojas     = ref([])
const loading   = ref(false)
const error     = ref('')
const total     = ref(0)
const page      = ref(1)
const pageSize  = 20

const filtroEvento    = ref('')
const filtroLoja      = ref('')

// ── Event combobox ────────────────────────────────────────────────────────────
const comboSearch  = ref('')
const comboOpen    = ref(false)
const comboRef     = ref(null)

const eventoLabel = computed(() =>
  EVENTOS.find(e => e.value === filtroEvento.value)?.label ?? 'Todos os eventos'
)

const comboFiltered = computed(() => {
  const q = comboSearch.value.trim().toLowerCase()
  if (!q) return EVENTOS
  return EVENTOS.filter(e => e.label.toLowerCase().includes(q))
})

function comboSelect(value) {
  filtroEvento.value = value
  comboSearch.value  = ''
  comboOpen.value    = false
  applyFilters()
}

function comboFocus() {
  comboSearch.value = ''
  comboOpen.value   = true
}

function onClickOutside(e) {
  if (comboRef.value && !comboRef.value.contains(e.target)) {
    comboOpen.value   = false
    comboSearch.value = ''
  }
}

onMounted(() => document.addEventListener('mousedown', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', onClickOutside))
const filtroDataInicio = ref('')
const filtroDataFim   = ref('')

const EVENTOS = [
  { value: '',                                  label: 'Todos os eventos' },
  // Auth
  { value: 'LOGIN_SUCESSO',                     label: 'Login bem-sucedido' },
  { value: 'LOGIN_FALHA',                       label: 'Login falhado' },
  { value: 'ACESSO_NEGADO',                     label: 'Acesso negado' },
  // Ordens de serviço
  { value: 'OS_CRIADA',                         label: 'OS criada' },
  { value: 'OS_ESTADO_ALTERADO',                label: 'Estado de OS alterado' },
  { value: 'OS_DIAGNOSTICO_SUBMETIDO',          label: 'Diagnóstico submetido' },
  { value: 'OS_PECA_ADICIONADA',                label: 'Peça adicionada a OS' },
  { value: 'OS_MECANICO_ATRIBUIDO',             label: 'Mecânico atribuído' },
  { value: 'OS_OBSERVACAO_ADICIONADA',          label: 'Observação adicionada' },
  // Stock
  { value: 'STOCK_ENTRADA',                     label: 'Entrada de stock' },
  { value: 'STOCK_TRANSFERENCIA',               label: 'Transferência de stock' },
  { value: 'STOCK_MINIMO_ALTERADO',             label: 'Stock mínimo alterado' },
  // Transferências
  { value: 'TRANSFERENCIA_CRIADA',              label: 'Pedido de transferência criado' },
  { value: 'TRANSFERENCIA_RESPONDIDA',          label: 'Pedido de transferência respondido' },
  { value: 'TRANSFERENCIA_RECEPCAO_CONFIRMADA', label: 'Receção de transferência confirmada' },
  { value: 'TRANSFERENCIA_CANCELADA',           label: 'Pedido de transferência cancelado' },
  // Pedidos de peça
  { value: 'PEDIDO_PECA_CRIADO',                label: 'Pedido de peça criado' },
  { value: 'PEDIDO_PECA_RESPONDIDO',            label: 'Pedido de peça respondido' },
  // Faturação
  { value: 'FATURA_EMITIDA',                    label: 'Fatura emitida' },
  // Entidades
  { value: 'CLIENTE_CRIADO',                    label: 'Cliente criado' },
  { value: 'CLIENTE_ATUALIZADO',                label: 'Cliente atualizado' },
  { value: 'TROTINETE_REGISTADA',               label: 'Trotinete registada' },
  { value: 'PECA_CRIADA',                       label: 'Peça criada no catálogo' },
  { value: 'UTILIZADOR_CRIADO',                 label: 'Utilizador criado' },
  { value: 'UTILIZADOR_ATUALIZADO',             label: 'Utilizador atualizado' },
  { value: 'UTILIZADOR_PASSWORD_ALTERADA',      label: 'Password de utilizador alterada' },
  { value: 'SERVICO_CRIADO',                    label: 'Serviço criado no catálogo' },
  { value: 'SERVICO_ATUALIZADO',                label: 'Serviço atualizado' },
]

const EVENTO_COLOR = {
  // Auth — verde/vermelho
  LOGIN_SUCESSO:                    { bg: '#dcfce7', color: '#166534' },
  LOGIN_FALHA:                      { bg: '#fee2e2', color: '#991b1b' },
  ACESSO_NEGADO:                    { bg: '#fee2e2', color: '#991b1b' },
  // OS — violeta
  OS_CRIADA:                        { bg: '#ede9fe', color: '#5b21b6' },
  OS_ESTADO_ALTERADO:               { bg: '#ede9fe', color: '#5b21b6' },
  OS_DIAGNOSTICO_SUBMETIDO:         { bg: '#ede9fe', color: '#5b21b6' },
  OS_PECA_ADICIONADA:               { bg: '#ede9fe', color: '#5b21b6' },
  OS_MECANICO_ATRIBUIDO:            { bg: '#ede9fe', color: '#5b21b6' },
  OS_OBSERVACAO_ADICIONADA:         { bg: '#ede9fe', color: '#5b21b6' },
  // Stock — azul
  STOCK_ENTRADA:                    { bg: '#dbeafe', color: '#1e40af' },
  STOCK_TRANSFERENCIA:              { bg: '#dbeafe', color: '#1e40af' },
  STOCK_MINIMO_ALTERADO:            { bg: '#dbeafe', color: '#1e40af' },
  // Transferências — ciano
  TRANSFERENCIA_CRIADA:             { bg: '#cffafe', color: '#0e7490' },
  TRANSFERENCIA_RESPONDIDA:         { bg: '#cffafe', color: '#0e7490' },
  TRANSFERENCIA_RECEPCAO_CONFIRMADA:{ bg: '#cffafe', color: '#0e7490' },
  TRANSFERENCIA_CANCELADA:          { bg: '#fee2e2', color: '#991b1b' },
  // Pedidos de peça — laranja
  PEDIDO_PECA_CRIADO:               { bg: '#ffedd5', color: '#9a3412' },
  PEDIDO_PECA_RESPONDIDO:           { bg: '#ffedd5', color: '#9a3412' },
  // Faturação — azul claro
  FATURA_EMITIDA:                   { bg: '#e0f2fe', color: '#0369a1' },
  // Entidades — cinza-verde
  CLIENTE_CRIADO:                   { bg: '#d1fae5', color: '#065f46' },
  CLIENTE_ATUALIZADO:               { bg: '#d1fae5', color: '#065f46' },
  TROTINETE_REGISTADA:              { bg: '#d1fae5', color: '#065f46' },
  PECA_CRIADA:                      { bg: '#fef9c3', color: '#854d0e' },
  UTILIZADOR_CRIADO:                { bg: '#f3e8ff', color: '#6b21a8' },
  UTILIZADOR_ATUALIZADO:            { bg: '#f3e8ff', color: '#6b21a8' },
  UTILIZADOR_PASSWORD_ALTERADA:     { bg: '#fce7f3', color: '#9d174d' },
  SERVICO_CRIADO:                   { bg: '#fef9c3', color: '#854d0e' },
  SERVICO_ATUALIZADO:               { bg: '#fef9c3', color: '#854d0e' },
}

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const sortKey = ref('')
const sortDir = ref(1)

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 1 ? -1 : 1
  } else {
    sortKey.value = key
    sortDir.value = 1
  }
}

function sortIcon(key) {
  if (sortKey.value !== key) return '↕'
  return sortDir.value === 1 ? '↑' : '↓'
}

const sortedRegistos = computed(() => {
  if (!sortKey.value) return registos.value
  return [...registos.value].sort((a, b) => {
    const av = a[sortKey.value] ?? ''
    const bv = b[sortKey.value] ?? ''
    return av < bv ? -sortDir.value : av > bv ? sortDir.value : 0
  })
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = { page: page.value, page_size: pageSize }
    if (filtroEvento.value)     params.evento      = filtroEvento.value
    if (filtroDataInicio.value) params.data_inicio  = filtroDataInicio.value
    if (filtroDataFim.value)    params.data_fim     = filtroDataFim.value
    if (isAdmin.value && filtroLoja.value) params.loja_id = filtroLoja.value
    const { data } = await getAuditoria(params)
    registos.value = data.data ?? []
    total.value    = data.total ?? 0
  } catch {
    error.value = 'Erro ao carregar registos de auditoria.'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  page.value = 1
  load()
}

function prevPage() { if (page.value > 1) { page.value--; load() } }
function nextPage() { if (page.value < totalPages.value) { page.value++; load() } }

function fmtDateTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('pt-PT', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

onMounted(async () => {
  if (isAdmin.value) {
    try {
      const r = await getLojas({ page_size: 50 })
      lojas.value = r.data.data ?? []
    } catch {}
  }
  await load()
})
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Auditoria</h1>
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <!-- Searchable event combobox -->
      <div class="combo" ref="comboRef">
        <div class="combo-input-wrap" @click="comboFocus">
          <input
            class="combo-input"
            :placeholder="comboOpen ? 'Pesquisar evento…' : eventoLabel"
            :value="comboOpen ? comboSearch : ''"
            @input="comboSearch = $event.target.value"
            @focus="comboFocus"
          />
          <span class="combo-arrow" :class="{ 'combo-arrow--open': comboOpen }">▾</span>
        </div>
        <ul v-if="comboOpen" class="combo-list">
          <li
            v-for="e in comboFiltered"
            :key="e.value"
            class="combo-item"
            :class="{ 'combo-item--active': e.value === filtroEvento }"
            @mousedown.prevent="comboSelect(e.value)"
          >{{ e.label }}</li>
          <li v-if="comboFiltered.length === 0" class="combo-empty">Sem resultados</li>
        </ul>
      </div>

      <select v-if="isAdmin" v-model="filtroLoja" @change="applyFilters">
        <option value="">Todas as lojas</option>
        <option v-for="l in lojas" :key="l.id" :value="l.id">{{ l.nome }}</option>
      </select>
      <div class="date-range">
        <input type="date" v-model="filtroDataInicio" @change="applyFilters" title="A partir de" />
        <span class="sep">até</span>
        <input type="date" v-model="filtroDataFim" @change="applyFilters" title="Até" />
      </div>
      <button class="btn btn--ghost btn--sm" @click="filtroEvento = ''; filtroLoja = ''; filtroDataInicio = ''; filtroDataFim = ''; comboSearch = ''; applyFilters()">Limpar</button>
      <span class="result-count">{{ total }} registo{{ total !== 1 ? 's' : '' }}</span>
    </div>

    <p v-if="error" class="msg-error">{{ error }}</p>
    <div v-else-if="loading" class="msg-empty">A carregar...</div>
    <p v-else-if="registos.length === 0" class="msg-empty">Sem registos para os filtros selecionados.</p>

    <table v-else class="tbl">
      <thead>
        <tr>
          <th @click="toggleSort('timestamp')" class="th-sort">Data/hora <span class="sort-icon">{{ sortIcon('timestamp') }}</span></th>
          <th @click="toggleSort('evento')" class="th-sort">Evento <span class="sort-icon">{{ sortIcon('evento') }}</span></th>
          <th @click="toggleSort('utilizador_nome')" class="th-sort">Utilizador <span class="sort-icon">{{ sortIcon('utilizador_nome') }}</span></th>
          <th @click="toggleSort('loja_id')" class="th-sort">Loja <span class="sort-icon">{{ sortIcon('loja_id') }}</span></th>
          <th>Descrição</th>
          <th>IP</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in sortedRegistos" :key="r.id">
          <td class="td-date mono">{{ fmtDateTime(r.timestamp) }}</td>
          <td>
            <span class="chip" :style="EVENTO_COLOR[r.evento] || { bg: '#f1f5f9', color: '#64748b' }">
              {{ EVENTOS.find(e => e.value === r.evento)?.label || r.evento }}
            </span>
          </td>
          <td>{{ r.utilizador_nome || '—' }}</td>
          <td>{{ r.loja_id ? `#${r.loja_id}` : '—' }}</td>
          <td class="td-desc">{{ r.descricao }}</td>
          <td class="mono td-ip">{{ r.ip_origem || '—' }}</td>
        </tr>
      </tbody>
    </table>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button class="btn btn--ghost btn--sm" :disabled="page === 1" @click="prevPage">← Anterior</button>
      <span class="page-info">Página {{ page }} de {{ totalPages }}</span>
      <button class="btn btn--ghost btn--sm" :disabled="page === totalPages" @click="nextPage">Seguinte →</button>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 1.5rem 2rem; }
.page-header { margin-bottom: 1.25rem; }
.page-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0; }

.filter-bar { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.filter-bar select, .filter-bar input[type="date"] { padding: 0.45rem 0.7rem; border: 1px solid #d1d5db; border-radius: 7px; font-size: 0.875rem; color: #374151; background: #fff; outline: none; }
.filter-bar select:focus, .filter-bar input:focus { border-color: #1abc9c; }
.date-range { display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0; }
.sep { font-size: 0.82rem; color: #6b7280; }

/* Combobox */
.combo { position: relative; min-width: 320px; }
.combo-input-wrap {
  display: flex;
  align-items: center;
  border: 1px solid #d1d5db;
  border-radius: 7px;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.15s;
}
.combo-input-wrap:focus-within { border-color: #1abc9c; }
.combo-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 0.45rem 0.5rem 0.45rem 0.7rem;
  font-size: 0.875rem;
  color: #374151;
  background: transparent;
  cursor: pointer;
  min-width: 0;
}
.combo-arrow {
  padding: 0 0.5rem;
  font-size: 0.75rem;
  color: #9ca3af;
  transition: transform 0.15s;
  user-select: none;
}
.combo-arrow--open { transform: rotate(180deg); }

.combo-list {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  max-height: 260px;
  overflow-y: auto;
  z-index: 200;
  list-style: none;
  margin: 0;
  padding: 0.3rem 0;
}
.combo-item {
  padding: 0.5rem 0.9rem;
  font-size: 0.875rem;
  color: #374151;
  cursor: pointer;
  transition: background 0.1s;
}
.combo-item:hover { background: #f0fdf4; }
.combo-item--active { color: #1abc9c; font-weight: 600; background: #f0fdf4; }
.combo-empty { padding: 0.6rem 0.9rem; font-size: 0.85rem; color: #9ca3af; }
.result-count { margin-left: auto; font-size: 0.82rem; color: #9ca3af; }

.tbl { width: 100%; border-collapse: collapse; font-size: 0.875rem; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.tbl th { padding: 0.65rem 1rem; text-align: left; font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
.th-sort { cursor: pointer; user-select: none; white-space: nowrap; }
.th-sort:hover { color: #1abc9c; }
.sort-icon { font-size: 0.65rem; margin-left: 0.2rem; opacity: 0.6; }
.tbl td { padding: 0.75rem 1rem; border-bottom: 1px solid #f1f5f9; color: #374151; vertical-align: top; }
.tbl tbody tr:last-child td { border-bottom: none; }
.tbl tbody tr:hover { background: #f8fafc; }

.td-date { white-space: nowrap; }
.td-desc { max-width: 320px; font-size: 0.83rem; color: #6b7280; }
.td-ip { font-size: 0.78rem; color: #9ca3af; }

.chip { display: inline-block; padding: 0.2rem 0.55rem; border-radius: 99px; font-size: 0.72rem; font-weight: 600; white-space: nowrap; }
.mono { font-family: 'Courier New', monospace; font-size: 0.82rem; }

.msg-empty { padding: 2rem; text-align: center; font-size: 0.9rem; color: #9ca3af; }
.msg-error { padding: 2rem; text-align: center; color: #dc2626; }

.btn { padding: 0.5rem 1.1rem; border-radius: 7px; font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; transition: opacity 0.15s; }
.btn--ghost { background: #f1f5f9; color: #374151; border: 1px solid #d1d5db; }
.btn--sm { padding: 0.3rem 0.7rem; font-size: 0.8rem; }
.btn:hover { opacity: 0.85; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }

.pagination { display: flex; align-items: center; gap: 1rem; justify-content: center; margin-top: 1.5rem; }
.page-info { font-size: 0.875rem; color: #6b7280; }
</style>
