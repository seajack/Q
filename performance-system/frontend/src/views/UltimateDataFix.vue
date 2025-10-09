<template>
  <div class="ultimate-data-fix">
    <h1>终极数据修复工具</h1>
    
    <div class="fix-section">
      <h2>1. 原始数据分析</h2>
      <el-button type="primary" @click="analyzeRawData" :loading="analyzing">
        分析原始数据
      </el-button>
      
      <div v-if="analysisResult">
        <h3>分析结果:</h3>
        <p>总员工数: {{ analysisResult.totalEmployees }}</p>
        <p>关羽数量: {{ analysisResult.guanYuCount }}</p>
        <p>陈宫数量: {{ analysisResult.chenGongCount }}</p>
        
        <div v-if="analysisResult.guanYuDetails.length > 0">
          <h4>关羽详细信息:</h4>
          <div v-for="(emp, index) in analysisResult.guanYuDetails" :key="emp.id" class="employee-detail">
            <p><strong>关羽 #{{ index + 1 }}</strong></p>
            <p>ID: {{ emp.id }}</p>
            <p>姓名: {{ emp.name }}</p>
            <p>职位: {{ emp.position_name }}</p>
            <p>部门: {{ emp.department_name }}</p>
            <p>创建时间: {{ emp.created_at }}</p>
            <p>更新时间: {{ emp.updated_at }}</p>
          </div>
        </div>
        
        <div v-if="analysisResult.chenGongDetails.length > 0">
          <h4>陈宫详细信息:</h4>
          <div v-for="(emp, index) in analysisResult.chenGongDetails" :key="emp.id" class="employee-detail">
            <p><strong>陈宫 #{{ index + 1 }}</strong></p>
            <p>ID: {{ emp.id }}</p>
            <p>姓名: {{ emp.name }}</p>
            <p>职位: {{ emp.position_name }}</p>
            <p>部门: {{ emp.department_name }}</p>
            <p>创建时间: {{ emp.created_at }}</p>
            <p>更新时间: {{ emp.updated_at }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="fix-section">
      <h2>2. 强制数据修复</h2>
      <el-button type="danger" @click="performUltimateFix" :loading="fixing">
        执行终极修复
      </el-button>
      
      <div v-if="fixResult">
        <h3>修复结果:</h3>
        <p>修复前员工数: {{ fixResult.beforeCount }}</p>
        <p>修复后员工数: {{ fixResult.afterCount }}</p>
        <p>关羽修复后数量: {{ fixResult.guanYuAfterCount }}</p>
        <p>陈宫修复后数量: {{ fixResult.chenGongAfterCount }}</p>
        
        <div v-if="fixResult.success">
          <el-alert type="success" title="修复成功！" :closable="false" />
        </div>
        <div v-else>
          <el-alert type="error" title="修复失败！" :closable="false" />
        </div>
      </div>
    </div>
    
    <div class="fix-section">
      <h2>3. 连接线验证</h2>
      <el-button type="success" @click="verifyConnections" :loading="verifying">
        验证连接线
      </el-button>
      
      <div v-if="connectionVerification">
        <h3>连接线验证结果:</h3>
        <div v-for="result in connectionVerification" :key="result.name" class="connection-result">
          <h4>{{ result.name }} 的连接线验证:</h4>
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
    
    <div class="fix-section">
      <h2>4. 数据库修复建议</h2>
      <div class="database-fix-suggestions">
        <h3>如果前端修复无效，请执行以下数据库操作:</h3>
        <div class="sql-commands">
          <h4>1. 查找重复的关羽记录:</h4>
          <pre><code>SELECT * FROM employees WHERE name LIKE '%关羽%' ORDER BY id;</code></pre>
          
          <h4>2. 查找重复的陈宫记录:</h4>
          <pre><code>SELECT * FROM employees WHERE name LIKE '%陈宫%' ORDER BY id;</code></pre>
          
          <h4>3. 删除重复的关羽记录 (保留ID最小的):</h4>
          <pre><code>DELETE FROM employees 
WHERE name LIKE '%关羽%' 
AND id NOT IN (
  SELECT MIN(id) FROM employees WHERE name LIKE '%关羽%'
);</code></pre>
          
          <h4>4. 删除重复的陈宫记录 (保留ID最小的):</h4>
          <pre><code>DELETE FROM employees 
WHERE name LIKE '%陈宫%' 
AND id NOT IN (
  SELECT MIN(id) FROM employees WHERE name LIKE '%陈宫%'
);</code></pre>
          
          <h4>5. 验证修复结果:</h4>
          <pre><code>SELECT COUNT(*) FROM employees WHERE name LIKE '%关羽%';
SELECT COUNT(*) FROM employees WHERE name LIKE '%陈宫%';</code></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useEvaluationStore } from '@/stores/evaluation'
import { ElMessage } from 'element-plus'

