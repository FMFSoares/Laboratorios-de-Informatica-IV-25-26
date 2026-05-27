<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUtilizadores, createUtilizador } from '../../services/utilizadores.js'
import { getLojas } from '../../services/lojas.js'

const router = useRouter()

const utilizadores = ref([])
const lojas        = ref([])
const loading      = ref(false)
const error        = ref('')

const search       = ref('')
const filtroPerfil = ref('')
const sortKey      = ref('nome')
const sortDir      = ref(1)

// ── Create modal ──────────────────────────────────────────────
const showCreate  = ref(false)
const creating    = ref(false)
const createError = ref('')
const createForm  = ref(emptyForm())

function emptyForm() {
  return { nome: '', email: '', password: '', perfil: '', loja_id: null, ativo: true, comissao: null, salario_base: null }
}

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

const createNeedsLoja  = computed(() => createForm.value.perfil && createForm.value.perfil !== 'ADMINISTRADOR')
const createIsMecanico = computed(() => createForm.value.perfil === 'MECANICO')

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  let list = utilizadores.value.filter(u => {
    const matchQ = !q || u.nome.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    const matchP = !filtroPerfil.value || u.perfil === filtroPerfil.value
    return matchQ && matchP
  })
  if (sortKey.value) {
    list = [...list].sort((a, b) => {
      const av = a[sortKey.value] ?? ''
      const bv = b[sortKey.value] ?? ''
      return av < bv ? -sortDir.value : av > bv ? sortDir.value : 0
    })
  }
  return list
})

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 1 ? -1 : 1
  } else {
    sortKey.value = key
    sortDir.value = 1
  }
}

function sortIcon(key) {
  if (sortKey.value !== key) return '↕'
  return sortDir.value === 1 ? '↑' : '↓'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [uRes, lRes] = await Promise.all([
      getUtilizadores({ page: 1, page_size: 100 }),
      getLojas({ page_size: 50 }),
    ])
    utilizadores.value = uRes.data.data ?? []
    lojas.value        = lRes.data.data ?? []
  } catch {
    error.value = 'Erro ao carregar utilizadores.'
  } finally {
    loading.value = false
  }
}

// ── Create ────────────────────────────────────────────────────
function openCreate() {
  createForm.value = emptyForm()
  createError.value = ''
  showCreate.value = true
}

