<template>
  <div class="permission-management">
    <div class="page-header">
      <h1>权限管理</h1>
      <p class="page-description">管理系统权限、角色分配和数据权限控制</p>
    </div>

    <!-- 功能导航卡片 -->
    <el-row :gutter="20" class="feature-cards">
      <el-col :span="6">
        <el-card class="feature-card" @click="navigateTo('/permission-dashboard')">
          <div class="card-content">
            <div class="card-icon dashboard">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="card-info">
              <h3>权限仪表板</h3>
              <p>查看权限统计、用户权限和操作日志</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="feature-card" @click="navigateTo('/permissions')">
          <div class="card-content">
            <div class="card-icon permissions">
              <el-icon><Key /></el-icon>
            </div>
            <div class="card-info">
              <h3>权限管理</h3>
              <p>管理菜单权限、按钮权限和API权限</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="feature-card" @click="navigateTo('/roles')">
          <div class="card-content">
            <div class="card-icon roles">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="card-info">
              <h3>角色管理</h3>
              <p>定义角色、分配权限和管理用户角色</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="feature-card" @click="navigateTo('/data-permissions')">
          <div class="card-content">
            <div class="card-icon data">
              <el-icon><Lock /></el-icon>
            </div>
            <div class="card-info">
              <h3>数据权限</h3>
              <p>控制数据访问范围、字段权限和数据脱敏</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速统计 -->
    <el-row :gutter="20" class="stats-section">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Key /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.permissions || 0 }}</div>
              <div class="stat-label">权限数量</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.roles || 0 }}</div>
              <div class="stat-label">角色数量</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.users || 0 }}</div>
              <div class="stat-label">用户数量</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.logs || 0 }}</div>
              <div class="stat-label">操作日志</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近权限操作 -->
    <el-card class="recent-activity">
      <template #header>
        <div class="card-header">
          <span>最近权限操作</span>
          <el-button size="small" @click="refreshActivity">刷新</el-button>
        </div>
      </template>
      
      <el-timeline>
        <el-timeline-item
          v-for="activity in recentActivities"
          :key="activity.id"
          :timestamp="activity.created_at"
          :type="getActivityType(activity.action_type)"
        >
          <div class="activity-content">
            <div class="activity-title">{{ activity.user_name }} - {{ getActivityText(activity.action_type) }}</div>
            <div class="activity-description">
              {{ activity.resource_type }}: {{ activity.resource_id }}
              <el-tag :type="getResultType(activity.result)" size="small">
                {{ activity.result_display }}
              </el-tag>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Key, UserFilled, Lock, User, Document } from '@element-plus/icons-vue'
import api from '@/utils/api'

const router = useRouter()

// 响应式数据
const stats = reactive({
  permissions: 0,
  roles: 0,
  users: 0,
  logs: 0
})

const recentActivities = ref([
  {
    id: 1,
    user_name: 'admin',
    action_type: 'grant',
    resource_type: 'role',
    resource_id: '1',
    result: 'success',
    result_display: '成功',
    created_at: '2024-01-15 14:30:00'
  },
  {
    id: 2,
    user_name: 'admin',
    action_type: 'revoke',
    resource_type: 'permission',
    resource_id: '2',
    result: 'success',
    result_display: '成功',
    created_at: '2024-01-15 14:25:00'
  },
  {
    id: 3,
    user_name: 'admin',
    action_type: 'inherit',
    resource_type: 'role',
    resource_id: '3',
    result: 'success',
    result_display: '成功',
    created_at: '2024-01-15 14:20:00'
  },
  {
    id: 4,
    user_name: 'admin',
    action_type: 'expire',
    resource_type: 'user_role',
    resource_id: '4',
    result: 'success',
    result_display: '成功',
    created_at: '2024-01-15 14:15:00'
  }
])

// 方法
const navigateTo = (path: string) => {
  router.push(path)
}

const loadStats = async () => {
  try {
    // 加载权限统计
    const permissionsResponse = await api.get('/permission/permissions/')
    stats.permissions = permissionsResponse.data.count || 0

    // 加载角色统计
    const rolesResponse = await api.get('/permission/roles/')
    stats.roles = rolesResponse.data.count || 0

    // 加载用户统计
    const usersResponse = await api.get('/api/users/')
    stats.users = usersResponse.data.count || 0

    // 加载日志统计
    const logsResponse = await api.get('/permission/permission-logs/')
    stats.logs = logsResponse.data.count || 0
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const refreshActivity = () => {
  ElMessage.success('活动列表已刷新')
}

const getActivityType = (actionType: string) => {
  const typeMap: Record<string, string> = {
    grant: 'success',
    revoke: 'danger',
    inherit: 'primary',
    expire: 'warning'
  }
  return typeMap[actionType] || 'info'
}

const getActivityText = (actionType: string) => {
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

// 生命周期
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.permission-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.feature-cards {
  margin-bottom: 30px;
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 120px;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.card-icon {
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

.card-icon.dashboard {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-icon.permissions {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.card-icon.roles {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.card-icon.data {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.card-info h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.card-info p {
  margin: 0;
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
}

.stats-section {
  margin-bottom: 30px;
}

.stat-card {
  height: 80px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
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

.recent-activity {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-content {
  padding-left: 10px;
}

.activity-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.activity-description {
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
}
</style>
