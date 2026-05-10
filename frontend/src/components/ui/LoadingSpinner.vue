<script setup>
defineProps({
  size: { type: String, default: '2rem' },
})
</script>

<template>
  <div class="spinner-wrap">
    <div class="spinner" :style="{ width: size, height: size }" />
  </div>
</template>

<style scoped>
.spinner-wrap {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.spinner {
  border: 3px solid #e5e7eb;
  border-top-color: #1abc9c;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
