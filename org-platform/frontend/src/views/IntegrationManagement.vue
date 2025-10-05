<template>
  <div class="integration-management-page">
    <!-- 现代化页面头部 -->
    <ModernPageHeader
      title="集成管理"
      subtitle="第三方系统集成、API网关和数据同步管理"
      icon="Connection"
      color="emerald"
    >
      <template #actions>
        <ModernButton type="primary" icon="Plus">
          新增集成
        </ModernButton>
      </template>
    </ModernPageHeader>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <ModernStatCard
        title="集成系统"
        :value="overview.systems?.total || 0"
        :subtitle="`活跃: ${overview.systems?.active || 0} | 禁用: ${overview.systems?.inactive || 0}`"
        change="+2 本月"
        change-type="positive"
        icon="Monitor"
        icon-type="success"
        card-type="systems"
        :trend="true"
        trend-type="up"
      />
      <ModernStatCard
        title="API网关"
        :value="overview.systems?.total || 0"
        :subtitle="`路由: 5 | 活跃: ${overview.systems?.active || 0}`"
        change="+1 本月"
        change-type="positive"
        icon="Connection"
        icon-type="primary"
        card-type="gateways"
        :trend="true"
        trend-type="up"
      />
      <ModernStatCard
        title="同步规则"
        :value="overview.sync_rules?.total || 0"
        :subtitle="`活跃: ${overview.sync_rules?.active || 0} | 禁用: ${overview.sync_rules?.inactive || 0}`"
        change="+3 本月"
        change-type="positive"
        icon="Refresh"
        icon-type="warning"
        card-type="sync"
        :trend="true"
        trend-type="up"
      />
      <ModernStatCard
        title="在线系统"
        :value="overview.recent_syncs?.total || 0"
        :subtitle="`成功率: ${overview.recent_syncs?.success_rate?.toFixed(1) || 0}%`"
        change="100% 在线"
        change-type="positive"
        icon="CircleCheck"
        icon-type="success"
        card-type="online"
        :trend="true"
        trend-type="stable"
      />
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 功能标签页 -->
      <ModernCard title="集成管理" icon="Menu" class="feature-tabs">
        <el-tabs v-model="activeTab" type="card" class="integration-tabs">
          <el-tab-pane label="系统监控" name="dashboard">
            <IntegrationDashboard />
          </el-tab-pane>
          <el-tab-pane label="集成系统" name="systems">
            <IntegrationSystems />
          </el-tab-pane>
          <el-tab-pane label="API网关" name="gateways">
            <APIGateways />
          </el-tab-pane>
          <el-tab-pane label="数据同步" name="sync">
            <DataSyncRules />
          </el-tab-pane>
        </el-tabs>
      </ModernCard>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Monitor, Connection, Refresh } from '@element-plus/icons-vue'
import api from '@/utils/api'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'
// 导入集成管理相关组件
import IntegrationDashboard from './IntegrationDashboard.vue'
import IntegrationSystems from './IntegrationSystems.vue'
import APIGateways from './APIGateways.vue'
import DataSyncRules from './DataSyncRules.vue'

const router = useRouter()

// 响应式数据
const activeTab = ref('dashboard')
const stats = reactive({
  systems: 0,
  gateways: 0,
  syncRules: 0
})

// 概览数据
const overview = reactive({
  systems: { total: 0, active: 0, inactive: 0 },
  sync_rules: { total: 0, active: 0, inactive: 0 },
  api_requests: { total: 0, success_rate: 0 },
  recent_syncs: { total: 0, success_rate: 0 }
})

// 统计方法
const getOnlineSystems = () => {
  return Math.floor((stats.systems || 0) * 0.9) // 模拟90%在线率
}

const recentActivities = ref([
  {
    id: 1,
    title: '绩效考核系统连接成功',
    description: '系统连接测试通过，响应时间 120ms',
    timestamp: '2024-01-15 14:30:00',
    type: 'success'
  },
  {
    id: 2,
    title: '员工数据同步完成',
    description: '同步 1,250 条员工记录，成功率 100%',
    timestamp: '2024-01-15 14:25:00',
    type: 'primary'
  },
  {
    id: 3,
    title: 'API网关路由更新',
    description: '新增 /api/performance/* 路由配置',
    timestamp: '2024-01-15 14:20:00',
    type: 'info'
  },
  {
    id: 4,
    title: 'OA系统连接失败',
    description: '连接超时，请检查网络配置',
    timestamp: '2024-01-15 14:15:00',
    type: 'danger'
  }
])

// 方法
const loadStats = async () => {
  try {
    // 加载概览数据
    try {
      const overviewResponse = await api.get('/integration/dashboard/overview/')
      Object.assign(overview, overviewResponse)
    } catch (error) {
      console.warn('概览数据API暂未实现，使用默认值')
      // 使用默认值
    }

    // 加载系统统计
    try {
      const systemsResponse = await api.get('/simple-integration/systems/')
      stats.systems = systemsResponse.length || 0
    } catch (error) {
      console.warn('集成系统API暂未实现')
      stats.systems = 0
    }

    // 加载网关统计
    try {
      const gatewaysResponse = await api.get('/simple-integration/gateways/')
      stats.gateways = gatewaysResponse.length || 0
    } catch (error) {
      console.warn('集成网关API暂未实现')
      stats.gateways = 0
    }

    // 加载同步规则统计
    try {
      const syncRulesResponse = await api.get('/simple-integration/sync_rules/')
      stats.syncRules = syncRulesResponse.length || 0
    } catch (error) {
      console.warn('同步规则API暂未实现')
      stats.syncRules = 0
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
.integration-management-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #d1fae5 100%);
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

/* 功能标签页 */
.feature-tabs {
  height: fit-content;
}

.integration-tabs {
  margin-top: 1rem;
}

.integration-tabs .el-tabs__content {
  padding: 1rem 0;
}

.integration-tabs .el-tab-pane {
  min-height: 600px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    display: block;
  }
}

@media (max-width: 768px) {
  .integration-management-page {
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
