<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTrotinetes } from '../../services/trotinetes.js'
import DataTable from '../../components/ui/DataTable.vue'

const router = useRouter()

const trotinetes = ref([])
const loading    = ref(false)
const total      = ref(0)
const page       = ref(1)
const PAGE_SIZE  = 20

const search  = ref('')
const sortKey = ref('marca')
const sortDir = ref('asc')

let searchTimer = null

const columns = [
  { key: 'numero_serie', label: 'Nº de Série',   sortable: true },
  { key: 'marca',        label: 'Marca / Modelo', sortable: true },
  { key: 'cor',          label: 'Cor',            sortable: false },
  { key: 'ano_compra',   label: 'Ano',            sortable: true },
  { key: 'cliente_nome', label: 'Cliente',        sortable: true },
]

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: PAGE_SIZE,
    }
    if (search.value.trim()) params.query = search.value.trim()
    const { data } = await getTrotinetes(params)
    trotinetes.value = data.data ?? []
    total.value      = data.total ?? 0
  } catch {
    trotinetes.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// Debounce search — reset to page 1 on new query
watch(search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    load()
  }, 300)
})

watch(page, load)

onMounted(load)

// Client-side sort only (server already filters; we sort the current page)
const sorted = computed(() => {
  const arr = [...trotinetes.value]
  return arr.sort((a, b) => {
    let va = a[sortKey.value] ?? ''
    let vb = b[sortKey.value] ?? ''
    if (typeof va === 'string') va = va.toLowerCase()
    if (typeof vb === 'string') vb = vb.toLowerCase()
    if (va < vb) return sortDir.value === 'asc' ? -1 : 1
    if (va > vb) return sortDir.value === 'asc' ? 1 : -1
    return 0
  })
})

function handleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">Trotinetes</h1>
      <span class="total-badge">{{ total }} registos</span>
    </div>

    <div class="toolbar">
      <div class="search-wrap">
        <svg class="search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input
          v-model="search"
          class="search-input"
          type="search"
          placeholder="Série, marca, modelo ou cliente…"
        />
      </div>
    </div>

    <DataTable
      :columns="columns"
      :rows="sorted"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="PAGE_SIZE"
      :clickable="true"
      :sort-key="sortKey"
      :sort-dir="sortDir"
      row-key="id"
      empty-title="Sem trotinetes"
      empty-message="Nenhuma trotinete encontrada para os critérios actuais."
      @sort="handleSort"
      @row-click="router.push(`/trotinetes/${$event.id}`)"
      @update:page="page = $event"
    >
      <template #cell-numero_serie="{ value }">
        <span class="mono">{{ value }}</span>
      </template>

      <template #cell-marca="{ row }">
        <div class="marca-cell">
          <span class="marca-name">{{ row.marca }}</span>
          <span class="modelo-name">{{ row.modelo }}</span>
        </div>
      </template>

      <template #cell-cor="{ value }">
        <span v-if="value" class="cor-chip">{{ value }}</span>
        <span v-else class="dim">—</span>
      </template>

      <template #cell-ano_compra="{ value }">
        {{ value || '—' }}
      </template>

      <template #cell-cliente_nome="{ value }">
        <span v-if="value" class="cliente-chip">{{ value }}</span>
        <span v-else class="dim">—</span>
      </template>
    </DataTable>
  </div>
</template>

<style scoped>
.page { padding: 1.5rem 2rem; }

.page-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}
.page-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0; }
.total-badge {
  background: #f1f5f9; color: #64748b;
  font-size: 0.78rem; font-weight: 600;
  padding: 0.2rem 0.6rem; border-radius: 999px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}
.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.search-icon {
  position: absolute;
  left: 0.65rem;
  color: #9ca3af;
  pointer-events: none;
}
.search-input {
  padding: 0.5rem 0.9rem 0.5rem 2.1rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #374151;
  background: #fff;
  outline: none;
  width: 280px;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.search-input:focus {
  border-color: #1abc9c;
  box-shadow: 0 0 0 3px rgba(26,188,156,0.12);
}

.mono { font-family: monospace; font-size: 0.82rem; color: #374151; }

.marca-cell { display: flex; flex-direction: column; gap: 0.1rem; }
.marca-name { font-weight: 600; font-size: 0.875rem; color: #111827; }
.modelo-name { font-size: 0.78rem; color: #6b7280; }

.cor-chip {
  font-size: 0.8rem;
  color: #374151;
}

.cliente-chip {
  font-size: 0.85rem;
  color: #374151;
  font-weight: 500;
}

.dim { color: #d1d5db; font-size: 0.85rem; }
</style>
