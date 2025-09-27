<template>
  <div class="evaluation-page">
    <div class="header">
      <div class="header-content">
        <h1 class="title">我的考核任务</h1>
        <div class="user-info">
          <span class="code-display">考核码: {{ evaluationCode }}</span>
          <el-button @click="logout" type="text" class="logout-btn">退出</el-button>
        </div>
      </div>
    </div>
    
    <div class="content">
      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      
      <div v-else-if="tasks.length === 0" class="empty-state">
        <el-icon class="empty-icon"><Document /></el-icon>
        <h3>暂无考核任务</h3>
        <p>您当前没有需要完成的考核任务</p>
      </div>
      
      <div v-else class="tasks-container">
        <div class="stats-bar">
          <div class="stat-item">
            <span class="stat-number">{{ tasks.length }}</span>
            <span class="stat-label">总任务数</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ completedCount }}</span>
            <span class="stat-label">已完成</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ pendingCount }}</span>
            <span class="stat-label">待完成</span>
          </div>
        </div>
        
        <div class="tasks-grid">
          <div 
            v-for="task in tasks" 
            :key="task.id"
            class="task-card"
            :class="{ 'completed': task.status === 'completed' }"
          >
            <div class="task-header">
              <h3 class="task-title">{{ task.evaluatee_name }}</h3>
              <el-tag 
                :type="getStatusType(task.status)"
                size="small"
              >
                {{ getStatusText(task.status) }}
              </el-tag>
            </div>
            
            <div class="task-info">
              <div class="info-row">
                <span class="label">职位:</span>
                <span class="value">{{ task.evaluatee_position }}</span>
              </div>
              <div class="info-row">
                <span class="label">部门:</span>
                <span class="value">{{ task.evaluatee_department }}</span>
              </div>
              <div class="info-row">
                <span class="label">关系类型:</span>
                <span class="value">{{ getRelationText(task.relation_type) }}</span>
              </div>
              <div class="info-row">
                <span class="label">权重:</span>
                <span class="value">{{ task.weight }}%</span>
              </div>
            </div>
            
            <div class="task-actions">
              <el-button 
                v-if="task.status === 'pending'"
                type="primary"
                @click="startEvaluation(task)"
                class="start-btn"
              >
                开始考核
              </el-button>
              <el-button 
                v-else-if="task.status === 'in_progress'"
                type="success"
                @click="continueEvaluation(task)"
                class="continue-btn"
              >
                继续考核
              </el-button>
              <el-button 
                v-else
                type="info"
                @click="viewEvaluation(task)"
                class="view-btn"
              >
                查看结果
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, Document } from '@element-plus/icons-vue'
import { taskApi } from '@/utils/api'

const router = useRouter()

// 响应式数据
const loading = ref(true)
const tasks = ref([])
const evaluationCode = ref('')

// 计算属性
const completedCount = computed(() => {
  return tasks.value.filter((task: any) => task.status === 'completed').length
})

const pendingCount = computed(() => {
  return tasks.value.filter((task: any) => task.status === 'pending' || task.status === 'in_progress').length
})

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待考核',
    'in_progress': '考核中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

// 获取关系类型文本
const getRelationText = (relationType: string) => {
  const relationMap: Record<string, string> = {
    'superior': '上级评下级',
    'peer': '同级互评',
    'subordinate': '下级评上级',
    'cross_superior': '跨部门上级'
  }
  return relationMap[relationType] || relationType
}

// 开始考核 - 自动选择下一个待完成的任务
const startEvaluation = (task: any) => {
  // 找到下一个待完成的任务
  const nextPendingTask = tasks.value.find(t => t.status === 'pending')
  if (nextPendingTask) {
    router.push(`/evaluation/${nextPendingTask.id}`)
  } else {
    ElMessage.warning('没有待完成的考核任务')
  }
}

// 继续考核
const continueEvaluation = (task: any) => {
  router.push(`/evaluation/${task.evaluation_code}`)
}

// 查看考核结果
const viewEvaluation = (task: any) => {
  router.push(`/evaluation/${task.evaluation_code}`)
}

// 退出登录
const logout = () => {
  sessionStorage.removeItem('evaluationCode')
  router.push('/evaluation-entry')
}

// 加载考核任务
const loadTasks = async () => {
  try {
    loading.value = true
    const code = sessionStorage.getItem('evaluationCode')
    
    if (!code) {
      ElMessage.error('请先输入考核码')
      router.push('/evaluation-entry')
      return
    }
    
    evaluationCode.value = code
    const response = await taskApi.getEvaluatorTasks(code)
    tasks.value = response.data.tasks || []
    
    // 调试信息：打印任务状态
    console.log('加载的任务:', tasks.value.map(t => ({
      id: t.id,
      evaluatee_name: t.evaluatee_name,
      status: t.status
    })))
    
  } catch (error: any) {
    console.error('加载考核任务失败:', error)
    ElMessage.error('加载考核任务失败，请重试')
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadTasks()
})

// 组件激活时重新加载数据（从其他页面返回时）
onActivated(() => {
  loadTasks()
})
</script>

<style scoped>
.evaluation-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px 0;
  margin-bottom: 30px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.code-display {
  font-family: 'Courier New', monospace;
  font-size: 1.1rem;
  font-weight: bold;
  color: #667eea;
  background: #f0f2ff;
  padding: 8px 16px;
  border-radius: 20px;
  border: 2px solid #e1e8ed;
}

.logout-btn {
  color: #7f8c8d;
  font-size: 1rem;
}

.logout-btn:hover {
  color: #e74c3c;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #7f8c8d;
  font-size: 1.1rem;
}

.loading-container .el-icon {
  font-size: 2rem;
  margin-bottom: 10px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  color: #bdc3c7;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.empty-state p {
  font-size: 1rem;
  margin: 0;
}

.stats-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  justify-content: center;
}

.stat-item {
  background: white;
  padding: 20px 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  min-width: 120px;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  color: #7f8c8d;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.task-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.task-card.completed {
  border-color: #27ae60;
  background: linear-gradient(135deg, #ffffff 0%, #f8fff8 100%);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.task-title {
  font-size: 1.3rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.task-info {
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  padding: 4px 0;
}

.info-row:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 500;
  color: #7f8c8d;
  min-width: 80px;
}

.value {
  color: #2c3e50;
  font-weight: 500;
}

.task-actions {
  text-align: center;
}

.start-btn,
.continue-btn,
.view-btn {
  width: 100%;
  height: 40px;
  font-weight: bold;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.start-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
}

.continue-btn {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  border: none;
}

.view-btn {
  background: linear-gradient(135deg, #3498db, #2980b9);
  border: none;
}

.start-btn:hover,
.continue-btn:hover,
.view-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .stats-bar {
    flex-direction: column;
    align-items: center;
  }
  
  .tasks-grid {
    grid-template-columns: 1fr;
  }
  
  .task-card {
    margin: 0 10px;
  }
}

@media (max-width: 480px) {
  .content {
    padding: 0 10px;
  }
  
  .task-card {
    margin: 0;
    padding: 20px;
  }
  
  .stat-item {
    padding: 15px 20px;
    min-width: 100px;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
}
</style>
