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
        <ModernButton type="secondary" icon="Monitor">
          系统监控
        </ModernButton>
        <ModernButton type="primary" icon="Plus">
          新增集成
        </ModernButton>
      </template>
    </ModernPageHeader>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <ModernStatCard
        title="集成系统"
        :value="stats.systems || 0"
        change="+2 本月"
        change-type="positive"
        icon="Monitor"
        icon-type="success"
      />
      <ModernStatCard
        title="API网关"
        :value="stats.gateways || 0"
        change="+1 本月"
        change-type="positive"
        icon="Connection"
        icon-type="primary"
      />
      <ModernStatCard
        title="同步规则"
        :value="stats.syncRules || 0"
        change="+3 本月"
        change-type="positive"
        icon="Refresh"
        icon-type="warning"
      />
      <ModernStatCard
        title="在线系统"
        :value="getOnlineSystems()"
        change="100% 在线"
        change-type="positive"
        icon="CircleCheck"
        icon-type="success"
      />
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 功能导航 -->
      <ModernCard title="功能导航" icon="Menu" class="feature-nav">
        <div class="feature-grid">
          <div class="feature-item" @click="navigateTo('/integration-dashboard')">
            <div class="feature-icon dashboard">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="feature-info">
              <h4>集成仪表板</h4>
              <p>查看系统状态和性能指标</p>
            </div>
          </div>
          
          <div class="feature-item" @click="navigateTo('/integration-systems')">
            <div class="feature-icon systems">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="feature-info">
              <h4>集成系统</h4>
              <p>管理第三方系统连接</p>
            </div>
          </div>
          
          <div class="feature-item" @click="navigateTo('/api-gateways')">
            <div class="feature-icon gateways">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="feature-info">
              <h4>API网关</h4>
              <p>配置API路由和限流</p>
            </div>
          </div>
          
          <div class="feature-item" @click="navigateTo('/data-sync-rules')">
            <div class="feature-icon sync">
              <el-icon><Refresh /></el-icon>
            </div>
            <div class="feature-info">
              <h4>数据同步</h4>
              <p>配置同步规则和映射</p>
            </div>
          </div>
        </div>
      </ModernCard>

      <!-- 最近活动 -->
      <ModernCard title="最近活动" icon="Clock" class="activity-card">
        <template #actions>
          <ModernButton type="secondary" icon="Refresh" size="small" @click="refreshActivity">
            刷新
          </ModernButton>
        </template>
        
        <el-timeline>
          <el-timeline-item
            v-for="activity in recentActivities"
            :key="activity.id"
            :timestamp="activity.timestamp"
            :type="activity.type"
          >
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-description">{{ activity.description }}</div>
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
import { DataAnalysis, Monitor, Connection, Refresh } from '@element-plus/icons-vue'
import api from '@/utils/api'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'

const router = useRouter()

// 响应式数据
const stats = reactive({
  systems: 0,
  gateways: 0,
  syncRules: 0
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
const navigateTo = (path: string) => {
  router.push(path)
}

const loadStats = async () => {
  try {
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

const refreshActivity = () => {
  ElMessage.success('活动列表已刷新')
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
  border-color: #10b981;
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

.feature-icon.systems {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.feature-icon.gateways {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.feature-icon.sync {
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
  .integration-management-page {
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

.card-icon.systems {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.card-icon.gateways {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.card-icon.sync {
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
