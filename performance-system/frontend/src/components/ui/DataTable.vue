<template>
  <div class="data-table">
    <!-- 表格头部操作 -->
    <div v-if="showHeader" class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-4">
        <h3 v-if="title" class="text-lg font-semibold text-gray-900">{{ title }}</h3>
        <div v-if="filters" class="flex items-center space-x-2">
          <select 
            v-for="filter in filters" 
            :key="filter.key"
            class="border border-gray-300 rounded-lg px-3 py-1 text-sm"
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
      </div>
      <div class="flex items-center space-x-2">
        <button 
          v-for="action in actions" 
          :key="action.key"
          class="px-3 py-2 rounded-lg text-sm transition-colors"
          :class="getActionClass(action)"
          @click="handleAction(action)"
        >
          <i :class="action.icon" class="mr-1"></i>
          {{ action.label }}
        </button>
      </div>
    </div>

    <!-- 表格容器 -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th 
                v-for="column in columns" 
                :key="column.key"
                class="text-left py-3 px-4 font-medium text-gray-900"
                :class="column.class"
              >
                {{ column.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(row, index) in data" 
              :key="getRowKey(row, index)"
              class="border-b border-gray-100 hover:bg-gray-50 transition-colors"
            >
              <td 
                v-for="column in columns" 
                :key="column.key"
                class="py-4 px-4"
                :class="column.class"
              >
                <slot 
                  :name="`cell-${column.key}`" 
                  :row="row" 
                  :value="getCellValue(row, column.key)"
                  :column="column"
                >
                  {{ getCellValue(row, column.key) }}
                </slot>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 空状态 -->
      <div v-if="!data || data.length === 0" class="text-center py-12">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <i class="fas fa-inbox text-gray-400 text-xl"></i>
        </div>
        <p class="text-gray-500">{{ emptyText }}</p>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="showPagination && total > 0" class="flex items-center justify-between mt-6 pt-6 border-t border-gray-200">
      <div class="text-sm text-gray-600">
        显示 {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, total) }} 条，共 {{ total }} 条记录
      </div>
      <div class="flex space-x-2">
        <button 
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
          :disabled="currentPage <= 1"
          @click="handlePageChange(currentPage - 1)"
        >
          上一页
        </button>
        
        <button 
          v-for="page in visiblePages" 
          :key="page"
          class="px-3 py-2 rounded-lg text-sm transition-colors"
          :class="page === currentPage ? 'bg-blue-600 text-white' : 'border border-gray-300 hover:bg-gray-50'"
          @click="handlePageChange(page)"
        >
          {{ page }}
        </button>
        
        <button 
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
          :disabled="currentPage >= totalPages"
          @click="handlePageChange(currentPage + 1)"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Column {
  key: string
  label: string
  class?: string
  sortable?: boolean
}

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
  title?: string
  columns: Column[]
  data: any[]
  showHeader?: boolean
  showPagination?: boolean
  currentPage?: number
  pageSize?: number
  total?: number
  filters?: Filter[]
  actions?: Action[]
  emptyText?: string
  rowKey?: string | ((row: any) => string)
}

const props = withDefaults(defineProps<Props>(), {
  showHeader: true,
  showPagination: true,
  currentPage: 1,
  pageSize: 20,
  total: 0,
  filters: () => [],
  actions: () => [],
  emptyText: '暂无数据',
  rowKey: 'id'
})

const emit = defineEmits<{
  filterChange: [filter: Filter]
  actionClick: [action: Action]
  pageChange: [page: number]
}>()

const totalPages = computed(() => Math.ceil(props.total / props.pageSize))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, props.currentPage - 2)
  const end = Math.min(totalPages.value, props.currentPage + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const getRowKey = (row: any, index: number) => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(row)
  }
  return row[props.rowKey] || index
}

const getCellValue = (row: any, key: string) => {
  return row[key] || ''
}

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

const handleFilterChange = (filter: Filter) => {
  emit('filterChange', filter)
}

const handleAction = (action: Action) => {
  if (!action.disabled) {
    emit('actionClick', action)
  }
}

const handlePageChange = (page: number) => {
  emit('pageChange', page)
}
</script>

<style scoped>
.data-table {
  /* 自定义样式 */
}
</style>