async function submitCreate() {
  createError.value = ''
  if (!createForm.value.nome.trim())                                    { createError.value = 'Nome obrigatório.'; return }
  if (!createForm.value.email.trim())                                   { createError.value = 'Email obrigatório.'; return }
  if (!createForm.value.password || createForm.value.password.length < 6) { createError.value = 'Password mínima 6 caracteres.'; return }
  if (!createForm.value.perfil)                                          { createError.value = 'Selecione um perfil.'; return }
  if (createNeedsLoja.value && !createForm.value.loja_id)               { createError.value = 'Selecione a loja.'; return }

  const body = {
    nome:     createForm.value.nome.trim(),
    email:    createForm.value.email.trim(),
    password: createForm.value.password,
    perfil:   createForm.value.perfil,
    loja_id:  createForm.value.perfil === 'ADMINISTRADOR' ? null : Number(createForm.value.loja_id),
    ativo:    createForm.value.ativo,
    comissao: createIsMecanico.value && createForm.value.comissao ? Number(createForm.value.comissao) : null,
    salario_base: createForm.value.salario_base ? Number(createForm.value.salario_base) : null,
  }

  creating.value = true
  try {
    await createUtilizador(body)
    showCreate.value = false
    await load()
  } catch (e) {
    createError.value = e.response?.data?.detail?.detail || e.response?.data?.detail || 'Erro ao criar utilizador.'
  } finally {
    creating.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Utilizadores</h1>
      <button class="btn btn--primary" @click="openCreate">+ Novo utilizador</button>
    </div>

    <!-- Filters -->
    <div class="toolbar">
      <input v-model="search" class="search-input" type="search" placeholder="Pesquisar por nome ou email…" />
      <select v-model="filtroPerfil" class="select-filter">
        <option value="">Todos os perfis</option>
        <option v-for="p in PERFIS" :key="p.value" :value="p.value">{{ p.label }}</option>
      </select>
      <span class="result-count">{{ filtered.length }} utilizador{{ filtered.length !== 1 ? 'es' : '' }}</span>
    </div>

    <p v-if="error" class="msg-error">{{ error }}</p>
    <div v-else-if="loading" class="msg-empty">A carregar...</div>
    <p v-else-if="filtered.length === 0" class="msg-empty">Nenhum utilizador encontrado.</p>

    <table v-else class="tbl">
      <thead>
        <tr>
          <th @click="toggleSort('nome')" class="th-sort">Nome <span class="sort-icon">{{ sortIcon('nome') }}</span></th>
          <th @click="toggleSort('email')" class="th-sort">Email <span class="sort-icon">{{ sortIcon('email') }}</span></th>
          <th @click="toggleSort('perfil')" class="th-sort">Perfil <span class="sort-icon">{{ sortIcon('perfil') }}</span></th>
          <th @click="toggleSort('loja_nome')" class="th-sort">Loja <span class="sort-icon">{{ sortIcon('loja_nome') }}</span></th>
          <th>Comissão</th>
          <th @click="toggleSort('ativo')" class="th-sort">Estado <span class="sort-icon">{{ sortIcon('ativo') }}</span></th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="u in filtered"
          :key="u.id"
          class="tbl-row"
          :class="{ 'row--inactive': !u.ativo }"
          @click="router.push(`/utilizadores/${u.id}`)"
        >
          <td class="td-nome">{{ u.nome }}</td>
          <td class="td-email">{{ u.email }}</td>
          <td>
            <span class="chip" :style="PERFIL_STYLE[u.perfil]">{{ PERFIL_LABEL[u.perfil] || u.perfil }}</span>
          </td>
          <td>{{ u.loja_nome || '—' }}</td>
          <td>{{ u.comissao != null ? u.comissao + '%' : '—' }}</td>
          <td>
            <span class="chip" :class="u.ativo ? 'chip--ativo' : 'chip--inativo'">
              {{ u.ativo ? 'Ativo' : 'Inativo' }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- ── Create modal ── -->
  <Teleport to="body">
    <div v-if="showCreate" class="overlay" @click.self="showCreate = false">
      <div class="dialog">
        <h2 class="dialog-title">Novo Utilizador</h2>
        <div class="field">
          <label>Nome completo *</label>
          <input v-model="createForm.nome" type="text" placeholder="Ana Silva" />
        </div>
        <div class="field">
          <label>Email *</label>
          <input v-model="createForm.email" type="email" placeholder="ana@dlmcare.pt" />
        </div>
        <div class="field">
          <label>Password *</label>
          <input v-model="createForm.password" type="password" placeholder="Mínimo 6 caracteres" />
        </div>
        <div class="field">
          <label>Perfil *</label>
          <select v-model="createForm.perfil">
            <option value="">Selecionar perfil…</option>
            <option v-for="p in PERFIS" :key="p.value" :value="p.value">{{ p.label }}</option>
          </select>
        </div>
        <div class="field" v-if="createNeedsLoja">
          <label>Loja *</label>
          <select v-model="createForm.loja_id">
            <option :value="null">Selecionar loja…</option>
            <option v-for="l in lojas" :key="l.id" :value="l.id">{{ l.nome }}</option>
          </select>
        </div>
        <div class="field">
          <label>Salário Base (€)</label>
          <input v-model="createForm.salario_base" type="number" min="0" step="0.01" placeholder="Ex: 1200" />
        </div>
        <div class="field" v-if="createIsMecanico">
          <label>Comissão (%)</label>
          <input v-model="createForm.comissao" type="number" min="0" max="100" placeholder="Ex: 10" />
        </div>
        <div class="field field--inline">
          <input id="create-ativo" v-model="createForm.ativo" type="checkbox" />
          <label for="create-ativo">Conta ativa</label>
        </div>
        <p v-if="createError" class="form-error">{{ createError }}</p>
        <div class="dialog-actions">
          <button class="btn btn--secondary" @click="showCreate = false">Cancelar</button>
          <button class="btn btn--primary" :disabled="creating" @click="submitCreate">
            {{ creating ? 'A criar...' : 'Criar utilizador' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.page { padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; }
.page-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0; }

.toolbar { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.search-input { padding: 0.5rem 0.9rem; border: 1px solid #d1d5db; border-radius: 8px; font-size: 0.875rem; color: #374151; background: #fff; outline: none; min-width: 260px; }
.search-input:focus { border-color: #1abc9c; box-shadow: 0 0 0 3px rgba(26,188,156,0.12); }
.select-filter { padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 8px; font-size: 0.875rem; color: #374151; background: #fff; outline: none; }
.select-filter:focus { border-color: #1abc9c; }
.result-count { margin-left: auto; font-size: 0.82rem; color: #9ca3af; }

.tbl { width: 100%; border-collapse: collapse; font-size: 0.875rem; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.tbl th { padding: 0.65rem 1rem; text-align: left; font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
.tbl td { padding: 0.8rem 1rem; border-bottom: 1px solid #f1f5f9; color: #374151; vertical-align: middle; }
.tbl tbody tr:last-child td { border-bottom: none; }
.tbl-row { cursor: pointer; transition: background 0.1s; }
.tbl-row:hover { background: #f8fafc; }
.row--inactive td { opacity: 0.55; }

.td-nome { font-weight: 600; color: #111827; }
.td-email { font-size: 0.85rem; color: #6b7280; }

.th-sort { cursor: pointer; user-select: none; white-space: nowrap; }
.th-sort:hover { color: #1abc9c; }
.sort-icon { font-size: 0.65rem; margin-left: 0.2rem; opacity: 0.6; }

.chip { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 99px; font-size: 0.72rem; font-weight: 600; }
.chip--ativo  { background: #dcfce7; color: #166534; }
.chip--inativo { background: #f1f5f9; color: #64748b; }

.msg-empty { padding: 2rem; text-align: center; font-size: 0.9rem; color: #9ca3af; }
.msg-error { padding: 2rem; text-align: center; color: #dc2626; }

.btn { padding: 0.55rem 1.2rem; border: none; border-radius: 7px; font-size: 0.875rem; font-weight: 600; cursor: pointer; transition: opacity 0.15s; white-space: nowrap; }
.btn:hover { opacity: 0.85; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary   { background: #1abc9c; color: #fff; }
.btn--secondary { background: #e5e7eb; color: #374151; }

.overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: #fff; border-radius: 12px; padding: 2rem; width: 100%; max-width: 480px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); max-height: 90vh; overflow-y: auto; }
.dialog-title { font-size: 1.15rem; font-weight: 700; color: #111827; margin-bottom: 1rem; }

.field { display: flex; flex-direction: column; gap: 0.3rem; margin-bottom: 1rem; }
.field label { font-size: 0.8rem; font-weight: 600; color: #374151; }
.field input, .field select { padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 7px; font-size: 0.875rem; color: #374151; outline: none; }
.field input:focus, .field select:focus { border-color: #1abc9c; box-shadow: 0 0 0 3px rgba(26,188,156,0.12); }
.field--inline { flex-direction: row; align-items: center; gap: 0.5rem; }
.field--inline input { width: auto; }
.field--inline label { font-size: 0.875rem; font-weight: 500; margin: 0; }

.form-error { color: #dc2626; font-size: 0.85rem; margin-top: 0.25rem; }
.dialog-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem; }
</style>
