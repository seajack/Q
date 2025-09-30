<template>
  <AppLayout
    page-title="考核结果统计"
    page-subtitle="Q4季度考核结果分析与统计"
    :filters="filters"
    :actions="headerActions"
    @filter-change="handleFilterChange"
    @action-click="handleHeaderAction"
  >
    <!-- 统计概览 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <MetricCard
        :value="stats?.total_participants || 0"
        label="参与人数"
        icon="fas fa-users"
        icon-color="blue"
        :trend="{ type: 'up', value: '+8.5%', text: '较上季度' }"
      />
      
      <MetricCard
        :value="stats?.completion_rate || 0"
        label="完成率"
        icon="fas fa-check-circle"
        icon-color="green"
        :show-progress="true"
        :progress="stats?.completion_rate || 0"
        :trend="{ type: 'up', value: '+2.1%', text: '较上季度' }"
      />
      
      <MetricCard
        :value="stats?.average_score || 0"
        label="平均分"
        icon="fas fa-star"
        icon-color="yellow"
        :trend="{ type: 'up', value: '+0.2', text: '较上期' }"
      />
      
      <MetricCard
        :value="stats?.excellent_count || 0"
        label="优秀人数"
        icon="fas fa-trophy"
        icon-color="purple"
        :trend="{ type: 'up', value: '+12', text: '较上季度' }"
      />
    </div>
    
    <!-- 图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- 评分分布图 -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">评分分布</h3>
          <button class="text-blue-600 text-sm hover:text-blue-700">查看详情</button>
        </div>
        <div class="h-64 flex items-center justify-center">
          <div class="text-center">
            <div class="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-chart-pie text-gray-400 text-2xl"></i>
            </div>
            <p class="text-gray-500">图表组件开发中</p>
          </div>
        </div>
      </div>
      
      <!-- 部门对比图 -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">部门平均分对比</h3>
          <button class="text-blue-600 text-sm hover:text-blue-700">查看详情</button>
        </div>
        <div class="h-64 flex items-center justify-center">
          <div class="text-center">
            <div class="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-chart-bar text-gray-400 text-2xl"></i>
            </div>
            <p class="text-gray-500">图表组件开发中</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 等级分布 -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
      <h3 class="text-lg font-semibold text-gray-900 mb-6">考核等级分布</h3>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="grade-excellent text-white p-4 rounded-lg text-center">
          <div class="text-2xl font-bold">{{ stats?.excellent_count || 0 }}</div>
          <div class="text-sm opacity-90">优秀 (4.5-5.0)</div>
          <div class="text-xs opacity-75 mt-1">{{ getPercentage(stats?.excellent_count, stats?.total_participants) }}%</div>
        </div>
        <div class="grade-good text-white p-4 rounded-lg text-center">
          <div class="text-2xl font-bold">{{ stats?.good_count || 0 }}</div>
          <div class="text-sm opacity-90">良好 (3.5-4.4)</div>
          <div class="text-xs opacity-75 mt-1">{{ getPercentage(stats?.good_count, stats?.total_participants) }}%</div>
        </div>
        <div class="grade-average text-white p-4 rounded-lg text-center">
          <div class="text-2xl font-bold">{{ stats?.average_count || 0 }}</div>
          <div class="text-sm opacity-90">一般 (2.5-3.4)</div>
          <div class="text-xs opacity-75 mt-1">{{ getPercentage(stats?.average_count, stats?.total_participants) }}%</div>
        </div>
        <div class="grade-poor text-white p-4 rounded-lg text-center">
          <div class="text-2xl font-bold">{{ stats?.poor_count || 0 }}</div>
          <div class="text-sm opacity-90">待改进 (<2.5)</div>
          <div class="text-xs opacity-75 mt-1">{{ getPercentage(stats?.poor_count, stats?.total_participants) }}%</div>
        </div>
      </div>
    </div>
    
    <!-- 排行榜 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 个人排行榜 -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">个人排行榜 TOP 10</h3>
          <button class="text-blue-600 text-sm hover:text-blue-700">查看完整榜单</button>
        </div>
        <div class="space-y-3">
          <div v-for="(employee, index) in topEmployees" :key="employee.id" class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors">
            <div class="flex items-center">
              <div class="ranking-badge mr-3" :class="getRankingClass(index + 1)">{{ index + 1 }}</div>
              <div class="w-8 h-8 rounded-full flex items-center justify-center mr-3" :class="getAvatarClass(employee.id)">
                <i class="fas fa-user text-sm"></i>
              </div>
              <div>
                <div class="font-medium text-gray-900">{{ employee.name }}</div>
                <div class="text-sm text-gray-600">{{ employee.department }}</div>
              </div>
            </div>
            <div class="text-right">
              <div class="font-bold text-gray-900">{{ employee.score }}</div>
              <div class="text-xs text-gray-500">加权后: {{ employee.weighted_score }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 部门排行榜 -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">部门排行榜</h3>
          <button class="text-blue-600 text-sm hover:text-blue-700">查看详细数据</button>
        </div>
        <div class="space-y-4">
          <div v-for="(dept, index) in departmentRankings" :key="dept.name" class="flex items-center justify-between p-4 rounded-lg" :class="getDepartmentBgClass(index)">
            <div class="flex items-center">
              <div class="ranking-badge mr-3" :class="getRankingClass(index + 1)">{{ index + 1 }}</div>
              <div>
                <div class="font-medium text-gray-900">{{ dept.name }}</div>
                <div class="text-sm text-gray-600">{{ dept.participants }}人参与</div>
              </div>
            </div>
            <div class="text-right">
              <div class="font-bold text-gray-900">{{ dept.average_score }}</div>
              <div class="text-xs text-gray-500">完成率: {{ dept.completion_rate }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import MetricCard from '../components/ui/MetricCard.vue'
import { resultsApi } from '../utils/api'

const router = useRouter()

// 响应式数据
const stats = ref(null)
const cycles = ref([])
const selectedCycle = ref('')
const loading = ref(false)

// 筛选器
const filters = ref([
  {
    key: 'cycle',
    placeholder: '考核周期',
    value: '',
    options: [
      { value: '', label: '全部周期' }
    ]
  },
  {
    key: 'department',
    placeholder: '部门',
    value: '',
    options: [
      { value: '', label: '全部部门' },
      { value: 'tech', label: '技术部' },
      { value: 'sales', label: '销售部' },
      { value: 'marketing', label: '市场部' },
      { value: 'hr', label: '人事部' },
      { value: 'finance', label: '财务部' }
    ]
  }
])

// 头部操作按钮
const headerActions = ref([
  {
    key: 'refresh',
    label: '刷新数据',
    icon: 'fas fa-sync-alt',
    type: 'secondary' as const
  },
  {
    key: 'export',
    label: '导出报告',
    icon: 'fas fa-download',
    type: 'primary' as const
  }
])

// 模拟数据
const topEmployees = ref([
  { id: 1, name: '张工程师', department: '技术部', score: '4.9', weighted_score: '5.88' },
  { id: 2, name: '李经理', department: '销售部', score: '4.8', weighted_score: '5.76' },
  { id: 3, name: '王主管', department: '市场部', score: '4.7', weighted_score: '5.17' },
  { id: 4, name: '赵专员', department: '人事部', score: '4.6', weighted_score: '4.14' },
  { id: 5, name: '孙会计', department: '财务部', score: '4.5', weighted_score: '4.05' }
])

const departmentRankings = ref([
  { name: '技术部', participants: 156, average_score: '4.6', completion_rate: 100 },
  { name: '销售部', participants: 89, average_score: '4.3', completion_rate: 98 },
  { name: '市场部', participants: 67, average_score: '4.1', completion_rate: 96 },
  { name: '人事部', participants: 34, average_score: '3.9', completion_rate: 94 },
  { name: '财务部', participants: 28, average_score: '3.8', completion_rate: 92 }
])

// 方法
const loadStats = async () => {
  try {
    loading.value = true
    const response = await resultsApi.overview()
    stats.value = response.data
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 使用模拟数据
    stats.value = {
      total_participants: 1247,
      completion_rate: 98.2,
      average_score: 4.3,
      excellent_count: 156,
      good_count: 687,
      average_count: 342,
      poor_count: 62
    }
  } finally {
    loading.value = false
  }
}

const loadCycles = async () => {
  try {
    const response = await resultsApi.cycles()
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

const handleFilterChange = (filter: any) => {
  if (filter.key === 'cycle') {
    selectedCycle.value = filter.value
    loadStats()
  }
}

const handleHeaderAction = (action: any) => {
  switch (action.key) {
    case 'refresh':
      loadStats()
      break
    case 'export':
      handleExport()
      break
  }
}

const handleExport = () => {
  console.log('导出考核结果报告')
}

const getPercentage = (count: number, total: number) => {
  if (!total) return 0
  return Math.round((count / total) * 100)
}

const getRankingClass = (rank: number) => {
  if (rank === 1) return 'rank-1'
  if (rank === 2) return 'rank-2'
  if (rank === 3) return 'rank-3'
  return 'rank-other'
}

const getAvatarClass = (id: string) => {
  const colors = [
    'bg-blue-100 text-blue-600',
    'bg-green-100 text-green-600',
    'bg-purple-100 text-purple-600',
    'bg-yellow-100 text-yellow-600',
    'bg-red-100 text-red-600'
  ]
  const index = id % colors.length
  return colors[index]
}

const getDepartmentBgClass = (index: number) => {
  const classes = [
    'bg-green-50',
    'bg-blue-50',
    'bg-purple-50',
    'bg-gray-50',
    'bg-gray-50'
  ]
  return classes[index] || 'bg-gray-50'
}

// 生命周期
onMounted(() => {
  loadStats()
  loadCycles()
})
</script>

<style scoped>
.grade-excellent {
  background: linear-gradient(135deg, #10b981, #059669);
}

.grade-good {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.grade-average {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.grade-poor {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.ranking-badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.rank-1 {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: white;
}

.rank-2 {
  background: linear-gradient(135deg, #9ca3af, #6b7280);
  color: white;
}

.rank-3 {
  background: linear-gradient(135deg, #d97706, #b45309);
  color: white;
}

.rank-other {
  background: #f3f4f6;
  color: #6b7280;
}
</style>
