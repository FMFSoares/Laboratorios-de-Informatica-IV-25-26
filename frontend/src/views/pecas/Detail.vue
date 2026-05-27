<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPeca, updatePeca } from '../../services/pecas.js'
import { getStock, updateStockMinimo } from '../../services/stock.js'
import { criarTransferencia } from '../../services/transferencias.js'
import { useAuthStore } from '../../store/auth.js'
import LoadingSpinner from '../../components/ui/LoadingSpinner.vue'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()
const lojaIdUsuario = auth.getCurrentUser?.loja_id

const isAdmin  = computed(() => auth.getCurrentUser?.perfil === 'ADMINISTRADOR')
const isGestao = computed(() => ['ADMINISTRADOR', 'GERENTE_LOJA'].includes(auth.getCurrentUser?.perfil))

const peca    = ref(null)
const stock   = ref([])
const loading = ref(true)

const CATEGORIA_LABELS = {
  BATERIA: 'Bateria', PNEU: 'Pneu', TRAVAO: 'Travão', MOTOR: 'Motor',
  CONTROLADOR: 'Controlador', LUZ: 'Luz', ACESSORIO: 'Acessório', OUTRO: 'Outro',
}

const myLojaStock     = computed(() => stock.value.filter(s => s.loja_id === lojaIdUsuario))
const otherLojasStock = computed(() => stock.value.filter(s => s.loja_id !== lojaIdUsuario))

async function load() {
  loading.value = true
  try {
    const pecaRes = await getPeca(route.params.id)
    peca.value = pecaRes.data.data
  } catch {
    peca.value = null
  } finally {
    loading.value = false
  }
  // Stock fetch is independent — failure must not hide the peca
  try {
    const stockRes = await getStock({ peca_id: route.params.id })
    stock.value = stockRes.data.data || []
  } catch {
    stock.value = []
  }
}

onMounted(load)

// ── Edit minimum ──────────────────────────────────────────────────────
const editingLojaId  = ref(null)
const editMinValue   = ref(0)
const editMinError   = ref('')

function startEdit(s) {
  if (!isGestao.value || editingLojaId.value === s.loja_id) return
  editingLojaId.value = s.loja_id
  editMinValue.value  = s.limite_minimo
  editMinError.value  = ''
}

function cancelEdit() {
  editingLojaId.value = null
  editMinError.value  = ''
}

async function saveMin(lojaId) {
  editMinError.value = ''
  try {
    await updateStockMinimo(peca.value.id, { loja_id: lojaId, limite_minimo: editMinValue.value })
    editingLojaId.value = null
    await load()
  } catch (e) {
    editMinError.value = e?.response?.data?.detail?.detail ?? 'Erro ao atualizar mínimo.'
  }
}

function fmtEur(v) {
  return v != null ? `${Number(v).toFixed(2)} €` : '—'
}

// ── Edit form ─────────────────────────────────────────────────────────
const CATEGORIAS = ['BATERIA', 'PNEU', 'TRAVAO', 'MOTOR', 'CONTROLADOR', 'LUZ', 'ACESSORIO', 'OUTRO']
const CAT_LABEL  = { BATERIA: 'Bateria', PNEU: 'Pneu', TRAVAO: 'Travão', MOTOR: 'Motor', CONTROLADOR: 'Controlador', LUZ: 'Luz', ACESSORIO: 'Acessório', OUTRO: 'Outro' }

const showEdit  = ref(false)
const editForm  = ref({})
const saving    = ref(false)
const saveError = ref('')
const saveOk    = ref(false)

function openEdit() {
  editForm.value = {
    nome:        peca.value.nome,
    categoria:   peca.value.categoria,
    descricao:   peca.value.descricao ?? '',
    unidade:     peca.value.unidade,
    preco_custo: peca.value.preco_custo ?? '',
    preco_venda: peca.value.preco_venda,
  }
  saveError.value = ''
  saveOk.value    = false
  showEdit.value  = true
}

async function submitEdit() {
  if (!editForm.value.nome || !editForm.value.categoria) { saveError.value = 'Nome e categoria são obrigatórios.'; return }
  if (editForm.value.preco_venda === '' || editForm.value.preco_venda == null) { saveError.value = 'Preço de venda é obrigatório.'; return }

  saving.value    = true
  saveError.value = ''
  try {
    await updatePeca(peca.value.id, {
      nome:        editForm.value.nome,
      categoria:   editForm.value.categoria,
      descricao:   editForm.value.descricao || null,
      unidade:     editForm.value.unidade,
      preco_custo: editForm.value.preco_custo !== '' ? parseFloat(editForm.value.preco_custo) : undefined,
      preco_venda: parseFloat(editForm.value.preco_venda),
    })
    saveOk.value = true
    await load()
    setTimeout(() => { saveOk.value = false; showEdit.value = false }, 900)
  } catch (e) {
    saveError.value = e?.response?.data?.detail?.detail ?? e?.response?.data?.detail ?? 'Erro ao guardar.'
  } finally {
    saving.value = false
  }
}

