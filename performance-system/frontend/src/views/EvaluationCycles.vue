<template>
  <div class="evaluation-cycles">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>考核周期管理</span>
          <div style="display: flex; gap: 8px;">
            <el-button type="info" @click="debugData">调试数据</el-button>
            <el-button type="primary" @click="showCreateDialog">
              <el-icon><Plus /></el-icon>
              新建考核周期
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="cycles" v-loading="loading">
        <template #empty>
          <div style="text-align: center; padding: 20px;">
            <p>暂无考核周期数据</p>
            <p>请先创建考核周期</p>
          </div>
        </template>
        <el-table-column prop="name" label="周期名称" />
        <el-table-column prop="start_date" label="开始日期" />
        <el-table-column prop="end_date" label="结束日期" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <el-button size="small" @click="editCycle(row)" style="display: inline-block !important;">编辑</el-button>
              <el-button size="small" type="success" @click="generateTasks(row)" style="display: inline-block !important;">生成任务</el-button>
              <el-button size="small" type="info" @click="viewTasks(row)" style="display: inline-block !important;">查看任务</el-button>
              <el-button size="small" type="danger" @click="deleteCycle(row)" style="display: inline-block !important;">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      :title="isEdit ? '编辑考核周期' : '新建考核周期'"
      v-model="dialogVisible"
      width="600px"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="周期名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入周期名称" />
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="formData.start_date"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="formData.end_date"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="考核规则" prop="evaluation_rule">
          <el-select 
            v-model="formData.evaluation_rule" 
            placeholder="请选择考核规则" 
            style="width: 100%"
            :loading="rulesLoading"
          >
            <el-option
              v-for="rule in activeRules"
              :key="rule.id"
              :label="rule.name"
              :value="rule.id"
            >
              <div>
                <span>{{ rule.name }}</span>
                <span style="color: #8492a6; font-size: 12px; margin-left: 8px">{{ rule.description }}</span>
              </div>
            </el-option>
          </el-select>
          <div class="form-tip">
            选择用于该考核周期的规则，将根据规则自动生成考核任务
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useEvaluationStore } from '@/stores/evaluation'
import type { EvaluationCycle } from '@/types'

const evaluationStore = useEvaluationStore()

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const rulesLoading = ref(false)
const formRef = ref()
const currentCycle = ref<EvaluationCycle | null>(null)

const formData = reactive({
  name: '',
  start_date: '',
  end_date: '',
  description: '',
  evaluation_rule: null as number | null
})

const rules = {
  name: [{ required: true, message: '请输入周期名称', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  evaluation_rule: [{ required: true, message: '请选择考核规则', trigger: 'change' }]
}

const cycles = computed(() => evaluationStore.cycles)
const loading = computed(() => evaluationStore.loading)
const evaluationRules = computed(() => evaluationStore.evaluationRules)
const activeRules = computed(() => evaluationRules.value.filter(rule => rule.is_active))

const getStatusType = (status: string) => {
  const statusMap = {
    'draft': 'info',
    'active': 'success',
    'completed': 'warning',
    'cancelled': 'danger'
  }
  return statusMap[status as keyof typeof statusMap] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap = {
    'draft': '草稿',
    'active': '进行中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const showCreateDialog = async () => {
  isEdit.value = false
  currentCycle.value = null
  resetForm()
  dialogVisible.value = true
  await loadRules()
}

const editCycle = async (cycle: EvaluationCycle) => {
  isEdit.value = true
  currentCycle.value = cycle
  formData.name = cycle.name
  formData.start_date = cycle.start_date
  formData.end_date = cycle.end_date
  formData.description = cycle.description
  formData.evaluation_rule = cycle.evaluation_rule || null
  dialogVisible.value = true
  await loadRules()
}

const resetForm = () => {
  formData.name = ''
  formData.start_date = ''
  formData.end_date = ''
  formData.description = ''
  formData.evaluation_rule = null
  formRef.value?.clearValidate()
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    // 格式化日期为字符串
    const submitData = {
      ...formData,
      start_date: formData.start_date instanceof Date 
        ? formData.start_date.toISOString().split('T')[0] 
        : formData.start_date,
      end_date: formData.end_date instanceof Date 
        ? formData.end_date.toISOString().split('T')[0] 
        : formData.end_date
    }
    
    if (isEdit.value && currentCycle.value) {
      await evaluationStore.updateCycle(currentCycle.value.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await evaluationStore.createCycle(submitData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    await loadData()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

const generateTasks = async (cycle: EvaluationCycle) => {
  try {
    await ElMessageBox.confirm(
      `确定要为"${cycle.name}"生成考核任务吗？`,
      '确认生成',
      { type: 'warning' }
    )
    
    await evaluationStore.generateTasksForCycle(cycle.id)
    ElMessage.success('考核任务生成成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('生成任务失败:', error)
      ElMessage.error('生成任务失败，请重试')
    }
  }
}

const viewTasks = (cycle: EvaluationCycle) => {
  // 跳转到评审任务页面，并筛选该周期的任务
  window.open(`/tasks?cycle=${cycle.id}`, '_blank')
}

const debugData = () => {
  console.log('=== 调试数据 ===')
  console.log('cycles.value:', cycles.value)
  console.log('cycles.length:', cycles.value.length)
  console.log('loading.value:', loading.value)
  console.log('evaluationStore:', evaluationStore)
  
  ElMessageBox.alert(
    `数据调试信息：\n` +
    `考核周期数量: ${cycles.value.length}\n` +
    `加载状态: ${loading.value}\n` +
    `数据: ${JSON.stringify(cycles.value, null, 2)}`,
    '调试信息',
    { type: 'info' }
  )
}

const deleteCycle = async (cycle: EvaluationCycle) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除考核周期"${cycle.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await evaluationStore.deleteCycle(cycle.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

const loadRules = async () => {
  try {
    rulesLoading.value = true
    await evaluationStore.fetchEvaluationRules()
  } catch (error) {
    console.error('加载考核规则失败:', error)
  } finally {
    rulesLoading.value = false
  }
}

const loadData = async () => {
  try {
    console.log('开始加载考核周期数据...')
    await evaluationStore.fetchCycles()
    console.log('考核周期数据加载完成:', cycles.value)
    console.log('数据长度:', cycles.value.length)
  } catch (error) {
    console.error('加载考核周期失败:', error)
    ElMessage.error('加载数据失败')
  }
}

onMounted(() => {
  console.log('考核周期页面加载中...')
  loadData()
  console.log('考核周期数据:', cycles.value)
})
</script>

<style scoped>
.evaluation-cycles {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}
</style>