<template>
  <div class="intelligent-analysis-page">
    <!-- 现代化页面头部 -->
    <ModernPageHeader
      title="智能分析"
      subtitle="AI驱动的组织架构优化分析与建议"
      icon="DataAnalysis"
      color="blue"
    >
      <template #actions>
        <ModernButton type="secondary" icon="Download" @click="exportReport">
          导出报告
        </ModernButton>
        <ModernButton type="primary" icon="RefreshRight" @click="refreshAnalysis" :loading="loading">
          重新分析
        </ModernButton>
      </template>
    </ModernPageHeader>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <ModernStatCard
        title="组织健康度"
        :value="analysisData.overall_score || 0"
        unit="分"
        change="+5 本月"
        change-type="positive"
        icon="TrendCharts"
        icon-type="success"
        :progress="analysisData.overall_score || 0"
      />
      <ModernStatCard
        title="效率指数"
        :value="getEfficiencyScore()"
        unit="分"
        change="+8 本月"
        change-type="positive"
        icon="DataAnalysis"
        icon-type="primary"
        :progress="getEfficiencyScore()"
      />
      <ModernStatCard
        title="风险等级"
        :value="getRiskLevel()"
        change="-2 本月"
        change-type="positive"
        icon="Warning"
        icon-type="warning"
        :progress="100 - getRiskPercentage()"
      />
      <ModernStatCard
        title="优化潜力"
        :value="getOptimizationPotential()"
        unit="%"
        change="-5 本月"
        change-type="positive"
        icon="Opportunity"
        icon-type="success"
        :progress="getOptimizationPotential()"
      />
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 左侧：分析结果 -->
      <div class="analysis-section">
        <!-- 组织架构可视化 -->
        <ModernCard title="智能架构分析" icon="DataBoard" class="visualization-card">
          <template #actions>
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button value="structure">结构视图</el-radio-button>
              <el-radio-button value="efficiency">效率热图</el-radio-button>
            </el-radio-group>
          </template>
          
          <div class="org-visualization" ref="orgChart">
            <div v-if="loading" class="loading-state">
              <el-icon class="loading-icon"><Loading /></el-icon>
              <p>AI正在分析组织架构...</p>
            </div>
            <div v-else class="org-chart">
              <!-- 这里可以集成组织架构图表库 -->
              <div class="chart-placeholder">
                <el-icon class="chart-icon"><Calendar /></el-icon>
                <p>组织架构图表将在这里显示</p>
              </div>
            </div>
          </div>
        </ModernCard>

        <!-- 分析详情 -->
        <ModernCard title="详细分析报告" icon="Document" class="analysis-details">
          
          <div class="analysis-items">
            <div 
              v-for="result in analysisData.analysis_results" 
              :key="result.category"
              class="analysis-item"
              :class="`border-${getLevelColor(result.level)}`"
            >
              <div class="item-header">
                <h4>{{ getCategoryName(result.category) }}</h4>
                <el-tag 
                  :type="getLevelType(result.level)"
                  effect="light"
                >
                  {{ result.score }}分
                </el-tag>
              </div>
              <p class="item-description">{{ result.description }}</p>
              <div class="item-recommendations">
                <el-tag 
                  v-for="rec in (result.recommendations || []).slice(0, 2)" 
                  :key="rec"
                  size="small"
                  class="recommendation-tag"
                >
                  {{ rec }}
                </el-tag>
              </div>
            </div>
          </div>
        </ModernCard>
      </div>

      <!-- 右侧：优化建议 -->
      <div class="suggestions-section">
        <!-- 智能建议 -->
        <ModernCard title="智能优化建议" icon="Opportunity" class="suggestions-card">
          
          <div class="suggestions-list">
            <div 
              v-for="suggestion in (suggestions || []).slice(0, 5)" 
              :key="suggestion.id"
              class="suggestion-item"
              :class="`priority-${suggestion.priority}`"
            >
              <div class="suggestion-header">
                <div class="priority-indicator" :class="`${suggestion.priority}-priority`">
                  <el-icon v-if="suggestion.priority === 'high'"><AlertCircle /></el-icon>
                  <el-icon v-else-if="suggestion.priority === 'medium'"><Calendar /></el-icon>
                  <el-icon v-else><Calendar /></el-icon>
                </div>
                <div class="suggestion-content">
                  <h4>{{ getPriorityText(suggestion.priority) }}</h4>
                  <p>{{ suggestion.title }}</p>
                </div>
              </div>
              <div class="suggestion-footer">
                <span class="benefit-text">{{ suggestion.expected_benefit }}</span>
                <el-button size="small" text>查看详情</el-button>
              </div>
            </div>
          </div>
        </ModernCard>

        <!-- 实施计划 -->
        <ModernCard title="实施时间线" icon="Calendar" class="timeline-card">
          
          <div class="timeline">
            <div class="timeline-item" v-for="(item, index) in timeline" :key="index">
              <div class="timeline-dot" :class="`${item.priority}-dot`"></div>
              <div class="timeline-content">
                <h4>{{ item.title }}</h4>
                <p>{{ item.description }}</p>
              </div>
            </div>
          </div>
        </ModernCard>

        <!-- 预期效果 -->
        <ModernCard title="预期效果" icon="TrendCharts" class="impact-card">
          
          <div class="impact-metrics">
            <div class="impact-item">
              <span class="metric-label">成本节省</span>
              <span class="metric-value success">¥18万/年</span>
            </div>
            <div class="impact-item">
              <span class="metric-label">效率提升</span>
              <span class="metric-value primary">+25%</span>
            </div>
            <div class="impact-item">
              <span class="metric-label">沟通改善</span>
              <span class="metric-value purple">+30%</span>
            </div>
            <div class="impact-item">
              <span class="metric-label">满意度</span>
              <span class="metric-value warning">+15%</span>
            </div>
          </div>
          
          <ModernButton 
            type="primary" 
            icon="Magic"
            class="generate-plan-btn"
            @click="generateDetailedPlan"
          >
            生成详细实施方案
          </ModernButton>
        </ModernCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  RefreshRight,
  Download,
  Loading,
  Warning as AlertCircle,
  Calendar
} from '@element-plus/icons-vue'
import { intelligenceApi } from '@/api/intelligence'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'

