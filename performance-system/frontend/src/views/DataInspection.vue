<template>
  <div class="data-inspection">
    <h1>数据检查页面</h1>
    
    <div class="data-section">
      <h2>员工数据 ({{ employees.length }})</h2>
      <div class="data-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>姓名</th>
              <th>职位</th>
              <th>部门</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="emp in employees" :key="emp.id">
              <td>{{ emp.id }}</td>
              <td>{{ emp.name }}</td>
              <td>{{ emp.position_name }}</td>
              <td>{{ emp.department_name }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div class="data-section">
      <h2>任务数据 ({{ tasks.length }})</h2>
      <div class="data-table">
        <table>
          <thead>
            <tr>
              <th>任务ID</th>
              <th>考核人ID</th>
              <th>考核人姓名</th>
              <th>被考核人ID</th>
              <th>被考核人姓名</th>
              <th>关系类型</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in tasks" :key="task.id">
              <td>{{ task.id }}</td>
              <td>{{ task.evaluator }}</td>
              <td>{{ task.evaluator_name }}</td>
              <td>{{ task.evaluatee }}</td>
              <td>{{ task.evaluatee_name }}</td>
              <td>{{ task.relation_type }}</td>
              <td>{{ task.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div class="data-section">
      <h2>关羽相关任务</h2>
      <div class="data-table">
        <table>
          <thead>
            <tr>
              <th>任务ID</th>
              <th>考核人</th>
              <th>被考核人</th>
              <th>关系类型</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in guanYuTasks" :key="task.id">
              <td>{{ task.id }}</td>
              <td>{{ task.evaluator_name }}</td>
              <td>{{ task.evaluatee_name }}</td>
              <td>{{ task.relation_type }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div class="data-section">
      <h2>陈宫相关任务</h2>
      <div class="data-table">
        <table>
          <thead>
            <tr>
              <th>任务ID</th>
              <th>考核人</th>
              <th>被考核人</th>
              <th>关系类型</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in chenGongTasks" :key="task.id">
              <td>{{ task.id }}</td>
              <td>{{ task.evaluator_name }}</td>
              <td>{{ task.evaluatee_name }}</td>
              <td>{{ task.relation_type }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div class="data-section">
      <h2>生成的节点数据</h2>
      <div class="node-data">
        <h3>考核人节点 ({{ evaluators.length }})</h3>
        <div class="node-list">
          <div v-for="node in evaluators" :key="node.id" class="node-item">
            <strong>{{ node.name }}</strong> - {{ node.position }} ({{ node.department }})
            <br>位置: ({{ node.x }}, {{ node.y }})
          </div>
        </div>
        
        <h3>被考核人节点 ({{ evaluatees.length }})</h3>
        <div class="node-list">
          <div v-for="node in evaluatees" :key="node.id" class="node-item">
            <strong>{{ node.name }}</strong> - {{ node.position }} ({{ node.department }})
            <br>位置: ({{ node.x }}, {{ node.y }})
          </div>
        </div>
      </div>
    </div>
    
    <div class="data-section">
      <h2>生成的连接线数据</h2>
      <div class="connection-data">
        <div v-for="conn in connections" :key="conn.id" class="connection-item">
          <strong>{{ conn.id }}</strong>
          <br>从: {{ conn.from.id }} ({{ conn.from.x }}, {{ conn.from.y }})
          <br>到: {{ conn.to.id }} ({{ conn.to.x }}, {{ conn.to.y }})
          <br>状态: {{ conn.status }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useEvaluationStore } from '@/stores/evaluation'

const evaluationStore = useEvaluationStore()

const employees = ref([])
const tasks = ref([])
const evaluators = ref([])
const evaluatees = ref([])
const connections = ref([])

const guanYuTasks = ref([])
const chenGongTasks = ref([])

const loadData = async () => {
  try {
    await evaluationStore.fetchEmployees()
    employees.value = evaluationStore.employees
    
    await evaluationStore.fetchTasks()
    tasks.value = evaluationStore.tasks
    
    // 筛选关羽和陈宫相关任务
    guanYuTasks.value = tasks.value.filter(task => 
      task.evaluator_name?.includes('关羽') || task.evaluatee_name?.includes('关羽')
    )
    
    chenGongTasks.value = tasks.value.filter(task => 
      task.evaluator_name?.includes('陈宫') || task.evaluatee_name?.includes('陈宫')
    )
    
    // 处理图形化数据
    processGraphData()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const processGraphData = () => {
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
          x: 150 + (evaluatorMap.size % 4) * 200,
          y: 150 + Math.floor(evaluatorMap.size / 4) * 150,
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
          x: 650 + (evaluateeMap.size % 4) * 200,
          y: 150 + Math.floor(evaluateeMap.size / 4) * 150,
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
        from: { id: evaluator.id, x: evaluator.x, y: evaluator.y },
        to: { id: evaluatee.id, x: evaluatee.x, y: evaluatee.y },
        status: task.status,
        dashed: task.status === 'completed',
        relationType: task.relation_type
      }
    }
    return null
  }).filter(Boolean)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.data-inspection {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.data-section {
  margin-bottom: 30px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
}

.data-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  border: 1px solid #e2e8f0;
  padding: 8px;
  text-align: left;
}

th {
  background: #f8fafc;
  font-weight: 600;
}

.node-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 10px;
}

.node-item {
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: #f8fafc;
}

.connection-data {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 10px;
}

.connection-item {
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: #f0f9ff;
}
</style>
