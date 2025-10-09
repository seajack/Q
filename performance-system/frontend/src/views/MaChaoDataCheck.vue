<template>
  <div class="machao-data-check">
    <h1>马超数据专项检查工具</h1>
    
    <div class="check-section">
      <h2>1. 马超基本信息检查</h2>
      <el-button type="primary" @click="checkMaChaoBasicInfo" :loading="loading">
        检查马超基本信息
      </el-button>
      
      <div v-if="maChaoBasicInfo">
        <h3>马超基本信息:</h3>
        <div class="info-box">
          <div class="info-item">
            <h4>组织架构中台:</h4>
            <p v-if="maChaoBasicInfo.orgPlatformFound">
              <strong>状态:</strong> 已找到
            </p>
            <p v-else>
              <strong>状态:</strong> 未找到
            </p>
            <div v-if="maChaoBasicInfo.orgPlatformEmployee">
              <p><strong>姓名:</strong> {{ maChaoBasicInfo.orgPlatformEmployee.name }}</p>
              <p><strong>员工ID:</strong> {{ maChaoBasicInfo.orgPlatformEmployee.employee_id }}</p>
              <p><strong>部门:</strong> {{ maChaoBasicInfo.orgPlatformEmployee.department_name }}</p>
              <p><strong>职位:</strong> {{ maChaoBasicInfo.orgPlatformEmployee.position_name }}</p>
              <p><strong>级别:</strong> {{ maChaoBasicInfo.orgPlatformEmployee.position_level }}</p>
              <p><strong>上级:</strong> {{ maChaoBasicInfo.orgPlatformEmployee.supervisor_id }}</p>
            </div>
          </div>
          
          <div class="info-item">
            <h4>绩效考核系统:</h4>
            <p v-if="maChaoBasicInfo.performanceSystemFound">
              <strong>状态:</strong> 已找到
            </p>
            <p v-else>
              <strong>状态:</strong> 未找到
            </p>
            <div v-if="maChaoBasicInfo.performanceSystemEmployee">
              <p><strong>姓名:</strong> {{ maChaoBasicInfo.performanceSystemEmployee.name }}</p>
              <p><strong>员工ID:</strong> {{ maChaoBasicInfo.performanceSystemEmployee.employee_id }}</p>
              <p><strong>部门:</strong> {{ maChaoBasicInfo.performanceSystemEmployee.department_name }}</p>
              <p><strong>职位:</strong> {{ maChaoBasicInfo.performanceSystemEmployee.position_name }}</p>
              <p><strong>级别:</strong> {{ maChaoBasicInfo.performanceSystemEmployee.position_level }}</p>
              <p><strong>上级:</strong> {{ maChaoBasicInfo.performanceSystemEmployee.supervisor_id }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="check-section">
      <h2>2. 马超考核关系检查</h2>
      <el-button type="success" @click="checkMaChaoRelations" :loading="loading">
        检查马超考核关系
      </el-button>
      
      <div v-if="maChaoRelations">
        <h3>马超考核关系:</h3>
        <div class="relation-info">
          <div class="relation-item">
            <h4>作为考核人:</h4>
            <p><strong>关系数量:</strong> {{ maChaoRelations.asEvaluatorCount }}</p>
            <div v-for="task in maChaoRelations.asEvaluatorTasks" :key="task.id" class="task-item">
              <p><strong>被考核人:</strong> {{ task.evaluatee_name }} ({{ task.evaluatee_position }})</p>
              <p><strong>关系类型:</strong> {{ task.relation_type }}</p>
              <p><strong>权重:</strong> {{ task.weight }}</p>
            </div>
          </div>
          
          <div class="relation-item">
            <h4>作为被考核人:</h4>
            <p><strong>关系数量:</strong> {{ maChaoRelations.asEvaluateeCount }}</p>
            <div v-for="task in maChaoRelations.asEvaluateeTasks" :key="task.id" class="task-item">
              <p><strong>考核人:</strong> {{ task.evaluator_name }} ({{ task.evaluator_position }})</p>
              <p><strong>关系类型:</strong> {{ task.relation_type }}</p>
              <p><strong>权重:</strong> {{ task.weight }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="check-section">
      <h2>3. 诸葛亮考核马超专项检查</h2>
      <el-button type="warning" @click="checkZhugeToMaChao" :loading="loading">
        检查诸葛亮考核马超
      </el-button>
      
      <div v-if="zhugeToMaChaoCheck">
        <h3>诸葛亮考核马超专项检查结果:</h3>
        <div class="special-check">
          <div class="check-item">
            <h4>关系存在性:</h4>
            <p :class="zhugeToMaChaoCheck.relationExists ? 'success' : 'error'">
              {{ zhugeToMaChaoCheck.relationExists ? '存在' : '不存在' }}
            </p>
          </div>
          
          <div class="check-item">
            <h4>关系详情:</h4>
            <div v-if="zhugeToMaChaoCheck.relationTasks.length > 0">
              <div v-for="task in zhugeToMaChaoCheck.relationTasks" :key="task.id" class="task-detail">
                <p><strong>任务ID:</strong> {{ task.id }}</p>
                <p><strong>关系类型:</strong> {{ task.relation_type }}</p>
                <p><strong>权重:</strong> {{ task.weight }}</p>
                <p><strong>状态:</strong> {{ task.status }}</p>
                <p><strong>考核码:</strong> {{ task.evaluation_code }}</p>
              </div>
            </div>
            <p v-else>无关系任务</p>
          </div>
          
          <div class="check-item">
            <h4>问题分析:</h4>
            <div v-if="zhugeToMaChaoCheck.issues.length > 0">
              <ul>
                <li v-for="issue in zhugeToMaChaoCheck.issues" :key="issue">{{ issue }}</li>
              </ul>
            </div>
            <p v-else>无问题</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="check-section">
      <h2>4. 考核规则检查</h2>
      <el-button type="info" @click="checkEvaluationRules" :loading="loading">
        检查考核规则
      </el-button>
      
      <div v-if="evaluationRules">
        <h3>考核规则检查结果:</h3>
        <div class="rules-info">
          <div class="rule-item">
            <h4>规则配置:</h4>
            <p><strong>规则名称:</strong> {{ evaluationRules.ruleName }}</p>
            <p><strong>关系类型:</strong> {{ evaluationRules.relationTypes.join(', ') }}</p>
            <p><strong>评价范围:</strong> {{ evaluationRules.evaluationScope }}</p>
            <p><strong>允许跨部门:</strong> {{ evaluationRules.allowCrossDepartment ? '是' : '否' }}</p>
          </div>
          
          <div class="rule-item">
            <h4>级别配置:</h4>
            <p><strong>诸葛亮级别:</strong> {{ evaluationRules.zhugeLiangLevel }}</p>
            <p><strong>马超级别:</strong> {{ evaluationRules.maChaoLevel }}</p>
            <p><strong>级别差异:</strong> {{ evaluationRules.levelDifference }}</p>
            <p><strong>是否允许考核:</strong> {{ evaluationRules.canEvaluate ? '是' : '否' }}</p>
          </div>
          
          <div class="rule-item">
            <h4>部门配置:</h4>
            <p><strong>诸葛亮部门:</strong> {{ evaluationRules.zhugeLiangDepartment }}</p>
            <p><strong>马超部门:</strong> {{ evaluationRules.maChaoDepartment }}</p>
            <p><strong>是否同部门:</strong> {{ evaluationRules.sameDepartment ? '是' : '否' }}</p>
            <p><strong>跨部门考核:</strong> {{ evaluationRules.crossDepartmentAllowed ? '允许' : '不允许' }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="check-section">
      <h2>5. 数据同步检查</h2>
      <el-button type="danger" @click="checkDataSync" :loading="loading">
        检查数据同步
      </el-button>
      
      <div v-if="dataSyncCheck">
        <h3>数据同步检查结果:</h3>
        <div class="sync-info">
          <div class="sync-item">
            <h4>同步状态:</h4>
            <p><strong>组织架构中台员工数:</strong> {{ dataSyncCheck.orgPlatformCount }}</p>
            <p><strong>绩效考核系统员工数:</strong> {{ dataSyncCheck.performanceSystemCount }}</p>
            <p><strong>同步状态:</strong> {{ dataSyncCheck.syncStatus }}</p>
          </div>
          
          <div class="sync-item">
            <h4>马超同步:</h4>
            <p><strong>组织架构中台:</strong> {{ dataSyncCheck.maChaoInOrgPlatform ? '存在' : '不存在' }}</p>
            <p><strong>绩效考核系统:</strong> {{ dataSyncCheck.maChaoInPerformanceSystem ? '存在' : '不存在' }}</p>
            <p><strong>同步状态:</strong> {{ dataSyncCheck.maChaoSyncStatus }}</p>
          </div>
          
          <div class="sync-item">
            <h4>建议操作:</h4>
            <div v-if="dataSyncCheck.suggestions.length > 0">
              <ul>
                <li v-for="suggestion in dataSyncCheck.suggestions" :key="suggestion">{{ suggestion }}</li>
              </ul>
            </div>
            <p v-else>无需操作</p>
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

const loading = ref(false)
const maChaoBasicInfo = ref(null)
const maChaoRelations = ref(null)
const zhugeToMaChaoCheck = ref(null)
const evaluationRules = ref(null)
const dataSyncCheck = ref(null)

// 检查马超基本信息
const checkMaChaoBasicInfo = async () => {
  loading.value = true
  
  try {
    // 检查组织架构中台
    const orgResponse = await fetch('http://127.0.0.1:8000/api/employees/')
    const orgData = await orgResponse.json()
    const orgEmployees = orgData.results || []
    const orgMaChao = orgEmployees.find(emp => emp.name?.includes('马超'))
    
    // 检查绩效考核系统
    await evaluationStore.fetchEmployees()
    const perfEmployees = evaluationStore.employees
    const perfMaChao = perfEmployees.find(emp => emp.name?.includes('马超'))
    
    maChaoBasicInfo.value = {
      orgPlatformFound: !!orgMaChao,
      orgPlatformEmployee: orgMaChao,
      performanceSystemFound: !!perfMaChao,
      performanceSystemEmployee: perfMaChao
    }
    
    console.log('马超基本信息检查结果:', maChaoBasicInfo.value)
    ElMessage.success('马超基本信息检查完成')
  } catch (error) {
    console.error('马超基本信息检查失败:', error)
    ElMessage.error('马超基本信息检查失败')
  } finally {
    loading.value = false
  }
}

// 检查马超考核关系
const checkMaChaoRelations = async () => {
  loading.value = true
  
  try {
    await evaluationStore.fetchEmployees()
    await evaluationStore.fetchTasks()
    
    const employees = evaluationStore.employees
    const tasks = evaluationStore.tasks
    
    // 找到马超
    const maChao = employees.find(emp => emp.name?.includes('马超'))
    if (!maChao) {
      ElMessage.warning('未找到马超')
      return
    }
    
    // 马超作为考核人的任务
    const asEvaluatorTasks = tasks.filter(t => t.evaluator === maChao.id)
    
    // 马超作为被考核人的任务
    const asEvaluateeTasks = tasks.filter(t => t.evaluatee === maChao.id)
    
    maChaoRelations.value = {
      asEvaluatorCount: asEvaluatorTasks.length,
      asEvaluatorTasks: asEvaluatorTasks,
      asEvaluateeCount: asEvaluateeTasks.length,
      asEvaluateeTasks: asEvaluateeTasks
    }
    
    console.log('马超考核关系检查结果:', maChaoRelations.value)
    ElMessage.success('马超考核关系检查完成')
  } catch (error) {
    console.error('马超考核关系检查失败:', error)
    ElMessage.error('马超考核关系检查失败')
  } finally {
    loading.value = false
  }
}

// 检查诸葛亮考核马超
const checkZhugeToMaChao = async () => {
  loading.value = true
  
  try {
    await evaluationStore.fetchEmployees()
    await evaluationStore.fetchTasks()
    
    const employees = evaluationStore.employees
    const tasks = evaluationStore.tasks
    
    // 找到诸葛亮和马超
    const zhugeLiang = employees.find(emp => emp.name?.includes('诸葛亮'))
    const maChao = employees.find(emp => emp.name?.includes('马超'))
    
    if (!zhugeLiang) {
      ElMessage.warning('未找到诸葛亮')
      return
    }
    
    if (!maChao) {
      ElMessage.warning('未找到马超')
      return
    }
    
    // 查找诸葛亮考核马超的任务
    const zhugeToMaChaoTasks = tasks.filter(t => 
      t.evaluator === zhugeLiang.id && t.evaluatee === maChao.id
    )
    
    // 分析问题
    const issues = []
    if (zhugeToMaChaoTasks.length === 0) {
      issues.push('诸葛亮和马超之间没有考核关系')
      
      // 检查级别差异
      const levelDiff = Math.abs(zhugeLiang.position_level - maChao.position_level)
      if (levelDiff > 3) {
        issues.push(`级别差异过大: 诸葛亮(${zhugeLiang.position_level}) vs 马超(${maChao.position_level})`)
      }
      
      // 检查部门差异
      if (zhugeLiang.department_name !== maChao.department_name) {
        issues.push(`部门不同: 诸葛亮(${zhugeLiang.department_name}) vs 马超(${maChao.department_name})`)
      }
      
      // 检查上级关系
      if (maChao.supervisor_id !== zhugeLiang.id) {
        issues.push(`马超的上级不是诸葛亮: 马超的上级ID是${maChao.supervisor_id}`)
      }
    }
    
    zhugeToMaChaoCheck.value = {
      relationExists: zhugeToMaChaoTasks.length > 0,
      relationTasks: zhugeToMaChaoTasks,
      issues: issues
    }
    
    console.log('诸葛亮考核马超检查结果:', zhugeToMaChaoCheck.value)
    ElMessage.success('诸葛亮考核马超检查完成')
  } catch (error) {
    console.error('诸葛亮考核马超检查失败:', error)
    ElMessage.error('诸葛亮考核马超检查失败')
  } finally {
    loading.value = false
  }
}

// 检查考核规则
const checkEvaluationRules = async () => {
  loading.value = true
  
  try {
    await evaluationStore.fetchEmployees()
    
    const employees = evaluationStore.employees
    
    // 找到诸葛亮和马超
    const zhugeLiang = employees.find(emp => emp.name?.includes('诸葛亮'))
    const maChao = employees.find(emp => emp.name?.includes('马超'))
    
    if (!zhugeLiang || !maChao) {
      ElMessage.warning('未找到诸葛亮或马超')
      return
    }
    
    // 分析级别和部门
    const levelDifference = Math.abs(zhugeLiang.position_level - maChao.position_level)
    const sameDepartment = zhugeLiang.department_name === maChao.department_name
    const canEvaluate = levelDifference <= 3 && (sameDepartment || true) // 假设允许跨部门
    
    evaluationRules.value = {
      ruleName: '上级考核下级规则',
      relationTypes: ['superior', 'peer', 'subordinate'],
      evaluationScope: 'company',
      allowCrossDepartment: true,
      zhugeLiangLevel: zhugeLiang.position_level,
      maChaoLevel: maChao.position_level,
      levelDifference: levelDifference,
      canEvaluate: canEvaluate,
      zhugeLiangDepartment: zhugeLiang.department_name,
      maChaoDepartment: maChao.department_name,
      sameDepartment: sameDepartment,
      crossDepartmentAllowed: true
    }
    
    console.log('考核规则检查结果:', evaluationRules.value)
    ElMessage.success('考核规则检查完成')
  } catch (error) {
    console.error('考核规则检查失败:', error)
    ElMessage.error('考核规则检查失败')
  } finally {
    loading.value = false
  }
}

// 检查数据同步
const checkDataSync = async () => {
  loading.value = true
  
  try {
    // 检查组织架构中台
    const orgResponse = await fetch('http://127.0.0.1:8000/api/employees/')
    const orgData = await orgResponse.json()
    const orgEmployees = orgData.results || []
    const orgMaChao = orgEmployees.find(emp => emp.name?.includes('马超'))
    
    // 检查绩效考核系统
    await evaluationStore.fetchEmployees()
    const perfEmployees = evaluationStore.employees
    const perfMaChao = perfEmployees.find(emp => emp.name?.includes('马超'))
    
    // 分析同步状态
    const suggestions = []
    if (!orgMaChao) {
      suggestions.push('马超在组织架构中台不存在，需要添加马超到组织架构中台')
    }
    if (!perfMaChao) {
      suggestions.push('马超在绩效考核系统不存在，需要同步马超数据')
    }
    if (orgMaChao && !perfMaChao) {
      suggestions.push('需要执行数据同步，将马超从组织架构中台同步到绩效考核系统')
    }
    if (orgMaChao && perfMaChao) {
      suggestions.push('马超数据已同步，需要重新生成考核关系')
    }
    
    dataSyncCheck.value = {
      orgPlatformCount: orgEmployees.length,
      performanceSystemCount: perfEmployees.length,
      syncStatus: orgEmployees.length === perfEmployees.length ? '已同步' : '未同步',
      maChaoInOrgPlatform: !!orgMaChao,
      maChaoInPerformanceSystem: !!perfMaChao,
      maChaoSyncStatus: (!!orgMaChao && !!perfMaChao) ? '已同步' : '未同步',
      suggestions: suggestions
    }
    
    console.log('数据同步检查结果:', dataSyncCheck.value)
    ElMessage.success('数据同步检查完成')
  } catch (error) {
    console.error('数据同步检查失败:', error)
    ElMessage.error('数据同步检查失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.machao-data-check {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.check-section {
  margin: 30px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.info-box {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.info-item {
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.relation-info {
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

.task-item {
  margin: 10px 0;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #007bff;
}

.special-check {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.check-item {
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.task-detail {
  margin: 10px 0;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #28a745;
}

.success {
  color: #28a745;
  font-weight: bold;
}

.error {
  color: #dc3545;
  font-weight: bold;
}

.rules-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.rule-item {
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.sync-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.sync-item {
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}
</style>
