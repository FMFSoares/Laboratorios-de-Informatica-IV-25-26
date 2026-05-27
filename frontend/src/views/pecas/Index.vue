<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getPecas, createPeca } from '../../services/pecas.js'

const router = useRouter()

const CATEGORIAS = ['BATERIA', 'PNEU', 'TRAVAO', 'MOTOR', 'CONTROLADOR', 'LUZ', 'ACESSORIO', 'OUTRO']
const CAT_LABEL  = { BATERIA: 'Bateria', PNEU: 'Pneu', TRAVAO: 'Travão', MOTOR: 'Motor', CONTROLADOR: 'Controlador', LUZ: 'Luz', ACESSORIO: 'Acessório', OUTRO: 'Outro' }

const pecas      = ref([])
const total      = ref(0)
const page       = ref(1)
const pageSize   = 20
const totalPages = ref(1)
const loading    = ref(false)
const error      = ref('')

const filtroBusca     = ref('')
const filtroCategoria = ref('')
const sortKey         = ref('')
const sortDir         = ref(1)
let searchTimer = null

// ── Create modal ──────────────────────────────────────────────────────────────
const showModal = ref(false)
const saving    = ref(false)
const formError = ref('')

const emptyForm = () => ({
  referencia: '', nome: '', categoria: 'OUTRO', descricao: '',
  unidade: 'unidade', preco_custo: '', preco_venda: '', ativo: true,
})
const form = ref(emptyForm())

function openCreate() {
  form.value      = emptyForm()
  formError.value = ''
  showModal.value = true
}

function closeModal() { showModal.value = false }

async function save() {
  const { referencia, nome, categoria, preco_custo, preco_venda } = form.value
  if (!nome || !categoria)             { formError.value = 'Nome e categoria são obrigatórios.'; return }
  if (!referencia)                     { formError.value = 'Referência é obrigatória.'; return }
  if (preco_venda === '' || preco_venda === null) { formError.value = 'Preço de venda é obrigatório.'; return }

  saving.value    = true
  formError.value = ''
  try {
    await createPeca({
      ...form.value,
      descricao:   form.value.descricao  || null,
      preco_custo: preco_custo !== '' ? parseFloat(preco_custo) : undefined,
      preco_venda: parseFloat(preco_venda),
    })
    showModal.value = false
    await load()
  } catch (e) {
    formError.value = e?.response?.data?.detail?.detail ?? e?.response?.data?.detail ?? 'Erro ao guardar.'
  } finally {
    saving.value = false
  }
}

// ── Sorting ───────────────────────────────────────────────────────────────────
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

function sortedPecas() {
  if (!sortKey.value) return pecas.value
  return [...pecas.value].sort((a, b) => {
    const av = a[sortKey.value] ?? ''
    const bv = b[sortKey.value] ?? ''
    return av < bv ? -sortDir.value : av > bv ? sortDir.value : 0
  })
}

// ── Data ──────────────────────────────────────────────────────────────────────
async function load() {
  loading.value = true
  error.value   = ''
  try {
    const params = { page: page.value, page_size: pageSize, incluir_inativos: true }
    if (filtroBusca.value)     params.query     = filtroBusca.value
    if (filtroCategoria.value) params.categoria = filtroCategoria.value
    const { data } = await getPecas(params)
    pecas.value      = data.data  ?? []
    total.value      = data.total ?? 0
    totalPages.value = data.pages ?? 1
  } catch {
    error.value = 'Erro ao carregar catálogo de peças.'
  } finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; load() }, 300)
}

function onFilter() { page.value = 1; load() }
function prevPage() { if (page.value > 1)                { page.value--; load() } }
function nextPage() { if (page.value < totalPages.value) { page.value++; load() } }

