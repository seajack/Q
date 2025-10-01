<template>
  <AppLayout
    page-title="考核任务管理"
    page-subtitle="管理和分配绩效考核任务"
    :show-search="true"
    search-placeholder="搜索考核码/姓名..."
    :filters="filters"
    :actions="headerActions"
    @search="handleSearch"
    @filter-change="handleFilterChange"
    @action-click="handleHeaderAction"
  >
    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <MetricCard
        :value="totalTasks"
        label="总任务数"
        icon="fas fa-tasks"
        icon-color="blue"
      />
      <MetricCard
        :value="pendingTasks"
        label="待考核"
        icon="fas fa-clock"
        icon-color="yellow"
      />
      <MetricCard
        :value="completedTasks"
        label="已完成"
        icon="fas fa-check-circle"
        icon-color="green"
      />
      <MetricCard
        :value="overdueTasks"
        label="已过期"
        icon="fas fa-exclamation-triangle"
        icon-color="red"
      />
    </div>
    
    <!-- 考核任务列表 -->
    <DataTable
      title="考核任务列表"
      :columns="tableColumns"
      :data="filteredTasks"
      :show-pagination="true"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      :actions="tableActions"
      @action-click="handleTableAction"
      @page-change="handlePageChange"
    >
      <!-- 任务信息列 -->
      <template #cell-task="{ row }">
        <div class="flex items-center">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center mr-3" :class="getTaskIconClass(row.status)">
            <i :class="getTaskIcon(row.status)" class="text-sm"></i>
          </div>
          <div>
            <div class="font-medium text-gray-900">{{ row.evaluation_code }}</div>
            <div class="text-sm text-gray-600">{{ row.evaluator_name }} → {{ row.evaluatee_name }}</div>
          </div>
        </div>
      </template>
      
      <!-- 考核周期列 -->
      <template #cell-cycle="{ row }">
        <div class="text-sm">
          <div class="text-gray-900">{{ row.cycle_name }}</div>
          <div class="text-gray-600">{{ formatDate(row.cycle_start_date) }} - {{ formatDate(row.cycle_end_date) }}</div>
        </div>
      </template>
      
      <!-- 关系类型列 -->
      <template #cell-relation="{ row }">
        <StatusBadge 
          :label="getRelationText(row.relation_type)" 
          :type="getRelationType(row.relation_type)"
          :icon="getRelationIcon(row.relation_type)"
        />
      </template>
      
      <!-- 状态列 -->
      <template #cell-status="{ row }">
        <StatusBadge 
          :label="getStatusText(row.status)" 
          :type="getStatusType(row.status)"
          :icon="getStatusIcon(row.status)"
        />
      </template>
      
      <!-- 进度列 -->
      <template #cell-progress="{ row }">
        <div class="flex items-center space-x-2">
          <div class="flex-1 bg-gray-200 h-2 rounded-full overflow-hidden">
            <div 
              class="h-full transition-all duration-500" 
              :class="getProgressColor(row.progress)"
              :style="{ width: row.progress + '%' }"
            ></div>
          </div>
          <span class="text-sm font-medium text-gray-900">{{ row.progress }}%</span>
        </div>
      </template>
      
      <!-- 截止时间列 -->
      <template #cell-deadline="{ row }">
        <div class="text-sm">
          <div class="text-gray-900">{{ formatDate(row.deadline) }}</div>
          <div class="text-gray-600">{{ getTimeRemaining(row.deadline) }}</div>
        </div>
      </template>
      
      <!-- 操作列 -->
      <template #cell-actions="{ row }">
        <div class="flex space-x-2">
          <button 
            v-if="row.status === 'pending'"
            class="text-blue-600 hover:text-blue-800 text-sm"
            @click="handleStart(row)"
          >
            开始考核
          </button>
          <button 
            v-if="row.status === 'in_progress'"
            class="text-green-600 hover:text-green-800 text-sm"
            @click="handleContinue(row)"
          >
            继续考核
          </button>
          <button 
            v-if="row.status === 'completed'"
            class="text-gray-600 hover:text-gray-800 text-sm"
            @click="handleView(row)"
          >
            查看结果
          </button>
          <button 
            class="text-gray-600 hover:text-gray-800 text-sm"
            @click="handleDetail(row)"
          >
            详情
          </button>
        </div>
      </template>
    </DataTable>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppLayout from '../layouts/AppLayout.vue'
