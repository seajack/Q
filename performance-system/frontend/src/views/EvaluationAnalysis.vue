<template>
  <div class="evaluation-analysis">
    <h1>考核关系分析工具</h1>
    
    <div class="analysis-section">
      <h2>1. 员工层级分析</h2>
      <el-button type="primary" @click="analyzeEmployeeLevels" :loading="analyzing">
        分析员工层级
      </el-button>
      
      <div v-if="employeeLevelAnalysis">
        <h3>员工层级分布:</h3>
        <div class="level-stats">
          <div class="level-item">
            <h4>公司领导 (L12-L13):</h4>
            <p>数量: {{ employeeLevelAnalysis.highLevelCount }}</p>
            <div v-for="emp in employeeLevelAnalysis.highLevelEmployees" :key="emp.id" class="employee-item">
              <p>{{ emp.name }} - {{ emp.position_name }} (级别: {{ emp.position_level }})</p>
            </div>
          </div>
          
          <div class="level-item">
            <h4>部门经理 (L9):</h4>
            <p>数量: {{ employeeLevelAnalysis.managerCount }}</p>
            <div v-for="emp in employeeLevelAnalysis.managerEmployees" :key="emp.id" class="employee-item">
              <p>{{ emp.name }} - {{ emp.position_name }} (级别: {{ emp.position_level }})</p>
            </div>
          </div>
          
          <div class="level-item">
            <h4>主管 (L4):</h4>
            <p>数量: {{ employeeLevelAnalysis.supervisorCount }}</p>
            <div v-for="emp in employeeLevelAnalysis.supervisorEmployees" :key="emp.id" class="employee-item">
              <p>{{ emp.name }} - {{ emp.position_name }} (级别: {{ emp.position_level }})</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="analysis-section">
      <h2>2. 考核关系分析</h2>
      <el-button type="success" @click="analyzeEvaluationRelations" :loading="analyzing">
        分析考核关系
      </el-button>
      
      <div v-if="relationAnalysis">
        <h3>考核关系分布:</h3>
        <div class="relation-stats">
          <div class="relation-item">
            <h4>总考核关系数: {{ relationAnalysis.totalRelations }}</h4>
            <p>理论关系数: {{ relationAnalysis.theoreticalRelations }}</p>
            <p>实际关系数: {{ relationAnalysis.actualRelations }}</p>
          </div>
          
          <div class="relation-item">
            <h4>各层级考核关系:</h4>
            <div v-for="(relations, level) in relationAnalysis.levelRelations" :key="level" class="level-relations">
              <h5>{{ level }}:</h5>
              <p>考核人数: {{ relations.evaluatorCount }}</p>
              <p>被考核人数: {{ relations.evaluateeCount }}</p>
              <p>关系数: {{ relations.relationCount }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="analysis-section">
      <h2>3. 诸葛亮考核关系详细分析</h2>
      <el-button type="warning" @click="analyzeZhugeLiangRelations" :loading="analyzing">
        分析诸葛亮考核关系
      </el-button>
      
      <div v-if="zhugeLiangAnalysis">
        <h3>诸葛亮考核关系详情:</h3>
        <div class="zhuge-analysis">
          <div class="zhuge-info">
            <h4>诸葛亮基本信息:</h4>
            <p>姓名: {{ zhugeLiangAnalysis.employee.name }}</p>
            <p>职位: {{ zhugeLiangAnalysis.employee.position_name }}</p>
            <p>级别: {{ zhugeLiangAnalysis.employee.position_level }}</p>
            <p>部门: {{ zhugeLiangAnalysis.employee.department_name }}</p>
          </div>
          
          <div class="zhuge-relations">
            <h4>诸葛亮作为考核人的关系:</h4>
            <p>关系数量: {{ zhugeLiangAnalysis.asEvaluatorCount }}</p>
            <div v-for="task in zhugeLiangAnalysis.asEvaluatorTasks" :key="task.id" class="task-item">
              <p>被考核人: {{ task.evaluatee_name }} ({{ task.evaluatee_position }})</p>
              <p>关系类型: {{ task.relation_type }}</p>
              <p>权重: {{ task.weight }}</p>
            </div>
          </div>
          
          <div class="zhuge-relations">
            <h4>诸葛亮作为被考核人的关系:</h4>
            <p>关系数量: {{ zhugeLiangAnalysis.asEvaluateeCount }}</p>
            <div v-for="task in zhugeLiangAnalysis.asEvaluateeTasks" :key="task.id" class="task-item">
              <p>考核人: {{ task.evaluator_name }} ({{ task.evaluator_position }})</p>
              <p>关系类型: {{ task.relation_type }}</p>
              <p>权重: {{ task.weight }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="analysis-section">
      <h2>4. 其他公司领导考核关系对比</h2>
      <el-button type="info" @click="analyzeOtherLeaders" :loading="analyzing">
        分析其他公司领导
      </el-button>
      
      <div v-if="otherLeadersAnalysis">
        <h3>其他公司领导考核关系:</h3>
        <div v-for="leader in otherLeadersAnalysis" :key="leader.id" class="leader-analysis">
          <h4>{{ leader.name }} ({{ leader.position_name }}):</h4>
          <p>作为考核人的关系数: {{ leader.asEvaluatorCount }}</p>
          <p>作为被考核人的关系数: {{ leader.asEvaluateeCount }}</p>
          <p>总关系数: {{ leader.totalRelations }}</p>
          
          <div v-if="leader.asEvaluatorTasks.length > 0">
            <h5>考核的人员:</h5>
            <div v-for="task in leader.asEvaluatorTasks" :key="task.id" class="task-item">
              <p>{{ task.evaluatee_name }} ({{ task.evaluatee_position }}) - {{ task.relation_type }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="analysis-section">
      <h2>5. 考核关系不平衡原因分析</h2>
      <el-button type="danger" @click="analyzeImbalance" :loading="analyzing">
        分析不平衡原因
      </el-button>
      
      <div v-if="imbalanceAnalysis">
        <h3>不平衡原因分析:</h3>
        <div class="imbalance-reasons">
          <div v-for="reason in imbalanceAnalysis.reasons" :key="reason.type" class="reason-item">
            <h4>{{ reason.title }}:</h4>
            <p>{{ reason.description }}</p>
            <div v-if="reason.examples && reason.examples.length > 0">
              <h5>具体例子:</h5>
              <ul>
                <li v-for="example in reason.examples" :key="example">{{ example }}</li>
              </ul>
            </div>
          </div>
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
const employeeLevelAnalysis = ref(null)
const relationAnalysis = ref(null)
const zhugeLiangAnalysis = ref(null)
const otherLeadersAnalysis = ref(null)
const imbalanceAnalysis = ref(null)

// 分析员工层级
const analyzeEmployeeLevels = async () => {
  analyzing.value = true
  
  try {
    await evaluationStore.fetchEmployees()
    let employees = evaluationStore.employees
    
    // 强制过滤掉关羽和陈宫
    employees = employees.filter(emp => 
      !emp.name?.includes('关羽') && !emp.name?.includes('陈宫')
    )
    
    console.log('过滤前员工数量:', evaluationStore.employees.length)
    console.log('过滤后员工数量:', employees.length)
    
    // 按职位级别分类
    const highLevelEmployees = employees.filter(emp => emp.position_level >= 12)
    const managerEmployees = employees.filter(emp => emp.position_level === 9)
    const supervisorEmployees = employees.filter(emp => emp.position_level === 4)
    
    employeeLevelAnalysis.value = {
      highLevelCount: highLevelEmployees.length,
      highLevelEmployees: highLevelEmployees,
      managerCount: managerEmployees.length,
      managerEmployees: managerEmployees,
      supervisorCount: supervisorEmployees.length,
      supervisorEmployees: supervisorEmployees
    }
    
    console.log('员工层级分析结果:', employeeLevelAnalysis.value)
    ElMessage.success('员工层级分析完成')
  } catch (error) {
    console.error('员工层级分析失败:', error)
    ElMessage.error('员工层级分析失败')
  } finally {
    analyzing.value = false
  }
}

// 分析考核关系
const analyzeEvaluationRelations = async () => {
  analyzing.value = true
  
  try {
    await evaluationStore.fetchTasks()
    let tasks = evaluationStore.tasks
    
    // 强制过滤掉关羽和陈宫的任务
    tasks = tasks.filter(t => 
      !t.evaluator_name?.includes('关羽') && 
      !t.evaluator_name?.includes('陈宫') &&
      !t.evaluatee_name?.includes('关羽') && 
      !t.evaluatee_name?.includes('陈宫')
    )
    
    console.log('过滤前任务数量:', evaluationStore.tasks.length)
    console.log('过滤后任务数量:', tasks.length)
    
    // 计算理论关系数
    const highLevelCount = tasks.filter(t => t.evaluator_position_level >= 12).length
    const managerCount = tasks.filter(t => t.evaluator_position_level === 9).length
    
    // 按层级分析关系
    const levelRelations = {}
    
    // 分析各层级的考核关系
    tasks.forEach(task => {
      const level = task.evaluator_position_level >= 12 ? '公司领导' : 
                   task.evaluator_position_level === 9 ? '部门经理' : '其他'
      
      if (!levelRelations[level]) {
        levelRelations[level] = {
          evaluatorCount: 0,
          evaluateeCount: 0,
          relationCount: 0
        }
      }
      
      levelRelations[level].relationCount++
    })
    
    // 计算各层级的考核人和被考核人数量
    Object.keys(levelRelations).forEach(level => {
      const levelTasks = tasks.filter(t => 
        (level === '公司领导' && t.evaluator_position_level >= 12) ||
        (level === '部门经理' && t.evaluator_position_level === 9)
      )
      
      const evaluators = new Set(levelTasks.map(t => t.evaluator))
      const evaluatees = new Set(levelTasks.map(t => t.evaluatee))
      
      levelRelations[level].evaluatorCount = evaluators.size
      levelRelations[level].evaluateeCount = evaluatees.size
    })
    
    relationAnalysis.value = {
      totalRelations: tasks.length,
      theoreticalRelations: highLevelCount * managerCount, // 理论上的关系数
      actualRelations: tasks.length,
      levelRelations: levelRelations
    }
    
    console.log('考核关系分析结果:', relationAnalysis.value)
    ElMessage.success('考核关系分析完成')
  } catch (error) {
    console.error('考核关系分析失败:', error)
    ElMessage.error('考核关系分析失败')
  } finally {
    analyzing.value = false
  }
}

// 分析诸葛亮考核关系
const analyzeZhugeLiangRelations = async () => {
  analyzing.value = true
  
  try {
    await evaluationStore.fetchEmployees()
    await evaluationStore.fetchTasks()
    
    let employees = evaluationStore.employees
    let tasks = evaluationStore.tasks
    
    // 强制过滤掉关羽和陈宫
    employees = employees.filter(emp => 
      !emp.name?.includes('关羽') && !emp.name?.includes('陈宫')
    )
    
    tasks = tasks.filter(t => 
      !t.evaluator_name?.includes('关羽') && 
      !t.evaluator_name?.includes('陈宫') &&
      !t.evaluatee_name?.includes('关羽') && 
      !t.evaluatee_name?.includes('陈宫')
    )
    
    console.log('过滤后员工数量:', employees.length)
    console.log('过滤后任务数量:', tasks.length)
    
    // 找到诸葛亮
    const zhugeLiang = employees.find(emp => emp.name?.includes('诸葛亮'))
    
    if (!zhugeLiang) {
      ElMessage.warning('未找到诸葛亮')
      return
    }
    
    console.log('诸葛亮信息:', zhugeLiang)
    
    // 诸葛亮作为考核人的任务
    const asEvaluatorTasks = tasks.filter(t => t.evaluator === zhugeLiang.id)
    console.log('诸葛亮作为考核人的任务:', asEvaluatorTasks)
    
    // 诸葛亮作为被考核人的任务
    const asEvaluateeTasks = tasks.filter(t => t.evaluatee === zhugeLiang.id)
    console.log('诸葛亮作为被考核人的任务:', asEvaluateeTasks)
    
    // 检查诸葛亮考核马超的关系
    const zhugeToMaChao = tasks.filter(t => 
      t.evaluator === zhugeLiang.id && t.evaluatee_name?.includes('马超')
    )
    console.log('诸葛亮考核马超的关系:', zhugeToMaChao)
    
    zhugeLiangAnalysis.value = {
      employee: zhugeLiang,
      asEvaluatorCount: asEvaluatorTasks.length,
      asEvaluatorTasks: asEvaluatorTasks,
      asEvaluateeCount: asEvaluateeTasks.length,
      asEvaluateeTasks: asEvaluateeTasks
    }
    
    console.log('诸葛亮考核关系分析结果:', zhugeLiangAnalysis.value)
    ElMessage.success('诸葛亮考核关系分析完成')
  } catch (error) {
    console.error('诸葛亮考核关系分析失败:', error)
    ElMessage.error('诸葛亮考核关系分析失败')
  } finally {
    analyzing.value = false
  }
}

// 分析其他公司领导
const analyzeOtherLeaders = async () => {
  analyzing.value = true
  
  try {
    await evaluationStore.fetchEmployees()
    await evaluationStore.fetchTasks()
    
    let employees = evaluationStore.employees
    let tasks = evaluationStore.tasks
    
    // 强制过滤掉关羽和陈宫
    employees = employees.filter(emp => 
      !emp.name?.includes('关羽') && !emp.name?.includes('陈宫')
    )
    
    tasks = tasks.filter(t => 
      !t.evaluator_name?.includes('关羽') && 
      !t.evaluator_name?.includes('陈宫') &&
      !t.evaluatee_name?.includes('关羽') && 
      !t.evaluatee_name?.includes('陈宫')
    )
    
    console.log('过滤后员工数量:', employees.length)
    console.log('过滤后任务数量:', tasks.length)
    
    // 找到所有公司领导（除了诸葛亮）
    const highLevelEmployees = employees.filter(emp => 
      emp.position_level >= 12 && !emp.name?.includes('诸葛亮')
    )
    
    const leadersAnalysis = highLevelEmployees.map(leader => {
      const asEvaluatorTasks = tasks.filter(t => t.evaluator === leader.id)
      const asEvaluateeTasks = tasks.filter(t => t.evaluatee === leader.id)
      
      return {
        id: leader.id,
        name: leader.name,
        position_name: leader.position_name,
        position_level: leader.position_level,
        asEvaluatorCount: asEvaluatorTasks.length,
        asEvaluatorTasks: asEvaluatorTasks,
        asEvaluateeCount: asEvaluateeTasks.length,
        asEvaluateeTasks: asEvaluateeTasks,
        totalRelations: asEvaluatorTasks.length + asEvaluateeTasks.length
      }
    })
    
    otherLeadersAnalysis.value = leadersAnalysis
    
    console.log('其他公司领导分析结果:', otherLeadersAnalysis.value)
    ElMessage.success('其他公司领导分析完成')
  } catch (error) {
    console.error('其他公司领导分析失败:', error)
    ElMessage.error('其他公司领导分析失败')
  } finally {
    analyzing.value = false
  }
}

// 分析不平衡原因
const analyzeImbalance = async () => {
  analyzing.value = true
  
  try {
    const reasons = []
    
    // 分析可能的不平衡原因
    if (zhugeLiangAnalysis.value && otherLeadersAnalysis.value) {
      const zhugeCount = zhugeLiangAnalysis.value.asEvaluatorCount
      const otherLeadersCounts = otherLeadersAnalysis.value.map(l => l.asEvaluatorCount)
      const avgOtherLeaders = otherLeadersCounts.reduce((a, b) => a + b, 0) / otherLeadersCounts.length
      
      if (zhugeCount < avgOtherLeaders) {
        reasons.push({
          type: 'position_level',
          title: '职位级别差异',
          description: '诸葛亮的职位级别可能与其他公司领导不同，导致考核关系数量不同',
          examples: [`诸葛亮考核 ${zhugeCount} 人，其他领导平均考核 ${avgOtherLeaders.toFixed(1)} 人`]
        })
      }
      
      reasons.push({
        type: 'department_structure',
        title: '部门结构差异',
        description: '不同公司领导可能负责不同的部门，导致考核关系数量不同',
        examples: ['某些领导可能负责更多部门', '某些领导可能负责特殊部门']
      })
      
      reasons.push({
        type: 'evaluation_rules',
        title: '考核规则差异',
        description: '考核规则可能对不同层级的领导有不同的考核关系配置',
        examples: ['高层领导可能有不同的考核范围', '某些领导可能有特殊的考核权限']
      })
    }
    
    imbalanceAnalysis.value = {
      reasons: reasons
    }
    
    console.log('不平衡原因分析结果:', imbalanceAnalysis.value)
    ElMessage.success('不平衡原因分析完成')
  } catch (error) {
    console.error('不平衡原因分析失败:', error)
    ElMessage.error('不平衡原因分析失败')
  } finally {
    analyzing.value = false
  }
}
</script>

<style scoped>
.evaluation-analysis {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.analysis-section {
  margin: 30px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.level-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.level-item {
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.employee-item {
  margin: 10px 0;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #007bff;
}

.relation-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.relation-item {
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.level-relations {
  margin: 15px 0;
  padding: 10px;
  background: #e9ecef;
  border-radius: 4px;
}

.zhuge-analysis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.zhuge-info, .zhuge-relations {
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.task-item {
  margin: 10px 0;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #28a745;
}

.leader-analysis {
  margin: 20px 0;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.imbalance-reasons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.reason-item {
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.reason-item h4 {
  color: #dc3545;
  margin-bottom: 10px;
}

.reason-item h5 {
  color: #6c757d;
  margin: 10px 0 5px 0;
}

.reason-item ul {
  margin: 10px 0;
  padding-left: 20px;
}

.reason-item li {
  margin: 5px 0;
  color: #495057;
}
</style>
