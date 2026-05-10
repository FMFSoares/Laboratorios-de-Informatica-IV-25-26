<script setup>
defineProps({
  estado: { type: String, required: true },
})

const LABELS = {
  PENDENTE: 'Pendente',
  EM_DIAGNOSTICO: 'Em Diagnóstico',
  AGUARDA_APROVACAO: 'Aguarda Aprovação',
  EM_REPARACAO: 'Em Reparação',
  AGUARDA_PECAS: 'Aguarda Peças',
  CONCLUIDA: 'Concluída',
  FATURADA: 'Faturada',
  CANCELADA: 'Cancelada',
}

const COLORS = {
  PENDENTE: 'badge--grey',
  EM_DIAGNOSTICO: 'badge--blue',
  AGUARDA_APROVACAO: 'badge--orange',
  EM_REPARACAO: 'badge--indigo',
  AGUARDA_PECAS: 'badge--yellow',
  CONCLUIDA: 'badge--green',
  FATURADA: 'badge--teal',
  CANCELADA: 'badge--red',
}
</script>

<template>
  <span class="badge" :class="COLORS[estado] || 'badge--grey'">
    {{ LABELS[estado] || estado }}
  </span>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge--grey   { background: #e5e7eb; color: #374151; }
.badge--blue   { background: #dbeafe; color: #1d4ed8; }
.badge--orange { background: #fed7aa; color: #c2410c; }
.badge--indigo { background: #e0e7ff; color: #4338ca; }
.badge--yellow { background: #fef9c3; color: #a16207; }
.badge--green  { background: #dcfce7; color: #15803d; }
.badge--teal   { background: #ccfbf1; color: #0f766e; }
.badge--red    { background: #fee2e2; color: #b91c1c; }
</style>
