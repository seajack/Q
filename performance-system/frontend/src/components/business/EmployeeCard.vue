<template>
  <div class="employee-card bg-white rounded-lg shadow-sm border border-gray-200 p-6 transition-all duration-300 hover:shadow-lg">
    <div class="flex items-start justify-between mb-4">
      <div class="flex items-center">
        <div class="w-12 h-12 rounded-lg flex items-center justify-center mr-3" :class="avatarClass">
          <i :class="avatarIcon" class="text-lg"></i>
        </div>
        <div>
          <h3 class="font-semibold text-gray-900">{{ employee.name }}</h3>
          <p class="text-sm text-gray-600">{{ employee.position }} • {{ employee.department }}</p>
        </div>
      </div>
      <StatusBadge 
        :label="employee.status" 
        :type="getStatusType(employee.status)"
        :icon="getStatusIcon(employee.status)"
      />
    </div>
    
    <div class="space-y-3 mb-4">
      <div class="flex justify-between text-sm">
        <span class="text-gray-600">职级:</span>
        <span class="text-gray-900">{{ employee.level }}</span>
      </div>
      <div class="flex justify-between text-sm">
        <span class="text-gray-600">权重:</span>
        <span class="text-gray-900 font-medium">{{ employee.weight }}x</span>
      </div>
      <div class="flex justify-between text-sm">
        <span class="text-gray-600">最近考核:</span>
        <span class="text-gray-900">{{ employee.lastEvaluation }}</span>
      </div>
    </div>
    
    <div class="flex space-x-2">
      <button 
        v-for="action in actions" 
        :key="action.key"
        class="flex-1 px-3 py-2 rounded text-sm transition-colors"
        :class="getActionClass(action)"
        @click="handleAction(action)"
      >
        <i :class="action.icon" class="mr-1"></i>
        {{ action.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import StatusBadge from '../ui/StatusBadge.vue'

interface Employee {
  id: string
  name: string
  position: string
  department: string
  level: string
  weight: number
  status: string
  lastEvaluation: string
  avatar?: string
}

interface Action {
  key: string
  label: string
  icon: string
  type: 'primary' | 'secondary' | 'danger'
  disabled?: boolean
}

interface Props {
  employee: Employee
  actions?: Action[]
}

const props = withDefaults(defineProps<Props>(), {
  actions: () => [
    { key: 'edit', label: '编辑', icon: 'fas fa-edit', type: 'primary' },
    { key: 'evaluate', label: '考核', icon: 'fas fa-star', type: 'secondary' },
    { key: 'detail', label: '详情', icon: 'fas fa-info', type: 'secondary' }
  ]
})

const emit = defineEmits<{
  actionClick: [action: Action, employee: Employee]
}>()

const avatarClass = computed(() => {
  const colors = ['bg-blue-100 text-blue-600', 'bg-green-100 text-green-600', 'bg-purple-100 text-purple-600', 'bg-yellow-100 text-yellow-600', 'bg-red-100 text-red-600']
  const index = props.employee.id.charCodeAt(0) % colors.length
  return colors[index]
})

const avatarIcon = computed(() => {
  return 'fas fa-user'
})

const getStatusType = (status: string) => {
  const statusMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    '在职': 'success',
    '离职': 'danger',
    '休假': 'warning',
    '停职': 'info'
  }
  return statusMap[status] || 'default'
}

const getStatusIcon = (status: string) => {
  const iconMap: Record<string, string> = {
    '在职': 'fas fa-check-circle',
    '离职': 'fas fa-times-circle',
    '休假': 'fas fa-clock',
    '停职': 'fas fa-pause-circle'
  }
  return iconMap[status] || 'fas fa-circle'
}

const getActionClass = (action: Action) => {
  const baseClass = 'transition-all duration-200'
  
  switch (action.type) {
    case 'primary':
      return `${baseClass} bg-blue-100 text-blue-700 hover:bg-blue-200 disabled:bg-gray-100 disabled:cursor-not-allowed`
    case 'secondary':
      return `${baseClass} bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:bg-gray-100 disabled:cursor-not-allowed`
    case 'danger':
      return `${baseClass} bg-red-100 text-red-700 hover:bg-red-200 disabled:bg-gray-100 disabled:cursor-not-allowed`
    default:
      return `${baseClass} bg-gray-100 text-gray-700 hover:bg-gray-200`
  }
}

const handleAction = (action: Action) => {
  if (!action.disabled) {
    emit('actionClick', action, props.employee)
  }
}
</script>

<style scoped>
.employee-card {
  transition: all 0.3s ease;
}

.employee-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}
</style>
