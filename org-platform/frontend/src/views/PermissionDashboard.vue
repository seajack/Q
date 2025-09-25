<template>
  <div class="permission-dashboard">
    <div class="page-header">
      <h1>权限仪表板</h1>
      <el-button @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon permissions">
              <el-icon><Key /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overview.permissions?.total || 0 }}</div>
              <div class="stat-label">总权限数</div>
              <div class="stat-detail">
                <span class="active">{{ overview.permissions?.active || 0 }} 启用</span>
                <span class="inactive">{{ overview.permissions?.inactive || 0 }} 禁用</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon roles">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overview.roles?.total || 0 }}</div>
              <div class="stat-label">总角色数</div>
              <div class="stat-detail">
                <span class="active">{{ overview.roles?.active || 0 }} 启用</span>
                <span class="inactive">{{ overview.roles?.inactive || 0 }} 禁用</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon users">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overview.users?.total || 0 }}</div>
              <div class="stat-label">总用户数</div>
              <div class="stat-detail">
                <span class="with-roles">{{ overview.users?.with_roles || 0 }} 有角色</span>
                <span class="without-roles">{{ overview.users?.without_roles || 0 }} 无角色</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon logs">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overview.logs || 0 }}</div>
              <div class="stat-label">操作日志</div>
              <div class="stat-detail">
                <span class="recent">最近24小时</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-section">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>权限类型分布</span>
            </div>
          </template>
          <div ref="permissionTypeChart" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>角色类型分布</span>
            </div>
          </template>
          <div ref="roleTypeChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近权限操作 -->
    <el-card class="recent-logs">
      <template #header>
        <div class="card-header">
          <span>最近权限操作</span>
          <el-button size="small" @click="loadRecentLogs">刷新</el-button>
        </div>
      </template>
      
      <el-table :data="recentLogs" stripe>
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="action_type_display" label="操作类型" width="120" />
        <el-table-column prop="resource_type" label="资源类型" width="120" />
        <el-table-column prop="resource_id" label="资源ID" width="100" />
        <el-table-column prop="result_display" label="结果" width="100">
          <template #default="{ row }">
            <el-tag :type="getResultType(row.result)" size="small">
              {{ row.result_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="120" />
        <el-table-column prop="created_at" label="操作时间" width="150" />
      </el-table>
    </el-card>

    <!-- 权限检查工具 -->
    <el-card class="permission-checker">
      <template #header>
        <div class="card-header">
          <span>权限检查工具</span>
        </div>
      </template>
      
      <div class="checker-form">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-select v-model="checkUser" placeholder="选择用户" filterable>
              <el-option
                v-for="user in users"
                :key="user.id"
                :label="user.username"
                :value="user.id"
              />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-input v-model="checkPermission" placeholder="输入权限编码" />
          </el-col>
          <el-col :span="8">
            <el-button type="primary" @click="checkUserPermission" :loading="checking">
              检查权限
            </el-button>
          </el-col>
        </el-row>
        
        <div v-if="checkResult" class="check-result">
          <el-alert
            :title="checkResult.has_permission ? '用户拥有该权限' : '用户没有该权限'"
            :type="checkResult.has_permission ? 'success' : 'warning'"
            :description="`用户ID: ${checkResult.user_id}, 权限编码: ${checkResult.permission_code}`"
            show-icon
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Key, UserFilled, User, Document } from '@element-plus/icons-vue'
import api from '@/utils/api'
import * as echarts from 'echarts'

// 响应式数据
const overview = reactive({
  permissions: { total: 0, active: 0, inactive: 0 },
  roles: { total: 0, active: 0, inactive: 0 },
  users: { total: 0, with_roles: 0, without_roles: 0 },
  logs: 0
})

const recentLogs = ref([])
const users = ref([])
const checkUser = ref('')
const checkPermission = ref('')
const checkResult = ref(null)
const checking = ref(false)

// 图表实例
const permissionTypeChart = ref()
const roleTypeChart = ref()
let permissionTypeChartInstance: echarts.ECharts | null = null
let roleTypeChartInstance: echarts.ECharts | null = null

// 方法
const loadOverview = async () => {
  try {
    const response = await api.get('/permission/dashboard/overview/')
    Object.assign(overview, response.data)
  } catch (error) {
    ElMessage.error('加载概览数据失败')
  }
}

const loadRecentLogs = async () => {
  try {
    const response = await api.get('/permission/permission-logs/', {
      params: { page_size: 10 }
    })
    recentLogs.value = response.data.results
  } catch (error) {
    ElMessage.error('加载操作日志失败')
  }
}

const loadUsers = async () => {
  try {
    const response = await api.get('/api/users/')
    users.value = response.data.results
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

const refreshData = () => {
  loadOverview()
  loadRecentLogs()
  ElMessage.success('数据已刷新')
}

const initCharts = async () => {
  await nextTick()
  
  // 权限类型分布图表
  if (permissionTypeChart.value) {
    permissionTypeChartInstance = echarts.init(permissionTypeChart.value)
    const permissionTypeData = overview.permission_types || []
    const option = {
      title: {
        text: '权限类型分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '权限类型',
          type: 'pie',
          radius: '50%',
          data: permissionTypeData.map(item => ({
            value: item.count,
            name: item.permission_type
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    permissionTypeChartInstance.setOption(option)
  }

  // 角色类型分布图表
  if (roleTypeChart.value) {
    roleTypeChartInstance = echarts.init(roleTypeChart.value)
    const roleTypeData = overview.role_types || []
    const option = {
      title: {
        text: '角色类型分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '角色类型',
          type: 'pie',
          radius: '50%',
          data: roleTypeData.map(item => ({
            value: item.count,
            name: item.role_type
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    roleTypeChartInstance.setOption(option)
  }
}

const checkUserPermission = async () => {
  if (!checkUser.value || !checkPermission.value) {
    ElMessage.warning('请选择用户并输入权限编码')
    return
  }

  checking.value = true
  try {
    const response = await api.get('/permission/dashboard/check_permission/', {
      params: {
        user_id: checkUser.value,
        permission_code: checkPermission.value
      }
    })
    checkResult.value = response.data
  } catch (error) {
    ElMessage.error('权限检查失败')
  } finally {
    checking.value = false
  }
}

const getResultType = (result: string) => {
  const typeMap: Record<string, string> = {
    success: 'success',
    failed: 'danger',
    denied: 'warning'
  }
  return typeMap[result] || 'info'
}

// 生命周期
onMounted(async () => {
  await loadOverview()
  await loadRecentLogs()
  await loadUsers()
  await initCharts()
})

onUnmounted(() => {
  if (permissionTypeChartInstance) {
    permissionTypeChartInstance.dispose()
  }
  if (roleTypeChartInstance) {
    roleTypeChartInstance.dispose()
  }
})
</script>

<style scoped>
.permission-dashboard {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.stats-cards {
  margin-bottom: 30px;
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

.stat-icon.permissions {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.roles {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.users {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.logs {
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
  margin-bottom: 8px;
}

.stat-detail {
  font-size: 12px;
  color: #909399;
}

.stat-detail .active {
  color: #67c23a;
  margin-right: 10px;
}

.stat-detail .inactive {
  color: #f56c6c;
  margin-right: 10px;
}

.stat-detail .with-roles {
  color: #409eff;
  margin-right: 10px;
}

.stat-detail .without-roles {
  color: #e6a23c;
  margin-right: 10px;
}

.stat-detail .recent {
  color: #909399;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-card {
  height: 400px;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.recent-logs {
  margin-bottom: 30px;
}

.permission-checker {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checker-form {
  padding: 20px 0;
}

.check-result {
  margin-top: 20px;
}
</style>
