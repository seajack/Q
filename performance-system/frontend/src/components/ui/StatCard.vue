<template>
  <div class="modern-stat-card" :class="cardClasses">
    <div class="modern-stat-header">
      <div class="modern-stat-icon" :class="iconClasses">
        <slot name="icon">
          <component :is="icon" v-if="icon" />
        </slot>
      </div>
      <div v-if="trend" class="modern-stat-trend" :class="trendClasses">
        <component :is="trendIcon" />
        <span>{{ trendText }}</span>
      </div>
    </div>
    <div class="modern-stat-number">{{ formatNumber(value) }}</div>
    <div class="modern-stat-label">{{ label }}</div>
    <div v-if="description" class="modern-stat-description">{{ description }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowUp, ArrowDown, Minus } from '@element-plus/icons-vue'

interface Props {
  value: number
  label: string
  description?: string
  icon?: any
  variant?: 'primary' | 'success' | 'warning' | 'error' | 'info'
  trend?: {
    value: number
    type: 'up' | 'down' | 'neutral'
  }
  format?: 'number' | 'currency' | 'percentage'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  format: 'number'
})

const cardClasses = computed(() => [
  `modern-stat-card-${props.variant}`
])

const iconClasses = computed(() => [
  `modern-stat-icon-${props.variant}`
])

const trendClasses = computed(() => {
  if (!props.trend) return []
  return [`modern-stat-trend-${props.trend.type}`]
})

const trendIcon = computed(() => {
  if (!props.trend) return null
  switch (props.trend.type) {
    case 'up': return ArrowUp
    case 'down': return ArrowDown
    default: return Minus
  }
})

const trendText = computed(() => {
  if (!props.trend) return ''
  const sign = props.trend.type === 'up' ? '+' : props.trend.type === 'down' ? '-' : ''
  return `${sign}${Math.abs(props.trend.value)}%`
})

const formatNumber = (value: number) => {
  switch (props.format) {
    case 'currency':
      return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: 'CNY'
      }).format(value)
    case 'percentage':
      return `${value}%`
    default:
      return new Intl.NumberFormat('zh-CN').format(value)
  }
}
</script>

<style scoped>
.modern-stat-card-primary::before {
  background: linear-gradient(90deg, var(--brand-primary-500) 0%, var(--brand-primary-600) 100%);
}

.modern-stat-card-success::before {
  background: linear-gradient(90deg, var(--semantic-success-500) 0%, var(--semantic-success-600) 100%);
}

.modern-stat-card-warning::before {
  background: linear-gradient(90deg, var(--semantic-warning-500) 0%, var(--semantic-warning-600) 100%);
}

.modern-stat-card-error::before {
  background: linear-gradient(90deg, var(--semantic-error-500) 0%, var(--semantic-error-600) 100%);
}

.modern-stat-card-info::before {
  background: linear-gradient(90deg, var(--semantic-info-500) 0%, var(--semantic-info-600) 100%);
}

.modern-stat-icon-primary {
  background: var(--brand-primary-50);
  color: var(--brand-primary-600);
}

.modern-stat-icon-success {
  background: var(--semantic-success-50);
  color: var(--semantic-success-600);
}

.modern-stat-icon-warning {
  background: var(--semantic-warning-50);
  color: var(--semantic-warning-600);
}

.modern-stat-icon-error {
  background: var(--semantic-error-50);
  color: var(--semantic-error-600);
}

.modern-stat-icon-info {
  background: var(--semantic-info-50);
  color: var(--semantic-info-600);
}

.modern-stat-description {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-top: var(--spacing-1);
}
</style>