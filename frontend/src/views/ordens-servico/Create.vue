<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getClientes, getCliente, createCliente } from '../../services/clientes.js'
import { getTrotinetes, createTrotinete } from '../../services/trotinetes.js'
import { createOrdemServico } from '../../services/ordensServico.js'
import { getLojas } from '../../services/lojas.js'
import { useAuthStore } from '../../store/auth.js'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const isAdmin = auth.getCurrentUser?.perfil === 'ADMINISTRADOR'

const step = ref(1)
const error = ref('')
const loading = ref(false)

// ── Loja selection (ADMINISTRADOR only) ───────────────────────
const lojas = ref([])
const lojaIdSelecionada = ref(null)

if (isAdmin) {
  getLojas({ page_size: 100 }).then(({ data }) => {
    lojas.value = data.data ?? []
  }).catch(() => {})
}

// ── Step 1: cliente autocomplete ───────────────────────────────
const clienteSearch = ref('')
const clienteResults = ref([])
const searchLoading = ref(false)
const showDropdown = ref(false)
const focusedIdx = ref(-1)
const clienteSelecionado = ref(null)
const criandoCliente = ref(false)
const novoCliente = ref({ nome: '', nif: '', telemovel: '', email: '', morada: '', consentimento_rgpd: false })

const comboRef = ref(null)
let debounceTimer = null

function onSearchInput() {
  clienteSelecionado.value = null
  focusedIdx.value = -1
  clearTimeout(debounceTimer)
  if (clienteSearch.value.trim().length < 2) {
    clienteResults.value = []
    showDropdown.value = false
    return
  }
  searchLoading.value = true
  showDropdown.value = true
  debounceTimer = setTimeout(async () => {
    try {
      const { data } = await getClientes({ query: clienteSearch.value.trim(), page_size: 8 })
      clienteResults.value = data.data ?? []
    } catch {
      clienteResults.value = []
    } finally {
      searchLoading.value = false
    }
  }, 300)
}

function onSearchFocus() {
  if (clienteSearch.value.trim().length >= 2) showDropdown.value = true
}

function onKeyDown(e) {
  if (!showDropdown.value) return
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    focusedIdx.value = Math.min(focusedIdx.value + 1, clienteResults.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    focusedIdx.value = Math.max(focusedIdx.value - 1, -1)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (focusedIdx.value >= 0 && clienteResults.value[focusedIdx.value]) {
      selectCliente(clienteResults.value[focusedIdx.value])
    }
  } else if (e.key === 'Escape') {
    showDropdown.value = false
  }
}

function onClickOutside(e) {
  if (comboRef.value && !comboRef.value.contains(e.target)) {
    showDropdown.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', onClickOutside))

async function selectCliente(c) {
  clienteSelecionado.value = c
  clienteSearch.value = c.nome
  showDropdown.value = false
  criandoCliente.value = false
  await fetchTrotinetes(c.id)
  step.value = 2
}

function clearSelection() {
  clienteSelecionado.value = null
  clienteSearch.value = ''
  clienteResults.value = []
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
    clienteTrotinetes.value = []
    step.value = 2
  } catch (e) {
    error.value = e.response?.data?.detail?.detail || 'Erro ao criar cliente.'
  } finally {
    loading.value = false
  }
}

// ── Step 2: trotinete ──────────────────────────────────────────
const clienteTrotinetes = ref([])
const trotSelecionada = ref(null)
const criandoTrot = ref(false)
const novaTrot = ref({ marca: '', modelo: '', numero_serie: '', ano_compra: '', cor: '' })

async function fetchTrotinetes(clienteId) {
  clienteTrotinetes.value = []
  try {
    const { data } = await getTrotinetes({ cliente_id: clienteId, page_size: 100 })
    clienteTrotinetes.value = data.data ?? []
  } catch {
    clienteTrotinetes.value = []
  }
}

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
})

