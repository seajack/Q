<template>
  <div class="modern-dashboard">
    <!-- 页面标题 -->
    <header class="dashboard-header">
      <div class="header-content">
        <h1 class="dashboard-title">仪表板</h1>
        <p class="dashboard-subtitle">绩效考核系统概览与数据统计</p>
      </div>
      <div class="header-actions">
        <Button variant="outline" size="sm" @click="refreshData">
          <template #icon>
            <el-icon><Refresh /></el-icon>
          </template>
          刷新数据
        </Button>
        <Button variant="primary" size="sm" @click="goToCycles">
          <template #icon>
            <el-icon><Plus /></el-icon>
          </template>
          创建考核
        </Button>
      </div>
    </header>

    <!-- 统计卡片网格 -->
    <section class="stats-section" aria-label="数据统计">
      <div class="stats-grid">
        <StatCard
          :value="stats?.active_cycles || 0"
          label="活跃考核周期"
          description="当前正在进行的考核周期数量"
          variant="primary"
          :icon="Calendar"
          :trend="{ value: 12, type: 'up' }"
          class="animate-fade-in"
          style="animation-delay: 0.1s"
        />
        
        <StatCard
          :value="stats?.total_tasks || 0"
          label="考核任务总数"
          description="系统中所有考核任务的总数量"
          variant="success"
          :icon="Document"
          :trend="{ value: 8, type: 'up' }"
          class="animate-fade-in"
          style="animation-delay: 0.2s"
        />
        
        <StatCard
          :value="stats?.completed_tasks || 0"
          label="已完成任务"
          description="已经完成的考核任务数量"
          variant="warning"
          :icon="Check"
          :trend="{ value: 15, type: 'up' }"
          class="animate-fade-in"
          style="animation-delay: 0.3s"
        />
        
        <StatCard
          :value="stats?.completion_rate || 0"
          label="完成率"
          description="整体考核任务的完成情况"
          variant="info"
          :icon="TrendCharts"
          :trend="{ value: 5, type: 'up' }"
          format="percentage"
          class="animate-fade-in"
          style="animation-delay: 0.4s"
        />
      </div>
    </section>

    <!-- 主要内容区域 -->
    <el-row :gutter="24" class="content-row">
      <!-- 考核周期概览 -->
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>考核周期概览</h3>
              <el-button type="primary" size="small" @click="goToCycles">
                查看全部
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="chart-container">
            <div v-if="loading" class="loading-container">
              <el-skeleton :rows="5" animated />
            </div>
            <EmptyState 
              v-else-if="cycles.length === 0"
              icon="Calendar"
              title="暂无考核周期"
              description="当前没有活跃的考核周期，请创建新的考核周期"
              action-text="创建考核周期"
              @action="goToCycles"
            />
            <div v-else class="cycles-list">
              <div 
                v-for="cycle in cycles.slice(0, 5)" 
                :key="cycle.id" 
                class="cycle-item"
              >
                <div class="cycle-info">
                  <h4>{{ cycle.name }}</h4>
                  <p>{{ cycle.description }}</p>
                  <div class="cycle-meta">
                    <el-tag :type="getCycleStatusType(cycle.status)" size="small">
                      {{ getCycleStatusText(cycle.status) }}
                    </el-tag>
                    <span class="cycle-date">{{ formatDate(cycle.start_date) }} - {{ formatDate(cycle.end_date) }}</span>
                  </div>
                </div>
                <div class="cycle-progress">
                  <el-progress 
                    :percentage="getCycleProgress(cycle)" 
                    :color="getProgressColor(getCycleProgress(cycle))"
                    :show-text="false"
                  />
                  <span class="progress-text">{{ getCycleProgress(cycle) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 快速操作 -->
      <el-col :xs="24" :lg="8">
        <el-card class="quick-actions-card">
          <template #header>
            <h3>快速操作</h3>
          </template>
          <div class="quick-actions">
            <el-button 
              type="primary" 
              class="action-btn"
              @click="goToCycles"
            >
              <el-icon><Calendar /></el-icon>
              创建考核周期
            </el-button>
            <el-button 
              type="success" 
              class="action-btn"
              @click="goToTasks"
            >
              <el-icon><Document /></el-icon>
              查看考核任务
            </el-button>
            <el-button 
              type="info" 
              class="action-btn"
              @click="goToResults"
            >
              <el-icon><TrendCharts /></el-icon>
              查看考核结果
            </el-button>
            <el-button 
              type="warning" 
              class="action-btn"
              @click="goToEmployees"
            >
              <el-icon><User /></el-icon>
              员工管理
            </el-button>
          </div>
        </el-card>

        <!-- 系统通知 -->
        <el-card class="notifications-card">
          <template #header>
            <h3>系统通知</h3>
          </template>
          <div class="notifications-list">
            <div class="notification-item">
              <el-icon class="notification-icon"><Bell /></el-icon>
              <div class="notification-content">
                <p>新的考核周期已创建</p>
                <span class="notification-time">2小时前</span>
              </div>
            </div>
            <div class="notification-item">
              <el-icon class="notification-icon"><Document /></el-icon>
              <div class="notification-content">
                <p>有3个考核任务待处理</p>
                <span class="notification-time">4小时前</span>
              </div>
            </div>
            <div class="notification-item">
              <el-icon class="notification-icon"><TrendCharts /></el-icon>
              <div class="notification-content">
                <p>考核结果已生成</p>
                <span class="notification-time">1天前</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-row :gutter="24" class="activity-row">
      <el-col :span="24">
        <el-card class="activity-card">
          <template #header>
            <div class="card-header">
              <h3>最近活动</h3>
              <el-button type="text" size="small">查看全部</el-button>
            </div>
          </template>
          <div class="activity-list">
            <div class="activity-item">
              <el-icon class="activity-icon"><User /></el-icon>
              <div class="activity-content">
                <p>张三完成了2024年第一季度考核</p>
                <span class="activity-time">10分钟前</span>
              </div>
            </div>
            <div class="activity-item">
              <el-icon class="activity-icon"><Calendar /></el-icon>
              <div class="activity-content">
                <p>创建了新的考核周期"2024年第二季度"</p>
                <span class="activity-time">1小时前</span>
              </div>
            </div>
            <div class="activity-item">
              <el-icon class="activity-icon"><Document /></el-icon>
              <div class="activity-content">
                <p>李四提交了考核任务评分</p>
                <span class="activity-time">2小时前</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Calendar, Document, Check, TrendCharts, ArrowUp, ArrowRight, 
  Bell, User, Refresh, Plus
} from '@element-plus/icons-vue'
import { statsApi, cycleApi } from '@/utils/api'
import type { EvaluationCycle, EvaluationStats } from '@/types'
import { Button, Card, StatCard, Progress, EmptyState } from '@/components/ui'
import EmptyStateComponent from '@/components/EmptyState.vue'

const router = useRouter()

// 数据状态
const loading = ref(true)
const stats = ref<EvaluationStats | null>(null)
const cycles = ref<EvaluationCycle[]>([])

// 快捷操作配置
const quickActions = ref([
  {
    key: 'cycles',
    title: '创建考核周期',
    description: '设置新的绩效考核时间周期',
    icon: Calendar,
    variant: 'primary',
    handler: () => goToCycles()
  },
  {
    key: 'tasks',
    title: '查看考核任务',
    description: '管理和跟踪考核任务进度',
    icon: Document,
    variant: 'success',
    handler: () => goToTasks()
  },
  {
    key: 'results',
    title: '查看考核结果',
    description: '分析和查看考核数据报告',
    icon: TrendCharts,
    variant: 'info',
    handler: () => goToResults()
  },
  {
    key: 'employees',
    title: '员工管理',
    description: '管理员工信息和组织架构',
    icon: User,
    variant: 'warning',
    handler: () => goToEmployees()
  }
])

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    
    // 并行加载统计数据
    const [statsResponse, cyclesResponse] = await Promise.all([
      statsApi.overview(),
      cycleApi.list()
    ])
    
    stats.value = statsResponse.data
    cycles.value = cyclesResponse.data.results || []
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  await loadData()
}

