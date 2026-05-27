<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getOrdemServico, atualizarEstado, deletarOS, getHistoricoOS } from '../../services/ordensServico.js'
import { getCliente } from '../../services/clientes.js'
import { useAuthStore } from '../../store/auth.js'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import LoadingSpinner from '../../components/ui/LoadingSpinner.vue'
import FaturaPreviewModal from '../../components/FaturaPreviewModal.vue'
import FaturaEmitirModal from '../../components/FaturaEmitirModal.vue'
import OsObservacoes from '../../components/OsObservacoes.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const os = ref(null)
const loading = ref(true)
const actionLoading = ref(false)
const actionError = ref('')

const showEstadoModal = ref(false)
const pendingTransition = ref(null)
const transitionObs = ref('')

const showFaturaModal = ref(false)
const faturaModalId = ref(null)

const showEmitirModal = ref(false)

const nivelFidelizacao = ref(0)
const descontoSugerido = ref(0)

const historico = ref([])
const historicoLoading = ref(false)

const perfil = computed(() => auth.getCurrentUser?.perfil)

// Valid transitions per (estado, perfil) — matches backend _TRANSICOES
const TRANSICOES = {
  PENDENTE: {
    ADMINISTRADOR: [
      { estado: 'EM_DIAGNOSTICO', label: 'Iniciar Diagnóstico', danger: false },
      { estado: 'CANCELADA', label: 'Cancelar OS', danger: true },
    ],
    GERENTE_LOJA: [
      { estado: 'EM_DIAGNOSTICO', label: 'Iniciar Diagnóstico', danger: false },
      { estado: 'CANCELADA', label: 'Cancelar OS', danger: true },
    ],
    RECECIONISTA: [],
    MECANICO: [{ estado: 'EM_DIAGNOSTICO', label: 'Iniciar Diagnóstico', danger: false }],
  },
  EM_DIAGNOSTICO: {
    ADMINISTRADOR: [
      { estado: 'EM_REPARACAO', label: 'Concluir Diagnóstico', danger: false },
      { estado: 'CANCELADA', label: 'Cancelar OS', danger: true },
    ],
    GERENTE_LOJA: [
      { estado: 'EM_REPARACAO', label: 'Concluir Diagnóstico', danger: false },
      { estado: 'CANCELADA', label: 'Cancelar OS', danger: true },
    ],
    RECECIONISTA: [],
    MECANICO: [
      { estado: 'EM_REPARACAO', label: 'Concluir Diagnóstico', danger: false },
    ],
  },
  EM_REPARACAO: {
    ADMINISTRADOR: [
      { estado: 'CONCLUIDA', label: 'Marcar como Concluída', danger: false },
      { estado: 'CANCELADA', label: 'Cancelar OS', danger: true },
    ],
    GERENTE_LOJA: [
      { estado: 'CONCLUIDA', label: 'Marcar como Concluída', danger: false },
      { estado: 'CANCELADA', label: 'Cancelar OS', danger: true },
    ],
    RECECIONISTA: [],
    MECANICO: [
      { estado: 'CONCLUIDA', label: 'Marcar como Concluída', danger: false },
    ],
  },
  AGUARDA_PECAS: {
    ADMINISTRADOR: [
      { estado: 'EM_REPARACAO', label: 'Retomar Reparação', danger: false },
      { estado: 'CANCELADA', label: 'Cancelar OS', danger: true },
    ],
    GERENTE_LOJA: [
      { estado: 'EM_REPARACAO', label: 'Retomar Reparação', danger: false },
      { estado: 'CANCELADA', label: 'Cancelar OS', danger: true },
    ],
    RECECIONISTA: [],
    MECANICO: [{ estado: 'EM_REPARACAO', label: 'Retomar Reparação', danger: false }],
  },
  CONCLUIDA: { ADMINISTRADOR: [], GERENTE_LOJA: [], RECECIONISTA: [], MECANICO: [] },
  FATURADA: { ADMINISTRADOR: [], GERENTE_LOJA: [], RECECIONISTA: [], MECANICO: [] },
  CANCELADA: { ADMINISTRADOR: [], GERENTE_LOJA: [], RECECIONISTA: [], MECANICO: [] },
}

