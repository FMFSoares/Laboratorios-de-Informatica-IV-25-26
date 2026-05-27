<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getFatura, downloadFaturaPdf } from '../../services/faturas.js'
import StatusBadge from '../../components/ui/StatusBadge.vue'

const route  = useRoute()
const router = useRouter()

const fatura  = ref(null)
const loading = ref(false)
const error   = ref(null)

async function load() {
  loading.value = true
  error.value   = null
  try {
    const { data } = await getFatura(route.params.id)
    fatura.value = data.data
  } catch (e) {
    error.value = e?.response?.data?.detail ?? 'Erro ao carregar fatura.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

function fmt(dt) {
  return dt
    ? new Date(dt).toLocaleDateString('pt-PT', { day: '2-digit', month: 'long', year: 'numeric' })
    : '—'
}

function fmtEur(v) {
  return v != null ? Number(v).toFixed(2) + ' €' : '—'
}

async function downloadPdf() {
  try {
    const res = await downloadFaturaPdf(fatura.value.id)
    const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `fatura-${fatura.value.numero}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch { /* silently ignore — backend may not have PDF generation yet */ }
}
</script>

<template>
  <div class="page">
    <div class="top-bar">
      <button class="back-btn" @click="router.back()">← Voltar</button>
      <button v-if="fatura" class="btn-download" @click="downloadPdf">↓ Descarregar PDF</button>
    </div>

    <div v-if="loading" class="loading-msg">A carregar...</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>

    <div v-else-if="fatura" class="invoice">

      <!-- Invoice header -->
      <div class="inv-header">
        <div class="inv-brand">
          <span class="brand">DLMCare</span>
          <span class="loja-nome">{{ fatura.loja.nome }}</span>
          <span class="loja-info">{{ fatura.loja.morada }}</span>
          <span class="loja-info">Tel. {{ fatura.loja.telefone }}</span>
        </div>
        <div class="inv-meta">
          <span class="inv-numero">{{ fatura.numero }}</span>
          <span class="inv-data">{{ fmt(fatura.data_emissao) }}</span>
          <StatusBadge :estado="fatura.estado" />
        </div>
      </div>

      <div class="inv-divider" />

      <!-- Client + Scooter -->
      <div class="inv-parties">
        <div class="party-block">
          <p class="party-label">Cliente</p>
          <p class="party-name">{{ fatura.cliente.nome }}</p>
          <p class="party-detail">NIF: {{ fatura.cliente.nif }}</p>
          <p v-if="fatura.cliente.morada" class="party-detail">{{ fatura.cliente.morada }}</p>
        </div>
        <div class="party-block">
          <p class="party-label">Trotinete</p>
          <p class="party-name">{{ fatura.trotinete.marca }} {{ fatura.trotinete.modelo }}</p>
          <p class="party-detail">S/N: {{ fatura.trotinete.numero_serie }}</p>
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
            <td>{{ fatura.servico.descricao }}</td>
            <td class="val">{{ fmtEur(fatura.servico.preco_servico) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Parts table -->
      <template v-if="fatura.pecas_aplicadas.length > 0">
        <p class="section-label">Peças aplicadas</p>
        <table class="line-table">
          <thead>
            <tr>
              <th class="col-ref">Ref.</th>
              <th class="col-desc">Designação</th>
              <th class="col-qty">Qtd.</th>
              <th class="col-val">Preço unit.</th>
              <th class="col-val">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in fatura.pecas_aplicadas" :key="p.peca_referencia">
              <td class="mono ref">{{ p.peca_referencia }}</td>
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
          <span>{{ fmtEur(fatura.servico.preco_servico) }}</span>
        </div>
        <div v-if="fatura.pecas_aplicadas.length > 0" class="totals-row">
          <span>Peças</span>
          <span>{{ fmtEur(fatura.subtotal_pecas) }}</span>
        </div>
        <div class="totals-row totals-row--total">
          <span>Total</span>
          <span>{{ fmtEur(fatura.valor_final) }}</span>
        </div>
      </div>

      <!-- Footer note -->
      <p class="inv-footer">
        Fatura associada à OS
        <a class="os-link" @click="router.push(`/ordens-servico/${fatura.ordem_servico_id}`)">
          #{{ fatura.ordem_servico_id }}
        </a>
      </p>

    </div>
  </div>
</template>

<style scoped>
.page { padding: 2rem; max-width: 860px; }

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}
.back-btn {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}
.back-btn:hover { color: #111827; }
.btn-download {
  padding: 0.45rem 1rem;
  background: #f8fafc;
  border: 1px solid #d1d5db;
  border-radius: 7px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-download:hover { background: #f0fdf9; border-color: #1abc9c; color: #1abc9c; }

.loading-msg { color: #6b7280; font-size: 0.875rem; }
.error-msg   { color: #dc2626; font-size: 0.875rem; }

/* Invoice card */
.invoice {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.07);
  padding: 2.5rem;
}

/* Header */
.inv-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}
.inv-brand {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.brand {
  font-size: 1.5rem;
  font-weight: 800;
  color: #1abc9c;
  letter-spacing: -0.02em;
  line-height: 1;
  margin-bottom: 0.35rem;
}
.loja-nome { font-size: 0.9rem; font-weight: 600; color: #111827; }
.loja-info { font-size: 0.82rem; color: #6b7280; }

.inv-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.35rem;
}
.inv-numero {
  font-size: 1.1rem;
  font-weight: 700;
  color: #111827;
  font-family: 'Courier New', monospace;
}
.inv-data { font-size: 0.85rem; color: #6b7280; }

/* Divider */
.inv-divider {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 1.5rem 0;
}

/* Parties */
.inv-parties {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}
.party-block { display: flex; flex-direction: column; gap: 0.2rem; }
.party-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #9ca3af; margin-bottom: 0.15rem; }
.party-name  { font-size: 0.95rem; font-weight: 600; color: #111827; }
.party-detail{ font-size: 0.85rem; color: #6b7280; }

/* Section label */
.section-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #9ca3af;
  margin: 1.25rem 0 0.5rem;
}

/* Line tables */
.line-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}
.line-table th {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #6b7280;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
  background: #f9fafb;
}
.line-table td {
  padding: 0.7rem 0.75rem;
  color: #374151;
  border-bottom: 1px solid #f3f4f6;
}
.line-table tbody tr:last-child td { border-bottom: none; }

.col-ref  { width: 110px; }
.col-desc { width: auto; }
.col-qty  { width: 60px; }
.col-val  { width: 110px; text-align: right; }

.val    { text-align: right; font-variant-numeric: tabular-nums; }
.center { text-align: center; }
.ref    { font-family: 'Courier New', monospace; font-size: 0.82rem; color: #6b7280; }
.mono   { font-family: 'Courier New', monospace; font-size: 0.82rem; }

/* Totals */
.totals {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.4rem;
  padding: 0.5rem 0.75rem 0;
}
.totals-row {
  display: flex;
  gap: 3rem;
  font-size: 0.875rem;
  color: #374151;
  min-width: 220px;
  justify-content: space-between;
}
.totals-row span:last-child { font-variant-numeric: tabular-nums; }
.totals-row--total {
  border-top: 2px solid #111827;
  padding-top: 0.4rem;
  margin-top: 0.2rem;
  font-size: 1rem;
  font-weight: 700;
  color: #111827;
}

/* Footer */
.inv-footer {
  margin-top: 2rem;
  font-size: 0.8rem;
  color: #9ca3af;
  text-align: center;
}
.os-link {
  color: #1abc9c;
  cursor: pointer;
  font-weight: 600;
}
.os-link:hover { text-decoration: underline; }
</style>