// 导航方法
const goToCycles = () => router.push('/cycles')
const goToTasks = () => router.push('/tasks')
const goToResults = () => router.push('/results')
const goToEmployees = () => router.push('/employees')

// 工具方法
const getCycleStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'draft': 'info',
    'active': 'success',
    'completed': 'warning',
    'cancelled': 'danger'
  }
  return statusMap[status] || 'info'
}

const getCycleStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'draft': '草稿',
    'active': '进行中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

const getCycleProgress = (cycle: EvaluationCycle) => {
  // 简单的进度计算逻辑
  if (cycle.status === 'completed') return 100
  if (cycle.status === 'draft') return 0
  return Math.floor(Math.random() * 80) + 20 // 模拟进度
}

const getProgressColor = (percentage: number) => {
  if (percentage < 30) return '#f56c6c'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
/* 现代化仪表板样式 */
.modern-dashboard {
  padding: 0;
  min-height: 100%;
  background: var(--surface-secondary);
}

/* 仪表板头部 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-8);
  padding: var(--spacing-6) 0;
  background: var(--surface-primary);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-subtle);
}

.header-content {
  flex: 1;
  padding: 0 var(--spacing-6);
}

.dashboard-title {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--spacing-2) 0;
  letter-spacing: -0.025em;
  line-height: var(--leading-tight);
}

.dashboard-subtitle {
  font-size: var(--text-lg);
  color: var(--text-secondary);
  margin: 0;
  font-weight: var(--font-normal);
  line-height: var(--leading-relaxed);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: 0 var(--spacing-6);
}

/* 统计区域 */
.stats-section {
  margin-bottom: var(--spacing-8);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-6);
}

