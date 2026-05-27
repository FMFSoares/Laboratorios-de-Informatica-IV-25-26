<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCliente, getClienteHistorico, updateCliente } from '../../services/clientes.js'
import { createTrotinete } from '../../services/trotinetes.js'
import { getLojas } from '../../services/lojas.js'
import { useAuthStore } from '../../store/auth.js'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import LoadingSpinner from '../../components/ui/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const isGestao = computed(() => ['ADMINISTRADOR', 'GERENTE_LOJA'].includes(auth.getCurrentUser?.perfil))

const cliente = ref(null)
const historico = ref([])
const lojas = ref([])
const loading = ref(true)
const histLoading = ref(true)

const showTrotModal = ref(false)
const trotForm = ref({ marca: '', modelo: '', numero_serie: '', ano_compra: '', cor: '', observacoes_tecnicas: '' })
const trotError = ref('')
const trotLoading = ref(false)

async function fetchAll() {
  const id = route.params.id
  loading.value = true
  histLoading.value = true
  try {
    const [c, h, l] = await Promise.all([
      getCliente(id),
      getClienteHistorico(id),
      getLojas({ page_size: 50 }),
    ])
    cliente.value = c.data.data
    historico.value = h.data.data
    lojas.value = l.data.data ?? []
  } catch {
    cliente.value = null
  } finally {
    loading.value = false
    histLoading.value = false
  }
}

onMounted(fetchAll)

// ── Edit ─────────────────────────────────────────────────────────────────────
const editing     = ref(false)
const editForm    = ref({})
const editLoading = ref(false)
const editError   = ref('')

function startEdit() {
  editForm.value = {
    nome:      cliente.value.nome,
    telemovel: cliente.value.telemovel,
    email:     cliente.value.email ?? '',
    morada:    cliente.value.morada ?? '',
  }
  editError.value = ''
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  editError.value = ''
}

async function submitEdit() {
  editError.value = ''
  editLoading.value = true
  try {
    const body = {
      nome:      editForm.value.nome,
      telemovel: editForm.value.telemovel,
      email:     editForm.value.email  || null,
      morada:    editForm.value.morada || null,
    }
    const res = await updateCliente(route.params.id, body)
    cliente.value = { ...cliente.value, ...res.data.data }
    editing.value = false
  } catch (e) {
    editError.value = e?.response?.data?.detail?.detail ?? 'Erro ao atualizar cliente.'
  } finally {
    editLoading.value = false
  }
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('pt-PT') : '—'
}

function openTrotModal() {
  trotForm.value = { marca: '', modelo: '', numero_serie: '', ano_compra: '', cor: '', observacoes_tecnicas: '' }
  trotError.value = ''
  showTrotModal.value = true
}

