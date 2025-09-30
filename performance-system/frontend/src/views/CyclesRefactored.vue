<template>
  <AppLayout
    page-title="考核周期管理"
    page-subtitle="创建和管理绩效考核周期"
    :show-search="true"
    search-placeholder="搜索周期名称..."
    :filters="filters"
    :actions="headerActions"
    @search="handleSearch"
    @filter-change="handleFilterChange"
    @action-click="handleHeaderAction"
  >
    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <MetricCard
        :value="totalCycles"
        label="总周期数"
        icon="fas fa-calendar-alt"
        icon-color="blue"
      />
      <MetricCard
        :value="activeCycles"
        label="进行中"
        icon="fas fa-play-circle"
        icon-color="green"
      />
      <MetricCard
        :value="completedCycles"
        label="已完成"
        icon="fas fa-check-circle"
        icon-color="green"
      />
      <MetricCard
        :value="draftCycles"
        label="草稿"
        icon="fas fa-edit"
        icon-color="yellow"
      />
    </div>
    
    <!-- 考核周期列表 -->
    <DataTable
      title="考核周期列表"
      :columns="tableColumns"
      :data="filteredCycles"
      :show-pagination="true"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      :actions="tableActions"
      @action-click="handleTableAction"
      @page-change="handlePageChange"
    >
      <!-- 周期名称列 -->
      <template #cell-name="{ row }">
        <div class="flex items-center">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center mr-3" :class="getCycleIconClass(row.status)">
            <i :class="getCycleIcon(row.status)" class="text-sm"></i>
          </div>
          <div>
            <div class="font-medium text-gray-900">{{ row.name }}</div>
            <div class="text-sm text-gray-600">{{ row.description }}</div>
          </div>
        </div>
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
      
      <!-- 时间范围列 -->
      <template #cell-dates="{ row }">
        <div class="text-sm">
          <div class="text-gray-900">{{ formatDate(row.start_date) }}</div>
          <div class="text-gray-600">至 {{ formatDate(row.end_date) }}</div>
        </div>
      </template>
      
      <!-- 操作列 -->
      <template #cell-actions="{ row }">
        <div class="flex space-x-2">
          <button 
            class="text-blue-600 hover:text-blue-800 text-sm"
            @click="handleEdit(row)"
          >
            编辑
          </button>
          <button 
            v-if="row.status === 'draft'"
            class="text-green-600 hover:text-green-800 text-sm"
            @click="handleStart(row)"
          >
            启动
          </button>
          <button 
            v-if="row.status === 'active'"
            class="text-orange-600 hover:text-orange-800 text-sm"
            @click="handlePause(row)"
          >
            暂停
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
import { cycleApi } from '../utils/api'

const router = useRouter()

// 响应式数据
const cycles = ref([])
const loading = ref(false)
const searchValue = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 筛选器
const filters = ref([
  {
    key: 'status',
    placeholder: '全部状态',
    value: '',
    options: [
      { value: '', label: '全部状态' },
      { value: 'draft', label: '草稿' },
      { value: 'active', label: '进行中' },
      { value: 'completed', label: '已完成' },
      { value: 'cancelled', label: '已取消' }
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
    label: '创建周期',
    icon: 'fas fa-plus',
    type: 'primary' as const
  }
])

// 表格列配置
const tableColumns = ref([
  { key: 'name', label: '周期名称', class: 'w-64' },
  { key: 'status', label: '状态', class: 'w-32' },
  { key: 'progress', label: '进度', class: 'w-48' },
  { key: 'dates', label: '时间范围', class: 'w-40' },
  { key: 'participants', label: '参与人数', class: 'w-32' },
  { key: 'evaluation_rule_name', label: '考核规则', class: 'w-40' },
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
const totalCycles = computed(() => cycles.value.length)
const activeCycles = computed(() => cycles.value.filter(cycle => cycle.status === 'active').length)
const completedCycles = computed(() => cycles.value.filter(cycle => cycle.status === 'completed').length)
const draftCycles = computed(() => cycles.value.filter(cycle => cycle.status === 'draft').length)

const filteredCycles = computed(() => {
  let filtered = cycles.value
  
  // 搜索过滤
  if (searchValue.value) {
    const search = searchValue.value.toLowerCase()
    filtered = filtered.filter(cycle => 
      cycle.name.toLowerCase().includes(search) ||
      cycle.description.toLowerCase().includes(search)
    )
  }
  
  // 状态过滤
  if (selectedStatus.value) {
    filtered = filtered.filter(cycle => cycle.status === selectedStatus.value)
  }
  
  return filtered
})

const total = computed(() => filteredCycles.value.length)

// 方法
const loadCycles = async () => {
  try {
    loading.value = true
    const response = await cycleApi.list()
    cycles.value = response.data.results || []
  } catch (error) {
    console.error('加载考核周期失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = (value: string) => {
  searchValue.value = value
}

const handleFilterChange = (filter: any) => {
  if (filter.key === 'status') {
    selectedStatus.value = filter.value
  }
}

const handleHeaderAction = (action: any) => {
  switch (action.key) {
    case 'refresh':
      loadCycles()
      break
    case 'create':
      router.push('/cycles/create')
      break
  }
}

const handleTableAction = (action: any) => {
  switch (action.key) {
    case 'export':
      console.log('导出考核周期数据')
      break
    case 'import':
      console.log('导入考核周期数据')
      break
  }
}

const handleEdit = (cycle: any) => {
  router.push(`/cycles/${cycle.id}/edit`)
}

const handleStart = async (cycle: any) => {
  try {
    await ElMessageBox.confirm('确认启动此考核周期？', '确认操作', {
      type: 'warning'
    })
    await cycleApi.start(cycle.id)
    ElMessage.success('考核周期已启动')
    loadCycles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('启动失败')
    }
  }
}

const handlePause = async (cycle: any) => {
  try {
    await ElMessageBox.confirm('确认暂停此考核周期？', '确认操作', {
      type: 'warning'
    })
    await cycleApi.pause(cycle.id)
    ElMessage.success('考核周期已暂停')
    loadCycles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('暂停失败')
    }
  }
}

const handleDetail = (cycle: any) => {
  router.push(`/cycles/${cycle.id}`)
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

// 工具方法
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'draft': '草稿',
    'active': '进行中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    'draft': 'info',
    'active': 'success',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return typeMap[status] || 'default'
}

const getStatusIcon = (status: string) => {
  const iconMap: Record<string, string> = {
    'draft': 'fas fa-edit',
    'active': 'fas fa-play-circle',
    'completed': 'fas fa-check-circle',
    'cancelled': 'fas fa-times-circle'
  }
  return iconMap[status] || 'fas fa-circle'
}

const getCycleIcon = (status: string) => {
  const iconMap: Record<string, string> = {
    'draft': 'fas fa-edit',
    'active': 'fas fa-play-circle',
    'completed': 'fas fa-check-circle',
    'cancelled': 'fas fa-times-circle'
  }
  return iconMap[status] || 'fas fa-calendar'
}

const getCycleIconClass = (status: string) => {
  const classMap: Record<string, string> = {
    'draft': 'bg-gray-100 text-gray-600',
    'active': 'bg-green-100 text-green-600',
    'completed': 'bg-blue-100 text-blue-600',
    'cancelled': 'bg-red-100 text-red-600'
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

// 生命周期
onMounted(() => {
  loadCycles()
})
</script>

<style scoped>
/* 自定义样式 */
</style>