// 响应式数据
const loading = ref(false)
const viewMode = ref('structure')
const analysisData = reactive({
  overall_score: 0,
  health_level: 'unknown',
  analysis_results: [],
  recommendations: [],
  metrics: {},
  timestamp: null
})

const suggestions = ref([])
const timeline = ref([
  {
    title: '第1周：职位合并方案制定',
    description: '人事部门重组',
    priority: 'high'
  },
  {
    title: '第2-4周：人员招聘',
    description: '市场部数据分析师',
    priority: 'medium'
  },
  {
    title: '第5-8周：流程优化',
    description: '跨部门协作机制',
    priority: 'low'
  }
])

// 方法
const fetchAnalysisData = async () => {
  try {
    loading.value = true
    const response = await intelligenceApi.getAnalysis()
    if (response.success) {
      Object.assign(analysisData, response.data)
    }
  } catch (error) {
    ElMessage.error('获取分析数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchSuggestions = async () => {
  try {
    const response = await intelligenceApi.getSuggestions()
    if (response.success && response.data && response.data.by_priority) {
      const high = response.data.by_priority.high || []
      const medium = response.data.by_priority.medium || []
      const low = response.data.by_priority.low || []
      suggestions.value = high.concat(medium, low)
    } else {
      suggestions.value = []
    }
  } catch (error) {
    console.error('获取建议失败:', error)
    suggestions.value = []
  }
}

const refreshAnalysis = async () => {
  try {
    loading.value = true
    const response = await intelligenceApi.refreshAnalysis()
    if (response.success) {
      // 安全地更新数据，确保所有字段都有默认值
      analysisData.overall_score = response.data.overall_score || 0
      analysisData.health_level = response.data.health_level || 'unknown'
      analysisData.analysis_results = response.data.analysis_results || []
      analysisData.recommendations = response.data.recommendations || []
      analysisData.metrics = response.data.metrics || {}
      analysisData.timestamp = response.data.timestamp || null
      ElMessage.success('分析结果已刷新')
      await fetchSuggestions()
    }
  } catch (error) {
    ElMessage.error('刷新分析失败')
  } finally {
    loading.value = false
  }
}

const exportReport = () => {
  ElMessage.info('报告导出功能开发中...')
}

const generateDetailedPlan = () => {
  ElMessageBox.confirm(
    '是否生成详细的实施方案？这将基于当前分析结果创建完整的优化计划。',
    '生成实施方案',
    {
      confirmButtonText: '生成',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    ElMessage.success('实施方案生成中，请稍候...')
  }).catch(() => {
    // 用户取消
  })
}

// 计算方法
const getEfficiencyScore = () => {
  const efficiencyResult = analysisData.analysis_results.find(
    result => result.category === 'structure_efficiency'
  )
  return Math.round(efficiencyResult?.score || 0)
}

const getRiskLevel = () => {
  const riskResult = analysisData.analysis_results.find(
    result => result.category === 'risk_assessment'
  )
  const score = riskResult?.score || 0
  if (score >= 80) return '低'
  if (score >= 60) return '中'
  return '高'
}

const getRiskPercentage = () => {
  const riskResult = analysisData.analysis_results.find(
    result => result.category === 'risk_assessment'
  )
  return 100 - (riskResult?.score || 0)
}

const getOptimizationPotential = () => {
  return Math.round(100 - (analysisData.overall_score || 0))
}

const getCategoryName = (category: string) => {
  const names = {
    'structure_efficiency': '组织结构分析',
    'communication_effectiveness': '沟通效率评估',
    'resource_utilization': '资源利用分析',
    'growth_potential': '成长潜力评估',
    'risk_assessment': '风险识别'
  }
  return names[category] || category
}

const getLevelColor = (level: string) => {
  const colors = {
    'excellent': 'green',
    'good': 'blue',
    'warning': 'yellow',
    'critical': 'red'
  }
  return colors[level] || 'gray'
}

const getLevelType = (level: string) => {
  const types = {
    'excellent': 'success',
    'good': 'primary',
    'warning': 'warning',
    'critical': 'danger'
  }
  return types[level] || 'info'
}

const getPriorityText = (priority: string) => {
  const texts = {
    'high': '高优先级',
    'medium': '中优先级',
    'low': '低优先级'
  }
  return texts[priority] || priority
}

// 生命周期
onMounted(() => {
  fetchAnalysisData()
  fetchSuggestions()
})
</script>

<style scoped>
.intelligent-analysis-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #dbeafe 100%);
  min-height: 100vh;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  font-size: 2.5rem;
}

.header-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
}

