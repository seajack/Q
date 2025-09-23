<template>
  <div class="evaluation-results">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>考核结果</span>
          <div class="header-actions">
            <el-select 
              v-model="selectedCycleId" 
              placeholder="选择考核周期" 
              style="width: 200px; margin-right: 10px"
              @change="handleCycleChange"
            >
              <el-option label="全部周期" :value="null" />
              <el-option
                v-for="cycle in cycles"
                :key="cycle.id"
                :label="cycle.name"
                :value="cycle.id"
              />
            </el-select>
            <el-button 
              type="primary" 
              @click="calculateResults"
              :loading="calculating"
              :disabled="!selectedCycleId"
            >
              <el-icon><Operation /></el-icon>
              计算结果
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="results" v-loading="loading">
        <el-table-column prop="employee_name" label="员工姓名" />
        <el-table-column prop="employee_department" label="部门" />
        <el-table-column prop="employee_position" label="职位" />
        <el-table-column prop="weighted_score" label="综合得分" width="120">
          <template #default="{ row }">
            <span class="score-value">{{ parseFloat(row.weighted_score).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="superior_score" label="上级评分" width="100">
          <template #default="{ row }">
            <span v-if="row.superior_score">
              {{ parseFloat(row.superior_score).toFixed(2) }}
            </span>
            <span v-else class="no-score">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="peer_score" label="同级评分" width="100">
          <template #default="{ row }">
            <span v-if="row.peer_score">
              {{ parseFloat(row.peer_score).toFixed(2) }}
            </span>
            <span v-else class="no-score">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="subordinate_score" label="下级评分" width="100">
          <template #default="{ row }">
            <span v-if="row.subordinate_score">
              {{ parseFloat(row.subordinate_score).toFixed(2) }}
            </span>
            <span v-else class="no-score">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="rank" label="排名" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.rank" :type="getRankType(row.rank)">
              {{ row.rank }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_final" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_final ? 'success' : 'warning'">
              {{ row.is_final ? '终版' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Operation } from '@element-plus/icons-vue'
import { useEvaluationStore } from '@/stores/evaluation'

const evaluationStore = useEvaluationStore()
const selectedCycleId = ref<number | null>(null)
const calculating = ref(false)

const results = computed(() => evaluationStore.results)
const loading = computed(() => evaluationStore.loading)
const cycles = computed(() => evaluationStore.cycles)

const getRankType = (rank: number) => {
  if (rank <= 3) return 'success'
  if (rank <= 10) return 'warning'
  return 'info'
}

const handleCycleChange = () => {
  loadResults()
}

const loadResults = async () => {
  try {
    const params = selectedCycleId.value ? { cycle_id: selectedCycleId.value } : {}
    await evaluationStore.fetchResults(params)
  } catch (error) {
    console.error('加载结果失败:', error)
    ElMessage.error('加载数据失败')
  }
}

const calculateResults = async () => {
  if (!selectedCycleId.value) {
    ElMessage.warning('请先选择考核周期')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      '确定要计算选定周期的考核结果吗？计算将会覆盖原有结果。',
      '确认计算',
      { type: 'warning' }
    )
    
    calculating.value = true
    await evaluationStore.calculateResults(selectedCycleId.value)
    ElMessage.success('结果计算完成')
    await loadResults()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('计算结果失败:', error)
      ElMessage.error('计算失败，请重试')
    }
  } finally {
    calculating.value = false
  }
}

onMounted(async () => {
  try {
    await evaluationStore.fetchCycles()
    await loadResults()
  } catch (error) {
    console.error('初始化失败:', error)
  }
})
</script>

<style scoped>
.evaluation-results {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.score-value {
  font-weight: 500;
  color: #409eff;
}

.no-score {
  color: #c0c4cc;
  font-style: italic;
}
</style>