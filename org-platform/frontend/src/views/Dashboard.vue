<template>
  <div class="dashboard-page">
    <!-- 现代化页面头部 -->
    <ModernPageHeader
      title="组织架构中台"
      subtitle="智能化组织管理与数据分析平台"
      icon="TrendCharts"
      color="blue"
    >
      <template #actions>
        <ModernButton type="secondary" icon="Download">
          导出报告
        </ModernButton>
        <ModernButton type="primary" icon="Plus">
          快速操作
        </ModernButton>
      </template>
    </ModernPageHeader>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <ModernStatCard
        title="总员工数"
        :value="stats.active_employees || 0"
        change="+12 本月"
        change-type="positive"
        icon="User"
        icon-type="primary"
      />
      <ModernStatCard
        title="部门数量"
        :value="stats.active_departments || 0"
        change="+2 本月"
        change-type="positive"
        icon="OfficeBuilding"
        icon-type="success"
      />
      <ModernStatCard
        title="职位数量"
        :value="stats.active_positions || 0"
        change="+8 本月"
        change-type="positive"
        icon="Suitcase"
        icon-type="warning"
      />
      <ModernStatCard
        title="活跃租户"
        :value="15"
        change="+1 本月"
        change-type="positive"
        icon="Globe"
        icon-type="success"
      />
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 快速导航 -->
      <ModernCard title="快速导航" icon="Rocket" class="navigation-card">
        <div class="nav-grid">
          <div class="nav-item" @click="$router.push('/employees')">
            <div class="nav-icon blue">
              <el-icon><User /></el-icon>
            </div>
            <div class="nav-info">
              <h4>员工管理</h4>
              <p>管理员工信息</p>
            </div>
          </div>
          
          <div class="nav-item" @click="$router.push('/departments')">
            <div class="nav-icon emerald">
              <el-icon><OfficeBuilding /></el-icon>
            </div>
            <div class="nav-info">
              <h4>部门管理</h4>
              <p>组织架构管理</p>
            </div>
          </div>
          
          <div class="nav-item" @click="$router.push('/positions')">
            <div class="nav-icon green">
              <el-icon><Suitcase /></el-icon>
            </div>
            <div class="nav-info">
              <h4>职位管理</h4>
              <p>职位体系管理</p>
            </div>
          </div>
          
          <div class="nav-item" @click="$router.push('/workflow-rules')">
            <div class="nav-icon purple">
              <el-icon><Setting /></el-icon>
            </div>
            <div class="nav-info">
              <h4>工作流</h4>
              <p>流程规则配置</p>
            </div>
          </div>
          
          <div class="nav-item" @click="$router.push('/intelligent-analysis')">
            <div class="nav-icon indigo">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="nav-info">
              <h4>智能分析</h4>
              <p>AI驱动分析</p>
            </div>
          </div>
          
          <div class="nav-item" @click="$router.push('/permission-management')">
            <div class="nav-icon purple">
              <el-icon><Lock /></el-icon>
            </div>
            <div class="nav-info">
              <h4>权限管理</h4>
              <p>安全权限控制</p>
            </div>
          </div>
        </div>
      </ModernCard>

      <!-- 最近活动 -->
      <ModernCard title="最近活动" icon="Clock" class="activity-card">
        <template #actions>
          <ModernButton type="secondary" icon="Refresh" size="small">
            查看全部
          </ModernButton>
        </template>
        
        <div class="activity-list">
          <div class="activity-item">
            <div class="activity-icon blue">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="activity-content">
              <div class="activity-title">新员工入职</div>
              <div class="activity-desc">张三加入技术部</div>
              <div class="activity-time">5分钟前</div>
            </div>
          </div>
          
          <div class="activity-item">
            <div class="activity-icon emerald">
              <el-icon><OfficeBuilding /></el-icon>
            </div>
            <div class="activity-content">
              <div class="activity-title">部门调整</div>
              <div class="activity-desc">产品部组织架构更新</div>
              <div class="activity-time">1小时前</div>
            </div>
          </div>
          
          <div class="activity-item">
            <div class="activity-icon green">
              <el-icon><Suitcase /></el-icon>
            </div>
            <div class="activity-content">
              <div class="activity-title">职位创建</div>
              <div class="activity-desc">新增高级产品经理职位</div>
              <div class="activity-time">2小时前</div>
            </div>
          </div>
          
          <div class="activity-item">
            <div class="activity-icon purple">
              <el-icon><Setting /></el-icon>
            </div>
            <div class="activity-content">
              <div class="activity-title">工作流更新</div>
              <div class="activity-desc">员工转岗流程优化</div>
              <div class="activity-time">3小时前</div>
            </div>
          </div>
          
          <div class="activity-item">
            <div class="activity-icon indigo">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="activity-content">
              <div class="activity-title">分析报告</div>
              <div class="activity-desc">月度组织健康度报告生成</div>
              <div class="activity-time">4小时前</div>
            </div>
          </div>
        </div>
      </ModernCard>
    </div>

    <!-- 底部网格 -->
    <div class="bottom-grid">
      <!-- 系统状态 -->
      <ModernCard title="系统状态" icon="Monitor" class="status-card">
        <div class="status-grid">
          <div class="status-item">
            <div class="status-indicator online"></div>
            <div class="status-info">
              <h5>核心服务</h5>
              <p>运行正常</p>
            </div>
          </div>
          <div class="status-item">
            <div class="status-indicator online"></div>
            <div class="status-info">
              <h5>数据库</h5>
              <p>连接正常</p>
            </div>
          </div>
          <div class="status-item">
            <div class="status-indicator warning"></div>
            <div class="status-info">
              <h5>集成服务</h5>
              <p>部分延迟</p>
            </div>
          </div>
          <div class="status-item">
            <div class="status-indicator online"></div>
            <div class="status-info">
              <h5>权限服务</h5>
              <p>运行正常</p>
            </div>
          </div>
        </div>
      </ModernCard>

      <!-- 数据概览 -->
      <ModernCard title="数据概览" icon="Database" class="data-card">
        <div class="status-grid">
          <div class="status-item">
            <div class="status-indicator online"></div>
            <div class="status-info">
              <h5>数据同步</h5>
              <p>实时同步中</p>
            </div>
          </div>
          <div class="status-item">
            <div class="status-indicator online"></div>
            <div class="status-info">
              <h5>备份状态</h5>
              <p>今日已备份</p>
            </div>
          </div>
          <div class="status-item">
            <div class="status-indicator online"></div>
            <div class="status-info">
              <h5>存储空间</h5>
              <p>使用率 68%</p>
            </div>
          </div>
          <div class="status-item">
            <div class="status-indicator online"></div>
            <div class="status-info">
              <h5>API调用</h5>
              <p>今日 2.3K</p>
            </div>
          </div>
        </div>
      </ModernCard>

      <!-- 快速统计 -->
      <ModernCard title="快速统计" icon="PieChart" class="quick-stats-card">
        <div class="status-grid">
          <div class="status-item">
            <div class="status-indicator blue"></div>
            <div class="status-info">
              <h5>在职员工</h5>
              <p>{{ stats.active_employees || 0 }} 人</p>
            </div>
          </div>
          <div class="status-item">
            <div class="status-indicator emerald"></div>
            <div class="status-info">
              <h5>本月入职</h5>
              <p>12 人</p>
            </div>
          </div>
          <div class="status-item">
            <div class="status-indicator green"></div>
            <div class="status-info">
              <h5>职位空缺</h5>
              <p>8 个</p>
            </div>
          </div>
          <div class="status-item">
            <div class="status-indicator purple"></div>
            <div class="status-info">
              <h5>待审批</h5>
              <p>3 项</p>
            </div>
          </div>
        </div>
      </ModernCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { useOrganizationStore } from '@/stores/organization'
