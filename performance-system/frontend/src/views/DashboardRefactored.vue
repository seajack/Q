<template>
  <AppLayout
    page-title="绩效考核仪表板"
    page-subtitle="实时监控考核进度和数据统计"
    :actions="headerActions"
    @action-click="handleHeaderAction"
  >
    <!-- 关键指标卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="metric-card p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-users text-blue-600 text-xl"></i>
          </div>
          <span class="text-2xl">📈</span>
        </div>
        <h3 class="text-2xl font-bold mb-1 text-gray-900">{{ stats?.total_employees || 1247 }}</h3>
        <p class="text-gray-600 text-sm">参与员工总数</p>
        <div class="mt-3 flex items-center text-green-600 text-sm">
          <i class="fas fa-arrow-up mr-1"></i>
          <span>+12% 较上月</span>
        </div>
      </div>
      
      <div class="metric-card p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-check-circle text-green-600 text-xl"></i>
          </div>
          <span class="text-2xl">✅</span>
        </div>
        <h3 class="text-2xl font-bold mb-1 text-gray-900">{{ stats?.completed_tasks || 892 }}</h3>
        <p class="text-gray-600 text-sm">已完成考核</p>
        <div class="mt-3">
          <div class="progress-bar h-2">
            <div class="progress-fill h-full" :style="{ width: getCompletionRate() + '%' }"></div>
          </div>
          <p class="text-xs text-gray-500 mt-1">{{ getCompletionRate() }}% 完成率</p>
        </div>
      </div>
      
      <div class="metric-card p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-clock text-yellow-600 text-xl"></i>
          </div>
          <span class="text-2xl">⏳</span>
        </div>
        <h3 class="text-2xl font-bold mb-1 text-gray-900">{{ (stats?.total_tasks || 1247) - (stats?.completed_tasks || 892) }}</h3>
        <p class="text-gray-600 text-sm">待处理任务</p>
        <div class="mt-3 flex items-center text-yellow-600 text-sm">
          <i class="fas fa-exclamation-triangle mr-1"></i>
          <span>需要关注</span>
        </div>
      </div>
      
      <div class="metric-card p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-star text-purple-600 text-xl"></i>
          </div>
          <span class="text-2xl">⭐</span>
        </div>
        <h3 class="text-2xl font-bold mb-1 text-gray-900">4.2</h3>
        <p class="text-gray-600 text-sm">平均评分</p>
        <div class="mt-3 flex items-center text-purple-600 text-sm">
          <i class="fas fa-arrow-up mr-1"></i>
          <span>+0.3 较上期</span>
        </div>
      </div>
    </div>
    
    <!-- 图表和数据展示 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- 考核进度图表 -->
      <div class="chart-container p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">考核进度趋势</h3>
          <select 
            v-model="selectedTimeRange" 
            class="bg-white border border-gray-300 rounded-lg px-3 py-1 text-sm text-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @change="handleTimeRangeChange"
          >
            <option value="7">最近7天</option>
            <option value="30">最近30天</option>
            <option value="90">最近90天</option>
          </select>
        </div>
        <div class="h-64 flex items-end justify-between space-x-2">
          <div v-for="(day, index) in progressData" :key="index" class="flex flex-col items-center">
            <div 
              class="w-8 bg-blue-500 rounded-t transition-all duration-500" 
              :style="{ height: day.percentage + '%' }"
            ></div>
            <span class="text-xs text-gray-500 mt-2">{{ day.label }}</span>
          </div>
        </div>
      </div>
      
      <!-- 部门评分分布 -->
      <div class="chart-container p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">部门评分分布</h3>
          <button class="text-blue-600 text-sm hover:text-blue-700" @click="goToResults">
            查看详情
          </button>
        </div>
        <div class="space-y-4">
          <div v-for="dept in departmentStats" :key="dept.name" class="flex items-center justify-between">
            <span class="text-sm text-gray-700">{{ dept.name }}</span>
            <div class="flex items-center space-x-3">
              <div class="w-32 progress-bar h-2">
                <div 
                  class="progress-fill h-full transition-all duration-500" 
                  :class="dept.color"
                  :style="{ width: dept.percentage + '%' }"
                ></div>
              </div>
              <span class="text-sm font-medium text-gray-900">{{ dept.score }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 最近活动和快速操作 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 最近活动 -->
      <div class="lg:col-span-2 chart-container p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">最近活动</h3>
          <button class="text-blue-600 text-sm hover:text-blue-700" @click="goToActivities">
            查看全部
          </button>
        </div>
        <div class="space-y-4">
          <div v-if="!recentActivities || recentActivities.length === 0" class="text-center py-8">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-bell text-gray-400 text-xl"></i>
            </div>
            <p class="text-gray-500">暂无系统通知</p>
            <span class="text-xs text-gray-400">系统运行正常</span>
          </div>
          <div v-else>
            <div v-for="activity in recentActivities.slice(0, 5)" :key="activity.id" class="flex items-start space-x-4 p-4 rounded-lg hover:bg-gray-50 transition-colors">
              <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0" :class="activity.iconClass">
                <i :class="activity.icon" class="text-sm"></i>
              </div>
              <div class="flex-1">
                <p class="text-sm text-gray-900" v-html="activity.message"></p>
                <p class="text-xs text-gray-500 mt-1">{{ activity.time }}</p>
              </div>
              <span class="status-badge px-2 py-1 rounded-full text-xs font-medium" :class="getStatusClass(activity.statusType)">
                {{ activity.status }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 快速操作 -->
      <div class="chart-container p-6">
        <h3 class="text-lg font-semibold mb-6 text-gray-900">快速操作</h3>
        <div class="space-y-3">
          <button 
            v-for="action in quickActions" 
            :key="action.key"
            class="w-full p-4 text-left rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all group"
            @click="handleQuickAction(action)"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center mr-3 group-hover:bg-blue-200" :class="action.iconClass">
                <i :class="action.icon" class="text-blue-600"></i>
              </div>
              <div>
                <p class="font-medium text-gray-900">{{ action.title }}</p>
                <p class="text-xs text-gray-500">{{ action.description }}</p>
              </div>
            </div>
          </button>
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
import StatusBadge from '../components/ui/StatusBadge.vue'
import { statsApi } from '../utils/api'

const router = useRouter()

// 响应式数据
const stats = ref(null)
const loading = ref(false)
const selectedTimeRange = ref('7')

// 头部操作按钮
const headerActions = ref([
  {
    key: 'refresh',
    label: '刷新数据',
    icon: 'fas fa-sync-alt',
    type: 'secondary' as const
  },
  {
    key: 'create',
    label: '创建考核',
    icon: 'fas fa-plus',
    type: 'primary' as const
  }
])

// 进度数据
const progressData = ref([
  { label: '周一', percentage: 60 },
  { label: '周二', percentage: 80 },
  { label: '周三', percentage: 45 },
  { label: '周四', percentage: 90 },
  { label: '周五', percentage: 70 },
  { label: '周六', percentage: 35 },
  { label: '周日', percentage: 25 }
])

// 部门统计数据
const departmentStats = ref([
  { name: '技术部', score: '4.6', percentage: 92, color: 'bg-green-500' },
  { name: '销售部', score: '4.3', percentage: 85, color: 'bg-blue-500' },
  { name: '市场部', score: '3.9', percentage: 78, color: 'bg-purple-500' },
  { name: '人事部', score: '4.1', percentage: 82, color: 'bg-yellow-500' },
  { name: '财务部', score: '4.4', percentage: 88, color: 'bg-red-500' }
])

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    message: '<strong>张三</strong> 完成了对 <strong>李四</strong> 的绩效评价',
    time: '2分钟前',
    status: '已完成',
    statusType: 'success' as const,
    icon: 'fas fa-check',
    iconClass: 'bg-green-100 text-green-600'
  },
  {
    id: 2,
    message: '系统自动生成了 <strong>Q4季度考核</strong> 的评价任务',
    time: '15分钟前',
    status: '新任务',
    statusType: 'info' as const,
    icon: 'fas fa-plus',
    iconClass: 'bg-blue-100 text-blue-600'
  },
  {
    id: 3,
    message: '<strong>王五</strong> 的考核任务即将到期',
    time: '1小时前',
    status: '待处理',
    statusType: 'warning' as const,
    icon: 'fas fa-exclamation',
    iconClass: 'bg-yellow-100 text-yellow-600'
  },
  {
    id: 4,
    message: '<strong>赵六</strong> 获得了本月最高评分',
    time: '2小时前',
    status: '优秀',
    statusType: 'success' as const,
    icon: 'fas fa-star',
    iconClass: 'bg-purple-100 text-purple-600'
  }
])

