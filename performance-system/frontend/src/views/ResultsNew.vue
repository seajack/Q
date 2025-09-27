<template>
  <div class="reports-container">
    <!-- 报表中心头部 -->
    <div class="reports-header">
      <div class="header-left">
        <h2 class="reports-title">报表中心</h2>
        <p class="reports-subtitle">绩效考核数据分析与报表生成</p>
      </div>
      <div class="header-actions">
        <el-select v-model="selectedCycle" placeholder="选择考核周期" style="width:200px" @change="onCycleChange">
          <el-option v-for="cycle in cycles" :key="cycle.id" :label="cycle.name" :value="cycle.id" />
        </el-select>
        <el-button type="primary" @click="generateReport">生成报表</el-button>
        <el-button @click="refreshData">刷新</el-button>
      </div>
    </div>

    <!-- 报表类型选择 -->
    <div class="report-types">
      <div class="type-tabs">
        <div 
          v-for="type in reportTypes" 
          :key="type.id"
          :class="['type-tab', { active: selectedReportType === type.id }]"
          @click="selectReportType(type.id)"
        >
          <i :class="type.icon"></i>
          <span>{{ type.name }}</span>
        </div>
      </div>
    </div>

    <!-- 报表内容区域 -->
    <div class="report-content">
      <!-- 概览报表 -->
      <div v-if="selectedReportType === 'overview'" class="report-section">
        <div class="section-header">
          <h3>概览报表</h3>
          <div class="section-actions">
            <el-button size="small" @click="exportOverview">导出概览</el-button>
          </div>
        </div>
        
        <!-- KPI 指标卡片 -->
        <div class="kpi-grid">
          <div class="kpi-card completion">
            <div class="kpi-header">
              <span class="kpi-label">完成率</span>
              <span class="kpi-badge success">目标 100%</span>
            </div>
            <div class="kpi-content">
              <div class="kpi-value">{{ kpi.completion_rate || 0 }}%</div>
              <div class="kpi-icon">📊</div>
            </div>
            <div class="kpi-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{width: (kpi.completion_rate || 0) + '%'}"></div>
              </div>
            </div>
          </div>

          <div class="kpi-card score">
            <div class="kpi-header">
              <span class="kpi-label">平均评分</span>
              <span class="kpi-badge warning">{{ kpi.avg_score || '-' }}</span>
            </div>
            <div class="kpi-content">
              <div class="kpi-value">{{ kpi.avg_grade || '-' }}</div>
              <div class="kpi-icon">⭐</div>
            </div>
            <div class="kpi-detail">
              <span class="detail-text">分布见右侧图表</span>
            </div>
          </div>

          <div class="kpi-card tasks">
            <div class="kpi-header">
              <span class="kpi-label">已完成任务</span>
              <span class="kpi-badge info">实时</span>
            </div>
            <div class="kpi-content">
              <div class="kpi-value">{{ kpi.completed_tasks || 0 }}</div>
              <div class="kpi-icon">✅</div>
            </div>
            <div class="kpi-detail">
              <span class="detail-text">周期内已完成数量</span>
            </div>
          </div>

          <div class="kpi-card cycles">
            <div class="kpi-header">
              <span class="kpi-label">活跃周期</span>
              <span class="kpi-badge danger">总 {{ kpi.total_cycles || '-' }}</span>
            </div>
            <div class="kpi-content">
              <div class="kpi-value">{{ kpi.active_cycles || 0 }}</div>
              <div class="kpi-icon">🔄</div>
            </div>
            <div class="kpi-detail">
              <span class="detail-text">当前活跃周期</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 绩效分析报表 -->
      <div v-if="selectedReportType === 'performance'" class="report-section">
        <div class="section-header">
          <h3>绩效分析报表</h3>
          <div class="section-actions">
            <el-button size="small" @click="exportPerformance">导出绩效分析</el-button>
          </div>
        </div>
        
        <div class="charts-grid">
          <div class="chart-card">
            <div class="chart-header">
              <h4>评分分布分析</h4>
            </div>
            <div ref="scoreDistributionRef" class="chart-container"></div>
          </div>
          
          <div class="chart-card">
            <div class="chart-header">
              <h4>部门绩效对比</h4>
            </div>
            <div ref="deptPerformanceRef" class="chart-container"></div>
          </div>
        </div>
      </div>

      <!-- 趋势分析报表 -->
      <div v-if="selectedReportType === 'trend'" class="report-section">
        <div class="section-header">
          <h3>趋势分析报表</h3>
          <div class="section-actions">
            <el-button size="small" @click="exportTrend">导出趋势分析</el-button>
          </div>
        </div>
        
        <div class="charts-grid">
          <div class="chart-card large">
            <div class="chart-header">
              <h4>绩效完成趋势</h4>
            </div>
            <div ref="trendChartRef" class="chart-container"></div>
          </div>
          
          <div class="chart-card">
            <div class="chart-header">
              <h4>月度对比</h4>
            </div>
            <div ref="monthlyComparisonRef" class="chart-container"></div>
          </div>
        </div>
      </div>

      <!-- 详细数据报表 -->
      <div v-if="selectedReportType === 'detailed'" class="report-section">
        <div class="section-header">
          <h3>详细数据报表</h3>
          <div class="section-actions">
            <el-input v-model="searchKeyword" placeholder="搜索员工/部门" style="width:200px" clearable @keyup.enter="loadDetailedData" />
            <el-button size="small" @click="loadDetailedData">搜索</el-button>
            <el-button size="small" type="primary" @click="exportDetailed">导出详细数据</el-button>
          </div>
        </div>
        
        <div class="data-table">
          <el-table :data="detailedData" v-loading="loading" stripe>
            <el-table-column type="index" label="序号" width="80" />
            <el-table-column prop="employee_name" label="员工姓名" min-width="120" />
            <el-table-column prop="department" label="部门" width="120" />
            <el-table-column prop="position" label="职位" width="120" />
            <el-table-column prop="score" label="评分" width="100">
              <template #default="{ row }">
                <span class="score-badge" :class="getScoreClass(row.score)">{{ row.score }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="grade" label="等级" width="80">
              <template #default="{ row }">
                <el-tag :type="getGradeType(row.grade)" size="small">{{ row.grade }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="completion_rate" label="完成度" width="100">
              <template #default="{ row }">
                <div class="completion-bar">
                  <div class="bar-bg">
                    <div class="bar-fill" :style="{width: row.completion_rate + '%'}"></div>
                  </div>
                  <span class="completion-text">{{ row.completion_rate }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间" width="150">
              <template #default="{ row }">
                {{ formatDate(row.updated_at) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import { cycleApi, taskApi, statsApi } from '@/utils/api'
import { ElMessage } from 'element-plus'

// 基础数据
const cycles = ref<any[]>([])
const selectedCycle = ref<number | null>(null)
const loading = ref(false)
const kpi = ref<any>({})

// 报表类型
const selectedReportType = ref('overview')
const reportTypes = ref([
  { id: 'overview', name: '概览报表', icon: 'el-icon-data-analysis' },
  { id: 'performance', name: '绩效分析', icon: 'el-icon-pie-chart' },
  { id: 'trend', name: '趋势分析', icon: 'el-icon-trend-charts' },
  { id: 'detailed', name: '详细数据', icon: 'el-icon-document' }
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

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(async () => {
  await loadCycles()
  await loadKpi()
})
</script>

<style scoped>
.reports-container {
  padding: 24px;
  background: #f8fafc;
  min-height: 100vh;
}

.reports-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left {
  flex: 1;
}

.reports-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.reports-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.report-types {
  margin-bottom: 24px;
}

.type-tabs {
  display: flex;
  gap: 8px;
  background: white;
  padding: 8px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.type-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  font-weight: 500;
}

.type-tab:hover {
  background: #f3f4f6;
}

.type-tab.active {
  background: #3b82f6;
  color: white;
}

.report-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.report-section {
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.section-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.kpi-card {
  padding: 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
  transition: all 0.3s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.kpi-label {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
}

.kpi-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.kpi-badge.success {
  background: #dcfce7;
  color: #166534;
}

.kpi-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.kpi-badge.info {
  background: #dbeafe;
  color: #1e40af;
}

.kpi-badge.danger {
  background: #fee2e2;
  color: #991b1b;
}

.kpi-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
}

.kpi-icon {
  font-size: 24px;
}

.kpi-progress {
  margin-top: 12px;
}

.progress-bar {
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  border-radius: 3px;
  transition: width 0.3s;
}

.kpi-detail {
  margin-top: 8px;
}

.detail-text {
  font-size: 12px;
  color: #6b7280;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.chart-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
}

.chart-card.large {
  grid-column: span 2;
}

.chart-header {
  margin-bottom: 16px;
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
}

.data-table {
  margin-top: 20px;
}

.score-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.score-badge.excellent {
  background: #dcfce7;
  color: #166534;
}

.score-badge.good {
  background: #dbeafe;
  color: #1e40af;
}

.score-badge.average {
  background: #fef3c7;
  color: #92400e;
}

.score-badge.poor {
  background: #fee2e2;
  color: #991b1b;
}

.completion-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bar-bg {
  width: 60px;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  border-radius: 3px;
  transition: width 0.3s;
}

.completion-text {
  font-size: 12px;
  color: #6b7280;
  min-width: 35px;
}

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .reports-container {
    padding: 16px;
  }
  
  .reports-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .type-tabs {
    flex-wrap: wrap;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card.large {
    grid-column: span 1;
  }
}
</style>