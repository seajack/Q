<template>
  <div class="permission-dashboard">
    <div class="dashboard-header">
      <h2>权限仪表板</h2>
      <p>查看权限统计和操作日志</p>
    </div>

    <!-- 权限统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Key /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalPermissions }}</div>
          <div class="stat-label">总权限数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><UserFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.activeRoles }}</div>
          <div class="stat-label">活跃角色</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalUsers }}</div>
          <div class="stat-label">用户总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.todayLogs }}</div>
          <div class="stat-label">今日日志</div>
        </div>
      </div>
    </div>

    <!-- 权限操作日志 -->
    <div class="logs-section">
      <h3>最近权限操作</h3>
      <el-table :data="recentLogs" stripe>
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="action_type" label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action_type)">
              {{ getActionText(row.action_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_type" label="资源类型" width="120" />
        <el-table-column prop="resource_id" label="资源ID" width="100" />
        <el-table-column prop="result" label="结果" width="100">
          <template #default="{ row }">
            <el-tag :type="getResultType(row.result)">
              {{ row.result_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Key, UserFilled, User, Document } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { permissionApi } from '@/utils/api'

const stats = reactive({
  totalPermissions: 0,
  activeRoles: 0,
  totalUsers: 0,
  todayLogs: 0
})

const recentLogs = ref([])

const loadStats = async () => {
  try {
    // 加载权限统计
    try {
      const permissionsResponse = await permissionApi.permissions.list()
      stats.totalPermissions = Array.isArray(permissionsResponse) ? permissionsResponse.length : 0
    } catch (error) {
      console.warn('权限API暂未实现')
      stats.totalPermissions = 0
    }

    // 加载角色统计
    try {
      const rolesResponse = await permissionApi.roles.list()
      stats.activeRoles = Array.isArray(rolesResponse) ? rolesResponse.length : 0
    } catch (error) {
      console.warn('角色API暂未实现')
      stats.activeRoles = 0
    }

    // 加载用户统计
    try {
      const usersResponse = await permissionApi.users.list()
      stats.totalUsers = Array.isArray(usersResponse) ? usersResponse.length : 0
    } catch (error) {
      console.warn('用户API暂未实现')
      stats.totalUsers = 0
    }

    // 加载日志统计
    try {
      const logsResponse = await permissionApi.logs.list()
      if (Array.isArray(logsResponse)) {
        stats.todayLogs = logsResponse.length
        recentLogs.value = logsResponse.slice(0, 10)
      } else {
        stats.todayLogs = 0
        recentLogs.value = []
      }
    } catch (error) {
      console.warn('权限日志API暂未实现')
      stats.todayLogs = 0
      recentLogs.value = []
    }
  } catch (error) {
    console.error('加载权限统计失败:', error)
  }
}

const getActionType = (actionType: string) => {
  const typeMap: Record<string, string> = {
    grant: 'success',
    revoke: 'danger',
    inherit: 'primary',
    expire: 'warning'
  }
  return typeMap[actionType] || 'info'
}

const getActionText = (actionType: string) => {
  const textMap: Record<string, string> = {
    grant: '授权',
    revoke: '撤销',
    inherit: '继承',
    expire: '过期'
  }
  return textMap[actionType] || actionType
}

const getResultType = (result: string) => {
  const typeMap: Record<string, string> = {
    success: 'success',
    failed: 'danger',
    denied: 'warning'
  }
  return typeMap[result] || 'info'
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.permission-dashboard {
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.dashboard-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #606266;
}

.logs-section h3 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}
</style>