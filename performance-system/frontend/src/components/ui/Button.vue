<template>
  <button 
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
    :type="type"
  >
    <span v-if="loading" class="loading-spinner"></span>
    <slot name="icon" v-if="!loading && $slots.icon"></slot>
    <span v-if="$slots.default" class="button-text">
      <slot></slot>
    </span>
    <slot name="suffix" v-if="!loading && $slots.suffix"></slot>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'success' | 'warning' | 'error'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  disabled?: boolean
  loading?: boolean
  block?: boolean
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  block: false,
  type: 'button'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => [
  'modern-btn',
  `modern-btn-${props.variant}`,
  `modern-btn-${props.size}`,
  {
    'modern-btn-loading': props.loading,
    'modern-btn-block': props.block,
    'modern-btn-disabled': props.disabled
  }
])

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.modern-btn-block {
  width: 100%;
}

.modern-btn-disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.button-text {
  display: inline-flex;
  align-items: center;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>