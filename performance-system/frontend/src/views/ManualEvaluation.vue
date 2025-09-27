<template>
  <div class="container" style="padding:24px 16px">
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">手动分配评分</h3>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索评价人/被评价人" clearable style="width:240px" @keyup.enter="reload" />
        <el-select v-model="selectedCycle" placeholder="选择考核周期" style="width:200px" @change="reload" clearable>
          <el-option 
            v-for="cycle in cycles" 
            :key="cycle.id" 
            :label="cycle.name" 
            :value="cycle.id" 
          />
        </el-select>
        <el-button type="primary" @click="reload">刷新</el-button>
      </div>
    </div>

    <div class="card">
      <div class="table-wrap">
        <el-table :data="rows" v-loading="loading" border stripe>
          <el-table-column prop="cycle_name" label="考核周期" width="150" />
          <el-table-column prop="evaluator_name" label="评价人" min-width="180" />
          <el-table-column prop="evaluatee_name" label="被评价人" min-width="180" />
          <el-table-column prop="relation_type" label="关系类型" width="140">
            <template #default="{ row }">{{ relationText(row.relation_type) }}</template>
          </el-table-column>
          <el-table-column prop="weight" label="权重" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="evaluation_code" label="考核码" width="200" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <div class="toolbar">
                <el-button 
                  v-if="row.status === 'pending'" 
                  size="small" 
                  type="primary" 
                  @click="startEvaluation(row)"
                >
                  开始评分
                </el-button>
                <el-button 
                  v-if="row.status === 'in_progress'" 
                  size="small" 
                  type="success" 
                  @click="continueEvaluation(row)"
                >
                  继续评分
                </el-button>
                <el-button 
                  v-if="row.status === 'completed'" 
                  size="small" 
                  type="info" 
                  @click="viewEvaluation(row)"
                >
                  查看评分
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div class="row" style="padding:12px 16px">
        <div class="toolbar" style="gap:6px">
          <span style="font-size:12px;color:#6b7280">每页</span>
          <el-select v-model="pageSize" size="small" style="width:90px" @change="reload">
            <el-option :value="10" label="10" />
            <el-option :value="20" label="20" />
            <el-option :value="50" label="50" />
            <el-option :value="100" label="100" />
          </el-select>
          <span style="font-size:12px;color:#6b7280">条</span>
        </div>
        <el-pagination
          background
          layout="prev, pager, next"
          :current-page="page"
          :page-size="pageSize"
          :total="total"
          @current-change="onPageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { taskApi, cycleApi } from '@/utils/api'

const router = useRouter()
const loading = ref(false)
const rows = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const keyword = ref('')
const selectedCycle = ref('')
const cycles = ref<any[]>([])

const load = async () => {
  try {
    loading.value = true
    const params: any = { 
      page: page.value, 
      page_size: pageSize.value,
      manual_assignment: true  // 只显示手动分配的任务
    }
    if (keyword.value) params.search = keyword.value
    if (selectedCycle.value) params.cycle = selectedCycle.value
    
    const res = await taskApi.list(params)
    const data: any = res.data
    rows.value = data.results || data || []
    total.value = data.count ?? rows.value.length
  } finally { 
    loading.value = false 
  }
}

const loadCycles = async () => {
  try {
    const res = await cycleApi.list()
    cycles.value = res.data.results || res.data || []
  } catch (error) {
    console.error('加载考核周期失败:', error)
  }
}

const reload = () => { 
  page.value = 1
  load() 
}

const onPageChange = (p: number) => { 
  page.value = p
  load() 
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    'pending': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'cancelled': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待评分',
    'in_progress': '评分中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

const relationText = (t: string) => ({
  superior: '上级评下级', 
  peer: '同级互评', 
  subordinate: '下级评上级', 
  self: '自评', 
  cross_superior: '跨部门上级', 
  cross_peer: '跨部门同级', 
  custom: '自定义关系'
} as any)[t] || t

const startEvaluation = (row: any) => {
  // 使用考核码进入评分页面
  sessionStorage.setItem('evaluationCode', row.evaluation_code)
  router.push('/evaluation')
}

const continueEvaluation = (row: any) => {
  // 使用考核码进入评分页面
  sessionStorage.setItem('evaluationCode', row.evaluation_code)
  router.push('/evaluation')
}

const viewEvaluation = (row: any) => {
  // 使用考核码进入评分页面
  sessionStorage.setItem('evaluationCode', row.evaluation_code)
  router.push('/evaluation')
}

onMounted(async () => {
  await Promise.all([
    load(),
    loadCycles()
  ])
})
</script>
