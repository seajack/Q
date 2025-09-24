<template>
  <div :class="cardClasses">
    <div v-if="$slots.header" class="modern-card-header">
      <slot name="header"></slot>
    </div>
    <div class="modern-card-body">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="modern-card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'default' | 'elevated' | 'interactive'
  size?: 'sm' | 'md' | 'lg'
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  hover?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
  shadow: 'sm',
  hover: false
})

const cardClasses = computed(() => [
  'modern-card',
  `modern-card-${props.variant}`,
  `modern-card-${props.size}`,
  `shadow-${props.shadow}`,
  {
    'modern-card-hover': props.hover
  }
])
</script>

<style scoped>
.modern-card-sm .modern-card-body {
  padding: var(--spacing-4);
}

.modern-card-sm .modern-card-header,
.modern-card-sm .modern-card-footer {
  padding: var(--spacing-3) var(--spacing-4);
}

.modern-card-lg .modern-card-body {
  padding: var(--spacing-8);
}

.modern-card-lg .modern-card-header,
.modern-card-lg .modern-card-footer {
  padding: var(--spacing-6) var(--spacing-8);
}

.modern-card-hover {
  transition: all var(--duration-normal) var(--ease-out);
}

.modern-card-hover:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}
</style>