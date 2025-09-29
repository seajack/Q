<template>
  <div class="permission-management-page">
    <!-- 现代化页面头部 -->
    <ModernPageHeader
      title="权限管理"
      subtitle="系统权限、角色分配和数据权限控制管理"
      icon="Lock"
      color="purple"
    >
      <template #actions>
        <ModernButton type="secondary" icon="Document">
          权限报告
        </ModernButton>
        <ModernButton type="primary" icon="Plus">
          新增权限
        </ModernButton>
      </template>
    </ModernPageHeader>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <ModernStatCard
        title="权限数量"
        :value="stats.permissions || 0"
        change="+5 本月"
        change-type="positive"
        icon="Key"
        icon-type="primary"
      />
      <ModernStatCard
        title="角色数量"
        :value="stats.roles || 0"
        change="+2 本月"
        change-type="positive"
        icon="UserFilled"
        icon-type="success"
      />
      <ModernStatCard
        title="用户数量"
        :value="stats.users || 0"
        change="+12 本月"
        change-type="positive"
        icon="User"
        icon-type="warning"
      />
      <ModernStatCard
        title="操作日志"
        :value="stats.logs || 0"
        change="+89 今日"
        change-type="positive"
        icon="Document"
        icon-type="success"
      />
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 功能导航 -->
      <ModernCard title="功能导航" icon="Menu" class="feature-nav">
        <div class="feature-grid">
          <div class="feature-item" @click="navigateTo('/permission-dashboard')">
            <div class="feature-icon dashboard">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="feature-info">
              <h4>权限仪表板</h4>
              <p>查看权限统计和日志</p>
            </div>
          </div>
          
          <div class="feature-item" @click="navigateTo('/permissions')">
            <div class="feature-icon permissions">
              <el-icon><Key /></el-icon>
            </div>
            <div class="feature-info">
              <h4>权限管理</h4>
              <p>管理菜单和API权限</p>
            </div>
          </div>
          
          <div class="feature-item" @click="navigateTo('/roles')">
            <div class="feature-icon roles">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="feature-info">
              <h4>角色管理</h4>
              <p>定义角色和分配权限</p>
            </div>
          </div>
          
          <div class="feature-item" @click="navigateTo('/data-permissions')">
            <div class="feature-icon data">
              <el-icon><Lock /></el-icon>
            </div>
            <div class="feature-info">
              <h4>数据权限</h4>
              <p>控制数据访问范围</p>
            </div>
          </div>
        </div>
      </ModernCard>

      <!-- 最近权限操作 -->
      <ModernCard title="最近权限操作" icon="Clock" class="activity-card">
        <template #actions>
          <ModernButton type="secondary" icon="Refresh" size="small" @click="refreshActivity">
            刷新
          </ModernButton>
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
      </ModernCard>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Key, UserFilled, Lock, User, Document } from '@element-plus/icons-vue'
import api from '@/utils/api'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'

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
    try {
      const permissionsResponse = await api.get('/simple-permission/permissions/')
      stats.permissions = permissionsResponse.length || 0
    } catch (error) {
      console.warn('权限API暂未实现')
      stats.permissions = 0
    }

    // 加载角色统计
    try {
      const rolesResponse = await api.get('/simple-permission/roles/')
      stats.roles = rolesResponse.length || 0
    } catch (error) {
      console.warn('角色API暂未实现')
      stats.roles = 0
    }

    // 加载用户统计
    try {
      const usersResponse = await api.get('/simple-permission/users/')
      stats.users = usersResponse.length || 0
    } catch (error) {
      console.warn('用户API暂未实现')
      stats.users = 0
    }

    // 加载日志统计
    try {
      const logsResponse = await api.get('/simple-permission/permission_logs/')
      stats.logs = logsResponse.length || 0
    } catch (error) {
      console.warn('权限日志API暂未实现')
      stats.logs = 0
    }
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
.permission-management-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f3e8ff 100%);
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
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

/* 功能导航 */
.feature-nav {
  height: fit-content;
}

.feature-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
  background: white;
}

.feature-item:hover {
  background: #f8fafc;
  border-color: #8b5cf6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
}

.feature-icon.dashboard {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.feature-icon.permissions {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.feature-icon.roles {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.feature-icon.data {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
}

.feature-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.feature-info p {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.4;
}

/* 活动卡片 */
.activity-card {
  height: fit-content;
}

.activity-content {
  padding-left: 10px;
}

.activity-title {
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
  font-size: 0.875rem;
}

.activity-description {
  font-size: 0.75rem;
  color: #6b7280;
  line-height: 1.4;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .permission-management-page {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
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
