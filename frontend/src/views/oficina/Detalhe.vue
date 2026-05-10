<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getOrdemServico,
  atualizarEstado,
  iniciarTempo,
  pararTempo,
  adicionarPeca,
  adicionarObservacao,
} from '../../services/ordensServico.js'
import { getPecas } from '../../services/pecas.js'
import { useAuthStore } from '../../store/auth.js'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import LoadingSpinner from '../../components/ui/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const os = ref(null)
const loading = ref(true)

// State transition
const showEstadoModal = ref(false)
const pendingTransition = ref(null)
const transitionObs = ref('')
const stateLoading = ref(false)
const stateError = ref('')

// Parts
const pecaSearch = ref('')
const pecaResults = ref([])
const pecaSearchLoading = ref(false)
const pecaSelecionada = ref(null)
const pecaQty = ref(1)
const pecaLoading = ref(false)
const pecaError = ref('')
let pecaSearchTimer

// Observations
const novaObs = ref('')
const obsLoading = ref(false)

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
const ESTADOS_TRABALHO   = ['EM_DIAGNOSTICO', 'EM_REPARACAO', 'AGUARDA_PECAS']

const availableActions = computed(() => TRANSICOES[os.value?.estado] ?? [])
const timerAtivo = computed(() => !!os.value?.inicio_tempo_atual)
const canAddParts = computed(() => os.value && ESTADOS_TRABALHO.includes(os.value.estado))

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
})
onUnmounted(() => clearInterval(pollInterval))

// Timer is fully automatic — starts/stops with state transitions
async function handleAutoTimer(novoEstado) {
  if (ESTADOS_AUTO_START.includes(novoEstado) && !timerAtivo.value) {
    try {
      await iniciarTempo(os.value.id)
    } catch (e) {
      // Another OS has a running timer — stop it first, then start here
      if (e.response?.data?.detail?.code === 'MECANICO_TIMER_CONFLICT') {
        const conflito_id = e.response.data.detail.os_conflito_id
        try { await pararTempo(conflito_id) } catch { /* ignore */ }
        try { await iniciarTempo(os.value.id) } catch { /* ignore */ }
      }
    }
  } else if (ESTADOS_AUTO_STOP.includes(novoEstado) && timerAtivo.value) {
    try { await pararTempo(os.value.id) } catch { /* ignore */ }
  }
}

// State transitions
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

// Observations
async function submitObs() {
  if (!novaObs.value.trim()) return
  obsLoading.value = true
  try {
    await adicionarObservacao(os.value.id, { texto: novaObs.value.trim() })
    novaObs.value = ''
    await load()
  } catch {
  } finally {
    obsLoading.value = false
  }
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
      <button class="btn-back" @click="router.push('/oficina')">← Oficina</button>
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
              <span class="minutos-label">⏱ {{ os.tempo_total_minutos || 0 }} min trabalhados</span>
            </div>
          </div>

          <!-- State actions -->
          <div class="card" v-if="availableActions.length > 0">
            <div class="card-title">Próxima Ação</div>
            <div class="action-list">
              <button
                v-for="action in availableActions"
                :key="action.estado"
                class="btn btn--primary btn--action"
                @click="startTransition(action)"
              >
                {{ action.label }}
              </button>
            </div>
          </div>

          <!-- Peças aplicadas -->
          <div class="card">
            <div class="card-title">Peças Aplicadas</div>
            <div v-if="os.pecas_aplicadas.length === 0" class="empty-msg">Nenhuma peça associada.</div>
            <table v-else class="table">
              <thead>
                <tr>
                  <th>Peça</th>
                  <th class="col-right">Qtd</th>
                  <th class="col-right">P. Unit.</th>
                  <th class="col-right">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in os.pecas_aplicadas" :key="p.peca_id">
                  <td>{{ p.peca_nome }}</td>
                  <td class="col-right">{{ p.quantidade }}</td>
                  <td class="col-right">{{ p.preco_venda_unitario.toFixed(2) }} €</td>
                  <td class="col-right">{{ p.subtotal.toFixed(2) }} €</td>
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
                    <span class="peca-ref">{{ p.referencia }} · {{ p.preco_venda.toFixed(2) }} €</span>
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

          <!-- Cost summary -->
          <div class="card">
            <div class="card-title">Custo Estimado</div>
            <div class="price-rows">
              <div class="price-row"><span>Serviço</span><span>{{ os.preco_servico.toFixed(2) }} €</span></div>
              <div class="price-row"><span>Peças</span><span>{{ os.subtotal_pecas.toFixed(2) }} €</span></div>
              <div class="price-row price-row--total"><span>Total</span><span>{{ os.valor_estimado_total.toFixed(2) }} €</span></div>
            </div>
          </div>
        </div>

        <!-- Right column -->
        <div class="right">
          <div class="card">
            <div class="card-title">Observações Internas</div>
            <div v-if="os.observacoes.length === 0" class="empty-msg">Sem observações.</div>
            <div class="obs-list">
              <div v-for="obs in os.observacoes" :key="obs.id" class="obs-item">
                <div class="obs-header">
                  <span class="obs-autor">{{ obs.autor_nome }}</span>
                  <span class="obs-date">{{ fmtDateTime(obs.criado_em) }}</span>
                </div>
                <p class="obs-text">{{ obs.texto }}</p>
              </div>
            </div>
            <div v-if="os.estado !== 'CANCELADA'" class="obs-form">
              <textarea v-model="novaObs" rows="3" placeholder="Adicionar observação..." />
              <button
                class="btn btn--primary btn--sm"
                :disabled="obsLoading || !novaObs.trim()"
                @click="submitObs"
              >
                {{ obsLoading ? 'A guardar...' : 'Adicionar' }}
              </button>
            </div>
          </div>
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
        <p class="dialog-sub">{{ os?.estado }} → <strong>{{ pendingTransition?.estado }}</strong></p>
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

.obs-list { display: flex; flex-direction: column; gap: 0.6rem; margin-bottom: 0.75rem; }
.obs-item { background: #f9fafb; border-radius: 6px; padding: 0.7rem; }
.obs-header { display: flex; justify-content: space-between; margin-bottom: 0.3rem; }
.obs-autor { font-size: 0.82rem; font-weight: 600; color: #374151; }
.obs-date { font-size: 0.75rem; color: #9ca3af; }
.obs-text { font-size: 0.875rem; color: #374151; line-height: 1.5; margin: 0; }
.obs-form { display: flex; flex-direction: column; gap: 0.5rem; }

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
.btn--sm { padding: 0.4rem 0.8rem; font-size: 0.825rem; }

.mono { font-family: 'Courier New', monospace; }

.overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: #fff; border-radius: 10px; padding: 2rem; width: 100%; max-width: 440px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.dialog-sub { font-size: 0.875rem; color: #6b7280; margin-top: 0.3rem; }
.dialog-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem; }
.field { display: flex; flex-direction: column; }
</style>
