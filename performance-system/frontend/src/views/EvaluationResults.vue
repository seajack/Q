<template>
  <div class="evaluation-results">
    <el-card>
      <template #header>
        <span>考核结果</span>
      </template>
      
      <el-table :data="results" v-loading="loading">
        <el-table-column prop="employee_name" label="员工姓名" />
        <el-table-column prop="department_name" label="部门" />
        <el-table-column prop="position_name" label="职位" />
        <el-table-column prop="weighted_score" label="综合得分" />
        <el-table-column prop="rank" label="排名" />
        <el-table-column prop="is_final" label="是否终版">
          <template #default="{ row }">
            <el-tag :type="row.is_final ? 'success' : 'warning'">
              {{ row.is_final ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useEvaluationStore } from '@/stores/evaluation'

const evaluationStore = useEvaluationStore()
const results = computed(() => evaluationStore.results)
const loading = computed(() => evaluationStore.loading)

onMounted(() => {
  evaluationStore.fetchResults()
})
</script>

<style scoped>
.evaluation-results {
  padding: 20px;
}
</style>