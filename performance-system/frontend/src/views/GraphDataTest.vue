<template>
  <div class="graph-data-test">
    <h2>图形化考核任务面板数据测试</h2>
    
    <div class="test-section">
      <h3>考核周期数据</h3>
      <pre>{{ JSON.stringify(cycles, null, 2) }}</pre>
    </div>
    
    <div class="test-section">
      <h3>员工数据</h3>
      <pre>{{ JSON.stringify(employees.slice(0, 5), null, 2) }}</pre>
    </div>
    
    <div class="test-section">
      <h3>考核任务数据</h3>
      <pre>{{ JSON.stringify(tasks.slice(0, 5), null, 2) }}</pre>
    </div>
    
    <div class="test-section">
      <h3>图形化考核人数据</h3>
      <pre>{{ JSON.stringify(evaluators, null, 2) }}</pre>
    </div>
    
    <div class="test-section">
      <h3>图形化被考核人数据</h3>
      <pre>{{ JSON.stringify(evaluatees, null, 2) }}</pre>
    </div>
    
    <div class="test-section">
      <h3>连接线数据</h3>
      <pre>{{ JSON.stringify(connections, null, 2) }}</pre>
    </div>
    
    <div class="test-section">
      <h3>加载状态</h3>
      <p>加载中: {{ loading }}</p>
      <p>错误: {{ error }}</p>
    </div>
    
    <div class="test-actions">
      <el-button type="primary" @click="loadData" :loading="loading">
        重新加载数据
      </el-button>
      <el-button @click="goToGraph">
        查看图形化面板
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useEvaluationStore } from '@/stores/evaluation'
import type { EvaluationTask, EvaluationCycle, Employee } from '@/types'

const router = useRouter()
const evaluationStore = useEvaluationStore()

const loading = ref(false)
const error = ref('')
const cycles = ref<EvaluationCycle[]>([])
const employees = ref<Employee[]>([])
const tasks = ref<EvaluationTask[]>([])
const evaluators = ref<any[]>([])
const evaluatees = ref<any[]>([])
const connections = ref<any[]>([])

const loadData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 加载考核周期
    await evaluationStore.fetchCycles()
    cycles.value = evaluationStore.cycles
    
    // 加载员工数据
    await evaluationStore.fetchEmployees()
    employees.value = evaluationStore.employees
    
    // 加载考核任务
    await evaluationStore.fetchTasks()
    tasks.value = evaluationStore.tasks
    
    // 处理图形化数据
    processGraphData()
    
  } catch (err: any) {
    error.value = err.message || '加载数据失败'
    console.error('加载数据失败:', err)
  } finally {
    loading.value = false
  }
}

// 处理图形化数据
const processGraphData = () => {
  // 处理考核人数据
  const evaluatorMap = new Map()
  const evaluateeMap = new Map()
  
  tasks.value.forEach((task, index) => {
    // 处理考核人
    if (!evaluatorMap.has(task.evaluator)) {
      const evaluator = employees.value.find(emp => emp.id === task.evaluator)
      if (evaluator) {
        evaluatorMap.set(task.evaluator, {
          id: task.evaluator,
          name: evaluator.name,
          position: evaluator.position_name,
          department: evaluator.department_name,
          status: 'active',
          x: 200 + (evaluatorMap.size % 3) * 150,
          y: 200 + Math.floor(evaluatorMap.size / 3) * 200,
          selected: false
        })
      }
    }
    
    
    // 处理被考核人
    if (!evaluateeMap.has(task.evaluatee)) {
      const evaluatee = employees.value.find(emp => emp.id === task.evaluatee)
      if (evaluatee) {
        evaluateeMap.set(task.evaluatee, {
          id: task.evaluatee,
          name: evaluatee.name,
          position: evaluatee.position_name,
          department: evaluatee.department_name,
          status: task.status,
          x: 600 + (evaluateeMap.size % 3) * 150,
          y: 200 + Math.floor(evaluateeMap.size / 3) * 200,
          selected: false
        })
      }
    }
  })
  
  evaluators.value = Array.from(evaluatorMap.values())
  evaluatees.value = Array.from(evaluateeMap.values())
  
  // 生成连接线数据
  connections.value = tasks.value.map((task, index) => {
    const evaluator = evaluators.value.find(e => e.id === task.evaluator)
    const evaluatee = evaluatees.value.find(e => e.id === task.evaluatee)
    
    if (evaluator && evaluatee) {
      return {
        id: `conn-${task.id}`,
        taskId: task.id,
        from: { x: evaluator.x, y: evaluator.y },
        to: { x: evaluatee.x, y: evaluatee.y },
        status: task.status,
        dashed: task.status === 'completed',
        relationType: task.relation_type
      }
    }
    return null
  }).filter(Boolean)
}

const goToGraph = () => {
  router.push('/evaluation-graph')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.graph-data-test {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.test-section h3 {
  margin: 0 0 16px 0;
  color: #1e293b;
  font-size: 18px;
}

.test-section pre {
  background: #f8fafc;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  overflow-x: auto;
  font-size: 12px;
  line-height: 1.4;
  max-height: 300px;
  overflow-y: auto;
}

.test-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}
</style>
