<template>
  <div class="reports-container">
    <!-- 现代化头部 -->
    <div class="modern-header">
      <div class="header-content">
        <div class="header-info">
          <div class="title-section">
            <h1 class="main-title">
              <el-icon class="title-icon"><DataAnalysis /></el-icon>
              报表中心
            </h1>
            <p class="subtitle">智能数据分析与可视化报表生成平台</p>
          </div>
          <div class="stats-overview">
            <div class="stat-item">
              <span class="stat-value">{{ cycles.length }}</span>
              <span class="stat-label">考核周期</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ kpi.completed_tasks || 0 }}</span>
              <span class="stat-label">已完成任务</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ kpi.completion_rate || 0 }}%</span>
              <span class="stat-label">完成率</span>
            </div>
          </div>
        </div>
        
        <div class="header-controls">
          <div class="control-group">
            <label class="control-label">考核周期</label>
            <el-select 
              v-model="selectedCycle" 
              placeholder="选择考核周期" 
              class="cycle-selector"
              @change="onCycleChange"
            >
              <el-option v-for="cycle in cycles" :key="cycle.id" :label="cycle.name" :value="cycle.id" />
            </el-select>
          </div>
          
          <div class="action-buttons">
            <el-button type="primary" @click="generateReport" class="action-btn">
              <el-icon><Refresh /></el-icon>
              生成报表
            </el-button>
            <el-button @click="refreshData" class="action-btn">
              <el-icon><RefreshRight /></el-icon>
              刷新数据
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能工具栏 -->
    <div class="toolbar-section">
      <div class="toolbar-content">
        <ReportTemplates @template-selected="onTemplateSelected" />
      </div>
    </div>

    <!-- 现代化报表内容区域 -->
    <div class="modern-report-content">
      <!-- 概览报表 -->
      <div v-if="selectedReportType === 'overview'" class="report-dashboard">
        <div class="dashboard-header">
          <div class="header-info">
            <h2 class="dashboard-title">
              <el-icon class="title-icon"><DataAnalysis /></el-icon>
              概览报表
            </h2>
            <p class="dashboard-desc">核心指标概览与数据洞察</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="exportOverview" class="export-btn">
              <el-icon><Download /></el-icon>
              导出概览
            </el-button>
          </div>
        </div>
        
        <!-- 现代化KPI指标卡片 -->
        <div class="modern-kpi-grid">
          <div class="kpi-card modern-card completion">
            <div class="card-header">
              <div class="card-icon completion-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="card-info">
                <h3 class="card-title">完成率</h3>
                <p class="card-subtitle">目标完成情况</p>
              </div>
              <div class="card-badge success">
                <span>目标 100%</span>
              </div>
            </div>
            <div class="card-content">
              <div class="metric-value">{{ kpi.completion_rate || 0 }}%</div>
              <div class="progress-container">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{width: (kpi.completion_rate || 0) + '%'}"></div>
                </div>
                <span class="progress-text">{{ kpi.completion_rate || 0 }}% 完成</span>
              </div>
            </div>
          </div>

          <div class="kpi-card modern-card score">
            <div class="card-header">
              <div class="card-icon score-icon">
                <el-icon><PieChart /></el-icon>
              </div>
              <div class="card-info">
                <h3 class="card-title">平均评分</h3>
                <p class="card-subtitle">整体绩效水平</p>
              </div>
              <div class="card-badge warning">
                <span>{{ kpi.avg_score || '-' }}</span>
              </div>
            </div>
            <div class="card-content">
              <div class="metric-value">{{ kpi.avg_grade || '-' }}</div>
              <div class="metric-detail">
                <span class="detail-text">分布见右侧图表</span>
              </div>
            </div>
          </div>

          <div class="kpi-card modern-card tasks">
            <div class="card-header">
              <div class="card-icon tasks-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="card-info">
                <h3 class="card-title">已完成任务</h3>
                <p class="card-subtitle">实时统计</p>
              </div>
              <div class="card-badge info">
                <span>实时</span>
              </div>
            </div>
            <div class="card-content">
              <div class="metric-value">{{ kpi.completed_tasks || 0 }}</div>
              <div class="metric-detail">
                <span class="detail-text">周期内已完成数量</span>
              </div>
            </div>
          </div>

          <div class="kpi-card modern-card cycles">
            <div class="card-header">
              <div class="card-icon cycles-icon">
                <el-icon><Refresh /></el-icon>
              </div>
              <div class="card-info">
                <h3 class="card-title">活跃周期</h3>
                <p class="card-subtitle">当前进行中</p>
              </div>
              <div class="card-badge primary">
                <span>{{ kpi.active_cycles || 0 }}</span>
              </div>
            </div>
            <div class="card-content">
              <div class="metric-value">{{ kpi.active_cycles || 0 }}</div>
              <div class="metric-detail">
                <span class="detail-text">当前进行中的周期</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 绩效分析报表 -->
      <div v-if="selectedReportType === 'performance'" class="report-dashboard">
        <div class="dashboard-header">
          <div class="header-info">
            <h2 class="dashboard-title">
              <el-icon class="title-icon"><PieChart /></el-icon>
              绩效分析报表
            </h2>
            <p class="dashboard-desc">详细的绩效分析，包含评分分布、部门对比等深度分析</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="exportPerformance" class="export-btn">
              <el-icon><Download /></el-icon>
              导出绩效分析
            </el-button>
          </div>
        </div>
        
        <div class="modern-charts-grid">
          <div class="chart-card modern-chart">
            <div class="chart-header">
              <h4>评分分布分析</h4>
            </div>
            <div ref="scoreDistributionRef" class="chart-container"></div>
          </div>
          
          <div class="chart-card modern-chart">
            <div class="chart-header">
              <h4>部门绩效对比</h4>
            </div>
            <div ref="deptPerformanceRef" class="chart-container"></div>
          </div>
        </div>
      </div>

      <!-- 趋势分析报表 -->
      <div v-if="selectedReportType === 'trend'" class="report-dashboard">
        <div class="dashboard-header">
          <div class="header-info">
            <h2 class="dashboard-title">
              <el-icon class="title-icon"><TrendCharts /></el-icon>
              趋势分析报表
            </h2>
            <p class="dashboard-desc">展示绩效完成趋势、月度对比等时间序列分析</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="exportTrend" class="export-btn">
              <el-icon><Download /></el-icon>
              导出趋势分析
            </el-button>
          </div>
        </div>
        
        <div class="modern-charts-grid">
          <div class="chart-card modern-chart large">
            <div class="chart-header">
              <h4>绩效完成趋势</h4>
            </div>
            <div ref="trendChartRef" class="chart-container"></div>
          </div>
          
          <div class="chart-card modern-chart">
            <div class="chart-header">
              <h4>月度对比</h4>
            </div>
            <div ref="monthlyComparisonRef" class="chart-container"></div>
          </div>
        </div>
      </div>

      <!-- 详细数据报表 -->
      <div v-if="selectedReportType === 'detailed'" class="report-dashboard">
        <div class="dashboard-header">
          <div class="header-info">
            <h2 class="dashboard-title">
              <el-icon class="title-icon"><Document /></el-icon>
              详细数据报表
            </h2>
            <p class="dashboard-desc">包含所有详细数据的表格形式报表，支持筛选和排序</p>
          </div>
          <div class="header-actions">
            <div class="search-group">
              <el-input 
                v-model="searchKeyword" 
                placeholder="搜索员工/部门" 
                class="search-input"
                clearable 
                @keyup.enter="loadDetailedData" 
              />
              <el-button @click="loadDetailedData" class="search-btn">搜索</el-button>
            </div>
            <el-button type="primary" @click="exportDetailed" class="export-btn">
              <el-icon><Download /></el-icon>
              导出详细数据
            </el-button>
          </div>
        </div>
        
        <div class="modern-data-table">
          <el-table :data="detailedData" v-loading="loading" stripe class="modern-table">
            <el-table-column type="index" label="序号" width="80" />
            <el-table-column prop="employee_name" label="员工姓名" min-width="120" />
            <el-table-column prop="department" label="部门" width="120" />
            <el-table-column prop="position" label="职位" width="120" />
            <el-table-column prop="score" label="评分" width="100">
              <template #default="{ row }">
                <span class="modern-score-badge" :class="getScoreClass(row.score)">{{ row.score }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="grade" label="等级" width="80">
              <template #default="{ row }">
                <el-tag :type="getGradeType(row.grade)" size="small">{{ row.grade }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="completion_rate" label="完成度" width="100">
              <template #default="{ row }">
                <div class="modern-completion-bar">
                  <div class="modern-bar-bg">
                    <div class="modern-bar-fill" :style="{width: row.completion_rate + '%'}"></div>
                  </div>
                  <span class="modern-completion-text">{{ row.completion_rate }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间" width="150">
              <template #default="{ row }">
                {{ formatDateTime(row.updated_at) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <!-- 自定义报表构建器对话框 -->
    <el-dialog
      v-model="showCustomBuilder"
      title="自定义报表构建器"
      width="95%"
      :close-on-click-modal="false"
    >
      <CustomReportBuilder @report-saved="onReportSaved" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import { cycleApi, taskApi, statsApi } from '@/utils/api'
import { ElMessage } from 'element-plus'
import { Edit, DataAnalysis, Refresh, RefreshRight, PieChart, TrendCharts, Document, Download } from '@element-plus/icons-vue'
import ReportTemplates from '@/components/ReportTemplates.vue'
import CustomReportBuilder from '@/components/CustomReportBuilder.vue'
import ReportExporter from '@/components/ReportExporter.vue'
import { formatDateTime } from '@/utils/dateUtils'

// 基础数据
const cycles = ref<any[]>([])
const selectedCycle = ref<number | null>(null)
const loading = ref(false)
const kpi = ref<any>({})

// 报表类型
const selectedReportType = ref('overview')
const reportTypes = ref([
  { id: 'overview', name: '概览报表', icon: 'DataAnalysis' },
  { id: 'performance', name: '绩效分析', icon: 'PieChart' },
  { id: 'trend', name: '趋势分析', icon: 'TrendCharts' },
  { id: 'detailed', name: '详细数据', icon: 'Document' }
])

// 图表引用
const scoreDistributionRef = ref<HTMLElement>()
const deptPerformanceRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const monthlyComparisonRef = ref<HTMLElement>()

// 详细数据
const detailedData = ref<any[]>([])
const searchKeyword = ref('')
const total = ref(0)
const page = ref(1)
const size = ref(20)

// 报表功能增强
const showCustomBuilder = ref(false)

// 方法
const loadCycles = async () => {
  try {
    const res = await cycleApi.list()
    cycles.value = res.data?.results || res.data || []
    if (cycles.value.length > 0 && !selectedCycle.value) {
      selectedCycle.value = cycles.value[0].id
    }
  } catch (error) {
    console.error('加载考核周期失败:', error)
  }
}

const loadKpi = async () => {
  try {
    const res = await statsApi.overview()
    kpi.value = res.data || {}
  } catch (error) {
    console.error('加载KPI数据失败:', error)
    kpi.value = {
      completion_rate: 0,
      avg_score: 0,
      avg_grade: 'B',
      completed_tasks: 0,
      total_cycles: 0,
      active_cycles: 0
    }
  }
}

const selectReportType = (type: string) => {
  selectedReportType.value = type
  nextTick(async () => {
    if (type === 'performance') {
      await initScoreDistributionChart()
      await initDeptPerformanceChart()
    } else if (type === 'trend') {
      initTrendChart()
      initMonthlyComparisonChart()
    } else if (type === 'detailed') {
      await loadDetailedData()
    }
  })
}

const onCycleChange = () => {
  refreshData()
}

const refreshData = async () => {
  await loadKpi()
  if (selectedReportType.value === 'detailed') {
    loadDetailedData()
  }
}

const generateReport = () => {
  ElMessage.success('报表生成中...')
  refreshData()
}

// 报表功能增强方法
const onTemplateSelected = (template: any) => {
  ElMessage.success(`已选择模板：${template.name}`)
  // 根据模板切换报表类型
  if (template.id === 'overview') {
    selectedReportType.value = 'overview'
  } else if (template.id === 'performance') {
    selectedReportType.value = 'performance'
  } else if (template.id === 'trend') {
    selectedReportType.value = 'trend'
  } else if (template.id === 'detailed') {
    selectedReportType.value = 'detailed'
  }
}

const onReportSaved = (reportData: any) => {
  ElMessage.success('自定义报表已保存')
  showCustomBuilder.value = false
  // 可以在这里处理保存的报表数据
  console.log('保存的报表数据:', reportData)
}

const loadDetailedData = async () => {
  try {
    loading.value = true
    console.log('加载详细数据，参数:', {
      page: page.value,
      page_size: size.value,
      search: searchKeyword.value,
      cycle: selectedCycle.value
    })
    
    const params = {
      page: page.value,
      page_size: size.value,
      search: searchKeyword.value,
      cycle: selectedCycle.value
    }
    
    const res = await taskApi.list(params)
    console.log('详细数据API响应:', res.data)
    
    // 处理数据，确保包含所需字段
    const tasks = res.data?.results || []
    detailedData.value = tasks.map((task: any) => ({
      id: task.id,
      employee_name: task.evaluatee_name || '未知员工',
      department: task.evaluatee_department || '未分配',
      position: task.evaluatee_position || '未知职位',
      score: task.avg_score || 0,
      grade: getGradeFromScore(task.avg_score || 0),
      completion_rate: task.status === 'completed' ? 100 : (task.status === 'in_progress' ? 50 : 0),
      updated_at: task.updated_at || task.created_at
    }))
    
    total.value = res.data?.count || 0
    console.log('处理后的详细数据:', detailedData.value)
  } catch (error) {
    console.error('加载详细数据失败:', error)
    ElMessage.error('加载数据失败: ' + (error as any)?.message || '未知错误')
    detailedData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 图表初始化
const initScoreDistributionChart = async () => {
  if (!scoreDistributionRef.value) return
  
  try {
    // 获取真实数据
    const res = await taskApi.list({ 
      page: 1, 
      page_size: 1000,
      cycle: selectedCycle.value 
    })
    const tasks = res.data?.results || []
    
    // 计算评分分布
    const distribution = {
      excellent: 0, // 90-100
      good: 0,      // 80-89
      average: 0,   // 70-79
      poor: 0       // 60-69
    }
    
    tasks.forEach((task: any) => {
      const score = task.avg_score || 0
      if (score >= 90) distribution.excellent++
      else if (score >= 80) distribution.good++
      else if (score >= 70) distribution.average++
      else distribution.poor++
    })
    
    const chart = echarts.init(scoreDistributionRef.value)
    const option = {
      title: {
        text: '评分分布',
        left: 'center',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      series: [{
        name: '评分分布',
        type: 'pie',
        radius: '60%',
        data: [
          { value: distribution.excellent, name: `优秀(90-100)`, itemStyle: { color: '#10b981' } },
          { value: distribution.good, name: `良好(80-89)`, itemStyle: { color: '#3b82f6' } },
          { value: distribution.average, name: `中等(70-79)`, itemStyle: { color: '#f59e0b' } },
          { value: distribution.poor, name: `待改进(60-69)`, itemStyle: { color: '#ef4444' } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    }
    chart.setOption(option)
    console.log('评分分布图表数据:', distribution)
  } catch (error) {
    console.error('加载评分分布数据失败:', error)
  }
}

const initDeptPerformanceChart = async () => {
  if (!deptPerformanceRef.value) return
  
  try {
    // 获取真实数据
    const res = await taskApi.list({ 
      page: 1, 
      page_size: 1000,
      cycle: selectedCycle.value 
    })
    const tasks = res.data?.results || []
    
    // 按部门统计平均分
    const deptStats: { [key: string]: { total: number, count: number, avg: number } } = {}
    
    tasks.forEach((task: any) => {
      const dept = task.evaluatee_department || '未分配'
      const score = task.avg_score || 0
      
      if (!deptStats[dept]) {
        deptStats[dept] = { total: 0, count: 0, avg: 0 }
      }
      deptStats[dept].total += score
      deptStats[dept].count += 1
    })
    
    // 计算平均分
    Object.keys(deptStats).forEach(dept => {
      deptStats[dept].avg = deptStats[dept].count > 0 
        ? Math.round((deptStats[dept].total / deptStats[dept].count) * 10) / 10 
        : 0
    })
    
    // 转换为图表数据
    const deptNames = Object.keys(deptStats)
    const deptScores = deptNames.map(dept => deptStats[dept].avg)
    
    const chart = echarts.init(deptPerformanceRef.value)
    const option = {
      title: {
        text: '部门绩效对比',
        left: 'center',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: any) => {
          const data = params[0]
          return `${data.name}<br/>平均分: ${data.value}分`
        }
      },
      xAxis: {
        type: 'category',
        data: deptNames,
        axisLabel: {
          rotate: deptNames.some(name => name.length > 4) ? 45 : 0
        }
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: {
          formatter: '{value}分'
        }
      },
      series: [{
        name: '平均分',
        data: deptScores,
        type: 'bar',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        }
      }]
    }
    chart.setOption(option)
    console.log('部门绩效对比数据:', deptStats)
  } catch (error) {
    console.error('加载部门绩效数据失败:', error)
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  const chart = echarts.init(trendChartRef.value)
  const option = {
    title: {
      text: '绩效完成趋势',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: {
      type: 'value',
      max: 100
    },
    series: [{
      data: [65, 72, 78, 85, 88, 92],
      type: 'line',
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
          { offset: 1, color: 'rgba(24, 144, 255, 0.1)' }
        ])
      }
    }]
  }
  chart.setOption(option)
}

const initMonthlyComparisonChart = () => {
  if (!monthlyComparisonRef.value) return
  
  const chart = echarts.init(monthlyComparisonRef.value)
  const option = {
    title: {
      text: '月度对比',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['本月', '上月', '去年同期']
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: [92, 88, 85],
      type: 'bar',
      itemStyle: {
        color: function(params: any) {
          const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']
          return colors[params.dataIndex]
        }
      }
    }]
  }
  chart.setOption(option)
}

// 导出功能
const exportOverview = () => {
  ElMessage.success('概览报表导出功能开发中...')
}

const exportPerformance = () => {
  ElMessage.success('绩效分析报表导出功能开发中...')
}

const exportTrend = () => {
  ElMessage.success('趋势分析报表导出功能开发中...')
}

const exportDetailed = () => {
  ElMessage.success('详细数据报表导出功能开发中...')
}

// 工具函数
const getScoreClass = (score: number) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'average'
  return 'poor'
}

const getGradeFromScore = (score: number) => {
  if (score >= 95) return 'A+'
  if (score >= 90) return 'A'
  if (score >= 85) return 'A-'
  if (score >= 80) return 'B+'
  if (score >= 75) return 'B'
  if (score >= 70) return 'B-'
  if (score >= 65) return 'C+'
  if (score >= 60) return 'C'
  return 'D'
}

const getGradeType = (grade: string) => {
  if (grade.includes('A')) return 'success'
  if (grade.includes('B')) return 'warning'
  return 'danger'
}

// 使用统一的时间格式化工具函数

onMounted(async () => {
  await loadCycles()
  await loadKpi()
})
</script>

<style scoped>
/* 现代化报表中心样式 */
.reports-container {
  padding: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 现代化头部样式 */
.modern-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 32px 24px;
  color: white;
  position: relative;
  overflow: hidden;
}

.modern-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  opacity: 0.3;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  position: relative;
  z-index: 1;
}

.header-info {
  flex: 1;
}

.title-section {
  margin-bottom: 24px;
}

.main-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 28px;
  color: #fbbf24;
}

.subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
  font-weight: 400;
}

.stats-overview {
  display: flex;
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #fbbf24;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
  font-weight: 500;
}

.header-controls {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-end;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}

.control-label {
  font-size: 14px;
  font-weight: 500;
  opacity: 0.9;
}

.cycle-selector {
  width: 200px;
}

.cycle-selector :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.cycle-selector :deep(.el-input__inner) {
  color: white;
}

.cycle-selector :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.7);
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 10px 16px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* 功能工具栏样式 */
.toolbar-section {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 16px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.toolbar-content {
  display: flex;
  align-items: center;
}

.toolbar-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  color: white;
  border-radius: 8px;
  padding: 10px 18px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  justify-content: center;
}

.toolbar-btn:hover {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.toolbar-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}


/* 现代化报表内容区域 */
.modern-report-content {
  background: #f8fafc;
  padding: 24px;
  min-height: calc(100vh - 200px);
}

.report-dashboard {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dashboard-title {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.dashboard-desc {
  color: #6b7280;
  margin: 0;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.export-btn {
  background: #3b82f6;
  border: none;
  color: white;
  border-radius: 8px;
  padding: 10px 16px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.export-btn:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* 现代化KPI网格 */
.modern-kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  padding: 24px;
}

.kpi-card.modern-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.kpi-card.modern-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
}

.kpi-card.modern-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.completion-icon {
  background: linear-gradient(135deg, #10b981, #059669);
}

.score-icon {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.tasks-icon {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.cycles-icon {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.card-info {
  flex: 1;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.card-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.card-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.card-badge.success {
  background: #dcfce7;
  color: #166534;
}

.card-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.card-badge.info {
  background: #dbeafe;
  color: #1e40af;
}

.card-badge.primary {
  background: #e0e7ff;
  color: #3730a3;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.metric-detail {
  display: flex;
  align-items: center;
}

.detail-text {
  font-size: 14px;
  color: #6b7280;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .modern-kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stats-overview {
    gap: 24px;
  }
}

@media (max-width: 768px) {
  .modern-header {
    padding: 24px 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 24px;
  }
  
  .header-controls {
    align-items: flex-start;
    width: 100%;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: flex-start;
  }
  
  .toolbar-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .template-selector {
    width: 100%;
  }
  
  .toolbar-actions {
    width: 100%;
    justify-content: flex-start;
    gap: 12px;
  }
  
  .toolbar-btn {
    min-width: 100px;
    padding: 8px 14px;
    font-size: 13px;
  }
  
  .modern-kpi-grid {
    grid-template-columns: 1fr;
    padding: 16px;
  }
  
  .modern-report-content {
    padding: 16px;
  }
  
  .stats-overview {
    flex-direction: column;
    gap: 16px;
  }
}

/* 现代化图表网格 */
.modern-charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  padding: 24px;
}

.chart-card.modern-chart {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.chart-card.modern-chart:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.chart-card.modern-chart.large {
  grid-column: span 2;
}

.chart-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.chart-header h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.chart-container {
  height: 300px;
  width: 100%;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px dashed #d1d5db;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

/* 现代化数据表格 */
.modern-data-table {
  padding: 24px;
}

.modern-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.search-group {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-right: 16px;
}

.search-input {
  width: 200px;
}

.search-btn {
  background: #f8f9fa;
  border: 1px solid #d1d5db;
  color: #6b7280;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.search-btn:hover {
  background: #e9ecef;
  border-color: #409eff;
  color: #409eff;
}

.modern-score-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.modern-score-badge.excellent {
  background: #dcfce7;
  color: #166534;
}

.modern-score-badge.good {
  background: #dbeafe;
  color: #1e40af;
}

.modern-score-badge.average {
  background: #fef3c7;
  color: #92400e;
}

.modern-score-badge.poor {
  background: #fee2e2;
  color: #991b1b;
}

.modern-completion-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.modern-bar-bg {
  width: 60px;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.modern-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  border-radius: 3px;
  transition: width 0.3s;
}

.modern-completion-text {
  font-size: 12px;
  color: #6b7280;
  min-width: 35px;
  font-weight: 500;
}

/* 响应式图表网格 */
@media (max-width: 1200px) {
  .modern-charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card.modern-chart.large {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .modern-charts-grid {
    padding: 16px;
    gap: 16px;
  }
  
  .chart-card.modern-chart {
    padding: 16px;
  }
  
  .chart-container {
    height: 250px;
  }
  
  .search-group {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .search-input {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .toolbar-left {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .toolbar-btn {
    width: 100%;
    min-width: auto;
    padding: 10px 16px;
    font-size: 14px;
  }
  
}
</style>