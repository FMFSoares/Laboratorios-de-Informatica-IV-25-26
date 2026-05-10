<script setup>
defineProps({
  open: { type: Boolean, required: true },
  title: { type: String, default: 'Confirmar' },
  message: { type: String, default: '' },
  confirmLabel: { type: String, default: 'Confirmar' },
  cancelLabel: { type: String, default: 'Cancelar' },
  danger: { type: Boolean, default: false },
})

const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="overlay" @click.self="emit('cancel')">
      <div class="dialog" role="dialog" :aria-label="title">
        <h2 class="dialog__title">{{ title }}</h2>
        <p v-if="message" class="dialog__message">{{ message }}</p>
        <slot />
        <div class="dialog__actions">
          <button class="btn btn--secondary" @click="emit('cancel')">{{ cancelLabel }}</button>
          <button class="btn" :class="danger ? 'btn--danger' : 'btn--primary'" @click="emit('confirm')">
            {{ confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: #fff;
  border-radius: 10px;
  padding: 2rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.dialog__title {
  margin: 0 0 0.75rem;
  font-size: 1.1rem;
  color: #111827;
}

.dialog__message {
  margin: 0 0 1.5rem;
  color: #4b5563;
  line-height: 1.5;
}

.dialog__actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}
.btn:hover { opacity: 0.85; }

.btn--primary   { background: #1abc9c; color: #fff; }
.btn--danger    { background: #dc2626; color: #fff; }
.btn--secondary { background: #e5e7eb; color: #374151; }
</style>