// ── Deactivate confirm ────────────────────────────────────────────────
const showConfirm = ref(false)
const toggling    = ref(false)
const toggleError = ref('')

async function confirmToggle() {
  toggling.value    = true
  toggleError.value = ''
  try {
    await updatePeca(peca.value.id, { ativo: !peca.value.ativo })
    showConfirm.value = false
    await load()
  } catch (e) {
    toggleError.value = e?.response?.data?.detail?.detail ?? 'Erro ao alterar estado.'
  } finally {
    toggling.value = false
  }
}

// ── Transfer request modal ────────────────────────────────────────────
const canRequest     = computed(() => auth.getCurrentUser?.perfil === 'GERENTE_LOJA')
const showModal      = ref(false)
const modalLojaId    = ref('')
const modalQty       = ref(1)
const modalObs       = ref('')
const modalLoading   = ref(false)
const modalError     = ref('')
const modalSuccess   = ref(false)

const availableLojas = computed(() =>
  otherLojasStock.value
    .map(s => ({ ...s, disponivel: Math.max(0, s.quantidade - s.limite_minimo) }))
    .filter(s => s.disponivel > 0)
)

const selectedLoja = computed(() =>
  availableLojas.value.find(s => s.loja_id === Number(modalLojaId.value)) ?? null
)

function openModal() {
  modalLojaId.value  = String(availableLojas.value[0]?.loja_id ?? '')
  modalQty.value     = 1
  modalObs.value     = ''
  modalError.value   = ''
  modalSuccess.value = false
  showModal.value    = true
}

