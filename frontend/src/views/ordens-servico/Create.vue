<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getClientes, createCliente } from '../../services/clientes.js'
import { createTrotinete } from '../../services/trotinetes.js'
import { createOrdemServico } from '../../services/ordensServico.js'
import { useAuthStore } from '../../store/auth.js'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const step = ref(1)
const error = ref('')
const loading = ref(false)

// ── Step 1: cliente ────────────────────────────────────────────
const clienteSearch = ref('')
const clienteResults = ref([])
const searchLoading = ref(false)
const clienteSelecionado = ref(null)
const criandoCliente = ref(false)
const novoCliente = ref({ nome: '', nif: '', telemovel: '', email: '', morada: '', consentimento_rgpd: false })

async function searchClientes() {
  if (!clienteSearch.value.trim()) return
  searchLoading.value = true
  error.value = ''
  try {
    const { data } = await getClientes({ query: clienteSearch.value.trim(), page_size: 10 })
    clienteResults.value = data.data
    if (clienteResults.value.length === 0) criandoCliente.value = true
  } catch {
    clienteResults.value = []
  } finally {
    searchLoading.value = false
  }
}

function selectCliente(c) {
  clienteSelecionado.value = c
  criandoCliente.value = false
  step.value = 2
}

async function createAndSelectCliente() {
  if (!novoCliente.value.consentimento_rgpd) {
    error.value = 'O consentimento RGPD é obrigatório.'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const { data } = await createCliente(novoCliente.value)
    clienteSelecionado.value = data.data
    step.value = 2
  } catch (e) {
    error.value = e.response?.data?.detail?.detail || 'Erro ao criar cliente.'
  } finally {
    loading.value = false
  }
}

// ── Step 2: trotinete ──────────────────────────────────────────
const trotSelecionada = ref(null)
const criandoTrot = ref(false)
const novaTrot = ref({ marca: '', modelo: '', numero_serie: '', ano_compra: '', cor: '' })

function selectTrot(t) {
  trotSelecionada.value = t
  criandoTrot.value = false
  step.value = 3
}

async function createAndSelectTrot() {
  loading.value = true
  error.value = ''
  try {
    const body = {
      cliente_id: clienteSelecionado.value.id,
      marca: novaTrot.value.marca,
      modelo: novaTrot.value.modelo,
      numero_serie: novaTrot.value.numero_serie,
    }
    if (novaTrot.value.ano_compra) body.ano_compra = parseInt(novaTrot.value.ano_compra)
    if (novaTrot.value.cor) body.cor = novaTrot.value.cor
    const { data } = await createTrotinete(body)
    trotSelecionada.value = data.data
    step.value = 3
  } catch (e) {
    error.value = e.response?.data?.detail?.detail || 'Erro ao registar trotinete.'
  } finally {
    loading.value = false
  }
}

// ── Step 3: OS details ─────────────────────────────────────────
const osForm = ref({
  descricao_problema: '',
  prioridade: 'NORMAL',
  preco_servico: '',
})

const PRIORIDADES = [
  { value: 'BAIXA', label: 'Baixa' },
  { value: 'NORMAL', label: 'Normal' },
  { value: 'ALTA', label: 'Alta' },
  { value: 'URGENTE', label: 'Urgente' },
]

