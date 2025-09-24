<template>
  <div class="modern-progress" :class="progressClasses">
    <div 
      class="modern-progress-bar" 
      :class="barClasses"
      :style="{ width: `${percentage}%` }"
    >
      <div v-if="animated" class="modern-progress-bar-animated"></div>
    </div>
    <div v-if="showText" class="modern-progress-text">
      {{ text || `${percentage}%` }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  percentage: number
  variant?: 'primary' | 'success' | 'warning' | 'error'
  size?: 'sm' | 'md' | 'lg'
  showText?: boolean
  text?: string
  animated?: boolean
  striped?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  showText: false,
  animated: false,
  striped: false
})

const progressClasses = computed(() => [
  `modern-progress-${props.size}`
])

const barClasses = computed(() => [
  `modern-progress-bar-${props.variant}`,
  {
    'modern-progress-bar-animated': props.animated || props.striped
  }
])
</script>

<style scoped>
.modern-progress-sm {
  height: var(--spacing-1);
}

.modern-progress-lg {
  height: var(--spacing-3);
}

.modern-progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  z-index: 1;
}

.modern-progress {
  position: relative;
  display: flex;
  align-items: center;
}
</style>