<template>
  <div class="evaluation-cycles">
    <div class="page-header">
      <h2 class="page-title">考核周期管理</h2>
      <p class="page-description">创建和管理组织的考核周期，设置考核规则和时间范围</p>
    </div>
    
    <div class="modern-card">
      <div class="card-header-modern">
        <div class="header-left">
          <div class="header-icon">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="header-content">
            <h3>考核周期列表</h3>
            <span class="header-subtitle">{{ cycles.length || 0 }}个周期</span>
          </div>
        </div>
        <div class="header-actions">
          <el-button 
            class="action-button" 
            type="info" 
            plain 
            @click="debugData"
            size="small"
          >
            <el-icon><InfoFilled /></el-icon>
            调试数据
          </el-button>
          <el-button 
            class="action-button create-button" 
            type="primary" 
            @click="showCreateDialog"
          >
            <el-icon><Plus /></el-icon>
            新建考核周期
          </el-button>
        </div>
      </div>

      <el-table 
        :data="cycles" 
        v-loading="loading"
        border
        stripe
        class="modern-table"
        :header-cell-style="{
          background: 'var(--surface-tertiary)',
          color: 'var(--text-primary)',
          fontWeight: 'var(--font-medium)'
        }"
      >
        <template #empty>
          <div class="empty-state">
            <el-icon class="empty-icon"><DocumentRemove /></el-icon>
            <h4>暂无考核周期数据</h4>
            <p>您可以点击"新建考核周期"按钮创建第一个考核周期</p>
            <el-button type="primary" @click="showCreateDialog" class="empty-action">
              <el-icon><Plus /></el-icon>
              创建考核周期
            </el-button>
          </div>
        </template>
        <el-table-column prop="name" label="周期名称" min-width="180" show-overflow-tooltip />
        <el-table-column label="考核时间" min-width="200">
          <template #default="{ row }">
            <div class="date-range">
              <div class="date-item">
                <el-icon><Calendar /></el-icon>
                <span>{{ row.start_date }}</span>
              </div>
              <div class="date-separator">至</div>
              <div class="date-item">
                <el-icon><Calendar /></el-icon>
                <span>{{ row.end_date }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <div class="status-tag-wrapper">
              <el-tag 
                :type="getStatusType(row.status)" 
                :effect="row.status === 'active' ? 'dark' : 'light'"
                class="status-tag"
              >
                <el-icon v-if="row.status === 'active'"><Loading /></el-icon>
                <el-icon v-else-if="row.status === 'completed'"><SuccessFilled /></el-icon>
                <el-icon v-else-if="row.status === 'cancelled'"><CloseBold /></el-icon>
                <el-icon v-else><Edit /></el-icon>
                {{ getStatusText(row.status) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-tooltip content="编辑周期" placement="top" :hide-after="1000">
                <el-button size="small" @click="editCycle(row)" class="action-btn">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
              </el-tooltip>
              <el-tooltip content="生成考核任务" placement="top" :hide-after="1000">
                <el-button size="small" type="success" @click="generateTasks(row)" class="action-btn">
                  <el-icon><DocumentAdd /></el-icon>
                  生成任务
                </el-button>
              </el-tooltip>
              <el-tooltip content="查看任务列表" placement="top" :hide-after="1000">
                <el-button size="small" type="info" @click="viewTasks(row)" class="action-btn">
                  <el-icon><View /></el-icon>
                  查看任务
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除周期" placement="top" :hide-after="1000">
                <el-button size="small" type="danger" @click="deleteCycle(row)" class="action-btn">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      :title="isEdit ? '编辑考核周期' : '新建考核周期'"
      v-model="dialogVisible"
      width="600px"
      destroy-on-close
      class="modern-dialog"
    >
      <div class="dialog-header-icon" v-if="!isEdit">
        <el-icon class="dialog-icon"><Calendar /></el-icon>
      </div>
      <div class="dialog-header-icon edit-icon" v-else>
        <el-icon class="dialog-icon"><EditPen /></el-icon>
      </div>
      
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px" class="modern-form">
        <el-form-item label="周期名称" prop="name">
          <el-input 
            v-model="formData.name" 
            placeholder="请输入周期名称"
            prefix-icon="Document"
          />
        </el-form-item>
        
        <div class="date-form-group">
          <el-form-item label="开始日期" prop="start_date">
            <el-date-picker
              v-model="formData.start_date"
              type="date"
              placeholder="选择开始日期"
              style="width: 100%"
              prefix-icon="Calendar"
            />
          </el-form-item>
          <el-form-item label="结束日期" prop="end_date">
            <el-date-picker
              v-model="formData.end_date"
              type="date"
              placeholder="选择结束日期"
              style="width: 100%"
              prefix-icon="Calendar"
            />
          </el-form-item>
        </div>
        
        <el-form-item label="考核规则" prop="evaluation_rule">
          <el-select 
            v-model="formData.evaluation_rule" 
            placeholder="请选择考核规则" 
            style="width: 100%"
            :loading="rulesLoading"
            prefix-icon="Setting"
          >
            <el-option
              v-for="rule in activeRules"
              :key="rule.id"
              :label="rule.name"
              :value="rule.id"
            >
              <div class="rule-option">
                <span class="rule-name">{{ rule.name }}</span>
                <span class="rule-description">{{ rule.description }}</span>
              </div>
            </el-option>
          </el-select>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            选择用于该考核周期的规则，将根据规则自动生成考核任务
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" class="cancel-btn">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting" class="submit-btn">
            <el-icon v-if="!submitting"><Check /></el-icon>
            <span>{{ isEdit ? '保存修改' : '创建周期' }}</span>
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
  InfoFilled, 
  Edit, 
  Delete, 
  View, 
  DocumentAdd, 
  DocumentRemove,
  Loading,
  SuccessFilled,
  CloseBold,
  Check,
  EditPen,
  Document,
  Setting
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
  padding: var(--spacing-6);
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面标题样式 */
.page-header {
  margin-bottom: var(--spacing-6);
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--spacing-2);
}

.page-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

/* 卡片样式 */
.modern-card {
  background: var(--surface-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  transition: all var(--duration-normal) var(--ease-out);
  border: 1px solid var(--border-subtle);
  margin-bottom: var(--spacing-6);
}

.card-header-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-5) var(--spacing-6);
  border-bottom: 1px solid var(--border-subtle);
  background: linear-gradient(to right, var(--surface-secondary), var(--surface-primary));
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.header-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  background: var(--brand-primary-50);
  color: var(--brand-primary-600);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.header-content h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  margin: 0;
  color: var(--text-primary);
}

.header-subtitle {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.header-actions {
  display: flex;
  gap: var(--spacing-3);
}

.action-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  transition: all var(--duration-fast) var(--ease-out);
}

.create-button {
  background: linear-gradient(135deg, var(--brand-primary-600) 0%, var(--brand-primary-700) 100%);
  border: none;
  box-shadow: var(--shadow-sm);
}

.create-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* 表格样式 */
.modern-table {
  width: 100%;
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
  overflow: hidden;
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-12);
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  color: var(--text-quaternary);
  margin-bottom: var(--spacing-4);
}

