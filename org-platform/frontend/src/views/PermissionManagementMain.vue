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
      <!-- 权限管理功能选项卡 -->
      <ModernCard title="权限管理" icon="Menu" class="permission-tabs">
        <el-tabs v-model="activeTab" type="card" class="permission-management-tabs">
          <el-tab-pane label="权限仪表板" name="dashboard">
            <PermissionDashboard />
          </el-tab-pane>
          <el-tab-pane label="权限管理" name="permissions">
            <PermissionManagement />
          </el-tab-pane>
          <el-tab-pane label="角色管理" name="roles">
            <RoleManagement />
          </el-tab-pane>
          <el-tab-pane label="数据权限" name="data-permissions">
            <DataPermissionManagement />
          </el-tab-pane>
        </el-tabs>
      </ModernCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { DataAnalysis, Key, UserFilled, Lock, User, Document } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { permissionApi } from '@/utils/api'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'
// 导入权限管理子组件
import PermissionDashboard from './PermissionDashboard.vue'
import PermissionManagement from './PermissionManagement.vue'
import RoleManagement from './RoleManagement.vue'
import DataPermissionManagement from './DataPermissionManagement.vue'

// 响应式数据
const activeTab = ref('dashboard')
const stats = reactive({
  permissions: 0,
  roles: 0,
  users: 0,
  logs: 0
})

// 方法
const loadStats = async () => {
  try {
    // 加载权限统计
    try {
      const permissionsResponse = await permissionApi.permissions.list()
      stats.permissions = Array.isArray(permissionsResponse) ? permissionsResponse.length : 0
    } catch (error) {
      console.warn('权限API暂未实现')
      stats.permissions = 0
    }

    // 加载角色统计
    try {
      const rolesResponse = await permissionApi.roles.list()
      stats.roles = Array.isArray(rolesResponse) ? rolesResponse.length : 0
    } catch (error) {
      console.warn('角色API暂未实现')
      stats.roles = 0
    }

    // 加载用户统计
    try {
      const usersResponse = await permissionApi.users.list()
      stats.users = Array.isArray(usersResponse) ? usersResponse.length : 0
    } catch (error) {
      console.warn('用户API暂未实现')
      stats.users = 0
    }

    // 加载日志统计
    try {
      const logsResponse = await permissionApi.logs.list()
      stats.logs = Array.isArray(logsResponse) ? logsResponse.length : 0
    } catch (error) {
      console.warn('权限日志API暂未实现')
      stats.logs = 0
    }
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
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
  display: block;
}

/* 权限管理选项卡 */
.permission-tabs {
  height: fit-content;
}

.permission-management-tabs {
  margin-top: 1rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
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
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
