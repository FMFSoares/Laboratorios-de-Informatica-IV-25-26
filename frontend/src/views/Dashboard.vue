<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth.js'
import { getDashboard } from '../services/dashboard.js'
import LoadingSpinner from '../components/ui/LoadingSpinner.vue'

const router = useRouter()
const auth   = useAuthStore()
const perfil = auth.getCurrentUser?.perfil

const isAdmin  = computed(() => perfil === 'ADMINISTRADOR')
const isGestao = computed(() => ['ADMINISTRADOR', 'GERENTE_LOJA'].includes(perfil))

// ── Date range ─────────────────────────────────────────────────────────────
const preset      = ref('30')
const customStart = ref('')
const customEnd   = ref('')

function todayStr() {
  return new Date().toISOString().slice(0, 10)
}
function subtractDays(n) {
  const d = new Date()
  d.setDate(d.getDate() - n)
  return d.toISOString().slice(0, 10)
}

const queryParams = computed(() => {
  if (preset.value === 'custom' && customStart.value && customEnd.value) {
    return { data_inicio: customStart.value, data_fim: customEnd.value }
  }
  const days = preset.value === '90' ? 90 : 30
  return { data_inicio: subtractDays(days), data_fim: todayStr() }
})

// ── Data ──────────────────────────────────────────────────────────────────
const data    = ref(null)
const loading = ref(true)
const erro    = ref('')

