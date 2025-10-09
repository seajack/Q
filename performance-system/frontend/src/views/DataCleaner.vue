<template>
  <div class="data-cleaner">
    <h1>数据清理工具</h1>
    
    <div class="cleaner-section">
      <h2>1. 原始数据检查</h2>
      <p>员工总数: {{ rawEmployees.length }}</p>
      <p>任务总数: {{ tasks.length }}</p>
      
      <h3>关羽员工 ({{ guanYuRaw.length }}个):</h3>
      <div v-for="(emp, index) in guanYuRaw" :key="emp.id" class="employee-card">
        <p><strong>关羽 #{{ index + 1 }}</strong></p>
        <p>ID: {{ emp.id }}</p>
        <p>姓名: {{ emp.name }}</p>
        <p>职位: {{ emp.position_name }}</p>
        <p>部门: {{ emp.department_name }}</p>
        <p>创建时间: {{ emp.created_at }}</p>
      </div>
      
      <h3>陈宫员工 ({{ chenGongRaw.length }}个):</h3>
      <div v-for="(emp, index) in chenGongRaw" :key="emp.id" class="employee-card">
        <p><strong>陈宫 #{{ index + 1 }}</strong></p>
        <p>ID: {{ emp.id }}</p>
        <p>姓名: {{ emp.name }}</p>
        <p>职位: {{ emp.position_name }}</p>
        <p>部门: {{ emp.department_name }}</p>
        <p>创建时间: {{ emp.created_at }}</p>
      </div>
    </div>
    
    <div class="cleaner-section">
      <h2>2. 强制去重处理</h2>
      <el-button type="primary" @click="performForceDeduplication" :loading="cleaning">
        执行强制去重
      </el-button>
      
      <div v-if="cleanedEmployees.length > 0">
        <h3>去重后数据:</h3>
        <p>去重后员工总数: {{ cleanedEmployees.length }}</p>
        
        <h4>关羽员工 ({{ guanYuCleaned.length }}个):</h4>
        <div v-for="(emp, index) in guanYuCleaned" :key="emp.id" class="employee-card cleaned">
          <p><strong>关羽 #{{ index + 1 }}</strong></p>
          <p>ID: {{ emp.id }}</p>
          <p>姓名: {{ emp.name }}</p>
          <p>职位: {{ emp.position_name }}</p>
          <p>部门: {{ emp.department_name }}</p>
        </div>
        
        <h4>陈宫员工 ({{ chenGongCleaned.length }}个):</h4>
        <div v-for="(emp, index) in chenGongCleaned" :key="emp.id" class="employee-card cleaned">
          <p><strong>陈宫 #{{ index + 1 }}</strong></p>
          <p>ID: {{ emp.id }}</p>
          <p>姓名: {{ emp.name }}</p>
          <p>职位: {{ emp.position_name }}</p>
          <p>部门: {{ emp.department_name }}</p>
        </div>
      </div>
    </div>
    
    <div class="cleaner-section">
      <h2>3. 连接线测试</h2>
      <el-button type="success" @click="testConnections" :loading="testing">
        测试连接线生成
      </el-button>
      
      <div v-if="connectionResults.length > 0">
        <h3>连接线测试结果:</h3>
        <div v-for="result in connectionResults" :key="result.name" class="connection-result">
          <h4>{{ result.name }} 的连接线:</h4>
          <p>节点数量: {{ result.nodeCount }}</p>
          <p>连接线数量: {{ result.connectionCount }}</p>
          <p>状态: {{ result.status }}</p>
          <div v-if="result.connections.length > 0">
            <p>连接详情:</p>
            <ul>
              <li v-for="conn in result.connections" :key="conn.id">
                {{ conn.fromName }} → {{ conn.toName }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    
    <div class="cleaner-section">
      <h2>4. 数据修复建议</h2>
      <div v-if="guanYuRaw.length > 1 || chenGongRaw.length > 1" class="fix-suggestions">
        <h3>发现重复数据，建议修复方案:</h3>
        <ol>
          <li><strong>数据库层面修复:</strong>
            <ul>
              <li>检查数据库中的员工表，删除重复的关羽和陈宫记录</li>
              <li>保留ID最小的记录，删除其他重复记录</li>
              <li>更新相关的任务数据，确保员工ID引用正确</li>
            </ul>
          </li>
          <li><strong>代码层面修复:</strong>
            <ul>
              <li>在数据加载时强制去重</li>
              <li>使用员工ID作为唯一标识符</li>
              <li>添加数据验证逻辑</li>
            </ul>
          </li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useEvaluationStore } from '@/stores/evaluation'