/* 内容区域 */
.content-section {
  margin-bottom: var(--spacing-8);
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: var(--spacing-6);
}

/* 卡片通用样式 */
.card-header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-4);
}

.card-title-section {
  flex: 1;
}

.card-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--spacing-1) 0;
  line-height: var(--leading-tight);
}

.card-subtitle {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
  line-height: var(--leading-normal);
}

/* 考核周期概览 */
.cycles-overview-card {
  min-height: 500px;
}

.cycles-content {
  padding: var(--spacing-2) 0;
}

.loading-state {
  padding: var(--spacing-6);
}

.loading-skeleton {
  padding: var(--spacing-4);
}

.cycles-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.cycle-item {
  padding: var(--spacing-5);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--surface-tertiary);
  transition: all var(--duration-normal) var(--ease-out);
  cursor: pointer;
}

.cycle-item:hover {
  border-color: var(--border-default);
  background: var(--surface-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.cycle-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-3);
}

.cycle-info {
  flex: 1;
  min-width: 0;
}

.cycle-name {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--spacing-1) 0;
  line-height: var(--leading-tight);
}

.cycle-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
  line-height: var(--leading-normal);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cycle-meta {
  margin-top: var(--spacing-2);
}

.cycle-date {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-weight: var(--font-medium);
}

.cycle-progress-section {
  margin-top: var(--spacing-3);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-2);
}

.progress-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-weight: var(--font-medium);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.progress-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-semibold);
}

/* 快捷操作面板 */
.quick-actions-card {
  height: fit-content;
}

.quick-actions-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.action-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--surface-tertiary);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out);
  position: relative;
  overflow: hidden;
}

.action-item:hover {
  border-color: var(--border-default);
  background: var(--surface-primary);
  transform: translateY(-2px) translateX(4px);
  box-shadow: var(--shadow-lg);
}

.action-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 4px;
  background: var(--brand-primary-500);
  opacity: 0;
  transition: opacity var(--duration-fast) var(--ease-out);
}

.action-item:hover::before {
  opacity: 1;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xl);
  flex-shrink: 0;
  transition: transform var(--duration-fast) var(--ease-out);
}

.action-item:hover .action-icon {
  transform: scale(1.1);
}

.action-icon-primary {
  background: var(--brand-primary-50);
  color: var(--brand-primary-600);
}

.action-icon-success {
  background: var(--semantic-success-50);
  color: var(--semantic-success-600);
}

.action-icon-info {
  background: var(--semantic-info-50);
  color: var(--semantic-info-600);
}

.action-icon-warning {
  background: var(--semantic-warning-50);
  color: var(--semantic-warning-600);
}

.action-content {
  flex: 1;
  min-width: 0;
}

.action-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--spacing-1) 0;
  line-height: var(--leading-tight);
}

.action-description {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin: 0;
  line-height: var(--leading-normal);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.action-arrow {
  color: var(--text-quaternary);
  font-size: var(--text-sm);
  flex-shrink: 0;
  transition: all var(--duration-fast) var(--ease-out);
}

.action-item:hover .action-arrow {
  color: var(--brand-primary-600);
  transform: translateX(4px);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-6);
  }
  
  .cycles-overview-card {
    min-height: auto;
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-4);
  }
  
  .header-actions {
    justify-content: flex-end;
  }
  
  .dashboard-title {
    font-size: var(--text-3xl);
  }
  
  .dashboard-subtitle {
    font-size: var(--text-base);
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-4);
  }
  
  .action-item {
    padding: var(--spacing-3);
  }
  
  .action-icon {
    width: 40px;
    height: 40px;
    font-size: var(--text-lg);
  }
}

@media (max-width: 640px) {
  .dashboard-header {
    margin-bottom: var(--spacing-6);
    padding: var(--spacing-4);
  }
  
  .content-grid {
    gap: var(--spacing-4);
  }
  
  .stats-grid {
    gap: var(--spacing-3);
  }
}
</style>