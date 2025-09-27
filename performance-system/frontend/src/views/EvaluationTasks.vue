<template>
  <div class="evaluation-tasks">
    <!-- 考核人信息头部 -->
    <div class="evaluator-header">
      <div class="evaluator-info">
        <h2>{{ evaluatorInfo.name }}</h2>
        <p>{{ evaluatorInfo.position }} · {{ evaluatorInfo.department }}</p>
        <el-tag type="primary" size="small">考核码: {{ evaluationCode }}</el-tag>
      </div>
      <el-button @click="logout" type="danger" plain>
        <el-icon><SwitchButton /></el-icon>
        退出登录
      </el-button>
    </div>

    <!-- 任务列表 -->
    <div class="tasks-container">
      <div class="tasks-header">
        <h3>我的考核任务</h3>
        <el-tag type="info">共 {{ tasks.length }} 个任务</el-tag>
      </div>

      <div class="tasks-list" v-loading="loading">
        <div 
          v-for="task in tasks" 
          :key="task.id"
          class="task-card"
          :class="{ 'completed': task.status === 'completed' }"
        >
          <div class="task-info">
            <div class="task-header">
              <h4>{{ task.evaluatee_name }}</h4>
              <el-tag :type="getStatusType(task.status)" size="small">
                {{ getStatusText(task.status) }}
              </el-tag>
            </div>
            <div class="task-details">
              <p><strong>职位:</strong> {{ task.evaluatee_position }}</p>
              <p><strong>关系:</strong> {{ getRelationText(task.relation_type) }}</p>
              <p><strong>权重:</strong> {{ task.weight }}</p>
              <p v-if="task.assigned_at">
                <strong>分配时间:</strong> {{ formatDateTime(task.assigned_at) }}
              </p>
            </div>
          </div>
          
          <div class="task-actions">
            <el-button 
              type="primary" 
              @click="startEvaluation(task)"
              :disabled="task.status === 'completed'"
            >
              <el-icon><Edit /></el-icon>
              {{ task.status === 'completed' ? '已完成' : '开始评价' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 评价对话框 -->
    <el-dialog
      v-model="evaluationDialogVisible"
      :title="`评价 ${currentTask?.evaluatee_name}`"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="currentTask" class="evaluation-form">
        <div class="evaluatee-info">
          <h4>{{ currentTask.evaluatee_name }}</h4>
          <p>{{ currentTask.evaluatee_position }} · {{ getRelationText(currentTask.relation_type) }}</p>
        </div>

        <el-form :model="evaluationForm" ref="evaluationFormRef" label-width="120px">
          <div v-for="indicator in indicators" :key="indicator.id" class="indicator-item">
            <el-form-item :label="indicator.name" required>
              <div class="indicator-content">
                <p class="indicator-description">{{ indicator.description }}</p>
                <el-slider
                  v-model="evaluationForm.scores[indicator.id]"
                  :min="0"
                  :max="100"
                  :step="1"
                  show-input
                  :show-input-controls="false"
                  style="width: 300px"
                />
                <span class="score-display">{{ evaluationForm.scores[indicator.id] || 0 }}分</span>
              </div>
            </el-form-item>
          </div>

          <el-form-item label="总体评价">
            <el-input
              v-model="evaluationForm.overallComment"
              type="textarea"
              :rows="4"
              placeholder="请输入对被评价人的总体评价意见..."
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="evaluationDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitEvaluation"
            :loading="submitting"
          >
            提交评价
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElForm } from 'element-plus'
import { SwitchButton, Edit } from '@element-plus/icons-vue'
import { taskApi } from '@/utils/api'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const evaluatorInfo = ref<any>({})
const evaluationCode = ref('')
const tasks = ref<any[]>([])
const indicators = ref<any[]>([])
const existingScores = ref<any>({})

// 评价对话框
const evaluationDialogVisible = ref(false)
const currentTask = ref<any>(null)
const submitting = ref(false)
const evaluationFormRef = ref<InstanceType<typeof ElForm>>()

const evaluationForm = reactive({
  scores: {} as Record<number, number>,
  overallComment: ''
})

// 计算属性
const getStatusText = (status: string) => {
  const map = { 
    pending: '待评价', 
    in_progress: '进行中', 
    completed: '已完成', 
    overdue: '已过期' 
  }
  return map[status as keyof typeof map] || status
}

const getStatusType = (status: string) => {
  const map = { 
    pending: 'warning', 
    in_progress: 'primary', 
    completed: 'success', 
    overdue: 'danger' 
  }
  return map[status as keyof typeof map] || 'info'
}

const getRelationText = (type: string) => {
  const map = { 
    superior: '上级考核下级', 
    peer: '同级互评', 
    subordinate: '下级评价上级',
    self: '自我评价',
    cross_peer: '跨部门同级互评'
  }
  return map[type as keyof typeof map] || type
}

const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 方法
const loadEvaluatorTasks = async () => {
  try {
    loading.value = true
    const code = router.currentRoute.value.query.code as string
    if (!code) {
      ElMessage.error('考核码无效')
      router.push('/evaluation-login')
      return
    }

    evaluationCode.value = code
    const response = await taskApi.getEvaluatorTasks(code)
    
    evaluatorInfo.value = response.data.evaluator
    tasks.value = response.data.tasks
    indicators.value = response.data.indicators
    existingScores.value = response.data.existing_scores || {}
    
  } catch (error: any) {
    console.error('加载考核任务失败:', error)
    if (error.response?.status === 404) {
      ElMessage.error('考核码不存在')
    } else {
      ElMessage.error('加载考核任务失败')
    }
    router.push('/evaluation-login')
  } finally {
    loading.value = false
  }
}

const startEvaluation = (task: any) => {
  currentTask.value = task
  
  // 初始化评价表单
  evaluationForm.scores = {}
  evaluationForm.overallComment = ''
  
  // 如果有已存在的评分，加载到表单中
  if (existingScores.value[task.id]) {
    const taskScores = existingScores.value[task.id]
    indicators.value.forEach(indicator => {
      if (taskScores[indicator.id]) {
        evaluationForm.scores[indicator.id] = taskScores[indicator.id].score
        evaluationForm.overallComment = taskScores[indicator.id].comment || ''
      } else {
        evaluationForm.scores[indicator.id] = 0
      }
    })
  } else {
    // 初始化所有指标为0分
    indicators.value.forEach(indicator => {
      evaluationForm.scores[indicator.id] = 0
    })
  }
  
  evaluationDialogVisible.value = true
}

const submitEvaluation = async () => {
  if (!evaluationFormRef.value || !currentTask.value) return
  
  try {
    await evaluationFormRef.value.validate()
    
    await ElMessageBox.confirm(
      '确认提交评价？提交后将无法修改。',
      '确认提交',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    submitting.value = true
    
    // 提交每个指标的评分
    for (const [indicatorId, score] of Object.entries(evaluationForm.scores)) {
      await taskApi.submitScore({
        task_id: currentTask.value.id,
        indicator_id: parseInt(indicatorId),
        score: score,
        comment: evaluationForm.overallComment
      })
    }
    
    ElMessage.success('评价提交成功！')
    evaluationDialogVisible.value = false
    
    // 重新加载任务列表
    await loadEvaluatorTasks()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('提交评价失败:', error)
      ElMessage.error('提交评价失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

const logout = () => {
  sessionStorage.removeItem('evaluator_info')
  sessionStorage.removeItem('evaluation_code')
  router.push('/evaluation-login')
}

onMounted(() => {
  loadEvaluatorTasks()
})
</script>

<style scoped>
.evaluation-tasks {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
}

.evaluator-header {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.evaluator-info h2 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 24px;
}

.evaluator-info p {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
}

.tasks-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.tasks-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.tasks-list {
  display: grid;
  gap: 15px;
}

.task-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s;
}

.task-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.task-card.completed {
  background: #f0f9ff;
  border-color: #67c23a;
}

.task-info {
  flex: 1;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.task-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
}

.task-details {
  color: #666;
  font-size: 14px;
}

.task-details p {
  margin: 4px 0;
}

.task-actions {
  margin-left: 20px;
}

.evaluation-form {
  max-height: 60vh;
  overflow-y: auto;
}

.evaluatee-info {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.evaluatee-info h4 {
  margin: 0 0 5px 0;
  color: #333;
}

.evaluatee-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.indicator-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
}

.indicator-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.indicator-description {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.score-display {
  font-weight: bold;
  color: #409eff;
  font-size: 16px;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-slider__runway) {
  background-color: #e4e7ed;
}

:deep(.el-slider__bar) {
  background-color: #409eff;
}

:deep(.el-slider__button) {
  border-color: #409eff;
}
</style>