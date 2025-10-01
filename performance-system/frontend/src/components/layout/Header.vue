<template>
  <header class="bg-white border-b border-gray-200 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">{{ title }}</h2>
        <p class="text-gray-600 mt-1">{{ subtitle }}</p>
      </div>
      <div class="flex items-center space-x-4">
        <!-- 搜索框 -->
        <div v-if="showSearch" class="flex items-center space-x-2">
          <input 
            type="text" 
            :placeholder="searchPlaceholder"
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm w-64"
            v-model="searchValue"
            @input="handleSearch"
          >
        </div>
        
        <!-- 筛选器 -->
        <div v-if="filters && filters.length > 0" class="flex items-center space-x-2">
          <select 
            v-for="filter in filters" 
            :key="filter.key"
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm"
            v-model="filter.value"
            @change="handleFilterChange(filter)"
          >
            <option :value="''">{{ filter.placeholder }}</option>
            <option 
              v-for="option in filter.options" 
              :key="option.value" 
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </div>
        
        <!-- 操作按钮 -->
        <div class="flex items-center space-x-2">
          <button 
            v-for="action in actions" 
            :key="action.key"
            class="px-4 py-2 rounded-lg text-sm transition-colors"
            :class="getActionClass(action)"
            @click="handleAction(action)"
          >
            <i :class="action.icon" class="mr-2"></i>
            {{ action.label }}
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface FilterOption {
  value: string
  label: string
}

interface Filter {
  key: string
  placeholder: string
  options: FilterOption[]
  value: string
}

interface Action {
  key: string
  label: string
  icon: string
  type: 'primary' | 'secondary' | 'danger'
  disabled?: boolean
}

interface Props {
  title: string
  subtitle: string
  showSearch?: boolean
  searchPlaceholder?: string
  filters?: Filter[]
  actions?: Action[]
}

const props = withDefaults(defineProps<Props>(), {
  showSearch: false,
  searchPlaceholder: '搜索...',
  filters: () => [],
  actions: () => []
})

const emit = defineEmits<{
  search: [value: string]
  filterChange: [filter: Filter]
  actionClick: [action: Action]
}>()

const searchValue = ref('')

const getActionClass = (action: Action) => {
  const baseClass = 'transition-all duration-200'
  
  switch (action.type) {
    case 'primary':
      return `${baseClass} bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed`
    case 'secondary':
      return `${baseClass} bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:bg-gray-100 disabled:cursor-not-allowed`
    case 'danger':
      return `${baseClass} bg-red-600 text-white hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed`
    default:
      return `${baseClass} bg-gray-100 text-gray-700 hover:bg-gray-200`
  }
}

const handleSearch = () => {
  emit('search', searchValue.value)
}

const handleFilterChange = (filter: Filter) => {
  emit('filterChange', filter)
}

const handleAction = (action: Action) => {
  if (!action.disabled) {
    emit('actionClick', action)
  }
}
</script>

<style scoped>
/* 自定义样式 */
</style>
