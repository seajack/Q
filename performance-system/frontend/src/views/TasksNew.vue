<template>
  <div class="evaluation-tasks container" style="padding:24px 16px">
    <!-- 标题区 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">考核任务</h3>
      <div class="toolbar">
        <el-select v-model="selectedCycle" placeholder="选择考核周期" style="width:200px" @change="reload">
          <el-option label="全部周期" value="" />
          <el-option 
            v-for="cycle in cycles" 
            :key="cycle.id" 
            :label="cycle.name" 
            :value="cycle.id"
          />
        </el-select>
        <el-input v-model="keyword" placeholder="搜索考核码/姓名" clearable style="width:220px" @keyup.enter="reload" />
        <el-select v-model="relationType" placeholder="关系" style="width:140px" @change="reload">
          <el-option label="全部" value="" />
          <el-option label="上级评下级" value="superior" />
          <el-option label="同级互评" value="peer" />
          <el-option label="下级评上级" value="subordinate" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="状态" style="width:140px" @change="reload">
          <el-option label="全部" value="" />
          <el-option label="待考核" value="pending" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="已完成" value="completed" />
          <el-option label="已过期" value="overdue" />
        </el-select>
        <el-button type="primary" @click="reload">查询</el-button>
        <el-button type="success" @click="exportToExcel" :loading="exportLoading">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
        <!-- 批量操作按钮 -->
        <el-button 
          type="warning" 
          :disabled="selectedTasks.length === 0"
          @click="showBatchDialog = true"
        >
          <el-icon><Operation /></el-icon>
          批量操作 ({{ selectedTasks.length }})
        </el-button>
        <!-- 申诉反馈系统 -->
        <FeedbackSystem />
        <!-- 拖拽排序开关 -->
        <el-button 
          :type="dragSortEnabled ? 'primary' : 'default'"
          @click="toggleDragSort"
        >
          <el-icon><Rank /></el-icon>
          {{ dragSortEnabled ? '退出排序' : '拖拽排序' }}
        </el-button>
      </div>
    </div>

    <!-- 拖拽排序模式 -->
    <div v-if="dragSortEnabled" class="drag-sort-container">
      <DragSortable
        v-model:items="tasks"
        :disabled="false"
        :show-handle="true"
        :show-order="true"
        @sort="handleTaskSort"
      >
        <template #default="{ item, index }">
          <div class="task-item">
            <div class="task-info">
              <div class="task-header">
                <h4>{{ item.evaluatee_name || '未知员工' }}</h4>
                <span class="task-status" :class="getStatusClass(item.status)">
                  {{ getStatusText(item.status) }}
                </span>
              </div>
              <div class="task-details">
                <p><strong>考核人：</strong>{{ item.evaluator_name || '未知' }}</p>
                <p><strong>关系：</strong>{{ getRelationText(item.relation_type) }}</p>
                <p><strong>截止时间：</strong>{{ formatDate(item.deadline) }}</p>
              </div>
            </div>
            <div class="task-actions">
              <el-button size="small" type="primary" @click="viewTask(item)">
                查看
              </el-button>
              <el-button size="small" @click="editTask(item)">
                编辑
              </el-button>
            </div>
          </div>
        </template>
      </DragSortable>
    </div>

    <!-- 表格模式 -->
    <div v-else class="card">
      <div class="table-wrap">
        <el-table 
          :data="tasks" 
          v-loading="loading" 
          border 
          stripe
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column type="index" label="序号" width="80" align="center" :index="getIndex" />
          <el-table-column prop="evaluation_code" label="考核码" width="180" show-overflow-tooltip />
          <el-table-column prop="evaluator_name" label="考核人" width="220">
            <template #default="{ row }">
              <div>
                <div class="employee-name">{{ row.evaluator_name }}</div>
                <div class="employee-position" v-if="row.evaluator_position">
                  {{ row.evaluator_position }}
                  <span class="position-level" v-if="row.evaluator_position_level">(L{{ row.evaluator_position_level }})</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="evaluatee_name" label="被考核人" width="220">
            <template #default="{ row }">
              <div>
                <div class="employee-name">{{ row.evaluatee_name }}</div>
                <div class="employee-position" v-if="row.evaluatee_position">
                  {{ row.evaluatee_position }}
                  <span class="position-level" v-if="row.evaluatee_position_level">(L{{ row.evaluatee_position_level }})</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="relation_type" label="考核关系" width="160">
            <template #default="{ row }">
              <el-tag>{{ getRelationText(row.relation_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="assigned_at" label="分配时间" min-width="160">
            <template #default="{ row }">
              {{ formatDateTime(row.assigned_at) }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页条 -->
      <div class="pagination-container" style="padding:12px 16px;display:flex;align-items:center;justify-content:center">
        <el-pagination
          :key="`pagination-${total}-${page}-${size}`"
          background
          layout="total, sizes, prev, pager, next, jumper"
          :current-page="page"
          :page-size="size"
          :total="Number(total) || 0"
          :page-sizes="[10, 20, 50, 100]"
          :pager-count="5"
          :hide-on-single-page="false"
          @current-change="onPageChange"
          @size-change="onSizeChange"
        />
      </div>
    </div>

    <!-- 批量操作对话框 -->
    <el-dialog
      v-model="showBatchDialog"
      title="批量操作"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="batch-operation-content">
        <div class="selected-info">
          <el-alert
            :title="`已选择 ${selectedTasks.length} 个任务`"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
        
        <div class="operation-options">
          <h4>选择操作类型：</h4>
          <el-radio-group v-model="batchOperation" class="operation-group">
            <el-radio value="status">修改状态</el-radio>
            <el-radio value="remind">发送提醒</el-radio>
            <el-radio value="extend">延长截止时间</el-radio>
            <el-radio value="delete">删除任务</el-radio>
          </el-radio-group>
        </div>

        <!-- 修改状态 -->
        <div v-if="batchOperation === 'status'" class="operation-detail">
          <h4>选择新状态：</h4>
          <el-select v-model="newStatus" placeholder="请选择状态" style="width: 100%">
            <el-option label="待考核" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已过期" value="overdue" />
          </el-select>
        </div>

        <!-- 发送提醒 -->
        <div v-if="batchOperation === 'remind'" class="operation-detail">
          <h4>提醒内容：</h4>
          <el-input
            v-model="remindMessage"
            type="textarea"
            :rows="3"
            placeholder="请输入提醒内容..."
            maxlength="200"
            show-word-limit
          />
        </div>

        <!-- 延长截止时间 -->
        <div v-if="batchOperation === 'extend'" class="operation-detail">
          <h4>延长天数：</h4>
          <el-input-number
            v-model="extendDays"
            :min="1"
            :max="30"
            placeholder="请输入延长天数"
            style="width: 100%"
          />
        </div>

        <!-- 删除确认 -->
        <div v-if="batchOperation === 'delete'" class="operation-detail">
          <el-alert
            title="警告：此操作将永久删除选中的任务，且无法恢复！"
            type="error"
            :closable="false"
            show-icon
          />
          <div style="margin-top: 10px;">
            <el-checkbox v-model="confirmDelete">
              我确认要删除这些任务
            </el-checkbox>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showBatchDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="executeBatchOperation"
            :loading="batchLoading"
            :disabled="!canExecuteBatch"
          >
            确认执行
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useEvaluationStore } from '@/stores/evaluation'
import { Download, Operation, Rank } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDateTime as formatDateTimeUtil } from '@/utils/dateUtils'
import * as XLSX from 'xlsx'
// import { saveAs } from 'file-saver'
import FeedbackSystem from '@/components/FeedbackSystem.vue'
import DragSortable from '@/components/DragSortable.vue'

// 定义 formatDateTime 函数供模板使用
const formatDateTime = formatDateTimeUtil

const route = useRoute()
const evaluationStore = useEvaluationStore()
const tasks = computed(() => evaluationStore.tasks)
const loading = computed(() => evaluationStore.loading)
const cycles = computed(() => evaluationStore.cycles)
const total = computed(() => {
  return evaluationStore.total || 0
})
const page = ref(1)
const size = ref(10)
const ordering = ref('')
const keyword = ref('')
const relationType = ref('')
const statusFilter = ref('')
const selectedCycle = ref('')
const exportLoading = ref(false)

// 批量操作相关
const selectedTasks = ref<any[]>([])
const showBatchDialog = ref(false)
const batchOperation = ref('')
const newStatus = ref('')
const remindMessage = ref('')
const extendDays = ref(1)
const confirmDelete = ref(false)
const batchLoading = ref(false)

// 拖拽排序相关
const dragSortEnabled = ref(false)

const reload = async () => {
  // 服务端筛选：page/search/ordering/relation_type/status/cycle
  const params:any = { page: page.value, page_size: size.value }
  if (keyword.value) params.search = keyword.value
  if (ordering.value) params.ordering = ordering.value
  if (relationType.value) params.relation_type = relationType.value
  if (statusFilter.value) params.status = statusFilter.value
  if (selectedCycle.value) params.cycle = selectedCycle.value
  await evaluationStore.fetchTasks(params)
  await nextTick()
}
const onPageChange = async (p:number) => { page.value = p; await reload() }
const onSizeChange = async (s:number) => { size.value = s; page.value = 1; await reload() }

// 批量操作相关方法
const handleSelectionChange = (selection: any[]) => {
  selectedTasks.value = selection
}

const canExecuteBatch = computed(() => {
  if (batchOperation.value === 'status') return newStatus.value !== ''
  if (batchOperation.value === 'remind') return remindMessage.value.trim() !== ''
  if (batchOperation.value === 'extend') return extendDays.value > 0
  if (batchOperation.value === 'delete') return confirmDelete.value
  return false
})

const executeBatchOperation = async () => {
  if (!canExecuteBatch.value) return
  
  try {
    batchLoading.value = true
    
    const taskIds = selectedTasks.value.map(task => task.id)
    
    switch (batchOperation.value) {
      case 'status':
        await batchUpdateStatus(taskIds, newStatus.value)
        break
      case 'remind':
        await batchSendReminder(taskIds, remindMessage.value)
        break
      case 'extend':
        await batchExtendDeadline(taskIds, extendDays.value)
        break
      case 'delete':
        await batchDeleteTasks(taskIds)
        break
    }
    
    ElMessage.success('批量操作执行成功！')
    showBatchDialog.value = false
    resetBatchForm()
    await reload()
    
  } catch (error) {
    console.error('批量操作失败:', error)
    ElMessage.error('批量操作失败，请重试')
  } finally {
    batchLoading.value = false
  }
}

const batchUpdateStatus = async (taskIds: number[], status: string) => {
  // 这里应该调用API更新任务状态
  console.log('批量更新状态:', taskIds, status)
  // TODO: 实现API调用
}

const batchSendReminder = async (taskIds: number[], message: string) => {
  // 这里应该调用API发送提醒
  console.log('批量发送提醒:', taskIds, message)
  // TODO: 实现API调用
}

const batchExtendDeadline = async (taskIds: number[], days: number) => {
  // 这里应该调用API延长截止时间
  console.log('批量延长截止时间:', taskIds, days)
  // TODO: 实现API调用
}

const batchDeleteTasks = async (taskIds: number[]) => {
  // 这里应该调用API删除任务
  console.log('批量删除任务:', taskIds)
  // TODO: 实现API调用
}

const resetBatchForm = () => {
  batchOperation.value = ''
  newStatus.value = ''
  remindMessage.value = ''
  extendDays.value = 1
  confirmDelete.value = false
  selectedTasks.value = []
}

// 拖拽排序相关方法
const toggleDragSort = () => {
  dragSortEnabled.value = !dragSortEnabled.value
  if (dragSortEnabled.value) {
    ElMessage.success('已启用拖拽排序模式，您可以拖拽任务来调整顺序')
  } else {
    ElMessage.info('已退出拖拽排序模式')
  }
}

const handleTaskSort = (newTasks: any[], oldIndex: number, newIndex: number) => {
  console.log('任务排序:', { oldIndex, newIndex, newTasks })
  // 这里可以调用API保存新的排序
  // TODO: 实现API调用保存排序
  ElMessage.success(`已将任务从第 ${oldIndex + 1} 位移动到第 ${newIndex + 1} 位`)
}

const getStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': 'status-pending',
    'in_progress': 'status-progress',
    'completed': 'status-completed',
    'overdue': 'status-overdue'
  }
  return statusMap[status] || 'status-default'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待考核',
    'in_progress': '进行中',
    'completed': '已完成',
    'overdue': '已过期'
  }
  return statusMap[status] || '未知'
}

