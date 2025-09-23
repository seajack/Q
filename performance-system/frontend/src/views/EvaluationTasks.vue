<template>
  <div class="evaluation-tasks">
    <el-card>
      <template #header>
        <span>考核任务管理</span>
      </template>
      
      <el-table :data="tasks" v-loading="loading">
        <el-table-column prop="evaluation_code" label="考核码" />
        <el-table-column prop="evaluator_name" label="考核人" />
        <el-table-column prop="evaluatee_name" label="被考核人" />
        <el-table-column prop="relation_type" label="考核关系">
          <template #default="{ row }">
            <el-tag>{{ getRelationText(row.relation_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assigned_at" label="分配时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useEvaluationStore } from '@/stores/evaluation'

const evaluationStore = useEvaluationStore()
const tasks = computed(() => evaluationStore.tasks)
const loading = computed(() => evaluationStore.loading)

const getRelationText = (type: string) => {
  const map = {
    'superior': '上级考核下级',
    'peer': '同级互评',
    'subordinate': '下级评价上级'
  }
  return map[type as keyof typeof map] || type
}

const getStatusType = (status: string) => {
  const map = {
    'pending': 'info',
    'in_progress': 'warning',
    'completed': 'success',
    'overdue': 'danger'
  }
  return map[status as keyof typeof map] || 'info'
}

const getStatusText = (status: string) => {
  const map = {
    'pending': '待考核',
    'in_progress': '进行中',
    'completed': '已完成',
    'overdue': '已过期'
  }
  return map[status as keyof typeof map] || status
}

onMounted(() => {
  evaluationStore.fetchTasks()
})
</script>

<style scoped>
.evaluation-tasks {
  padding: 20px;
}
</style>