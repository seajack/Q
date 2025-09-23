<template>
  <div class="evaluation-indicators">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>考核指标管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建指标
          </el-button>
        </div>
      </template>

      <el-table :data="indicators" v-loading="loading">
        <el-table-column prop="name" label="指标名称" />
        <el-table-column prop="category" label="指标类别">
          <template #default="{ row }">
            <el-tag>{{ getCategoryText(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="指标描述" show-overflow-tooltip />
        <el-table-column prop="weight" label="权重" width="100">
          <template #default="{ row }">
            {{ (row.weight * 100).toFixed(0) }}%
          </template>
        </el-table-column>
        <el-table-column prop="max_score" label="最高分数" width="100" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="editIndicator(row)">编辑</el-button>
            <el-button 
              size="small" 
              :type="row.is_active ? 'warning' : 'success'"
              @click="toggleStatus(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" type="danger" @click="deleteIndicator(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      :title="isEdit ? '编辑考核指标' : '新建考核指标'"
      v-model="dialogVisible"
      width="600px"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="指标名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入指标名称" />
        </el-form-item>
        <el-form-item label="指标类别" prop="category">
          <el-select v-model="formData.category" placeholder="请选择指标类别" style="width: 100%">
            <el-option
              v-for="item in categoryOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="指标描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入指标描述"
          />
        </el-form-item>
        <el-form-item label="权重" prop="weight">
          <el-input-number
            v-model="formData.weight"
            :min="0.01"
            :max="1"
            :step="0.01"
            :precision="2"
            style="width: 100%"
          />
          <div class="form-tip">权重范围：0.01 - 1.00，表示该指标在整体评价中的比重</div>
        </el-form-item>
        <el-form-item label="最高分数" prop="max_score">
          <el-input-number
            v-model="formData.max_score"
            :min="1"
            :max="200"
            style="width: 100%"
          />
          <div class="form-tip">该指标的最高得分，通常为100分</div>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="formData.is_active"
            active-text="启用"
            inactive-text="禁用"
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useEvaluationStore } from '@/stores/evaluation'
import type { EvaluationIndicator } from '@/types'

const evaluationStore = useEvaluationStore()

// 响应式变量
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref()
const currentIndicator = ref<EvaluationIndicator | null>(null)

// 表单数据
const formData = reactive({
  name: '',
  category: '',
  description: '',
  weight: 0.1,
  max_score: 100,
  is_active: true
})

const categoryOptions = [
  { label: '工作绩效', value: 'performance' },
  { label: '工作能力', value: 'ability' },
  { label: '工作态度', value: 'attitude' },
  { label: '团队合作', value: 'teamwork' },
  { label: '创新能力', value: 'innovation' }
]

const rules = {
  name: [{ required: true, message: '请输入指标名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择指标类别', trigger: 'change' }],
  description: [{ required: true, message: '请输入指标描述', trigger: 'blur' }],
  weight: [
    { required: true, message: '请输入权重', trigger: 'blur' },
    { type: 'number', min: 0.01, max: 1, message: '权重必须在 0.01 到 1 之间', trigger: 'blur' }
  ],
  max_score: [
    { required: true, message: '请输入最高分数', trigger: 'blur' },
    { type: 'number', min: 1, max: 200, message: '最高分数必须在 1 到 200 之间', trigger: 'blur' }
  ]
}

const indicators = computed(() => evaluationStore.indicators)
const loading = computed(() => evaluationStore.loading)

const getCategoryText = (category: string) => {
  const categoryMap = {
    'performance': '工作绩效',
    'ability': '工作能力',
    'attitude': '工作态度',
    'teamwork': '团队合作',
    'innovation': '创新能力'
  }
  return categoryMap[category as keyof typeof categoryMap] || category
}

const showCreateDialog = () => {
  isEdit.value = false
  currentIndicator.value = null
  resetForm()
  dialogVisible.value = true
}

const editIndicator = (indicator: EvaluationIndicator) => {
  isEdit.value = true
  currentIndicator.value = indicator
  formData.name = indicator.name
  formData.category = indicator.category
  formData.description = indicator.description
  // 确保数值类型转换
  formData.weight = typeof indicator.weight === 'string' ? parseFloat(indicator.weight) : indicator.weight
  formData.max_score = typeof indicator.max_score === 'string' ? parseInt(indicator.max_score) : indicator.max_score
  formData.is_active = indicator.is_active
  dialogVisible.value = true
}

const resetForm = () => {
  formData.name = ''
  formData.category = ''
  formData.description = ''
  formData.weight = 0.1
  formData.max_score = 100
  formData.is_active = true
  formRef.value?.clearValidate()
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    if (isEdit.value && currentIndicator.value) {
      await evaluationStore.updateIndicator(currentIndicator.value.id, formData)
      ElMessage.success('更新成功')
    } else {
      await evaluationStore.createIndicator(formData)
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

const toggleStatus = async (indicator: EvaluationIndicator) => {
  try {
    const newStatus = !indicator.is_active
    const updateData = {
      name: indicator.name,
      category: indicator.category,
      description: indicator.description,
      weight: typeof indicator.weight === 'string' ? parseFloat(indicator.weight) : indicator.weight,
      max_score: typeof indicator.max_score === 'string' ? parseInt(indicator.max_score) : indicator.max_score,
      is_active: newStatus
    }
    await evaluationStore.updateIndicator(indicator.id, updateData)
    ElMessage.success(`${newStatus ? '启用' : '禁用'}成功`)
    await loadData()
  } catch (error) {
    console.error('状态更新失败:', error)
    ElMessage.error('操作失败，请重试')
  }
}

const deleteIndicator = async (indicator: EvaluationIndicator) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除指标“${indicator.name}”吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await evaluationStore.deleteIndicator(indicator.id)
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
    await evaluationStore.fetchIndicators()
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.evaluation-indicators {
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
}
</style>