async function submitModal() {
  modalError.value   = ''
  modalLoading.value = true
  try {
    await criarTransferencia({
      loja_origem_id: Number(modalLojaId.value),
      peca_id:        peca.value.id,
      quantidade:     modalQty.value,
      observacoes:    modalObs.value || null,
    })
    modalSuccess.value = true
  } catch (e) {
    console.error('[submitModal] error:', e)
    const detail = e.response?.data?.detail
    let msg
    if (typeof detail === 'string') {
      msg = detail
    } else if (Array.isArray(detail)) {
      msg = detail.map(d => d.msg ?? JSON.stringify(d)).join('; ')
    } else if (detail) {
      msg = JSON.stringify(detail)
    } else if (e.message) {
      msg = e.message
    } else {
      msg = 'Erro ao enviar pedido.'
    }
    modalError.value = msg
  } finally {
    modalLoading.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="back-row">
      <button class="btn-back" @click="router.back()">← Voltar</button>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="!peca" class="empty">Peça não encontrada.</div>

    <template v-else>
      <!-- ── Header ───────────────────────────────────────────────── -->
      <div class="page-header">
        <div class="header-top">
          <h1>{{ peca.nome }}</h1>
          <span class="badge badge--cat">{{ CATEGORIA_LABELS[peca.categoria] ?? peca.categoria }}</span>
          <span v-if="!peca.ativo" class="badge badge--inativo">Inativo</span>
        </div>
        <div class="header-bottom">
          <p class="ref mono">{{ peca.referencia }}</p>
          <button v-if="isAdmin" class="btn-edit" @click="openEdit">Editar peça</button>
        </div>
      </div>

      <div class="layout">
        <!-- ── Left column ─────────────────────────────────────────── -->
        <div class="left">
          <div class="card">
            <div class="card-title">Descrição</div>
            <p class="descricao">{{ peca.descricao ?? 'Sem descrição disponível.' }}</p>
          </div>

          <div class="card">
            <div class="card-title">Especificações</div>
            <div class="specs-grid">
              <div class="spec-item">
                <span class="spec-label">Unidade</span>
                <span class="spec-value">{{ peca.unidade }}</span>
              </div>
              <div class="spec-item">
                <span class="spec-label">Preço de Venda</span>
                <span class="spec-value price">{{ fmtEur(peca.preco_venda) }}</span>
              </div>
              <template v-if="isGestao">
                <div class="spec-item">
                  <span class="spec-label">Preço de Custo</span>
                  <span class="spec-value price--cost">{{ peca.preco_custo != null ? fmtEur(peca.preco_custo) : '—' }}</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">Margem</span>
                  <span class="spec-value price--margin">
                    <template v-if="peca.preco_custo != null && peca.preco_venda > 0">
                      {{ (((peca.preco_venda - peca.preco_custo) / peca.preco_venda) * 100).toFixed(1) }}%
                    </template>
                    <template v-else>—</template>
                  </span>
                </div>
              </template>
              <div class="spec-item">
                <span class="spec-label">Categoria</span>
                <span class="spec-value">{{ CATEGORIA_LABELS[peca.categoria] ?? peca.categoria }}</span>
              </div>
              <div class="spec-item">
                <span class="spec-label">Estado</span>
                <span :class="['spec-value', peca.ativo ? 'text--ok' : 'text--inactive']">
                  {{ peca.ativo ? 'Ativo' : 'Inativo' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Current loja stock -->
          <div class="card" v-if="myLojaStock.length > 0">
            <div class="card-title">A Minha Loja</div>
            <div class="stock-list">
              <div
                v-for="s in myLojaStock"
                :key="s.loja_id"
                :class="[
                  'stock-row',
                  s.quantidade === 0 && 'stock-row--esgotado',
                  s.alerta && s.quantidade > 0 && isGestao && 'stock-row--alerta',
                  isGestao && editingLojaId !== s.loja_id && 'stock-row--clickable',
                ]"
                :title="isGestao && editingLojaId !== s.loja_id ? 'Clique para editar o mínimo' : undefined"
                @click="startEdit(s)"
              >
                <div class="stock-loja">{{ s.loja_nome }}</div>
                <div class="stock-sep"></div>
                <div class="stock-bottom">
                  <div class="stock-numbers">
                    <div class="stock-qty">
                      <span class="stock-num" :class="s.quantidade === 0 && 'num--zero'">{{ s.quantidade }}</span>
                      <span class="stock-unit">em stock</span>
                    </div>
                    <div v-if="isGestao" class="stock-min">
                      <template v-if="editingLojaId === s.loja_id">
                        <input
                          v-model.number="editMinValue"
                          type="number" min="0"
                          class="min-input"
                          @click.stop
                          @keyup.enter="saveMin(s.loja_id)"
                          @keyup.esc="cancelEdit"
                        />
                        <button class="btn-icon btn-icon--ok" @click.stop="saveMin(s.loja_id)">✓</button>
                        <button class="btn-icon btn-icon--cancel" @click.stop="cancelEdit">✕</button>
                      </template>
                      <template v-else>
                        <span class="stock-num stock-num--min">{{ s.limite_minimo }}</span>
                        <span class="stock-unit">mínimo</span>
                        <span class="edit-hint">✎</span>
                      </template>
                    </div>
                  </div>
                  <div v-if="isGestao" class="stock-badge-wrap">
                    <span v-if="s.quantidade === 0" class="sbadge sbadge--esgotado">Esgotado</span>
                    <span v-else-if="s.alerta"      class="sbadge sbadge--alerta">Alerta</span>
                    <span v-else                     class="sbadge sbadge--ok">OK</span>
                  </div>
                </div>
              </div>
              <p v-if="editMinError && myLojaStock.some(s => s.loja_id === editingLojaId)" class="edit-error">{{ editMinError }}</p>
            </div>
          </div>
        </div>

        <!-- ── Right column — other lojas + estado ───────────────── -->
        <div class="right">
          <div v-if="isAdmin" class="card zone-card" :class="peca.ativo ? 'zone-card--danger' : 'zone-card--success'">
            <div class="card-title" style="margin-bottom:0.75rem">Estado da Peça</div>
            <p class="zone-desc">
              <template v-if="peca.ativo">
                Desativar impede que esta peça apareça em novas ordens de serviço.
              </template>
              <template v-else>
                Reativar permite que a peça volte a ser usada em ordens de serviço.
              </template>
            </p>
            <button class="btn" :class="peca.ativo ? 'btn--danger' : 'btn--success'" @click="showConfirm = true">
              {{ peca.ativo ? 'Desativar peça' : 'Ativar peça' }}
            </button>
          </div>

          <div class="card">
            <div class="card-header-row">
              <div class="card-title">Outras Lojas</div>
              <button v-if="canRequest && availableLojas.length > 0" class="btn-request" @click="openModal">
                Pedir Transferência
              </button>
            </div>
            <div v-if="otherLojasStock.length === 0" class="empty-msg">
              {{ stock.length === 0 ? 'Sem stock registado.' : 'Sem stock noutras lojas.' }}
            </div>
            <div v-else class="stock-list">
              <div
                v-for="s in otherLojasStock"
                :key="s.loja_id"
                :class="[
                  'stock-row',
                  s.quantidade === 0 && 'stock-row--esgotado',
                  s.alerta && s.quantidade > 0 && isGestao && 'stock-row--alerta',
                ]"
              >
                <div class="stock-loja">{{ s.loja_nome }}</div>
                <div class="stock-sep"></div>
                <div class="stock-bottom">
                  <div class="stock-numbers">
                    <div class="stock-qty">
                      <span class="stock-num" :class="s.quantidade === 0 && 'num--zero'">{{ s.quantidade }}</span>
                      <span class="stock-unit">em stock</span>
                    </div>
                  </div>
                  <div class="stock-badge-wrap" v-if="isGestao">
                    <span v-if="s.quantidade === 0" class="sbadge sbadge--esgotado">Esgotado</span>
                    <span v-else-if="s.alerta"      class="sbadge sbadge--alerta">Alerta</span>
                    <span v-else                    class="sbadge sbadge--ok">OK</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>

  <!-- Confirm toggle modal -->
  <Teleport to="body">
    <div v-if="showConfirm" class="overlay" @click.self="showConfirm = false">
      <div class="modal modal--sm">
        <h2 class="modal-title">Confirmar ação</h2>
        <p class="confirm-msg">
          Tem a certeza que pretende <strong>{{ peca?.ativo ? 'desativar' : 'ativar' }}</strong> a peça "{{ peca?.nome }}"?
        </p>
        <p v-if="toggleError" class="field-error">{{ toggleError }}</p>
        <div class="modal-footer">
          <button class="btn btn--ghost" @click="showConfirm = false">Cancelar</button>
          <button
            class="btn"
            :class="peca?.ativo ? 'btn--danger' : 'btn--primary'"
            :disabled="toggling"
            @click="confirmToggle"
          >
            {{ toggling ? 'A processar…' : peca?.ativo ? 'Desativar' : 'Ativar' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Edit modal (admin only) -->
  <Teleport to="body">
    <div v-if="showEdit" class="overlay" @click.self="showEdit = false">
      <div class="modal">
        <h2 class="modal-title">Editar Peça</h2>
        <p class="modal-sub">{{ peca?.referencia }}</p>

        <div class="field-row">
          <div class="field">
            <label>Nome *</label>
            <input v-model="editForm.nome" type="text" />
          </div>
          <div class="field">
            <label>Categoria *</label>
            <select v-model="editForm.categoria">
              <option v-for="c in CATEGORIAS" :key="c" :value="c">{{ CAT_LABEL[c] }}</option>
            </select>
          </div>
        </div>

        <div class="field">
          <label>Descrição</label>
          <textarea v-model="editForm.descricao" rows="2" placeholder="Detalhes técnicos…" />
        </div>

        <div class="field-row">
          <div class="field">
            <label>Unidade</label>
            <input v-model="editForm.unidade" type="text" />
          </div>
          <div class="field">
            <label>Preço Custo (€)</label>
            <input v-model="editForm.preco_custo" type="number" step="0.01" min="0" />
          </div>
          <div class="field">
            <label>Preço Venda (€) *</label>
            <input v-model="editForm.preco_venda" type="number" step="0.01" min="0" />
          </div>
        </div>

        <p v-if="saveError" class="field-error">{{ saveError }}</p>
        <p v-if="saveOk" class="field-ok">Guardado com sucesso.</p>

        <div class="modal-footer">
          <button class="btn btn--ghost" @click="showEdit = false">Cancelar</button>
          <button class="btn btn--primary" :disabled="saving" @click="submitEdit">
            {{ saving ? 'A guardar…' : 'Guardar alterações' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Transfer request modal -->
  <Teleport to="body">
    <div v-if="showModal" class="overlay" @click.self="showModal = false">
      <div class="modal">
        <h2 class="modal-title">Pedir Transferência</h2>
        <p class="modal-sub">{{ peca?.nome }}</p>

        <div v-if="modalSuccess" class="modal-success">
          Pedido enviado! O gerente da loja de origem receberá uma notificação.
          <div class="modal-footer">
            <button class="btn btn--primary" @click="showModal = false">Fechar</button>
          </div>
        </div>

        <template v-else>
          <div class="field">
            <label>Loja de origem</label>
            <select v-model="modalLojaId">
              <option v-for="s in availableLojas" :key="s.loja_id" :value="String(s.loja_id)">
                {{ s.loja_nome }} — {{ s.disponivel }} disponível{{ s.disponivel !== 1 ? 'is' : '' }}
              </option>
            </select>
          </div>
          <div class="field">
            <label>Quantidade</label>
            <input
              v-model.number="modalQty"
              type="number" min="1"
              :max="selectedLoja?.disponivel ?? 999"
            />
            <span v-if="selectedLoja" class="field-hint">Máximo pedível: {{ selectedLoja.disponivel }}</span>
          </div>
          <div class="field">
            <label>Observações (opcional)</label>
            <textarea v-model="modalObs" rows="2" placeholder="Motivo ou notas..." />
          </div>

          <p v-if="modalError" class="field-error">{{ modalError }}</p>

          <div class="modal-footer">
            <button class="btn btn--ghost" @click="showModal = false">Cancelar</button>
            <button
              class="btn btn--primary"
              :disabled="modalLoading || !modalLojaId || modalQty < 1"
              @click="submitModal"
            >
              {{ modalLoading ? 'A enviar...' : 'Enviar Pedido' }}
            </button>
          </div>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.page { padding: 2rem; }

.back-row { margin-bottom: 1rem; }
.btn-back { background: none; border: none; color: #1abc9c; font-size: 0.9rem; font-weight: 500; cursor: pointer; padding: 0; }
.btn-back:hover { text-decoration: underline; }

.page-header { margin-bottom: 1.75rem; }
.header-top { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.35rem; }
.header-top h1 { margin: 0; font-size: 1.5rem; color: #111827; }
.header-bottom { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.ref { margin: 0; font-size: 0.85rem; color: #6b7280; }
.btn-edit { background: #f1f5f9; border: 1px solid #d1d5db; color: #374151; font-size: 0.82rem; font-weight: 600; padding: 0.35rem 0.85rem; border-radius: 6px; cursor: pointer; transition: background 0.12s; }
.btn-edit:hover { background: #e2e8f0; }
.mono { font-family: 'Courier New', monospace; }

.badge { display: inline-block; padding: 0.2rem 0.65rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
.badge--cat     { background: #dbeafe; color: #1e40af; }
.badge--inativo { background: #f3f4f6; color: #6b7280; }

.layout { display: grid; grid-template-columns: 1fr 340px; gap: 1.5rem; align-items: start; }
@media (max-width: 860px) { .layout { grid-template-columns: 1fr; } }
.left, .right { display: flex; flex-direction: column; gap: 1.25rem; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 1.5rem; }
.card-title { font-size: 0.75rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; }
.zone-card { border-left: 3px solid; }
.zone-card--danger  { border-color: #fca5a5; }
.zone-card--success { border-color: #6ee7b7; }
.zone-desc { font-size: 0.875rem; color: #6b7280; line-height: 1.5; margin: 0 0 1rem; }
.confirm-msg { font-size: 0.9rem; color: #374151; line-height: 1.5; margin: 0 0 0.75rem; }
.btn--danger { background: #ef4444; color: #fff; }

.descricao { color: #374151; line-height: 1.65; font-size: 0.925rem; margin: 0; }

.specs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.spec-item { display: flex; flex-direction: column; gap: 0.2rem; }
.spec-label { font-size: 0.72rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.04em; }
.spec-value { font-size: 0.925rem; color: #111827; font-weight: 500; }
.price         { color: #1abc9c; font-weight: 700; }
.price--cost   { color: #6b7280; font-weight: 700; }
.price--margin { color: #7c3aed; font-weight: 700; }
.text--ok { color: #059669; }
.text--inactive { color: #9ca3af; }

/* Stock list */
.stock-list { display: flex; flex-direction: column; gap: 0.6rem; }

.stock-row {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.stock-row--clickable { cursor: pointer; transition: background 0.12s, border-color 0.12s; }
.stock-row--clickable:hover { background: #f0fdf4; border-color: #6ee7b7; }
.stock-row--esgotado { opacity: 0.55; background: #f9fafb; }
.stock-row--alerta   { background: #fffbeb; border-color: #fde68a; }
.stock-row--alerta.stock-row--clickable:hover { background: #fef9c3; }

.stock-loja { font-size: 0.875rem; font-weight: 600; color: #374151; }
.stock-sep  { border: none; border-top: 1px solid #e5e7eb; margin: 0; }

.stock-bottom { display: flex; align-items: center; gap: 1rem; min-width: 0; }
.stock-numbers { display: flex; gap: 1.5rem; align-items: center; flex: 1; min-width: 0; }
.stock-qty, .stock-min { display: flex; align-items: baseline; gap: 0.35rem; }
.stock-num { font-size: 1.25rem; font-weight: 700; color: #111827; }
.stock-num--min { font-size: 1.1rem; color: #6b7280; }
.num--zero { color: #9ca3af; }
.stock-unit { font-size: 0.72rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.03em; }
.edit-hint {
  font-size: 0.8rem;
  color: #9ca3af;
  opacity: 0;
  transition: opacity 0.15s;
}
.stock-row--clickable:hover .edit-hint { opacity: 1; }

.min-input {
  width: 56px;
  padding: 0.25rem 0.5rem;
  border: 1px solid #1abc9c;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #111827;
  text-align: center;
  outline: none;
}

.btn-icon {
  background: none;
  border: none;
  width: 26px;
  height: 26px;
  border-radius: 5px;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-icon:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-icon--ok     { color: #059669; }
.btn-icon--ok:hover:not(:disabled) { background: #d1fae5; }
.btn-icon--cancel { color: #9ca3af; }
.btn-icon--cancel:hover { background: #f3f4f6; }

.stock-badge-wrap { margin-left: auto; flex-shrink: 0; }
.sbadge { display: inline-block; padding: 0.2rem 0.55rem; border-radius: 9999px; font-size: 0.72rem; font-weight: 600; }
.sbadge--ok       { background: #d1fae5; color: #065f46; }
.sbadge--alerta   { background: #fef3c7; color: #92400e; }
.sbadge--esgotado { background: #f3f4f6; color: #6b7280; }

.edit-error { color: #dc2626; font-size: 0.82rem; margin-top: 0.5rem; }
.empty-msg  { color: #6b7280; font-size: 0.875rem; }
.empty      { padding: 2rem; color: #6b7280; }

.card-header-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
.card-header-row .card-title { margin-bottom: 0; }
.btn-request { background: #1abc9c; color: #fff; border: none; font-size: 0.8rem; font-weight: 600; padding: 0.35rem 0.85rem; border-radius: 6px; cursor: pointer; white-space: nowrap; transition: opacity 0.15s; }
.btn-request:hover { opacity: 0.85; }

.overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 12px; padding: 1.75rem; width: 100%; max-width: 520px; max-height: 90vh; overflow-y: auto; box-shadow: 0 8px 32px rgba(0,0,0,0.15); }
.modal--sm { max-width: 380px; }
.modal-title { font-size: 1.1rem; font-weight: 700; color: #1e293b; margin: 0 0 0.15rem; }
.modal-sub { font-size: 0.85rem; color: #6b7280; margin: 0 0 1.25rem; }
.modal-success { background: #dcfce7; color: #166534; border-radius: 8px; padding: 1rem; font-size: 0.9rem; line-height: 1.5; }
.modal-footer { display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 1.25rem; }
.field-row { display: flex; gap: 0.75rem; }
.field { display: flex; flex-direction: column; gap: 0.3rem; margin-bottom: 0.9rem; flex: 1; }
.field label { font-size: 0.82rem; font-weight: 600; color: #374151; }
.field input, .field select, .field textarea { padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 7px; font-size: 0.875rem; outline: none; font-family: inherit; width: 100%; box-sizing: border-box; }
.field input:focus, .field select:focus, .field textarea:focus { border-color: #1abc9c; }
.field-hint { font-size: 0.78rem; color: #6b7280; }
.field-error { color: #dc2626; font-size: 0.85rem; margin: 0 0 0.5rem; }
.field-ok    { color: #059669; font-size: 0.85rem; margin: 0 0 0.5rem; }

.toggle-group { display: flex; border: 1px solid #d1d5db; border-radius: 7px; overflow: hidden; width: fit-content; }
.toggle-opt { background: #fff; border: none; padding: 0.45rem 1.1rem; font-size: 0.85rem; font-weight: 500; color: #6b7280; cursor: pointer; transition: background 0.12s, color 0.12s; }
.toggle-opt--on  { background: #dcfce7; color: #166534; font-weight: 700; }
.toggle-opt--off { background: #f1f5f9; color: #6b7280;  font-weight: 700; }

.btn { padding: 0.5rem 1.1rem; border-radius: 7px; font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--ghost { background: #f1f5f9; color: #374151; border: 1px solid #d1d5db; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
