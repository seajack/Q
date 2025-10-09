<template>
  <div class="simple-data-test">
    <h1>简单数据测试</h1>
    
    <div class="test-section">
      <h2>1. 原始数据检查</h2>
      <p>员工总数: {{ employees.length }}</p>
      <p>任务总数: {{ tasks.length }}</p>
      
      <h3>关羽相关数据 ({{ guanYuEmployees.length }}个):</h3>
      <div v-for="(emp, index) in guanYuEmployees" :key="emp.id" class="employee-item">
        <p><strong>员工 #{{ index + 1 }}</strong></p>
        <p>员工ID: {{ emp.id }}</p>
        <p>姓名: {{ emp.name }}</p>
        <p>职位: {{ emp.position_name }}</p>
        <p>部门: {{ emp.department_name }}</p>
      </div>
      <p v-if="guanYuEmployees.length === 0">未找到关羽员工数据</p>
      
      <h3>陈宫相关数据 ({{ chenGongEmployees.length }}个):</h3>
      <div v-for="(emp, index) in chenGongEmployees" :key="emp.id" class="employee-item">
        <p><strong>员工 #{{ index + 1 }}</strong></p>
        <p>员工ID: {{ emp.id }}</p>
        <p>姓名: {{ emp.name }}</p>
        <p>职位: {{ emp.position_name }}</p>
        <p>部门: {{ emp.department_name }}</p>
      </div>
      <p v-if="chenGongEmployees.length === 0">未找到陈宫员工数据</p>
      
      <div v-if="guanYuEmployees.length > 1 || chenGongEmployees.length > 1" class="duplicate-warning">
        <h4 style="color: red;">⚠️ 发现重复员工数据！</h4>
        <p>这会导致节点生成和连接线问题。需要去重处理。</p>
        
        <h5>重复数据分析：</h5>
        <div v-if="guanYuEmployees.length > 1">
          <p><strong>关羽重复情况：</strong></p>
          <ul>
            <li v-for="(emp, index) in guanYuEmployees" :key="emp.id">
              关羽 #{{ index + 1 }}: ID={{ emp.id }}, 职位={{ emp.position_name }}, 部门={{ emp.department_name }}
            </li>
          </ul>
        </div>
        
        <div v-if="chenGongEmployees.length > 1">
          <p><strong>陈宫重复情况：</strong></p>
          <ul>
            <li v-for="(emp, index) in chenGongEmployees" :key="emp.id">
              陈宫 #{{ index + 1 }}: ID={{ emp.id }}, 职位={{ emp.position_name }}, 部门={{ emp.department_name }}
            </li>
          </ul>
        </div>
        
        <h5>建议解决方案：</h5>
        <ul>
          <li>检查数据库中的员工数据，删除重复记录</li>
          <li>或者在代码中强制去重，只保留第一个记录</li>
          <li>确保任务数据中的员工ID与去重后的员工ID匹配</li>
        </ul>
      </div>
    </div>
    
    <div class="test-section">
      <h2>2. 任务关系检查</h2>
      <h3>关羽作为考核人的任务:</h3>
      <div v-for="task in guanYuAsEvaluator" :key="task.id">
        <p>任务ID: {{ task.id }} - 被考核人: {{ task.evaluatee_name }} (ID: {{ task.evaluatee }})</p>
      </div>
      
      <h3>关羽作为被考核人的任务:</h3>
      <div v-for="task in guanYuAsEvaluatee" :key="task.id">
        <p>任务ID: {{ task.id }} - 考核人: {{ task.evaluator_name }} (ID: {{ task.evaluator }})</p>
      </div>
      
      <h3>陈宫作为考核人的任务:</h3>
      <div v-for="task in chenGongAsEvaluator" :key="task.id">
        <p>任务ID: {{ task.id }} - 被考核人: {{ task.evaluatee_name }} (ID: {{ task.evaluatee }})</p>
      </div>
      
      <h3>陈宫作为被考核人的任务:</h3>
      <div v-for="task in chenGongAsEvaluatee" :key="task.id">
        <p>任务ID: {{ task.id }} - 考核人: {{ task.evaluator_name }} (ID: {{ task.evaluator }})</p>
      </div>
    </div>
    
    <div class="test-section">
      <h2>3. 节点生成检查</h2>
      <h3>关羽节点:</h3>
      <div v-if="guanYuNode">
        <p>节点ID: {{ guanYuNode.id }}</p>
        <p>姓名: {{ guanYuNode.name }}</p>
        <p>位置: ({{ guanYuNode.x }}, {{ guanYuNode.y }})</p>
      </div>
      <p v-else>未生成关羽节点</p>
      
      <h3>陈宫节点:</h3>
      <div v-if="chenGongNode">
        <p>节点ID: {{ chenGongNode.id }}</p>
        <p>姓名: {{ chenGongNode.name }}</p>
        <p>位置: ({{ chenGongNode.x }}, {{ chenGongNode.y }})</p>
      </div>
      <p v-else>未生成陈宫节点</p>
    </div>
    
    <div class="test-section">
      <h2>4. 连接线检查</h2>
      <h3>关羽相关连接线:</h3>
      <div v-for="conn in guanYuConnections" :key="conn.id">
        <p>连接线ID: {{ conn.id }}</p>
        <p>从: {{ conn.from.id }} 到: {{ conn.to.id }}</p>
        <p>状态: {{ conn.status }}</p>
      </div>
      
      <h3>陈宫相关连接线:</h3>
      <div v-for="conn in chenGongConnections" :key="conn.id">
        <p>连接线ID: {{ conn.id }}</p>
        <p>从: {{ conn.from.id }} 到: {{ conn.to.id }}</p>
        <p>状态: {{ conn.status }}</p>
      </div>
    </div>
    
    <div class="test-section">
      <h2>5. 关羽和陈宫之间的直接关系</h2>
      <div v-for="task in guanYuChenGongTasks" :key="task.id">
        <p>任务ID: {{ task.id }}</p>
        <p>考核人: {{ task.evaluator_name }} (ID: {{ task.evaluator }})</p>
        <p>被考核人: {{ task.evaluatee_name }} (ID: {{ task.evaluatee }})</p>
        <p>关系类型: {{ task.relation_type }}</p>
        <p>状态: {{ task.status }}</p>
      </div>
      <p v-if="guanYuChenGongTasks.length === 0">关羽和陈宫之间没有直接的考核关系（这是正常的）</p>
    </div>
    
    <div class="test-section">
      <h2>6. 关羽的所有考核关系</h2>
      <h3>关羽作为考核人的任务 ({{ guanYuAsEvaluator.length }}个):</h3>
      <div v-for="task in guanYuAsEvaluator" :key="task.id" class="task-item">
        <p><strong>任务ID:</strong> {{ task.id }}</p>
        <p><strong>被考核人:</strong> {{ task.evaluatee_name }} (ID: {{ task.evaluatee }})</p>
        <p><strong>关系类型:</strong> {{ task.relation_type }}</p>
        <p><strong>状态:</strong> {{ task.status }}</p>
        <p><strong>考核码:</strong> {{ task.evaluation_code }}</p>
      </div>
      
      <h3>关羽作为被考核人的任务 ({{ guanYuAsEvaluatee.length }}个):</h3>
      <div v-for="task in guanYuAsEvaluatee" :key="task.id" class="task-item">
        <p><strong>任务ID:</strong> {{ task.id }}</p>
        <p><strong>考核人:</strong> {{ task.evaluator_name }} (ID: {{ task.evaluator }})</p>
        <p><strong>关系类型:</strong> {{ task.relation_type }}</p>
        <p><strong>状态:</strong> {{ task.status }}</p>
        <p><strong>考核码:</strong> {{ task.evaluation_code }}</p>
      </div>
    </div>
    
    <div class="test-section">
      <h2>7. 陈宫的所有考核关系</h2>
      <h3>陈宫作为考核人的任务 ({{ chenGongAsEvaluator.length }}个):</h3>
      <div v-for="task in chenGongAsEvaluator" :key="task.id" class="task-item">
        <p><strong>任务ID:</strong> {{ task.id }}</p>
        <p><strong>被考核人:</strong> {{ task.evaluatee_name }} (ID: {{ task.evaluatee }})</p>
        <p><strong>关系类型:</strong> {{ task.relation_type }}</p>
        <p><strong>状态:</strong> {{ task.status }}</p>
        <p><strong>考核码:</strong> {{ task.evaluation_code }}</p>
      </div>
      
      <h3>陈宫作为被考核人的任务 ({{ chenGongAsEvaluatee.length }}个):</h3>
      <div v-for="task in chenGongAsEvaluatee" :key="task.id" class="task-item">
        <p><strong>任务ID:</strong> {{ task.id }}</p>
        <p><strong>考核人:</strong> {{ task.evaluator_name }} (ID: {{ task.evaluator }})</p>
        <p><strong>关系类型:</strong> {{ task.relation_type }}</p>
        <p><strong>状态:</strong> {{ task.status }}</p>
        <p><strong>考核码:</strong> {{ task.evaluation_code }}</p>
      </div>
    </div>
    
    <div class="test-section">
      <h2>8. 连接线生成问题诊断</h2>
      <h3>关羽的连接线问题:</h3>
      <div v-if="guanYuEmployee">
        <p>关羽员工ID: {{ guanYuEmployee.id }}</p>
        <p>关羽节点: {{ guanYuNode ? '已生成' : '未生成' }}</p>
        <p>关羽连接线数量: {{ guanYuConnections.length }}</p>
        <div v-if="guanYuConnections.length === 0">
          <p style="color: red;"><strong>问题：关羽没有连接线！</strong></p>
          <p>可能原因：</p>
          <ul>
            <li>关羽的任务数据存在，但节点生成失败</li>
            <li>关羽的节点生成了，但连接线生成失败</li>
            <li>员工ID和任务中的ID不匹配</li>
          </ul>
        </div>
      </div>
      
      <h3>陈宫的连接线问题:</h3>
      <div v-if="chenGongEmployee">
        <p>陈宫员工ID: {{ chenGongEmployee.id }}</p>
        <p>陈宫节点: {{ chenGongNode ? '已生成' : '未生成' }}</p>
        <p>陈宫连接线数量: {{ chenGongConnections.length }}</p>
        <div v-if="chenGongConnections.length === 0">
          <p style="color: red;"><strong>问题：陈宫没有连接线！</strong></p>
          <p>可能原因：</p>
          <ul>
            <li>陈宫的任务数据存在，但节点生成失败</li>
            <li>陈宫的节点生成了，但连接线生成失败</li>
            <li>员工ID和任务中的ID不匹配</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useEvaluationStore } from '@/stores/evaluation'

