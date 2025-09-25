<template>
  <div class="container dashboard-view">
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">首页概览</h3>
      <div class="toolbar"></div>
    </div>

    <div class="kpi-grid">
      <div v-for="card in kpiCards" :key="card.key" class="kpi-card">
        <div class="kpi-header">
          <p class="kpi-label">{{ card.label }}</p>
          <span class="kpi-tag" :class="card.tagClass">{{ card.tag }}</span>
        </div>
        <div class="kpi-body">
          <h3>{{ card.displayValue }}</h3>
          <div class="kpi-bubble" :class="card.palette"></div>
        </div>
        <div v-if="card.progress !== undefined" class="kpi-progress">
          <div class="kpi-progress-track">
            <div class="kpi-progress-fill" :style="{ width: card.progress + '%' }"></div>
          </div>
          <div class="kpi-progress-meta">
            <span>{{ card.progress }}%</span>
            <span>{{ card.progressLabel }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="chart-grid">
      <div class="chart-card large">
        <div class="chart-header">
          <h3>部门层级分布</h3>
          <span class="chart-sub">当前结构</span>
        </div>
        <div class="chart-body">
          <div v-if="departmentLevels.length" class="level-list">
            <div v-for="level in departmentLevels" :key="level.label" class="level-row">
              <div class="level-left">
                <span class="level-dot"></span>
                <span class="level-name">第 {{ level.label }} 层</span>
              </div>
              <div class="level-right">
                <span class="level-value">{{ level.count }} 个</span>
                <div class="level-bar">
                  <div class="level-bar-fill" :style="{ width: level.percent + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-placeholder">暂无部门层级数据</div>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>职位级别分布</h3>
          <span class="chart-sub">活跃职位</span>
        </div>
        <div class="chart-body">
          <div v-if="positionLevels.length" class="level-list compact">
            <div v-for="level in positionLevels" :key="level.label" class="level-row">
              <div class="level-left">
                <span class="level-dot secondary"></span>
                <span class="level-name">级别 {{ level.label }}</span>
              </div>
              <div class="level-right">
                <span class="level-value">{{ level.count }} 个</span>
                <div class="level-bar">
                  <div class="level-bar-fill secondary" :style="{ width: level.percent + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-placeholder">暂无职位级别数据</div>
        </div>
      </div>
    </div>

    <div class="action-panel">
      <div class="action-header">
        <div>
          <h3>快捷操作</h3>
          <p>常用入口与新增操作</p>
        </div>
        <el-tag size="small" effect="plain">日常管理</el-tag>
      </div>
      <div class="action-grid">
        <el-button class="action-btn" @click="$router.push('/departments')">
          <el-icon><Plus /></el-icon>
          新建部门
        </el-button>
        <el-button class="action-btn" @click="$router.push('/positions')">
          <el-icon><Plus /></el-icon>
          新建职位
        </el-button>
        <el-button class="action-btn" @click="$router.push('/employees')">
          <el-icon><Plus /></el-icon>
          新建员工
        </el-button>
        <el-button class="action-btn" @click="$router.push('/organization-tree')">
          <el-icon><View /></el-icon>
          查看组织架构
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { useOrganizationStore } from '@/stores/organization'
import { Plus, View } from '@element-plus/icons-vue'

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
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-bottom: 32px;
  background: #ffffff !important;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.kpi-card {
  background: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 16px !important;
  padding: 20px !important;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
  display: flex;
  flex-direction: column;
  gap: 16px;
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

@media (max-width: 768px) {
  .kpi-card {
    padding: 16px !important;
  }

  .chart-card.large {
    grid-column: span 1;
  }

  .action-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}
</style>