// 快速操作
const quickActions = ref([
  {
    key: 'create-cycle',
    title: '创建考核周期',
    description: '设置新的考核周期',
    icon: 'fas fa-calendar-plus',
    iconClass: 'bg-blue-100'
  },
  {
    key: 'view-tasks',
    title: '查看考核任务',
    description: '管理考核任务分配',
    icon: 'fas fa-tasks',
    iconClass: 'bg-green-100'
  },
  {
    key: 'view-results',
    title: '查看考核结果',
    description: '分析考核结果数据',
    icon: 'fas fa-chart-bar',
    iconClass: 'bg-purple-100'
  },
  {
    key: 'manage-employees',
    title: '员工管理',
    description: '管理员工信息和权限',
    icon: 'fas fa-users',
    iconClass: 'bg-yellow-100'
  }
])

// 计算属性
const getCompletionRate = () => {
  if (!stats.value) return 0
  const total = stats.value.total_tasks || 0
  const completed = stats.value.completed_tasks || 0
  return total > 0 ? Math.round((completed / total) * 100) : 0
}

// 方法
const loadStats = async () => {
  try {
    loading.value = true
    const response = await statsApi.overview()
    stats.value = response.data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleHeaderAction = (action: any) => {
  switch (action.key) {
    case 'refresh':
      loadStats()
      break
    case 'create':
      router.push('/cycles/create')
      break
  }
}

const handleTimeRangeChange = () => {
  // 根据时间范围重新加载数据
  loadStats()
}

const handleQuickAction = (action: any) => {
  switch (action.key) {
    case 'create-cycle':
      router.push('/cycles/create')
      break
    case 'view-tasks':
      router.push('/tasks')
      break
    case 'view-results':
      router.push('/results')
      break
    case 'manage-employees':
      router.push('/employees')
      break
  }
}

const goToResults = () => {
  router.push('/results')
}

const goToActivities = () => {
  router.push('/activities')
}

const getStatusClass = (statusType: string) => {
  switch (statusType) {
    case 'success':
      return 'status-completed'
    case 'warning':
      return 'status-pending'
    case 'info':
      return 'status-active'
    default:
      return 'status-pending'
  }
}

// 生命周期
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
/* 自定义样式 */
</style>