import DataTable from '../components/ui/DataTable.vue'
import MetricCard from '../components/ui/MetricCard.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'
import { taskApi, cycleApi } from '../utils/api'

const router = useRouter()

// 响应式数据
const tasks = ref([])
const cycles = ref([])
const loading = ref(false)
const searchValue = ref('')
const selectedCycle = ref('')
const selectedRelation = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 筛选器
const filters = ref([
  {
    key: 'cycle',
    placeholder: '全部周期',
    value: '',
    options: [
      { value: '', label: '全部周期' }
    ]
  },
  {
    key: 'relation',
    placeholder: '关系类型',
    value: '',
    options: [
      { value: '', label: '全部' },
      { value: 'superior', label: '上级评下级' },
      { value: 'peer', label: '同级互评' },
      { value: 'subordinate', label: '下级评上级' }
    ]
  },
  {
    key: 'status',
    placeholder: '任务状态',
    value: '',
    options: [
      { value: '', label: '全部' },
      { value: 'pending', label: '待考核' },
      { value: 'in_progress', label: '进行中' },
      { value: 'completed', label: '已完成' },
      { value: 'overdue', label: '已过期' }
    ]
  }
])

// 头部操作按钮
const headerActions = ref([
  {
    key: 'refresh',
    label: '刷新',
    icon: 'fas fa-sync-alt',
    type: 'secondary' as const
  },
  {
    key: 'export',
    label: '导出Excel',
    icon: 'fas fa-download',
    type: 'primary' as const
  },
  {
    key: 'batch',
    label: '批量操作',
    icon: 'fas fa-tasks',
    type: 'warning' as const
  }
])

// 表格列配置
const tableColumns = ref([
  { key: 'task', label: '任务信息', class: 'w-64' },
  { key: 'cycle', label: '考核周期', class: 'w-48' },
  { key: 'relation', label: '关系类型', class: 'w-32' },
  { key: 'status', label: '状态', class: 'w-32' },
  { key: 'progress', label: '进度', class: 'w-48' },
  { key: 'deadline', label: '截止时间', class: 'w-40' },
  { key: 'actions', label: '操作', class: 'w-40' }
])

// 表格操作按钮
const tableActions = ref([
  {
    key: 'export',
    label: '导出',
    icon: 'fas fa-download',
    type: 'secondary' as const
  },
  {
    key: 'import',
    label: '导入',
    icon: 'fas fa-upload',
    type: 'secondary' as const
  }
])

// 计算属性
const totalTasks = computed(() => tasks.value.length)
const pendingTasks = computed(() => tasks.value.filter(task => task.status === 'pending').length)
const completedTasks = computed(() => tasks.value.filter(task => task.status === 'completed').length)
const overdueTasks = computed(() => tasks.value.filter(task => task.status === 'overdue').length)

const filteredTasks = computed(() => {
  let filtered = tasks.value
  
  // 搜索过滤
  if (searchValue.value) {
    const search = searchValue.value.toLowerCase()
    filtered = filtered.filter(task => 
      task.evaluation_code.toLowerCase().includes(search) ||
      task.evaluator_name.toLowerCase().includes(search) ||
      task.evaluatee_name.toLowerCase().includes(search)
    )
  }
  
  // 周期过滤
  if (selectedCycle.value) {
    filtered = filtered.filter(task => task.cycle_id === selectedCycle.value)
  }
  
  // 关系类型过滤
  if (selectedRelation.value) {
    filtered = filtered.filter(task => task.relation_type === selectedRelation.value)
  }
  
  // 状态过滤
  if (selectedStatus.value) {
    filtered = filtered.filter(task => task.status === selectedStatus.value)
  }
  
  return filtered
})

const total = computed(() => filteredTasks.value.length)

