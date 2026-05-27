<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTrotinete, updateTrotinete } from '../../services/trotinetes.js'
import { getOrdensServico } from '../../services/ordensServico.js'
import { useAuthStore } from '../../store/auth.js'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import LoadingSpinner from '../../components/ui/LoadingSpinner.vue'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()
const isGestao = computed(() => ['ADMINISTRADOR', 'GERENTE_LOJA'].includes(auth.getCurrentUser?.perfil))

const trotinete = ref(null)
const historico  = ref([])
const loading    = ref(true)

const editing    = ref(false)
const editForm   = ref({})
const editLoading = ref(false)
const editError   = ref('')

async function load() {
  loading.value = true
  try {
    const [tRes, osRes] = await Promise.all([
      getTrotinete(route.params.id),
      getOrdensServico({ trotinete_id: route.params.id, page_size: 50 }),
    ])
    trotinete.value = tRes.data.data
    historico.value = osRes.data.data ?? []
  } catch {
    trotinete.value = null
  } finally {
    loading.value = false
  }
}

onMounted(load)

function startEdit() {
  editForm.value = {
    marca:                 trotinete.value.marca,
    modelo:                trotinete.value.modelo,
    numero_serie:          trotinete.value.numero_serie,
    ano_compra:            trotinete.value.ano_compra ?? '',
    cor:                   trotinete.value.cor ?? '',
    observacoes_tecnicas:  trotinete.value.observacoes_tecnicas ?? '',
  }
  editError.value = ''
  editing.value = true
}

async function submitEdit() {
  editError.value = ''
  editLoading.value = true
  try {
    const body = {
      marca:                editForm.value.marca,
      modelo:               editForm.value.modelo,
      numero_serie:         editForm.value.numero_serie,
      ano_compra:           editForm.value.ano_compra ? Number(editForm.value.ano_compra) : null,
      cor:                  editForm.value.cor || null,
      observacoes_tecnicas: editForm.value.observacoes_tecnicas || null,
    }
    const res = await updateTrotinete(route.params.id, body)
    trotinete.value = { ...trotinete.value, ...res.data.data }
    editing.value = false
  } catch (e) {
    editError.value = e?.response?.data?.detail?.detail ?? 'Erro ao atualizar trotinete.'
  } finally {
    editLoading.value = false
  }
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('pt-PT') : '—'
}
</script>