const availableActions = computed(() => {
  if (!os.value || !perfil.value) return []
  return TRANSICOES[os.value.estado]?.[perfil.value] ?? []
})

const canAddObservacao = computed(() =>
  ['ADMINISTRADOR', 'GERENTE_LOJA', 'MECANICO'].includes(perfil.value) &&
  os.value?.estado !== 'CANCELADA'
)

const canEmitirFatura = computed(() =>
  ['ADMINISTRADOR', 'GERENTE_LOJA', 'RECECIONISTA'].includes(perfil.value) &&
  os.value?.estado === 'CONCLUIDA' &&
  !os.value?.fatura_id
)

const canDeleteOS = computed(() => perfil.value === 'ADMINISTRADOR')

const initialized = ref(false)
async function loadOS() {
  if (!initialized.value) loading.value = true
  try {
    const { data } = await getOrdemServico(route.params.id)
    os.value = data.data
  } catch {
    if (!initialized.value) os.value = null
  } finally {
    loading.value = false
    initialized.value = true
  }
}

async function loadHistorico() {
  if (!os.value) return
  historicoLoading.value = true
  try {
    const { data } = await getHistoricoOS(os.value.id)
    historico.value = data.data ?? []
  } catch {
    historico.value = []
  } finally {
    historicoLoading.value = false
  }
}

let pollInterval
onMounted(async () => {
  await loadOS()
  loadHistorico()
  pollInterval = setInterval(() => { if (!showEstadoModal.value) loadOS() }, 30000)
})
onUnmounted(() => clearInterval(pollInterval))

function startTransition(action) {
  pendingTransition.value = action
  transitionObs.value = ''
  actionError.value = ''
  showEstadoModal.value = true
}

async function confirmTransition() {
  if (!pendingTransition.value) return
  const targetEstado = pendingTransition.value.estado
  const obs = transitionObs.value || null

  showEstadoModal.value = false
  pendingTransition.value = null
  transitionObs.value = ''
  actionError.value = ''
  actionLoading.value = true

  try {
    await atualizarEstado(os.value.id, { novo_estado: targetEstado, observacao: obs })
  } catch (e) {
    actionError.value = e.response?.data?.detail?.detail || 'Erro ao atualizar estado.'
  } finally {
    actionLoading.value = false
    await loadOS()
    loadHistorico()
  }
}

async function deleteOS() {
  if (!confirm('Eliminar definitivamente esta OS? Esta ação não pode ser desfeita.')) return
  try {
    await deletarOS(os.value.id)
    router.push('/ordens-servico')
  } catch (e) {
    actionError.value = e.response?.data?.detail?.detail || 'Erro ao eliminar.'
  }
}

async function openEmitirModal() {
  actionError.value = ''
  nivelFidelizacao.value = 0
  descontoSugerido.value = 0
  try {
    const { data } = await getCliente(os.value.cliente_id)
    nivelFidelizacao.value = data.data.nivel_fidelizacao ?? 0
    descontoSugerido.value = data.data.desconto_sugerido_pct ?? 0
  } catch { /* open modal anyway without pre-fill */ }
  showEmitirModal.value = true
}

async function onFaturaEmitida(faturaId) {
  await loadOS()
  faturaModalId.value = faturaId
}

function openFaturaModal() {
  faturaModalId.value = os.value.fatura_id
  showFaturaModal.value = true
}

