<template>
  <span :class="badgeClasses">
    <slot name="icon" v-if="$slots.icon"></slot>
    <slot></slot>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral'
  size?: 'sm' | 'md' | 'lg'
  dot?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  dot: false
})

const badgeClasses = computed(() => [
  'modern-badge',
  `modern-badge-${props.variant}`,
  `modern-badge-${props.size}`,
  {
    'modern-badge-dot': props.dot
  }
])
</script>

<style scoped>
.modern-badge-sm {
  padding: var(--spacing-0-5) var(--spacing-1-5);
  font-size: 10px;
}

.modern-badge-lg {
  padding: var(--spacing-1-5) var(--spacing-3);
  font-size: var(--text-sm);
}

.modern-badge-dot {
  width: 8px;
  height: 8px;
  padding: 0;
  border-radius: 50%;
  display: inline-block;
}

.modern-badge-dot.modern-badge-sm {
  width: 6px;
  height: 6px;
}

.modern-badge-dot.modern-badge-lg {
  width: 10px;
  height: 10px;
}
</style>