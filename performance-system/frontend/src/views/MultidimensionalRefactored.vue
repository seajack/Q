<template>
  <AppLayout
    page-title="多维度评估管理"
    page-subtitle="管理和执行多维度绩效评估"
    :show-search="true"
    search-placeholder="搜索评估记录..."
    :filters="filters"
    :actions="headerActions"
    @search="handleSearch"
    @filter-change="handleFilterChange"
    @action-click="handleHeaderAction"
  >
    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <MetricCard
        :value="totalEvaluations"
        label="总评估数"
        icon="fas fa-layer-group"
        icon-color="blue"
      />
      <MetricCard
        :value="draftEvaluations"
        label="草稿"
        icon="fas fa-edit"
        icon-color="yellow"
      />
      <MetricCard
        :value="submittedEvaluations"
        label="已提交"
        icon="fas fa-check-circle"
        icon-color="green"
      />
      <MetricCard
        :value="reviewedEvaluations"
        label="已审核"
        icon="fas fa-eye"
        icon-color="purple"
      />
    </div>
    
    <!-- 多维度评估列表 -->
    <DataTable
      title="多维度评估列表"
      :columns="tableColumns"
      :data="filteredEvaluations"
      :show-pagination="true"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      :actions="tableActions"
      @action-click="handleTableAction"
      @page-change="handlePageChange"
    >
      <!-- 评估信息列 -->
      <template #cell-evaluation="{ row }">
        <div class="flex items-center">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center mr-3" :class="getEvaluationIconClass(row.status)">
            <i :class="getEvaluationIcon(row.status)" class="text-sm"></i>
          </div>
          <div>
            <div class="font-medium text-gray-900">{{ row.evaluator_name }} → {{ row.evaluatee_name }}</div>
            <div class="text-sm text-gray-600">{{ row.method_name }}</div>
          </div>
        </div>
      </template>
      
      <!-- 评估周期列 -->
      <template #cell-cycle="{ row }">
        <div class="text-sm">
          <div class="text-gray-900">{{ row.cycle_name }}</div>
          <div class="text-gray-600">{{ formatDate(row.cycle_start_date) }} - {{ formatDate(row.cycle_end_date) }}</div>
        </div>
      </template>
      
      <!-- 评估方法列 -->
      <template #cell-method="{ row }">
        <StatusBadge 
          :label="row.method_name" 
          :type="getMethodType(row.method_type)"
          :icon="getMethodIcon(row.method_type)"
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
      
      <!-- 评分列 -->
      <template #cell-scores="{ row }">
        <div class="text-sm">
          <div class="text-gray-900">总分: {{ row.total_score }}</div>
          <div class="text-gray-600">加权: {{ row.weighted_score }}</div>
        </div>
      </template>
      
      <!-- 维度评分列 -->
      <template #cell-dimensions="{ row }">
        <div class="space-y-1">
          <div v-for="(score, dimension) in row.dimensions" :key="dimension" class="flex justify-between text-xs">
            <span class="text-gray-600">{{ dimension }}:</span>
            <span class="text-gray-900 font-medium">{{ score }}</span>
          </div>
        </div>
      </template>
      
      <!-- 操作列 -->
      <template #cell-actions="{ row }">
        <div class="flex space-x-2">
          <button 
            v-if="row.status === 'draft'"
            class="text-blue-600 hover:text-blue-800 text-sm"
            @click="handleEdit(row)"
          >
            编辑
          </button>
          <button 
            v-if="row.status === 'draft'"
            class="text-green-600 hover:text-green-800 text-sm"
            @click="handleSubmit(row)"
          >
            提交
          </button>
          <button 
            v-if="row.status === 'submitted'"
            class="text-purple-600 hover:text-purple-800 text-sm"
            @click="handleReview(row)"
          >
            审核
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
import { ElMessage, ElMessageBox } from 'element-plus'
import AppLayout from '../layouts/AppLayout.vue'
import DataTable from '../components/ui/DataTable.vue'
import MetricCard from '../components/ui/MetricCard.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'
import { multidimensionalApi, cycleApi } from '../utils/api'

const router = useRouter()

