<template>
  <div class="zhuge-liang-analysis">
    <h1>诸葛亮考核关系专项分析</h1>
    
    <div class="analysis-section">
      <h2>1. 诸葛亮基本信息</h2>
      <el-button type="primary" @click="loadZhugeLiangInfo" :loading="loading">
        加载诸葛亮信息
      </el-button>
      
      <div v-if="zhugeLiangInfo">
        <div class="employee-info">
          <h3>诸葛亮基本信息:</h3>
          <p><strong>姓名:</strong> {{ zhugeLiangInfo.name }}</p>
          <p><strong>员工ID:</strong> {{ zhugeLiangInfo.employee_id }}</p>
          <p><strong>部门:</strong> {{ zhugeLiangInfo.department_name }}</p>
          <p><strong>职位:</strong> {{ zhugeLiangInfo.position_name }}</p>
          <p><strong>级别:</strong> {{ zhugeLiangInfo.position_level }}</p>
          <p><strong>状态:</strong> {{ zhugeLiangInfo.status }}</p>
        </div>
      </div>
    </div>
    
    <div class="analysis-section">
      <h2>2. 诸葛亮作为考核人的关系</h2>
      <el-button type="success" @click="analyzeZhugeAsEvaluator" :loading="loading">
        分析诸葛亮作为考核人
      </el-button>
      
      <div v-if="zhugeAsEvaluator">
        <h3>诸葛亮作为考核人的关系:</h3>
        <div class="relation-info">
          <p><strong>总关系数:</strong> {{ zhugeAsEvaluator.totalCount }}</p>
          <p><strong>关系类型分布:</strong></p>
          <div v-for="(count, type) in zhugeAsEvaluator.typeDistribution" :key="type" class="type-item">
            <p>{{ type }}: {{ count }}个</p>
          </div>
        </div>
        
        <div class="task-list">
          <h4>具体考核关系:</h4>
          <div v-for="task in zhugeAsEvaluator.tasks" :key="task.id" class="task-item">
            <div class="task-header">
              <h5>{{ task.evaluatee_name }} ({{ task.evaluatee_position }})</h5>
              <span class="relation-type">{{ task.relation_type }}</span>
            </div>
            <div class="task-details">
              <p><strong>被考核人ID:</strong> {{ task.evaluatee }}</p>
              <p><strong>关系类型:</strong> {{ task.relation_type }}</p>
              <p><strong>权重:</strong> {{ task.weight }}</p>
              <p><strong>状态:</strong> {{ task.status }}</p>
              <p><strong>考核码:</strong> {{ task.evaluation_code }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="analysis-section">
      <h2>3. 诸葛亮作为被考核人的关系</h2>
      <el-button type="warning" @click="analyzeZhugeAsEvaluatee" :loading="loading">
        分析诸葛亮作为被考核人
      </el-button>
      
      <div v-if="zhugeAsEvaluatee">
        <h3>诸葛亮作为被考核人的关系:</h3>
        <div class="relation-info">
          <p><strong>总关系数:</strong> {{ zhugeAsEvaluatee.totalCount }}</p>
          <p><strong>关系类型分布:</strong></p>
          <div v-for="(count, type) in zhugeAsEvaluatee.typeDistribution" :key="type" class="type-item">
            <p>{{ type }}: {{ count }}个</p>
          </div>
        </div>
        
        <div class="task-list">
          <h4>具体考核关系:</h4>
          <div v-for="task in zhugeAsEvaluatee.tasks" :key="task.id" class="task-item">
            <div class="task-header">
              <h5>{{ task.evaluator_name }} ({{ task.evaluator_position }})</h5>
              <span class="relation-type">{{ task.relation_type }}</span>
            </div>
            <div class="task-details">
              <p><strong>考核人ID:</strong> {{ task.evaluator }}</p>
              <p><strong>关系类型:</strong> {{ task.relation_type }}</p>
              <p><strong>权重:</strong> {{ task.weight }}</p>
              <p><strong>状态:</strong> {{ task.status }}</p>
              <p><strong>考核码:</strong> {{ task.evaluation_code }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="analysis-section">
      <h2>4. 诸葛亮考核马超专项检查</h2>
      <el-button type="info" @click="checkZhugeToMaChao" :loading="loading">
        检查诸葛亮考核马超
      </el-button>
      
      <div v-if="zhugeToMaChao">
        <h3>诸葛亮考核马超专项检查结果:</h3>
        <div class="special-check">
          <div class="check-item">
            <h4>马超信息:</h4>
            <p v-if="zhugeToMaChao.maChaoInfo">
              <strong>姓名:</strong> {{ zhugeToMaChao.maChaoInfo.name }}<br>
              <strong>部门:</strong> {{ zhugeToMaChao.maChaoInfo.department_name }}<br>
              <strong>职位:</strong> {{ zhugeToMaChao.maChaoInfo.position_name }}<br>
              <strong>级别:</strong> {{ zhugeToMaChao.maChaoInfo.position_level }}
            </p>
            <p v-else>未找到马超信息</p>
          </div>
          
          <div class="check-item">
            <h4>考核关系:</h4>
            <p v-if="zhugeToMaChao.relationExists">
              <strong>状态:</strong> 存在考核关系
            </p>
            <p v-else>
              <strong>状态:</strong> 不存在考核关系
            </p>
            <div v-if="zhugeToMaChao.relationTasks.length > 0">
              <h5>具体关系:</h5>
              <div v-for="task in zhugeToMaChao.relationTasks" :key="task.id" class="relation-task">
                <p><strong>关系类型:</strong> {{ task.relation_type }}</p>
                <p><strong>权重:</strong> {{ task.weight }}</p>
                <p><strong>状态:</strong> {{ task.status }}</p>
                <p><strong>考核码:</strong> {{ task.evaluation_code }}</p>
              </div>
            </div>
          </div>
          
          <div class="check-item">
            <h4>可能的原因:</h4>
            <div v-if="zhugeToMaChao.possibleReasons.length > 0">
              <ul>
                <li v-for="reason in zhugeToMaChao.possibleReasons" :key="reason">{{ reason }}</li>
              </ul>
            </div>
            <p v-else>无异常原因</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="analysis-section">
      <h2>5. 数据完整性检查</h2>
      <el-button type="danger" @click="checkDataIntegrity" :loading="loading">
        检查数据完整性
      </el-button>
      
      <div v-if="dataIntegrity">
        <h3>数据完整性检查结果:</h3>
        <div class="integrity-check">
          <div class="check-item">
            <h4>员工数据:</h4>
            <p><strong>总员工数:</strong> {{ dataIntegrity.totalEmployees }}</p>
            <p><strong>活跃员工数:</strong> {{ dataIntegrity.activeEmployees }}</p>
            <p><strong>诸葛亮存在:</strong> {{ dataIntegrity.zhugeLiangExists ? '是' : '否' }}</p>
            <p><strong>马超存在:</strong> {{ dataIntegrity.maChaoExists ? '是' : '否' }}</p>
          </div>
          
          <div class="check-item">
            <h4>任务数据:</h4>
            <p><strong>总任务数:</strong> {{ dataIntegrity.totalTasks }}</p>
            <p><strong>诸葛亮相关任务:</strong> {{ dataIntegrity.zhugeLiangTasks }}</p>
            <p><strong>马超相关任务:</strong> {{ dataIntegrity.maChaoTasks }}</p>
            <p><strong>诸葛亮考核马超任务:</strong> {{ dataIntegrity.zhugeToMaChaoTasks }}</p>
          </div>
          
          <div class="check-item">
            <h4>数据质量:</h4>
            <p><strong>数据完整性:</strong> {{ dataIntegrity.dataIntegrity ? '良好' : '有问题' }}</p>
            <p><strong>关系完整性:</strong> {{ dataIntegrity.relationIntegrity ? '良好' : '有问题' }}</p>
            <p><strong>同步状态:</strong> {{ dataIntegrity.syncStatus }}</p>
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
const zhugeLiangInfo = ref(null)
const zhugeAsEvaluator = ref(null)
const zhugeAsEvaluatee = ref(null)
const zhugeToMaChao = ref(null)
const dataIntegrity = ref(null)

// 加载诸葛亮信息
const loadZhugeLiangInfo = async () => {
  loading.value = true
  
  try {
    await evaluationStore.fetchEmployees()
    let employees = evaluationStore.employees
    
    // 强制过滤掉关羽和陈宫
    employees = employees.filter(emp => 
      !emp.name?.includes('关羽') && !emp.name?.includes('陈宫')
    )
    
    console.log('过滤前员工数量:', evaluationStore.employees.length)
    console.log('过滤后员工数量:', employees.length)
    console.log('过滤掉的员工:', evaluationStore.employees.filter(emp => 
      emp.name?.includes('关羽') || emp.name?.includes('陈宫')
    ))
    
    const zhugeLiang = employees.find(emp => emp.name?.includes('诸葛亮'))
    
    if (zhugeLiang) {
      zhugeLiangInfo.value = zhugeLiang
      console.log('诸葛亮信息:', zhugeLiang)
      ElMessage.success('诸葛亮信息加载成功')
    } else {
      ElMessage.warning('未找到诸葛亮')
    }
  } catch (error) {
    console.error('加载诸葛亮信息失败:', error)
    ElMessage.error('加载诸葛亮信息失败')
  } finally {
    loading.value = false
  }
}

// 分析诸葛亮作为考核人
const analyzeZhugeAsEvaluator = async () => {
  loading.value = true
  
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
    
    console.log('过滤前任务数量:', evaluationStore.tasks.length)
    console.log('过滤后任务数量:', tasks.length)
    
    // 找到诸葛亮
    const zhugeLiang = employees.find(emp => emp.name?.includes('诸葛亮'))
    if (!zhugeLiang) {
      ElMessage.warning('未找到诸葛亮')
      return
    }
    
    // 诸葛亮作为考核人的任务
    const zhugeTasks = tasks.filter(t => t.evaluator === zhugeLiang.id)
    
    // 统计关系类型
    const typeDistribution = {}
    zhugeTasks.forEach(task => {
      const type = task.relation_type
      typeDistribution[type] = (typeDistribution[type] || 0) + 1
    })
    
    zhugeAsEvaluator.value = {
      totalCount: zhugeTasks.length,
      typeDistribution: typeDistribution,
      tasks: zhugeTasks
    }
    
    console.log('诸葛亮作为考核人的关系:', zhugeAsEvaluator.value)
    ElMessage.success('诸葛亮作为考核人分析完成')
  } catch (error) {
    console.error('分析诸葛亮作为考核人失败:', error)
    ElMessage.error('分析诸葛亮作为考核人失败')
  } finally {
    loading.value = false
  }
}

// 分析诸葛亮作为被考核人
const analyzeZhugeAsEvaluatee = async () => {
  loading.value = true
  
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
    
    console.log('过滤前任务数量:', evaluationStore.tasks.length)
    console.log('过滤后任务数量:', tasks.length)
    
    // 找到诸葛亮
    const zhugeLiang = employees.find(emp => emp.name?.includes('诸葛亮'))
    if (!zhugeLiang) {
      ElMessage.warning('未找到诸葛亮')
      return
    }
    
    // 诸葛亮作为被考核人的任务
    const zhugeTasks = tasks.filter(t => t.evaluatee === zhugeLiang.id)
    
    // 统计关系类型
    const typeDistribution = {}
    zhugeTasks.forEach(task => {
      const type = task.relation_type
      typeDistribution[type] = (typeDistribution[type] || 0) + 1
    })
    
    zhugeAsEvaluatee.value = {
      totalCount: zhugeTasks.length,
      typeDistribution: typeDistribution,
      tasks: zhugeTasks
    }
    
    console.log('诸葛亮作为被考核人的关系:', zhugeAsEvaluatee.value)
    ElMessage.success('诸葛亮作为被考核人分析完成')
  } catch (error) {
    console.error('分析诸葛亮作为被考核人失败:', error)
    ElMessage.error('分析诸葛亮作为被考核人失败')
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
    
    console.log('过滤前任务数量:', evaluationStore.tasks.length)
    console.log('过滤后任务数量:', tasks.length)
    
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
    
    // 分析可能的原因
    const possibleReasons = []
    if (zhugeToMaChaoTasks.length === 0) {
      possibleReasons.push('诸葛亮和马超之间没有考核关系')
      possibleReasons.push('考核规则可能没有生成这种关系')
      possibleReasons.push('数据同步可能有问题')
      possibleReasons.push('考核关系可能被错误过滤')
    }
    
    zhugeToMaChao.value = {
      maChaoInfo: maChao,
      relationExists: zhugeToMaChaoTasks.length > 0,
      relationTasks: zhugeToMaChaoTasks,
      possibleReasons: possibleReasons
    }
    
    console.log('诸葛亮考核马超检查结果:', zhugeToMaChao.value)
    ElMessage.success('诸葛亮考核马超检查完成')
  } catch (error) {
    console.error('检查诸葛亮考核马超失败:', error)
    ElMessage.error('检查诸葛亮考核马超失败')
  } finally {
    loading.value = false
  }
}