const getRelationText = (relationType: string) => {
  const relationMap: Record<string, string> = {
    'superior': '上级评下级',
    'peer': '同级互评',
    'subordinate': '下级评上级'
  }
  return relationMap[relationType] || '未知关系'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '未设置'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const viewTask = (task: any) => {
  console.log('查看任务:', task)
  // TODO: 实现查看任务功能
}

const editTask = (task: any) => {
  console.log('编辑任务:', task)
  // TODO: 实现编辑任务功能
}

const getIndex = (index: number) => {
  return (page.value - 1) * size.value + index + 1
}

// 导出Excel功能
const exportToExcel = async () => {
  try {
    exportLoading.value = true
    
    // 获取所有数据（不分页）
    const params: any = { page_size: 10000 } // 获取大量数据
    if (keyword.value) params.search = keyword.value
    if (ordering.value) params.ordering = ordering.value
    if (relationType.value) params.relation_type = relationType.value
    if (statusFilter.value) params.status = statusFilter.value
    if (selectedCycle.value) params.cycle = selectedCycle.value
    
    await evaluationStore.fetchTasks(params)
    
    // 准备Excel数据
    const excelData = tasks.value.map((task, index) => ({
      '序号': index + 1,
      '考核码': task.evaluation_code,
      '考核周期': (task as any).cycle_name || '未知周期',
      '被考核人': task.evaluatee_name,
      '被考核人职位': task.evaluatee_position,
      '被考核人职级': task.evaluatee_position_level,
      '考核人': task.evaluator_name,
      '考核人职位': task.evaluator_position,
      '考核人职级': task.evaluator_position_level,
      '关系类型': getRelationText(task.relation_type),
      '权重': task.weight,
      '状态': getStatusText(task.status),
      '分配时间': task.assigned_at ? formatDateTime(task.assigned_at) : '',
      '完成时间': task.completed_at ? formatDateTime(task.completed_at) : ''
    }))
    
    // 创建工作簿
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet(excelData)
    
    // 设置列宽
    const colWidths = [
      { wch: 8 },   // 序号
      { wch: 20 },  // 考核码
      { wch: 15 },  // 考核周期
      { wch: 12 },  // 被考核人
      { wch: 15 },  // 被考核人职位
      { wch: 12 },  // 被考核人职级
      { wch: 12 },  // 考核人
      { wch: 15 },  // 考核人职位
      { wch: 12 },  // 考核人职级
      { wch: 15 },  // 关系类型
      { wch: 8 },   // 权重
      { wch: 10 },  // 状态
      { wch: 20 },  // 分配时间
      { wch: 20 }   // 完成时间
    ]
    ws['!cols'] = colWidths
    
    // 添加工作表
    XLSX.utils.book_append_sheet(wb, ws, '考核任务')
    
    // 生成Excel文件
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([wbout], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    
    // 生成文件名
    const now = new Date()
    const timestamp = now.toISOString().slice(0, 19).replace(/:/g, '-')
    const cycleName = selectedCycle.value ? 
      cycles.value.find(c => String(c.id) === selectedCycle.value)?.name || '全部周期' : 
      '全部周期'
    const fileName = `考核任务_${cycleName}_${timestamp}.xlsx`
    
    // 下载文件
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    link.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功！')
    
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请重试')
  } finally {
    exportLoading.value = false
  }
}


const getStatusType = (status: string) => {
  const map = { pending: 'info', in_progress: 'warning', completed: 'success', overdue: 'danger' }
  return map[status as keyof typeof map] || 'info'
}


onMounted(async () => { 
  // 加载考核周期数据
  await evaluationStore.fetchCycles()
  
  // 从URL参数中获取考核周期ID
  const cycleId = route.query.cycle
  if (cycleId) {
    selectedCycle.value = String(cycleId)
  }
  
  await reload() 
})
</script>

<style scoped>
.employee-name { font-weight: 600; color: #303133; margin-bottom: 2px; }
.employee-position { font-size: 12px; color: #909399; line-height: 1.2; }
.position-level { font-weight: 500; color: var(--brand-600); }

/* 拖拽排序样式 */
.drag-sort-container {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 16px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.task-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.task-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.task-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background: #fef3c7;
  color: #d97706;
}

.status-progress {
  background: #dbeafe;
  color: #2563eb;
}

.status-completed {
  background: #d1fae5;
  color: #059669;
}

.status-overdue {
  background: #fee2e2;
  color: #dc2626;
}

.status-default {
  background: #f3f4f6;
  color: #6b7280;
}

.task-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-details p {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.4;
}

.task-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .task-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .task-actions {
    justify-content: flex-end;
  }
}

/* 确保分页器显示 */
:deep(.el-pagination) {
  display: flex !important;
  align-items: center;
}

:deep(.el-pagination .el-pager) {
  display: flex !important;
}

:deep(.el-pagination .el-pager li) {
  display: inline-block !important;
  min-width: 30px;
  height: 30px;
  line-height: 30px;
  text-align: center;
  margin: 0 2px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
}

:deep(.el-pagination .el-pager li:hover) {
  color: #409eff;
  border-color: #409eff;
}

:deep(.el-pagination .el-pager li.is-active) {
  background: #409eff;
  color: #fff;
  border-color: #409eff;
}

/* 强制显示分页器所有元素 */
:deep(.el-pagination .el-pagination__total) {
  display: inline-block !important;
}

:deep(.el-pagination .el-pagination__jump) {
  display: inline-block !important;
}

:deep(.el-pagination .el-pagination__sizes) {
  display: inline-block !important;
}

/* 批量操作对话框样式 */
.batch-operation-content {
  padding: 16px 0;
}

.selected-info {
  margin-bottom: 20px;
}

.operation-options {
  margin-bottom: 20px;
}

.operation-options h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.operation-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.operation-detail {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.operation-detail h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