// 响应式数据
const evaluations = ref([])
const cycles = ref([])
const methods = ref([])
const loading = ref(false)
const searchValue = ref('')
const selectedCycle = ref('')
const selectedMethod = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 筛选器
const filters = ref([
  {
    key: 'cycle',
    placeholder: '评估周期',
    value: '',
    options: [
      { value: '', label: '全部周期' }
    ]
  },
  {
    key: 'method',
    placeholder: '评估方法',
    value: '',
    options: [
      { value: '', label: '全部方法' }
    ]
  },
  {
    key: 'status',
    placeholder: '状态',
    value: '',
    options: [
      { value: '', label: '全部状态' },
      { value: 'draft', label: '草稿' },
      { value: 'submitted', label: '已提交' },
      { value: 'reviewed', label: '已审核' },
      { value: 'finalized', label: '已确定' }
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
    key: 'create',
    label: '新建评估',
    icon: 'fas fa-plus',
    type: 'primary' as const
  }
])

// 表格列配置
const tableColumns = ref([
  { key: 'evaluation', label: '评估信息', class: 'w-64' },
  { key: 'cycle', label: '评估周期', class: 'w-48' },
  { key: 'method', label: '评估方法', class: 'w-32' },
  { key: 'status', label: '状态', class: 'w-32' },
  { key: 'scores', label: '评分', class: 'w-32' },
  { key: 'dimensions', label: '维度评分', class: 'w-48' },
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
const totalEvaluations = computed(() => evaluations.value.length)
const draftEvaluations = computed(() => evaluations.value.filter(evaluation => evaluation.status === 'draft').length)
const submittedEvaluations = computed(() => evaluations.value.filter(evaluation => evaluation.status === 'submitted').length)
const reviewedEvaluations = computed(() => evaluations.value.filter(evaluation => evaluation.status === 'reviewed').length)

const filteredEvaluations = computed(() => {
  let filtered = evaluations.value
  
  // 搜索过滤
  if (searchValue.value) {
    const search = searchValue.value.toLowerCase()
    filtered = filtered.filter(evaluation => 
      evaluation.evaluator_name.toLowerCase().includes(search) ||
      evaluation.evaluatee_name.toLowerCase().includes(search) ||
      evaluation.method_name.toLowerCase().includes(search)
    )
  }
  
  // 周期过滤
  if (selectedCycle.value) {
    filtered = filtered.filter(evaluation => evaluation.cycle_id === selectedCycle.value)
  }
  
  // 方法过滤
  if (selectedMethod.value) {
    filtered = filtered.filter(evaluation => evaluation.method_id === selectedMethod.value)
  }
  
  // 状态过滤
  if (selectedStatus.value) {
    filtered = filtered.filter(evaluation => evaluation.status === selectedStatus.value)
  }
  
  return filtered
})

const total = computed(() => filteredEvaluations.value.length)

// 方法
const loadEvaluations = async () => {
  try {
    loading.value = true
    const response = await multidimensionalApi.list()
    evaluations.value = response.data.results || []
  } catch (error) {
    console.error('加载多维度评估失败:', error)
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

const loadMethods = async () => {
  try {
    const response = await multidimensionalApi.methods()
    methods.value = response.data.results || []
    
    // 更新筛选器选项
    filters.value[1].options = [
      { value: '', label: '全部方法' },
      ...methods.value.map(method => ({
        value: method.id,
        label: method.name
      }))
    ]
  } catch (error) {
    console.error('加载评估方法失败:', error)
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
    case 'method':
      selectedMethod.value = filter.value
      break
    case 'status':
      selectedStatus.value = filter.value
      break
  }
}

const handleHeaderAction = (action: any) => {
  switch (action.key) {
    case 'refresh':
      loadEvaluations()
      break
    case 'create':
      router.push('/multidimensional/create')
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

const handleEdit = (evaluation: any) => {
  router.push(`/multidimensional/${evaluation.id}/edit`)
}

const handleSubmit = async (evaluation: any) => {
  try {
    await ElMessageBox.confirm('确认提交此评估？', '确认操作', {
      type: 'warning'
    })
    await multidimensionalApi.submit(evaluation.id)
    ElMessage.success('评估已提交')
    loadEvaluations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('提交失败')
    }
  }
}

const handleReview = (evaluation: any) => {
  router.push(`/multidimensional/${evaluation.id}/review`)
}

const handleDetail = (evaluation: any) => {
  router.push(`/multidimensional/${evaluation.id}`)
}

const handleExport = () => {
  console.log('导出多维度评估数据')
  ElMessage.success('导出功能开发中')
}

const handleImport = () => {
  console.log('导入多维度评估数据')
  ElMessage.success('导入功能开发中')
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

// 工具方法
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'draft': '草稿',
    'submitted': '已提交',
    'reviewed': '已审核',
    'finalized': '已确定'
  }
  return statusMap[status] || status
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    'draft': 'info',
    'submitted': 'warning',
    'reviewed': 'success',
    'finalized': 'success'
  }
  return typeMap[status] || 'default'
}

const getStatusIcon = (status: string) => {
  const iconMap: Record<string, string> = {
    'draft': 'fas fa-edit',
    'submitted': 'fas fa-paper-plane',
    'reviewed': 'fas fa-eye',
    'finalized': 'fas fa-check-circle'
  }
  return iconMap[status] || 'fas fa-circle'
}

const getMethodType = (methodType: string) => {
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    '360_degree': 'success',
    'okr': 'info',
    'kpi': 'warning',
    'mbo': 'info',
    'bsc': 'success'
  }
  return typeMap[methodType] || 'default'
}

const getMethodIcon = (methodType: string) => {
  const iconMap: Record<string, string> = {
    '360_degree': 'fas fa-sync-alt',
    'okr': 'fas fa-bullseye',
    'kpi': 'fas fa-chart-line',
    'mbo': 'fas fa-target',
    'bsc': 'fas fa-balance-scale'
  }
  return iconMap[methodType] || 'fas fa-chart-bar'
}

const getEvaluationIcon = (status: string) => {
  const iconMap: Record<string, string> = {
    'draft': 'fas fa-edit',
    'submitted': 'fas fa-paper-plane',
    'reviewed': 'fas fa-eye',
    'finalized': 'fas fa-check-circle'
  }
  return iconMap[status] || 'fas fa-layer-group'
}

const getEvaluationIconClass = (status: string) => {
  const classMap: Record<string, string> = {
    'draft': 'bg-yellow-100 text-yellow-600',
    'submitted': 'bg-blue-100 text-blue-600',
    'reviewed': 'bg-green-100 text-green-600',
    'finalized': 'bg-purple-100 text-purple-600'
  }
  return classMap[status] || 'bg-gray-100 text-gray-600'
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadEvaluations()
  loadCycles()
  loadMethods()
})
</script>

<style scoped>
/* 自定义样式 */
</style>