import { Plus, View, User, OfficeBuilding, Suitcase, Setting, DataAnalysis, Lock, UserFilled, TrendCharts } from '@element-plus/icons-vue'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'

interface KpiCard {
  key: string
  label: string
  displayValue: string
  tag: string
  tagClass: string
  palette: string
  progress?: number
  progressLabel?: string
}

interface LevelItem {
  label: string | number
  count: number
  percent: number
}

const organizationStore = useOrganizationStore()

const stats = computed<Record<string, any>>(() => organizationStore.stats || {})

const formatNumber = (value: number) => {
  const num = Number(value) || 0
  return new Intl.NumberFormat('zh-CN').format(num)
}

const kpiCards = computed<KpiCard[]>(() => {
  const s = stats.value
  const departments = Number(s.active_departments) || 0
  const positions = Number(s.active_positions) || 0
  const employees = Number(s.active_employees) || 0
  const totalUnits = departments + positions
  const changeEvents = Number(s.changes_this_month ?? s.recent_changes ?? 0)

  const cards: KpiCard[] = [
    {
      key: 'departments',
      label: '部门数',
      displayValue: formatNumber(departments),
      tag: '实时',
      tagClass: 'tag-brand',
      palette: 'palette-brand'
    },
    {
      key: 'employees',
      label: '员工数',
      displayValue: formatNumber(employees),
      tag: '本月',
      tagClass: 'tag-emerald',
      palette: 'palette-emerald'
    },
    {
      key: 'units',
      label: '组织单元',
      displayValue: formatNumber(totalUnits),
      tag: '总览',
      tagClass: 'tag-blue',
      palette: 'palette-blue'
    }
  ]

  const quota = Number(s.employee_quota)
  if (!Number.isNaN(quota) && quota > 0) {
    const utilization = Math.min(100, Math.round((employees / quota) * 100))
    cards.push({
      key: 'utilization',
      label: '编制使用率',
      displayValue: `${utilization}%`,
      tag: '目标 ≤ 95%',
      tagClass: 'tag-amber',
      palette: 'palette-amber',
      progress: utilization,
      progressLabel: '利用率'
    })
  } else {
    cards.push({
      key: 'changes',
      label: '本月变更',
      displayValue: formatNumber(changeEvents),
      tag: '入/转/离',
      tagClass: 'tag-fuchsia',
      palette: 'palette-fuchsia'
    })
  }

  return cards
})

