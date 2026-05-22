<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth.js'
import { getStock, registarEntrada } from '../../services/stock.js'
import { getLojas } from '../../services/lojas.js'
import { getPecas, createPeca } from '../../services/pecas.js'
import LoadingSpinner from '../../components/ui/LoadingSpinner.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const authStore      = useAuthStore()
const perfil         = authStore.getCurrentUser?.perfil
const lojaIdUsuario  = authStore.getCurrentUser?.loja_id

const router   = useRouter()
const isGestao = computed(() => ['ADMINISTRADOR', 'GERENTE_LOJA'].includes(perfil))
const isAdmin  = computed(() => perfil === 'ADMINISTRADOR')

// ── Data ──────────────────────────────────────────────────────────────
const allItems = ref([])
const lojas    = ref([])
const pecas    = ref([])
const loading  = ref(false)

// ── Filters ───────────────────────────────────────────────────────────
const search       = ref('')
const filtroLoja   = ref(null)
const apenasAlerta = ref(false)

// ── Sort ──────────────────────────────────────────────────────────────
const sortKey = ref('peca_nome')
const sortDir = ref('asc')

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

function sortIcon(key) {
  if (sortKey.value !== key) return '↕'
  return sortDir.value === 'asc' ? '↑' : '↓'
}

// ── Filtered + sorted rows ────────────────────────────────────────────
const filteredRows = computed(() => {
  const q = search.value.trim().toLowerCase()
  let rows = allItems.value.filter(s => {
    if (apenasAlerta.value && !s.alerta) return false
    if (q && !s.peca_nome.toLowerCase().includes(q) && !s.peca_referencia.toLowerCase().includes(q)) return false
    return true
  })
  return [...rows].sort((a, b) => {
    let va = a[sortKey.value] ?? ''
    let vb = b[sortKey.value] ?? ''
    if (typeof va === 'string') { va = va.toLowerCase(); vb = vb.toLowerCase() }
    if (va < vb) return sortDir.value === 'asc' ? -1 : 1
    if (va > vb) return sortDir.value === 'asc' ? 1 : -1
    return 0
  })
})

// ── Fetch ─────────────────────────────────────────────────────────────
async function fetchStock() {
  loading.value = true
  try {
    const params = { page_size: 100 }
    if (isAdmin.value) {
      if (filtroLoja.value) params.loja_id = filtroLoja.value
    } else {
      params.loja_id = lojaIdUsuario
    }
    const { data } = await getStock(params)
    // _estado_sort: 0=Esgotado, 1=Alerta, 2=OK — used for column sort
    allItems.value = (data.data || []).map(s => ({
      ...s,
      uid: `${s.peca_id}-${s.loja_id}`,
      _estado_sort: s.quantidade === 0 ? 0 : s.alerta ? 1 : 2,
    }))
  } catch {
    allItems.value = []
  } finally {
    loading.value = false
  }
}

async function fetchMeta() {
  if (!isGestao.value) return
  try {
    const [lojasRes, pecasRes] = await Promise.all([
      getLojas({ page_size: 50 }),
      getPecas({ page_size: 100 }),
    ])
    lojas.value = lojasRes.data.data || []
    pecas.value = pecasRes.data.data || []
  } catch { /* non-critical */ }
}

onMounted(() => {
  fetchStock()
  fetchMeta()
})

function resetFilters() {
  search.value       = ''
  apenasAlerta.value = false
  filtroLoja.value   = null
  sortKey.value      = 'peca_nome'
  sortDir.value      = 'asc'
  fetchStock()
}

const hasActiveFilters = computed(() =>
  search.value || apenasAlerta.value || filtroLoja.value ||
  sortKey.value !== 'peca_nome' || sortDir.value !== 'asc'
)

// ── Entrada Modal ─────────────────────────────────────────────────────
const CATEGORIAS = [
  { value: 'BATERIA',     label: 'Bateria' },
  { value: 'PNEU',        label: 'Pneu' },
  { value: 'TRAVAO',      label: 'Travão' },
  { value: 'MOTOR',       label: 'Motor' },
  { value: 'CONTROLADOR', label: 'Controlador' },
  { value: 'LUZ',         label: 'Luz' },
  { value: 'ACESSORIO',   label: 'Acessório' },
  { value: 'OUTRO',       label: 'Outro' },
]

const showEntrada    = ref(false)
const entradaLoading = ref(false)
const entradaError   = ref('')
const entradaMode    = ref('existente') // 'existente' | 'nova'

// Existing piece fields
const entradaPecaId  = ref('')
const entradaLojaId  = ref('')
const entradaQtd     = ref(1)

// New piece fields
const novaNome       = ref('')
const novaReferencia = ref('')
const novaCategoria  = ref('OUTRO')
const novaUnidade    = ref('unidade')
const novaPrecoCusto = ref('')
const novaPrecoVenda = ref('')
const novaDescricao  = ref('')

