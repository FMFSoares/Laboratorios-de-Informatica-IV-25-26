<script setup>
defineProps({
  title: { type: String, default: 'Sem resultados' },
  message: { type: String, default: null },
  actionLabel: { type: String, default: null },
})

const emit = defineEmits(['action'])
</script>

<template>
  <div class="empty">
    <p class="empty__title">{{ title }}</p>
    <p v-if="message" class="empty__message">{{ message }}</p>
    <button v-if="actionLabel" class="empty__btn" @click="emit('action')">{{ actionLabel }}</button>
  </div>
</template>

<style scoped>
.empty {
  text-align: center;
  padding: 3rem 1rem;
  color: #9ca3af;
}

.empty__title {
  font-size: 1rem;
  font-weight: 600;
  color: #6b7280;
  margin: 0 0 0.5rem;
}

.empty__message {
  font-size: 0.875rem;
  margin: 0 0 1.25rem;
}

.empty__btn {
  padding: 0.6rem 1.2rem;
  background: #1abc9c;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}
.empty__btn:hover { opacity: 0.85; }
</style>
