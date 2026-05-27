<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getServicos, createServico } from '../../services/servicos.js'

const router = useRouter()

const servicos = ref([])
const loading  = ref(false)
const error    = ref('')

const search  = ref('')
const sortKey = ref('nome')
const sortDir = ref('asc')

const showModal   = ref(false)
const form        = ref({ nome: '', preco_base: '', ativo: true })
const formLoading = ref(false)
const formError   = ref('')

async function load() {
  loading.value = true
  error.value   = ''
  try {
    const { data } = await getServicos()
    servicos.value = data.data ?? []
  } catch {
    error.value = 'Erro ao carregar serviços.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

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

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  let list = q
    ? servicos.value.filter(s => s.nome.toLowerCase().includes(q))
    : [...servicos.value]

  list.sort((a, b) => {
    let va = a[sortKey.value]
    let vb = b[sortKey.value]
    if (typeof va === 'string') va = va.toLowerCase()
    if (typeof vb === 'string') vb = vb.toLowerCase()
    if (va < vb) return sortDir.value === 'asc' ? -1 : 1
    if (va > vb) return sortDir.value === 'asc' ? 1 : -1
    return 0
  })
  return list
})

function openCreate() {
  form.value      = { nome: '', preco_base: '', ativo: true }
  formError.value = ''
  showModal.value = true
}