const evaluationStore = useEvaluationStore()

const employees = ref([])
const tasks = ref([])
const evaluators = ref([])
const evaluatees = ref([])
const connections = ref([])

// 计算属性
const guanYuEmployees = computed(() => 
  employees.value.filter(emp => emp.name?.includes('关羽'))
)

const chenGongEmployees = computed(() => 
  employees.value.filter(emp => emp.name?.includes('陈宫'))
)

const guanYuEmployee = computed(() => 
  guanYuEmployees.value[0] // 取第一个关羽
)

const chenGongEmployee = computed(() => 
  chenGongEmployees.value[0] // 取第一个陈宫
)

const guanYuAsEvaluator = computed(() => 
  tasks.value.filter(task => task.evaluator_name?.includes('关羽'))
)

const guanYuAsEvaluatee = computed(() => 
  tasks.value.filter(task => task.evaluatee_name?.includes('关羽'))
)

const chenGongAsEvaluator = computed(() => 
  tasks.value.filter(task => task.evaluator_name?.includes('陈宫'))
)

const chenGongAsEvaluatee = computed(() => 
  tasks.value.filter(task => task.evaluatee_name?.includes('陈宫'))
)

const guanYuNode = computed(() => 
  [...evaluators.value, ...evaluatees.value].find(node => node.name?.includes('关羽'))
)