const PRIORIDADES = [
  { value: 'BAIXA', label: 'Baixa' },
  { value: 'NORMAL', label: 'Normal' },
  { value: 'ALTA', label: 'Alta' },
  { value: 'URGENTE', label: 'Urgente' },
]

async function submitOS() {
  if (!osForm.value.descricao_problema.trim()) {
    error.value = 'Preencha a descrição do problema.'
    return
  }
  const lojaId = isAdmin ? lojaIdSelecionada.value : auth.getCurrentUser.loja_id
  if (!lojaId) {
    error.value = 'Selecione uma loja antes de continuar.'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const body = {
      trotinete_id: trotSelecionada.value.id,
      loja_id: lojaId,
      descricao_problema: osForm.value.descricao_problema.trim(),
      prioridade: osForm.value.prioridade,
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
      const { data } = await getCliente(clienteId)
      clienteSelecionado.value = data.data
      clienteSearch.value = data.data.nome
      await fetchTrotinetes(clienteId)
      step.value = 2
    } catch {
      // ignore
    }
  }
})
</script>

<template>
  <div class="page-wrap">
    <div class="page">
      <!-- Header -->
      <div class="page-header">
        <button class="btn-back" @click="router.push('/ordens-servico')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          Ordens de Serviço
        </button>
        <h1 class="page-title">Nova Ordem de Serviço</h1>
      </div>

      <!-- Step indicator -->
      <div class="steps">
        <div class="step-track" />
        <div v-for="n in 3" :key="n" class="step-item" :class="{ active: step === n, done: step > n }">
          <div class="step-circle">
            <svg v-if="step > n" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
            <span v-else>{{ n }}</span>
          </div>
          <span class="step-label">{{ n === 1 ? 'Cliente' : n === 2 ? 'Trotinete' : 'Detalhes' }}</span>
        </div>
      </div>

      <!-- Card -->
      <div class="card">

        <!-- ── Step 1 ── -->
        <template v-if="step === 1">
          <div v-if="!criandoCliente">
            <div class="card-header">
              <h2 class="card-title">Selecionar Cliente</h2>
              <p class="card-sub">Pesquise por nome, NIF ou telemóvel</p>
            </div>

            <!-- Autocomplete combobox -->
            <div class="combo" ref="comboRef">
              <div class="combo-input-wrap">
                <svg class="combo-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input
                  class="combo-input"
                  v-model="clienteSearch"
                  placeholder="Nome, NIF ou telemóvel..."
                  autocomplete="off"
                  spellcheck="false"
                  @input="onSearchInput"
                  @focus="onSearchFocus"
                  @keydown="onKeyDown"
                />
                <div v-if="searchLoading" class="combo-spinner" />
              </div>

              <!-- Dropdown results -->
              <div v-if="showDropdown" class="combo-dropdown">
                <template v-if="clienteResults.length > 0">
                  <div
                    v-for="(c, i) in clienteResults"
                    :key="c.id"
                    class="combo-item"
                    :class="{ focused: i === focusedIdx }"
                    @mousedown.prevent="selectCliente(c)"
                    @mouseenter="focusedIdx = i"
                  >
                    <div class="combo-item-name">{{ c.nome }}</div>
                    <div class="combo-item-sub">NIF {{ c.nif }} · {{ c.telemovel }}</div>
                  </div>
                </template>
                <div v-else-if="!searchLoading" class="combo-empty">
                  <span>Nenhum cliente encontrado para "{{ clienteSearch }}"</span>
                </div>
              </div>
            </div>

            <div class="divider-or"><span>ou</span></div>

            <button class="btn-new-client" @click="criandoCliente = true">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Registar novo cliente
            </button>
          </div>

          <!-- New client form -->
          <div v-else>
            <div class="card-header">
              <button class="btn-back-inline" @click="criandoCliente = false">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
                Voltar à pesquisa
              </button>
              <h2 class="card-title" style="margin-top: 0.5rem">Novo Cliente</h2>
            </div>
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
                  <span>Li e aceito o tratamento dos dados pessoais (RGPD) *</span>
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
          <div class="card-header">
            <h2 class="card-title">Selecionar Trotinete</h2>
            <div class="client-pill">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              {{ clienteSelecionado?.nome }}
            </div>
          </div>

          <div v-if="!criandoTrot">
            <div v-if="clienteTrotinetes.length > 0" class="trot-list">
              <div
                v-for="t in clienteTrotinetes"
                :key="t.id"
                class="trot-item"
                @click="selectTrot(t)"
              >
                <div class="trot-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="5" cy="17" r="3"/><circle cx="19" cy="17" r="3"/><path d="M12 17V7l-7 4"/><path d="M14 7h6l-3 4h-3"/></svg>
                </div>
                <div class="trot-info">
                  <div class="trot-name">{{ t.marca }} {{ t.modelo }}</div>
                  <div class="trot-serial">{{ t.numero_serie }}</div>
                </div>
                <svg class="trot-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
              </div>
            </div>
            <div v-else class="empty-state">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#d1d5db" stroke-width="1.5"><circle cx="5" cy="17" r="3"/><circle cx="19" cy="17" r="3"/><path d="M12 17V7l-7 4"/><path d="M14 7h6l-3 4h-3"/></svg>
              <p>Este cliente não tem trotinetes registadas.</p>
            </div>

            <div class="divider-or" style="margin-top: 1rem"><span>ou</span></div>

            <button class="btn-new-client" @click="criandoTrot = true">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Registar nova trotinete
            </button>
            <button class="btn btn--ghost btn--sm" style="margin-top: 0.5rem; width: 100%" @click="step = 1; clearSelection()">← Voltar ao cliente</button>
          </div>

          <div v-else>
            <button class="btn-back-inline" @click="criandoTrot = false">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
              Voltar à lista
            </button>
            <div class="form-grid" style="margin-top: 1rem">
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
          <div class="card-header">
            <h2 class="card-title">Detalhes da Ordem de Serviço</h2>
          </div>

          <div class="summary-row">
            <div class="summary-chip">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              {{ clienteSelecionado?.nome }}
            </div>
            <div class="summary-chip">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="5" cy="17" r="3"/><circle cx="19" cy="17" r="3"/><path d="M12 17V7l-7 4"/><path d="M14 7h6l-3 4h-3"/></svg>
              {{ trotSelecionada?.marca }} {{ trotSelecionada?.modelo }}
            </div>
            <div class="summary-chip summary-chip--mono">{{ trotSelecionada?.numero_serie }}</div>
          </div>

          <div class="form-grid" style="margin-top: 1.25rem">
            <div v-if="isAdmin" class="field field--full">
              <label>Loja *</label>
              <select v-model="lojaIdSelecionada" required>
                <option :value="null" disabled>Selecione a loja...</option>
                <option v-for="l in lojas" :key="l.id" :value="l.id">{{ l.nome }}</option>
              </select>
            </div>
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
  </div>
