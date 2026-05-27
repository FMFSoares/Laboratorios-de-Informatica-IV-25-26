<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth.js'
import {
  getTransferencia, responderTransferencia,
  confirmarRecepcao, cancelarTransferencia, getPdfTransferencia,
} from '../../services/transferencias.js'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()

const t       = ref(null)
const loading = ref(true)
const error   = ref('')
const actionLoading = ref(false)

const showResponder = ref(false)
const resAceitar    = ref(true)
const resObs        = ref('')

const showConfirmar = ref(false)
const showCancelar  = ref(false)

async function load() {
  loading.value = true
  try {
    const r = await getTransferencia(route.params.id)
    t.value = r.data
  } catch { error.value = 'Erro ao carregar.' }
  finally { loading.value = false }
}

async function responder(aceitar) {
  actionLoading.value = true
  try {
    await responderTransferencia(t.value.id, { aceitar, observacoes: resObs.value || null })
    showResponder.value = false
    await load()
  } catch (e) { error.value = e.response?.data?.detail?.detail || 'Erro.' }
  finally { actionLoading.value = false }
}

async function confirmar() {
  showConfirmar.value = false
  actionLoading.value = true
  try { await confirmarRecepcao(t.value.id); await load() }
  catch (e) { error.value = e.response?.data?.detail?.detail || 'Erro.' }
  finally { actionLoading.value = false }
}

async function cancelar() {
  showCancelar.value = false
  actionLoading.value = true
  try { await cancelarTransferencia(t.value.id); await load() }
  catch (e) { error.value = e.response?.data?.detail?.detail || 'Erro.' }
  finally { actionLoading.value = false }
}

