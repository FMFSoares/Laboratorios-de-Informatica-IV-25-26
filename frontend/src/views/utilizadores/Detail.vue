<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUtilizador, updateUtilizador, resetPasswordAdmin } from '../../services/utilizadores.js'
import { getLojas } from '../../services/lojas.js'
import api from '../../services/api.js'

const route  = useRoute()
const router = useRouter()

const utilizador = ref(null)
const lojas      = ref([])
const loading    = ref(true)
const loadError  = ref('')

const PERFIS = [
  { value: 'ADMINISTRADOR', label: 'Administrador' },
  { value: 'GERENTE_LOJA',  label: 'Gerente de Loja' },
  { value: 'RECECIONISTA',  label: 'Rececionista' },
  { value: 'MECANICO',      label: 'Mecânico' },
]

const PERFIL_LABEL = {
  ADMINISTRADOR: 'Administrador',
  GERENTE_LOJA:  'Gerente de Loja',
  RECECIONISTA:  'Rececionista',
  MECANICO:      'Mecânico',
}

const PERFIL_STYLE = {
  ADMINISTRADOR: { background: '#ede9fe', color: '#5b21b6' },
  GERENTE_LOJA:  { background: '#dbeafe', color: '#1e40af' },
  RECECIONISTA:  { background: '#dcfce7', color: '#166534' },
  MECANICO:      { background: '#fef9c3', color: '#854d0e' },
}

