<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getOrdemServico,
  getOrdensServico,
  atualizarEstado,
  iniciarTempo,
  pararTempo,
  adicionarPeca,
  removerPeca,
} from '../../services/ordensServico.js'
import { getPecas } from '../../services/pecas.js'
import { useAuthStore } from '../../store/auth.js'
import { useWorkshopStore } from '../../store/workshop.js'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import LoadingSpinner from '../../components/ui/LoadingSpinner.vue'
import OsObservacoes from '../../components/OsObservacoes.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const workshop = useWorkshopStore()

const os = ref(null)
const loading = ref(true)

// State transition
const showEstadoModal = ref(false)
const pendingTransition = ref(null)
const transitionObs = ref('')
const stateLoading = ref(false)
const stateError = ref('')

// Pause
const pauseLoading = ref(false)

// Timer-conflict modal (when starting work while another OS timer is active)
const showConflict = ref(false)
const conflictActiveOS = ref(null)
const conflictSwitching = ref(false)

// Parts
const pecaSearch = ref('')
const pecaResults = ref([])
const pecaSearchLoading = ref(false)
const pecaSelecionada = ref(null)
const pecaQty = ref(1)
const pecaLoading = ref(false)
const pecaError = ref('')
let pecaSearchTimer


// Mechanic-only state machine
const TRANSICOES = {
  PENDENTE: [{ estado: 'EM_DIAGNOSTICO', label: 'Iniciar Diagnóstico' }],
  EM_DIAGNOSTICO: [{ estado: 'EM_REPARACAO', label: 'Iniciar Reparação' }],
  AGUARDA_APROVACAO: [],
  EM_REPARACAO: [
    { estado: 'AGUARDA_PECAS', label: 'Aguardar Peças' },
    { estado: 'CONCLUIDA', label: 'Marcar como Concluída', confirm: true },
  ],
  AGUARDA_PECAS: [{ estado: 'EM_REPARACAO', label: 'Retomar Reparação' }],
  CONCLUIDA: [],
  FATURADA: [],
  CANCELADA: [],
}

// States where the timer runs automatically
const ESTADOS_AUTO_START = ['EM_DIAGNOSTICO', 'EM_REPARACAO']
const ESTADOS_AUTO_STOP  = ['AGUARDA_APROVACAO', 'AGUARDA_PECAS', 'CONCLUIDA', 'CANCELADA']
const ESTADOS_TRABALHO   = ['EM_REPARACAO', 'AGUARDA_PECAS']

const ESTADO_LABELS = {
  PENDENTE: 'Pendente',
  EM_DIAGNOSTICO: 'Em Diagnóstico',
  AGUARDA_APROVACAO: 'Aguarda Aprovação',
  EM_REPARACAO: 'Em Reparação',
  AGUARDA_PECAS: 'Aguarda Peças',
  CONCLUIDA: 'Concluída',
  FATURADA: 'Faturada',
  CANCELADA: 'Cancelada',
}

const availableActions = computed(() => TRANSICOES[os.value?.estado] ?? [])

// The right-column "milestone" button — modal-confirmed, moves the OS to the next major phase
const rightColumnAction = computed(() => {
  if (!os.value) return null
  if (os.value.estado === 'EM_DIAGNOSTICO') return { estado: 'EM_REPARACAO', label: 'Concluir Diagnóstico' }
  if (os.value.estado === 'EM_REPARACAO')   return { estado: 'CONCLUIDA',    label: 'Concluir Reparação' }
  return null
})

// Remaining transitions for the left column — executed directly, no modal
const mainActions = computed(() => {
  const rightTarget = rightColumnAction.value?.estado
  return availableActions.value.filter(a => a.estado !== rightTarget)
})
const timerAtivo = computed(() => !!os.value?.inicio_tempo_atual)
const canAddParts = computed(() => os.value && ESTADOS_TRABALHO.includes(os.value.estado))

// Live elapsed minutes — ticks every 30s while timer is active
const now = ref(Date.now())
let clockInterval = null
const minutosTrabalhadosLive = computed(() => {
  const base = os.value?.tempo_total_minutos ?? 0
  if (!os.value?.inicio_tempo_atual) return base
  const sessao = Math.max(0, Math.floor((now.value - new Date(os.value.inicio_tempo_atual).getTime()) / 60000))
  return base + sessao
})
const canResume = computed(() =>
  os.value &&
  ESTADOS_AUTO_START.includes(os.value.estado) &&
  !timerAtivo.value
)

