<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api.js'

const hoje = new Date()
const ano = ref(hoje.getFullYear())
const mes = ref(hoje.getMonth() + 1)

const salarios = ref([])
const loading = ref(false)
const error = ref(null)

const MESES = [
  'Janeiro','Fevereiro','Março','Abril','Maio','Junho',
  'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro',
]

const PERFIL_LABEL = {
  ADMINISTRADOR: 'Administrador',
  GERENTE_LOJA: 'Gerente de Loja',
  RECECIONISTA: 'Rececionista',
  MECANICO: 'Mecânico',
}

async function carregar() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get('/salarios', { params: { ano: ano.value, mes: mes.value } })
    salarios.value = res.data.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erro ao carregar salários.'
  } finally {
    loading.value = false
  }
}

onMounted(carregar)

const totalMassa = computed(() =>
  salarios.value.reduce((s, w) => s + w.total, 0)
)

function fmt(val) {
  return val.toLocaleString('pt-PT', { style: 'currency', currency: 'EUR' })
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Salários</h1>
    </div>

    <!-- Period picker -->
    <div class="filters card">
      <div class="filter-group">
        <label>Mês</label>
        <select v-model="mes">
          <option v-for="(label, i) in MESES" :key="i+1" :value="i+1">{{ label }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Ano</label>
        <input type="number" v-model.number="ano" min="2020" max="2100" />
      </div>
      <button class="btn btn--primary" @click="carregar" :disabled="loading">
        {{ loading ? 'A calcular…' : 'Calcular' }}
      </button>
    </div>

    <div v-if="error" class="alert-error">{{ error }}</div>

    <div v-if="!loading && salarios.length" class="card table-card">
      <table class="table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Perfil</th>
            <th>Loja</th>
            <th class="num">Salário Base</th>
            <th class="num">Comissão (%)</th>
            <th class="num">Comissão Ganha</th>
            <th class="num total-col">Total</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="w in salarios" :key="w.id">
            <td class="nome">{{ w.nome }}</td>
            <td><span class="badge" :class="'badge--' + w.perfil.toLowerCase()">{{ PERFIL_LABEL[w.perfil] ?? w.perfil }}</span></td>
            <td>{{ w.loja_nome ?? '—' }}</td>
            <td class="num">{{ fmt(w.salario_base) }}</td>
            <td class="num">{{ w.comissao_percentagem != null ? w.comissao_percentagem + '%' : '—' }}</td>
            <td class="num">{{ w.comissao_ganha > 0 ? fmt(w.comissao_ganha) : '—' }}</td>
            <td class="num total-col"><strong>{{ fmt(w.total) }}</strong></td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="footer-row">
            <td colspan="6" class="footer-label">Massa salarial total</td>
            <td class="num total-col"><strong>{{ fmt(totalMassa) }}</strong></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div v-else-if="!loading && !error" class="empty">
      Nenhum colaborador encontrado para o período selecionado.
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 2rem;
  max-width: 1100px;
}
.page-header {
  margin-bottom: 1.5rem;
}
.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,.07);
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.5rem;
}

.filters {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  flex-wrap: wrap;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.filter-group label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: .04em;
}
.filter-group select,
.filter-group input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color .15s;
}
.filter-group select:focus,
.filter-group input:focus { border-color: #1abc9c; }
.filter-group input { width: 100px; }

.btn {
  padding: 0.55rem 1.25rem;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity .15s;
}
.btn:disabled { opacity: .6; cursor: not-allowed; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--primary:hover:not(:disabled) { opacity: .88; }

.alert-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  border-radius: 8px;
  padding: .75rem 1rem;
  font-size: .875rem;
  margin-bottom: 1rem;
}

.table-card { padding: 0; overflow: hidden; }
.table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.table th {
  background: #f9fafb;
  padding: .75rem 1rem;
  text-align: left;
  font-size: .72rem;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: .05em;
  border-bottom: 1px solid #f3f4f6;
}
.table th.num { text-align: right; }
.table td {
  padding: .75rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  color: #374151;
}
.table tbody tr:last-child td { border-bottom: none; }
.table tbody tr:hover { background: #f9fafb; }
.table td.num { text-align: right; }
.table td.nome { font-weight: 500; color: #111827; }
.total-col { min-width: 110px; }

.badge {
  display: inline-block;
  padding: .2rem .6rem;
  border-radius: 99px;
  font-size: .72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .04em;
}
.badge--administrador { background: #fef3c7; color: #92400e; }
.badge--gerente_loja  { background: #ede9fe; color: #5b21b6; }
.badge--rececionista  { background: #dbeafe; color: #1d4ed8; }
.badge--mecanico      { background: #d1fae5; color: #065f46; }

tfoot .footer-row td {
  padding: .8rem 1rem;
  background: #f9fafb;
  font-size: .875rem;
  border-top: 2px solid #e5e7eb;
}
.footer-label {
  text-align: right;
  color: #6b7280;
  font-weight: 600;
}

.empty {
  text-align: center;
  padding: 3rem;
  color: #9ca3af;
  font-size: .9rem;
}
</style>