<template>
  <div class="page">
    <div class="back-row">
      <button class="btn-back" @click="router.back()">← Voltar</button>
    </div>

    <LoadingSpinner v-if="loading" />

    <template v-else-if="trotinete">
      <div class="page-header">
        <div>
          <h1>{{ trotinete.marca }} {{ trotinete.modelo }}</h1>
          <p class="sub">S/N: {{ trotinete.numero_serie }} · {{ trotinete.total_ordens }} ordem{{ trotinete.total_ordens !== 1 ? 's' : '' }} de serviço</p>
        </div>
        <button
          class="btn btn--primary"
          @click="router.push(`/ordens-servico/nova?trotinete_id=${trotinete.id}`)"
        >
          + Nova OS
        </button>
      </div>

      <!-- Info card -->
      <div class="card info-card">
        <div class="info-card-header">
          <span class="info-card-title">Detalhes</span>
          <button v-if="isGestao && !editing" class="btn btn--ghost btn--sm" @click="startEdit">Editar</button>
        </div>

        <div v-if="!editing" class="info-grid">
          <div class="info-item">
            <span class="info-label">Marca</span>
            <span class="info-value">{{ trotinete.marca }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Modelo</span>
            <span class="info-value">{{ trotinete.modelo }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Nº de Série</span>
            <span class="info-value mono">{{ trotinete.numero_serie }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Ano de Compra</span>
            <span class="info-value">{{ trotinete.ano_compra || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Cor</span>
            <span class="info-value">{{ trotinete.cor || '—' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Cliente</span>
            <span
              class="info-value info-link"
              @click="router.push(`/clientes/${trotinete.cliente.id}`)"
            >{{ trotinete.cliente.nome }}</span>
          </div>
          <div v-if="trotinete.observacoes_tecnicas" class="info-item info-item--full">
            <span class="info-label">Observações Técnicas</span>
            <span class="info-value">{{ trotinete.observacoes_tecnicas }}</span>
          </div>
        </div>

        <form v-else class="edit-form" @submit.prevent="submitEdit">
          <div class="edit-grid">
            <div class="field">
              <label>Marca *</label>
              <input v-model="editForm.marca" required />
            </div>
            <div class="field">
              <label>Modelo *</label>
              <input v-model="editForm.modelo" required />
            </div>
            <div class="field field--full">
              <label>Nº de Série *</label>
              <input v-model="editForm.numero_serie" required />
            </div>
            <div class="field">
              <label>Ano de Compra</label>
              <input v-model="editForm.ano_compra" type="number" min="2000" max="2100" />
            </div>
            <div class="field">
              <label>Cor</label>
              <input v-model="editForm.cor" />
            </div>
            <div class="field field--full">
              <label>Observações Técnicas</label>
              <textarea v-model="editForm.observacoes_tecnicas" rows="2" />
            </div>
          </div>
          <p v-if="editError" class="edit-error">{{ editError }}</p>
          <div class="edit-actions">
            <button type="button" class="btn btn--ghost" @click="editing = false">Cancelar</button>
            <button type="submit" class="btn btn--primary" :disabled="editLoading">
              {{ editLoading ? 'A guardar…' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Histórico de OS -->
      <div class="section">
        <h3>Histórico de Ordens de Serviço</h3>
        <p v-if="historico.length === 0" class="empty-msg">Nenhuma ordem de serviço associada.</p>
        <div v-else class="card">
          <table class="table">
            <thead>
              <tr>
                <th>Número</th>
                <th>Estado</th>
                <th>Prioridade</th>
                <th>Entrada</th>
                <th>Conclusão</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="o in historico"
                :key="o.id"
                class="row-clickable"
                @click="router.push(`/ordens-servico/${o.id}`)"
              >
                <td class="mono">{{ o.numero }}</td>
                <td><StatusBadge :estado="o.estado" /></td>
                <td>{{ o.prioridade }}</td>
                <td>{{ fmt(o.data_entrada) }}</td>
                <td>{{ fmt(o.data_conclusao) }}</td>
                <td><span class="link-arrow">→</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <div v-else class="empty-msg">Trotinete não encontrada.</div>
  </div>
</template>

<style scoped>
.page { padding: 2rem; }
.back-row { margin-bottom: 1rem; }
.btn-back { background: none; border: none; color: #1abc9c; font-size: 0.9rem; font-weight: 500; cursor: pointer; padding: 0; }
.btn-back:hover { text-decoration: underline; }

.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 1.5rem; gap: 1rem; }
.sub { font-size: 0.85rem; color: #6b7280; margin-top: 0.25rem; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); overflow: hidden; margin-bottom: 1.5rem; }
.info-card { padding: 1.5rem; }
.info-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; }
.info-card-title { font-size: 0.75rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }
.info-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1.25rem; }
.info-item { display: flex; flex-direction: column; gap: 0.2rem; }
.info-item--full { grid-column: 1 / -1; }
.info-label { font-size: 0.78rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.04em; }
.info-value { font-size: 0.95rem; color: #111827; font-weight: 500; }
.info-link { color: #1abc9c; cursor: pointer; }
.info-link:hover { text-decoration: underline; }

.edit-form { display: flex; flex-direction: column; gap: 1rem; }
.edit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; }
.field { display: flex; flex-direction: column; gap: 0.3rem; }
.field--full { grid-column: 1 / -1; }
.field label { font-size: 0.78rem; font-weight: 600; color: #374151; text-transform: uppercase; letter-spacing: 0.04em; }
.field input, .field textarea { padding: 0.55rem 0.75rem; border: 1px solid #d1d5db; border-radius: 8px; font-size: 0.9rem; color: #111827; outline: none; resize: vertical; }
.field input:focus, .field textarea:focus { border-color: #1abc9c; box-shadow: 0 0 0 3px rgba(26,188,156,0.15); }
.edit-error { color: #dc2626; font-size: 0.85rem; }
.edit-actions { display: flex; justify-content: flex-end; gap: 0.75rem; }

.section { margin-bottom: 2rem; }
.section h3 { margin-bottom: 0.75rem; }

.table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.table th { background: #f9fafb; padding: 0.65rem 1rem; text-align: left; font-size: 0.78rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.03em; border-bottom: 1px solid #e5e7eb; }
.table td { padding: 0.8rem 1rem; border-bottom: 1px solid #f3f4f6; color: #374151; vertical-align: middle; }
.table tbody tr:last-child td { border-bottom: none; }

.row-clickable { cursor: pointer; }
.row-clickable:hover { background: #f9fafb; }

.mono { font-family: 'Courier New', monospace; font-size: 0.85rem; }
.link-arrow { color: #1abc9c; font-weight: 600; }
.empty-msg { color: #6b7280; font-size: 0.9rem; padding: 0.5rem 0; }

.btn { padding: 0.6rem 1.2rem; border: none; border-radius: 6px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: opacity 0.15s; white-space: nowrap; }
.btn:hover { opacity: 0.85; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary   { background: #1abc9c; color: #fff; }
.btn--ghost     { background: transparent; border: 1px solid #d1d5db; color: #374151; }
.btn--sm { padding: 0.4rem 0.8rem; font-size: 0.825rem; }
</style>
