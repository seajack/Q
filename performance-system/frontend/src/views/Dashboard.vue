<template>
  <div class="performance-dashboard">
    <!-- 导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <h1 class="title">绩效考核管理系统</h1>
        <el-menu mode="horizontal" :default-active="activeMenu" class="nav-menu" router>
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <span>仪表板</span>
          </el-menu-item>
          <el-menu-item index="/cycles">
            <el-icon><Calendar /></el-icon>
            <span>考核周期</span>
          </el-menu-item>
          <el-menu-item index="/indicators">
            <el-icon><DataBoard /></el-icon>
            <span>考核指标</span>
          </el-menu-item>
          <el-menu-item index="/rules">
            <el-icon><Setting /></el-icon>
            <span>考核规则</span>
          </el-menu-item>
          <el-menu-item index="/employees">
            <el-icon><User /></el-icon>
            <span>员工管理</span>
          </el-menu-item>
          <el-menu-item index="/tasks">
            <el-icon><Document /></el-icon>
            <span>考核任务</span>
          </el-menu-item>
          <el-menu-item index="/results">
            <el-icon><TrendCharts /></el-icon>
            <span>考核结果</span>
          </el-menu-item>
          <el-menu-item index="/organization">
            <el-icon><OfficeBuilding /></el-icon>
            <span>组织架构</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-container class="main-container">
      <el-main class="main-content">
        <!-- 统计卡片 -->
        <el-row :gutter="20" class="stats-row">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-icon cycles">
                  <el-icon><Calendar /></el-icon>
                </div>
                <div class="stat-info">
                  <h3>{{ stats?.active_cycles || 0 }}</h3>
                  <p>活跃考核周期</p>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-icon tasks">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="stat-info">
                  <h3>{{ stats?.total_tasks || 0 }}</h3>
                  <p>考核任务总数</p>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-icon completed">
                  <el-icon><Check /></el-icon>
                </div>
                <div class="stat-info">
                  <h3>{{ stats?.completed_tasks || 0 }}</h3>
                  <p>已完成任务</p>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-icon rate">
                  <el-icon><TrendCharts /></el-icon>
                </div>
                <div class="stat-info">
                  <h3>{{ (stats?.completion_rate || 0).toFixed(1) }}%</h3>
                  <p>完成率</p>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 考核进度和部门统计 -->
        <el-row :gutter="20" class="chart-row">
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>考核进度概览</span>
                </div>
              </template>
              <div class="progress-content">
                <div class="progress-item">
                  <span class="progress-label">总体完成率</span>
                  <el-progress 
                    :percentage="stats?.completion_rate || 0"
                    :format="(percentage) => `${percentage}%`"
                    :stroke-width="20"
                  />
                </div>
                <div class="metrics-grid">
                  <div class="metric-item">
                    <span class="metric-label">平均分数</span>
                    <span class="metric-value">{{ (stats?.average_score || 0).toFixed(1) }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">参与部门</span>
                    <span class="metric-value">{{ stats?.department_stats?.length || 0 }}</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>各部门考核情况</span>
                </div>
              </template>
              <div class="department-stats">
                <div 
                  v-for="dept in stats?.department_stats?.slice(0, 5)" 
                  :key="dept.department_name"
                  class="dept-item"
                >
                  <div class="dept-name">{{ dept.department_name }}</div>
                  <div class="dept-metrics">
                    <span class="dept-count">{{ dept.employee_count }}人</span>
                    <el-progress 
                      :percentage="dept.completion_rate"
                      :format="() => `${dept.average_score.toFixed(1)}分`"
                      :stroke-width="12"
                      :color="getProgressColor(dept.average_score)"
                    />
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 快速操作和考核码入口 -->
        <el-row :gutter="20" class="action-row">
          <el-col :span="12">
            <el-card class="action-card">
              <template #header>
                <div class="card-header">
                  <span>快速操作</span>
                </div>
              </template>
              <div class="action-buttons">
                <el-button type="primary" size="large" @click="$router.push('/cycles')">
                  <el-icon><Plus /></el-icon>
                  新建考核周期
                </el-button>
                <el-button type="success" size="large" @click="syncEmployees">
                  <el-icon><Refresh /></el-icon>
                  同步员工数据
                </el-button>
                <el-button type="info" size="large" @click="$router.push('/tasks')">
                  <el-icon><View /></el-icon>
                  查看考核任务
                </el-button>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="evaluation-card">
              <template #header>
                <div class="card-header">
                  <span>考核评分入口</span>
                </div>
              </template>
              <div class="evaluation-form">
                <el-input
                  v-model="evaluationCode"
                  placeholder="请输入16位考核码"
                  maxlength="16"
                  show-word-limit
                  size="large"
                  class="code-input"
                >
                  <template #prepend>考核码</template>
                </el-input>
                <el-button 
                  type="primary" 
                  size="large" 
                  @click="goToEvaluation"
                  :disabled="!evaluationCode || evaluationCode.length !== 16"
                  class="eval-button"
                >
                  开始考核
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useEvaluationStore } from '@/stores/evaluation'
import { 
  House, 
  Calendar, 
  DataBoard, 
  Setting,
  User, 
  Document, 
  TrendCharts,
  OfficeBuilding,
  Check,
  Plus,
  Refresh,
  View
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const evaluationStore = useEvaluationStore()

const evaluationCode = ref('')
const activeMenu = computed(() => route.path)
const stats = computed(() => evaluationStore.stats)

const getProgressColor = (score: number) => {
  if (score >= 90) return '#67C23A'
  if (score >= 80) return '#E6A23C'
  if (score >= 70) return '#F56C6C'
  return '#909399'
}

const syncEmployees = async () => {
  try {
    await evaluationStore.syncEmployees()
    ElMessage.success('员工数据同步成功')
  } catch (error) {
    ElMessage.error('员工数据同步失败')
  }
}

const goToEvaluation = () => {
  if (evaluationCode.value && evaluationCode.value.length === 16) {
    router.push(`/evaluation/${evaluationCode.value}`)
  }
}

onMounted(async () => {
  try {
    await evaluationStore.fetchStats()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
})
</script>

<style scoped>
.performance-dashboard {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.title {
  color: #303133;
  font-size: 20px;
  margin: 0;
}

.nav-menu {
  background: none;
  border: none;
}

.main-container {
  background: none;
}

.main-content {
  padding: 20px;
}

.stats-row {
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
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.stat-icon.cycles {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.tasks {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.completed {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon.rate {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-icon .el-icon {
  font-size: 24px;
}

.stat-info h3 {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
  color: #303133;
}

.stat-info p {
  font-size: 14px;
  color: #909399;
  margin: 5px 0 0 0;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  min-height: 300px;
}

.card-header {
  font-weight: bold;
  color: #303133;
}

.progress-content {
  padding: 20px 0;
}

.progress-item {
  margin-bottom: 30px;
}

.progress-label {
  display: block;
  margin-bottom: 10px;
  font-size: 14px;
  color: #606266;
}

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.metric-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.metric-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.department-stats {
  padding: 20px 0;
}

.dept-item {
  margin-bottom: 20px;
}

.dept-name {
  font-size: 14px;
  color: #303133;
  margin-bottom: 8px;
}

.dept-metrics {
  display: flex;
  align-items: center;
  gap: 15px;
}

.dept-count {
  font-size: 12px;
  color: #909399;
  min-width: 40px;
}

.action-row {
  margin-bottom: 20px;
}

.action-card {
  text-align: center;
}

.action-buttons {
  padding: 20px 0;
}

.action-buttons .el-button {
  margin: 0 10px 10px 0;
}

.evaluation-card {
  text-align: center;
}

.evaluation-form {
  padding: 20px 0;
}

.code-input {
  margin-bottom: 20px;
}

.eval-button {
  width: 100%;
}
</style>