<script setup>
defineProps({
  title: { type: String, required: true },
  value: { type: [String, Number], required: true },
  label: { type: String, default: null },
  accent: { type: String, default: '#1abc9c' },
})
</script>

<template>
  <div class="stat-card">
    <p class="stat-card__title">{{ title }}</p>
    <p class="stat-card__value" :style="{ color: accent }">{{ value }}</p>
    <p v-if="label" class="stat-card__label">{{ label }}</p>
  </div>
</template>

<style scoped>
.stat-card {
  background: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.stat-card__title {
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.stat-card__value {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}

.stat-card__label {
  margin: 0.4rem 0 0;
  font-size: 0.8rem;
  color: #9ca3af;
}
</style>
