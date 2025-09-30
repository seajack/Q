<template>
  <AppLayout
    page-title="考核指标管理"
    page-subtitle="设置和管理绩效考核指标体系"
    :show-search="true"
    search-placeholder="搜索指标名称/描述..."
    :filters="filters"
    :actions="headerActions"
    @search="handleSearch"
    @filter-change="handleFilterChange"
    @action-click="handleHeaderAction"
  >
    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <MetricCard
        :value="totalIndicators"
        label="总指标数"
        icon="fas fa-bullseye"
        icon-color="blue"
      />
      <MetricCard
        :value="quantitativeIndicators"
        label="定量指标"
        icon="fas fa-chart-bar"
        icon-color="green"
      />
      <MetricCard
        :value="qualitativeIndicators"
        label="定性指标"
        icon="fas fa-comments"
        icon-color="blue"
      />
      <MetricCard
        :value="behavioralIndicators"
        label="行为指标"
        icon="fas fa-user-check"
        icon-color="purple"
      />
    </div>
    
    <!-- 指标列表 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <div 
        v-for="indicator in filteredIndicators" 
        :key="indicator.id"
        class="indicator-card bg-white rounded-lg shadow-sm border border-gray-200 p-6 transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
        :class="getIndicatorBorderClass(indicator.type)"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center">
            <div class="w-12 h-12 rounded-lg flex items-center justify-center mr-3" :class="getIndicatorIconClass(indicator.type)">
              <i :class="getIndicatorIcon(indicator.type)" class="text-lg"></i>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">{{ indicator.name }}</h3>
              <p class="text-sm text-gray-600">{{ indicator.type_text }} • {{ indicator.group }}</p>
            </div>
          </div>
          <StatusBadge 
            :label="indicator.enabled ? '启用' : '停用'" 
            :type="indicator.enabled ? 'success' : 'info'"
          />
        </div>
        
        <div class="space-y-3 mb-4">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">指标描述:</span>
            <span class="text-gray-900">{{ indicator.description }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">权重:</span>
            <span class="text-gray-900 font-medium">{{ indicator.weight || '-' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">评分标准:</span>
            <span class="text-gray-900">{{ getScoringStandard(indicator) }}</span>
          </div>
        </div>
        
        <div v-if="indicator.data_source" class="mb-4 p-3 rounded-lg" :class="getDataSourceClass(indicator.type)">
          <div class="text-sm" :class="getDataSourceTextClass(indicator.type)">
            <i class="fas fa-info-circle mr-1"></i>
            数据来源: {{ indicator.data_source }}
          </div>
        </div>
        
        <div class="flex space-x-2">
          <button 
            class="flex-1 px-3 py-2 bg-blue-100 text-blue-700 rounded text-sm hover:bg-blue-200 transition-colors"
            @click="handleEdit(indicator)"
          >
            编辑
          </button>
          <button 
            class="flex-1 px-3 py-2 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200 transition-colors"
            @click="handleCopy(indicator)"
          >
            复制
          </button>
          <button 
            class="flex-1 px-3 py-2 bg-purple-100 text-purple-700 rounded text-sm hover:bg-purple-200 transition-colors"
            @click="handleHistory(indicator)"
          >
            历史
          </button>
        </div>
      </div>
    </div>
    
    <!-- 分页 -->
    <div v-if="showPagination" class="flex items-center justify-between">
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
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppLayout from '../layouts/AppLayout.vue'
import MetricCard from '../components/ui/MetricCard.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'
import { indicatorApi } from '../utils/api'

const router = useRouter()

// 响应式数据
const indicators = ref([])
const loading = ref(false)
const searchValue = ref('')
const selectedCategory = ref('')
const selectedGroup = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const showPagination = ref(true)

// 筛选器
const filters = ref([
  {
    key: 'category',
    placeholder: '指标类别',
    value: '',
    options: [
      { value: '', label: '全部' },
      { value: 'performance', label: '工作绩效' },
      { value: 'ability', label: '工作能力' },
      { value: 'attitude', label: '工作态度' },
      { value: 'teamwork', label: '团队合作' },
      { value: 'innovation', label: '创新能力' }
    ]
  },
  {
    key: 'group',
    placeholder: '分组',
    value: '',
    options: [
      { value: '', label: '全部分组' }
    ]
  },
  {
    key: 'status',
    placeholder: '状态',
    value: '',
    options: [
      { value: '', label: '全部' },
      { value: 'enabled', label: '启用' },
      { value: 'disabled', label: '停用' }
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
    label: '新增指标',
    icon: 'fas fa-plus',
    type: 'primary' as const
  }
])

// 计算属性
const totalIndicators = computed(() => indicators.value.length)
const quantitativeIndicators = computed(() => indicators.value.filter(ind => ind.type === 'quantitative').length)
const qualitativeIndicators = computed(() => indicators.value.filter(ind => ind.type === 'qualitative').length)
const behavioralIndicators = computed(() => indicators.value.filter(ind => ind.type === 'behavioral').length)

const filteredIndicators = computed(() => {
  let filtered = indicators.value
  
  // 搜索过滤
  if (searchValue.value) {
    const search = searchValue.value.toLowerCase()
    filtered = filtered.filter(indicator => 
      indicator.name.toLowerCase().includes(search) ||
      indicator.description.toLowerCase().includes(search)
    )
  }
  
  // 类别过滤
  if (selectedCategory.value) {
    filtered = filtered.filter(indicator => indicator.category === selectedCategory.value)
  }
  
  // 分组过滤
  if (selectedGroup.value) {
    filtered = filtered.filter(indicator => indicator.group === selectedGroup.value)
  }
  
  // 状态过滤
  if (selectedStatus.value) {
    if (selectedStatus.value === 'enabled') {
      filtered = filtered.filter(indicator => indicator.enabled)
    } else if (selectedStatus.value === 'disabled') {
      filtered = filtered.filter(indicator => !indicator.enabled)
    }
  }
  
  return filtered
})

const total = computed(() => filteredIndicators.value.length)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// 方法
const loadIndicators = async () => {
  try {
    loading.value = true
    const response = await indicatorApi.list()
    indicators.value = response.data.results || []
    
    // 更新分组选项
    const groups = [...new Set(indicators.value.map(ind => ind.group))]
    filters.value[1].options = [
      { value: '', label: '全部分组' },
      ...groups.map(group => ({ value: group, label: group }))
    ]
  } catch (error) {
    console.error('加载考核指标失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = (value: string) => {
  searchValue.value = value
}

const handleFilterChange = (filter: any) => {
  switch (filter.key) {
    case 'category':
      selectedCategory.value = filter.value
      break
    case 'group':
      selectedGroup.value = filter.value
      break
    case 'status':
      selectedStatus.value = filter.value
      break
  }
}

const handleHeaderAction = (action: any) => {
  switch (action.key) {
    case 'refresh':
      loadIndicators()
      break
    case 'create':
      router.push('/indicators/create')
      break
  }
}

const handleEdit = (indicator: any) => {
  router.push(`/indicators/${indicator.id}/edit`)
}

const handleCopy = (indicator: any) => {
  router.push(`/indicators/create?copy=${indicator.id}`)
}

const handleHistory = (indicator: any) => {
  router.push(`/indicators/${indicator.id}/history`)
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

// 工具方法
const getIndicatorIcon = (type: string) => {
  const iconMap: Record<string, string> = {
    'quantitative': 'fas fa-chart-bar',
    'qualitative': 'fas fa-comments',
    'behavioral': 'fas fa-user-check'
  }
  return iconMap[type] || 'fas fa-bullseye'
}

const getIndicatorIconClass = (type: string) => {
  const classMap: Record<string, string> = {
    'quantitative': 'bg-green-100 text-green-600',
    'qualitative': 'bg-blue-100 text-blue-600',
    'behavioral': 'bg-purple-100 text-purple-600'
  }
  return classMap[type] || 'bg-gray-100 text-gray-600'
}

const getIndicatorBorderClass = (type: string) => {
  const classMap: Record<string, string> = {
    'quantitative': 'border-l-4 border-green-500',
    'qualitative': 'border-l-4 border-blue-500',
    'behavioral': 'border-l-4 border-purple-500'
  }
  return classMap[type] || ''
}

const getScoringStandard = (indicator: any) => {
  if (indicator.type === 'quantitative') {
    return indicator.scoring_standard || '数值计算'
  } else if (indicator.type === 'qualitative') {
    return '5级评分制'
  } else {
    return '行为观察'
  }
}

const getDataSourceClass = (type: string) => {
  const classMap: Record<string, string> = {
    'quantitative': 'bg-green-50',
    'qualitative': 'bg-blue-50',
    'behavioral': 'bg-purple-50'
  }
  return classMap[type] || 'bg-gray-50'
}

const getDataSourceTextClass = (type: string) => {
  const classMap: Record<string, string> = {
    'quantitative': 'text-green-700',
    'qualitative': 'text-blue-700',
    'behavioral': 'text-purple-700'
  }
  return classMap[type] || 'text-gray-700'
}

// 生命周期
onMounted(() => {
  loadIndicators()
})
</script>

<style scoped>
.indicator-card {
  transition: all 0.3s ease;
}

.indicator-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}
</style>