async function downloadPdf() {
  try {
    const bytes = await getPdfTransferencia(t.value.id)
    const url = URL.createObjectURL(new Blob([bytes], { type: 'application/pdf' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `${t.value.numero}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch { error.value = 'Erro ao gerar PDF.' }
}

const minhaLoja = computed(() => auth.getCurrentUser?.loja_id)
const podeResponder = computed(() => t.value?.estado === 'PENDENTE' && t.value?.loja_origem?.id === minhaLoja.value)
const podeCancelar  = computed(() => t.value?.estado === 'PENDENTE' && t.value?.loja_destino?.id === minhaLoja.value)
const podeConfirmar = computed(() => t.value?.estado === 'ACEITE'   && t.value?.loja_destino?.id === minhaLoja.value)

const ESTADO_COLOR = {
  PENDENTE:  { bg: '#fef9c3', color: '#854d0e' },
  ACEITE:    { bg: '#dbeafe', color: '#1e40af' },
  CONCLUIDA: { bg: '#dcfce7', color: '#166534' },
  RECUSADO:  { bg: '#fee2e2', color: '#991b1b' },
  CANCELADO: { bg: '#f1f5f9', color: '#64748b' },
}

function fmtDt(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('pt-PT', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' })
}

onMounted(load)
</script>

<template>
  <div class="page">
    <button class="back-btn" @click="router.push('/transferencias')">← Transferências</button>

    <div v-if="loading" class="msg">A carregar...</div>
    <div v-else-if="error && !t" class="msg msg--error">{{ error }}</div>
    <template v-else-if="t">
      <div class="page-header">
        <div>
          <h1 class="page-title">{{ t.numero }}</h1>
          <span class="chip" :style="ESTADO_COLOR[t.estado]">{{ t.estado }}</span>
        </div>
        <div class="actions">
          <button v-if="t.estado !== 'PENDENTE'" class="btn btn--ghost" @click="downloadPdf">
            Documento PDF
          </button>
          <button v-if="podeResponder" class="btn btn--primary" @click="showResponder = true">
            Responder
          </button>
          <button v-if="podeConfirmar" class="btn btn--primary" :disabled="actionLoading" @click="showConfirmar = true">
            Confirmar Receção
          </button>
          <button v-if="podeCancelar" class="btn btn--ghost" :disabled="actionLoading" @click="showCancelar = true">
            Cancelar
          </button>
        </div>
      </div>

      <p v-if="error" class="msg msg--error">{{ error }}</p>

      <div class="grid-2">
        <!-- Transfer details -->
        <div class="card">
          <div class="card-title">Detalhes</div>
          <div class="info-grid">
            <span class="lbl">Peça</span>      <span>{{ t.peca?.referencia }} — {{ t.peca?.nome }}</span>
            <span class="lbl">Quantidade</span><span>{{ t.quantidade }}</span>
            <span class="lbl">Data pedido</span><span>{{ fmtDt(t.data_pedido) }}</span>
            <span class="lbl">Resposta</span>  <span>{{ fmtDt(t.data_resposta) }}</span>
            <span class="lbl">Receção</span>   <span>{{ fmtDt(t.data_recepcao) }}</span>
          </div>
          <div v-if="t.observacoes_pedido" class="obs">
            <span class="lbl">Obs. pedido:</span> {{ t.observacoes_pedido }}
          </div>
          <div v-if="t.observacoes_resposta" class="obs">
            <span class="lbl">Obs. resposta:</span> {{ t.observacoes_resposta }}
          </div>
        </div>

        <!-- Stores -->
        <div class="card">
          <div class="card-title">Lojas</div>
          <div class="loja-row">
            <div class="loja-block">
              <div class="loja-label">Origem (cedente)</div>
              <div class="loja-name">{{ t.loja_origem?.nome }}</div>
              <div class="loja-gerente">{{ t.gerente_origem?.nome }}</div>
              <div class="sig-row">
                <span :class="['sig', t.data_assinatura_origem ? 'sig--ok' : 'sig--pending']">
                  {{ t.data_assinatura_origem ? '✓ Assinado' : '⏳ Pendente' }}
                </span>
                <span v-if="t.data_assinatura_origem" class="sig-date">{{ fmtDt(t.data_assinatura_origem) }}</span>
              </div>
            </div>
            <div class="arrow">→</div>
            <div class="loja-block">
              <div class="loja-label">Destino (recetor)</div>
              <div class="loja-name">{{ t.loja_destino?.nome }}</div>
              <div class="loja-gerente">{{ t.gerente_destino?.nome }}</div>
              <div class="sig-row">
                <span :class="['sig', t.data_assinatura_destino ? 'sig--ok' : 'sig--pending']">
                  {{ t.data_assinatura_destino ? '✓ Assinado' : '⏳ Pendente' }}
                </span>
                <span v-if="t.data_assinatura_destino" class="sig-date">{{ fmtDt(t.data_assinatura_destino) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Confirm receipt modal -->
      <Teleport to="body">
        <div v-if="showConfirmar" class="overlay" @click.self="showConfirmar = false">
          <div class="modal modal--sm">
            <h2 class="modal-title">Confirmar receção</h2>
            <p class="modal-sub">
              Confirma que recebeu <strong>{{ t.quantidade }} {{ t.peca?.nome }}</strong>
              da loja <strong>{{ t.loja_origem?.nome }}</strong>?
              Esta ação adicionará o stock ao inventário da sua loja.
            </p>
            <div class="modal-footer">
              <button class="btn btn--ghost" @click="showConfirmar = false">Cancelar</button>
              <button class="btn btn--primary" :disabled="actionLoading" @click="confirmar">
                {{ actionLoading ? 'A confirmar...' : 'Confirmar Receção' }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- Cancel modal -->
      <Teleport to="body">
        <div v-if="showCancelar" class="overlay" @click.self="showCancelar = false">
          <div class="modal modal--sm">
            <h2 class="modal-title">Cancelar pedido</h2>
            <p class="modal-sub">
              Tens a certeza que queres cancelar o pedido de
              <strong>{{ t.quantidade }} {{ t.peca?.nome }}</strong>?
              Esta ação não pode ser desfeita.
            </p>
            <div class="modal-footer">
              <button class="btn btn--ghost" @click="showCancelar = false">Voltar</button>
              <button class="btn btn--danger" :disabled="actionLoading" @click="cancelar">
                {{ actionLoading ? 'A cancelar...' : 'Cancelar Pedido' }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- Respond modal -->
      <Teleport to="body">
        <div v-if="showResponder" class="overlay" @click.self="showResponder = false">
          <div class="modal">
            <h2 class="modal-title">Responder ao pedido</h2>
            <p class="modal-sub">{{ t.peca?.nome }} — {{ t.quantidade }} un. de {{ t.loja_origem?.nome }}</p>

            <div class="decision-cards">
              <button
                :class="['decision-card', 'decision-card--accept', resAceitar && 'decision-card--selected']"
                @click="resAceitar = true"
              >
                <span class="decision-icon">✓</span>
                <span class="decision-label">Aceitar</span>
                <span class="decision-desc">Deduz stock e notifica a loja destino</span>
              </button>
              <button
                :class="['decision-card', 'decision-card--refuse', !resAceitar && 'decision-card--selected']"
                @click="resAceitar = false"
              >
                <span class="decision-icon">✕</span>
                <span class="decision-label">Recusar</span>
                <span class="decision-desc">Notifica a loja destino da recusa</span>
              </button>
            </div>

            <div class="field">
              <label>Observações (opcional)</label>
              <textarea v-model="resObs" rows="3" placeholder="Motivo ou notas para a outra loja..." />
            </div>
            <div class="modal-footer">
              <button class="btn btn--ghost" @click="showResponder = false">Cancelar</button>
              <button
                class="btn"
                :class="resAceitar ? 'btn--primary' : 'btn--danger'"
                :disabled="actionLoading"
                @click="responder(resAceitar)"
              >{{ actionLoading ? 'A enviar...' : resAceitar ? 'Confirmar Aceitação' : 'Confirmar Recusa' }}</button>
            </div>
          </div>
        </div>
      </Teleport>
    </template>
  </div>
</template>

<style scoped>
.page { padding: 1.5rem 2rem; max-width: 900px; margin: 0 auto; }
.back-btn { background: none; border: none; color: #64748b; font-size: 0.85rem; cursor: pointer; padding: 0; margin-bottom: 1rem; }
.back-btn:hover { color: #1abc9c; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; margin-bottom: 1.5rem; }
.page-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0 0 0.4rem; }
.actions { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.chip { display: inline-block; padding: 0.2rem 0.7rem; border-radius: 99px; font-size: 0.78rem; font-weight: 600; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 6px rgba(0,0,0,0.07); padding: 1.25rem; }
.card-title { font-size: 0.8rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.9rem; }
.info-grid { display: grid; grid-template-columns: auto 1fr; gap: 0.35rem 1rem; font-size: 0.875rem; align-items: baseline; }
.lbl { font-weight: 600; color: #64748b; white-space: nowrap; }
.obs { margin-top: 0.75rem; font-size: 0.85rem; color: #374151; }
.loja-row { display: flex; align-items: center; gap: 0.75rem; }
.loja-block { flex: 1; }
.arrow { font-size: 1.2rem; color: #94a3b8; flex-shrink: 0; }
.loja-label { font-size: 0.72rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.2rem; }
.loja-name { font-size: 0.95rem; font-weight: 700; color: #1e293b; }
.loja-gerente { font-size: 0.82rem; color: #64748b; margin-bottom: 0.5rem; }
.sig-row { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.sig { font-size: 0.78rem; font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 5px; }
.sig--ok { background: #dcfce7; color: #166534; }
.sig--pending { background: #f1f5f9; color: #94a3b8; }
.sig-date { font-size: 0.72rem; color: #94a3b8; }
.msg { padding: 2rem; text-align: center; color: #9ca3af; font-size: 0.9rem; }
.msg--error { color: #dc2626; }
.btn { padding: 0.5rem 1.1rem; border-radius: 7px; font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--ghost   { background: #f1f5f9; color: #374151; border: 1px solid #d1d5db; }
.btn--danger  { background: #ef4444; color: #fff; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Modal */
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 14px; padding: 1.75rem; width: 100%; max-width: 460px; box-shadow: 0 12px 40px rgba(0,0,0,0.18); }
.modal--sm { max-width: 400px; }
.modal-title { font-size: 1.15rem; font-weight: 700; margin: 0 0 0.25rem; color: #1e293b; }
.modal-sub { font-size: 0.85rem; color: #64748b; margin: 0 0 1.25rem; }

/* Decision cards */
.decision-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1.25rem; }
.decision-card {
  display: flex; flex-direction: column; align-items: center; gap: 0.3rem;
  padding: 1rem 0.75rem; border-radius: 10px; border: 2px solid #e2e8f0;
  background: #f8fafc; cursor: pointer; transition: all 0.15s; text-align: center;
}
.decision-card:hover { border-color: #cbd5e1; background: #f1f5f9; }
.decision-card--accept.decision-card--selected { border-color: #1abc9c; background: #f0fdf9; }
.decision-card--refuse.decision-card--selected { border-color: #ef4444; background: #fff5f5; }
.decision-icon { font-size: 1.4rem; font-weight: 700; }
.decision-card--accept .decision-icon { color: #1abc9c; }
.decision-card--refuse .decision-icon { color: #ef4444; }
.decision-label { font-size: 0.9rem; font-weight: 700; color: #1e293b; }
.decision-desc { font-size: 0.72rem; color: #94a3b8; line-height: 1.4; }

.field { display: flex; flex-direction: column; gap: 0.3rem; margin-bottom: 0.9rem; }
.field label { font-size: 0.82rem; font-weight: 600; color: #374151; }
.field textarea { padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 7px; font-size: 0.875rem; font-family: inherit; outline: none; resize: vertical; }
.field textarea:focus { border-color: #1abc9c; }
.modal-footer { display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 1rem; }

@media (max-width: 700px) { .grid-2 { grid-template-columns: 1fr; } }
</style>
