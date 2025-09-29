<template>
  <div class="cycles-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">考核周期管理</h1>
        <el-button type="primary" @click="openCreate">创建考核周期</el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="filter-section">
      <el-input 
        v-model="search" 
        placeholder="搜索周期名称" 
        clearable 
        @keyup.enter="reload"
        @clear="reload"
        style="width: 300px; margin-right: 16px;"
      />
      <el-select v-model="status" placeholder="筛选状态" @change="reload" style="width: 150px; margin-right: 16px;">
        <el-option label="全部" value="" />
        <el-option label="草稿" value="draft" />
        <el-option label="进行中" value="active" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-button @click="reload">刷新</el-button>
    </div>

    <!-- 数据表格区域 -->
    <div class="table-section">
      <el-table 
        :data="cycles" 
        v-loading="loading" 
        border
        stripe
      >
        <el-table-column prop="name" label="周期名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="考核规则" width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.evaluation_rule_name">{{ row.evaluation_rule_name }}</span>
            <span v-else style="color: #999;">未设置</span>
          </template>
        </el-table-column>
        <el-table-column label="考核指标" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <div v-if="row.evaluation_indicators && row.evaluation_indicators.length > 0">
              <el-tag 
                v-for="indicator in row.evaluation_indicators.slice(0, 2)" 
                :key="indicator.id"
                size="small"
                style="margin-right: 4px;"
              >
                {{ indicator.name }}
              </el-tag>
              <el-tag v-if="row.evaluation_indicators.length > 2" size="small" type="info">
                +{{ row.evaluation_indicators.length - 2 }}
              </el-tag>
            </div>
            <span v-else style="color: #999;">未设置</span>
          </template>
        </el-table-column>
        <el-table-column label="开始日期" width="120">
          <template #default="{ row }">
            {{ row.start_date }}
          </template>
        </el-table-column>
        <el-table-column label="结束日期" width="120">
          <template #default="{ row }">
            {{ row.end_date }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="view(row)">详情</el-button>
            <el-button size="small" type="primary" @click="edit(row)">编辑</el-button>
            <el-button size="small" type="success" @click="generateTasks(row)">生成任务</el-button>
            <el-button size="small" type="info" @click="viewTasks(row)">查看任务</el-button>
            <el-button size="small" type="warning" @click="exportCodes(row)">导出</el-button>
            <el-button size="small" type="danger" @click="deleteCycle(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页区域 -->
    <div class="pagination-section">
      <el-pagination
        v-if="total > 0"
        layout="prev, pager, next"
        :current-page="page"
        :page-size="size"
        :total="total"
        @current-change="onPageChange"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogMode === 'create' ? '创建考核周期' : '编辑考核周期'" 
      width="500px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="周期名称" required>
          <el-input v-model="form.name" placeholder="请输入周期名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="开始日期" required>
          <el-date-picker v-model="form.start_date" type="date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束日期" required>
          <el-date-picker v-model="form.end_date" type="date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="考核规则" required>
          <el-select v-model="form.evaluation_rule" placeholder="请选择考核规则" style="width: 100%">
            <el-option 
              v-for="rule in evaluationRules" 
              :key="rule.id" 
              :label="rule.name" 
              :value="rule.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="考核指标" required>
          <el-select 
            v-model="form.evaluation_indicators" 
            placeholder="请选择考核指标" 
            multiple 
            style="width: 100%"
          >
            <el-option 
              v-for="indicator in evaluationIndicators" 
              :key="indicator.id" 
              :label="indicator.name" 
              :value="indicator.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save" :loading="saving">
          {{ dialogMode === 'create' ? '创建' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Calendar, 
  Plus, 
  Search, 
  Refresh, 
  Setting, 
  View, 
  Edit, 
  List, 
  Download, 
  Delete 
} from '@element-plus/icons-vue'
import { useEvaluationStore } from '@/stores/evaluation'

const store = useEvaluationStore()
const cycles = computed(() => store.cycles)
const loading = computed(() => store.loading)
const total = computed(() => cycles.value.length)
const page = ref(1)
const size = ref(10)
const ordering = ref('') // 预留排序字段，后端支持 ordering
const search = ref('')
const status = ref('')

// 考核规则和指标数据
const evaluationRules = computed(() => store.evaluationRules)
const evaluationIndicators = computed(() => store.indicators)

const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const saving = ref(false)
const rulesLoading = ref(false)
const indicatorsLoading = ref(false)
const form = ref<any>({ 
  name: '', 
  description: '', 
  start_date: '', 
  end_date: '', 
  evaluation_rule: null,
  evaluation_indicators: []
})

const reload = () => {
  const params: any = { page: page.value, page_size: size.value }
  if (search.value) params.search = search.value
  if (ordering.value) params.ordering = ordering.value
  if (status.value) params.status = status.value
  store.fetchCycles(params)
}

const onPageChange = (p: number) => { 
  page.value = p
  reload() 
}

const onSizeChange = (s: number) => {
  size.value = s
  page.value = 1
  reload()
}

const statusText = (s: string) => ({ 
  draft: '草稿', 
  active: '进行中', 
  completed: '已完成', 
  cancelled: '已取消' 
} as any)[s] || s

const statusType = (s: string) => ({ 
  draft: 'info', 
  active: 'success', 
  completed: 'warning', 
  cancelled: 'danger' 
} as any)[s] || 'info'

const openCreate = async () => { 
  dialogMode.value = 'create'
  form.value = { 
    name: '', 
    description: '', 
    start_date: '', 
    end_date: '', 
    status: 'draft',
    evaluation_rule: null,
    evaluation_indicators: []
  }
  
  // 加载考核规则和指标数据
  try {
    rulesLoading.value = true
    indicatorsLoading.value = true
    await Promise.all([
      store.fetchEvaluationRules(),
      store.fetchIndicators()
    ])
  } catch (error) {
    console.error('加载考核规则和指标失败:', error)
    ElMessage.error('加载数据失败，请重试')
  } finally {
    rulesLoading.value = false
    indicatorsLoading.value = false
  }
  
  dialogVisible.value = true 
}

const view = (row: any) => { 
  console.log('查看详情:', row)
  ElMessage.info(`查看考核周期: ${row.name}`)
}

const edit = async (row: any) => { 
  dialogMode.value = 'edit'
  form.value = { 
    ...row,
    evaluation_rule: row.evaluation_rule || null,
    evaluation_indicators: row.evaluation_indicators || []
  }
  
  // 加载考核规则和指标数据
  try {
    rulesLoading.value = true
    indicatorsLoading.value = true
    await Promise.all([
      store.fetchEvaluationRules(),
      store.fetchIndicators()
    ])
  } catch (error) {
    console.error('加载考核规则和指标失败:', error)
    ElMessage.error('加载数据失败，请重试')
  } finally {
    rulesLoading.value = false
    indicatorsLoading.value = false
  }
  
  dialogVisible.value = true 
}

// 删除考核周期功能
const deleteCycle = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除考核周期"${row.name}"吗？\n\n删除后将无法恢复，请谨慎操作！`,
      '确认删除',
      { 
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await store.deleteCycle(row.id)
    ElMessage.success('删除成功')
    await reload()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

const generateTasks = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要为"${row.name}"生成考核任务吗？`,
      '确认生成',
      { 
        type: 'warning',
        confirmButtonText: '确定生成',
        cancelButtonText: '取消'
      }
    )
    
    await store.generateTasksForCycle(row.id)
    ElMessage.success('考核任务生成成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('生成任务失败:', error)
      ElMessage.error('生成任务失败，请重试')
    }
  }
}