const ESTADO_LABELS = {
  PENDENTE: 'Pendente',
  EM_DIAGNOSTICO: 'Em Diagnóstico',
  EM_REPARACAO: 'Em Reparação',
  AGUARDA_PECAS: 'Aguarda Peças',
  CONCLUIDA: 'Concluída',
  FATURADA: 'Faturada',
  CANCELADA: 'Cancelada',
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/ordens-servico')
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('pt-PT') : '—'
}

function fmtDateTime(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('pt-PT', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="page">
    <div class="back-row">
      <button class="btn-back" @click="goBack">← Voltar</button>
    </div>

    <LoadingSpinner v-if="loading" />

    <template v-else-if="os">
      <!-- Header -->
      <div class="page-header">
        <div>
          <div class="header-top">
            <h1 class="mono">{{ os.numero }}</h1>
            <StatusBadge :estado="os.estado" />
            <span v-if="os.em_atraso" class="atraso-badge">⚠ +{{ os.minutos_em_atraso }}min em atraso</span>
          </div>
          <p class="sub">Entrada: {{ fmt(os.data_entrada) }} · Loja: {{ os.loja_nome || `#${os.loja_id}` }}</p>
        </div>
      </div>

      <div class="layout">
        <!-- Left column -->
        <div class="left">
          <!-- Pessoas -->
          <div class="card">
            <h3 class="card-title">Informação</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Cliente</span>
                <span class="info-value">{{ os.cliente.nome }}</span>
                <span class="info-sub">{{ os.cliente.telemovel }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Trotinete</span>
                <span class="info-value">{{ os.trotinete.marca }} {{ os.trotinete.modelo }}</span>
                <span class="info-sub mono">{{ os.trotinete.numero_serie }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Mecânico</span>
                <span class="info-value">{{ os.mecanico?.nome || 'Não atribuído' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Prioridade</span>
                <span class="info-value" :class="`prio-${os.prioridade.toLowerCase()}`">{{ os.prioridade }}</span>
              </div>
              <div v-if="os.data_conclusao" class="info-item">
                <span class="info-label">Conclusão</span>
                <span class="info-value">{{ fmt(os.data_conclusao) }}</span>
              </div>
              <div v-if="os.tempo_total_minutos != null" class="info-item">
                <span class="info-label">Tempo de trabalho</span>
                <span class="info-value">{{ os.tempo_total_minutos }} min</span>
              </div>
            </div>
          </div>

          <!-- Problema -->
          <div class="card">
            <h3 class="card-title">Descrição do Problema</h3>
            <p class="problem-text">{{ os.descricao_problema }}</p>
          </div>

          <!-- Preços -->
          <div class="card">
            <h3 class="card-title">Estimativa de Custo</h3>
            <div class="price-rows">
              <div class="price-row">
                <span>Serviço</span>
                <span>{{ os.preco_servico.toFixed(2) }} €</span>
              </div>
              <div class="price-row">
                <span>Peças</span>
                <span>{{ os.subtotal_pecas.toFixed(2) }} €</span>
              </div>
              <div class="price-row price-row--total">
                <span>Total estimado</span>
                <span>{{ os.valor_estimado_total.toFixed(2) }} €</span>
              </div>
            </div>
          </div>

          <!-- Peças -->
          <div class="card" v-if="os.pecas_aplicadas.length > 0">
            <h3 class="card-title">Peças Aplicadas</h3>
            <table class="table">
              <thead>
                <tr>
                  <th>Peça</th>
                  <th class="right">Qtd</th>
                  <th class="right">P. Unit.</th>
                  <th class="right">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in os.pecas_aplicadas" :key="p.peca_id">
                  <td>{{ p.peca_nome }}</td>
                  <td class="right">{{ p.quantidade }}</td>
                  <td class="right">{{ p.preco_venda_unitario.toFixed(2) }} €</td>
                  <td class="right">{{ p.subtotal.toFixed(2) }} €</td>
                </tr>
              </tbody>
            </table>
          </div>
          <!-- Histórico -->
          <div class="card">
            <h3 class="card-title">Histórico</h3>
            <div v-if="historicoLoading" class="dim">A carregar…</div>
            <div v-else-if="historico.length === 0" class="dim">Sem eventos registados.</div>
            <div v-else class="history-list">
              <div v-for="item in historico" :key="item.id" class="history-item">
                <div class="history-meta">
                  <span class="history-time">{{ fmtDateTime(item.timestamp) }}</span>
                  <span v-if="item.utilizador_nome" class="history-user">{{ item.utilizador_nome }}</span>
                </div>
                <span class="history-desc">{{ item.descricao }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right column -->
        <div class="right">
          <!-- Actions -->
          <div class="card" v-if="availableActions.length > 0 || canEmitirFatura">
            <h3 class="card-title">Ações</h3>
            <div class="action-buttons">
              <button
                v-for="action in availableActions"
                :key="action.estado"
                class="btn btn--action"
                :class="action.danger ? 'btn--danger' : 'btn--primary'"
                @click="startTransition(action)"
              >
                {{ action.label }}
              </button>
              <button
                v-if="canEmitirFatura"
                class="btn btn--action btn--primary"
                :disabled="actionLoading"
                @click="openEmitirModal"
              >
                Emitir Fatura
              </button>
            </div>
            <p v-if="actionError" class="form-error" style="margin-top:0.75rem">{{ actionError }}</p>
          </div>

          <!-- Fatura emitida -->
          <div class="card" v-if="os.fatura_id">
            <h3 class="card-title">Fatura</h3>
            <button class="btn btn--ghost" @click="openFaturaModal">
              Ver Fatura →
            </button>
          </div>

          <!-- Eliminar (admin only) -->
          <div class="card" v-if="canDeleteOS">
            <h3 class="card-title">Zona de Perigo</h3>
            <button class="btn btn--danger" style="width:100%" @click="deleteOS">Eliminar OS</button>
          </div>

          <!-- Observações -->
          <OsObservacoes
            :observacoes="os.observacoes"
            :os-id="os.id"
            :can-add="canAddObservacao"
            @refresh="loadOS"
          />
        </div>
      </div>
    </template>

    <div v-else class="empty-msg">Ordem de serviço não encontrada.</div>
  </div>

  <!-- Ver fatura already emitted -->
  <FaturaPreviewModal
    v-if="showFaturaModal && faturaModalId && !showEmitirModal"
    :fatura-id="faturaModalId"
    @close="showFaturaModal = false"
  />

  <!-- Emitir fatura (draft preview + emission) -->
  <FaturaEmitirModal
    v-if="showEmitirModal && os"
    :os="os"
    :nivel-fidelizacao="nivelFidelizacao"
    :desconto-sugerido="descontoSugerido"
    @close="showEmitirModal = false"
    @emitida="onFaturaEmitida"
  />

  <!-- Estado transition modal -->
  <Teleport to="body">
    <div v-if="showEstadoModal" class="overlay" @click.self="showEstadoModal = false">
      <div class="dialog">
        <h2 class="dialog-title">{{ pendingTransition?.label }}</h2>
        <p class="dialog-sub">
          {{ ESTADO_LABELS[os?.estado] }} → <strong>{{ ESTADO_LABELS[pendingTransition?.estado] }}</strong>
        </p>
        <div class="field" style="margin-top: 1rem">
          <label>Observação (opcional)</label>
          <textarea v-model="transitionObs" rows="3" placeholder="Nota sobre esta alteração..." />
        </div>
        <p v-if="actionError" class="form-error" style="margin-top:0.5rem">{{ actionError }}</p>
        <div class="dialog-actions">
          <button class="btn btn--secondary" @click="showEstadoModal = false">Cancelar</button>
          <button
            class="btn"
            :class="pendingTransition?.danger ? 'btn--danger' : 'btn--primary'"
            :disabled="actionLoading"
            @click="confirmTransition"
          >
            {{ actionLoading ? 'A processar...' : 'Confirmar' }}
          </button>
        </div>
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

.page-header { margin-bottom: 1.5rem; }
.header-top { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.sub { font-size: 0.85rem; color: #6b7280; margin-top: 0.3rem; }

.atraso-badge {
  background: #fef3c7; color: #92400e;
  font-size: 0.78rem; font-weight: 600;
  padding: 0.2rem 0.65rem; border-radius: 999px;
}

.layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 1.5rem;
  align-items: start;
}
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
}

.left, .right { display: flex; flex-direction: column; gap: 1.25rem; }

.card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  padding: 1.5rem;
}
.card-title { font-size: 0.875rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; }

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.info-item { display: flex; flex-direction: column; gap: 0.15rem; }
.info-label { font-size: 0.75rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.04em; }
.info-value { font-size: 0.9rem; font-weight: 600; color: #111827; }
.info-sub { font-size: 0.8rem; color: #6b7280; }

.prio-baixa { color: #6b7280; }
.prio-normal { color: #374151; }
.prio-alta { color: #d97706; }
.prio-urgente { color: #dc2626; }

.problem-text { color: #374151; line-height: 1.6; font-size: 0.9rem; }

.price-rows { display: flex; flex-direction: column; gap: 0.6rem; }
.price-row { display: flex; justify-content: space-between; font-size: 0.9rem; color: #374151; }
.price-row--total {
  border-top: 1px solid #e5e7eb;
  padding-top: 0.6rem;
  font-weight: 700;
  color: #111827;
  font-size: 1rem;
}

.table {
  width: 100%; border-collapse: collapse; font-size: 0.875rem;
}
.table th {
  font-size: 0.75rem; font-weight: 600; color: #6b7280;
  text-transform: uppercase; letter-spacing: 0.03em;
  padding: 0.5rem 0; border-bottom: 1px solid #e5e7eb;
  text-align: left;
}
.table td { padding: 0.6rem 0; border-bottom: 1px solid #f3f4f6; color: #374151; }
.table tbody tr:last-child td { border-bottom: none; }
.right { text-align: right; }

/* Actions */
.action-buttons { display: flex; flex-direction: column; gap: 0.6rem; }
.btn--action { width: 100%; justify-content: center; }

.empty-msg { color: #6b7280; font-size: 0.9rem; }
.form-error { color: #dc2626; font-size: 0.85rem; }

/* Buttons */
.btn {
  padding: 0.6rem 1.2rem;
  border: none; border-radius: 6px;
  font-size: 0.9rem; font-weight: 600;
  cursor: pointer; transition: opacity 0.15s;
  white-space: nowrap;
}
.btn:hover { opacity: 0.85; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--danger { background: #dc2626; color: #fff; }
.btn--secondary { background: #e5e7eb; color: #374151; }
.btn--ghost { background: transparent; border: 1px solid #d1d5db; color: #374151; }
.btn--sm { padding: 0.4rem 0.8rem; font-size: 0.825rem; }

/* History */
.history-list { display: flex; flex-direction: column; gap: 0; }
.history-item {
  padding: 0.6rem 0;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.history-item:last-child { border-bottom: none; }
.history-meta { display: flex; justify-content: space-between; align-items: center; }
.history-time { font-size: 0.75rem; color: #9ca3af; }
.history-user { font-size: 0.75rem; color: #6b7280; font-weight: 500; }
.history-desc { font-size: 0.85rem; color: #374151; }
.dim { color: #9ca3af; font-size: 0.85rem; }

.mono { font-family: 'Courier New', monospace; }

/* Dialog */
.overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.dialog {
  background: #fff;
  border-radius: 10px;
  padding: 2rem;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}
.dialog-title { margin-bottom: 0.4rem; }
.dialog-sub { font-size: 0.875rem; color: #6b7280; }
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}
</style>
