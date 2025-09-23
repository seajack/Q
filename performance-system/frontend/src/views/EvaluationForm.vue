<template>
  <div class="evaluation-form">
    <el-card>
      <template #header>
        <span>考核评分 - {{ task?.evaluatee_name }}</span>
      </template>
      
      <div v-if="task" class="evaluation-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="考核码">{{ task.evaluation_code }}</el-descriptions-item>
          <el-descriptions-item label="被考核人">{{ task.evaluatee_name }}</el-descriptions-item>
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
          <el-button type="primary" size="large" @click="submitEvaluation">
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
import { useEvaluationStore } from '@/stores/evaluation'

const props = defineProps<{
  code: string
}>()

const route = useRoute()
const router = useRouter()
const evaluationStore = useEvaluationStore()

const task = ref(null)
const indicators = ref([])
const scoreForm = reactive({})
const commentForm = reactive({})

const getRelationText = (type: string) => {
  const map = {
    'superior': '上级考核下级',
    'peer': '同级互评', 
    'subordinate': '下级评价上级'
  }
  return map[type as keyof typeof map] || type
}

const submitEvaluation = async () => {
  try {
    ElMessage.success('评分提交成功')
    router.push('/dashboard')
  } catch (error) {
    ElMessage.error('提交失败，请重试')
  }
}

onMounted(async () => {
  try {
    // 这里应该根据考核码获取任务和指标
    // task.value = await evaluationStore.getTaskByCode(props.code)
    // indicators.value = await evaluationStore.fetchIndicators()
  } catch (error) {
    console.error('加载考核任务失败:', error)
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