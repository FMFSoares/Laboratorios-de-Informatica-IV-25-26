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
  submeterDiagnostico,
} from '../../services/ordensServico.js'
import { getServicos } from '../../services/servicos.js'
import { getPecas } from '../../services/pecas.js'
import { criarPedidoPeca } from '../../services/pedidosPeca.js'
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

// Diagnostic modal
const showDiagModal = ref(false)
const diagCatalog   = ref([])
const diagSlots     = ref([{ servico_id: null }])
const diagLoading   = ref(false)
const diagError     = ref('')

async function openDiagModal() {
  diagSlots.value = [{ servico_id: null }]
  diagError.value = ''
  try {
    const { data } = await getServicos({ apenas_ativos: true })
    diagCatalog.value = data.data ?? []
  } catch {
    diagCatalog.value = []
  }
  showDiagModal.value = true
}

function onSlotChange(idx) {
  if (idx === diagSlots.value.length - 1 && diagSlots.value[idx].servico_id !== null) {
    diagSlots.value.push({ servico_id: null })
  }
}

function removeSlot(idx) {
  diagSlots.value.splice(idx, 1)
  if (diagSlots.value.length === 0) diagSlots.value.push({ servico_id: null })
}

async function confirmDiag() {
  const filled = diagSlots.value.filter(s => s.servico_id !== null)
  if (filled.length === 0) { diagError.value = 'Selecione pelo menos uma operação.'; return }
  diagLoading.value = true
  diagError.value   = ''
  try {
    const itens = filled.map(s => {
      const cat = diagCatalog.value.find(c => c.id === s.servico_id)
      return { servico_id: s.servico_id, nome: cat.nome, preco: cat.preco_base }
    })
    await submeterDiagnostico(os.value.id, { itens })
    showDiagModal.value = false
    await load()
  } catch (e) {
    diagError.value = e.response?.data?.detail?.detail || 'Erro ao submeter diagnóstico.'
  } finally {
    diagLoading.value = false
  }
}

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
  EM_DIAGNOSTICO: [],
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
const ESTADOS_AUTO_STOP  = ['AGUARDA_PECAS', 'CONCLUIDA', 'CANCELADA']
const ESTADOS_TRABALHO   = ['EM_REPARACAO', 'AGUARDA_PECAS']