.header-subtitle {
  font-size: 1rem;
  opacity: 0.9;
  margin: 0.5rem 0 0 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.card-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.metric-info h3 {
  font-size: 0.9rem;
  color: #6b7280;
  margin: 0 0 0.5rem 0;
  font-weight: 500;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
}

.metric-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.success-gradient {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.primary-gradient {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.warning-gradient {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.purple-gradient {
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease;
}

/* 主要内容 */
.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.analysis-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.suggestions-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 卡片样式 */
.el-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
}

.header-icon {
  margin-right: 0.5rem;
  color: #6366f1;
}

/* 组织架构可视化 */
.org-visualization {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-state {
  text-align: center;
  color: #6b7280;
}

.loading-icon {
  font-size: 2rem;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.chart-placeholder {
  text-align: center;
  color: #9ca3af;
}

.chart-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

/* 分析详情 */
.analysis-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.analysis-item {
  padding: 1rem;
  border-left: 4px solid;
  background: #f9fafb;
  border-radius: 0 8px 8px 0;
}

.border-green { border-left-color: #10b981; }
.border-blue { border-left-color: #3b82f6; }
.border-yellow { border-left-color: #f59e0b; }
.border-red { border-left-color: #ef4444; }

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.item-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.item-description {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.item-recommendations {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.recommendation-tag {
  font-size: 0.8rem;
}

/* 建议列表 */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.suggestion-item {
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: white;
}

.priority-high {
  border-left: 4px solid #ef4444;
  background: #fef2f2;
}

.priority-medium {
  border-left: 4px solid #f59e0b;
  background: #fffbeb;
}

.priority-low {
  border-left: 4px solid #3b82f6;
  background: #eff6ff;
}

.suggestion-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.priority-indicator {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.high-priority { background: #ef4444; }
.medium-priority { background: #f59e0b; }
.low-priority { background: #3b82f6; }

.suggestion-content h4 {
  margin: 0 0 0.25rem 0;
  font-size: 0.9rem;
  font-weight: 600;
}

.suggestion-content p {
  margin: 0;
  font-size: 0.85rem;
  color: #6b7280;
  line-height: 1.4;
}

.suggestion-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.benefit-text {
  font-size: 0.8rem;
  color: #059669;
  font-weight: 500;
}

/* 时间线 */
.timeline {
  position: relative;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
  position: relative;
}

.timeline-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 0.75rem;
  top: 2rem;
  width: 2px;
  height: calc(100% + 0.5rem);
  background: #e5e7eb;
}

.timeline-dot {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  flex-shrink: 0;
  z-index: 1;
}

.high-dot { background: #ef4444; }
.medium-dot { background: #f59e0b; }
.low-dot { background: #3b82f6; }

.timeline-content h4 {
  margin: 0 0 0.25rem 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1f2937;
}

.timeline-content p {
  margin: 0;
  font-size: 0.8rem;
  color: #6b7280;
}

/* 影响指标 */
.impact-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.impact-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 0.9rem;
  color: #6b7280;
}

.metric-value {
  font-weight: 600;
  font-size: 1rem;
}

.metric-value.success { color: #10b981; }
.metric-value.primary { color: #3b82f6; }
.metric-value.purple { color: #8b5cf6; }
.metric-value.warning { color: #f59e0b; }

.generate-plan-btn {
  width: 100%;
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
  border: none;
  font-weight: 600;
}

.generate-plan-btn:hover {
  background: linear-gradient(135deg, #7c3aed, #8b5cf6);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .overview-cards {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .overview-cards {
    grid-template-columns: 1fr;
    padding: 0 1rem;
  }
  
  .main-content {
    padding: 0 1rem;
  }
}
</style>