// 方法
const loadTasks = async () => {
  try {
    loading.value = true
    const response = await taskApi.list()
    tasks.value = response.data.results || []
  } catch (error) {
    console.error('加载考核任务失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadCycles = async () => {
  try {
    const response = await cycleApi.list()
    cycles.value = response.data.results || []
    
    // 更新筛选器选项
    filters.value[0].options = [
      { value: '', label: '全部周期' },
      ...cycles.value.map(cycle => ({
        value: cycle.id,
        label: cycle.name
      }))
    ]
  } catch (error) {
    console.error('加载考核周期失败:', error)
  }
}

const handleSearch = (value: string) => {
  searchValue.value = value
}

const handleFilterChange = (filter: any) => {
  switch (filter.key) {
    case 'cycle':
      selectedCycle.value = filter.value
      break
    case 'relation':
      selectedRelation.value = filter.value
      break
    case 'status':
      selectedStatus.value = filter.value
      break
  }
}

const handleHeaderAction = (action: any) => {
  switch (action.key) {
    case 'refresh':
      loadTasks()
      break
    case 'export':
      handleExport()
      break
    case 'batch':
      handleBatchOperation()
      break
  }
}

const handleTableAction = (action: any) => {
  switch (action.key) {
    case 'export':
      handleExport()
      break
    case 'import':
      handleImport()
      break
  }
}

const handleStart = (task: any) => {
  router.push(`/evaluation/${task.id}`)
}

const handleContinue = (task: any) => {
  router.push(`/evaluation/${task.id}`)
}

const handleView = (task: any) => {
  router.push(`/results/${task.id}`)
}

const handleDetail = (task: any) => {
  router.push(`/tasks/${task.id}`)
}

const handleExport = () => {
  console.log('导出考核任务数据')
  ElMessage.success('导出功能开发中')
}

const handleImport = () => {
  console.log('导入考核任务数据')
  ElMessage.success('导入功能开发中')
}

const handleBatchOperation = () => {
  console.log('批量操作')
  ElMessage.success('批量操作功能开发中')
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

// 工具方法
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待考核',
    'in_progress': '进行中',
    'completed': '已完成',
    'overdue': '已过期'
  }
  return statusMap[status] || status
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    'pending': 'info',
    'in_progress': 'warning',
    'completed': 'success',
    'overdue': 'danger'
  }
  return typeMap[status] || 'default'
}

const getStatusIcon = (status: string) => {
  const iconMap: Record<string, string> = {
    'pending': 'fas fa-clock',
    'in_progress': 'fas fa-play-circle',
    'completed': 'fas fa-check-circle',
    'overdue': 'fas fa-exclamation-triangle'
  }
  return iconMap[status] || 'fas fa-circle'
}

const getRelationText = (relation: string) => {
  const relationMap: Record<string, string> = {
    'superior': '上级评下级',
    'peer': '同级互评',
    'subordinate': '下级评上级'
  }
  return relationMap[relation] || relation
}

const getRelationType = (relation: string) => {
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    'superior': 'success',
    'peer': 'info',
    'subordinate': 'warning'
  }
  return typeMap[relation] || 'default'
}

const getRelationIcon = (relation: string) => {
  const iconMap: Record<string, string> = {
    'superior': 'fas fa-arrow-up',
    'peer': 'fas fa-arrows-alt-h',
    'subordinate': 'fas fa-arrow-down'
  }
  return iconMap[relation] || 'fas fa-link'
}

const getTaskIcon = (status: string) => {
  const iconMap: Record<string, string> = {
    'pending': 'fas fa-clock',
    'in_progress': 'fas fa-play-circle',
    'completed': 'fas fa-check-circle',
    'overdue': 'fas fa-exclamation-triangle'
  }
  return iconMap[status] || 'fas fa-task'
}

const getTaskIconClass = (status: string) => {
  const classMap: Record<string, string> = {
    'pending': 'bg-yellow-100 text-yellow-600',
    'in_progress': 'bg-blue-100 text-blue-600',
    'completed': 'bg-green-100 text-green-600',
    'overdue': 'bg-red-100 text-red-600'
  }
  return classMap[status] || 'bg-gray-100 text-gray-600'
}

const getProgressColor = (progress: number) => {
  if (progress < 30) return 'bg-red-500'
  if (progress < 70) return 'bg-yellow-500'
  return 'bg-green-500'
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const getTimeRemaining = (deadline: string) => {
  if (!deadline) return ''
  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diffTime = deadlineDate.getTime() - now.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return '已过期'
  if (diffDays === 0) return '今天截止'
  if (diffDays === 1) return '明天截止'
  return `${diffDays}天后截止`
}

// 生命周期
onMounted(() => {
  loadTasks()
  loadCycles()
})
</script>

<style scoped>
/* 自定义样式 */
</style>
