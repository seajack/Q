<template>
  <div class="integration-management">
    <div class="page-header">
      <h1>集成管理</h1>
      <p class="page-description">管理第三方系统集成、API网关和数据同步</p>
    </div>

    <!-- 功能导航卡片 -->
    <el-row :gutter="20" class="feature-cards">
      <el-col :span="6">
        <el-card class="feature-card" @click="navigateTo('/integration-dashboard')">
          <div class="card-content">
            <div class="card-icon dashboard">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="card-info">
              <h3>集成仪表板</h3>
              <p>查看系统状态、性能指标和监控数据</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="feature-card" @click="navigateTo('/integration-systems')">
          <div class="card-content">
            <div class="card-icon systems">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="card-info">
              <h3>集成系统</h3>
              <p>管理第三方系统连接和配置</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="feature-card" @click="navigateTo('/api-gateways')">
          <div class="card-content">
            <div class="card-icon gateways">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="card-info">
              <h3>API网关</h3>
              <p>配置API路由、限流和缓存</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="feature-card" @click="navigateTo('/data-sync-rules')">
          <div class="card-content">
            <div class="card-icon sync">
              <el-icon><Refresh /></el-icon>
            </div>
            <div class="card-info">
              <h3>数据同步</h3>
              <p>配置数据同步规则和字段映射</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速统计 -->
    <el-row :gutter="20" class="stats-section">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.systems || 0 }}</div>
              <div class="stat-label">集成系统</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.gateways || 0 }}</div>
              <div class="stat-label">API网关</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Refresh /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.syncRules || 0 }}</div>
              <div class="stat-label">同步规则</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-card class="recent-activity">
      <template #header>
        <div class="card-header">
          <span>最近活动</span>
          <el-button size="small" @click="refreshActivity">刷新</el-button>
        </div>
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
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Monitor, Connection, Refresh } from '@element-plus/icons-vue'
import api from '@/utils/api'

const router = useRouter()

// 响应式数据
const stats = reactive({
  systems: 0,
  gateways: 0,
  syncRules: 0
})

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
    const systemsResponse = await api.get('/integration/systems/')
    stats.systems = systemsResponse.data.count || 0

    // 加载网关统计
    const gatewaysResponse = await api.get('/integration/gateways/')
    stats.gateways = gatewaysResponse.data.count || 0

    // 加载同步规则统计
    const syncRulesResponse = await api.get('/integration/sync-rules/')
    stats.syncRules = syncRulesResponse.data.count || 0
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
.integration-management {
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
