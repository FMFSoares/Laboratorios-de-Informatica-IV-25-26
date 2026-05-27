<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getServico, updateServico } from '../../services/servicos.js'

const route  = useRoute()
const router = useRouter()

const servico  = ref(null)
const loading  = ref(true)
const loadErr  = ref('')

async function load() {
  loading.value = true
  loadErr.value = ''
  try {
    const { data } = await getServico(route.params.id)
    servico.value = data.data
  } catch {
    loadErr.value = 'Serviço não encontrado.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

// ── Edit modal ─────────────────────────────────────────────────
const showEdit  = ref(false)
const editForm  = ref({})
const editing   = ref(false)
const editError = ref('')
const editOk    = ref(false)

function openEdit() {
  editForm.value  = { nome: servico.value.nome, preco_base: String(servico.value.preco_base) }
  editError.value = ''
  editOk.value    = false
  showEdit.value  = true
}

async function submitEdit() {
  editError.value = ''
  if (!editForm.value.nome.trim()) { editError.value = 'Nome obrigatório.'; return }
  const preco = parseFloat(editForm.value.preco_base)
  if (isNaN(preco) || preco < 0) { editError.value = 'Preço inválido.'; return }

  editing.value = true
  try {
    const { data } = await updateServico(servico.value.id, { nome: editForm.value.nome.trim(), preco_base: preco })
    servico.value = data.data
    editOk.value  = true
    setTimeout(() => { editOk.value = false; showEdit.value = false }, 1200)
  } catch (e) {
    editError.value = e?.response?.data?.detail?.detail ?? 'Erro ao guardar.'
  } finally {
    editing.value = false
  }
}

// ── Deactivate confirm ─────────────────────────────────────────
const showConfirm = ref(false)
const toggling    = ref(false)
const toggleError = ref('')

async function confirmToggle() {
  toggling.value    = true
  toggleError.value = ''
  try {
    const { data } = await updateServico(servico.value.id, { ativo: !servico.value.ativo })
    servico.value     = data.data
    showConfirm.value = false
  } catch (e) {
    toggleError.value = e?.response?.data?.detail?.detail ?? 'Erro ao alterar estado.'
  } finally {
    toggling.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="back-row">
      <button class="btn-back" @click="router.back()">← Serviços</button>
    </div>

    <div v-if="loading" class="msg-loading">A carregar...</div>
    <div v-else-if="loadErr" class="msg-error">{{ loadErr }}</div>

    <template v-else-if="servico">
      <div class="page-header">
        <div class="header-left">
          <div class="avatar">{{ servico.nome.charAt(0).toUpperCase() }}</div>
          <div class="header-info">
            <h1>{{ servico.nome }}</h1>
            <p class="sub">{{ servico.preco_base.toFixed(2) }} € preço base</p>
          </div>
        </div>
        <div class="header-chips">
          <span class="chip" :class="servico.ativo ? 'chip--green' : 'chip--gray'">
            {{ servico.ativo ? 'Ativo' : 'Inativo' }}
          </span>
        </div>
      </div>

      <div class="layout">
        <div class="col">
          <div class="card">
            <div class="card-hd">
              <span class="card-title">Informações</span>
              <button class="btn btn--ghost btn--sm" @click="openEdit">Editar</button>
            </div>
            <dl class="info-list">
              <div class="info-row">
                <dt>Nome</dt>
                <dd>{{ servico.nome }}</dd>
              </div>
              <div class="info-row">
                <dt>Preço base</dt>
                <dd class="price">{{ servico.preco_base.toFixed(2) }} €</dd>
              </div>
              <div class="info-row">
                <dt>Estado</dt>
                <dd>
                  <span class="chip" :class="servico.ativo ? 'chip--green' : 'chip--gray'">
                    {{ servico.ativo ? 'Ativo' : 'Inativo' }}
                  </span>
                </dd>
              </div>
            </dl>
          </div>
        </div>

        <div class="col">
          <div class="card zone-card" :class="servico.ativo ? 'zone-card--danger' : 'zone-card--success'">
            <div class="card-hd"><span class="card-title">Estado do Serviço</span></div>
            <p class="zone-desc">
              <template v-if="servico.ativo">
                Desativar este serviço impede que apareça em novas ordens de serviço.
              </template>
              <template v-else>
                Reativar este serviço permite que volte a ser usado em ordens de serviço.
              </template>
            </p>
            <button
              class="btn"
              :class="servico.ativo ? 'btn--danger' : 'btn--success'"
              @click="showConfirm = true"
            >
              {{ servico.ativo ? 'Desativar serviço' : 'Ativar serviço' }}
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>

  <!-- Edit modal -->
  <Teleport to="body">
    <div v-if="showEdit" class="modal-backdrop" @click.self="showEdit = false">
      <div class="modal">
        <div class="modal-hd">
          <span class="modal-hd-title">Editar Serviço</span>
          <button class="modal-close" @click="showEdit = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="field">
            <label>Nome *</label>
            <input v-model="editForm.nome" placeholder="Ex: Revisão geral" />
          </div>
          <div class="field">
            <label>Preço base (€) *</label>
            <input v-model="editForm.preco_base" type="number" step="0.01" min="0" />
          </div>
          <p v-if="editError" class="msg-inline-err">{{ editError }}</p>
          <p v-if="editOk"    class="msg-inline-ok">Guardado com sucesso.</p>
        </div>
        <div class="modal-ft">
          <button class="btn btn--ghost btn--sm" @click="showEdit = false">Cancelar</button>
          <button class="btn btn--primary" :disabled="editing" @click="submitEdit">
            {{ editing ? 'A guardar…' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Confirm toggle modal -->
  <Teleport to="body">
    <div v-if="showConfirm" class="modal-backdrop" @click.self="showConfirm = false">
      <div class="modal modal--sm">
        <div class="modal-hd">
          <span class="modal-hd-title">Confirmar ação</span>
          <button class="modal-close" @click="showConfirm = false">✕</button>
        </div>
        <div class="modal-body">
          <p class="confirm-msg">
            Tem a certeza que pretende <strong>{{ servico?.ativo ? 'desativar' : 'ativar' }}</strong> o serviço "{{ servico?.nome }}"?
          </p>
          <p v-if="toggleError" class="msg-inline-err">{{ toggleError }}</p>
        </div>
        <div class="modal-ft">
          <button class="btn btn--ghost btn--sm" @click="showConfirm = false">Cancelar</button>
          <button
            class="btn btn--sm"
            :class="servico?.ativo ? 'btn--danger' : 'btn--success'"
            :disabled="toggling"
            @click="confirmToggle"
          >
            {{ toggling ? 'A processar…' : servico?.ativo ? 'Desativar' : 'Ativar' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.page { padding: 2rem; }
.back-row { margin-bottom: 1.25rem; }
.btn-back { background: none; border: none; color: #6b7280; font-size: 0.875rem; font-weight: 500; cursor: pointer; padding: 0; }
.btn-back:hover { color: #1abc9c; }

.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.avatar { width: 48px; height: 48px; border-radius: 10px; background: #1abc9c; color: #fff; font-size: 1.25rem; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.header-info h1 { margin: 0; font-size: 1.4rem; font-weight: 700; color: #111827; }
.sub { margin: 0.2rem 0 0; font-size: 0.85rem; color: #6b7280; }
.header-chips { display: flex; align-items: center; gap: 0.5rem; }

.layout { display: grid; grid-template-columns: 1fr 320px; gap: 1.5rem; align-items: start; }
@media (max-width: 800px) { .layout { grid-template-columns: 1fr; } }
.col { display: flex; flex-direction: column; gap: 1.25rem; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 1.5rem; }
.card-hd { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; }
.card-title { font-size: 0.72rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }

.info-list { margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.75rem; }
.info-row { display: flex; align-items: baseline; gap: 0.5rem; }
.info-row dt { font-size: 0.8rem; font-weight: 600; color: #6b7280; min-width: 90px; flex-shrink: 0; }
.info-row dd { margin: 0; font-size: 0.9rem; color: #111827; font-weight: 500; }
.price { color: #1abc9c; font-weight: 700; }

.zone-card { border-left: 3px solid; }
.zone-card--danger  { border-color: #fca5a5; }
.zone-card--success { border-color: #6ee7b7; }
.zone-desc { font-size: 0.875rem; color: #6b7280; line-height: 1.5; margin: 0 0 1rem; }

.chip { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
.chip--green { background: #dcfce7; color: #166534; }
.chip--gray  { background: #f1f5f9; color: #64748b; }

.btn { padding: 0.55rem 1.2rem; border: none; border-radius: 7px; font-size: 0.875rem; font-weight: 600; cursor: pointer; transition: opacity 0.15s; white-space: nowrap; }
.btn:hover    { opacity: 0.85; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--ghost   { background: #f1f5f9; color: #374151; border: 1px solid #d1d5db; }
.btn--danger  { background: #ef4444; color: #fff; }
.btn--success { background: #22c55e; color: #fff; }
.btn--sm      { padding: 0.4rem 0.85rem; font-size: 0.825rem; }

.msg-loading    { padding: 2rem; text-align: center; color: #9ca3af; }
.msg-error      { padding: 2rem; text-align: center; color: #dc2626; }
.msg-inline-ok  { color: #059669; font-size: 0.85rem; margin: 0.5rem 0 0; font-weight: 500; }
.msg-inline-err { color: #dc2626; font-size: 0.85rem; margin: 0.5rem 0 0; }

.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 12px; width: 100%; max-width: 420px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); overflow: hidden; }
.modal--sm { max-width: 360px; }
.modal-hd { display: flex; align-items: center; justify-content: space-between; padding: 1.25rem 1.5rem; border-bottom: 1px solid #f1f5f9; }
.modal-hd-title { font-size: 1rem; font-weight: 700; color: #111827; }
.modal-close { background: none; border: none; font-size: 1rem; color: #9ca3af; cursor: pointer; padding: 0.25rem; }
.modal-close:hover { color: #374151; }
.modal-body { padding: 1.5rem; }
.modal-ft { display: flex; justify-content: flex-end; gap: 0.75rem; padding: 1rem 1.5rem; border-top: 1px solid #f1f5f9; }

.field { display: flex; flex-direction: column; gap: 0.3rem; margin-bottom: 1rem; }
.field label { font-size: 0.8rem; font-weight: 600; color: #374151; }
.field input { padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 7px; font-size: 0.875rem; color: #374151; outline: none; width: 100%; box-sizing: border-box; }
.field input:focus { border-color: #1abc9c; box-shadow: 0 0 0 3px rgba(26,188,156,0.12); }

.confirm-msg { font-size: 0.9rem; color: #374151; line-height: 1.5; margin: 0; }
</style>