async function submitTrot() {
  trotError.value = ''
  trotLoading.value = true
  try {
    const body = {
      cliente_id: cliente.value.id,
      marca: trotForm.value.marca,
      modelo: trotForm.value.modelo,
      numero_serie: trotForm.value.numero_serie,
    }
    if (trotForm.value.ano_compra) body.ano_compra = parseInt(trotForm.value.ano_compra)
    if (trotForm.value.cor) body.cor = trotForm.value.cor
    if (trotForm.value.observacoes_tecnicas) body.observacoes_tecnicas = trotForm.value.observacoes_tecnicas
    await createTrotinete(body)
    showTrotModal.value = false
    fetchAll()
  } catch (e) {
    trotError.value = e.response?.data?.detail?.detail || 'Erro ao registar trotinete.'
  } finally {
    trotLoading.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="back-row">
      <button class="btn-back" @click="router.push('/clientes')">← Clientes</button>
    </div>

    <LoadingSpinner v-if="loading" />

    <template v-else-if="cliente">
      <div class="page-header">
        <div>
          <h1>{{ cliente.nome }}</h1>
          <p class="sub">NIF {{ cliente.nif }} · Registado em {{ fmt(cliente.data_registo) }}</p>
        </div>
        <button
          class="btn btn--primary"
          @click="router.push(`/ordens-servico/nova?cliente_id=${cliente.id}`)"
        >
          + Nova OS
        </button>
      </div>

      <!-- Info card -->
      <div class="card info-card">
        <div class="info-card-header">
          <span class="info-card-title">Informações</span>
          <button v-if="isGestao && !editing" class="btn btn--ghost btn--sm" @click="startEdit">Editar</button>
        </div>

        <!-- Read mode -->
        <div v-if="!editing" class="info-grid">
          <div class="info-item">
            <span class="info-label">Nome</span>
            <span class="info-value">{{ cliente.nome }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">NIF</span>
            <span class="info-value">{{ cliente.nif }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Telemóvel</span>
            <span class="info-value">{{ cliente.telemovel }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Email</span>
            <span class="info-value">{{ cliente.email || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Morada</span>
            <span class="info-value">{{ cliente.morada || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">RGPD</span>
            <span class="info-value">{{ cliente.consentimento_rgpd ? 'Autorizado' : 'Não autorizado' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Loja</span>
            <span class="info-value">{{ lojas.find(l => l.id === cliente.loja_id)?.nome || `#${cliente.loja_id}` }}</span>
          </div>
        </div>

        <!-- Edit mode -->
        <form v-else class="edit-form" @submit.prevent="submitEdit">
          <div class="edit-grid">
            <div class="field">
              <label>Nome *</label>
              <input v-model="editForm.nome" required placeholder="Nome completo" />
            </div>
            <div class="field">
              <label>Telemóvel *</label>
              <input v-model="editForm.telemovel" required placeholder="9XXXXXXXX" />
            </div>
            <div class="field">
              <label>Email</label>
              <input v-model="editForm.email" type="email" placeholder="email@exemplo.com" />
            </div>
            <div class="field field--full">
              <label>Morada</label>
              <input v-model="editForm.morada" placeholder="Rua, número, cidade" />
            </div>
          </div>
          <p v-if="editError" class="edit-error">{{ editError }}</p>
          <div class="edit-actions">
            <button type="button" class="btn btn--ghost" @click="cancelEdit">Cancelar</button>
            <button type="submit" class="btn btn--primary" :disabled="editLoading">
              {{ editLoading ? 'A guardar…' : 'Guardar Alterações' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Trotinetes -->
      <div class="section">
        <div class="section-header">
          <h3>Trotinetes</h3>
          <button class="btn btn--secondary btn--sm" @click="openTrotModal">+ Registar Trotinete</button>
        </div>
        <div v-if="cliente.trotinetes.length === 0" class="empty-msg">Nenhuma trotinete registada.</div>
        <div v-else class="card">
          <table class="table">
            <thead>
              <tr>
                <th>Marca</th>
                <th>Modelo</th>
                <th>Nº de Série</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in cliente.trotinetes" :key="t.id" class="row-clickable" @click="router.push(`/trotinetes/${t.id}`)">
                <td>{{ t.marca }}</td>
                <td>{{ t.modelo }}</td>
                <td class="mono">{{ t.numero_serie }}</td>
                <td><span class="link-arrow">→</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Histórico de OS -->
      <div class="section">
        <h3>Histórico de Ordens de Serviço</h3>
        <div v-if="histLoading" class="empty-msg">A carregar...</div>
        <div v-else-if="historico.length === 0" class="empty-msg">Nenhuma ordem de serviço registada.</div>
        <div v-else class="card">
          <table class="table">
            <thead>
              <tr>
                <th>Trotinete</th>
                <th>Descrição</th>
                <th>Estado</th>
                <th>Entrada</th>
                <th>Conclusão</th>
                <th>Valor</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in historico"
                :key="item.id"
                class="row-clickable"
                @click="router.push(`/ordens-servico/${item.id}`)"
              >
                <td class="mono">{{ item.trotinete_numero_serie }}</td>
                <td class="truncate">{{ item.descricao }}</td>
                <td><StatusBadge :estado="item.estado" /></td>
                <td>{{ fmt(item.data_entrada) }}</td>
                <td>{{ fmt(item.data_conclusao) }}</td>
                <td>{{ item.valor_final != null ? `${item.valor_final.toFixed(2)} €` : '—' }}</td>
                <td><span class="link-arrow">→</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <div v-else class="empty-msg">Cliente não encontrado.</div>
  </div>

  <!-- Modal registar trotinete -->
  <Teleport to="body">
    <div v-if="showTrotModal" class="overlay" @click.self="showTrotModal = false">
      <div class="modal">
        <div class="modal__header">
          <h2>Registar Trotinete</h2>
          <button class="modal__close" @click="showTrotModal = false">✕</button>
        </div>
        <form @submit.prevent="submitTrot" class="form-grid">
          <div class="field">
            <label>Marca *</label>
            <input v-model="trotForm.marca" required placeholder="Xiaomi" />
          </div>
          <div class="field">
            <label>Modelo *</label>
            <input v-model="trotForm.modelo" required placeholder="Mi Electric Scooter 3" />
          </div>
          <div class="field field--full">
            <label>Número de Série *</label>
            <input v-model="trotForm.numero_serie" required placeholder="XM2024ABC123" />
          </div>
          <div class="field">
            <label>Ano de Compra</label>
            <input v-model="trotForm.ano_compra" type="number" placeholder="2024" min="2000" max="2100" />
          </div>
          <div class="field">
            <label>Cor</label>
            <input v-model="trotForm.cor" placeholder="Preto" />
          </div>
          <div class="field field--full">
            <label>Observações Técnicas</label>
            <textarea v-model="trotForm.observacoes_tecnicas" rows="2" placeholder="Notas relevantes..." />
          </div>
          <p v-if="trotError" class="form-error field--full">{{ trotError }}</p>
          <div class="modal__actions field--full">
            <button type="button" class="btn btn--secondary" @click="showTrotModal = false">Cancelar</button>
            <button type="submit" class="btn btn--primary" :disabled="trotLoading">
              {{ trotLoading ? 'A guardar...' : 'Registar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.page { padding: 2rem; }

.back-row { margin-bottom: 1rem; }
.btn-back {
  background: none; border: none;
  color: #1abc9c; font-size: 0.9rem; font-weight: 500;
  cursor: pointer; padding: 0;
}
.btn-back:hover { text-decoration: underline; }

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.sub { font-size: 0.85rem; color: #6b7280; margin-top: 0.25rem; }

.card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.info-card { padding: 1.5rem; margin-bottom: 1.5rem; }

.info-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}
.info-card-title { font-size: 0.75rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.25rem;
}

.info-item { display: flex; flex-direction: column; gap: 0.2rem; }
.info-label { font-size: 0.78rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.04em; }
.info-value { font-size: 0.95rem; color: #111827; font-weight: 500; }

.edit-form { display: flex; flex-direction: column; gap: 1rem; }
.edit-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
}
.field { display: flex; flex-direction: column; gap: 0.3rem; }
.field--full { grid-column: 1 / -1; }
.field label { font-size: 0.78rem; font-weight: 600; color: #374151; text-transform: uppercase; letter-spacing: 0.04em; }
.field input {
  padding: 0.55rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #111827;
  outline: none;
}
.field input:focus { border-color: #1abc9c; box-shadow: 0 0 0 3px rgba(26,188,156,0.15); }
.edit-error { color: #dc2626; font-size: 0.85rem; margin: 0; }
.edit-actions { display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 0.25rem; }

.section { margin-bottom: 2rem; }

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
.table th {
  background: #f9fafb;
  padding: 0.65rem 1rem;
  text-align: left;
  font-size: 0.78rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  border-bottom: 1px solid #e5e7eb;
}
.table td {
  padding: 0.8rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  color: #374151;
  vertical-align: middle;
}
.table tbody tr:last-child td { border-bottom: none; }

.row-clickable { cursor: pointer; }
.row-clickable:hover { background: #f9fafb; }

.mono { font-family: 'Courier New', monospace; font-size: 0.85rem; }
.truncate { max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.link-arrow { color: #1abc9c; font-weight: 600; }

.empty-msg { color: #6b7280; font-size: 0.9rem; padding: 0.5rem 0; }

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
.btn--primary   { background: #1abc9c; color: #fff; }
.btn--secondary { background: #e5e7eb; color: #374151; }
.btn--ghost     { background: transparent; border: 1px solid #d1d5db; color: #374151; }
.btn--sm { padding: 0.4rem 0.8rem; font-size: 0.825rem; }

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
  max-width: 520px;
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
.form-error { color: #dc2626; font-size: 0.85rem; }
.modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.25rem;
}
</style>
