<template>
  <div class="evaluation-form">
    <el-card v-loading="loading">
      <template #header>
        <span>考核评分 - {{ task?.evaluatee_name }}</span>
      </template>
      
      <div v-if="task" class="evaluation-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="考核码">{{ task.evaluation_code }}</el-descriptions-item>
          <el-descriptions-item label="被考核人">
            {{ task.evaluatee_name }}
            <span v-if="task.evaluatee_position" class="position-info">
              ({{ task.evaluatee_position }})
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="考核关系">{{ getRelationText(task.relation_type) }}</el-descriptions-item>
          <el-descriptions-item label="考核权重">{{ task.weight }}</el-descriptions-item>
        </el-descriptions>

        <div class="indicators-section">
          <h3>考核指标</h3>
          <el-form :model="scoreForm" label-width="120px">
            <div v-for="indicator in indicators" :key="indicator.id" class="indicator-item">
              <el-form-item :label="indicator.name">
                <el-rate 
                  v-model="scoreForm[indicator.id]"
                  :max="5"
                  allow-half
                  show-score
                  text-color="#ff9900"
                />
                <el-input
                  v-model="commentForm[indicator.id]"
                  type="textarea"
                  placeholder="请输入评价意见"
                  :rows="2"
                  style="margin-top: 10px"
                />
              </el-form-item>
            </div>
          </el-form>
        </div>

        <div class="submit-section">
          <el-button 
            type="primary" 
            size="large" 
            @click="submitEvaluation"
            :loading="loading"
            :disabled="loading"
          >
            提交评分
          </el-button>
          <el-button size="large" @click="$router.go(-1)">
            返回
          </el-button>
        </div>
      </div>
      
      <div v-else class="error-content">
        <el-result icon="error" title="考核任务不存在" sub-title="请检查考核码是否正确">
          <template #extra>
            <el-button type="primary" @click="$router.push('/dashboard')">返回首页</el-button>
          </template>
        </el-result>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { taskApi, scoreApi } from '@/utils/api'
import type { EvaluationTask, EvaluationIndicator } from '@/types'

const props = defineProps<{
  code: string
}>()

const route = useRoute()
const router = useRouter()

const task = ref<EvaluationTask | null>(null)
const indicators = ref<EvaluationIndicator[]>([])
const scoreForm = reactive<Record<number, number>>({})
const commentForm = reactive<Record<number, string>>({})
const loading = ref(false)

const getRelationText = (type: string) => {
  const map = {
    'superior': '上级考核下级',
    'peer': '同级互评', 
    'subordinate': '下级评价上级'
  }
  return map[type as keyof typeof map] || type
}

const submitEvaluation = async () => {
  if (!task.value) {
    ElMessage.error('考核任务不存在')
    return
  }
  
  try {
    loading.value = true
    
    // 准备评分数据
    const scores = indicators.value.map(indicator => ({
      indicator_id: indicator.id,
      score: Math.round((scoreForm[indicator.id] || 0) * 20), // 将星级评分(1-5)转换为百分制(0-100)
      comment: commentForm[indicator.id] || ''
    })).filter(score => score.score > 0) // 只提交有评分的指标
    
    if (scores.length === 0) {
      ElMessage.warning('请至少对一个指标进行评分')
      return
    }
    
    await scoreApi.submitTaskScores({
      task_id: task.value.id,
      scores: scores
    })
    ElMessage.success('评分提交成功')
    
    // 检查是否还有其他未完成的任务
    const evaluationCode = sessionStorage.getItem('evaluationCode')
    if (evaluationCode) {
      try {
        const response = await taskApi.getEvaluatorTasks(evaluationCode)
        const allTasks = response.data.tasks || []
        const pendingTasks = allTasks.filter((t: any) => t.status === 'pending' || t.status === 'in_progress')
        
        if (pendingTasks.length > 0) {
          // 还有未完成的任务，返回任务列表页面
          router.push('/evaluation')
        } else {
          // 所有任务都已完成，跳转到仪表板
          router.push('/dashboard')
        }
      } catch (error) {
        console.error('检查任务状态失败:', error)
        // 出错时默认返回任务列表页面
        router.push('/evaluation')
      }
    } else {
      // 没有考核码，跳转到仪表板
      router.push('/dashboard')
    }
  } catch (error) {
    console.error('提交评分失败:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const taskId = route.params.id as string
  
  if (!taskId) {
    ElMessage.error('缺少任务ID参数')
    router.push('/dashboard')
    return
  }
  
  try {
    loading.value = true
    const response = await taskApi.getByTaskId(parseInt(taskId))
    
    task.value = response.data.task
    indicators.value = response.data.indicators
    
    // 初始化表单数据，如果有已存在的评分则填入
    const existingScores = response.data.existing_scores || {}
    indicators.value.forEach(indicator => {
      const existingScore = existingScores[indicator.id.toString()]
      if (existingScore) {
        scoreForm[indicator.id] = existingScore.score / 20 // 转换为星级评分
        commentForm[indicator.id] = existingScore.comment
      } else {
        scoreForm[indicator.id] = 0
        commentForm[indicator.id] = ''
      }
    })
    
  } catch (error: any) {
    console.error('加载考核任务失败:', error)
    if (error.response?.status === 404) {
      ElMessage.error('考核任务不存在，请检查考核码是否正确')
    } else {
      ElMessage.error('加载失败，请重试')
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.evaluation-form {
  padding: 20px;
}

.evaluation-content {
  margin-top: 20px;
}

.position-info {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

.indicators-section {
  margin: 30px 0;
}

.indicator-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.submit-section {
  text-align: center;
  margin-top: 30px;
}

.error-content {
  text-align: center;
  padding: 50px 0;
}
</style>