const evaluationStore = useEvaluationStore()

const analyzing = ref(false)
const fixing = ref(false)
const verifying = ref(false)
const analysisResult = ref(null)
const fixResult = ref(null)
const connectionVerification = ref([])

// 分析原始数据
const analyzeRawData = async () => {
  analyzing.value = true
  
  try {
    await evaluationStore.fetchEmployees()
    const employees = evaluationStore.employees
    
    const guanYuEmployees = employees.filter(emp => emp.name?.includes('关羽'))
    const chenGongEmployees = employees.filter(emp => emp.name?.includes('陈宫'))
    
    analysisResult.value = {
      totalEmployees: employees.length,
      guanYuCount: guanYuEmployees.length,
      chenGongCount: chenGongEmployees.length,
      guanYuDetails: guanYuEmployees,
      chenGongDetails: chenGongEmployees
    }
    
    console.log('原始数据分析结果:', analysisResult.value)
    ElMessage.success('数据分析完成')
  } catch (error) {
    console.error('数据分析失败:', error)
    ElMessage.error('数据分析失败')
  } finally {
    analyzing.value = false
  }
}

// 执行终极修复
const performUltimateFix = async () => {
  fixing.value = true
  
  try {
    await evaluationStore.fetchEmployees()
    const rawEmployees = evaluationStore.employees
    
    // 记录修复前的数据
    const beforeCount = rawEmployees.length
    const guanYuBefore = rawEmployees.filter(emp => emp.name?.includes('关羽'))
    const chenGongBefore = rawEmployees.filter(emp => emp.name?.includes('陈宫'))
    
    console.log('修复前数据:', {
      total: beforeCount,
      guanYu: guanYuBefore.length,
      chenGong: chenGongBefore.length
    })
    
    // 超强制修复：直接修改员工数据
    const fixedEmployees = []
    let guanYuFound = false
    let chenGongFound = false
    
    // 第一遍：只处理关羽和陈宫，确保各只有一个
    rawEmployees.forEach((emp, index) => {
      const name = emp.name
      console.log(`第一遍处理员工 ${index + 1}:`, name, emp.id)
      
      if (name?.includes('关羽') && !guanYuFound) {
        fixedEmployees.push(emp)
        guanYuFound = true
        console.log('✅ 第一遍保留关羽:', emp.name, emp.id)
      } else if (name?.includes('陈宫') && !chenGongFound) {
        fixedEmployees.push(emp)
        chenGongFound = true
        console.log('✅ 第一遍保留陈宫:', emp.name, emp.id)
      } else if (name?.includes('关羽') && guanYuFound) {
        console.log('❌ 第一遍跳过重复关羽:', emp.name, emp.id)
      } else if (name?.includes('陈宫') && chenGongFound) {
        console.log('❌ 第一遍跳过重复陈宫:', emp.name, emp.id)
      }
    })
    
    // 第二遍：处理其他员工
    const processedNames = new Set(['关羽', '陈宫'])
    rawEmployees.forEach((emp, index) => {
      const name = emp.name
      if (!name?.includes('关羽') && !name?.includes('陈宫')) {
        if (!processedNames.has(name)) {
          fixedEmployees.push(emp)
          processedNames.add(name)
          console.log('✅ 第二遍保留其他员工:', emp.name, emp.id)
        } else {
          console.log('❌ 第二遍跳过重复其他员工:', emp.name, emp.id)
        }
      }
    })
    
    // 强制更新员工数据
    evaluationStore.employees = fixedEmployees
    
    const afterCount = fixedEmployees.length
    const guanYuAfter = fixedEmployees.filter(emp => emp.name?.includes('关羽'))
    const chenGongAfter = fixedEmployees.filter(emp => emp.name?.includes('陈宫'))
    
    fixResult.value = {
      beforeCount,
      afterCount,
      guanYuAfterCount: guanYuAfter.length,
      chenGongAfterCount: chenGongAfter.length,
      success: guanYuAfter.length === 1 && chenGongAfter.length === 1
    }
    
    console.log('修复后数据:', {
      total: afterCount,
      guanYu: guanYuAfter.length,
      chenGong: chenGongAfter.length,
      success: fixResult.value.success
    })
    
    if (fixResult.value.success) {
      ElMessage.success('数据修复成功！')
    } else {
      ElMessage.error('数据修复失败！')
    }
  } catch (error) {
    console.error('数据修复失败:', error)
    ElMessage.error('数据修复失败')
  } finally {
    fixing.value = false
  }
}