async function load() {
  loading.value   = true
  loadError.value = ''
  try {
    const [uRes, lRes] = await Promise.all([
      getUtilizador(route.params.id),
      getLojas({ page_size: 50 }),
    ])
    utilizador.value = uRes.data.data
    lojas.value      = lRes.data.data ?? []
    resetEditForm()
  } catch {
    loadError.value = 'Utilizador não encontrado.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

const lojaNome = computed(() => {
  if (!utilizador.value?.loja_id) return '—'
  return lojas.value.find(l => l.id === utilizador.value.loja_id)?.nome || '—'
})

const isMecanico = computed(() => utilizador.value?.perfil === 'MECANICO')

// ── Tabs ──────────────────────────────────────────────────────
const activeTab = ref('info')

function switchTab(tab) {
  activeTab.value = tab
  if (tab === 'salario' && !salarioLoaded.value) loadSalario()
}

// ── Salary history ────────────────────────────────────────────
const salarioHistorico  = ref([])
const salarioLoading    = ref(false)
const salarioError      = ref(null)
const salarioLoaded     = ref(false)

const salarioAtual = computed(() => {
  if (!salarioHistorico.value.length) return null
  return salarioHistorico.value[salarioHistorico.value.length - 1]
})

async function loadSalario() {
  salarioLoading.value = true
  salarioError.value   = null
  try {
    const res = await api.get(`/salarios/${route.params.id}/historico`, { params: { meses: 12 } })
    salarioHistorico.value = res.data.data
    salarioLoaded.value    = true
  } catch (e) {
    salarioError.value = e.response?.data?.detail?.detail || e.response?.data?.detail || 'Erro ao carregar histórico.'
  } finally {
    salarioLoading.value = false
  }
}

function fmt(val) {
  return (val ?? 0).toLocaleString('pt-PT', { style: 'currency', currency: 'EUR' })
}

// ── Edit modal ────────────────────────────────────────────────
const showEditModal  = ref(false)
const editForm       = ref({})
const editing        = ref(false)
const editError      = ref('')
const editOk         = ref(false)

const editNeedsLoja  = computed(() => editForm.value.perfil && editForm.value.perfil !== 'ADMINISTRADOR')
const editIsMecanico = computed(() => editForm.value.perfil === 'MECANICO')

function resetEditForm() {
  const u = utilizador.value
  if (!u) return
  editForm.value = {
    nome:         u.nome,
    email:        u.email,
    perfil:       u.perfil,
    loja_id:      u.loja_id,
    comissao:     u.comissao,
    salario_base: u.salario_base,
  }
  editError.value = ''
  editOk.value    = false
}

function openEditModal() {
  resetEditForm()
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
  editError.value     = ''
}

async function submitEdit() {
  editError.value = ''
  if (!editForm.value.nome.trim())  { editError.value = 'Nome obrigatório.'; return }
  if (!editForm.value.email.trim()) { editError.value = 'Email obrigatório.'; return }
  if (editNeedsLoja.value && !editForm.value.loja_id) { editError.value = 'Selecione a loja.'; return }

  editing.value = true
  try {
    await updateUtilizador(utilizador.value.id, {
      nome:         editForm.value.nome.trim(),
      email:        editForm.value.email.trim(),
      perfil:       editForm.value.perfil,
      loja_id:      editForm.value.perfil === 'ADMINISTRADOR' ? null : Number(editForm.value.loja_id),
      comissao:     editIsMecanico.value && editForm.value.comissao ? Number(editForm.value.comissao) : null,
      salario_base: editForm.value.salario_base ? Number(editForm.value.salario_base) : null,
    })
    editOk.value = true
    salarioLoaded.value = false  // invalidate cached salary data
    await load()
    setTimeout(() => {
      editOk.value        = false
      showEditModal.value = false
    }, 1200)
  } catch (e) {
    editError.value = e.response?.data?.detail?.detail || e.response?.data?.detail || 'Erro ao actualizar.'
  } finally {
    editing.value = false
  }
}

// ── Password modal ────────────────────────────────────────────
const showPasswordModal = ref(false)
const newPassword       = ref('')
const confirmPassword   = ref('')
const savingPassword    = ref(false)
const passwordError     = ref('')
const passwordOk        = ref(false)

function openPasswordModal() {
  newPassword.value     = ''
  confirmPassword.value = ''
  passwordError.value   = ''
  passwordOk.value      = false
  showPasswordModal.value = true
}

function closePasswordModal() {
  showPasswordModal.value = false
  passwordError.value     = ''
}

async function submitPassword() {
  passwordError.value = ''
  passwordOk.value    = false
  if (newPassword.value.length < 6)               { passwordError.value = 'Password mínima 6 caracteres.'; return }
  if (newPassword.value !== confirmPassword.value) { passwordError.value = 'As passwords não coincidem.'; return }

  savingPassword.value = true
  try {
    await resetPasswordAdmin(utilizador.value.id, { nova_password: newPassword.value })
    passwordOk.value = true
    setTimeout(() => {
      passwordOk.value        = false
      showPasswordModal.value = false
    }, 1500)
  } catch (e) {
    passwordError.value = e.response?.data?.detail?.detail || 'Erro ao alterar password.'
  } finally {
    savingPassword.value = false
  }
}

// ── Toggle ativo ──────────────────────────────────────────────
const showConfirm   = ref(false)
const togglingAtivo = ref(false)
const toggleError   = ref('')

async function confirmToggle() {
  togglingAtivo.value = true
  toggleError.value   = ''
  try {
    await updateUtilizador(utilizador.value.id, { ativo: !utilizador.value.ativo })
    showConfirm.value = false
    await load()
  } catch (e) {
    toggleError.value = e.response?.data?.detail?.detail || 'Erro ao alterar estado.'
  } finally {
    togglingAtivo.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="back-row">
      <button class="btn-back" @click="router.back()">← Utilizadores</button>
    </div>

    <div v-if="loading" class="msg-empty">A carregar...</div>
    <div v-else-if="loadError" class="msg-error">{{ loadError }}</div>

    <template v-else-if="utilizador">
      <!-- Header -->
      <div class="page-header">
        <div class="header-left">
          <div class="avatar">{{ utilizador.nome?.charAt(0).toUpperCase() }}</div>
          <div>
            <h1>{{ utilizador.nome }}</h1>
            <p class="email">{{ utilizador.email }}</p>
          </div>
        </div>
        <div class="header-right">
          <span class="chip chip--perfil" :style="PERFIL_STYLE[utilizador.perfil]">
            {{ PERFIL_LABEL[utilizador.perfil] || utilizador.perfil }}
          </span>
          <span class="chip" :class="utilizador.ativo ? 'chip--ativo' : 'chip--inativo'">
            {{ utilizador.ativo ? 'Ativo' : 'Inativo' }}
          </span>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tabs">
        <button class="tab-btn" :class="{ active: activeTab === 'info' }" @click="switchTab('info')">Informações</button>
        <button class="tab-btn" :class="{ active: activeTab === 'salario' }" @click="switchTab('salario')">Salário</button>
      </div>

      <!-- ── Tab: Informações ────────────────────────────────── -->
      <div v-if="activeTab === 'info'" class="layout">
        <div class="left">
          <!-- Info card -->
          <div class="card">
            <div class="card-title-row">
              <span class="card-title">Informações</span>
              <button class="btn btn--ghost btn--sm" @click="openEditModal">Editar</button>
            </div>
            <dl class="info-list">
              <div class="info-row">
                <dt>Nome</dt>
                <dd>{{ utilizador.nome }}</dd>
              </div>
              <div class="info-row">
                <dt>Email</dt>
                <dd>{{ utilizador.email }}</dd>
              </div>
              <div class="info-row">
                <dt>Perfil</dt>
                <dd>
                  <span class="chip chip--perfil" :style="PERFIL_STYLE[utilizador.perfil]">
                    {{ PERFIL_LABEL[utilizador.perfil] || utilizador.perfil }}
                  </span>
                </dd>
              </div>
              <div class="info-row" v-if="utilizador.perfil !== 'ADMINISTRADOR'">
                <dt>Loja</dt>
                <dd>{{ lojaNome }}</dd>
              </div>
              <div class="info-row">
                <dt>Salário Base</dt>
                <dd>{{ utilizador.salario_base != null ? fmt(utilizador.salario_base) : '—' }}</dd>
              </div>
            </dl>
            <div class="card-footer">
              <button class="btn btn--ghost" @click="openPasswordModal">Alterar Password</button>
            </div>
          </div>

          <!-- Commission card (mechanics only) -->
          <div v-if="isMecanico" class="card card--commission">
            <div class="card-title-row">
              <span class="card-title">Comissão</span>
              <button class="btn btn--ghost btn--sm" @click="openEditModal">Editar</button>
            </div>
            <div class="commission-display">
              <span class="commission-value">{{ utilizador.comissao != null ? utilizador.comissao + '%' : '—' }}</span>
              <span class="commission-desc">por serviço faturado</span>
            </div>
            <p class="commission-note">
              A comissão é calculada sobre o valor final de cada fatura emitida no mês em que o mecânico interveio na OS.
            </p>
          </div>
        </div>

        <!-- Right: account status -->
        <div class="right">
          <div
            v-if="utilizador.perfil !== 'ADMINISTRADOR'"
            class="card"
            :class="utilizador.ativo ? 'card--danger-zone' : 'card--success-zone'"
          >
            <div class="card-title">Estado da Conta</div>
            <p class="zone-desc">
              <template v-if="utilizador.ativo">
                A conta está ativa. Desativar impede o utilizador de fazer login.
              </template>
              <template v-else>
                A conta está desativada. Reativar permite que o utilizador faça login novamente.
              </template>
            </p>
            <button
              class="btn"
              :class="utilizador.ativo ? 'btn--danger' : 'btn--success'"
              @click="showConfirm = true"
            >
              {{ utilizador.ativo ? 'Desativar conta' : 'Ativar conta' }}
            </button>
          </div>
        </div>
      </div>

      <!-- ── Tab: Salário ────────────────────────────────────── -->
      <div v-if="activeTab === 'salario'">
        <div v-if="salarioLoading" class="msg-empty">A calcular...</div>
        <div v-else-if="salarioError" class="alert-error">{{ salarioError }}</div>

        <template v-else-if="salarioAtual">
          <!-- Current month cards -->
          <div class="salary-summary">
            <div class="salary-card">
              <div class="salary-card__label">Salário Base</div>
              <div class="salary-card__value">{{ fmt(salarioAtual.salario_base) }}</div>
              <div class="salary-card__sub">mensal fixo</div>
            </div>
            <div v-if="isMecanico" class="salary-card salary-card--commission">
              <div class="salary-card__label">Comissão ({{ utilizador.comissao }}%)</div>
              <div class="salary-card__value">{{ fmt(salarioAtual.comissao_ganha) }}</div>
              <div class="salary-card__sub">{{ salarioAtual.mes_label }}</div>
            </div>
            <div class="salary-card salary-card--total">
              <div class="salary-card__label">Total {{ salarioAtual.mes_label }}</div>
              <div class="salary-card__value">{{ fmt(salarioAtual.total) }}</div>
              <div class="salary-card__sub">base{{ isMecanico ? ' + comissão' : '' }}</div>
            </div>
          </div>

          <!-- History table -->
          <div class="card table-card">
            <div class="card-title-row" style="padding: 1rem 1.25rem 0">
              <span class="card-title">Histórico (12 meses)</span>
            </div>
            <table class="table">
              <thead>
                <tr>
                  <th>Mês</th>
                  <th class="num">Salário Base</th>
                  <th v-if="isMecanico" class="num">Comissão Ganha</th>
                  <th class="num">Total</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in [...salarioHistorico].reverse()"
                  :key="`${row.ano}-${row.mes}`"
                  :class="{ 'row--current': row === salarioAtual }"
                >
                  <td>
                    {{ row.mes_label }}
                    <span v-if="row === salarioAtual" class="badge-now">este mês</span>
                  </td>
                  <td class="num">{{ fmt(row.salario_base) }}</td>
                  <td v-if="isMecanico" class="num">{{ row.comissao_ganha > 0 ? fmt(row.comissao_ganha) : '—' }}</td>
                  <td class="num"><strong>{{ fmt(row.total) }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </div>
    </template>

    <!-- Edit modal -->
    <Teleport to="body">
      <div v-if="showEditModal" class="modal-backdrop" @click.self="closeEditModal">
        <div class="modal">
          <div class="modal-header">
            <span class="modal-title">Editar Utilizador</span>
            <button class="modal-close" @click="closeEditModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="field">
              <label>Nome completo *</label>
              <input v-model="editForm.nome" type="text" />
            </div>
            <div class="field">
              <label>Email *</label>
              <input v-model="editForm.email" type="email" />
            </div>
            <div class="field">
              <label>Perfil *</label>
              <select v-model="editForm.perfil">
                <option v-for="p in PERFIS" :key="p.value" :value="p.value">{{ p.label }}</option>
              </select>
            </div>
            <div v-if="editNeedsLoja" class="field">
              <label>Loja *</label>
              <select v-model="editForm.loja_id">
                <option :value="null">Selecionar loja…</option>
                <option v-for="l in lojas" :key="l.id" :value="l.id">{{ l.nome }}</option>
              </select>
            </div>
            <div class="field">
              <label>Salário Base (€)</label>
              <input v-model="editForm.salario_base" type="number" min="0" step="0.01" placeholder="Ex: 1200" />
            </div>
            <div v-if="editIsMecanico" class="field">
              <label>Comissão (%)</label>
              <input v-model="editForm.comissao" type="number" min="0" max="100" />
            </div>
            <p v-if="editError" class="msg-error-inline">{{ editError }}</p>
            <p v-if="editOk" class="msg-ok">Alterações guardadas.</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn--ghost btn--sm" @click="closeEditModal">Cancelar</button>
            <button class="btn btn--primary" :disabled="editing" @click="submitEdit">
              {{ editing ? 'A guardar…' : 'Guardar alterações' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Confirm toggle modal -->
    <Teleport to="body">
      <div v-if="showConfirm" class="modal-backdrop" @click.self="showConfirm = false">
        <div class="modal modal--sm">
          <div class="modal-header">
            <span class="modal-title">Confirmar ação</span>
            <button class="modal-close" @click="showConfirm = false">✕</button>
          </div>
          <div class="modal-body">
            <p class="confirm-msg">
              Tem a certeza que pretende <strong>{{ utilizador?.ativo ? 'desativar' : 'ativar' }}</strong> a conta de "{{ utilizador?.nome }}"?
            </p>
            <p v-if="toggleError" class="msg-error-inline">{{ toggleError }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn--ghost btn--sm" @click="showConfirm = false">Cancelar</button>
            <button
              class="btn btn--sm"
              :class="utilizador?.ativo ? 'btn--danger' : 'btn--success'"
              :disabled="togglingAtivo"
              @click="confirmToggle"
            >
              {{ togglingAtivo ? 'A processar…' : utilizador?.ativo ? 'Desativar' : 'Ativar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Password modal -->
    <Teleport to="body">
      <div v-if="showPasswordModal" class="modal-backdrop" @click.self="closePasswordModal">
        <div class="modal modal--sm">
          <div class="modal-header">
            <span class="modal-title">Alterar Password</span>
            <button class="modal-close" @click="closePasswordModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="field">
              <label>Nova password *</label>
              <input v-model="newPassword" type="password" placeholder="Mínimo 6 caracteres" />
            </div>
            <div class="field">
              <label>Confirmar password *</label>
              <input v-model="confirmPassword" type="password" placeholder="Repita a password" />
            </div>
            <p v-if="passwordError" class="msg-error-inline">{{ passwordError }}</p>
            <p v-if="passwordOk" class="msg-ok">Password alterada com sucesso.</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn--ghost btn--sm" @click="closePasswordModal">Cancelar</button>
            <button class="btn btn--primary" :disabled="savingPassword" @click="submitPassword">
              {{ savingPassword ? 'A guardar…' : 'Redefinir password' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.page { padding: 2rem; max-width: 1000px; }

.back-row { margin-bottom: 1.25rem; }
.btn-back { background: none; border: none; color: #1abc9c; font-size: 0.9rem; font-weight: 500; cursor: pointer; padding: 0; }
.btn-back:hover { text-decoration: underline; }

/* Header */
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.avatar { width: 52px; height: 52px; border-radius: 50%; background: #1abc9c; color: #fff; font-size: 1.3rem; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.header-left h1 { margin: 0; font-size: 1.5rem; color: #111827; }
.email { margin: 0.2rem 0 0; font-size: 0.875rem; color: #6b7280; }
.header-right { display: flex; align-items: center; gap: 0.5rem; }

/* Tabs */
.tabs { display: flex; gap: 0; border-bottom: 2px solid #e5e7eb; margin-bottom: 1.5rem; }
.tab-btn {
  background: none; border: none; padding: 0.65rem 1.25rem;
  font-size: 0.9rem; font-weight: 600; color: #6b7280;
  cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px;
  transition: color .15s, border-color .15s;
}
.tab-btn:hover { color: #374151; }
.tab-btn.active { color: #1abc9c; border-bottom-color: #1abc9c; }

/* Layout */
.layout { display: grid; grid-template-columns: 1fr 300px; gap: 1.5rem; align-items: start; }
@media (max-width: 800px) { .layout { grid-template-columns: 1fr; } }
.left, .right { display: flex; flex-direction: column; gap: 1.25rem; }

/* Card */
.card { background: #fff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 1.5rem; }
.card-title { font-size: 0.75rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }
.card-title-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; }
.card-footer { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.25rem; }
.card--danger-zone  { border-left: 3px solid #fca5a5; }
.card--success-zone { border-left: 3px solid #6ee7b7; }
.zone-desc { font-size: 0.875rem; color: #6b7280; line-height: 1.5; margin: 0 0 1rem; }

/* Commission card */
.card--commission { border-left: 3px solid #fbbf24; }
.commission-display { display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 0.75rem; }
.commission-value { font-size: 2.5rem; font-weight: 800; color: #111827; line-height: 1; }
.commission-desc { font-size: 0.85rem; color: #6b7280; }
.commission-note { font-size: 0.8rem; color: #9ca3af; line-height: 1.5; margin: 0; }

/* Info list */
.info-list { margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.75rem; }
.info-row { display: flex; align-items: baseline; gap: 0.5rem; }
.info-row dt { font-size: 0.8rem; font-weight: 600; color: #6b7280; min-width: 90px; flex-shrink: 0; }
.info-row dd { margin: 0; font-size: 0.9rem; color: #111827; font-weight: 500; }

/* Salary summary cards */
.salary-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.salary-card {
  background: #fff; border-radius: 10px; padding: 1.25rem 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  border-top: 3px solid #e5e7eb;
}
.salary-card--commission { border-top-color: #fbbf24; }
.salary-card--total { border-top-color: #1abc9c; }
.salary-card__label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; color: #6b7280; margin-bottom: 0.4rem; }
.salary-card__value { font-size: 1.75rem; font-weight: 800; color: #111827; line-height: 1.1; }
.salary-card--total .salary-card__value { color: #1abc9c; }
.salary-card__sub { font-size: 0.78rem; color: #9ca3af; margin-top: 0.3rem; }

/* History table */
.table-card { padding: 0; overflow: hidden; margin-bottom: 1.5rem; }
.table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.table th {
  background: #f9fafb; padding: .7rem 1.25rem;
  text-align: left; font-size: .72rem; font-weight: 700; color: #6b7280;
  text-transform: uppercase; letter-spacing: .05em; border-bottom: 1px solid #f3f4f6;
}
.table th.num { text-align: right; }
.table td { padding: .7rem 1.25rem; border-bottom: 1px solid #f3f4f6; color: #374151; }
.table tbody tr:last-child td { border-bottom: none; }
.table tbody tr:hover { background: #f9fafb; }
.table td.num { text-align: right; }
.row--current td { background: #f0fdf9; font-weight: 500; }
.badge-now {
  display: inline-block; margin-left: 0.5rem; padding: .1rem .45rem;
  background: #d1fae5; color: #065f46; font-size: .68rem; font-weight: 700;
  border-radius: 99px; text-transform: uppercase; letter-spacing: .03em;
  vertical-align: middle;
}

/* Fields */
.field { display: flex; flex-direction: column; gap: 0.3rem; margin-bottom: 1rem; }
.field label { font-size: 0.8rem; font-weight: 600; color: #374151; }
.field input, .field select { padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 7px; font-size: 0.875rem; color: #374151; outline: none; }
.field input:focus, .field select:focus { border-color: #1abc9c; box-shadow: 0 0 0 3px rgba(26,188,156,0.12); }

/* Chips */
.chip { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
.chip--perfil  { font-size: 0.8rem; padding: 0.3rem 0.8rem; }
.chip--ativo   { background: #dcfce7; color: #166534; }
.chip--inativo { background: #f1f5f9; color: #64748b; }

/* Buttons */
.btn { padding: 0.55rem 1.2rem; border: none; border-radius: 7px; font-size: 0.875rem; font-weight: 600; cursor: pointer; transition: opacity 0.15s; white-space: nowrap; }
.btn:hover    { opacity: 0.85; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--ghost   { background: #f1f5f9; color: #374151; border: 1px solid #d1d5db; }
.btn--danger  { background: #ef4444; color: #fff; }
.btn--success { background: #22c55e; color: #fff; }
.btn--sm      { padding: 0.4rem 0.85rem; font-size: 0.825rem; }

/* Feedback */
.msg-empty        { padding: 2rem; text-align: center; color: #9ca3af; }
.msg-error        { padding: 2rem; text-align: center; color: #dc2626; }
.msg-error-inline { color: #dc2626; font-size: 0.85rem; margin: 0 0 0.5rem; }
.msg-ok           { color: #059669; font-size: 0.85rem; margin: 0 0 0.5rem; font-weight: 500; }
.alert-error { background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c; border-radius: 8px; padding: .75rem 1rem; font-size: .875rem; margin-bottom: 1rem; }

/* Modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 12px; width: 100%; max-width: 480px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); overflow: hidden; }
.modal--sm { max-width: 380px; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1.25rem 1.5rem; border-bottom: 1px solid #f1f5f9; }
.modal-title { font-size: 1rem; font-weight: 700; color: #111827; }
.modal-close { background: none; border: none; font-size: 1rem; color: #9ca3af; cursor: pointer; line-height: 1; padding: 0.25rem; }
.modal-close:hover { color: #374151; }
.modal-body { padding: 1.5rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; padding: 1rem 1.5rem; border-top: 1px solid #f1f5f9; }
.confirm-msg { font-size: 0.9rem; color: #374151; line-height: 1.5; margin: 0 0 0.5rem; }
</style>