const viewTasks = (row: any) => {
  // 跳转到评审任务页面，并筛选该周期的任务
  window.open(`/tasks?cycle=${row.id}`, '_blank')
}

const exportCodes = async (row: any) => {
  try {
    const { taskApi } = await import('@/utils/api')
    const response = await taskApi.exportEvaluatorCodes(row.id)
    
    // 创建下载链接
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `考核码分发表_${row.name}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('考核码Excel文件导出成功')
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error(`导出失败: ${error.response?.data?.error || error.message}`)
  }
}

const save = async () => {
  try {
    saving.value = true
    
    // 基础校验
    if (!form.value.name?.trim()) {
      ElMessage.error('请输入周期名称')
      return
    }
    if (!form.value.start_date) {
      ElMessage.error('请选择开始日期')
      return
    }
    if (!form.value.end_date) {
      ElMessage.error('请选择结束日期')
      return
    }
    if (!form.value.evaluation_rule) {
      ElMessage.error('请选择考核规则')
      return
    }
    if (!form.value.evaluation_indicators || form.value.evaluation_indicators.length === 0) {
      ElMessage.error('请选择至少一个考核指标')
      return
    }
    
    // 日期校验
    if (new Date(form.value.start_date) >= new Date(form.value.end_date)) {
      ElMessage.error('结束日期必须晚于开始日期')
      return
    }
    
    // 格式化日期为字符串
    const formatDate = (date: any) => {
      if (date instanceof Date) {
        return date.toISOString().split('T')[0]
      }
      return date
    }
    
    const payload = { 
      name: form.value.name.trim(),
      description: form.value.description?.trim() || '',
      start_date: formatDate(form.value.start_date),
      end_date: formatDate(form.value.end_date),
      status: form.value.status || 'draft',
      evaluation_rule: form.value.evaluation_rule,
      evaluation_indicators: form.value.evaluation_indicators
    }
    
    if (dialogMode.value === 'create') {
      await store.createCycle(payload as any)
      ElMessage.success('考核周期创建成功')
    } else {
      await store.updateCycle(form.value.id, payload as any)
      ElMessage.success('考核周期更新成功')
    }
    
    dialogVisible.value = false
    await reload()
  } catch (e: any) {
    console.error('保存失败:', e)
    // 显示更详细的错误信息
    if (e.response?.data?.detail) {
      ElMessage.error(`保存失败: ${e.response.data.detail}`)
    } else if (e.response?.data?.non_field_errors) {
      ElMessage.error(`保存失败: ${e.response.data.non_field_errors.join(', ')}`)
    } else if (e.response?.data) {
      // 处理字段验证错误
      const errors = Object.values(e.response.data).flat()
      ElMessage.error(`保存失败: ${errors.join(', ')}`)
    } else {
      ElMessage.error('保存失败，请重试')
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => { 
  store.fetchCycles() 
})
</script>

<style scoped>
/* 页面整体样式 */
.cycles-page {
  min-height: 100vh;
  background: #f5f6fa;
  padding: 0;
}

/* Add color variables for consistency */
:root {
  --primary-color: #3498db;
  --primary-dark: #2980b9;
  --text-dark: #34495e;
  --text-gray: #6c757d;
  --bg-light: #f8f9fa;
  --border-light: #e9ecef;
}

/* Apply to page header */
.page-header {
  background: var(--primary-color);
  color: white;
  padding: 16px 24px;
  margin-bottom: 16px;
}

/* Simplify header content */
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 20px;
  margin: 0;
}

.title-icon {
  font-size: 32px;
}

.page-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.create-btn {
  background: #3498db;
  border: 1px solid #2980b9;
  color: white;
  font-weight: 500;
  padding: 12px 24px;
  height: auto;
}

.create-btn:hover {
  background: #2980b9;
  border-color: #2980b9;
}

/* Filter section */
.filter-section {
  padding: 16px 24px;
  background: white;
  margin-bottom: 16px;
  display: flex;
  gap: 16px;
  align-items: center;
}

.filter-content {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.search-group {
  flex: 1;
  min-width: 300px;
}

.search-input {
  width: 100%;
}

.filter-group {
  min-width: 160px;
}

.status-filter {
  width: 100%;
}

.action-group {
  display: flex;
  gap: 8px;
}

.refresh-btn {
  background: #ecf0f1;
  border: 1px solid #bdc3c7;
  color: #34495e;
}

.refresh-btn:hover {
  background: #d5dbdb;
  border-color: #bdc3c7;
}

/* Table section */
.table-section {
  background: white;
  padding: 16px;
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  color: #34495e;
  font-weight: 600;
  border-bottom: 2px solid #e9ecef;
}

.cycles-table :deep(.el-table__row) {
  transition: all 0.2s ease;
}

.cycles-table :deep(.el-table__row:hover) {
  background: #f8f9fa;
}

/* 空状态样式 */
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

/* 表格单元格样式 */
.cycle-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name-icon {
  color: #3498db;
  font-size: 16px;
}

.name-text {
  font-weight: 500;
  color: #34495e;
}

.description-text {
  color: #495057;
  line-height: 1.4;
}

.no-description {
  color: #adb5bd;
  font-style: italic;
}

.status-tag {
  font-weight: 500;
  border-radius: 6px;
}

.status-draft {
  background: #e9ecef;
  color: #495057;
}

.status-active {
  background: #d4edda;
  color: #155724;
}

.status-completed {
  background: #fff3cd;
  color: #856404;
}

.status-cancelled {
  background: #f8d7da;
  color: #721c24;
}

.rule-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.rule-icon {
  color: #3498db;
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

.indicators-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.indicators-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.indicator-tag {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  color: #495057;
  font-size: 12px;
}

.more-indicators {
  background: #e9ecef;
  border: 1px solid #dee2e6;
  color: #495057;
}

.no-indicators {
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
  color: #3498db;
  font-size: 12px;
}

.start-date {
  color: #495057;
  font-weight: 500;
}

.end-date {
  color: #6c757d;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  gap: 4px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: center;
}

.action-btn {
  min-width: 60px;
  height: 32px;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.view-btn {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  color: #495057;
}

.view-btn:hover {
  background: #e9ecef;
  border-color: #dee2e6;
}

.edit-btn {
  background: #e9ecef;
  border: 1px solid #dee2e6;
  color: #495057;
}

.edit-btn:hover {
  background: #dee2e6;
  border-color: #ced4da;
}

.generate-btn {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.generate-btn:hover {
  background: #c3e6cb;
  border-color: #b1dfbb;
}

.tasks-btn {
  background: #d1ecf1;
  border: 1px solid #bee5eb;
  color: #0c5460;
}

.tasks-btn:hover {
  background: #bee5eb;
  border-color: #abdde5;
}

.export-btn {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  color: #856404;
}

.export-btn:hover {
  background: #ffeaa7;
  border-color: #fdcb6e;
}

.delete-btn {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.delete-btn:hover {
  background: #f5c6cb;
  border-color: #f1b0b7;
}

/* Pagination */
.pagination-section {
  padding: 16px;
  text-align: center;
}

.pagination {
  display: flex;
  justify-content: center;
}

/* Dialog */
.el-dialog {
  border-radius: 4px;
}

.el-dialog__header {
  background: var(--bg-light);
  border-bottom: 1px solid var(--border-light);
}

.el-dialog__footer {
  border-top: 1px solid var(--border-light);
  padding: 10px 20px;
}

/* Button styles */
.el-button--primary {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

.el-button--primary:hover {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
}

/* Table styles */
.el-table th {
  background: var(--bg-light);
  color: var(--text-dark);
}

.el-table tr:hover {
  background: var(--bg-light);
}

/* 动画效果 */
.cycles-table :deep(.el-table__row) {
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 加载状态 */
.cycles-table :deep(.el-loading-mask) {
  background: rgba(255, 255, 255, 0.8);
}

.cycles-table :deep(.el-loading-spinner) {
  color: #3498db;
}
</style>