// 验证连接线
const verifyConnections = async () => {
  verifying.value = true
  
  try {
    await evaluationStore.fetchTasks()
    const tasks = evaluationStore.tasks
    const employees = evaluationStore.employees
    
    // 生成节点
    const nodes = employees.filter(emp => 
      emp.name?.includes('关羽') || emp.name?.includes('陈宫')
    )
    
    // 生成连接线
    const connections = []
    tasks.forEach(task => {
      const evaluator = employees.find(emp => emp.id === task.evaluator)
      const evaluatee = employees.find(emp => emp.id === task.evaluatee)
      
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
    
    // 验证关羽的连接线
    const guanYuConnections = connections.filter(conn => 
      conn.fromName?.includes('关羽') || conn.toName?.includes('关羽')
    )
    
    // 验证陈宫的连接线
    const chenGongConnections = connections.filter(conn => 
      conn.fromName?.includes('陈宫') || conn.toName?.includes('陈宫')
    )
    
    connectionVerification.value = [
      {
        name: '关羽',
        nodeCount: employees.filter(emp => emp.name?.includes('关羽')).length,
        connectionCount: guanYuConnections.length,
        status: guanYuConnections.length > 0 ? '有连接线' : '无连接线',
        connections: guanYuConnections
      },
      {
        name: '陈宫',
        nodeCount: employees.filter(emp => emp.name?.includes('陈宫')).length,
        connectionCount: chenGongConnections.length,
        status: chenGongConnections.length > 0 ? '有连接线' : '无连接线',
        connections: chenGongConnections
      }
    ]
    
    console.log('连接线验证结果:', connectionVerification.value)
    ElMessage.success('连接线验证完成')
  } catch (error) {
    console.error('连接线验证失败:', error)
    ElMessage.error('连接线验证失败')
  } finally {
    verifying.value = false
  }
}
</script>

<style scoped>
.ultimate-data-fix {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.fix-section {
  margin: 30px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.employee-detail {
  margin: 15px 0;
  padding: 15px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
}

.employee-detail p {
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

.database-fix-suggestions {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.database-fix-suggestions h3 {
  margin: 0 0 15px 0;
  color: #856404;
}

.database-fix-suggestions h4 {
  margin: 15px 0 10px 0;
  color: #856404;
}

.sql-commands {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 15px;
  margin: 10px 0;
}

.sql-commands pre {
  margin: 10px 0;
  padding: 10px;
  background: #2d3748;
  color: #e2e8f0;
  border-radius: 4px;
  overflow-x: auto;
}

.sql-commands code {
  font-family: 'Courier New', monospace;
  font-size: 14px;
}
</style>