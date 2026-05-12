<script setup>
import { ref } from 'vue'
import { adicionarObservacao } from '../services/ordensServico.js'

const props = defineProps({
  observacoes: { type: Array, required: true },
  osId: { type: Number, required: true },
  canAdd: { type: Boolean, default: false },
})
const emit = defineEmits(['refresh'])

const novaObs = ref('')
const obsLoading = ref(false)

const OBS_LABEL_COLORS = {
  'Conclusão do Diagnóstico': '#6366f1',
  'Conclusão da Reparação':   '#1abc9c',
  'Cancelamento':             '#dc2626',
}

function parseObs(texto) {
  const m = texto.match(/^\[([^\]]+)\]\s*(.*)$/s)
  if (m) return { label: m[1], body: m[2], color: OBS_LABEL_COLORS[m[1]] ?? '#6b7280' }
  return { label: null, body: texto, color: null }
}

function fmtDateTime(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('pt-PT', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

async function submitObs() {
  if (!novaObs.value.trim()) return
  obsLoading.value = true
  try {
    await adicionarObservacao(props.osId, { texto: novaObs.value.trim() })
    novaObs.value = ''
    emit('refresh')
  } catch {
    // silently — parent will still reload
  } finally {
    obsLoading.value = false
  }
}
</script>

<template>
  <div class="card">
    <div class="card-title">Observações Internas</div>
    <div v-if="observacoes.length === 0" class="empty-msg">Sem observações.</div>
    <div v-else class="obs-list">
      <div v-for="obs in observacoes" :key="obs.id" class="obs-item">
        <div class="obs-header">
          <span class="obs-autor">{{ obs.autor_nome }}</span>
          <span class="obs-date">{{ fmtDateTime(obs.criado_em) }}</span>
        </div>
        <template v-if="parseObs(obs.texto).label">
          <span
            class="obs-label"
            :style="{ color: parseObs(obs.texto).color, borderColor: parseObs(obs.texto).color }"
          >
            {{ parseObs(obs.texto).label }}
          </span>
          <p class="obs-text">{{ parseObs(obs.texto).body }}</p>
        </template>
        <p v-else class="obs-text">{{ obs.texto }}</p>
      </div>
    </div>
    <div v-if="canAdd" class="obs-form">
      <textarea v-model="novaObs" rows="3" placeholder="Adicionar observação..." />
      <button
        class="btn btn--primary btn--sm"
        :disabled="obsLoading || !novaObs.trim()"
        @click="submitObs"
      >
        {{ obsLoading ? 'A guardar...' : 'Adicionar' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
}

.card-title {
  font-size: 0.78rem;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.obs-list { display: flex; flex-direction: column; gap: 0.6rem; margin-bottom: 0.75rem; }
.obs-item { background: #f9fafb; border-radius: 6px; padding: 0.7rem; }
.obs-header { display: flex; justify-content: space-between; margin-bottom: 0.3rem; }
.obs-autor { font-size: 0.82rem; font-weight: 600; color: #374151; }
.obs-date { font-size: 0.75rem; color: #9ca3af; }
.obs-label {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid;
  border-radius: 4px;
  padding: 0.1rem 0.45rem;
  margin-bottom: 0.35rem;
}
.obs-text { font-size: 0.875rem; color: #374151; line-height: 1.5; margin: 0; }

.obs-form { display: flex; flex-direction: column; gap: 0.5rem; }
.obs-form textarea { resize: vertical; }

.empty-msg { color: #6b7280; font-size: 0.875rem; margin-bottom: 0.75rem; }

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
  align-self: flex-start;
}
.btn:hover { opacity: 0.85; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: #1abc9c; color: #fff; }
.btn--sm { padding: 0.4rem 0.8rem; font-size: 0.825rem; }
</style>