</template>

<style scoped>
/* ── Layout ──────────────────────────────────────────────────── */
.page-wrap {
  display: flex;
  justify-content: center;
  padding: 2rem 1rem;
  min-height: 100%;
}

.page {
  width: 100%;
  max-width: 580px;
}

/* ── Page header ─────────────────────────────────────────────── */
.page-header { margin-bottom: 2rem; }
.btn-back {
  display: inline-flex; align-items: center; gap: 0.3rem;
  background: none; border: none;
  color: #64748b; font-size: 0.825rem; font-weight: 500;
  cursor: pointer; padding: 0; margin-bottom: 0.75rem;
  transition: color 0.15s;
}
.btn-back:hover { color: #1abc9c; }

.page-title {
  font-size: 1.5rem; font-weight: 700;
  color: #111827; margin: 0;
}

/* ── Steps ───────────────────────────────────────────────────── */
.steps {
  display: flex;
  align-items: flex-start;
  margin-bottom: 2rem;
  position: relative;
}
.step-track {
  position: absolute;
  top: 17px;
  left: calc(16.67% - 0px);
  right: calc(16.67% - 0px);
  height: 2px;
  background: #e5e7eb;
  z-index: 0;
}
.step-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 1;
}
.step-circle {
  width: 34px; height: 34px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.85rem;
  background: #fff;
  border: 2px solid #e5e7eb;
  color: #9ca3af;
  transition: all 0.2s;
}
.step-item.active .step-circle {
  background: #1abc9c; border-color: #1abc9c; color: #fff;
  box-shadow: 0 0 0 4px rgba(26,188,156,0.15);
}
.step-item.done .step-circle {
  background: #ecfdf5; border-color: #6ee7b7; color: #059669;
}
.step-label {
  font-size: 0.78rem; font-weight: 500; color: #9ca3af;
  white-space: nowrap;
}
.step-item.active .step-label { color: #1abc9c; font-weight: 600; }
.step-item.done .step-label { color: #059669; }

/* ── Card ────────────────────────────────────────────────────── */
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 4px 16px rgba(0,0,0,0.05);
  padding: 2rem;
}

.card-header { margin-bottom: 1.5rem; }
.card-title { font-size: 1.1rem; font-weight: 700; color: #111827; margin: 0 0 0.25rem; }
.card-sub { font-size: 0.85rem; color: #6b7280; margin: 0; }

/* ── Autocomplete combobox ───────────────────────────────────── */
.combo { position: relative; }

.combo-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  padding: 0 0.75rem;
  background: #fff;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.combo-input-wrap:focus-within {
  border-color: #1abc9c;
  box-shadow: 0 0 0 3px rgba(26,188,156,0.12);
}
.combo-icon { color: #9ca3af; flex-shrink: 0; }
.combo-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 0.7rem 0;
  font-size: 0.9rem;
  color: #111827;
  background: transparent;
}
.combo-input::placeholder { color: #9ca3af; }
.combo-spinner {
  width: 16px; height: 16px;
  border: 2px solid #e5e7eb;
  border-top-color: #1abc9c;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.combo-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0; right: 0;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  z-index: 100;
  overflow: hidden;
}
.combo-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid #f9fafb;
  transition: background 0.1s;
}
.combo-item:last-child { border-bottom: none; }
.combo-item:hover, .combo-item.focused { background: #f0fdf4; }
.combo-item-name { font-weight: 600; font-size: 0.9rem; color: #111827; }
.combo-item-sub { font-size: 0.8rem; color: #6b7280; margin-top: 0.1rem; }
.combo-empty {
  padding: 1rem;
  text-align: center;
  font-size: 0.875rem;
  color: #9ca3af;
}

/* ── Divider ─────────────────────────────────────────────────── */
.divider-or {
  display: flex; align-items: center; gap: 0.75rem;
  margin: 1.25rem 0;
  color: #d1d5db; font-size: 0.8rem;
}
.divider-or::before, .divider-or::after {
  content: ''; flex: 1; height: 1px; background: #e5e7eb;
}
.divider-or span { color: #9ca3af; }

/* ── New client/trotinete button ─────────────────────────────── */
.btn-new-client {
  display: flex; align-items: center; justify-content: center; gap: 0.5rem;
  width: 100%;
  padding: 0.65rem 1rem;
  border: 1.5px dashed #d1d5db;
  border-radius: 8px;
  background: none;
  color: #6b7280;
  font-size: 0.875rem; font-weight: 500;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}
.btn-new-client:hover { border-color: #1abc9c; color: #1abc9c; }

/* ── Client pill (step 2 header) ─────────────────────────────── */
.client-pill {
  display: inline-flex; align-items: center; gap: 0.35rem;
  background: #f0fdf4; border: 1px solid #6ee7b7;
  color: #065f46; font-size: 0.8rem; font-weight: 600;
  padding: 0.25rem 0.65rem; border-radius: 999px;
  margin-top: 0.5rem;
}

/* ── Trotinete list ──────────────────────────────────────────── */
.trot-list {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}
.trot-item {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.85rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.1s;
}
.trot-item:last-child { border-bottom: none; }
.trot-item:hover { background: #f0fdf4; }
.trot-icon {
  width: 36px; height: 36px;
  border-radius: 8px;
  background: #f3f4f6;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  color: #6b7280;
}
.trot-info { flex: 1; min-width: 0; }
.trot-name { font-weight: 600; font-size: 0.9rem; color: #111827; }
.trot-serial { font-size: 0.8rem; color: #6b7280; font-family: 'Courier New', monospace; margin-top: 0.1rem; }
.trot-chevron { color: #d1d5db; flex-shrink: 0; }

.empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 0.5rem; padding: 2rem 0;
  color: #9ca3af; font-size: 0.875rem;
}

/* ── Summary chips (step 3) ──────────────────────────────────── */
.summary-row {
  display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem;
  margin-bottom: 0.25rem;
}
.summary-chip {
  display: inline-flex; align-items: center; gap: 0.35rem;
  background: #f8fafc; border: 1px solid #e5e7eb;
  color: #374151; font-size: 0.8rem; font-weight: 500;
  padding: 0.25rem 0.65rem; border-radius: 999px;
}
.summary-chip--mono { font-family: 'Courier New', monospace; color: #6b7280; }

/* ── Back inline button ──────────────────────────────────────── */
.btn-back-inline {
  display: inline-flex; align-items: center; gap: 0.3rem;
  background: none; border: none;
  color: #6b7280; font-size: 0.825rem; font-weight: 500;
  cursor: pointer; padding: 0; margin-bottom: 0.5rem;
  transition: color 0.15s;
}
.btn-back-inline:hover { color: #374151; }

/* ── Form ────────────────────────────────────────────────────── */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.field { display: flex; flex-direction: column; gap: 0.35rem; }
.field--full { grid-column: 1 / -1; }
.field label {
  font-size: 0.8rem; font-weight: 600;
  color: #374151; letter-spacing: 0.01em;
}
.field input, .field select, .field textarea {
  padding: 0.55rem 0.75rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 7px;
  font-size: 0.875rem;
  color: #111827;
  transition: border-color 0.15s, box-shadow 0.15s;
  background: #fff;
}
.field input:focus, .field select:focus, .field textarea:focus {
  outline: none;
  border-color: #1abc9c;
  box-shadow: 0 0 0 3px rgba(26,188,156,0.1);
}
.field textarea { resize: vertical; }

.rgpd-check {
  display: flex; align-items: flex-start; gap: 0.5rem;
  cursor: pointer; font-size: 0.85rem; font-weight: 400;
  color: #374151;
}
.rgpd-check input[type="checkbox"] { width: auto; margin-top: 2px; accent-color: #1abc9c; }

.step-actions {
  display: flex; justify-content: flex-end; gap: 0.75rem;
  margin-top: 0.5rem;
}

.form-error { color: #dc2626; font-size: 0.82rem; margin: 0; }

/* ── Buttons ─────────────────────────────────────────────────── */
.btn {
  padding: 0.6rem 1.2rem;
  border: none; border-radius: 7px;
  font-size: 0.875rem; font-weight: 600;
  cursor: pointer; transition: opacity 0.15s;
  white-space: nowrap;
}
.btn:hover { opacity: 0.85; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--ghost { background: transparent; border: 1px solid #d1d5db; color: #374151; }
.btn--sm { padding: 0.4rem 0.8rem; font-size: 0.8rem; }
</style>