async function submitOS() {
  if (!osForm.value.descricao_problema.trim() || !osForm.value.preco_servico) {
    error.value = 'Preencha todos os campos obrigatórios.'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const body = {
      trotinete_id: trotSelecionada.value.id,
      loja_id: auth.getCurrentUser.loja_id,
      descricao_problema: osForm.value.descricao_problema.trim(),
      prioridade: osForm.value.prioridade,
      preco_servico: parseFloat(osForm.value.preco_servico),
    }
    const { data } = await createOrdemServico(body)
    router.push(`/ordens-servico/${data.data.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail?.detail || 'Erro ao criar ordem de serviço.'
  } finally {
    loading.value = false
  }
}

// Pre-fill from query param
onMounted(async () => {
  const clienteId = route.query.cliente_id
  if (clienteId) {
    try {
      const { getCliente } = await import('../../services/clientes.js')
      const { data } = await getCliente(clienteId)
      clienteSelecionado.value = data.data
      step.value = 2
    } catch {
      // ignore
    }
  }
})
</script>

<template>
  <div class="page">
    <div class="back-row">
      <button class="btn-back" @click="router.push('/ordens-servico')">← Ordens de Serviço</button>
    </div>
    <h1 style="margin-bottom: 2rem">Nova Ordem de Serviço</h1>

    <!-- Step indicator -->
    <div class="steps">
      <div v-for="n in 3" :key="n" class="step-item" :class="{ active: step === n, done: step > n }">
        <div class="step-circle">{{ step > n ? '✓' : n }}</div>
        <span class="step-label">
          {{ n === 1 ? 'Cliente' : n === 2 ? 'Trotinete' : 'Detalhes' }}
        </span>
      </div>
      <div class="step-line" />
    </div>

    <div class="card form-card">
      <!-- ── Step 1 ── -->
      <template v-if="step === 1">
        <h2 class="step-title">Selecionar Cliente</h2>

        <div v-if="!criandoCliente">
          <div class="search-row">
            <input
              v-model="clienteSearch"
              placeholder="NIF ou telemóvel do cliente..."
              @keydown.enter="searchClientes"
            />
            <button class="btn btn--primary" :disabled="searchLoading" @click="searchClientes">
              {{ searchLoading ? '...' : 'Pesquisar' }}
            </button>
          </div>

          <div v-if="clienteResults.length > 0" class="results-list">
            <div
              v-for="c in clienteResults"
              :key="c.id"
              class="result-item"
              @click="selectCliente(c)"
            >
              <div class="result-name">{{ c.nome }}</div>
              <div class="result-sub">NIF {{ c.nif }} · {{ c.telemovel }}</div>
            </div>
          </div>

          <button class="btn-link-block" @click="criandoCliente = true">
            + Registar novo cliente
          </button>
        </div>

        <div v-else>
          <div class="back-link" @click="criandoCliente = false">← Voltar à pesquisa</div>
          <div class="form-grid">
            <div class="field field--full">
              <label>Nome completo *</label>
              <input v-model="novoCliente.nome" required placeholder="João Silva" />
            </div>
            <div class="field">
              <label>NIF *</label>
              <input v-model="novoCliente.nif" required placeholder="123456789" maxlength="9" />
            </div>
            <div class="field">
              <label>Telemóvel *</label>
              <input v-model="novoCliente.telemovel" required placeholder="912345678" maxlength="9" />
            </div>
            <div class="field">
              <label>Email</label>
              <input v-model="novoCliente.email" type="email" placeholder="joao@email.com" />
            </div>
            <div class="field">
              <label>Morada</label>
              <input v-model="novoCliente.morada" placeholder="Rua das Flores 10, Lisboa" />
            </div>
            <div class="field field--full">
              <label class="rgpd-check">
                <input type="checkbox" v-model="novoCliente.consentimento_rgpd" />
                <span>Consentimento RGPD *</span>
              </label>
            </div>
            <p v-if="error" class="form-error field--full">{{ error }}</p>
            <div class="field--full step-actions">
              <button class="btn btn--primary" :disabled="loading" @click="createAndSelectCliente">
                {{ loading ? 'A criar...' : 'Criar e Continuar →' }}
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- ── Step 2 ── -->
      <template v-else-if="step === 2">
        <h2 class="step-title">Selecionar Trotinete</h2>
        <p class="step-sub">Cliente: <strong>{{ clienteSelecionado?.nome }}</strong></p>

        <div v-if="!criandoTrot">
          <div
            v-if="clienteSelecionado?.trotinetes?.length > 0"
            class="results-list"
          >
            <div
              v-for="t in clienteSelecionado.trotinetes"
              :key="t.id"
              class="result-item"
              @click="selectTrot(t)"
            >
              <div class="result-name">{{ t.marca }} {{ t.modelo }}</div>
              <div class="result-sub mono">{{ t.numero_serie }}</div>
            </div>
          </div>
          <div v-else class="empty-hint">Este cliente não tem trotinetes registadas.</div>

          <button class="btn-link-block" @click="criandoTrot = true">
            + Registar nova trotinete
          </button>
          <button class="btn btn--ghost btn--sm" style="margin-top:0.5rem" @click="step = 1">← Voltar</button>
        </div>

        <div v-else>
          <div class="back-link" @click="criandoTrot = false">← Voltar à lista</div>
          <div class="form-grid">
            <div class="field">
              <label>Marca *</label>
              <input v-model="novaTrot.marca" required placeholder="Xiaomi" />
            </div>
            <div class="field">
              <label>Modelo *</label>
              <input v-model="novaTrot.modelo" required placeholder="Mi Electric Scooter 3" />
            </div>
            <div class="field field--full">
              <label>Número de Série *</label>
              <input v-model="novaTrot.numero_serie" required placeholder="XM2024ABC123" />
            </div>
            <div class="field">
              <label>Ano de Compra</label>
              <input v-model="novaTrot.ano_compra" type="number" placeholder="2024" min="2000" max="2100" />
            </div>
            <div class="field">
              <label>Cor</label>
              <input v-model="novaTrot.cor" placeholder="Preto" />
            </div>
            <p v-if="error" class="form-error field--full">{{ error }}</p>
            <div class="field--full step-actions">
              <button class="btn btn--primary" :disabled="loading" @click="createAndSelectTrot">
                {{ loading ? 'A registar...' : 'Registar e Continuar →' }}
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- ── Step 3 ── -->
      <template v-else>
        <h2 class="step-title">Detalhes da Ordem de Serviço</h2>
        <div class="summary-chips">
          <span class="chip">{{ clienteSelecionado?.nome }}</span>
          <span class="chip mono">{{ trotSelecionada?.numero_serie }}</span>
          <span class="chip-sub">{{ trotSelecionada?.marca }} {{ trotSelecionada?.modelo }}</span>
        </div>

        <div class="form-grid" style="margin-top: 1.25rem">
          <div class="field field--full">
            <label>Descrição do problema *</label>
            <textarea
              v-model="osForm.descricao_problema"
              rows="4"
              placeholder="Descreva o problema reportado pelo cliente..."
            />
          </div>
          <div class="field">
            <label>Prioridade *</label>
            <select v-model="osForm.prioridade">
              <option v-for="p in PRIORIDADES" :key="p.value" :value="p.value">{{ p.label }}</option>
            </select>
          </div>
          <div class="field">
            <label>Preço do serviço (€) *</label>
            <input
              v-model="osForm.preco_servico"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
            />
          </div>
          <p v-if="error" class="form-error field--full">{{ error }}</p>
          <div class="field--full step-actions">
            <button class="btn btn--ghost btn--sm" @click="step = 2">← Voltar</button>
            <button class="btn btn--primary" :disabled="loading" @click="submitOS">
              {{ loading ? 'A criar...' : 'Criar Ordem de Serviço' }}
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 2rem; max-width: 680px; }

.back-row { margin-bottom: 1rem; }
.btn-back {
  background: none; border: none;
  color: #1abc9c; font-size: 0.9rem; font-weight: 500;
  cursor: pointer; padding: 0;
}
.btn-back:hover { text-decoration: underline; }

/* Steps */
.steps {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 2rem;
  position: relative;
}
.step-line {
  position: absolute;
  top: 18px;
  left: 18px;
  right: 18px;
  height: 2px;
  background: #e5e7eb;
  z-index: 0;
}
.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  flex: 1;
  position: relative;
  z-index: 1;
}
.step-circle {
  width: 36px; height: 36px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.9rem;
  background: #e5e7eb; color: #6b7280;
  border: 2px solid #e5e7eb;
  transition: all 0.2s;
}
.step-item.active .step-circle {
  background: #1abc9c; color: #fff; border-color: #1abc9c;
}
.step-item.done .step-circle {
  background: #d1fae5; color: #065f46; border-color: #6ee7b7;
}
.step-label { font-size: 0.8rem; font-weight: 500; color: #6b7280; }
.step-item.active .step-label { color: #1abc9c; }

.card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  padding: 2rem;
}

.step-title { margin-bottom: 1.25rem; }
.step-sub { color: #6b7280; font-size: 0.9rem; margin-bottom: 1rem; }

/* Search */
.search-row {
  display: flex; gap: 0.75rem; margin-bottom: 1rem;
}
.search-row input { flex: 1; }

.results-list {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 1rem;
  overflow: hidden;
}
.result-item {
  padding: 0.9rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.1s;
}
.result-item:last-child { border-bottom: none; }
.result-item:hover { background: #f0fdf4; }
.result-name { font-weight: 600; color: #111827; }
.result-sub { font-size: 0.82rem; color: #6b7280; margin-top: 0.15rem; }

.btn-link-block {
  display: block;
  background: none; border: 1px dashed #d1d5db;
  color: #1abc9c; font-size: 0.875rem; font-weight: 500;
  cursor: pointer; padding: 0.65rem 1rem;
  border-radius: 6px; width: 100%;
  text-align: left; margin-top: 0.5rem;
  transition: border-color 0.15s;
}
.btn-link-block:hover { border-color: #1abc9c; }

.back-link {
  color: #6b7280; font-size: 0.875rem;
  cursor: pointer; margin-bottom: 1rem;
}
.back-link:hover { color: #374151; }

.empty-hint { color: #6b7280; font-size: 0.9rem; margin-bottom: 0.75rem; }

/* Form */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.field { display: flex; flex-direction: column; }
.field--full { grid-column: 1 / -1; }

.rgpd-check {
  display: flex; align-items: flex-start; gap: 0.5rem;
  cursor: pointer; font-size: 0.875rem; font-weight: 400;
  color: #374151; margin-bottom: 0;
}
.rgpd-check input { width: auto; margin-top: 3px; }

.step-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

/* Summary chips */
.summary-chips {
  display: flex; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;
}
.chip {
  background: #f0fdf4; color: #065f46;
  border: 1px solid #6ee7b7;
  padding: 0.2rem 0.75rem; border-radius: 999px;
  font-size: 0.82rem; font-weight: 600;
}
.chip-sub { color: #6b7280; font-size: 0.82rem; }

.form-error { color: #dc2626; font-size: 0.85rem; }

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
.btn--ghost { background: transparent; border: 1px solid #d1d5db; color: #374151; }
.btn--sm { padding: 0.4rem 0.8rem; font-size: 0.825rem; }

.mono { font-family: 'Courier New', monospace; font-size: 0.85rem; }
</style>
