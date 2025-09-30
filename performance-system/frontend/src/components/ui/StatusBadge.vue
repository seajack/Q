<template>
  <span 
    class="status-badge px-2 py-1 rounded-full text-xs font-medium"
    :class="badgeClass"
  >
    <i v-if="icon" :class="icon" class="mr-1"></i>
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  label: string
  type?: 'success' | 'warning' | 'danger' | 'info' | 'default'
  icon?: string
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'default',
  size: 'md'
})

const badgeClass = computed(() => {
  const sizeClass = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base'
  }
  
  const typeClass = {
    success: 'bg-green-100 text-green-700',
    warning: 'bg-yellow-100 text-yellow-700',
    danger: 'bg-red-100 text-red-700',
    info: 'bg-blue-100 text-blue-700',
    default: 'bg-gray-100 text-gray-700'
  }
  
  return `${sizeClass[props.size]} ${typeClass[props.type]}`
})
</script>

<style scoped>
.status-badge {
  border-radius: 20px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
}
</style>
