<template>
  <div class="evaluation-tasks container" style="padding:24px 16px">
    <!-- 标题区 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">考核任务</h3>
      <div class="toolbar">
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
      </div>
    </div>

    <!-- 表格卡片 -->
    <div class="card">
      <div class="table-wrap">
        <el-table :data="tasks" v-loading="loading" border stripe>
          <el-table-column prop="evaluation_code" label="考核码" width="140" />
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
          <el-table-column prop="assigned_at" label="分配时间" min-width="160" />
        </el-table>
      </div>

      <!-- 分页条 -->
      <div class="row" style="padding:12px 16px">
        <div class="toolbar" style="gap:6px">
          <span style="font-size:12px;color:#6b7280">每页</span>
          <el-select v-model="size" size="small" style="width:90px" @change="reload">
            <el-option :value="10" label="10" />
            <el-option :value="20" label="20" />
            <el-option :value="50" label="50" />
          </el-select>
          <span style="font-size:12px;color:#6b7280">条</span>
        </div>
        <el-pagination
          background
          layout="prev, pager, next"
          :current-page="page"
          :page-size="size"
          :total="total"
          @current-change="onPageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useEvaluationStore } from '@/stores/evaluation'

const evaluationStore = useEvaluationStore()
const tasks = computed(() => evaluationStore.tasks)
const loading = computed(() => evaluationStore.loading)
const total = computed(() => tasks.value.length)
const page = ref(1)
const size = ref(10)
const ordering = ref('')
const keyword = ref('')
const relationType = ref('')
const statusFilter = ref('')

const reload = () => {
  // 服务端筛选：page/search/ordering/relation_type/status
  const params:any = { page: page.value, page_size: size.value }
  if (keyword.value) params.search = keyword.value
  if (ordering.value) params.ordering = ordering.value
  if (relationType.value) params.relation_type = relationType.value
  if (statusFilter.value) params.status = statusFilter.value
  evaluationStore.fetchTasks(params)
}
const onPageChange = (p:number) => { page.value = p; reload() }

const getRelationText = (type: string) => {
  const map = { superior: '上级考核下级', peer: '同级互评', subordinate: '下级评价上级' }
  return map[type as keyof typeof map] || type
}
const getStatusType = (status: string) => {
  const map = { pending: 'info', in_progress: 'warning', completed: 'success', overdue: 'danger' }
  return map[status as keyof typeof map] || 'info'
}
const getStatusText = (status: string) => {
  const map = { pending: '待考核', in_progress: '进行中', completed: '已完成', overdue: '已过期' }
  return map[status as keyof typeof map] || status
}

onMounted(() => { reload() })
</script>

<style scoped>
.employee-name { font-weight: 600; color: #303133; margin-bottom: 2px; }
.employee-position { font-size: 12px; color: #909399; line-height: 1.2; }
.position-level { font-weight: 500; color: var(--brand-600); }
</style>