const chenGongNode = computed(() => 
  [...evaluators.value, ...evaluatees.value].find(node => node.name?.includes('陈宫'))
)

const guanYuConnections = computed(() => 
  connections.value.filter(conn => 
    conn.from.id === guanYuEmployee.value?.id || conn.to.id === guanYuEmployee.value?.id
  )
)

const chenGongConnections = computed(() => 
  connections.value.filter(conn => 
    conn.from.id === chenGongEmployee.value?.id || conn.to.id === chenGongEmployee.value?.id
  )
)

const guanYuChenGongTasks = computed(() => 
  tasks.value.filter(task => 
    (task.evaluator_name?.includes('关羽') && task.evaluatee_name?.includes('陈宫')) ||
    (task.evaluator_name?.includes('陈宫') && task.evaluatee_name?.includes('关羽'))
  )
)

const loadData = async () => {
  try {
    console.log('开始加载数据...')
    
    await evaluationStore.fetchEmployees()
    employees.value = evaluationStore.employees
    console.log('员工数据:', employees.value)
    
    await evaluationStore.fetchTasks()
    tasks.value = evaluationStore.tasks
    console.log('任务数据:', tasks.value)
    
    // 处理图形化数据
    processGraphData()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const processGraphData = () => {
  console.log('开始处理图形数据...')
  
  const evaluatorMap = new Map()
  const evaluateeMap = new Map()
  
  tasks.value.forEach((task, index) => {
    console.log(`处理任务 ${index + 1}:`, task)
    
    // 处理考核人
    if (!evaluatorMap.has(task.evaluator)) {
      const evaluator = employees.value.find(emp => emp.id === task.evaluator)
      console.log('查找考核人:', { taskEvaluatorId: task.evaluator, foundEvaluator: evaluator })
      
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
      console.log('查找被考核人:', { taskEvaluateeId: task.evaluatee, foundEvaluatee: evaluatee })
      
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
  
  console.log('生成的考核人:', evaluators.value)
  console.log('生成的被考核人:', evaluatees.value)
  
  // 生成连接线数据
  connections.value = tasks.value.map((task, index) => {
    const evaluator = evaluators.value.find(e => e.id === task.evaluator)
    const evaluatee = evaluatees.value.find(e => e.id === task.evaluatee)
    
    console.log(`处理连接线 ${index + 1}:`, {
      taskId: task.id,
      evaluatorId: task.evaluator,
      evaluateeId: task.evaluatee,
      evaluatorName: task.evaluator_name,
      evaluateeName: task.evaluatee_name,
      foundEvaluator: evaluator,
      foundEvaluatee: evaluatee
    })
    
    if (evaluator && evaluatee) {
      const connection = {
        id: `conn-${task.id}`,
        taskId: task.id,
        from: { id: evaluator.id, x: evaluator.x, y: evaluator.y },
        to: { id: evaluatee.id, x: evaluatee.x, y: evaluatee.y },
        status: task.status,
        dashed: task.status === 'completed',
        relationType: task.relation_type
      }
      console.log('生成连接线:', connection)
      return connection
    } else {
      console.warn('连接线生成失败:', {
        taskId: task.id,
        evaluatorFound: !!evaluator,
        evaluateeFound: !!evaluatee,
        evaluatorId: task.evaluator,
        evaluateeId: task.evaluatee
      })
    }
    return null
  }).filter(Boolean)
  
  console.log('最终连接线数据:', connections.value)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.simple-data-test {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 30px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  background: #f8fafc;
}

h2 {
  color: #1e293b;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 10px;
}

h3 {
  color: #475569;
  margin-top: 15px;
}

p {
  margin: 5px 0;
  padding: 5px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

.task-item {
  margin: 10px 0;
  padding: 15px;
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  border-radius: 8px;
}

.task-item p {
  margin: 3px 0;
  background: transparent;
  border: none;
  padding: 2px 0;
}

ul {
  margin: 10px 0;
  padding-left: 20px;
}

li {
  margin: 5px 0;
  color: #dc2626;
}

.employee-item {
  margin: 10px 0;
  padding: 15px;
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
}

.employee-item p {
  margin: 3px 0;
  background: transparent;
  border: none;
  padding: 2px 0;
}

.duplicate-warning {
  margin: 20px 0;
  padding: 15px;
  background: #fef2f2;
  border: 2px solid #dc2626;
  border-radius: 8px;
}

.duplicate-warning h4 {
  margin: 0 0 10px 0;
}

.duplicate-warning p {
  margin: 5px 0;
  background: transparent;
  border: none;
  color: #dc2626;
}
</style>
