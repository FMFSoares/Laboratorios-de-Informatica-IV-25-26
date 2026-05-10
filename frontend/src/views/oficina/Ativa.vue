<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getOrdensServico, pararTempo } from '../../services/ordensServico.js'
import { useAuthStore } from '../../store/auth.js'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import LoadingSpinner from '../../components/ui/LoadingSpinner.vue'

const router = useRouter()
const auth = useAuthStore()

const loading = ref(true)
const pausing = ref(false)
const osAtiva = ref(null)

async function fetchAtiva() {
  try {
    const { data } = await getOrdensServico({
      mecanico_id: auth.getCurrentUser.id,
      page_size: 100,
    })
    osAtiva.value = data.data.find(o => o.tem_timer_ativo) ?? null
  } catch {
    osAtiva.value = null
  } finally {
    loading.value = false
  }
}

async function pausar() {
  if (!osAtiva.value || pausing.value) return
  pausing.value = true
  try {
    await pararTempo(osAtiva.value.id)
    osAtiva.value = null
  } catch {
    await fetchAtiva()
  } finally {
    pausing.value = false
  }
}

let pollInterval
onMounted(() => {
  fetchAtiva()
  pollInterval = setInterval(fetchAtiva, 15000)
})
onUnmounted(() => clearInterval(pollInterval))

const PRIORIDADE_COLORS = { BAIXA: '#6b7280', NORMAL: '#374151', ALTA: '#d97706', URGENTE: '#dc2626' }
</script>

<template>
  <div class="page">
    <h1>OS Activa</h1>
    <p class="sub">A ordem de serviço onde tem o timer a correr neste momento.</p>

    <LoadingSpinner v-if="loading" />

    <template v-else-if="osAtiva">
      <div class="os-card">
        <div class="os-header">
          <span class="mono os-numero">{{ osAtiva.numero }}</span>
          <StatusBadge :estado="osAtiva.estado" />
          <span class="timer-pill">● Timer activo</span>
          <span v-if="osAtiva.em_atraso" class="atraso-pill">⚠ +{{ osAtiva.minutos_em_atraso }}min</span>
        </div>

        <div class="os-meta">
          <div class="meta-item">
            <span class="meta-label">Cliente</span>
            <span>{{ osAtiva.cliente_nome || '—' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Trotinete</span>
            <span class="mono">{{ osAtiva.trotinete_numero_serie || '—' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Prioridade</span>
            <span :style="{ color: PRIORIDADE_COLORS[osAtiva.prioridade], fontWeight: 600 }">
              {{ osAtiva.prioridade }}
            </span>
          </div>
        </div>

        <div class="card-actions">
          <button
            class="btn btn--pause"
            :disabled="pausing"
            @click="pausar"
          >
            {{ pausing ? 'A pausar...' : '⏸ Pausar' }}
          </button>
          <button class="btn btn--ghost" @click="router.push(`/oficina/${osAtiva.id}`)">
            Abrir OS →
          </button>
        </div>
      </div>
    </template>

    <div v-else class="empty-state">
      <div class="empty-icon">⏱</div>
      <p class="empty-title">Nenhuma OS activa</p>
      <p class="empty-msg">Não tem nenhuma ordem de serviço com o timer a correr neste momento.</p>
      <button class="btn btn--secondary" @click="router.push('/oficina')">
        Ver todas as ordens
      </button>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 2rem; max-width: 600px; }
h1 { margin-bottom: 0.25rem; }
.sub { font-size: 0.875rem; color: #6b7280; margin-bottom: 2rem; }

.os-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
  padding: 1.75rem;
  border: 2px solid #1abc9c;
}

.os-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
}

.os-numero { font-family: 'Courier New', monospace; font-size: 1.1rem; font-weight: 700; }

.timer-pill {
  background: #f0fdf4;
  color: #1abc9c;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  border: 1px solid #1abc9c;
}

.atraso-pill {
  background: #fef3c7;
  color: #92400e;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
}

.os-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.meta-item { display: flex; flex-direction: column; gap: 0.15rem; }
.meta-label { font-size: 0.72rem; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }
.mono { font-family: 'Courier New', monospace; font-size: 0.875rem; }

.card-actions {
  display: flex;
  gap: 0.75rem;
}

/* Empty state */
.empty-state { text-align: center; padding: 4rem 2rem; }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.1rem; font-weight: 700; color: #374151; margin-bottom: 0.5rem; }
.empty-msg { color: #6b7280; font-size: 0.9rem; margin-bottom: 1.5rem; }

.btn { padding: 0.7rem 1.4rem; border: none; border-radius: 6px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: opacity 0.15s; }
.btn:hover { opacity: 0.85; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--pause { background: #d97706; color: #fff; flex: 1; }
.btn--ghost { background: transparent; border: 1px solid #d1d5db; color: #374151; }
.btn--secondary { background: #e5e7eb; color: #374151; }
.btn--primary { background: #1abc9c; color: #fff; }
</style>