const normalizeLevels = (items: unknown): LevelItem[] => {
  const array = Array.isArray(items) ? items : []
  const total = array.reduce((sum: number, item: any) => sum + (Number(item?.count) || 0), 0)
  return array.map((item: any) => {
    const count = Number(item?.count) || 0
    const level = item?.level ?? item?.label ?? '-'
    const percent = total ? Math.round((count / total) * 100) : 0
    return { label: level, count, percent }
  })
}

const departmentLevels = computed<LevelItem[]>(() => normalizeLevels(stats.value.department_levels))
const positionLevels = computed<LevelItem[]>(() => normalizeLevels(stats.value.position_levels))

onMounted(async () => {
  try {
    await organizationStore.fetchStats()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
})
</script>

<style scoped>
.dashboard-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
  min-height: 100vh;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* 主内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

/* 导航网格 */
.nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
  cursor: pointer;
  background: white;
}

.nav-item:hover {
  border-color: #3b82f6;
  background: #f8fafc;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.nav-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: white;
}

.nav-icon.blue { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.nav-icon.emerald { background: linear-gradient(135deg, #10b981, #059669); }
.nav-icon.green { background: linear-gradient(135deg, #22c55e, #16a34a); }
.nav-icon.purple { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.nav-icon.indigo { background: linear-gradient(135deg, #6366f1, #4f46e5); }

.nav-info h4 {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  color: #111827;
}

.nav-info p {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0;
}

.kpi-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kpi-label {
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6b7280 !important;
  margin: 0;
}

.kpi-tag {
  border-radius: 9999px;
  padding: 2px 10px;
  font-size: 11px;
  font-weight: 500;
}

.tag-brand { background: #eef7fd !important; color: #177fc1 !important; }
.tag-emerald { background: #ecfdf3 !important; color: #047857 !important; }
.tag-blue { background: #e0f2fe !important; color: #0369a1 !important; }
.tag-amber { background: #fef3c7 !important; color: #b45309 !important; }
.tag-fuchsia { background: #fdf4ff !important; color: #a21caf !important; }

.kpi-body {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
}

.kpi-body h3 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #111827 !important;
}

.kpi-bubble {
  width: 36px;
  height: 36px;
  border-radius: 12px;
}

.palette-brand { background: linear-gradient(135deg, #4faee7, #177fc1); }
.palette-emerald { background: linear-gradient(135deg, #34d399, #0d9488); }
.palette-blue { background: linear-gradient(135deg, #60a5fa, #2563eb); }
.palette-amber { background: linear-gradient(135deg, #fbbf24, #f59e0b); }
.palette-fuchsia { background: linear-gradient(135deg, #ec4899, #a855f7); }

.kpi-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.kpi-progress-track {
  width: 100%;
  height: 6px;
  border-radius: 9999px;
  background: #f3f4f6 !important;
  overflow: hidden;
}

.kpi-progress-fill {
  height: 100%;
  border-radius: 9999px;
  background: linear-gradient(135deg, #f97316, #fb923c);
  transition: width 0.3s ease;
}

.kpi-progress-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280 !important;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.chart-card {
  background: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 16px !important;
  padding: 20px !important;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-card.large {
  grid-column: span 2;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chart-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827 !important;
}

.chart-sub {
  font-size: 12px;
  color: #6b7280 !important;
}

.chart-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.level-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.level-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.level-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.level-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #177fc1 !important;
}

.level-dot.secondary {
  background: #10b981 !important;
}

.level-name {
  font-size: 13px;
  color: #1f2937 !important;
}

.level-right {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 160px;
}

.level-value {
  font-size: 12px;
  color: #6b7280 !important;
  min-width: 48px;
}

.level-bar {
  flex: 1;
  height: 6px;
  border-radius: 9999px;
  background: #f3f4f6 !important;
  overflow: hidden;
}

.level-bar-fill {
  height: 100%;
  border-radius: 9999px;
  background: linear-gradient(135deg, #4faee7, #177fc1);
  transition: width 0.3s ease;
}

.level-bar-fill.secondary {
  background: linear-gradient(135deg, #34d399, #0d9488);
}

.level-list.compact .level-row {
  gap: 12px;
}

.empty-placeholder {
  padding: 40px 0;
  text-align: center;
  font-size: 13px;
  color: #9ca3af !important;
}

.action-panel {
  background: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 16px !important;
  padding: 20px !important;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.action-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.action-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827 !important;
}

.action-header p {
  margin: 4px 0 0;
  font-size: 13px;
  color: #6b7280 !important;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

:deep(.action-btn) {
  width: 100%;
  justify-content: flex-start;
  gap: 8px;
  padding: 12px 16px !important;
  background: #f9fafb !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 12px !important;
  color: #111827 !important;
}

:deep(.action-btn:hover) {
  background: #f3f4f6 !important;
}

:deep(.action-btn .el-icon) {
  font-size: 16px;
}

/* 活动列表 */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.activity-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  border: 1px solid #f3f4f6;
  transition: all 0.2s ease;
}

.activity-item:hover {
  border-color: #e5e7eb;
  background: #f9fafb;
}

.activity-icon {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: white;
  flex-shrink: 0;
}

.activity-icon.blue { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.activity-icon.emerald { background: linear-gradient(135deg, #10b981, #059669); }
.activity-icon.green { background: linear-gradient(135deg, #22c55e, #16a34a); }
.activity-icon.purple { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.activity-icon.indigo { background: linear-gradient(135deg, #6366f1, #4f46e5); }

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: #111827;
}

.activity-desc {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.activity-time {
  font-size: 0.625rem;
  color: #9ca3af;
}

/* 底部网格 */
.bottom-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

/* 状态网格 */
.status-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 0.5rem;
  background: #f9fafb;
}

.status-indicator {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-indicator.online { background: #10b981; }
.status-indicator.offline { background: #ef4444; }
.status-indicator.warning { background: #f59e0b; }
.status-indicator.blue { background: #3b82f6; border-radius: 0.25rem; }
.status-indicator.emerald { background: #10b981; border-radius: 0.25rem; }
.status-indicator.green { background: #22c55e; border-radius: 0.25rem; }
.status-indicator.purple { background: #8b5cf6; border-radius: 0.25rem; }

.status-info h5 {
  font-size: 0.75rem;
  font-weight: 500;
  margin: 0 0 0.125rem 0;
  color: #111827;
}

.status-info p {
  font-size: 0.625rem;
  color: #6b7280;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .dashboard-page {
    padding: 1rem;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .nav-grid {
    grid-template-columns: 1fr;
  }
  
  .bottom-grid {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>