import { ElMessage } from 'element-plus'

const evaluationStore = useEvaluationStore()

const rawEmployees = ref([])
const tasks = ref([])
const cleanedEmployees = ref([])
const cleaning = ref(false)
const testing = ref(false)
const connectionResults = ref([])

// 计算属性
const guanYuRaw = computed(() => 
  rawEmployees.value.filter(emp => emp.name?.includes('关羽'))
)

const chenGongRaw = computed(() => 
  rawEmployees.value.filter(emp => emp.name?.includes('陈宫'))
)

const guanYuCleaned = computed(() => 
  cleanedEmployees.value.filter(emp => emp.name?.includes('关羽'))
)

const chenGongCleaned = computed(() => 
  cleanedEmployees.value.filter(emp => emp.name?.includes('陈宫'))
)

// 加载数据
const loadData = async () => {
  try {
    await evaluationStore.fetchEmployees()
    await evaluationStore.fetchTasks()
    
    rawEmployees.value = evaluationStore.employees
    tasks.value = evaluationStore.tasks
    
    console.log('原始员工数据:', rawEmployees.value)
    console.log('关羽原始数据:', guanYuRaw.value)
    console.log('陈宫原始数据:', chenGongRaw.value)
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

// 强制去重处理
const performForceDeduplication = async () => {
  cleaning.value = true
  
  try {
    // 方法1: 按姓名去重，保留第一个
    const nameMap = new Map()
    rawEmployees.value.forEach(emp => {
      if (!nameMap.has(emp.name)) {
        nameMap.set(emp.name, emp)
      }
    })
    
    // 方法2: 特殊处理关羽和陈宫，强制只保留一个
    const uniqueEmployees = Array.from(nameMap.values())
    
    // 找到关羽，只保留第一个
    const guanYuEmployees = uniqueEmployees.filter(emp => emp.name?.includes('关羽'))
    if (guanYuEmployees.length > 0) {
      const firstGuanYu = guanYuEmployees[0]
      // 移除所有关羽
      const filteredEmployees = uniqueEmployees.filter(emp => !emp.name?.includes('关羽'))
      // 只添加第一个关羽
      filteredEmployees.push(firstGuanYu)
      uniqueEmployees.splice(0, uniqueEmployees.length, ...filteredEmployees)
    }
    
    // 找到陈宫，只保留第一个
    const chenGongEmployees = uniqueEmployees.filter(emp => emp.name?.includes('陈宫'))
    if (chenGongEmployees.length > 0) {
      const firstChenGong = chenGongEmployees[0]
      // 移除所有陈宫
      const filteredEmployees = uniqueEmployees.filter(emp => !emp.name?.includes('陈宫'))
      // 只添加第一个陈宫
      filteredEmployees.push(firstChenGong)
      uniqueEmployees.splice(0, uniqueEmployees.length, ...filteredEmployees)
    }
    
    cleanedEmployees.value = uniqueEmployees
    
    console.log('去重处理完成:')
    console.log('原始员工数量:', rawEmployees.value.length)
    console.log('去重后员工数量:', cleanedEmployees.value.length)
    console.log('关羽去重后:', guanYuCleaned.value)
    console.log('陈宫去重后:', chenGongCleaned.value)
    
    ElMessage.success('去重处理完成')
  } catch (error) {
    console.error('去重处理失败:', error)
    ElMessage.error('去重处理失败')
  } finally {
    cleaning.value = false
  }
}

// 测试连接线生成
const testConnections = async () => {
  testing.value = true
  connectionResults.value = []
  
  try {
    // 使用去重后的员工数据
    const evaluatorMap = new Map()
    const evaluateeMap = new Map()
    
    // 生成节点
    cleanedEmployees.value.forEach(emp => {
      if (emp.name?.includes('关羽') || emp.name?.includes('陈宫')) {
        evaluatorMap.set(emp.id, {
          id: emp.id,
          name: emp.name,
          position: emp.position_name,
          department: emp.department_name,
          status: 'active',
          x: 100,
          y: 100,
          selected: false
        })
      }
    })
    
    // 生成连接线
    const connections = []
    tasks.value.forEach(task => {
      const evaluator = evaluatorMap.get(task.evaluator)
      const evaluatee = evaluatorMap.get(task.evaluatee)
      
      if (evaluator && evaluatee) {
        connections.push({
          id: `${task.evaluator}-${task.evaluatee}`,
          fromName: evaluator.name,
          toName: evaluatee.name,
          fromId: task.evaluator,
          toId: task.evaluatee
        })
      }
    })
    
    // 测试关羽的连接线
    const guanYuConnections = connections.filter(conn => 
      conn.fromName?.includes('关羽') || conn.toName?.includes('关羽')
    )
    
    // 测试陈宫的连接线
    const chenGongConnections = connections.filter(conn => 
      conn.fromName?.includes('陈宫') || conn.toName?.includes('陈宫')
    )
    
    connectionResults.value = [
      {
        name: '关羽',
        nodeCount: guanYuCleaned.value.length,
        connectionCount: guanYuConnections.length,
        status: guanYuConnections.length > 0 ? '有连接线' : '无连接线',
        connections: guanYuConnections
      },
      {
        name: '陈宫',
        nodeCount: chenGongCleaned.value.length,
        connectionCount: chenGongConnections.length,
        status: chenGongConnections.length > 0 ? '有连接线' : '无连接线',
        connections: chenGongConnections
      }
    ]
    
    console.log('连接线测试结果:', connectionResults.value)
    ElMessage.success('连接线测试完成')
  } catch (error) {
    console.error('连接线测试失败:', error)
    ElMessage.error('连接线测试失败')
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.data-cleaner {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.cleaner-section {
  margin: 30px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.employee-card {
  margin: 15px 0;
  padding: 15px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
}

.employee-card.cleaned {
  background: #d1edff;
  border: 1px solid #74c0fc;
}

.employee-card p {
  margin: 5px 0;
  background: transparent;
  border: none;
  padding: 2px 0;
}

.connection-result {
  margin: 15px 0;
  padding: 15px;
  background: #e8f5e8;
  border: 1px solid #28a745;
  border-radius: 8px;
}

.connection-result h4 {
  margin: 0 0 10px 0;
  color: #155724;
}

.connection-result p {
  margin: 5px 0;
  background: transparent;
  border: none;
}

.connection-result ul {
  margin: 10px 0;
  padding-left: 20px;
}

.connection-result li {
  margin: 5px 0;
  color: #155724;
}

.fix-suggestions {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.fix-suggestions h3 {
  margin: 0 0 15px 0;
  color: #856404;
}

.fix-suggestions ol {
  margin: 10px 0;
  padding-left: 20px;
}

.fix-suggestions li {
  margin: 10px 0;
  color: #856404;
}

.fix-suggestions ul {
  margin: 10px 0;
  padding-left: 20px;
}

.fix-suggestions ul li {
  margin: 5px 0;
  color: #856404;
}
</style>
