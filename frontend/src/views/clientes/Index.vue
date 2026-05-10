<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getClientes, createCliente } from '../../services/clientes.js'
import DataTable from '../../components/ui/DataTable.vue'

const router = useRouter()

const clientes = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const search = ref('')

const showModal = ref(false)
const formLoading = ref(false)
const formError = ref('')
const form = ref({
  nome: '',
  nif: '',
  telemovel: '',
  email: '',
  morada: '',
  consentimento_rgpd: false,
})

const columns = [
  { key: 'nome', label: 'Nome' },
  { key: 'nif', label: 'NIF' },
  { key: 'telemovel', label: 'Telemóvel' },
  { key: 'email', label: 'Email' },
  { key: 'data_registo', label: 'Registo' },
]

async function fetchClientes() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (search.value.trim()) params.query = search.value.trim()
    const { data } = await getClientes(params)
    clientes.value = data.data
    total.value = data.total
  } catch {
    clientes.value = []
  } finally {
    loading.value = false
  }
}

let timer
watch(search, () => {
  clearTimeout(timer)
  timer = setTimeout(() => { page.value = 1; fetchClientes() }, 350)
})
watch(page, fetchClientes)
onMounted(fetchClientes)

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('pt-PT') : '—'
}

function openModal() {
  form.value = { nome: '', nif: '', telemovel: '', email: '', morada: '', consentimento_rgpd: false }
  formError.value = ''
  showModal.value = true
}

async function submitCreate() {
  formError.value = ''
  if (!form.value.consentimento_rgpd) {
    formError.value = 'O consentimento RGPD é obrigatório.'
    return
  }
  formLoading.value = true
  try {
    const { data } = await createCliente(form.value)
    showModal.value = false
    router.push(`/clientes/${data.data.id}`)
  } catch (e) {
    formError.value = e.response?.data?.detail?.detail || 'Erro ao registar cliente.'
  } finally {
    formLoading.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>Clientes</h1>
        <p class="sub">Pesquise por nome, NIF, telemóvel ou email</p>
      </div>
      <button class="btn btn--primary" @click="openModal">+ Novo Cliente</button>
    </div>

    <div class="filter-bar">
      <input v-model="search" placeholder="Pesquisar por nome, NIF, telemóvel ou email..." style="max-width:360px" />
    </div>

    <DataTable
      :columns="columns"
      :rows="clientes"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="20"
      :clickable="true"
      row-key="id"
      empty-title="Nenhum cliente encontrado"
      empty-message="Introduza um NIF ou telemóvel para pesquisar, ou registe um novo cliente."
      @update:page="page = $event"
      @row-click="router.push(`/clientes/${$event.id}`)"
    >
      <template #cell-email="{ value }">{{ value || '—' }}</template>
      <template #cell-data_registo="{ value }">{{ fmt(value) }}</template>
      <template #actions="{ row }">
        <button class="btn-link" @click.stop="router.push(`/clientes/${row.id}`)">Ver →</button>
      </template>
    </DataTable>
  </div>

  <Teleport to="body">
    <div v-if="showModal" class="overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal__header">
          <h2>Registar Novo Cliente</h2>
          <button class="modal__close" @click="showModal = false">✕</button>
        </div>
        <form @submit.prevent="submitCreate" class="form-grid">
          <div class="field field--full">
            <label>Nome completo *</label>
            <input v-model="form.nome" required placeholder="João Silva" />
          </div>
          <div class="field">
            <label>NIF *</label>
            <input v-model="form.nif" required placeholder="123456789" maxlength="9" />
          </div>
          <div class="field">
            <label>Telemóvel *</label>
            <input v-model="form.telemovel" required placeholder="912345678" maxlength="9" />
          </div>
          <div class="field">
            <label>Email</label>
            <input v-model="form.email" type="email" placeholder="joao@email.com" />
          </div>
          <div class="field">
            <label>Morada</label>
            <input v-model="form.morada" placeholder="Rua das Flores 10, Lisboa" />
          </div>
          <div class="field field--full">
            <label class="rgpd-check">
              <input type="checkbox" v-model="form.consentimento_rgpd" />
              <span>Cliente autoriza o tratamento dos seus dados pessoais (RGPD) *</span>
            </label>
          </div>
          <p v-if="formError" class="form-error field--full">{{ formError }}</p>
          <div class="modal__actions field--full">
            <button type="button" class="btn btn--secondary" @click="showModal = false">Cancelar</button>
            <button type="submit" class="btn btn--primary" :disabled="formLoading">
              {{ formLoading ? 'A guardar...' : 'Registar Cliente' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.page { padding: 2rem; }

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.sub { font-size: 0.85rem; color: #6b7280; margin-top: 0.25rem; }

.filter-bar { margin-bottom: 1.25rem; }

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
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--secondary { background: #e5e7eb; color: #374151; }
.btn-link { background: none; border: none; color: #1abc9c; cursor: pointer; font-size: 0.85rem; font-weight: 500; padding: 0; }

.overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}

.modal {
  background: #fff;
  border-radius: 10px;
  padding: 2rem;
  width: 100%;
  max-width: 560px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  max-height: 90vh;
  overflow-y: auto;
}

.modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.modal__close {
  background: none; border: none;
  font-size: 1.1rem; color: #6b7280; cursor: pointer;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.field { display: flex; flex-direction: column; }
.field--full { grid-column: 1 / -1; }

.rgpd-check {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
  margin-bottom: 0;
  font-weight: 400;
}
.rgpd-check input { width: auto; flex-shrink: 0; margin-top: 3px; }

.form-error { color: #dc2626; font-size: 0.85rem; }

.modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.25rem;
}
</style>