.empty-state h4 {
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--spacing-2);
}

.empty-state p {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin-bottom: var(--spacing-6);
  max-width: 300px;
}

.empty-action {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

/* 状态标签样式 */
.status-tag-wrapper {
  display: flex;
  justify-content: flex-start;
}

.status-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

/* 日期范围样式 */
.date-range {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.date-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--text-sm);
}

.date-separator {
  font-size: var(--text-xs);
  color: var(--text-quaternary);
  margin-left: var(--spacing-4);
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  gap: var(--spacing-2);
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-xs);
  border-radius: var(--radius-md);
  padding: 6px 10px;
  transition: all var(--duration-fast) var(--ease-out);
}

.action-btn:hover {
  transform: translateY(-2px);
}

/* 对话框样式 */
.modern-dialog :deep(.el-dialog__header) {
  padding: var(--spacing-6) var(--spacing-6) 0;
  text-align: center;
  position: relative;
}

.modern-dialog :deep(.el-dialog__title) {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.modern-dialog :deep(.el-dialog__body) {
  padding: var(--spacing-6);
}

.dialog-header-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand-primary-500) 0%, var(--brand-primary-600) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--spacing-4);
  box-shadow: var(--shadow-md);
}

.edit-icon {
  background: linear-gradient(135deg, var(--semantic-warning-500) 0%, var(--semantic-warning-600) 100%);
}

.dialog-icon {
  font-size: 24px;
}

/* 表单样式 */
.modern-form {
  margin-top: var(--spacing-4);
}

.date-form-group {
  display: flex;
  gap: var(--spacing-4);
}

.date-form-group .el-form-item {
  flex: 1;
}

.form-tip {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-top: var(--spacing-2);
  line-height: 1.4;
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
}

.rule-option {
  display: flex;
  flex-direction: column;
}

.rule-name {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.rule-description {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-top: 2px;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  gap: var(--spacing-4);
  padding-top: var(--spacing-2);
}

.cancel-btn {
  min-width: 100px;
}

.submit-btn {
  min-width: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  background: linear-gradient(135deg, var(--brand-primary-600) 0%, var(--brand-primary-700) 100%);
  border: none;
}
</style>