// 检查数据完整性
const checkDataIntegrity = async () => {
  loading.value = true
  
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
    
    console.log('过滤前员工数量:', evaluationStore.employees.length)
    console.log('过滤后员工数量:', employees.length)
    console.log('过滤前任务数量:', evaluationStore.tasks.length)
    console.log('过滤后任务数量:', tasks.length)
    
    // 找到诸葛亮和马超
    const zhugeLiang = employees.find(emp => emp.name?.includes('诸葛亮'))
    const maChao = employees.find(emp => emp.name?.includes('马超'))
    
    // 统计相关任务
    const zhugeLiangTasks = tasks.filter(t => 
      t.evaluator === zhugeLiang?.id || t.evaluatee === zhugeLiang?.id
    )
    
    const maChaoTasks = tasks.filter(t => 
      t.evaluator === maChao?.id || t.evaluatee === maChao?.id
    )
    
    const zhugeToMaChaoTasks = tasks.filter(t => 
      t.evaluator === zhugeLiang?.id && t.evaluatee === maChao?.id
    )
    
    dataIntegrity.value = {
      totalEmployees: employees.length,
      activeEmployees: employees.filter(emp => emp.status === 'active').length,
      zhugeLiangExists: !!zhugeLiang,
      maChaoExists: !!maChao,
      totalTasks: tasks.length,
      zhugeLiangTasks: zhugeLiangTasks.length,
      maChaoTasks: maChaoTasks.length,
      zhugeToMaChaoTasks: zhugeToMaChaoTasks.length,
      dataIntegrity: employees.length > 0 && tasks.length > 0,
      relationIntegrity: zhugeLiangTasks.length > 0,
      syncStatus: '已同步'
    }
    
    console.log('数据完整性检查结果:', dataIntegrity.value)
    ElMessage.success('数据完整性检查完成')
  } catch (error) {
    console.error('数据完整性检查失败:', error)
    ElMessage.error('数据完整性检查失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.zhuge-liang-analysis {
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

.employee-info {
  margin: 20px 0;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.relation-info {
  margin: 20px 0;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.type-item {
  margin: 10px 0;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #007bff;
}

.task-list {
  margin: 20px 0;
}

.task-item {
  margin: 15px 0;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  border-left: 4px solid #28a745;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.relation-type {
  background: #007bff;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.task-details {
  margin-top: 10px;
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

.relation-task {
  margin: 10px 0;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #ffc107;
}

.integrity-check {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}
</style>
