<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPeca } from '../../services/pecas.js'
import { getStock, updateStockMinimo } from '../../services/stock.js'
import { useAuthStore } from '../../store/auth.js'
import LoadingSpinner from '../../components/ui/LoadingSpinner.vue'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()
const perfil        = auth.getCurrentUser?.perfil
const lojaIdUsuario = auth.getCurrentUser?.loja_id

const isGestao = computed(() => ['ADMINISTRADOR', 'GERENTE_LOJA'].includes(perfil))

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
    const [pecaRes, stockRes] = await Promise.all([
      getPeca(route.params.id),
      getStock({ page_size: 100 }),
    ])
    peca.value  = pecaRes.data.data
    stock.value = (stockRes.data.data || []).filter(s => s.peca_id === Number(route.params.id))
  } catch {
    peca.value = null
  } finally {
    loading.value = false
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
        <p class="ref mono">{{ peca.referencia }}</p>
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

        <!-- ── Right column — other lojas ─────────────────────────── -->
        <div class="right">
          <div class="card">
            <div class="card-title">Outras Lojas</div>
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
              <p v-if="editMinError && otherLojasStock.some(s => s.loja_id === editingLojaId)" class="edit-error">{{ editMinError }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page { padding: 2rem; }

.back-row { margin-bottom: 1rem; }
.btn-back { background: none; border: none; color: #1abc9c; font-size: 0.9rem; font-weight: 500; cursor: pointer; padding: 0; }
.btn-back:hover { text-decoration: underline; }

.page-header { margin-bottom: 1.75rem; }
.header-top { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.35rem; }
.header-top h1 { margin: 0; font-size: 1.5rem; color: #111827; }
.ref { margin: 0; font-size: 0.85rem; color: #6b7280; }
.mono { font-family: 'Courier New', monospace; }

.badge { display: inline-block; padding: 0.2rem 0.65rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
.badge--cat     { background: #dbeafe; color: #1e40af; }
.badge--inativo { background: #f3f4f6; color: #6b7280; }

.layout { display: grid; grid-template-columns: 1fr 340px; gap: 1.5rem; align-items: start; }
@media (max-width: 860px) { .layout { grid-template-columns: 1fr; } }
.left, .right { display: flex; flex-direction: column; gap: 1.25rem; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 1.5rem; }
.card-title { font-size: 0.75rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; }

.descricao { color: #374151; line-height: 1.65; font-size: 0.925rem; margin: 0; }

.specs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.spec-item { display: flex; flex-direction: column; gap: 0.2rem; }
.spec-label { font-size: 0.72rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.04em; }
.spec-value { font-size: 0.925rem; color: #111827; font-weight: 500; }
.price { color: #1abc9c; font-weight: 700; }
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
</style>
