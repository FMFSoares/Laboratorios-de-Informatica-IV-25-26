<script setup>
import { ref, computed, onMounted } from 'vue'
import { emitirFatura, getFatura, enviarEmailFatura, downloadFaturaPdf } from '../services/faturas.js'
import { getLoja } from '../services/lojas.js'

const props = defineProps({
  os:               { type: Object, required: true },
  nivelFidelizacao: { type: Number, default: 0 },
  descontoSugerido: { type: Number, default: 0 },
})
const emit = defineEmits(['close', 'emitida'])

// 'draft' → 'emitindo' → 'confirmada'
const fase         = ref('draft')
const loja         = ref(null)
const fatura       = ref(null)
const error        = ref('')
const printLoading = ref(false)

const descontoTipo  = ref('PERCENTUAL')
const descontoValor = ref(props.descontoSugerido)

const emailState = ref('idle')
const emailInput = ref('')
const emailErr   = ref('')

onMounted(async () => {
  try {
    const { data } = await getLoja(props.os.loja_id)
    loja.value = data.data
  } catch { /* preview still works without loja details */ }
})

// ── Live computed totals (draft) ───────────────────────────────────────────────

const subtotalPecas = computed(() =>
  props.os.pecas_aplicadas.reduce((s, p) => s + p.subtotal, 0)
)

const subtotalBruto = computed(() =>
  r2(props.os.preco_servico + subtotalPecas.value)
)

const valorDesconto = computed(() => {
  const v = parseFloat(descontoValor.value) || 0
  if (v <= 0) return 0
  if (descontoTipo.value === 'PERCENTUAL')
    return r2(subtotalBruto.value * Math.min(v, 100) / 100)
  return r2(Math.min(v, subtotalBruto.value))
})

const valorFinal = computed(() => r2(subtotalBruto.value - valorDesconto.value))

function r2(n) { return Math.round(n * 100) / 100 }

// ── Emission ───────────────────────────────────────────────────────────────────

async function confirmar() {
  error.value = ''
  fase.value = 'emitindo'
  try {
    const body = { ordem_servico_id: props.os.id }
    const v = parseFloat(descontoValor.value) || 0
    if (v > 0) {
      body.desconto_tipo  = descontoTipo.value
      body.desconto_valor = v
    }
    const { data: res }  = await emitirFatura(body)
    const { data: fdata } = await getFatura(res.data.id)
    fatura.value     = fdata.data
    emailInput.value = fatura.value.cliente?.email ?? ''
    fase.value = 'confirmada'
    emit('emitida', fatura.value.id)
  } catch (e) {
    error.value = e.response?.data?.detail?.detail || 'Erro ao emitir fatura.'
    fase.value = 'draft'
  }
}

// ── Print / email (confirmed phase) ───────────────────────────────────────────

async function handlePrint() {
  printLoading.value = true
  let url = null
  try {
    const { data } = await downloadFaturaPdf(fatura.value.id)
    url = URL.createObjectURL(new Blob([data], { type: 'application/pdf' }))
    const iframe = document.createElement('iframe')
    iframe.style.cssText = 'position:fixed;width:0;height:0;border:0;visibility:hidden'
    document.body.appendChild(iframe)
    iframe.onload = () => {
      iframe.contentWindow.print()
      setTimeout(() => { document.body.removeChild(iframe); URL.revokeObjectURL(url) }, 1000)
    }
    iframe.src = url
  } catch { if (url) window.open(url, '_blank') }
  finally { printLoading.value = false }
}

function handleEmailClick() {
  if (fatura.value?.cliente?.email) doSend(fatura.value.cliente.email)
  else emailState.value = 'input'
}

async function doSend(emailTo) {
  emailState.value = 'sending'
  emailErr.value = ''
  try {
    await enviarEmailFatura(fatura.value.id, { email: emailTo || null })
    emailState.value = 'sent'
  } catch (e) {
    emailErr.value = e?.response?.data?.detail?.detail ?? 'Erro ao enviar email.'
    emailState.value = 'error'
  }
}

