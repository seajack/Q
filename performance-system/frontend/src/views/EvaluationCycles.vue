<template>
  <div class="evaluation-cycles">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>考核周期管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建考核周期
          </el-button>
        </div>
      </template>

      <el-table :data="cycles" v-loading="loading">
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
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="editCycle(row)">编辑</el-button>
            <el-button size="small" type="success" @click="generateTasks(row)">生成任务</el-button>
            <el-button size="small" type="danger" @click="deleteCycle(row)">删除</el-button>
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
        <el-form-item label="周期描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入周期描述"
          />
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
const formRef = ref()

const formData = reactive({
  name: '',
  start_date: '',
  end_date: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入周期名称', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }]
}

const cycles = computed(() => evaluationStore.cycles)
const loading = computed(() => evaluationStore.loading)

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

const showCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editCycle = (cycle: EvaluationCycle) => {
  isEdit.value = true
  formData.name = cycle.name
  formData.start_date = cycle.start_date
  formData.end_date = cycle.end_date
  formData.description = cycle.description
  dialogVisible.value = true
}

const resetForm = () => {
  formData.name = ''
  formData.start_date = ''
  formData.end_date = ''
  formData.description = ''
  formRef.value?.clearValidate()
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    if (isEdit.value) {
      ElMessage.success('更新成功')
    } else {
      await evaluationStore.createCycle(formData)
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

const loadData = async () => {
  try {
    await evaluationStore.fetchCycles()
  } catch (error) {
    console.error('加载考核周期失败:', error)
    ElMessage.error('加载数据失败')
  }
}

onMounted(() => {
  loadData()
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
</style>