const ESTADO_LABELS = {
  PENDENTE: 'Pendente',
  EM_DIAGNOSTICO: 'Em Diagnóstico',
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
  if (os.value.estado === 'EM_DIAGNOSTICO') return { isDiag: true, label: 'Concluir Diagnóstico' }
  if (os.value.estado === 'EM_REPARACAO')   return { estado: 'CONCLUIDA', label: 'Concluir Reparação' }
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

// Part request (pedido de peça ao gerente)
const showPedidoPeca   = ref(false)
const pedidoPecaSearch = ref('')
const pedidoPecaResults = ref([])
const pedidoPecaSelected = ref(null)
const pedidoPecaQty    = ref(1)
const pedidoPecaObs    = ref('')
const pedidoPecaLoading = ref(false)
const pedidoPecaError  = ref('')
const pedidoPecaSuccess = ref(false)
let pedidoPecaTimer

const canRequestPeca = computed(() =>
  os.value && ['EM_REPARACAO', 'AGUARDA_PECAS'].includes(os.value.estado)
)

async function searchPedidoPeca() {
  if (!pedidoPecaSearch.value.trim()) { pedidoPecaResults.value = []; return }
  try {
    const { data } = await getPecas({ query: pedidoPecaSearch.value.trim(), page_size: 8 })
    pedidoPecaResults.value = data.data
  } catch { pedidoPecaResults.value = [] }
}

function watchPedidoPecaSearch() {
  clearTimeout(pedidoPecaTimer)
  pedidoPecaSelected.value = null
  pedidoPecaTimer = setTimeout(searchPedidoPeca, 300)
}

function selectPedidoPeca(p) {
  pedidoPecaSelected.value = p
  pedidoPecaSearch.value = p.nome
  pedidoPecaResults.value = []
  pedidoPecaQty.value = 1
}

async function submitPedidoPeca() {
  if (!pedidoPecaSelected.value) return
  pedidoPecaError.value = ''
  pedidoPecaLoading.value = true
  try {
    await criarPedidoPeca({
      ordem_servico_id: os.value.id,
      peca_id: pedidoPecaSelected.value.id,
      quantidade: pedidoPecaQty.value,
      observacoes: pedidoPecaObs.value || null,
    })
    pedidoPecaSuccess.value = true
    pedidoPecaSearch.value = ''
    pedidoPecaSelected.value = null
    pedidoPecaQty.value = 1
    pedidoPecaObs.value = ''
  } catch (e) {
    pedidoPecaError.value = e.response?.data?.detail?.detail || 'Erro ao enviar pedido.'
  } finally {
    pedidoPecaLoading.value = false
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

          <!-- Serviços do Diagnóstico -->
          <div class="card" v-if="['EM_REPARACAO', 'AGUARDA_PECAS', 'CONCLUIDA'].includes(os.estado) && os.servicos_diagnostico?.length > 0">
            <div class="card-title">Serviços do Diagnóstico</div>
            <table class="table">
              <thead>
                <tr>
                  <th>Operação</th>
                  <th class="col-right">Preço</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in os.servicos_diagnostico" :key="s.id">
                  <td>{{ s.nome }}</td>
                  <td class="col-right">{{ s.preco.toFixed(2) }} €</td>
                </tr>
              </tbody>
            </table>
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
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in os.pecas_aplicadas" :key="p.peca_id">
                  <td>{{ p.peca_nome }}</td>
                  <td class="col-right">{{ p.quantidade }}</td>
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

          <!-- Pedir Peça ao Gerente -->
          <div class="card" v-if="canRequestPeca">
            <button class="collapsible-header" @click="showPedidoPeca = !showPedidoPeca; pedidoPecaSuccess = false">
              <span class="card-title" style="margin:0">Pedir Peça ao Gerente</span>
              <span class="chevron">{{ showPedidoPeca ? '▲' : '▼' }}</span>
            </button>
            <div v-if="showPedidoPeca" class="pedido-peca-body">
              <div v-if="pedidoPecaSuccess" class="success-msg">
                Pedido enviado! O gerente receberá uma notificação.
              </div>
              <template v-else>
                <div class="peca-search-wrap" style="margin-bottom: 0.5rem">
                  <input
                    v-model="pedidoPecaSearch"
                    placeholder="Pesquisar peça em falta..."
                    @input="watchPedidoPecaSearch"
                    autocomplete="off"
                  />
                  <div v-if="pedidoPecaResults.length > 0" class="peca-dropdown">
                    <div
                      v-for="p in pedidoPecaResults"
                      :key="p.id"
                      class="peca-option"
                      @mousedown.prevent="selectPedidoPeca(p)"
                    >
                      <span class="peca-nome">{{ p.nome }}</span>
                      <span class="peca-ref">{{ p.referencia }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="pedidoPecaSelected" class="peca-selected">
                  <span>{{ pedidoPecaSelected.nome }}</span>
                  <div class="qty-row">
                    <label>Quantidade</label>
                    <input v-model.number="pedidoPecaQty" type="number" min="1" style="width: 80px" />
                  </div>
                </div>
                <div class="field" style="margin-top: 0.5rem">
                  <label style="font-size:0.8rem;font-weight:600;color:#6b7280">Observações (opcional)</label>
                  <textarea v-model="pedidoPecaObs" rows="2" placeholder="Motivo ou notas..." />
                </div>
                <p v-if="pedidoPecaError" class="form-error">{{ pedidoPecaError }}</p>
                <button
                  class="btn btn--primary btn--sm"
                  style="margin-top: 0.5rem"
                  :disabled="pedidoPecaLoading || !pedidoPecaSelected"
                  @click="submitPedidoPeca"
                >
                  {{ pedidoPecaLoading ? 'A enviar...' : 'Enviar Pedido' }}
                </button>
              </template>
            </div>
          </div>

        </div>

        <!-- Right column -->
        <div class="right">
          <!-- Right-column milestone action -->
          <div class="card card--conclude" v-if="rightColumnAction">
            <button
              class="btn btn--primary btn--action"
              :disabled="!timerAtivo"
              :title="!timerAtivo ? 'O timer deve estar ativo para continuar' : ''"
              @click="rightColumnAction.isDiag ? openDiagModal() : startTransition(rightColumnAction)"
            >
              ✓ {{ rightColumnAction.label }}
            </button>
            <p v-if="!timerAtivo" class="timer-warn">Inicia o timer para continuar.</p>
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

  <!-- Diagnostic modal -->
  <Teleport to="body">
    <div v-if="showDiagModal" class="overlay" @click.self="showDiagModal = false">
      <div class="dialog dialog--diag">
        <h2>Submeter Diagnóstico</h2>
        <p class="dialog-sub">Selecione as operações identificadas. A OS passará imediatamente a Em Reparação.</p>

        <!-- Operation slots -->
        <div class="diag-slots">
          <div class="diag-slot" v-for="(slot, idx) in diagSlots" :key="idx">
            <select v-model="slot.servico_id" class="diag-select" @change="onSlotChange(idx)">
              <option :value="null" disabled>Selecionar operação...</option>
              <option v-for="s in diagCatalog" :key="s.id" :value="s.id">{{ s.nome }}</option>
            </select>
            <button class="btn-remove-slot" @click="removeSlot(idx)" title="Remover">✕</button>
          </div>
        </div>

        <p v-if="diagError" class="form-error" style="margin-top: 0.5rem">{{ diagError }}</p>
        <div class="dialog-actions">
          <button class="btn btn--secondary" :disabled="diagLoading" @click="showDiagModal = false">Cancelar</button>
          <button class="btn btn--primary" :disabled="diagLoading || diagSlots.every(s => s.servico_id === null)" @click="confirmDiag">
            {{ diagLoading ? 'A submeter...' : 'Confirmar Diagnóstico' }}
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
.timer-warn { color: #9ca3af; font-size: 0.8rem; margin-top: 0.5rem; text-align: center; }

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
.card--info { background: #fffbeb; border: 1px solid #fde68a; }
.info-text { font-size: 0.875rem; color: #92400e; line-height: 1.6; margin: 0; }

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

.collapsible-header { display: flex; align-items: center; justify-content: space-between; background: none; border: none; width: 100%; cursor: pointer; padding: 0; }
.chevron { font-size: 0.75rem; color: #9ca3af; }
.pedido-peca-body { margin-top: 1rem; }
.success-msg { background: #dcfce7; color: #166534; border-radius: 6px; padding: 0.75rem 1rem; font-size: 0.875rem; font-weight: 500; }

.dialog--diag { max-width: 500px; }
.diag-slots { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 1.25rem; }
.diag-slot { display: flex; align-items: center; gap: 0.5rem; }
.diag-select { flex: 1; padding: 0.5rem 0.7rem; border: 1px solid #d1d5db; border-radius: 6px; font-size: 0.875rem; color: #111827; outline: none; }
.diag-select:focus { border-color: #1abc9c; }
.btn-remove-slot { background: none; border: none; color: #9ca3af; cursor: pointer; font-size: 0.85rem; padding: 0.25rem 0.5rem; border-radius: 4px; flex-shrink: 0; transition: color 0.1s, background 0.1s; }
.btn-remove-slot:hover { color: #dc2626; background: #fef2f2; }
</style>