function fmt(dt) { return dt ? new Date(dt).toLocaleDateString('pt-PT') : '—' }
function fmtEur(v) { return v != null ? Number(v).toFixed(2) + ' €' : '—' }
</script>

<template>
  <Teleport to="body">
    <div class="overlay" @click.self="emit('close')">
      <div class="modal">

        <!-- Header -->
        <div class="modal-header">
          <div class="header-left">
            <span class="modal-title">{{ fase === 'confirmada' ? 'Fatura' : 'Emitir Fatura' }}</span>
            <span v-if="fase === 'confirmada'" class="chip chip--numero">{{ fatura.numero }}</span>
            <span v-else class="chip chip--draft">Rascunho</span>
          </div>
          <button class="close-btn" @click="emit('close')">✕</button>
        </div>

        <!-- Body: scrollable preview paper -->
        <div class="modal-body">
          <div class="preview-paper">

            <!-- Loja + meta -->
            <div class="inv-header">
              <div class="inv-brand">
                <span class="brand">DLMCare</span>
                <template v-if="fase === 'confirmada'">
                  <span class="loja-nome">{{ fatura.loja.nome }}</span>
                  <span class="loja-info">{{ fatura.loja.morada }}</span>
                  <span class="loja-info">Tel. {{ fatura.loja.telefone }}</span>
                </template>
                <template v-else>
                  <span class="loja-nome">{{ loja?.nome ?? os.loja_nome ?? '' }}</span>
                  <span v-if="loja?.morada" class="loja-info">{{ loja.morada }}</span>
                  <span v-if="loja?.telefone" class="loja-info">Tel. {{ loja.telefone }}</span>
                </template>
              </div>
              <div class="inv-meta">
                <span v-if="fase === 'confirmada'" class="inv-numero">{{ fatura.numero }}</span>
                <span v-else class="inv-numero inv-numero--draft">Rascunho</span>
                <span class="inv-data">{{ fmt(fase === 'confirmada' ? fatura.data_emissao : new Date()) }}</span>
                <span v-if="fase === 'confirmada'" class="inv-estado estado--emitida">EMITIDA</span>
                <span v-else class="inv-estado estado--draft">RASCUNHO</span>
              </div>
            </div>

            <div class="inv-divider" />

            <!-- Client + scooter -->
            <div class="inv-parties">
              <div class="party-block">
                <p class="party-label">Cliente</p>
                <p class="party-name">{{ fase === 'confirmada' ? fatura.cliente.nome : os.cliente.nome }}</p>
                <p class="party-detail">NIF: {{ fase === 'confirmada' ? fatura.cliente.nif : '—' }}</p>
                <p v-if="fase === 'confirmada' && fatura.cliente.morada" class="party-detail">{{ fatura.cliente.morada }}</p>
              </div>
              <div class="party-block">
                <p class="party-label">Trotinete</p>
                <p class="party-name">{{ os.trotinete.marca }} {{ os.trotinete.modelo }}</p>
                <p class="party-detail">S/N: {{ os.trotinete.numero_serie }}</p>
              </div>
            </div>

            <div class="inv-divider" />

            <!-- Service line -->
            <table class="line-table">
              <thead>
                <tr>
                  <th class="col-desc">Descrição do serviço</th>
                  <th class="col-val">Valor</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>{{ os.descricao_problema }}</td>
                  <td class="val">{{ fmtEur(os.preco_servico) }}</td>
                </tr>
              </tbody>
            </table>

            <!-- Parts -->
            <template v-if="os.pecas_aplicadas.length > 0">
              <p class="section-label">Peças aplicadas</p>
              <table class="line-table">
                <thead>
                  <tr>
                    <th class="col-desc">Designação</th>
                    <th class="col-qty">Qtd.</th>
                    <th class="col-val">P. Unit.</th>
                    <th class="col-val">Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in os.pecas_aplicadas" :key="p.peca_id">
                    <td>{{ p.peca_nome }}</td>
                    <td class="center">{{ p.quantidade }}</td>
                    <td class="val">{{ fmtEur(p.preco_venda_unitario) }}</td>
                    <td class="val">{{ fmtEur(p.subtotal) }}</td>
                  </tr>
                </tbody>
              </table>
            </template>

            <div class="inv-divider" />

            <!-- Totals -->
            <div class="totals">
              <div class="totals-row">
                <span>Serviço</span>
                <span>{{ fmtEur(os.preco_servico) }}</span>
              </div>
              <div v-if="os.pecas_aplicadas.length > 0" class="totals-row">
                <span>Peças</span>
                <span>{{ fmtEur(subtotalPecas) }}</span>
              </div>

              <!-- Discount row — live computed in draft, static when confirmed -->
              <div v-if="fase !== 'confirmada' && valorDesconto > 0" class="totals-row totals-row--desconto">
                <span>
                  Desconto
                  <template v-if="descontoTipo === 'PERCENTUAL'"> ({{ descontoValor }}%)</template>
                </span>
                <span>-{{ fmtEur(valorDesconto) }}</span>
              </div>
              <div v-else-if="fase === 'confirmada' && fatura.valor_desconto > 0" class="totals-row totals-row--desconto">
                <span>
                  Desconto
                  <template v-if="fatura.desconto_tipo === 'PERCENTUAL'"> ({{ fatura.desconto_valor }}%)</template>
                </span>
                <span>-{{ fmtEur(fatura.valor_desconto) }}</span>
              </div>

              <div class="totals-row totals-row--total">
                <span>Total</span>
                <span>{{ fase === 'confirmada' ? fmtEur(fatura.valor_final) : fmtEur(valorFinal) }}</span>
              </div>
            </div>

            <p class="inv-footer">OS #{{ os.id }}</p>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">

          <!-- Draft footer -->
          <template v-if="fase === 'draft' || fase === 'emitindo'">
            <div class="draft-footer">
              <div class="draft-left">
                <div v-if="nivelFidelizacao > 0" class="fidelizacao-info">
                  Fidelização nível {{ nivelFidelizacao }}/5
                  <span v-if="descontoSugerido > 0"> — sugerido {{ descontoSugerido }}%</span>
                </div>
                <div class="desconto-controls">
                  <select v-model="descontoTipo" class="desconto-select" :disabled="fase === 'emitindo'">
                    <option value="PERCENTUAL">% Desconto</option>
                    <option value="FIXO">€ Desconto fixo</option>
                  </select>
                  <input
                    v-model.number="descontoValor"
                    type="number"
                    min="0"
                    :max="descontoTipo === 'PERCENTUAL' ? 100 : undefined"
                    step="0.5"
                    class="desconto-input"
                    :placeholder="descontoTipo === 'PERCENTUAL' ? '0 %' : '0 €'"
                    :disabled="fase === 'emitindo'"
                  />
                </div>
              </div>
              <div class="draft-right">
                <p v-if="error" class="emit-error">{{ error }}</p>
                <button class="btn btn--secondary" @click="emit('close')" :disabled="fase === 'emitindo'">
                  Cancelar
                </button>
                <button class="btn btn--primary" @click="confirmar" :disabled="fase === 'emitindo'">
                  {{ fase === 'emitindo' ? 'A emitir...' : 'Confirmar e Emitir' }}
                </button>
              </div>
            </div>
          </template>

          <!-- Confirmed footer -->
          <template v-else>
            <div class="confirmed-banner">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#15803d" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              Fatura emitida com sucesso
            </div>
            <div class="footer-actions">
              <button class="action-btn" :disabled="printLoading" @click="handlePrint">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
                {{ printLoading ? 'A preparar...' : 'Imprimir' }}
              </button>

              <button v-if="emailState === 'idle' && fatura.cliente?.email" class="action-btn" @click="handleEmailClick">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
                Enviar por Email
                <span class="email-hint">{{ fatura.cliente.email }}</span>
              </button>

              <button v-else-if="emailState === 'idle' && !fatura.cliente?.email" class="action-btn" @click="handleEmailClick">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
                Enviar por Email
              </button>

              <div v-else-if="emailState === 'input'" class="email-input-row">
                <input v-model="emailInput" type="email" class="email-field" placeholder="Email do cliente" @keydown.enter="doSend(emailInput)" />
                <button class="action-btn action-btn--compact" @click="doSend(emailInput)" :disabled="!emailInput.trim()">Enviar</button>
                <button class="action-btn action-btn--ghost" @click="emailState = 'idle'">Cancelar</button>
              </div>

              <div v-else-if="emailState === 'sending'" class="email-status sending">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spin"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                A enviar...
              </div>

              <div v-else-if="emailState === 'sent'" class="email-status sent">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                Email enviado
              </div>

              <div v-else-if="emailState === 'error'" class="email-status error-status">
                <span>{{ emailErr }}</span>
                <button class="action-btn action-btn--compact" @click="emailState = 'idle'">Tentar novamente</button>
              </div>
            </div>
          </template>

        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.55);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000;
}