async function submitCreate() {
  formError.value = ''
  if (!form.value.nome.trim()) { formError.value = 'Nome obrigatório.'; return }
  const preco = parseFloat(form.value.preco_base)
  if (isNaN(preco) || preco < 0) { formError.value = 'Preço inválido.'; return }

  formLoading.value = true
  try {
    const { data } = await createServico({ nome: form.value.nome.trim(), preco_base: preco, ativo: form.value.ativo })
    showModal.value = false
    router.push(`/servicos/${data.data.id}`)
  } catch (e) {
    formError.value = e?.response?.data?.detail?.detail ?? 'Erro ao guardar serviço.'
  } finally {
    formLoading.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Catálogo de Serviços</h1>
      <button class="btn btn--primary" @click="openCreate">+ Novo Serviço</button>
    </div>

    <div class="toolbar">
      <input v-model="search" class="search-input" placeholder="Pesquisar serviço…" />
      <span class="result-count">{{ filtered.length }} serviço{{ filtered.length !== 1 ? 's' : '' }}</span>
    </div>

    <p v-if="error" class="msg-error">{{ error }}</p>
    <div v-else-if="loading" class="msg-empty">A carregar...</div>
    <div v-else-if="filtered.length === 0" class="msg-empty">
      {{ search ? `Nenhum resultado para "${search}".` : 'Nenhum serviço criado ainda.' }}
    </div>

    <table v-else class="tbl">
      <thead>
        <tr>
          <th class="th-sort" @click="toggleSort('nome')">Nome <span class="sort-icon">{{ sortIcon('nome') }}</span></th>
          <th class="th-sort th-num" @click="toggleSort('preco_base')">Preço base <span class="sort-icon">{{ sortIcon('preco_base') }}</span></th>
          <th class="th-sort" @click="toggleSort('ativo')">Estado <span class="sort-icon">{{ sortIcon('ativo') }}</span></th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="s in filtered"
          :key="s.id"
          class="tbl-row"
          :class="{ 'row--inactive': !s.ativo }"
          @click="router.push(`/servicos/${s.id}`)"
        >
          <td class="td-nome">{{ s.nome }}</td>
          <td class="td-num">{{ s.preco_base.toFixed(2) }} €</td>
          <td>
            <span class="chip" :class="s.ativo ? 'chip--green' : 'chip--gray'">
              {{ s.ativo ? 'Ativo' : 'Inativo' }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <Teleport to="body">
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-hd">
          <span class="modal-hd-title">Novo Serviço</span>
          <button class="modal-close" @click="showModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="field">
            <label>Nome *</label>
            <input v-model="form.nome" placeholder="Ex: Revisão geral" />
          </div>
          <div class="field">
            <label>Preço base (€) *</label>
            <input v-model="form.preco_base" type="number" step="0.01" min="0" placeholder="0.00" />
          </div>
          <div class="field field--checkbox">
            <label>
              <input type="checkbox" v-model="form.ativo" />
              Ativo (visível para mecânicos)
            </label>
          </div>
          <p v-if="formError" class="msg-inline-err">{{ formError }}</p>
        </div>
        <div class="modal-ft">
          <button class="btn btn--ghost btn--sm" :disabled="formLoading" @click="showModal = false">Cancelar</button>
          <button class="btn btn--primary" :disabled="formLoading" @click="submitCreate">
            {{ formLoading ? 'A guardar...' : 'Criar Serviço' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.page { padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; }
.page-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0; }

.toolbar { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }
.search-input { flex: 1; max-width: 340px; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 8px; font-size: 0.875rem; color: #374151; outline: none; }
.search-input:focus { border-color: #1abc9c; box-shadow: 0 0 0 3px rgba(26,188,156,0.12); }
.result-count { margin-left: auto; font-size: 0.82rem; color: #9ca3af; }

.tbl { width: 100%; border-collapse: collapse; font-size: 0.875rem; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.tbl th { padding: 0.65rem 1rem; text-align: left; font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
.tbl td { padding: 0.8rem 1rem; border-bottom: 1px solid #f1f5f9; color: #374151; vertical-align: middle; }
.tbl tbody tr:last-child td { border-bottom: none; }
.tbl-row { cursor: pointer; transition: background 0.1s; }
.tbl-row:hover { background: #f0fdf4; }
.row--inactive td { opacity: 0.5; }
.td-nome { font-weight: 600; color: #111827; }
.td-num  { text-align: right; font-variant-numeric: tabular-nums; }
.th-sort { cursor: pointer; user-select: none; white-space: nowrap; }
.th-sort:hover { color: #1abc9c; }
.th-num { text-align: right; }
.sort-icon { font-size: 0.65rem; margin-left: 0.2rem; opacity: 0.6; }

.chip { display: inline-block; padding: 0.2rem 0.55rem; border-radius: 99px; font-size: 0.72rem; font-weight: 600; }
.chip--green { background: #dcfce7; color: #166534; }
.chip--gray  { background: #f1f5f9; color: #64748b; }

.btn { padding: 0.55rem 1.2rem; border-radius: 7px; font-size: 0.875rem; font-weight: 600; cursor: pointer; border: none; transition: opacity 0.15s; white-space: nowrap; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--ghost   { background: #f1f5f9; color: #374151; border: 1px solid #d1d5db; }
.btn--sm      { padding: 0.4rem 0.85rem; font-size: 0.825rem; }
.btn:hover    { opacity: 0.85; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }

.msg-empty       { padding: 2rem; text-align: center; color: #9ca3af; font-size: 0.9rem; }
.msg-error       { padding: 2rem; text-align: center; color: #dc2626; }
.msg-inline-err  { color: #dc2626; font-size: 0.85rem; margin: 0; }

.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 12px; width: 100%; max-width: 420px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); overflow: hidden; }
.modal-hd { display: flex; align-items: center; justify-content: space-between; padding: 1.25rem 1.5rem; border-bottom: 1px solid #f1f5f9; }
.modal-hd-title { font-size: 1rem; font-weight: 700; color: #111827; }
.modal-close { background: none; border: none; font-size: 1rem; color: #9ca3af; cursor: pointer; padding: 0.25rem; }
.modal-close:hover { color: #374151; }
.modal-body { padding: 1.5rem; }
.modal-ft { display: flex; justify-content: flex-end; gap: 0.75rem; padding: 1rem 1.5rem; border-top: 1px solid #f1f5f9; }

.field { display: flex; flex-direction: column; gap: 0.3rem; margin-bottom: 1rem; }
.field label { font-size: 0.8rem; font-weight: 600; color: #374151; }
.field input { padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 7px; font-size: 0.875rem; color: #374151; outline: none; width: 100%; box-sizing: border-box; }
.field input:focus { border-color: #1abc9c; box-shadow: 0 0 0 3px rgba(26,188,156,0.12); }
.field--checkbox label { display: flex; align-items: center; gap: 0.5rem; text-transform: none; font-weight: 400; font-size: 0.875rem; cursor: pointer; }
.field--checkbox input { width: auto; }
</style>
