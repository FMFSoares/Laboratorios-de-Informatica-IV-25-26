<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getLojas, createLoja } from '../../services/lojas.js'

const router = useRouter()

const lojas      = ref([])
const total      = ref(0)
const page       = ref(1)
const pageSize   = 20
const loading    = ref(false)
const error      = ref('')
const totalPages = ref(1)

const showModal = ref(false)
const saving    = ref(false)
const formError = ref('')
const form      = ref({ nome: '', cidade: '', morada: '', telefone: '', email: '' })

async function load() {
  loading.value = true
  error.value   = ''
  try {
    const { data } = await getLojas({ page: page.value, page_size: pageSize })
    lojas.value      = data.data ?? []
    total.value      = data.total ?? 0
    totalPages.value = data.pages ?? 1
  } catch {
    error.value = 'Erro ao carregar lojas.'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  form.value      = { nome: '', cidade: '', morada: '', telefone: '', email: '' }
  formError.value = ''
  showModal.value = true
}

async function save() {
  if (!form.value.nome || !form.value.cidade || !form.value.morada || !form.value.telefone) {
    formError.value = 'Nome, cidade, morada e telefone são obrigatórios.'
    return
  }
  saving.value    = true
  formError.value = ''
  try {
    const { data } = await createLoja({ ...form.value, email: form.value.email || null })
    showModal.value = false
    router.push(`/lojas/${data.data.id}`)
  } catch (e) {
    formError.value = e?.response?.data?.detail?.detail ?? e?.response?.data?.detail ?? 'Erro ao guardar.'
  } finally {
    saving.value = false
  }
}

function prevPage() { if (page.value > 1)               { page.value--; load() } }
function nextPage() { if (page.value < totalPages.value) { page.value++; load() } }

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Lojas</h1>
      <button class="btn btn--primary" @click="openCreate">+ Nova Loja</button>
    </div>

    <p v-if="error" class="msg-error">{{ error }}</p>
    <div v-else-if="loading" class="msg-empty">A carregar...</div>
    <p v-else-if="lojas.length === 0" class="msg-empty">Sem lojas registadas.</p>

    <div v-else class="card">
      <table class="tbl">
        <thead>
          <tr>
            <th>#</th>
            <th>Nome</th>
            <th>Cidade</th>
            <th>Telefone</th>
            <th>Email</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="l in lojas"
            :key="l.id"
            class="row--clickable"
            :class="{ 'row--inactive': !l.ativo }"
            @click="router.push(`/lojas/${l.id}`)"
          >
            <td class="mono">{{ l.id }}</td>
            <td class="td-nome">{{ l.nome }}</td>
            <td>{{ l.cidade }}</td>
            <td class="mono">{{ l.telefone }}</td>
            <td>{{ l.email ?? '—' }}</td>
            <td>
              <span class="chip" :class="l.ativo ? 'chip--green' : 'chip--gray'">
                {{ l.ativo ? 'Ativa' : 'Inativa' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button class="btn btn--ghost btn--sm" :disabled="page === 1" @click="prevPage">← Anterior</button>
      <span class="page-info">Página {{ page }} de {{ totalPages }}</span>
      <button class="btn btn--ghost btn--sm" :disabled="page === totalPages" @click="nextPage">Seguinte →</button>
    </div>

    <!-- Create modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal">
          <div class="modal-header">
            <h2>Nova Loja</h2>
            <button class="modal-close" @click="showModal = false">✕</button>
          </div>
          <div class="modal-body">
            <p v-if="formError" class="msg-error">{{ formError }}</p>
            <label class="field-label">Nome *</label>
            <input v-model="form.nome" class="field-input" placeholder="DLMCare Lisboa" />
            <label class="field-label">Cidade *</label>
            <input v-model="form.cidade" class="field-input" placeholder="Lisboa" />
            <label class="field-label">Morada *</label>
            <input v-model="form.morada" class="field-input" placeholder="Av. da Liberdade 100" />
            <label class="field-label">Telefone *</label>
            <input v-model="form.telefone" class="field-input" placeholder="213000001" />
            <label class="field-label">Email</label>
            <input v-model="form.email" class="field-input" type="email" placeholder="lisboa@dlmcare.pt" />
          </div>
          <div class="modal-footer">
            <button class="btn btn--ghost" @click="showModal = false">Cancelar</button>
            <button class="btn btn--primary" :disabled="saving" @click="save">
              {{ saving ? 'A criar…' : 'Criar Loja' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.page { padding: 1.5rem 2rem; display: flex; flex-direction: column; gap: 1rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; }
.page-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); overflow: hidden; }
.tbl { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.tbl th { padding: 0.65rem 1rem; text-align: left; font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
.tbl td { padding: 0.75rem 1rem; border-bottom: 1px solid #f1f5f9; color: #374151; }
.tbl tbody tr:last-child td { border-bottom: none; }
.row--clickable { cursor: pointer; }
.row--clickable:hover td { background: #f8fafc; }
.row--inactive td { opacity: 0.5; }
.td-nome { font-weight: 600; color: #1e293b; }
.mono { font-family: monospace; font-size: 0.82rem; }

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

.pagination { display: flex; align-items: center; gap: 1rem; justify-content: center; }
.page-info { font-size: 0.875rem; color: #6b7280; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 12px; width: 480px; max-width: 95vw; box-shadow: 0 20px 60px rgba(0,0,0,0.2); display: flex; flex-direction: column; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1.25rem 1.5rem 0; }
.modal-header h2 { font-size: 1.1rem; font-weight: 700; margin: 0; color: #1e293b; }
.modal-close { background: none; border: none; font-size: 1.1rem; color: #6b7280; cursor: pointer; }
.modal-body { padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 0.5rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; padding: 1rem 1.5rem; border-top: 1px solid #f1f5f9; }
.field-label { font-size: 0.8rem; font-weight: 600; color: #374151; }
.field-input { width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 7px; font-size: 0.875rem; box-sizing: border-box; }
.field-input:focus { outline: none; border-color: #1abc9c; }
</style>
