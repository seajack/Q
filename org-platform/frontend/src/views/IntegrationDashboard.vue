<template>
  <div class="integration-dashboard">
    <div class="page-header">
      <h1>集成管理</h1>
      <div class="header-actions">
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 子页面导航 -->
    <div class="sub-nav">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="仪表板" name="dashboard" />
        <el-tab-pane label="集成系统" name="systems" />
        <el-tab-pane label="API网关" name="gateways" />
        <el-tab-pane label="数据同步" name="sync-rules" />
      </el-tabs>
    </div>

    <!-- 概览统计 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon systems">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overview.systems?.total || 0 }}</div>
              <div class="stat-label">集成系统</div>
              <div class="stat-detail">
                活跃: {{ overview.systems?.active || 0 }} | 
                禁用: {{ overview.systems?.inactive || 0 }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon sync">
              <el-icon><Refresh /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overview.sync_rules?.total || 0 }}</div>
              <div class="stat-label">同步规则</div>
              <div class="stat-detail">
                活跃: {{ overview.sync_rules?.active || 0 }} | 
                禁用: {{ overview.sync_rules?.inactive || 0 }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon requests">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overview.api_requests?.total || 0 }}</div>
              <div class="stat-label">API请求</div>
              <div class="stat-detail">
                成功率: {{ overview.api_requests?.success_rate?.toFixed(1) || 0 }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon sync-status">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overview.recent_syncs?.total || 0 }}</div>
              <div class="stat-label">最近同步</div>
              <div class="stat-detail">
                成功率: {{ overview.recent_syncs?.success_rate?.toFixed(1) || 0 }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统健康状态 -->
    <el-card class="health-card" v-loading="healthLoading">
      <template #header>
        <div class="card-header">
          <span>系统健康状态</span>
          <el-button size="small" @click="refreshHealth">刷新</el-button>
        </div>
      </template>
      
      <el-table :data="systemHealth" stripe>
        <el-table-column prop="system_name" label="系统名称" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getHealthStatusType(row.status)">
              {{ getHealthStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="response_time" label="响应时间(ms)" width="120">
          <template #default="{ row }">
            {{ row.response_time ? row.response_time.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="last_check" label="最后检查" width="150">
          <template #default="{ row }">
            {{ formatDate(row.last_check) }}
          </template>
        </el-table-column>
        <el-table-column prop="details" label="详情" min-width="200" show-overflow-tooltip />
      </el-table>
    </el-card>

    <!-- 同步性能图表 -->
    <el-card class="performance-card" v-loading="performanceLoading">
      <template #header>
        <div class="card-header">
          <span>同步性能趋势</span>
          <el-button size="small" @click="refreshPerformance">刷新</el-button>
        </div>
      </template>
      
      <div class="chart-container">
        <div ref="performanceChart" style="height: 300px;"></div>
      </div>
    </el-card>

    <!-- 最近同步日志 -->
    <el-card class="logs-card">
      <template #header>
        <div class="card-header">
          <span>最近同步日志</span>
          <el-button size="small" @click="viewAllLogs">查看全部</el-button>
        </div>
      </template>
      
      <el-table :data="recentLogs" stripe>
        <el-table-column prop="sync_rule_name" label="同步规则" min-width="150" />
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="150" />
        <el-table-column prop="duration_formatted" label="耗时" width="100" />
        <el-table-column prop="total_records" label="总记录数" width="100" />
        <el-table-column prop="success_records" label="成功记录数" width="100" />
        <el-table-column prop="error_records" label="错误记录数" width="100" />
        <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Monitor, Connection, DataAnalysis } from '@element-plus/icons-vue'
import api from '@/utils/api'
import * as echarts from 'echarts'

// 响应式数据
const activeTab = ref('dashboard')
const overview = reactive({
  systems: {},
  sync_rules: {},
  recent_syncs: {},
  api_requests: {}
})

const systemHealth = ref([])
const healthLoading = ref(false)
const performanceLoading = ref(false)
const recentLogs = ref([])

// 图表实例
const performanceChart = ref()
let chartInstance: echarts.ECharts | null = null

// 方法
const loadOverview = async () => {
  try {
    const response = await api.get('/integration/dashboard/overview/')
    Object.assign(overview, response.data)
  } catch (error) {
    ElMessage.error('加载概览数据失败')
  }
}

const loadSystemHealth = async () => {
  healthLoading.value = true
  try {
    const response = await api.get('/integration/dashboard/system_health/')
    systemHealth.value = response.data
  } catch (error) {
    ElMessage.error('加载系统健康状态失败')
  } finally {
    healthLoading.value = false
  }
}

const loadPerformanceData = async () => {
  performanceLoading.value = true
  try {
    const response = await api.get('/integration/dashboard/sync_performance/')
    await nextTick()
    initPerformanceChart(response.data)
  } catch (error) {
    ElMessage.error('加载性能数据失败')
  } finally {
    performanceLoading.value = false
  }
}

const loadRecentLogs = async () => {
  try {
    const response = await api.get('/integration/sync-logs/?limit=10')
    recentLogs.value = response.data.results
  } catch (error) {
    ElMessage.error('加载最近日志失败')
  }
}

const initPerformanceChart = (data: any[]) => {
  if (!performanceChart.value) return
  
  chartInstance = echarts.init(performanceChart.value)
  
  const dates = data.map(item => item.date)
  const durationData = data.map(item => item.duration)
  const recordsData = data.map(item => item.total_records)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['同步耗时(秒)', '同步记录数']
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: [
      {
        type: 'value',
        name: '耗时(秒)',
        position: 'left'
      },
      {
        type: 'value',
        name: '记录数',
        position: 'right'
      }
    ],
    series: [
      {
        name: '同步耗时(秒)',
        type: 'line',
        yAxisIndex: 0,
        data: durationData,
        smooth: true,
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '同步记录数',
        type: 'bar',
        yAxisIndex: 1,
        data: recordsData,
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }
  
  chartInstance.setOption(option)
}

const refreshData = () => {
  loadOverview()
  loadSystemHealth()
  loadPerformanceData()
  loadRecentLogs()
}

const refreshHealth = () => {
  loadSystemHealth()
}

const refreshPerformance = () => {
  loadPerformanceData()
}

const viewAllLogs = () => {
  // 跳转到日志页面
  window.open('/integration/sync-logs/', '_blank')
}

const getHealthStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    healthy: 'success',
    unhealthy: 'danger',
    error: 'danger'
  }
  return statusMap[status] || 'info'
}

const getHealthStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    healthy: '健康',
    unhealthy: '不健康',
    error: '错误'
  }
  return statusMap[status] || '未知'
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    success: 'success',
    error: 'danger',
    warning: 'warning',
    running: 'info'
  }
  return statusMap[status] || 'info'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString()
}

const handleTabChange = (tabName: string) => {
  const routes: Record<string, string> = {
    dashboard: '/integration-dashboard',
    systems: '/integration-systems',
    gateways: '/api-gateways',
    'sync-rules': '/data-sync-rules'
  }
  
  if (routes[tabName]) {
    window.location.href = routes[tabName]
  }
}

// 生命周期
onMounted(() => {
  refreshData()
})

// 组件卸载时销毁图表
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped>
.integration-dashboard {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.sub-nav {
  margin-bottom: 20px;
}

.overview-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.stat-icon.systems {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.sync {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.requests {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.sync-status {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.stat-detail {
  font-size: 12px;
  color: #909399;
}

.health-card,
.performance-card,
.logs-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
}
</style>