.modal {
  width: 92vw; height: 90vh;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 24px 80px rgba(0,0,0,0.3);
  display: flex; flex-direction: column;
  overflow: hidden;
}

/* Header */
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 0.75rem; }
.modal-title { font-size: 1rem; font-weight: 700; color: #111827; }

.chip {
  font-size: 0.78rem; font-weight: 600;
  padding: 0.15rem 0.6rem; border-radius: 6px;
}
.chip--numero { font-family: 'Courier New', monospace; background: #f3f4f6; color: #6b7280; }
.chip--draft  { background: #fef9c3; color: #92400e; }

.close-btn {
  background: none; border: none; font-size: 1rem;
  color: #9ca3af; cursor: pointer;
  padding: 0.25rem 0.5rem; border-radius: 6px; line-height: 1;
  transition: background 0.15s, color 0.15s;
}
.close-btn:hover { background: #f3f4f6; color: #374151; }

/* Body */
.modal-body {
  flex: 1; overflow: auto;
  background: #f3f4f6;
  display: flex; align-items: flex-start; justify-content: center;
  padding: 2rem;
}

.preview-paper {
  width: 100%; max-width: 700px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.1);
  padding: 2.5rem;
  font-size: 0.875rem; color: #374151;
}

/* Invoice internals */
.inv-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.inv-brand  { display: flex; flex-direction: column; gap: 0.2rem; }
.brand      { font-size: 1.4rem; font-weight: 800; color: #1abc9c; letter-spacing: -0.02em; line-height: 1; margin-bottom: 0.3rem; }
.loja-nome  { font-size: 0.875rem; font-weight: 600; color: #111827; }
.loja-info  { font-size: 0.8rem; color: #6b7280; }

.inv-meta   { display: flex; flex-direction: column; align-items: flex-end; gap: 0.3rem; }
.inv-numero { font-size: 1rem; font-weight: 700; color: #111827; font-family: 'Courier New', monospace; }
.inv-numero--draft { color: #9ca3af; }
.inv-data   { font-size: 0.82rem; color: #6b7280; }
.inv-estado { font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.6rem; border-radius: 999px; }
.estado--emitida { background: #ccfbf1; color: #0f766e; }
.estado--draft   { background: #fef9c3; color: #92400e; }

.inv-divider { border: none; border-top: 1px solid #e5e7eb; margin: 1.25rem 0; }

.inv-parties { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.party-block { display: flex; flex-direction: column; gap: 0.15rem; }
.party-label  { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #9ca3af; margin-bottom: 0.1rem; }
.party-name   { font-size: 0.9rem; font-weight: 600; color: #111827; }
.party-detail { font-size: 0.8rem; color: #6b7280; }

.section-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #9ca3af; margin: 1rem 0 0.4rem; }

.line-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.line-table th { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: #6b7280; padding: 0.45rem 0.6rem; border-bottom: 1px solid #e5e7eb; text-align: left; background: #f9fafb; }
.line-table td { padding: 0.6rem 0.6rem; border-bottom: 1px solid #f3f4f6; }
.line-table tbody tr:last-child td { border-bottom: none; }
.col-desc { width: auto; }
.col-qty  { width: 50px; }
.col-val  { width: 90px; text-align: right; }
.val    { text-align: right; font-variant-numeric: tabular-nums; }
.center { text-align: center; }

/* Totals */
.totals { display: flex; flex-direction: column; align-items: flex-end; gap: 0.35rem; padding: 0.4rem 0.6rem 0; }
.totals-row { display: flex; gap: 2.5rem; font-size: 0.85rem; color: #374151; min-width: 260px; justify-content: space-between; align-items: center; }
.totals-row span:last-child { font-variant-numeric: tabular-nums; }
.totals-row--total    { border-top: 2px solid #111827; padding-top: 0.35rem; margin-top: 0.15rem; font-size: 0.95rem; font-weight: 700; color: #111827; }
.totals-row--desconto { color: #dc2626; font-weight: 500; }

/* Discount controls (in footer) */
.desconto-controls { display: flex; gap: 0.4rem; align-items: center; }
.desconto-select {
  padding: 0.35rem 0.5rem; border: 1px solid #d1d5db; border-radius: 6px;
  font-size: 0.82rem; color: #374151; background: #fff; cursor: pointer; outline: none;
}
.desconto-select:focus { border-color: #1abc9c; }
.desconto-select:disabled { opacity: 0.5; cursor: not-allowed; }
.desconto-input {
  width: 80px; padding: 0.35rem 0.5rem;
  border: 1px solid #d1d5db; border-radius: 6px;
  font-size: 0.875rem; color: #374151; text-align: right; outline: none;
  appearance: textfield; -moz-appearance: textfield;
}
.desconto-input::-webkit-inner-spin-button,
.desconto-input::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
.desconto-input:focus { border-color: #1abc9c; }
.desconto-input:disabled { opacity: 0.5; cursor: not-allowed; }

.inv-footer { margin-top: 1.5rem; font-size: 0.75rem; color: #9ca3af; text-align: center; }

/* Footer */
.modal-footer {
  border-top: 1px solid #e5e7eb;
  padding: 0.85rem 1.5rem;
  flex-shrink: 0; background: #fff;
}

/* Draft footer */
.draft-footer {
  display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
}
.draft-left  { display: flex; flex-direction: column; gap: 0.4rem; }
.draft-right { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.fidelizacao-info {
  font-size: 0.78rem; color: #065f46;
  background: #ecfdf5; border: 1px solid #6ee7b7;
  padding: 0.25rem 0.6rem; border-radius: 6px;
  width: fit-content;
}
.emit-error { font-size: 0.82rem; color: #dc2626; }

.btn {
  padding: 0.6rem 1.2rem; border: none; border-radius: 6px;
  font-size: 0.875rem; font-weight: 600; cursor: pointer;
  transition: opacity 0.15s; white-space: nowrap;
}
.btn:hover:not(:disabled) { opacity: 0.85; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary   { background: #1abc9c; color: #fff; }
.btn--secondary { background: #e5e7eb; color: #374151; }

/* Confirmed footer */
.confirmed-banner {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.82rem; font-weight: 600; color: #15803d;
  margin-bottom: 0.65rem;
}

.footer-actions { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }

.action-btn {
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  border: 1px solid #d1d5db; border-radius: 8px;
  background: #fff; font-size: 0.875rem; font-weight: 600;
  color: #374151; cursor: pointer;
  transition: background 0.15s, border-color 0.15s; white-space: nowrap;
}
.action-btn:hover:not(:disabled) { background: #f9fafb; border-color: #9ca3af; }
.action-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.action-btn--compact { padding: 0.45rem 0.9rem; font-size: 0.82rem; }
.action-btn--ghost   { background: transparent; border-color: transparent; color: #6b7280; }
.action-btn--ghost:hover { background: #f3f4f6; }

.email-hint { font-size: 0.78rem; font-weight: 400; color: #9ca3af; }
.email-input-row { display: flex; align-items: center; gap: 0.5rem; flex: 1; }
.email-field {
  flex: 1; min-width: 200px; padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db; border-radius: 6px;
  font-size: 0.875rem; color: #374151; outline: none;
}
.email-field:focus { border-color: #1abc9c; box-shadow: 0 0 0 3px rgba(26,188,156,0.15); }

.email-status { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; font-weight: 500; }
.sending { color: #6b7280; }
.sent    { color: #15803d; }
.error-status { color: #dc2626; gap: 0.75rem; }

@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; }
</style>