function fmtPrice(v) { return v != null ? `${parseFloat(v).toFixed(2)} €` : '—' }

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Catálogo de Peças</h1>
      <button class="btn btn--primary" @click="openCreate">+ Nova Peça</button>
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <input v-model="filtroBusca" class="search-input" placeholder="Pesquisar por nome ou referência…" @input="onSearch" />
      <select v-model="filtroCategoria" @change="onFilter">
        <option value="">Todas as categorias</option>
        <option v-for="c in CATEGORIAS" :key="c" :value="c">{{ CAT_LABEL[c] }}</option>
      </select>
      <span class="result-count">{{ total }} peça{{ total !== 1 ? 's' : '' }}</span>
    </div>

    <p v-if="error" class="msg-error">{{ error }}</p>
    <div v-else-if="loading" class="msg-empty">A carregar...</div>
    <p v-else-if="pecas.length === 0" class="msg-empty">Sem peças para os filtros selecionados.</p>

    <table v-else class="tbl">
      <thead>
        <tr>
          <th @click="toggleSort('referencia')" class="th-sort">Ref. <span class="sort-icon">{{ sortIcon('referencia') }}</span></th>
          <th @click="toggleSort('nome')" class="th-sort">Nome <span class="sort-icon">{{ sortIcon('nome') }}</span></th>
          <th @click="toggleSort('categoria')" class="th-sort">Categoria <span class="sort-icon">{{ sortIcon('categoria') }}</span></th>
          <th>Unidade</th>
          <th>Preço Custo</th>
          <th>Preço Venda</th>
          <th>Margem</th>
          <th @click="toggleSort('ativo')" class="th-sort">Estado <span class="sort-icon">{{ sortIcon('ativo') }}</span></th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="p in sortedPecas()"
          :key="p.id"
          class="tbl-row"
          :class="{ 'row--inactive': !p.ativo }"
          @click="router.push(`/pecas/${p.id}`)"
        >
          <td class="mono td-ref">{{ p.referencia }}</td>
          <td class="td-nome">{{ p.nome }}</td>
          <td>{{ CAT_LABEL[p.categoria] ?? p.categoria }}</td>
          <td>{{ p.unidade }}</td>
          <td class="td-price">{{ fmtPrice(p.preco_custo) }}</td>
          <td class="td-price">{{ fmtPrice(p.preco_venda) }}</td>
          <td class="td-margem">
            <span v-if="p.preco_custo && p.preco_venda">
              {{ (((p.preco_venda - p.preco_custo) / p.preco_venda) * 100).toFixed(0) }}%
            </span>
            <span v-else>—</span>
          </td>
          <td>
            <span class="chip" :class="p.ativo ? 'chip--green' : 'chip--gray'">
              {{ p.ativo ? 'Ativa' : 'Inativa' }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="totalPages > 1" class="pagination">
      <button class="btn btn--ghost btn--sm" :disabled="page === 1" @click="prevPage">← Anterior</button>
      <span class="page-info">Página {{ page }} de {{ totalPages }}</span>
      <button class="btn btn--ghost btn--sm" :disabled="page === totalPages" @click="nextPage">Seguinte →</button>
    </div>

    <!-- Create Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h2>Nova Peça</h2>
            <button class="modal-close" @click="closeModal">✕</button>
          </div>
          <div class="modal-body">
            <p v-if="formError" class="msg-error">{{ formError }}</p>

            <div class="form-row">
              <div class="form-col">
                <label class="field-label">Referência *</label>
                <input v-model="form.referencia" class="field-input" placeholder="PEC-BAT-001" />
              </div>
              <div class="form-col">
                <label class="field-label">Categoria *</label>
                <select v-model="form.categoria" class="field-input">
                  <option v-for="c in CATEGORIAS" :key="c" :value="c">{{ CAT_LABEL[c] }}</option>
                </select>
              </div>
            </div>

            <label class="field-label">Nome *</label>
            <input v-model="form.nome" class="field-input" placeholder="Bateria 36V 7.5Ah Xiaomi" />

            <label class="field-label">Descrição</label>
            <textarea v-model="form.descricao" class="field-input field-textarea" rows="2" placeholder="Detalhes técnicos…" />

            <div class="form-row">
              <div class="form-col">
                <label class="field-label">Unidade</label>
                <input v-model="form.unidade" class="field-input" placeholder="unidade" />
              </div>
              <div class="form-col">
                <label class="field-label">Preço Custo (€)</label>
                <input v-model="form.preco_custo" class="field-input" type="number" step="0.01" min="0" placeholder="42.00" />
              </div>
              <div class="form-col">
                <label class="field-label">Preço Venda (€) *</label>
                <input v-model="form.preco_venda" class="field-input" type="number" step="0.01" min="0" placeholder="89.90" />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn--ghost" @click="closeModal">Cancelar</button>
            <button class="btn btn--primary" :disabled="saving" @click="save">
              {{ saving ? 'A guardar…' : 'Guardar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.page { padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; }
.page-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0; }

.filter-bar { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.search-input { flex: 1; min-width: 200px; padding: 0.45rem 0.75rem; border: 1px solid #d1d5db; border-radius: 7px; font-size: 0.875rem; }
.search-input:focus { outline: none; border-color: #1abc9c; }
.filter-bar select { padding: 0.45rem 0.7rem; border: 1px solid #d1d5db; border-radius: 7px; font-size: 0.875rem; color: #374151; background: #fff; }
.result-count { margin-left: auto; font-size: 0.82rem; color: #9ca3af; }

.tbl { width: 100%; border-collapse: collapse; font-size: 0.875rem; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.tbl th { padding: 0.65rem 1rem; text-align: left; font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
.tbl td { padding: 0.75rem 1rem; border-bottom: 1px solid #f1f5f9; color: #374151; }
.tbl tbody tr:last-child td { border-bottom: none; }
.tbl-row { cursor: pointer; transition: background 0.1s; }
.tbl-row:hover { background: #f0fdf4; }
.row--inactive td { opacity: 0.5; }
.td-ref { color: #6b7280; }
.td-nome { font-weight: 600; }
.td-price { font-variant-numeric: tabular-nums; text-align: right; }
.td-margem { text-align: right; font-weight: 600; color: #059669; }
.mono { font-family: monospace; font-size: 0.82rem; }

.th-sort { cursor: pointer; user-select: none; white-space: nowrap; }
.th-sort:hover { color: #1abc9c; }
.sort-icon { font-size: 0.65rem; margin-left: 0.2rem; opacity: 0.6; }

.chip { display: inline-block; padding: 0.2rem 0.55rem; border-radius: 99px; font-size: 0.72rem; font-weight: 600; }
.chip--green { background: #dcfce7; color: #166534; }
.chip--gray  { background: #f1f5f9; color: #64748b; }

.btn { padding: 0.5rem 1.1rem; border-radius: 7px; font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; transition: opacity 0.15s; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--ghost   { background: #f1f5f9; color: #374151; border: 1px solid #d1d5db; }
.btn--sm      { padding: 0.3rem 0.6rem; font-size: 0.8rem; }
.btn:hover    { opacity: 0.85; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }

.msg-empty { padding: 2rem; text-align: center; color: #9ca3af; font-size: 0.9rem; }
.msg-error { padding: 0.6rem 0.9rem; background: #fef2f2; color: #dc2626; border-radius: 7px; font-size: 0.85rem; margin-bottom: 0.75rem; }

.pagination { display: flex; align-items: center; gap: 1rem; justify-content: center; margin-top: 1.5rem; }
.page-info { font-size: 0.875rem; color: #6b7280; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 12px; width: 560px; max-width: 95vw; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.2); display: flex; flex-direction: column; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1.25rem 1.5rem 0; }
.modal-header h2 { font-size: 1.1rem; font-weight: 700; margin: 0; color: #1e293b; }
.modal-close { background: none; border: none; font-size: 1.1rem; color: #6b7280; cursor: pointer; padding: 0.25rem; }
.modal-body { padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 0.5rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; padding: 1rem 1.5rem; border-top: 1px solid #f1f5f9; }

.form-row { display: flex; gap: 0.75rem; }
.form-col { flex: 1; display: flex; flex-direction: column; gap: 0.25rem; }
.field-label { font-size: 0.8rem; font-weight: 600; color: #374151; }
.field-input { width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 7px; font-size: 0.875rem; box-sizing: border-box; }
.field-input:focus { outline: none; border-color: #1abc9c; }
.field-input:disabled { background: #f8fafc; color: #9ca3af; }
.field-textarea { resize: vertical; font-family: inherit; }
</style>
