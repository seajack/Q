<template>
  <div class="evaluation-cycles">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <el-icon class="title-icon"><Calendar /></el-icon>
            考核周期管理
          </h1>
          <p class="page-subtitle">管理和配置绩效考核周期，设置考核规则和指标</p>
        </div>
        <div class="header-actions">
          <el-button @click="debugData" class="debug-btn">
            <el-icon><Setting /></el-icon>
            调试数据
          </el-button>
          <el-button type="primary" @click="showCreateDialog" class="create-btn">
            <el-icon><Plus /></el-icon>
            新建考核周期
          </el-button>
        </div>
      </div>
    </div>

    <!-- 数据表格区域 -->
    <div class="table-section">
      <div class="table-container">
        <el-table 
          :data="cycles" 
          v-loading="loading" 
          class="cycles-table"
          :empty-text="loading ? '加载中...' : '暂无考核周期数据'"
        >
          <template #empty>
            <div class="empty-state">
              <el-icon class="empty-icon"><Calendar /></el-icon>
              <p class="empty-text">暂无考核周期数据</p>
              <p class="empty-subtitle">点击上方"新建考核周期"按钮开始创建</p>
            </div>
          </template>
          
          <el-table-column prop="name" label="周期名称" min-width="180" show-overflow-tooltip>
            <template #default="{ row }">
              <div class="cycle-name">
                <el-icon class="name-icon"><Calendar /></el-icon>
                <span class="name-text">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.description" class="description-text">{{ row.description }}</span>
              <span v-else class="no-description">暂无描述</span>
            </template>
          </el-table-column>
          
          <el-table-column label="时间范围" width="180">
            <template #default="{ row }">
              <div class="time-range">
                <div class="start-date">
                  <el-icon class="date-icon"><Calendar /></el-icon>
                  <span>{{ row.start_date }}</span>
                </div>
                <div class="end-date">
                  <el-icon class="date-icon"><Calendar /></el-icon>
                  <span>{{ row.end_date }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag 
                :type="getStatusType(row.status)" 
                :class="`status-tag status-${row.status}`"
                effect="light"
              >
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="考核规则" width="160" show-overflow-tooltip>
            <template #default="{ row }">
              <div class="rule-info">
                <el-icon v-if="row.evaluation_rule_name" class="rule-icon"><Setting /></el-icon>
                <span v-if="row.evaluation_rule_name" class="rule-name">{{ row.evaluation_rule_name }}</span>
                <span v-else class="no-rule">未设置</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="320" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button 
                  size="small" 
                  @click="editCycle(row)"
                  class="action-btn edit-btn"
                >
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="success" 
                  @click="generateTasks(row)"
                  class="action-btn generate-btn"
                >
                  <el-icon><Plus /></el-icon>
                  生成任务
                </el-button>
                <el-button 
                  size="small" 
                  type="info" 
                  @click="viewTasks(row)"
                  class="action-btn tasks-btn"
                >
                  <el-icon><List /></el-icon>
                  查看任务
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="deleteCycle(row)"
                  class="action-btn delete-btn"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑考核周期' : '新建考核周期'" 
      width="600px"
      class="cycle-dialog"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px" class="cycle-form">
        <el-form-item label="周期名称" prop="name" required>
          <el-input 
            v-model="formData.name" 
            placeholder="请输入考核周期名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="周期描述">
          <el-input 
            v-model="formData.description" 
            type="textarea"
            placeholder="请输入考核周期描述（可选）"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="开始日期" prop="start_date" required>
          <el-date-picker 
            v-model="formData.start_date" 
            type="date" 
            placeholder="选择开始日期"
            style="width: 100%"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="结束日期" prop="end_date" required>
          <el-date-picker 
            v-model="formData.end_date" 
            type="date" 
            placeholder="选择结束日期"
            style="width: 100%"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="考核规则" prop="evaluation_rule" required>
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
              :disabled="!rule.is_active"
            >
              <div class="rule-option">
                <span class="rule-name">{{ rule.name }}</span>
                <span class="rule-desc">{{ rule.description }}</span>
              </div>
            </el-option>
          </el-select>
          <div class="form-tip">
            选择用于该考核周期的规则，将根据规则自动生成考核任务
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" size="large">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitForm" 
            size="large"
            :loading="submitting"
          >
            {{ isEdit ? '保存' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Calendar, 
  Setting, 
  Edit, 
  List, 
  Delete 
} from '@element-plus/icons-vue'
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