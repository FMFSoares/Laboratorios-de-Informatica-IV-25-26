<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getOrdensServico } from '../../services/ordensServico.js'
import { useAuthStore } from '../../store/auth.js'
import LoadingSpinner from '../../components/ui/LoadingSpinner.vue'

const router = useRouter()
const auth = useAuthStore()

const loading = ref(true)
const hasNone = ref(false)

onMounted(async () => {
  try {
    const { data } = await getOrdensServico({
      mecanico_id: auth.getCurrentUser.id,
      page_size: 100,
    })
    const ativa = data.data.find(o => o.tem_timer_ativo)
    if (ativa) {
      router.replace(`/oficina/${ativa.id}`)
      return
    }
  } catch { /* show empty state */ }
  loading.value = false
  hasNone.value = true
})
</script>

<template>
  <div class="page">
    <LoadingSpinner v-if="loading" />

    <div v-else-if="hasNone" class="empty-state">
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
.page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 2rem;
}

.empty-state {
  text-align: center;
  max-width: 380px;
}
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.1rem; font-weight: 700; color: #374151; margin-bottom: 0.5rem; }
.empty-msg { color: #6b7280; font-size: 0.9rem; margin-bottom: 1.5rem; }

.btn { padding: 0.6rem 1.4rem; border: none; border-radius: 6px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: opacity 0.15s; }
.btn:hover { opacity: 0.85; }
.btn--secondary { background: #e5e7eb; color: #374151; }
</style>