async function load() {
  loading.value = true
  erro.value    = ''
  try {
    const res = await getDashboard(queryParams.value)
    data.value = res.data.data
  } catch {
    erro.value = 'Erro ao carregar o dashboard.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

// ── Derived values ─────────────────────────────────────────────────────────
const ACTIVE_STATES = ['PENDENTE', 'EM_DIAGNOSTICO', 'AGUARDA_APROVACAO', 'EM_REPARACAO', 'AGUARDA_PECAS']

const osAtivas = computed(() => {
  if (!data.value) return 0
  return ACTIVE_STATES.reduce((sum, s) => sum + (data.value.ordens_por_estado[s] ?? 0), 0)
})

const alertCount = computed(() => data.value?.pecas_abaixo_stock_minimo?.length ?? 0)

const maxLojaTotal = computed(() => {
  if (!data.value?.ordens_concluidas_por_loja?.length) return 1
  return Math.max(...data.value.ordens_concluidas_por_loja.map(l => l.total), 1)
})

function fmtEur(v) {
  return v != null
    ? Number(v).toLocaleString('pt-PT', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €'
    : '—'
}

function fmtMin(m) {
  if (m == null) return '—'
  const h   = Math.floor(m / 60)
  const min = m % 60
  if (h === 0) return `${min}min`
  return min === 0 ? `${h}h` : `${h}h ${min}min`
}

const ESTADO_CONFIG = {
  PENDENTE:          { label: 'Pendente',          color: '#6b7280', bg: '#f3f4f6' },
  EM_DIAGNOSTICO:    { label: 'Em Diagnóstico',    color: '#2563eb', bg: '#dbeafe' },
  AGUARDA_APROVACAO: { label: 'Aguarda Aprovação', color: '#d97706', bg: '#fef3c7' },
  EM_REPARACAO:      { label: 'Em Reparação',      color: '#7c3aed', bg: '#ede9fe' },
  AGUARDA_PECAS:     { label: 'Aguarda Peças',     color: '#dc2626', bg: '#fee2e2' },
  CONCLUIDA:         { label: 'Concluída',         color: '#059669', bg: '#d1fae5' },
  FATURADA:          { label: 'Faturada',          color: '#0f766e', bg: '#ccfbf1' },
  CANCELADA:         { label: 'Cancelada',         color: '#9ca3af', bg: '#f9fafb' },
}

const estadoEntries = computed(() => {
  if (!data.value) return []
  return Object.entries(data.value.ordens_por_estado)
    .map(([estado, count]) => ({ estado, count, ...(ESTADO_CONFIG[estado] ?? { label: estado, color: '#374151', bg: '#f3f4f6' }) }))
})

const totalOS = computed(() => estadoEntries.value.reduce((s, e) => s + e.count, 0))
</script>

<template>
  <div class="page">
    <!-- ── Header ─────────────────────────────────────────────────────── -->
    <div class="page-header">
      <div>
        <h1>Dashboard</h1>
        <p class="subtitle">Bem-vindo, {{ auth.getCurrentUser?.nome?.split(' ')[0] }}.</p>
      </div>

      <div class="date-filter">
        <div class="preset-tabs">
          <button
            v-for="p in [['30', '30 dias'], ['90', '90 dias'], ['custom', 'Personalizado']]"
            :key="p[0]"
            :class="['preset-tab', preset === p[0] && 'preset-tab--active']"
            @click="preset = p[0]; if (p[0] !== 'custom') load()"
          >{{ p[1] }}</button>
        </div>
        <div v-if="preset === 'custom'" class="custom-range">
          <input type="date" v-model="customStart" :max="customEnd || todayStr()" />
          <span class="range-arrow">→</span>
          <input type="date" v-model="customEnd"   :min="customStart" :max="todayStr()" />
          <button class="btn btn--primary btn--sm" :disabled="!customStart || !customEnd" @click="load">Aplicar</button>
        </div>
      </div>
    </div>

    <LoadingSpinner v-if="loading" />
    <p v-else-if="erro" class="error-msg">{{ erro }}</p>

    <template v-else-if="data">

      <!-- ── KPI Cards ───────────────────────────────────────────────── -->
      <div :class="['kpi-grid', isGestao && 'kpi-grid--5']">
        <div class="kpi-card">
          <div class="kpi-label">Faturação</div>
          <div class="kpi-value kpi-value--green">{{ fmtEur(data.faturacao_total) }}</div>
          <div class="kpi-sub">no período</div>
        </div>

        <div v-if="isGestao" class="kpi-card kpi-card--lucro">
          <div class="kpi-label">Lucro Líquido</div>
          <div class="kpi-value kpi-value--lucro">{{ fmtEur(data.lucro_liquido_total) }}</div>
          <div class="kpi-sub">após custo de peças</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-label">OS Ativas</div>
          <div class="kpi-value">{{ osAtivas }}</div>
          <div class="kpi-sub">em curso</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-label">Tempo Médio</div>
          <div class="kpi-value">{{ fmtMin(data.tempo_medio_reparacao_minutos) }}</div>
          <div class="kpi-sub">por reparação</div>
        </div>

        <div class="kpi-card" :class="alertCount > 0 && 'kpi-card--alert'">
          <div class="kpi-label">Alertas de Stock</div>
          <div class="kpi-value" :class="alertCount > 0 ? 'kpi-value--red' : 'kpi-value--green'">{{ alertCount }}</div>
          <div class="kpi-sub">{{ alertCount === 1 ? 'peça abaixo do mínimo' : 'peças abaixo do mínimo' }}</div>
        </div>
      </div>

      <!-- ── OS por estado ───────────────────────────────────────────── -->
      <div class="card">
        <div class="card-title">Ordens de Serviço por Estado</div>
        <div v-if="totalOS === 0" class="empty-msg">Sem ordens no período selecionado.</div>
        <div v-else class="estado-grid">
          <div
            v-for="e in estadoEntries"
            :key="e.estado"
            class="estado-chip"
            :style="{ background: e.bg, color: e.color, borderColor: e.color + '33' }"
          >
            <span class="estado-count">{{ e.count }}</span>
            <span class="estado-label">{{ e.label }}</span>
          </div>
        </div>
      </div>

      <!-- ── Bottom row ──────────────────────────────────────────────── -->
      <div v-if="isGestao" class="bottom-grid">

        <!-- Admin: Faturação por Loja -->
        <div v-if="isAdmin" class="card">
          <div class="card-title">Faturação e Lucro por Loja</div>
          <div v-if="!data.faturacao_por_loja?.length" class="empty-msg">Sem faturação no período.</div>
          <div v-else class="fat-list">
            <div
              v-for="l in data.faturacao_por_loja"
              :key="l.loja_id"
              class="fat-block"
            >
              <div class="fat-loja">{{ l.loja_nome }}</div>
              <div class="fat-bars-col">
                <div class="fat-bar-item">
                  <span class="fat-bar-label">Faturação</span>
                  <div class="fat-bar-wrap">
                    <div
                      class="fat-bar-fill fat-bar-fill--rev"
                      :style="{ width: `${Math.max(2, (l.faturacao_total / Math.max(...data.faturacao_por_loja.map(x => x.faturacao_total), 1)) * 100)}%` }"
                    ></div>
                  </div>
                  <div class="fat-value">{{ fmtEur(l.faturacao_total) }}</div>
                </div>
                <div class="fat-bar-item">
                  <span class="fat-bar-label fat-bar-label--lucro">Lucro</span>
                  <div class="fat-bar-wrap">
                    <div
                      class="fat-bar-fill fat-bar-fill--lucro"
                      :style="{ width: `${Math.max(2, (l.lucro_liquido / Math.max(...data.faturacao_por_loja.map(x => x.faturacao_total), 1)) * 100)}%` }"
                    ></div>
                  </div>
                  <div class="fat-value fat-value--lucro">{{ fmtEur(l.lucro_liquido) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Gerente: Eficiência por Mecânico -->
        <div v-else class="card">
          <div class="card-title">Eficiência por Mecânico</div>
          <div v-if="!data.eficiencia_por_mecanico?.length" class="empty-msg">Sem dados no período.</div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>Mecânico</th>
                <th class="col-num">OS Concluídas</th>
                <th class="col-num">Tempo Médio</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="m in [...data.eficiencia_por_mecanico].sort((a, b) => b.ordens_concluidas - a.ordens_concluidas)"
                :key="m.mecanico_id"
              >
                <td class="mecanico-nome">{{ m.nome }}</td>
                <td class="col-num"><span class="os-count">{{ m.ordens_concluidas }}</span></td>
                <td class="col-num tempo-cell">{{ fmtMin(m.tempo_medio_minutos) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Alertas de stock -->
        <div class="card">
          <div class="card-title">Alertas de Stock</div>
          <div v-if="data.pecas_abaixo_stock_minimo.length === 0" class="empty-msg ok-msg">
            Tudo normalizado. Sem alertas ativos.
          </div>
          <div v-else class="alert-list">
            <div
              v-for="a in data.pecas_abaixo_stock_minimo"
              :key="`${a.peca_id}-${a.loja_id}`"
              class="alert-row"
              @click="router.push(`/pecas/${a.peca_id}`)"
            >
              <div class="alert-info">
                <div class="alert-peca">{{ a.peca_nome }}</div>
                <div class="alert-loja">{{ a.loja_nome }}</div>
              </div>
              <div class="alert-qty">
                <span class="qty-current" :class="a.quantidade === 0 && 'qty--zero'">{{ a.quantidade }}</span>
                <span class="qty-sep">/</span>
                <span class="qty-min">{{ a.limite_minimo }}</span>
              </div>
              <span v-if="a.quantidade === 0" class="sbadge sbadge--esgotado">Esgotado</span>
              <span v-else                     class="sbadge sbadge--alerta">Alerta</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Ordens por loja (admin only) ───────────────────────────── -->
      <div v-if="isAdmin && data.ordens_concluidas_por_loja.length > 0" class="card">
        <div class="card-title">OS Concluídas por Loja</div>
        <div class="loja-bars">
          <div v-for="l in data.ordens_concluidas_por_loja" :key="l.loja_id" class="loja-bar-row">
            <div class="loja-bar-name">{{ l.loja_nome }}</div>
            <div class="loja-bar-track">
              <div
                class="loja-bar-fill"
                :style="{ width: `${Math.max(2, (l.total / maxLojaTotal) * 100)}%` }"
              ></div>
            </div>
            <div class="loja-bar-total">{{ l.total }}</div>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<style scoped>
.page { padding: 2rem; display: flex; flex-direction: column; gap: 1.5rem; }

/* ── Header ──────────────────────────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}
.page-header h1 { margin: 0; font-size: 1.6rem; color: #111827; }
.subtitle { margin: 0.2rem 0 0; font-size: 0.9rem; color: #6b7280; }

/* ── Date filter ─────────────────────────────────────────────────────────── */
.date-filter { display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem; }

.preset-tabs { display: flex; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; }
.preset-tab {
  padding: 0.45rem 1rem;
  background: #fff;
  border: none;
  font-size: 0.85rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  border-right: 1px solid #e5e7eb;
  transition: background 0.12s, color 0.12s;
}
.preset-tab:last-child { border-right: none; }
.preset-tab:hover { background: #f9fafb; color: #374151; }
.preset-tab--active { background: #1abc9c; color: #fff; font-weight: 600; }
.preset-tab--active:hover { background: #17a589; }

.custom-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}
.custom-range input[type="date"] {
  padding: 0.4rem 0.65rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #374151;
  outline: none;
}
.custom-range input[type="date"]:focus { border-color: #1abc9c; }
.range-arrow { color: #9ca3af; }

/* ── KPI Grid ────────────────────────────────────────────────────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}
.kpi-grid--5 { grid-template-columns: repeat(5, 1fr); }
@media (max-width: 1100px) { .kpi-grid--5 { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 900px)  { .kpi-grid, .kpi-grid--5 { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 500px)  { .kpi-grid, .kpi-grid--5 { grid-template-columns: 1fr; } }

.kpi-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-left: 3px solid transparent;
}
.kpi-card--alert { border-left-color: #f59e0b; background: #fffbeb; }
.kpi-card--lucro { border-left-color: #7c3aed; }

.kpi-label { font-size: 0.75rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-value { font-size: 1.75rem; font-weight: 700; color: #111827; line-height: 1.1; margin: 0.25rem 0; }
.kpi-value--green { color: #1abc9c; }
.kpi-value--red   { color: #dc2626; }
.kpi-value--lucro { color: #7c3aed; }
.kpi-sub  { font-size: 0.78rem; color: #9ca3af; }

/* ── Card ────────────────────────────────────────────────────────────────── */
.card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  padding: 1.5rem;
}
.card-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1.25rem;
}

/* ── Estado chips ────────────────────────────────────────────────────────── */
.estado-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 0.6rem;
}
@media (max-width: 900px) { .estado-grid { grid-template-columns: repeat(4, 1fr); } }
@media (max-width: 500px) { .estado-grid { grid-template-columns: repeat(2, 1fr); } }
.estado-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  padding: 0.6rem 0.4rem;
  border-radius: 8px;
  border: 1px solid transparent;
  text-align: center;
}
.estado-count { font-size: 1.4rem; font-weight: 700; line-height: 1; }
.estado-label { font-size: 0.72rem; font-weight: 600; line-height: 1.25; }

/* ── Bottom grid ─────────────────────────────────────────────────────────── */
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}
@media (max-width: 760px) { .bottom-grid { grid-template-columns: 1fr; } }

/* ── Mechanic efficiency table ───────────────────────────────────────────── */
.table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.table th { text-align: left; font-size: 0.72rem; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.04em; padding: 0 0 0.65rem; border-bottom: 1px solid #f3f4f6; }
.table td { padding: 0.75rem 0; border-bottom: 1px solid #f9fafb; color: #374151; vertical-align: middle; }
.table tbody tr:last-child td { border-bottom: none; }
.col-num { text-align: right; }
.mecanico-nome { font-weight: 500; color: #111827; }
.os-count { font-weight: 700; color: #1abc9c; }
.tempo-cell { color: #6b7280; font-size: 0.85rem; }

/* ── Faturação por loja ──────────────────────────────────────────────────── */
.fat-list  { display: flex; flex-direction: column; gap: 1.1rem; }
.fat-block { display: flex; align-items: flex-start; gap: 0.9rem; }
.fat-loja  { font-size: 0.875rem; font-weight: 600; color: #374151; min-width: 130px; padding-top: 0.2rem; }
.fat-bars-col { flex: 1; display: flex; flex-direction: column; gap: 0.45rem; }
.fat-bar-item { display: flex; align-items: center; gap: 0.6rem; }
.fat-bar-label {
  font-size: 0.72rem; font-weight: 600; color: #6b7280;
  width: 72px; flex-shrink: 0; text-align: right; text-transform: uppercase; letter-spacing: 0.03em;
}
.fat-bar-label--lucro { color: #7c3aed; }
.fat-bar-wrap {
  flex: 1;
  height: 8px;
  background: #f3f4f6;
  border-radius: 9999px;
  overflow: hidden;
}
.fat-bar-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.4s ease;
}
.fat-bar-fill--rev   { background: #1abc9c; }
.fat-bar-fill--lucro { background: #7c3aed; }
.fat-value { font-size: 0.875rem; font-weight: 700; color: #111827; min-width: 90px; text-align: right; }
.fat-value--lucro { color: #7c3aed; }

/* ── Stock alerts ────────────────────────────────────────────────────────── */
.alert-list { display: flex; flex-direction: column; gap: 0.5rem; }
.alert-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: background 0.1s;
}
.alert-row:hover { background: #f9fafb; }
.alert-info { flex: 1; min-width: 0; }
.alert-peca { font-size: 0.875rem; font-weight: 600; color: #111827; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.alert-loja { font-size: 0.75rem; color: #6b7280; }
.alert-qty  { display: flex; align-items: baseline; gap: 0.2rem; flex-shrink: 0; }
.qty-current { font-size: 1.1rem; font-weight: 700; color: #111827; }
.qty--zero   { color: #9ca3af; }
.qty-sep     { font-size: 0.85rem; color: #9ca3af; }
.qty-min     { font-size: 0.85rem; color: #9ca3af; }

.sbadge { display: inline-block; padding: 0.2rem 0.55rem; border-radius: 9999px; font-size: 0.72rem; font-weight: 600; flex-shrink: 0; }
.sbadge--alerta   { background: #fef3c7; color: #92400e; }
.sbadge--esgotado { background: #f3f4f6; color: #6b7280; }

/* ── Loja bars ───────────────────────────────────────────────────────────── */
.loja-bars { display: flex; flex-direction: column; gap: 0.9rem; }
.loja-bar-row { display: flex; align-items: center; gap: 1rem; }
.loja-bar-name  { font-size: 0.875rem; font-weight: 500; color: #374151; min-width: 150px; }
.loja-bar-track {
  flex: 1;
  height: 10px;
  background: #f3f4f6;
  border-radius: 9999px;
  overflow: hidden;
}
.loja-bar-fill {
  height: 100%;
  background: #1abc9c;
  border-radius: 9999px;
  transition: width 0.4s ease;
}
.loja-bar-total { font-size: 0.875rem; font-weight: 700; color: #111827; min-width: 28px; text-align: right; }

/* ── Misc ────────────────────────────────────────────────────────────────── */
.empty-msg { color: #9ca3af; font-size: 0.875rem; }
.ok-msg    { color: #059669; }
.error-msg { color: #dc2626; font-size: 0.9rem; }

.btn { padding: 0.6rem 1.2rem; border: none; border-radius: 6px; font-size: 0.875rem; font-weight: 600; cursor: pointer; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--sm { padding: 0.4rem 0.8rem; font-size: 0.825rem; }
</style>