function openEntrada() {
  entradaMode.value    = 'existente'
  entradaPecaId.value  = pecas.value[0]?.id ?? ''
  entradaLojaId.value  = isAdmin.value ? (lojas.value[0]?.id ?? '') : lojaIdUsuario
  entradaQtd.value     = 1
  entradaError.value   = ''
  novaNome.value       = ''
  novaReferencia.value = ''
  novaCategoria.value  = 'OUTRO'
  novaUnidade.value    = 'unidade'
  novaPrecoCusto.value = ''
  novaPrecoVenda.value = ''
  novaDescricao.value  = ''
  showEntrada.value    = true
}

async function submitEntrada() {
  entradaError.value = ''

  let pecaId = Number(entradaPecaId.value)

  if (entradaMode.value === 'nova') {
    if (!novaNome.value || !novaReferencia.value || !novaPrecoCusto.value || !novaPrecoVenda.value) {
      entradaError.value = 'Preencha nome, referência e ambos os preços.'
      return
    }
    entradaLoading.value = true
    try {
      const { data } = await createPeca({
        nome:        novaNome.value,
        referencia:  novaReferencia.value,
        categoria:   novaCategoria.value,
        unidade:     novaUnidade.value,
        preco_custo: Number(novaPrecoCusto.value),
        preco_venda: Number(novaPrecoVenda.value),
        descricao:   novaDescricao.value || null,
      })
      pecaId = data.data.id
      await fetchMeta() // refresh pecas list
    } catch (e) {
      entradaError.value = e?.response?.data?.detail?.detail ?? 'Erro ao criar peça.'
      entradaLoading.value = false
      return
    }
  }

  if (!pecaId || !entradaLojaId.value || entradaQtd.value < 1) {
    entradaError.value = 'Preencha todos os campos.'
    entradaLoading.value = false
    return
  }

  entradaLoading.value = true
  try {
    await registarEntrada({
      peca_id:    pecaId,
      loja_id:    Number(entradaLojaId.value),
      quantidade: Number(entradaQtd.value),
    })
    showEntrada.value = false
    fetchStock()
  } catch (e) {
    entradaError.value = e?.response?.data?.detail?.detail ?? 'Erro ao registar entrada.'
  } finally {
    entradaLoading.value = false
  }
}

</script>

