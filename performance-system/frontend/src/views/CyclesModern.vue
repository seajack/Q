<template>
  <div class="cycles-modern">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-background"></div>
      <div class="header-content">
        <div class="header-left">
          <div class="page-icon">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="page-info">
            <h1 class="page-title">考核周期管理</h1>
            <p class="page-subtitle">创建和管理绩效考核周期，设置考核规则和时间范围</p>
            <div class="stats-overview">
              <div class="stat-item">
                <span class="stat-value">{{ totalCycles }}</span>
                <span class="stat-label">总周期数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ activeCycles }}</span>
                <span class="stat-label">进行中</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ completedCycles }}</span>
                <span class="stat-label">已完成</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ draftCycles }}</span>
                <span class="stat-label">草稿</span>
              </div>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <el-button 
            class="action-btn secondary" 
            @click="refreshData"
            :loading="loading"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button 
            class="action-btn primary" 
            @click="showCreateDialog"
          >
            <el-icon><Plus /></el-icon>
            新建考核周期
          </el-button>
        </div>
      </div>
    </div>


    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <div class="filter-container">
        <div class="filter-left">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索考核周期..."
            class="search-input"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="statusFilter"
            placeholder="状态筛选"
            class="status-filter"
            clearable
            @change="handleFilter"
          >
            <el-option label="全部状态" value="" />
            <el-option label="草稿" value="draft" />
            <el-option label="进行中" value="active" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </div>
        <div class="filter-right">
          <el-button-group>
            <el-button 
              :type="viewMode === 'card' ? 'primary' : ''"
              @click="viewMode = 'card'"
            >
              <el-icon><Grid /></el-icon>
              卡片视图
            </el-button>
            <el-button 
              :type="viewMode === 'table' ? 'primary' : ''"
              @click="viewMode = 'table'"
            >
              <el-icon><List /></el-icon>
              列表视图
            </el-button>
          </el-button-group>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-section">
      <!-- 卡片视图 -->
      <div v-if="viewMode === 'card'" class="cards-container">
        <div 
          v-for="cycle in filteredCycles" 
          :key="cycle.id"
          class="cycle-card"
          :class="`status-${cycle.status}`"
        >
          <div class="card-header">
            <div class="card-title">
              <el-icon class="title-icon"><Calendar /></el-icon>
              <span>{{ cycle.name }}</span>
            </div>
            <div class="card-status">
              <el-tag 
                :type="getStatusType(cycle.status)"
                effect="light"
                class="status-tag"
              >
                {{ getStatusText(cycle.status) }}
              </el-tag>
            </div>
          </div>
          
          <div class="card-content">
            <div class="card-description" v-if="cycle.description">
              {{ cycle.description }}
            </div>
            <div class="card-dates">
              <div class="date-item">
                <el-icon><Calendar /></el-icon>
                <span>开始：{{ cycle.start_date }}</span>
              </div>
              <div class="date-item">
                <el-icon><Calendar /></el-icon>
                <span>结束：{{ cycle.end_date }}</span>
              </div>
            </div>
            <div class="card-rule" v-if="cycle.evaluation_rule_name">
              <el-icon><Setting /></el-icon>
              <span>{{ cycle.evaluation_rule_name }}</span>
            </div>
          </div>
          
          <div class="card-actions">
            <el-button 
              size="small" 
              @click="editCycle(cycle)"
              class="action-btn edit"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="success"
              @click="generateTasks(cycle)"
              class="action-btn generate"
            >
              <el-icon><Plus /></el-icon>
              生成任务
            </el-button>
            <el-button 
              size="small" 
              type="info"
              @click="viewTasks(cycle)"
              class="action-btn view"
            >
              <el-icon><List /></el-icon>
              查看任务
            </el-button>
            <el-button 
              size="small" 
              type="danger"
              @click="deleteCycle(cycle)"
              class="action-btn delete"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 表格视图 -->
      <div v-else class="table-container">
        <el-table 
          :data="filteredCycles" 
          v-loading="loading"
          class="cycles-table"
          :empty-text="loading ? '加载中...' : '暂无考核周期数据'"
          stripe
        >
          <template #empty>
            <div class="empty-state">
              <el-icon class="empty-icon"><Calendar /></el-icon>
              <p class="empty-text">暂无考核周期数据</p>
              <p class="empty-subtitle">点击上方"新建考核周期"按钮开始创建</p>
            </div>
          </template>
          
          <el-table-column prop="name" label="周期名称" min-width="200">
            <template #default="{ row }">
              <div class="cycle-name">
                <el-icon class="name-icon"><Calendar /></el-icon>
                <span class="name-text">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.description" class="description-text">{{ row.description }}</span>
              <span v-else class="no-description">暂无描述</span>
            </template>
          </el-table-column>
          
          <el-table-column label="时间范围" width="200">
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
          
          <el-table-column prop="status" label="状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag 
                :type="getStatusType(row.status)"
                effect="light"
                class="status-tag"
              >
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="考核规则" width="180" show-overflow-tooltip>
            <template #default="{ row }">
              <div class="rule-info">
                <el-icon v-if="row.evaluation_rule_name" class="rule-icon"><Setting /></el-icon>
                <span v-if="row.evaluation_rule_name" class="rule-name">{{ row.evaluation_rule_name }}</span>
                <span v-else class="no-rule">未设置</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="300" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button 
                  size="small" 
                  @click="editCycle(row)"
                  class="action-btn edit"
                >
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="success"
                  @click="generateTasks(row)"
                  class="action-btn generate"
                >
                  <el-icon><Plus /></el-icon>
                  生成任务
                </el-button>
                <el-button 
                  size="small" 
                  type="info"
                  @click="viewTasks(row)"
                  class="action-btn view"
                >
                  <el-icon><List /></el-icon>
                  查看任务
                </el-button>
                <el-button 
                  size="small" 
                  type="danger"
                  @click="deleteCycle(row)"
                  class="action-btn delete"
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
  Delete,
  Refresh,
  Search,
  Grid,
  VideoPlay,
  Check
} from '@element-plus/icons-vue'
import { useEvaluationStore } from '@/stores/evaluation'
import type { EvaluationCycle } from '@/types'