async function load() {
  loading.value = true
  try {
    const { data } = await getOrdemServico(route.params.id)
    os.value = data.data
  } catch {
    os.value = null
  } finally {
    loading.value = false
  }
}

let pollInterval

onMounted(() => {
  load()
  pollInterval = setInterval(() => { if (!showEstadoModal.value) load() }, 30000)
  clockInterval = setInterval(() => { now.value = Date.now() }, 30000)
})
onUnmounted(() => {
  clearInterval(pollInterval)
  clearInterval(clockInterval)
})

async function findConflictingOS() {
  try {
    const { data } = await getOrdensServico({ page_size: 100 })
    return data.data.find(o => o.tem_timer_ativo && o.id !== os.value.id) ?? null
  } catch { return null }
}

async function doStartTimer() {
  try { await iniciarTempo(os.value.id); workshop.set(true) } catch { /* ignore */ }
}

async function confirmConflict() {
  conflictSwitching.value = true
  try { await pararTempo(conflictActiveOS.value.id); workshop.set(false) } catch { /* ignore */ }
  await doStartTimer()
  conflictSwitching.value = false
  showConflict.value = false
  conflictActiveOS.value = null
  await load()
}

function cancelConflict() {
  showConflict.value = false
  conflictActiveOS.value = null
}

// Timer is fully automatic — starts/stops with state transitions
async function handleAutoTimer(novoEstado) {
  if (ESTADOS_AUTO_START.includes(novoEstado) && !timerAtivo.value) {
    if (workshop.hasActiveOS) {
      const active = await findConflictingOS()
      if (active) { conflictActiveOS.value = active; showConflict.value = true; return }
    }
    await doStartTimer()
  } else if (ESTADOS_AUTO_STOP.includes(novoEstado) && timerAtivo.value) {
    try { await pararTempo(os.value.id) } catch { /* ignore */ }
    workshop.set(false)
  }
}

async function pause() {
  pauseLoading.value = true
  try { await pararTempo(os.value.id) } catch { /* ignore */ }
  workshop.set(false)
  pauseLoading.value = false
  await load()
}

async function resumeWork() {
  if (workshop.hasActiveOS) {
    const active = await findConflictingOS()
    if (active) { conflictActiveOS.value = active; showConflict.value = true; return }
  }
  await doStartTimer()
  await load()
}

// State transitions
async function directTransition(action) {
  stateLoading.value = true
  stateError.value = ''
  try {
    await atualizarEstado(os.value.id, { novo_estado: action.estado, observacao: null })
    await handleAutoTimer(action.estado)
  } catch (e) {
    stateError.value = e.response?.data?.detail?.detail || 'Erro ao atualizar estado.'
  } finally {
    stateLoading.value = false
    await load()
  }
}

function startTransition(action) {
  pendingTransition.value = action
  transitionObs.value = ''
  stateError.value = ''
  showEstadoModal.value = true
}

async function confirmTransition() {
  if (!pendingTransition.value) return
  const targetEstado = pendingTransition.value.estado
  const obs = transitionObs.value || null

  showEstadoModal.value = false
  pendingTransition.value = null
  transitionObs.value = ''
  stateError.value = ''
  stateLoading.value = true

  try {
    await atualizarEstado(os.value.id, { novo_estado: targetEstado, observacao: obs })
    await handleAutoTimer(targetEstado)
  } catch (e) {
    stateError.value = e.response?.data?.detail?.detail || 'Erro ao atualizar estado.'
  }

  stateLoading.value = false
  await load()
}

// Parts search
async function searchPecas() {
  if (!pecaSearch.value.trim()) { pecaResults.value = []; return }
  pecaSearchLoading.value = true
  try {
    const { data } = await getPecas({ query: pecaSearch.value.trim(), page_size: 8 })
    pecaResults.value = data.data
  } catch {
    pecaResults.value = []
  } finally {
    pecaSearchLoading.value = false
  }
}

function watchPecaSearch() {
  clearTimeout(pecaSearchTimer)
  pecaSelecionada.value = null
  pecaSearchTimer = setTimeout(searchPecas, 300)
}

function selectPeca(p) {
  pecaSelecionada.value = p
  pecaSearch.value = p.nome
  pecaResults.value = []
  pecaQty.value = 1
}

async function submitPeca() {
  if (!pecaSelecionada.value) return
  pecaError.value = ''
  pecaLoading.value = true
  try {
    await adicionarPeca(os.value.id, { peca_id: pecaSelecionada.value.id, quantidade: pecaQty.value })
    pecaSearch.value = ''
    pecaSelecionada.value = null
    pecaQty.value = 1
    await load()
  } catch (e) {
    pecaError.value = e.response?.data?.detail?.detail || 'Erro ao adicionar peça.'
  } finally {
    pecaLoading.value = false
  }
}

