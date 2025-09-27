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
      </div>
    </div>

    <!-- 表格卡片 -->
    <div class="card">
      <div class="table-wrap">
        <el-table :data="tasks" v-loading="loading" border stripe>
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useEvaluationStore } from '@/stores/evaluation'
import { Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

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
      '考核周期': task.cycle_name,
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
      cycles.value.find(c => c.id === selectedCycle.value)?.name || '全部周期' : 
      '全部周期'
    const fileName = `考核任务_${cycleName}_${timestamp}.xlsx`
    
    // 下载文件
    saveAs(blob, fileName)
    
    ElMessage.success('导出成功！')
    
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请重试')
  } finally {
    exportLoading.value = false
  }
}

const getRelationText = (type: string) => {
  const map = { superior: '上级考核下级', peer: '同级互评', subordinate: '下级评价上级' }
  return map[type as keyof typeof map] || type
}

const getStatusText = (status: string) => {
  const map = { 
    pending: '待考核', 
    in_progress: '进行中', 
    completed: '已完成', 
    overdue: '已过期' 
  }
  return map[status as keyof typeof map] || status
}

const getStatusType = (status: string) => {
  const map = { pending: 'info', in_progress: 'warning', completed: 'success', overdue: 'danger' }
  return map[status as keyof typeof map] || 'info'
}

const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(async () => { 
  // 加载考核周期数据
  await evaluationStore.fetchCycles()
  
  // 从URL参数中获取考核周期ID
  const cycleId = route.query.cycle
  if (cycleId) {
    selectedCycle.value = Number(cycleId)
  }
  
  await reload() 
})
</script>

<style scoped>
.employee-name { font-weight: 600; color: #303133; margin-bottom: 2px; }
.employee-position { font-size: 12px; color: #909399; line-height: 1.2; }
.position-level { font-weight: 500; color: var(--brand-600); }

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
</style>
