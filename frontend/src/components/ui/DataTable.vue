<script setup>
import { computed } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'
import EmptyState from './EmptyState.vue'

/**
 * columns: Array<{ key: string, label: string, sortable?: boolean }>
 * rows: Array<object>
 */
const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  total: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  pageSize: { type: Number, default: 20 },
  emptyTitle: { type: String, default: 'Sem resultados' },
  emptyMessage: { type: String, default: null },
  rowKey: { type: String, default: 'id' },
  clickable: { type: Boolean, default: false },
})

const emit = defineEmits(['update:page', 'row-click'])

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))

const getValue = (row, key) => {
  return key.split('.').reduce((obj, k) => obj?.[k], row)
}
</script>

<template>
  <div class="data-table-wrap">
    <LoadingSpinner v-if="loading" />

    <template v-else>
      <div v-if="rows.length === 0">
        <EmptyState :title="emptyTitle" :message="emptyMessage" />
      </div>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col.key">{{ col.label }}</th>
            <th v-if="$slots['actions']" class="col-actions">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in rows"
            :key="row[rowKey]"
            :class="{ 'row--clickable': clickable }"
            @click="clickable && emit('row-click', row)"
          >
            <td v-for="col in columns" :key="col.key">
              <slot :name="`cell-${col.key}`" :row="row" :value="getValue(row, col.key)">
                {{ getValue(row, col.key) ?? '—' }}
              </slot>
            </td>
            <td v-if="$slots['actions']" class="col-actions">
              <slot name="actions" :row="row" />
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="total > pageSize" class="pagination">
        <button :disabled="page <= 1" @click="emit('update:page', page - 1)">‹ Anterior</button>
        <span>Página {{ page }} de {{ totalPages }}</span>
        <button :disabled="page >= totalPages" @click="emit('update:page', page + 1)">Próxima ›</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.data-table-wrap {
  width: 100%;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.data-table th {
  background: #f9fafb;
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.8rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  border-bottom: 1px solid #e5e7eb;
}

.data-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  color: #374151;
  vertical-align: middle;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.data-table tbody tr:hover {
  background: #f9fafb;
}

.row--clickable {
  cursor: pointer;
}

.col-actions {
  text-align: right;
  white-space: nowrap;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.pagination button {
  padding: 0.4rem 0.9rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  color: #374151;
}
.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.pagination button:not(:disabled):hover {
  background: #f3f4f6;
}
</style>