const evaluationStore = useEvaluationStore()

// 响应式数据
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const rulesLoading = ref(false)
const formRef = ref()
const currentCycle = ref<EvaluationCycle | null>(null)
const searchKeyword = ref('')
const statusFilter = ref('')
const viewMode = ref<'card' | 'table'>('card')

// 表单数据
const formData = reactive({
  name: '',
  start_date: '',
  end_date: '',
  description: '',
  evaluation_rule: null as number | null
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入周期名称', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  evaluation_rule: [{ required: true, message: '请选择考核规则', trigger: 'change' }]
}

// 计算属性
const cycles = computed(() => evaluationStore.cycles)
const evaluationRules = computed(() => evaluationStore.evaluationRules)
const activeRules = computed(() => evaluationRules.value.filter(rule => rule.is_active))

// 统计数据
const totalCycles = computed(() => cycles.value.length)
const activeCycles = computed(() => cycles.value.filter(c => c.status === 'active').length)
const completedCycles = computed(() => cycles.value.filter(c => c.status === 'completed').length)
const draftCycles = computed(() => cycles.value.filter(c => c.status === 'draft').length)

// 筛选后的数据
const filteredCycles = computed(() => {
  let result = cycles.value

  // 搜索筛选
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(cycle => 
      cycle.name.toLowerCase().includes(keyword) ||
      (cycle.description && cycle.description.toLowerCase().includes(keyword))
    )
  }

  // 状态筛选
  if (statusFilter.value) {
    result = result.filter(cycle => cycle.status === statusFilter.value)
  }

  return result
})

