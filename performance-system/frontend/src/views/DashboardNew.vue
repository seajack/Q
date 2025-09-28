<template>
  <div class="dashboard-container">
    <!-- 顶部操作条 -->
    <div class="dashboard-header">
      <div class="header-left">
        <h2 class="dashboard-title">考核看板</h2>
        <p class="dashboard-subtitle">绩效考核数据洞察与分析</p>
      </div>
      <div class="header-actions">
        <el-select v-model="selectedCycle" placeholder="选择考核周期" style="width:200px" @change="onCycleChange">
          <el-option v-for="cycle in cycles" :key="cycle.id" :label="cycle.name" :value="cycle.id" />
        </el-select>
        <el-input v-model="keyword" placeholder="搜索员工、部门…" style="width:240px" clearable @keyup.enter="onSearch" />
        <el-button type="primary" @click="onCreate">新增评审</el-button>
        <el-button @click="refreshData">刷新</el-button>
        </div>
      </div>

    <!-- 截止日期提醒 -->
    <DeadlineReminder />

    <!-- KPI 指标卡片 -->
    <section class="kpi-section">
      <div class="kpi-grid">
        <div class="kpi-card completion">
          <div class="kpi-header">
            <span class="kpi-label">完成率</span>
            <span class="kpi-trend positive">+{{ completionTrend }}%</span>
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
            <span class="kpi-badge">{{ kpi.avg_score || 0 }}</span>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ kpi.avg_grade || 'B' }}</div>
            <div class="kpi-icon">⭐</div>
        </div>
          <div class="kpi-detail">
            <span class="detail-text">评分分布见右侧图表</span>
          </div>
        </div>

        <div class="kpi-card pending">
          <div class="kpi-header">
            <span class="kpi-label">待评审</span>
            <span class="kpi-trend negative">-{{ pendingTrend }} 人</span>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ kpi.pending_tasks || 0 }} 人</div>
            <div class="kpi-icon">⏰</div>
          </div>
          <div class="kpi-detail">
            <span class="detail-text">需要关注的待处理任务</span>
          </div>
        </div>

        <div class="kpi-card anomaly">
          <div class="kpi-header">
            <span class="kpi-label">异常检测</span>
            <span class="kpi-badge warning">{{ kpi.anomaly_count || 0 }} 项</span>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ kpi.anomaly_rate || 0 }}%</div>
            <div class="kpi-icon">⚠️</div>
          </div>
          <div class="kpi-detail">
            <span class="detail-text">评分波动异常的员工</span>
          </div>
        </div>
        </div>
      </section>

    <!-- 图表分析区域 -->
    <section class="charts-section">
      <div class="charts-grid">
        <!-- 评分分布图 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>评分分布分析</h3>
            <div class="chart-actions">
              <el-button size="small" @click="exportChart('distribution')">导出图表</el-button>
            </div>
          </div>
          <div ref="distributionRef" class="chart-container"></div>
        </div>

        <!-- 部门绩效对比 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>部门绩效对比</h3>
            <span class="chart-subtitle">完成率 vs 平均分</span>
          </div>
          <div ref="deptPerformanceRef" class="chart-container"></div>
                    </div>
                  </div>

      <div class="charts-grid">
        <!-- 绩效趋势图 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>绩效完成趋势</h3>
            <div class="chart-actions">
              <el-select v-model="trendPeriod" size="small" style="width:120px" @change="updateTrendChart">
                <el-option label="最近7天" value="7" />
                <el-option label="最近30天" value="30" />
                <el-option label="最近90天" value="90" />
              </el-select>
            </div>
                  </div>
          <div ref="trendRef" class="chart-container"></div>
        </div>

        <!-- 员工能力雷达图 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>员工能力雷达图</h3>
            <div class="chart-actions">
              <el-select 
                v-model="selectedEmployee" 
                size="small" 
                style="width:160px" 
                @change="updateRadarChart"
              >
                <el-option 
                  v-for="emp in employees" 
                  :key="emp.id" 
                  :label="emp.name" 
                  :value="emp.id" 
                />
              </el-select>
            </div>
          </div>
          <div ref="radarRef" class="chart-container"></div>
        </div>

        <!-- 考核周期进度 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>考核周期进度</h3>
            <span class="chart-subtitle">各周期完成情况</span>
          </div>
          <div ref="cycleProgressRef" class="chart-container"></div>
        </div>
      </div>
    </section>

    <!-- 员工绩效排名 -->
    <section class="performance-section">
      <div class="section-header">
        <h3>员工绩效排名</h3>
        <div class="section-actions">
          <el-select v-model="rankingType" size="small" style="width:120px" @change="updateRanking">
            <el-option label="按评分" value="score" />
            <el-option label="按完成度" value="completion" />
            <el-option label="按部门" value="department" />
          </el-select>
          <el-button size="small" @click="exportRanking">导出排名</el-button>
        </div>
      </div>
      
      <div class="performance-table">
        <el-table :data="performanceRanking" v-loading="loading" stripe>
          <el-table-column type="index" label="排名" width="80" />
          <el-table-column prop="name" label="员工" min-width="150">
            <template #default="{ row }">
              <div class="employee-info">
                <div class="avatar">{{ row.name?.[0] || '?' }}</div>
                <div class="info">
                  <div class="name">{{ row.name }}</div>
                  <div class="position">{{ row.position }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="department" label="部门" width="120" />
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
          <el-table-column prop="trend" label="趋势" width="100">
            <template #default="{ row }">
              <span class="trend-indicator" :class="row.trend">
                <i :class="getTrendIcon(row.trend)"></i>
                {{ row.trend_text }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" @click="viewDetail(row)">详情</el-button>
                <el-button size="small" type="primary" @click="editPerformance(row)">编辑</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        </div>
      </section>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { statsApi, cycleApi, taskApi } from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import DeadlineReminder from '@/components/DeadlineReminder.vue'

// 品牌色
const brand600 = () => getComputedStyle(document.documentElement).getPropertyValue('--brand-600').trim() || '#177fc1'
const brand400 = () => getComputedStyle(document.documentElement).getPropertyValue('--brand-400').trim() || '#59b6ea'
const brand700 = () => getComputedStyle(document.documentElement).getPropertyValue('--brand-700').trim() || '#115f96'

// 响应式数据
const loading = ref(false)
const keyword = ref('')
const selectedCycle = ref<number | null>(null)
const cycles = ref<any[]>([])
const kpi = ref<any>({})
const performanceRanking = ref<any[]>([])
const rankingType = ref('score')
const trendPeriod = ref('7')

// 图表引用
const distributionRef = ref<HTMLDivElement | null>(null)
const deptPerformanceRef = ref<HTMLDivElement | null>(null)
const trendRef = ref<HTMLDivElement | null>(null)
const cycleProgressRef = ref<HTMLDivElement | null>(null)
const radarRef = ref<HTMLDivElement | null>(null)

let distributionChart: echarts.ECharts | null = null
let deptPerformanceChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let cycleProgressChart: echarts.ECharts | null = null
let radarChart: echarts.ECharts | null = null

// 新增状态
const router = useRouter()
const timeRange = ref('30')
const customDateRange = ref([])
const drilldownTarget = ref('')
const selectedEmployee = ref(null)
const employees = ref([])

// 计算属性
const completionTrend = computed(() => {
  // 模拟趋势数据，实际应该从API获取
  return Math.floor(Math.random() * 10) + 5
})

const pendingTrend = computed(() => {
  return Math.floor(Math.random() * 5) + 1
})

// 事件处理
const onCycleChange = () => {
  loadData()
}

const onSearch = () => {
  loadPerformanceRanking()
}

const onCreate = () => {
  // 跳转到创建考核周期页面
  window.location.href = '/cycles'
}

const refreshData = () => {
  loadData()
}

const updateTrendChart = () => {
  loadTrendChart()
}

const updateRanking = () => {
  loadPerformanceRanking()
}

const exportChart = (type: string) => {
  let chart: echarts.ECharts | null = null
  let filename = ''
  
  switch (type) {
    case 'distribution':
      chart = distributionChart
      filename = '评分分布图.png'
      break
    case 'deptPerformance':
      chart = deptPerformanceChart
      filename = '部门绩效对比图.png'
      break
    case 'trend':
      chart = trendChart
      filename = '绩效趋势图.png'
      break
    case 'cycleProgress':
      chart = cycleProgressChart
      filename = '考核周期进度图.png'
      break
  }
  
  if (chart) {
    const url = chart.getDataURL({ type: 'png', backgroundColor: '#fff' })
    const link = document.createElement('a')
    link.download = filename
    link.href = url
    link.click()
  }
}

const exportRanking = () => {
  // 导出排名数据
  const data = performanceRanking.value.map((item, index) => ({
    排名: index + 1,
    员工: item.name,
    部门: item.department,
    评分: item.score,
    等级: item.grade,
    完成度: item.completion_rate + '%',
    趋势: item.trend_text
  }))
  
  const csvContent = [
    Object.keys(data[0]).join(','),
    ...data.map(row => Object.values(row).join(','))
  ].join('\n')
  
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `员工绩效排名_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
  URL.revokeObjectURL(link.href)
}

const viewDetail = (row: any) => {
  // 查看员工详情
  console.log('查看详情:', row)
  
  // 显示员工详情对话框
  ElMessageBox.alert(
    `
    <div style="text-align: left;">
      <h3>员工绩效详情</h3>
      <p><strong>姓名：</strong>${row.name}</p>
      <p><strong>部门：</strong>${row.department}</p>
      <p><strong>职位：</strong>${row.position}</p>
      <p><strong>评分：</strong>${row.score}分</p>
      <p><strong>等级：</strong>${row.grade}</p>
      <p><strong>完成度：</strong>${row.completion_rate}%</p>
      <p><strong>趋势：</strong>${row.trend_text}</p>
    </div>
    `,
    '员工绩效详情',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '确定'
    }
  )
}

const editPerformance = (row: any) => {
  // 编辑绩效
  console.log('编辑绩效:', row)
  
  // 显示编辑对话框
  ElMessageBox.prompt(
    `请输入新的评分 (当前: ${row.score}分)`,
    '编辑绩效评分',
    {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputPattern: /^[0-9]+(\.[0-9]+)?$/,
      inputErrorMessage: '请输入有效的数字'
    }
  ).then(({ value }) => {
    const newScore = parseFloat(value)
    if (newScore >= 0 && newScore <= 100) {
      // 这里应该调用API更新评分
      ElMessage.success(`已更新 ${row.name} 的评分为 ${newScore} 分`)
      
      // 重新加载数据
      loadPerformanceRanking()
    } else {
      ElMessage.error('评分必须在0-100之间')
    }
  }).catch(() => {
    // 用户取消
  })
}

// 工具函数
const getScoreClass = (score: number) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'average'
  return 'poor'
}

const getGradeType = (grade: string) => {
  if (grade.includes('A')) return 'success'
  if (grade.includes('B')) return 'warning'
  return 'danger'
}

const getTrendIcon = (trend: string) => {
  switch (trend) {
    case 'up': return 'el-icon-arrow-up'
    case 'down': return 'el-icon-arrow-down'
    case 'stable': return 'el-icon-minus'
    default: return 'el-icon-minus'
  }
}

// 数据加载函数
const loadData = async () => {
  try {
    loading.value = true
    await Promise.all([
      loadCycles(),
      loadKpi(),
      loadPerformanceRanking(),
      loadEmployees()
    ])
    await loadAllCharts()
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const loadEmployees = async () => {
  try {
    const res = await statsApi.listEmployees()
    employees.value = res.data.results || []
    if (employees.value.length > 0) {
      selectedEmployee.value = employees.value[0].id
    }
  } catch (error) {
    console.error('加载员工列表失败:', error)
  }
}

const loadCycles = async () => {
  try {
    const res = await cycleApi.list()
    cycles.value = res.data.results || []
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
    console.log('KPI数据:', kpi.value)
  } catch (error) {
    console.error('加载KPI失败:', error)
    kpi.value = {
      completion_rate: 0,
      avg_score: 0,
      avg_grade: 'B',
      pending_tasks: 0,
      anomaly_count: 0,
      anomaly_rate: 0
    }
  }
}

const loadPerformanceRanking = async () => {
  try {
    const params: any = {
      status: 'completed',
      ordering: rankingType.value === 'score' ? '-avg_score' : 
                rankingType.value === 'completion' ? '-completion_rate' : 'department'
    }
    
    if (selectedCycle.value) {
      params.cycle = selectedCycle.value
    }
    
    if (keyword.value) {
      params.search = keyword.value
    }
    
    const res = await taskApi.list(params)
    const tasks = res.data.results || []
    
    performanceRanking.value = tasks.map((task: any, index: number) => {
      // 计算完成度：基于任务状态和评分情况
      let completion_rate = 0
      if (task.status === 'completed') {
        completion_rate = 100
      } else if (task.status === 'in_progress') {
        completion_rate = 50 // 进行中假设50%
      } else {
        completion_rate = 0
      }
      
      // 计算趋势：基于评分和历史数据
      let trend = 'stable'
      let trend_text = '稳定'
      if (task.avg_score > 85) {
        trend = 'up'
        trend_text = '上升'
      } else if (task.avg_score < 70) {
        trend = 'down'
        trend_text = '下降'
      }
      
      return {
        id: task.id,
        name: task.evaluatee_name || '员工',
        position: task.evaluatee_position || '',
        department: task.evaluatee_department || '未分配',
        score: task.avg_score || 0,
        grade: getGradeFromScore(task.avg_score || 0),
        completion_rate: completion_rate,
        trend: trend,
        trend_text: trend_text
      }
    })
    
    console.log('绩效排名数据:', performanceRanking.value)
  } catch (error) {
    console.error('加载绩效排名失败:', error)
    performanceRanking.value = []
  }
}

const getGradeFromScore = (score: number) => {
  if (score >= 90) return 'A+'
  if (score >= 85) return 'A'
  if (score >= 80) return 'A-'
  if (score >= 75) return 'B+'
  if (score >= 70) return 'B'
  if (score >= 65) return 'B-'
  return 'C'
}

// 图表渲染函数
const loadAllCharts = async () => {
  await Promise.all([
    loadDistributionChart(),
    loadDeptPerformanceChart(),
    loadTrendChart(),
    loadCycleProgressChart()
  ])
}

const loadDistributionChart = async () => {
  if (!distributionChart) return
  
  try {
    const distribution = kpi.value.score_distribution || {}
    const grades = ['C', 'B-', 'B', 'B+', 'A-', 'A', 'A+']
    const counts = grades.map(grade => distribution[grade] || 0)
    
    distributionChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: grades,
        axisLabel: {
          color: '#666'
        }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          color: '#666'
        }
      },
      series: [{
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: brand400() },
            { offset: 1, color: brand600() }
          ])
        },
        barWidth: '60%',
        label: {
          show: true,
          position: 'top',
          color: '#333'
        }
      }]
    })
  } catch (error) {
    console.error('渲染评分分布图失败:', error)
  }
}

const loadDeptPerformanceChart = async () => {
  if (!deptPerformanceChart) return
  
  try {
    const deptData = kpi.value.dept_performance || []
    const departments = deptData.map((dept: any) => dept.department)
    const completionRates = deptData.map((dept: any) => dept.completion_rate)
    const avgScores = deptData.map((dept: any) => dept.avg_score)
    
    deptPerformanceChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
      },
      legend: {
        data: ['完成率', '平均分']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: departments,
        axisLabel: {
          color: '#666',
          rotate: 45
        }
      },
      yAxis: [
        {
          type: 'value',
          name: '完成率(%)',
          position: 'left',
          axisLabel: {
            color: '#666'
          }
        },
        {
          type: 'value',
          name: '平均分',
          position: 'right',
          axisLabel: {
            color: '#666'
          }
        }
      ],
      series: [
        {
          name: '完成率',
          type: 'bar',
          data: completionRates,
          itemStyle: {
            color: brand600()
          }
        },
        {
          name: '平均分',
          type: 'line',
          yAxisIndex: 1,
          data: avgScores,
          itemStyle: {
            color: '#ff6b6b'
          },
          lineStyle: {
            width: 3
          }
        }
      ]
    })
  } catch (error) {
    console.error('渲染部门绩效图失败:', error)
  }
}

const loadTrendChart = async () => {
  if (!trendChart) return
  
  try {
    const trendData = kpi.value.performance_trend || []
    const dates = trendData.map((item: any) => item.date.split('-').slice(1).join('/'))
    const completed = trendData.map((item: any) => item.completed)
    
    trendChart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          color: '#666'
        }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          color: '#666'
        }
      },
      series: [{
        type: 'line',
        data: completed,
        smooth: true,
        itemStyle: {
          color: brand600()
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: brand400() + '80' },
            { offset: 1, color: brand400() + '20' }
          ])
        },
        lineStyle: {
          width: 3
        }
      }]
    })
  } catch (error) {
    console.error('渲染趋势图失败:', error)
  }
}

const loadCycleProgressChart = async () => {
  if (!cycleProgressChart) return
  
  try {
    const cycleData = kpi.value.cycle_progress || []
    const cycles = cycleData.map((cycle: any) => cycle.name)
    const progress = cycleData.map((cycle: any) => cycle.progress)
    
    cycleProgressChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: cycles,
        axisLabel: {
          color: '#666',
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: {
          color: '#666',
          formatter: '{value}%'
        }
      },
      series: [{
        type: 'bar',
        data: progress,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#4facfe' },
            { offset: 1, color: '#00f2fe' }
          ])
        },
        barWidth: '60%',
        label: {
          show: true,
          position: 'top',
          formatter: '{c}%',
          color: '#333'
        }
      }]
    })
  } catch (error) {
    console.error('渲染周期进度图失败:', error)
  }
}

const updateRadarChart = async () => {
  if (!radarChart || !selectedEmployee.value) return

  try {
    // 获取员工能力数据
    const res = await statsApi.getEmployeeSkills(selectedEmployee.value)
    const skills = res.data.skills || []
    
    const indicator = skills.map(skill => ({
      name: skill.name,
      max: 100
    }))
    
    const data = [{
      value: skills.map(skill => skill.score),
      name: '能力评估'
    }]
    
    radarChart.setOption({
      tooltip: {
        trigger: 'item'
      },
      radar: {
        indicator: indicator,
        splitArea: {
          areaStyle: {
            color: ['rgba(5, 150, 105, 0.1)']
          }
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(5, 150, 105, 0.5)'
          }
        }
      },
      series: [{
        type: 'radar',
        data: data,
        areaStyle: {
          color: 'rgba(5, 150, 105, 0.3)'
        },
        lineStyle: {
          width: 2,
          color: brand600()
        },
        symbolSize: 6,
        label: {
          show: true,
          formatter: '{c}'
        }
      }]
    })
  } catch (error) {
    console.error('渲染雷达图失败:', error)
  }
}

// 初始化图表
const initCharts = () => {
  if (distributionRef.value) {
    distributionChart = echarts.init(distributionRef.value)
  }
  if (deptPerformanceRef.value) {
    deptPerformanceChart = echarts.init(deptPerformanceRef.value)
  }
  if (trendRef.value) {
    trendChart = echarts.init(trendRef.value)
  }
  if (cycleProgressRef.value) {
    cycleProgressChart = echarts.init(cycleProgressRef.value)
  }
  if (radarRef.value) {
    radarChart = echarts.init(radarRef.value)
  }
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    distributionChart?.resize()
    deptPerformanceChart?.resize()
    trendChart?.resize()
    cycleProgressChart?.resize()
    radarChart?.resize()
  })
}

onMounted(async () => {
  initCharts()
  await loadData()
})



// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待评价',
    'completed': '已完成',
    'in_progress': '进行中'
  }
  return statusMap[status] || '未知'
}


</script>

<style scoped>
.dashboard-container {
  padding: 16px;
  background: #f8fafc;
  min-height: 100vh;
}

/* 头部样式 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.header-left {
  flex: 1;
}

.dashboard-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 4px 0;
}

.dashboard-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* KPI 卡片样式 */
.kpi-section {
  margin-bottom: 24px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.kpi-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.kpi-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}

.kpi-trend {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.kpi-trend.positive {
  background: #dcfce7;
  color: #166534;
}

.kpi-trend.negative {
  background: #fef2f2;
  color: #dc2626;
}

.kpi-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  background: #f1f5f9;
  color: #475569;
}

.kpi-badge.warning {
  background: #fef3c7;
  color: #d97706;
}

.kpi-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: #1a202c;
}

.kpi-icon {
  font-size: 18px;
}

.kpi-progress {
  margin-top: 12px;
}

.progress-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.kpi-detail {
  margin-top: 8px;
}

.detail-text {
  font-size: 12px;
  color: #64748b;
}

/* 图表区域样式 */
.charts-section {
  margin-bottom: 24px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}


.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.chart-subtitle {
  font-size: 11px;
  color: #64748b;
}

.chart-actions {
  display: flex;
  gap: 6px;
}

.chart-container {
  height: 240px;
  width: 100%;
}

/* 绩效排名区域 */
.performance-section {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.section-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.performance-table {
  margin-top: 16px;
}

.employee-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
}

.info .name {
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 2px;
}

.info .position {
  font-size: 12px;
  color: #64748b;
}

.score-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 12px;
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
  color: #d97706;
}

.score-badge.poor {
  background: #fef2f2;
  color: #dc2626;
}

.completion-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bar-bg {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.completion-text {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  min-width: 35px;
}

.trend-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
}

.trend-indicator.up {
  color: #059669;
}

.trend-indicator.down {
  color: #dc2626;
}

.trend-indicator.stable {
  color: #64748b;
}

.action-buttons {
  display: flex;
  gap: 6px;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 12px;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-end;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .section-actions {
    justify-content: flex-end;
  }
  
  .chart-container {
    height: 200px;
  }
}
</style>
