<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTrotinetes } from '../../services/trotinetes.js'

const router = useRouter()

const trotinetes = ref([])
const loading    = ref(false)
const search     = ref('')

async function load() {
  loading.value = true
  try {
    const { data } = await getTrotinetes({ page_size: 200 })
    trotinetes.value = data.data ?? []
  } catch {
    trotinetes.value = []
  } finally {
    loading.value = false
  }
}

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return trotinetes.value
  return trotinetes.value.filter(t =>
    (t.numero_serie || '').toLowerCase().includes(q) ||
    (t.marca        || '').toLowerCase().includes(q) ||
    (t.modelo       || '').toLowerCase().includes(q) ||
    (t.cliente_nome || '').toLowerCase().includes(q)
  )
})

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Trotinetes</h1>
    </div>

    <div class="toolbar">
      <input
        v-model="search"
        class="search-input"
        type="search"
        placeholder="Pesquisar por série, marca, modelo ou cliente…"
      />
      <span class="result-count">{{ filtered.length }} resultado{{ filtered.length !== 1 ? 's' : '' }}</span>
    </div>

    <div v-if="loading" class="msg-empty">A carregar...</div>
    <p v-else-if="filtered.length === 0" class="msg-empty">Sem trotinetes encontradas.</p>

    <table v-else class="tbl">
      <thead>
        <tr>
          <th>Nº de Série</th>
          <th>Marca / Modelo</th>
          <th>Cor</th>
          <th>Ano</th>
          <th>Cliente</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="t in filtered"
          :key="t.id"
          class="tbl-row"
          @click="router.push(`/trotinetes/${t.id}`)"
        >
          <td class="mono">{{ t.numero_serie }}</td>
          <td>{{ t.marca }} {{ t.modelo }}</td>
          <td>{{ t.cor || '—' }}</td>
          <td>{{ t.ano_compra || '—' }}</td>
          <td>{{ t.cliente_nome || '—' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.page { padding: 1.5rem 2rem; }
.page-header { margin-bottom: 1.25rem; }
.page-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0; }

.toolbar { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }
.search-input { padding: 0.5rem 0.9rem; border: 1px solid #d1d5db; border-radius: 8px; font-size: 0.875rem; color: #374151; background: #fff; outline: none; max-width: 380px; width: 100%; }
.search-input:focus { border-color: #1abc9c; box-shadow: 0 0 0 3px rgba(26,188,156,0.12); }
.result-count { margin-left: auto; font-size: 0.82rem; color: #9ca3af; }

.tbl { width: 100%; border-collapse: collapse; font-size: 0.875rem; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.tbl th { padding: 0.65rem 1rem; text-align: left; font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
.tbl td { padding: 0.75rem 1rem; border-bottom: 1px solid #f1f5f9; color: #374151; }
.tbl tbody tr:last-child td { border-bottom: none; }
.tbl-row { cursor: pointer; transition: background 0.1s; }
.tbl-row:hover { background: #f0fdf9; }

.mono { font-family: monospace; font-size: 0.82rem; }
.msg-empty { padding: 2rem; text-align: center; font-size: 0.9rem; color: #9ca3af; }
</style>