// 方法
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
  formData.description = cycle.description || ''
  formData.evaluation_rule = (cycle as any).evaluation_rule || null
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
    
    const submitData = {
      ...formData,
      start_date: typeof formData.start_date === 'string' 
        ? formData.start_date 
        : formData.start_date,
      end_date: typeof formData.end_date === 'string' 
        ? formData.end_date 
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
  window.open(`/tasks?cycle=${cycle.id}`, '_blank')
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
    loading.value = true
    console.log('开始加载考核周期数据...')
    await evaluationStore.fetchCycles()
    console.log('考核周期数据加载完成:', cycles.value)
  } catch (error) {
    console.error('加载考核周期失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  await loadData()
}

const handleSearch = () => {
  // 搜索逻辑已在计算属性中处理
}

const handleFilter = () => {
  // 筛选逻辑已在计算属性中处理
}

onMounted(() => {
  console.log('考核周期页面加载中...')
  loadData()
})
</script>

<style scoped>
/* 页面整体样式 */
.cycles-modern {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 0;
}

/* 页面头部 */
.page-header {
  position: relative;
  background: linear-gradient(135deg, #2647b2 0%, #3b82f6 100%);
  color: white;
  padding: 60px 0;
  margin-bottom: 32px;
  overflow: hidden;
}

.header-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.05)"/><circle cx="10" cy="60" r="0.5" fill="rgba(255,255,255,0.05)"/><circle cx="90" cy="40" r="0.5" fill="rgba(255,255,255,0.05)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  opacity: 0.3;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.page-icon {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.page-info {
  flex: 1;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0 0 20px 0;
  font-weight: 400;
}

.stats-overview {
  display: flex;
  gap: 32px;
  margin-top: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #ff6b35 !important;
  margin-bottom: 4px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
}

.stat-label {
  font-size: 12px;
  color: #fbbf24 !important;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
  border: none;
  position: relative;
  overflow: hidden;
}

.action-btn.primary {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-btn.primary:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

/* 统计卡片 */
.stats-section {
  max-width: 1200px;
  margin: 0 auto 32px auto;
  padding: 0 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.active {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
}

.stat-icon.completed {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
}

.stat-icon.draft {
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

/* 筛选区域 */
.filter-section {
  max-width: 1200px;
  margin: 0 auto 32px auto;
  padding: 0 24px;
}

.filter-container {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.filter-left {
  display: flex;
  gap: 16px;
  flex: 1;
}

.search-input {
  max-width: 300px;
}

.status-filter {
  width: 150px;
}

.filter-right {
  display: flex;
  gap: 8px;
}

/* 内容区域 */
.content-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 32px 24px;
}

/* 卡片视图 */
.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.cycle-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid #e5e7eb;
  position: relative;
  overflow: hidden;
}

.cycle-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: #e5e7eb;
}

.cycle-card.status-active::before {
  background: #3b82f6;
}

.cycle-card.status-completed::before {
  background: #f59e0b;
}

.cycle-card.status-draft::before {
  background: #6b7280;
}

.cycle-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.title-icon {
  color: #667eea;
  font-size: 20px;
}

.card-status {
  flex-shrink: 0;
}

.status-tag {
  font-weight: 600;
  border-radius: 12px;
  padding: 6px 12px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border: none;
}

.card-content {
  margin-bottom: 20px;
}

.card-description {
  color: #6b7280;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
}

.card-dates {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6b7280;
}

.card-rule {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6b7280;
  background: #f9fafb;
  padding: 8px 12px;
  border-radius: 8px;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.card-actions .action-btn {
  flex: 1;
  min-width: 80px;
  font-size: 12px;
  padding: 8px 12px;
}

/* 表格视图 */
.table-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.cycles-table {
  width: 100%;
}

.cycles-table :deep(.el-table__header) {
  background: #f8f9fa;
}

.cycles-table :deep(.el-table__header th) {
  background: #f8f9fa;
  color: #495057;
  font-weight: 600;
  border-bottom: 2px solid #e9ecef;
}

.cycles-table :deep(.el-table__row) {
  transition: all 0.2s ease;
}

.cycles-table :deep(.el-table__row:hover) {
  background: #f8f9fa;
}

/* 表格单元格样式 */
.cycle-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name-icon {
  color: #667eea;
  font-size: 16px;
}

.name-text {
  font-weight: 600;
  color: #1f2937;
}

.description-text {
  color: #495057;
  line-height: 1.4;
}

.no-description {
  color: #adb5bd;
  font-style: italic;
}

.time-range {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.start-date,
.end-date {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.date-icon {
  color: #667eea;
  font-size: 12px;
}

.start-date {
  color: #495057;
  font-weight: 500;
}

.end-date {
  color: #6c757d;
}

.rule-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.rule-icon {
  color: #667eea;
  font-size: 14px;
}

.rule-name {
  color: #495057;
  font-weight: 500;
}

.no-rule {
  color: #adb5bd;
  font-style: italic;
}

.action-buttons {
  display: flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
  flex-wrap: nowrap;
}

.action-btn {
  min-width: 60px;
  height: 28px;
  font-size: 11px;
  padding: 4px 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: none;
  border-radius: 6px;
  flex: 1;
}

.action-btn.edit {
  background: #3b82f6;
  color: white;
  border: 1px solid #3b82f6;
}

.action-btn.edit:hover {
  background: #2563eb;
  border-color: #2563eb;
  transform: translateY(-1px);
}

.action-btn.generate {
  background: #10b981;
  color: white;
  border: 1px solid #10b981;
}

.action-btn.generate:hover {
  background: #059669;
  border-color: #059669;
  transform: translateY(-1px);
}

.action-btn.view {
  background: #6b7280;
  color: white;
  border: 1px solid #6b7280;
}

.action-btn.view:hover {
  background: #4b5563;
  border-color: #4b5563;
  transform: translateY(-1px);
}

.action-btn.delete {
  background: #ef4444;
  color: white;
  border: 1px solid #ef4444;
}

.action-btn.delete:hover {
  background: #dc2626;
  border-color: #dc2626;
  transform: translateY(-1px);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.empty-icon {
  font-size: 64px;
  color: #dee2e6;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 18px;
  font-weight: 500;
  margin: 0 0 8px 0;
}

.empty-subtitle {
  font-size: 14px;
  margin: 0;
  opacity: 0.8;
}

/* 对话框样式 */
.cycle-dialog :deep(.el-dialog__header) {
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  padding: 20px 24px;
}

.cycle-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.cycle-form {
  padding: 24px;
}

.form-tip {
  font-size: 12px;
  color: #6c757d;
  margin-top: 4px;
  line-height: 1.4;
}

.rule-option {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rule-name {
  font-weight: 500;
  color: #2c3e50;
}

.rule-desc {
  font-size: 12px;
  color: #6c757d;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-left {
    flex-direction: column;
  }
  
  .search-input {
    max-width: none;
  }
  
  .cards-container {
    grid-template-columns: 1fr;
  }
  
  .card-actions {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>