<template>
  <div class="page">
    <!-- ── Header ────────────────────────────────────────────────── -->
    <div class="page-header">
      <h1>Stock</h1>
      <div v-if="isGestao" class="header-actions">
        <button class="btn btn--primary" @click="openEntrada">Registar Entrada</button>
      </div>
    </div>

    <!-- ── Search bar — all roles ────────────────────────────────── -->
    <div class="filter-bar">
      <input
        v-model="search"
        class="search-input"
        type="search"
        placeholder="Pesquisar peça…"
      />
      <select v-if="isAdmin" v-model="filtroLoja" @change="fetchStock">
        <option :value="null">Todas as lojas</option>
        <option v-for="l in lojas" :key="l.id" :value="l.id">{{ l.nome }}</option>
      </select>
      <label v-if="isGestao" class="toggle-label">
        <input type="checkbox" v-model="apenasAlerta" />
        Apenas alertas
      </label>
      <button v-if="hasActiveFilters" class="btn btn--ghost btn--sm" @click="resetFilters">Limpar</button>
    </div>

    <!-- ── Legend ──────────────────────────────────────────────────── -->
    <div v-if="isGestao" class="legend">
      <span class="dot dot--alerta"></span><span>Abaixo do mínimo</span>
      <span class="dot dot--esgotado"></span><span>Esgotado</span>
    </div>

    <!-- ── Table ──────────────────────────────────────────────────── -->
    <LoadingSpinner v-if="loading" />

    <template v-else>
      <EmptyState
        v-if="filteredRows.length === 0"
        title="Sem stock registado"
        message="Não foram encontradas peças com os filtros aplicados."
      />

      <div v-else class="table-wrap">
        <table class="stock-table">
          <thead>
            <tr>
              <th class="th--sort" :class="{ 'th--active': sortKey === 'peca_referencia' }" @click="toggleSort('peca_referencia')">
                Referência <span class="sort-icon">{{ sortIcon('peca_referencia') }}</span>
              </th>
              <th class="th--sort" :class="{ 'th--active': sortKey === 'peca_nome' }" @click="toggleSort('peca_nome')">
                Peça <span class="sort-icon">{{ sortIcon('peca_nome') }}</span>
              </th>
              <th v-if="isAdmin" class="th--sort" :class="{ 'th--active': sortKey === 'loja_nome' }" @click="toggleSort('loja_nome')">
                Loja <span class="sort-icon">{{ sortIcon('loja_nome') }}</span>
              </th>
              <th class="col-num th--sort" :class="{ 'th--active': sortKey === 'quantidade' }" @click="toggleSort('quantidade')">
                Quantidade <span class="sort-icon">{{ sortIcon('quantidade') }}</span>
              </th>
              <th v-if="isGestao" class="col-num th--sort" :class="{ 'th--active': sortKey === 'limite_minimo' }" @click="toggleSort('limite_minimo')">
                Mínimo <span class="sort-icon">{{ sortIcon('limite_minimo') }}</span>
              </th>
              <th v-if="isGestao" class="th--sort" :class="{ 'th--active': sortKey === '_estado_sort' }" @click="toggleSort('_estado_sort')">
                Estado <span class="sort-icon">{{ sortIcon('_estado_sort') }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="s in filteredRows"
              :key="s.uid"
              class="row--clickable"
              :class="{
                'row--esgotado': s.quantidade === 0,
                'row--alerta':   s.alerta && s.quantidade > 0 && isGestao,
              }"
              @click="router.push(`/pecas/${s.peca_id}`)"
            >
              <td class="mono">{{ s.peca_referencia }}</td>
              <td><RouterLink :to="`/pecas/${s.peca_id}`" class="peca-link" @click.stop>{{ s.peca_nome }}</RouterLink></td>
              <td v-if="isAdmin" class="loja-cell">{{ s.loja_nome }}</td>
              <td class="col-num qty-cell">{{ s.quantidade }}</td>
              <td v-if="isGestao" class="col-num">{{ s.limite_minimo }}</td>
              <td v-if="isGestao">
                <span v-if="s.quantidade === 0" class="badge badge--esgotado">Esgotado</span>
                <span v-else-if="s.alerta"      class="badge badge--alerta">Alerta</span>
                <span v-else                     class="badge badge--ok">OK</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>

  <!-- ── Entrada Modal ──────────────────────────────────────────────── -->
  <Teleport to="body">
    <div v-if="showEntrada" class="modal-backdrop" @click.self="showEntrada = false">
      <div class="modal modal--wide">
        <div class="modal-header">
          <h2>Registar Entrada de Stock</h2>
          <button class="modal-close" @click="showEntrada = false">×</button>
        </div>

        <!-- Mode toggle -->
        <div class="mode-tabs">
          <button :class="['mode-tab', entradaMode === 'existente' && 'mode-tab--active']" @click="entradaMode = 'existente'">
            Peça existente
          </button>
          <button :class="['mode-tab', entradaMode === 'nova' && 'mode-tab--active']" @click="entradaMode = 'nova'">
            Nova peça
          </button>
        </div>

        <div class="modal-body">
          <!-- Existing piece -->
          <template v-if="entradaMode === 'existente'">
            <div class="field">
              <label>Peça</label>
              <select v-model="entradaPecaId">
                <option value="" disabled>Selecionar peça…</option>
                <option v-for="p in pecas" :key="p.id" :value="p.id">{{ p.nome }}</option>
              </select>
            </div>
          </template>

          <!-- New piece -->
          <template v-else>
            <div class="field-row">
              <div class="field">
                <label>Nome</label>
                <input type="text" v-model="novaNome" placeholder="Nome da peça" />
              </div>
              <div class="field">
                <label>Referência</label>
                <input type="text" v-model="novaReferencia" placeholder="PEC-XXX-000" />
              </div>
            </div>
            <div class="field-row">
              <div class="field">
                <label>Categoria</label>
                <select v-model="novaCategoria">
                  <option v-for="c in CATEGORIAS" :key="c.value" :value="c.value">{{ c.label }}</option>
                </select>
              </div>
              <div class="field">
                <label>Unidade</label>
                <input type="text" v-model="novaUnidade" placeholder="unidade, par, kit…" />
              </div>
            </div>
            <div class="field-row">
              <div class="field">
                <label>Preço de Custo (€)</label>
                <input type="number" v-model="novaPrecoCusto" min="0" step="0.01" placeholder="0.00" />
              </div>
              <div class="field">
                <label>Preço de Venda (€)</label>
                <input type="number" v-model="novaPrecoVenda" min="0" step="0.01" placeholder="0.00" />
              </div>
            </div>
            <div class="field">
              <label>Descrição <span class="label-optional">(opcional)</span></label>
              <input type="text" v-model="novaDescricao" placeholder="Breve descrição da peça" />
            </div>
          </template>

          <!-- Shared fields -->
          <div v-if="isAdmin" class="field">
            <label>Loja</label>
            <select v-model="entradaLojaId">
              <option value="" disabled>Selecionar loja…</option>
              <option v-for="l in lojas" :key="l.id" :value="l.id">{{ l.nome }}</option>
            </select>
          </div>
          <div class="field">
            <label>Quantidade</label>
            <input type="number" v-model.number="entradaQtd" min="1" />
          </div>

          <p v-if="entradaError" class="field-error">{{ entradaError }}</p>
        </div>

        <div class="modal-footer">
          <button class="btn btn--ghost" @click="showEntrada = false">Cancelar</button>
          <button class="btn btn--primary" :disabled="entradaLoading" @click="submitEntrada">
            {{ entradaLoading ? 'A registar…' : entradaMode === 'nova' ? 'Criar e Registar' : 'Registar' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>

</template>

<style scoped>
.page { padding: 2rem; }

/* ── Header ─────────────────────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}
.header-actions { display: flex; gap: 0.75rem; }

/* ── Filter bar ─────────────────────────────────────────────────────── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}
.filter-bar select { width: auto; }

.search-input {
  padding: 0.55rem 0.9rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #374151;
  background: #fff;
  outline: none;
  min-width: 220px;
}
.search-input:focus {
  border-color: #1abc9c;
  box-shadow: 0 0 0 3px rgba(26,188,156,0.15);
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.875rem;
  color: #374151;
  cursor: pointer;
  user-select: none;
}

/* ── Legend ─────────────────────────────────────────────────────────── */
.legend {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 1rem;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  margin-left: 0.75rem;
}
.dot:first-child { margin-left: 0; }
.dot--alerta  { background: #f59e0b; }
.dot--esgotado { background: #9ca3af; }

/* ── Table ──────────────────────────────────────────────────────────── */
.table-wrap {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.stock-table thead th {
  background: #f9fafb;
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}
.th--sort {
  cursor: pointer;
  user-select: none;
}
.th--sort:hover { color: #1abc9c; }
.th--active { color: #1abc9c; }
.sort-icon { font-size: 0.75rem; margin-left: 0.25rem; opacity: 0.6; }

.stock-table tbody tr {
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.1s;
}
.stock-table tbody tr:last-child { border-bottom: none; }
.stock-table tbody tr:hover { background: #f9fafb; }
.row--clickable { cursor: pointer; }

.stock-table td {
  padding: 0.75rem 1rem;
  color: #111827;
  vertical-align: middle;
}

/* Row states */
.row--esgotado td { color: #9ca3af; }
.row--esgotado .qty-cell { font-weight: 600; }
.row--alerta { background: #fffbeb; }
.row--alerta:hover { background: #fef3c7 !important; }

.col-num { text-align: center; width: 100px;}
.mono { font-family: 'Courier New', monospace; font-size: 0.82rem; color: #6b7280; }
.peca-link { color: inherit; text-decoration: none; }
.peca-link:hover { color: #1abc9c; text-decoration: underline; }
.loja-cell { font-size: 0.85rem; color: #4b5563; }

/* ── Badges ─────────────────────────────────────────────────────────── */
.badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}
.badge--ok       { background: #d1fae5; color: #065f46; }
.badge--alerta   { background: #fef3c7; color: #92400e; }
.badge--esgotado { background: #f3f4f6; color: #6b7280; }

/* ── Buttons ────────────────────────────────────────────────────────── */
.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.btn:hover:not(:disabled) { opacity: 0.85; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary   { background: #1abc9c; color: #fff; }
.btn--secondary { background: #e5e7eb; color: #374151; }
.btn--ghost     { background: transparent; border: 1px solid #d1d5db; color: #374151; }
.btn--sm        { padding: 0.4rem 0.8rem; font-size: 0.825rem; }

/* ── Modals ─────────────────────────────────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
}
.modal--wide { max-width: 560px; }

/* Mode tabs */
.mode-tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
}
.mode-tab {
  flex: 1;
  padding: 0.65rem 1rem;
  background: none;
  border: none;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: color 0.15s, border-bottom 0.15s;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}
.mode-tab:hover { color: #374151; }
.mode-tab--active { color: #1abc9c; border-bottom-color: #1abc9c; font-weight: 600; }

/* Side-by-side fields */
.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.label-optional { font-weight: 400; color: #9ca3af; font-size: 0.75rem; }

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem 1rem;
  border-bottom: 1px solid #e5e7eb;
}
.modal-header h2 { margin: 0; font-size: 1.1rem; color: #111827; }

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #9ca3af;
  cursor: pointer;
  line-height: 1;
  padding: 0 0.25rem;
}
.modal-close:hover { color: #374151; }

.modal-body {
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #f3f4f6;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.field label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.field input[type="number"],
.field select {
  padding: 0.55rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #111827;
  background: #fff;
  outline: none;
  width: 100%;
}
.field input[type="number"]:focus,
.field select:focus {
  border-color: #1abc9c;
  box-shadow: 0 0 0 3px rgba(26,188,156,0.15);
}

.field-error {
  color: #dc2626;
  font-size: 0.85rem;
  margin: 0;
}
</style>