const removingPecaId = ref(null)

async function removePeca(pecaId) {
  removingPecaId.value = pecaId
  try {
    await removerPeca(os.value.id, pecaId)
    await load()
  } catch (e) {
    pecaError.value = e.response?.data?.detail?.detail || 'Erro ao remover peça.'
  } finally {
    removingPecaId.value = null
  }
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/oficina')
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
        <div class="header-top">
          <h1 class="mono">{{ os.numero }}</h1>
          <StatusBadge :estado="os.estado" />
          <span v-if="os.em_atraso" class="atraso-badge">⚠ +{{ os.minutos_em_atraso }}min em atraso</span>
        </div>
        <p class="sub">
          {{ os.cliente.nome }} · <span class="mono">{{ os.trotinete.numero_serie }}</span> ·
          {{ os.trotinete.marca }} {{ os.trotinete.modelo }}
        </p>
      </div>

      <p v-if="stateError" class="global-error">{{ stateError }}</p>

      <div class="layout">
        <!-- Left column -->
        <div class="left">
          <!-- Problem -->
          <div class="card">
            <div class="card-title">Problema Reportado</div>
            <p class="problem-text">{{ os.descricao_problema }}</p>
            <div class="meta-row">
              <span>Prioridade: <strong :class="`prio-${os.prioridade.toLowerCase()}`">{{ os.prioridade }}</strong></span>
              <span>Entrada: {{ fmt(os.data_entrada) }}</span>
              <span v-if="os.data_conclusao">Conclusão: {{ fmt(os.data_conclusao) }}</span>
              <span class="minutos-label">⏱ {{ minutosTrabalhadosLive }} min trabalhados</span>
            </div>
          </div>

          <!-- State actions -->
          <div class="card" v-if="timerAtivo || canResume || mainActions.length > 0">
            <div class="card-title">Próxima Ação</div>
            <div class="action-list">
              <button
                v-if="timerAtivo"
                class="btn btn--danger btn--action"
                :disabled="pauseLoading"
                @click="pause"
              >
                {{ pauseLoading ? '...' : '⏹ Parar' }}
              </button>
              <button
                v-if="canResume"
                class="btn btn--primary btn--action"
                @click="resumeWork"
              >
                {{ os.estado === 'EM_DIAGNOSTICO' ? '▶ Retomar Avaliação' : '▶ Retomar Reparação' }}
              </button>
              <button
                v-for="action in mainActions"
                :key="action.estado"
                class="btn btn--action"
                :class="canResume || timerAtivo ? 'btn--secondary' : 'btn--primary'"
                @click="directTransition(action)"
              >
                {{ action.label }}
              </button>
            </div>
          </div>

          <!-- Peças aplicadas -->
          <div class="card" v-if="os.estado !== 'EM_DIAGNOSTICO'">
            <div class="card-title">Peças Aplicadas</div>
            <div v-if="os.pecas_aplicadas.length === 0" class="empty-msg">Nenhuma peça associada.</div>
            <table v-else class="table">
              <thead>
                <tr>
                  <th>Peça</th>
                  <th class="col-right">Qtd</th>
                  <th v-if="canAddParts"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in os.pecas_aplicadas" :key="p.peca_id">
                  <td>{{ p.peca_nome }}</td>
                  <td class="col-right">{{ p.quantidade }}</td>
                  <td v-if="canAddParts" class="col-remove">
                    <button
                      class="btn-remove"
                      :disabled="removingPecaId === p.peca_id"
                      @click="removePeca(p.peca_id)"
                      title="Remover peça"
                    >✕</button>
                  </td>
                </tr>
              </tbody>
            </table>

            <!-- Add part -->
            <div v-if="canAddParts" class="add-peca">
              <div class="card-title" style="margin-top: 1rem">Adicionar Peça</div>
              <div class="peca-search-wrap">
                <input
                  v-model="pecaSearch"
                  placeholder="Pesquisar peça por nome ou referência..."
                  @input="watchPecaSearch"
                  autocomplete="off"
                />
                <div v-if="pecaResults.length > 0" class="peca-dropdown">
                  <div
                    v-for="p in pecaResults"
                    :key="p.id"
                    class="peca-option"
                    @mousedown.prevent="selectPeca(p)"
                  >
                    <span class="peca-nome">{{ p.nome }}</span>
                    <span class="peca-ref">{{ p.referencia }}</span>
                  </div>
                </div>
                <LoadingSpinner v-if="pecaSearchLoading" />
              </div>
              <div v-if="pecaSelecionada" class="peca-selected">
                <span>{{ pecaSelecionada.nome }}</span>
                <div class="qty-row">
                  <label>Quantidade</label>
                  <input v-model.number="pecaQty" type="number" min="1" style="width: 80px" />
                  <button class="btn btn--primary btn--sm" :disabled="pecaLoading" @click="submitPeca">
                    {{ pecaLoading ? '...' : 'Adicionar' }}
                  </button>
                </div>
              </div>
              <p v-if="pecaError" class="form-error">{{ pecaError }}</p>
            </div>
          </div>

        </div>

        <!-- Right column -->
        <div class="right">
          <!-- Right-column milestone action -->
          <div class="card card--conclude" v-if="rightColumnAction">
            <button
              class="btn btn--primary btn--action"
              :disabled="rightColumnAction.estado === 'CONCLUIDA' && !timerAtivo"
              @click="startTransition(rightColumnAction)"
            >
              ✓ {{ rightColumnAction.label }}
            </button>
            <p v-if="rightColumnAction.estado === 'CONCLUIDA' && !timerAtivo" class="conclude-hint">
              O timer tem de estar activo para concluir a OS.
            </p>
          </div>

          <OsObservacoes
            :observacoes="os.observacoes"
            :os-id="os.id"
            :can-add="os.estado !== 'CANCELADA'"
            @refresh="load"
          />
        </div>
      </div>
    </template>

    <div v-else class="empty-msg">Ordem de serviço não encontrada.</div>
  </div>

  <!-- State transition modal -->
  <Teleport to="body">
    <div v-if="showEstadoModal" class="overlay" @click.self="showEstadoModal = false">
      <div class="dialog">
        <h2>{{ pendingTransition?.label }}</h2>
        <p class="dialog-sub">
          {{ ESTADO_LABELS[os?.estado] }} → <strong>{{ ESTADO_LABELS[pendingTransition?.estado] }}</strong>
        </p>
        <div class="field" style="margin-top: 1rem">
          <label>Nota (opcional)</label>
          <textarea v-model="transitionObs" rows="3" placeholder="Observação sobre esta alteração..." />
        </div>
        <p v-if="stateError" class="form-error" style="margin-top: 0.5rem">{{ stateError }}</p>
        <div class="dialog-actions">
          <button class="btn btn--secondary" :disabled="stateLoading" @click="showEstadoModal = false">Cancelar</button>
          <button class="btn btn--primary" :disabled="stateLoading" @click="confirmTransition">
            {{ stateLoading ? 'A processar...' : 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Timer-conflict modal -->
  <Teleport to="body">
    <div v-if="showConflict" class="overlay" @click.self="cancelConflict">
      <div class="dialog">
        <p class="dialog-label">Timer activo</p>
        <h2 class="dialog-title">Mudar de ordem de serviço?</h2>
        <div class="dialog-os-info" v-if="conflictActiveOS">
          <span class="os-num">{{ conflictActiveOS.numero }}</span>
          <span class="os-detail">{{ conflictActiveOS.cliente_nome || '—' }}</span>
          <span class="os-detail mono">{{ conflictActiveOS.trotinete_numero_serie || '—' }}</span>
        </div>
        <p class="dialog-body">Atualmente a trabalhar nesta OS. Parar o timer e começar aqui?</p>
        <div class="dialog-actions">
          <button class="btn btn--secondary" :disabled="conflictSwitching" @click="cancelConflict">Não</button>
          <button class="btn btn--danger" :disabled="conflictSwitching" @click="confirmConflict">
            {{ conflictSwitching ? 'A parar...' : 'Sim, mudar' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.page { padding: 2rem; }

.back-row { margin-bottom: 1rem; }
.btn-back { background: none; border: none; color: #1abc9c; font-size: 0.9rem; font-weight: 500; cursor: pointer; padding: 0; }
.btn-back:hover { text-decoration: underline; }

.page-header { margin-bottom: 1.5rem; }
.header-top { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.3rem; }
.sub { font-size: 0.875rem; color: #6b7280; margin: 0; }

.atraso-badge { background: #fef3c7; color: #92400e; font-size: 0.78rem; font-weight: 600; padding: 0.2rem 0.65rem; border-radius: 999px; }

.global-error { color: #dc2626; font-size: 0.875rem; margin-bottom: 1rem; }

.layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 1.5rem;
  align-items: start;
}
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }

.left, .right { display: flex; flex-direction: column; gap: 1.25rem; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 1.5rem; }
.card-title { font-size: 0.78rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem; }

.problem-text { color: #374151; line-height: 1.6; font-size: 0.9rem; margin-bottom: 0.75rem; }
.meta-row { display: flex; gap: 1.5rem; flex-wrap: wrap; font-size: 0.82rem; color: #6b7280; }
.minutos-label { color: #1abc9c; font-weight: 600; }

.action-list { display: flex; flex-direction: column; gap: 0.6rem; }
.btn--action { width: 100%; }

.table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.table th { font-size: 0.75rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.03em; padding: 0.5rem 0; border-bottom: 1px solid #e5e7eb; text-align: left; }
.table td { padding: 0.6rem 0; border-bottom: 1px solid #f3f4f6; }
.table tbody tr:last-child td { border-bottom: none; }
.col-right { text-align: right; }
.col-remove { text-align: right; width: 2rem; }
.btn-remove { background: none; border: none; color: #9ca3af; font-size: 0.85rem; cursor: pointer; padding: 0.2rem 0.4rem; border-radius: 4px; transition: color 0.1s, background 0.1s; }
.btn-remove:hover:not(:disabled) { color: #dc2626; background: #fef2f2; }
.btn-remove:disabled { opacity: 0.4; cursor: not-allowed; }

.add-peca { border-top: 1px solid #f3f4f6; margin-top: 1rem; padding-top: 1rem; }
.peca-search-wrap { position: relative; margin-bottom: 0.5rem; }
.peca-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0; right: 0;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  z-index: 100;
  overflow: hidden;
}
.peca-option { padding: 0.75rem 1rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.peca-option:hover { background: #f0fdf4; }
.peca-nome { font-weight: 500; color: #111827; font-size: 0.875rem; }
.peca-ref { font-size: 0.8rem; color: #6b7280; }
.peca-selected { background: #f0fdf4; border-radius: 6px; padding: 0.75rem; margin-bottom: 0.5rem; font-size: 0.875rem; color: #065f46; }
.qty-row { display: flex; align-items: center; gap: 0.75rem; margin-top: 0.5rem; }
.qty-row label { margin: 0; white-space: nowrap; }

.price-rows { display: flex; flex-direction: column; gap: 0.6rem; }
.price-row { display: flex; justify-content: space-between; font-size: 0.9rem; color: #374151; }
.price-row--total { border-top: 1px solid #e5e7eb; padding-top: 0.6rem; font-weight: 700; color: #111827; }


.empty-msg { color: #6b7280; font-size: 0.875rem; }
.form-error { color: #dc2626; font-size: 0.85rem; }

.prio-baixa { color: #6b7280; }
.prio-normal { color: #374151; }
.prio-alta { color: #d97706; }
.prio-urgente { color: #dc2626; }

.btn { padding: 0.6rem 1.2rem; border: none; border-radius: 6px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: opacity 0.15s; white-space: nowrap; }
.btn:hover { opacity: 0.85; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--secondary { background: #e5e7eb; color: #374151; }
.btn--danger { background: #dc2626; color: #fff; }
.btn--sm { padding: 0.4rem 0.8rem; font-size: 0.825rem; }

.card--conclude { padding: 1rem 1.5rem; }
.conclude-hint { margin-top: 0.6rem; font-size: 0.8rem; color: #9ca3af; text-align: center; }

.mono { font-family: 'Courier New', monospace; }

.overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: #fff; border-radius: 10px; padding: 2rem; width: 100%; max-width: 440px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.dialog-sub { font-size: 0.875rem; color: #6b7280; margin-top: 0.3rem; }
.dialog-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem; }
.field { display: flex; flex-direction: column; }

.dialog-label { font-size: 0.72rem; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.35rem; }
.dialog-title { font-size: 1.1rem; font-weight: 700; color: #111827; margin-bottom: 1rem; }
.dialog-os-info { background: #f9fafb; border-radius: 8px; padding: 0.75rem 1rem; display: flex; flex-direction: column; gap: 0.2rem; margin-bottom: 1rem; }
.os-num { font-family: 'Courier New', monospace; font-size: 0.85rem; font-weight: 700; color: #1abc9c; }
.os-detail { font-size: 0.82rem; color: #6b7280; }
.dialog-body { font-size: 0.9rem; color: #374151; margin-bottom: 1.5rem; line-height: 1.5; }
</style>
