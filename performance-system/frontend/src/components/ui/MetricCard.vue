<template>
  <div 
    class="metric-card p-6 rounded-lg transition-all duration-300 hover:transform hover:-translate-y-1"
    :class="cardClass"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="w-12 h-12 rounded-lg flex items-center justify-center" :class="iconClass">
        <i :class="icon" class="text-xl"></i>
      </div>
      <div class="text-right">
        <div class="text-2xl font-bold text-gray-900">{{ value }}</div>
        <div class="text-sm text-gray-600">{{ label }}</div>
      </div>
    </div>
    
    <!-- 趋势指示器 -->
    <div v-if="trend" class="flex items-center text-sm" :class="trendClass">
      <i :class="trendIcon" class="mr-1"></i>
      <span>{{ trendText }}</span>
    </div>
    
    <!-- 进度条 -->
    <div v-if="showProgress" class="mt-3">
      <div class="progress-bar h-2 rounded-full overflow-hidden">
        <div 
          class="progress-fill h-full transition-all duration-500" 
          :style="{ width: progress + '%' }"
        ></div>
      </div>
      <p class="text-xs text-gray-500 mt-1">{{ progress }}% 完成率</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Trend {
  type: 'up' | 'down' | 'stable'
  value: string
  text?: string
}

interface Props {
  value: string | number
  label: string
  icon: string
  iconColor?: string
  trend?: Trend
  showProgress?: boolean
  progress?: number
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: 'blue',
  showProgress: false,
  progress: 0,
  variant: 'default'
})

const cardClass = computed(() => {
  const baseClass = 'bg-white border border-gray-200 shadow-sm'
  const hoverClass = 'hover:shadow-lg'
  
  return `${baseClass} ${hoverClass}`
})

const iconClass = computed(() => {
  const colorMap = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600',
    gray: 'bg-gray-100 text-gray-600'
  }
  
  return colorMap[props.iconColor as keyof typeof colorMap] || colorMap.blue
})

const trendClass = computed(() => {
  if (!props.trend) return ''
  
  switch (props.trend.type) {
    case 'up':
      return 'text-green-600'
    case 'down':
      return 'text-red-600'
    case 'stable':
      return 'text-gray-600'
    default:
      return 'text-gray-600'
  }
})

const trendIcon = computed(() => {
  if (!props.trend) return ''
  
  switch (props.trend.type) {
    case 'up':
      return 'fas fa-arrow-up'
    case 'down':
      return 'fas fa-arrow-down'
    case 'stable':
      return 'fas fa-minus'
    default:
      return 'fas fa-minus'
  }
})

const trendText = computed(() => {
  if (!props.trend) return ''
  
  return props.trend.text || `${props.trend.value} 较上期`
})
</script>

<style scoped>
.metric-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.progress-bar {
  background: #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.progress-fill {
  background: linear-gradient(90deg, #2563eb, #3b82f6);
  transition: width 0.5s ease;
}
</style>
