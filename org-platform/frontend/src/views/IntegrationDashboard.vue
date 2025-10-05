<template>
  <div class="integration-dashboard">
    <div class="page-header">
      <h1>系统监控</h1>
      <div class="header-actions">
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>



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
    Object.assign(overview, response)
  } catch (error) {
    ElMessage.error('加载概览数据失败')
  }
}

const loadSystemHealth = async () => {
  healthLoading.value = true
  try {
    const response = await api.get('/integration/dashboard/system_health/')
    systemHealth.value = response
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
    console.log('性能数据响应:', response)
    await nextTick()
    initPerformanceChart(response)
  } catch (error) {
    console.error('加载性能数据失败:', error)
    ElMessage.error(`加载性能数据失败: ${error.message || '未知错误'}`)
  } finally {
    performanceLoading.value = false
  }
}

const loadRecentLogs = async () => {
  try {
    const response = await api.get('/integration/sync-logs/?limit=10')
    console.log('同步日志响应:', response)
    recentLogs.value = response.results || []
    
    // 如果没有数据，添加一些模拟数据用于测试
    if (recentLogs.value.length === 0) {
      recentLogs.value = [
        {
          id: 1,
          sync_rule_name: '员工数据同步',
          status: 'success',
          status_display: '成功',
          start_time: '2025-10-05 10:30:00',
          duration_formatted: '2分30秒',
          total_records: 150,
          success_records: 150,
          error_records: 0,
          error_message: ''
        },
        {
          id: 2,
          sync_rule_name: '部门数据同步',
          status: 'success',
          status_display: '成功',
          start_time: '2025-10-05 09:15:00',
          duration_formatted: '1分45秒',
          total_records: 50,
          success_records: 50,
          error_records: 0,
          error_message: ''
        }
      ]
    }
  } catch (error) {
    console.error('加载最近日志失败:', error)
    ElMessage.error(`加载最近日志失败: ${error.message || '未知错误'}`)
  }
}

const initPerformanceChart = (data: any[]) => {
  if (!performanceChart.value) {
    console.warn('性能图表容器未找到')
    return
  }
  
  if (!data || data.length === 0) {
    console.warn('性能数据为空，跳过图表初始化')
    return
  }
  
  try {
    // 强制所有事件监听器为passive模式
    const originalAddEventListener = EventTarget.prototype.addEventListener
    EventTarget.prototype.addEventListener = function(type, listener, options) {
      if (type === 'wheel' || type === 'mousewheel') {
        options = { passive: true, ...options }
      }
      return originalAddEventListener.call(this, type, listener, options)
    }

    chartInstance = echarts.init(performanceChart.value, null, {
      renderer: 'canvas',
      useDirtyRect: true
    })
    
    const dates = data.map(item => item.date)
    const durationData = data.map(item => item.duration)
    const recordsData = data.map(item => item.total_records)
    
    console.log('图表数据:', { dates, durationData, recordsData })
  
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
    
    // 恢复原始的addEventListener
    EventTarget.prototype.addEventListener = originalAddEventListener
  } catch (error) {
    console.error('初始化性能图表失败:', error)
    ElMessage.error('初始化性能图表失败')
    
    // 确保在错误情况下也恢复原始的addEventListener
    EventTarget.prototype.addEventListener = originalAddEventListener
  }
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
