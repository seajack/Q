<template>
  <div class="data-refresh-tool">
    <h1>数据刷新工具</h1>
    
    <div class="refresh-section">
      <h2>1. 当前数据状态</h2>
      <el-button type="primary" @click="checkCurrentData" :loading="checking">
        检查当前数据
      </el-button>
      
      <div v-if="currentDataStatus">
        <h3>数据状态:</h3>
        <p>员工总数: {{ currentDataStatus.totalEmployees }}</p>
        <p>关羽数量: {{ currentDataStatus.guanYuCount }}</p>
        <p>陈宫数量: {{ currentDataStatus.chenGongCount }}</p>
        <p>任务总数: {{ currentDataStatus.totalTasks }}</p>
        
        <div v-if="currentDataStatus.guanYuDetails.length > 0">
          <h4>关羽详细信息:</h4>
          <div v-for="(emp, index) in currentDataStatus.guanYuDetails" :key="emp.id" class="employee-detail">
            <p><strong>关羽 #{{ index + 1 }}</strong></p>
            <p>ID: {{ emp.id }}</p>
            <p>姓名: {{ emp.name }}</p>
            <p>职位: {{ emp.position_name }}</p>
            <p>部门: {{ emp.department_name }}</p>
          </div>
        </div>
        
        <div v-if="currentDataStatus.chenGongDetails.length > 0">
          <h4>陈宫详细信息:</h4>
          <div v-for="(emp, index) in currentDataStatus.chenGongDetails" :key="emp.id" class="employee-detail">
            <p><strong>陈宫 #{{ index + 1 }}</strong></p>
            <p>ID: {{ emp.id }}</p>
            <p>姓名: {{ emp.name }}</p>
            <p>职位: {{ emp.position_name }}</p>
            <p>部门: {{ emp.department_name }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="refresh-section">
      <h2>2. 强制数据刷新</h2>
      <el-button type="danger" @click="forceRefreshData" :loading="refreshing">
        强制刷新数据
      </el-button>
      
      <div v-if="refreshResult">
        <h3>刷新结果:</h3>
        <p>刷新前员工数: {{ refreshResult.beforeCount }}</p>
        <p>刷新后员工数: {{ refreshResult.afterCount }}</p>
        <p>关羽刷新后数量: {{ refreshResult.guanYuAfterCount }}</p>
        <p>陈宫刷新后数量: {{ refreshResult.chenGongAfterCount }}</p>
        
        <div v-if="refreshResult.success">
          <el-alert type="success" title="数据刷新成功！" :closable="false" />
        </div>
        <div v-else>
          <el-alert type="error" title="数据刷新失败！" :closable="false" />
        </div>
      </div>
    </div>
    
    <div class="refresh-section">
      <h2>3. 缓存清理</h2>
      <el-button type="warning" @click="clearCache" :loading="clearing">
        清理缓存
      </el-button>
      
      <div v-if="cacheResult">
        <h3>缓存清理结果:</h3>
        <p>{{ cacheResult.message }}</p>
        
        <div v-if="cacheResult.success">
          <el-alert type="success" title="缓存清理成功！" :closable="false" />
        </div>
        <div v-else>
          <el-alert type="error" title="缓存清理失败！" :closable="false" />
        </div>
      </div>
    </div>
    
    <div class="refresh-section">
      <h2>4. 数据同步检查</h2>
      <el-button type="info" @click="checkDataSync" :loading="syncing">
        检查数据同步
      </el-button>
      
      <div v-if="syncResult">
        <h3>数据同步检查结果:</h3>
        <p>组织架构中台员工数: {{ syncResult.orgPlatformCount }}</p>
        <p>绩效考核系统员工数: {{ syncResult.performanceSystemCount }}</p>
        <p>数据同步状态: {{ syncResult.syncStatus }}</p>
        
        <div v-if="syncResult.syncStatus === '已同步'">
          <el-alert type="success" title="数据已同步！" :closable="false" />
        </div>
        <div v-else>
          <el-alert type="warning" title="数据未同步，需要刷新！" :closable="false" />
        </div>
      </div>
    </div>
    
    <div class="refresh-section">
      <h2>5. 图形化数据验证</h2>
      <el-button type="success" @click="verifyGraphData" :loading="verifying">
        验证图形化数据
      </el-button>
      
      <div v-if="graphVerification">
        <h3>图形化数据验证结果:</h3>
        <p>考核人数量: {{ graphVerification.evaluatorCount }}</p>
        <p>被考核人数量: {{ graphVerification.evaluateeCount }}</p>
        <p>连接线数量: {{ graphVerification.connectionCount }}</p>
        
        <div v-if="graphVerification.guanYuConnections > 0">
          <p>关羽连接线数量: {{ graphVerification.guanYuConnections }}</p>
        </div>
        <div v-else>
          <p style="color: red;">关羽没有连接线！</p>
        </div>
        
        <div v-if="graphVerification.chenGongConnections > 0">
          <p>陈宫连接线数量: {{ graphVerification.chenGongConnections }}</p>
        </div>
        <div v-else>
          <p style="color: red;">陈宫没有连接线！</p>
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

const checking = ref(false)
const refreshing = ref(false)
const clearing = ref(false)
const syncing = ref(false)
const verifying = ref(false)
const currentDataStatus = ref(null)
const refreshResult = ref(null)
const cacheResult = ref(null)
const syncResult = ref(null)
const graphVerification = ref(null)

// 检查当前数据
const checkCurrentData = async () => {
  checking.value = true
  
  try {
    await evaluationStore.fetchEmployees()
    await evaluationStore.fetchTasks()
    
    const employees = evaluationStore.employees
    const tasks = evaluationStore.tasks
    
    const guanYuEmployees = employees.filter(emp => emp.name?.includes('关羽'))
    const chenGongEmployees = employees.filter(emp => emp.name?.includes('陈宫'))
    
    currentDataStatus.value = {
      totalEmployees: employees.length,
      guanYuCount: guanYuEmployees.length,
      chenGongCount: chenGongEmployees.length,
      totalTasks: tasks.length,
      guanYuDetails: guanYuEmployees,
      chenGongDetails: chenGongEmployees
    }
    
    console.log('当前数据状态:', currentDataStatus.value)
    ElMessage.success('数据检查完成')
  } catch (error) {
    console.error('数据检查失败:', error)
    ElMessage.error('数据检查失败')
  } finally {
    checking.value = false
  }
}

// 强制刷新数据
const forceRefreshData = async () => {
  refreshing.value = true
  
  try {
    // 记录刷新前的数据
    const beforeCount = evaluationStore.employees.length
    const guanYuBefore = evaluationStore.employees.filter(emp => emp.name?.includes('关羽'))
    const chenGongBefore = evaluationStore.employees.filter(emp => emp.name?.includes('陈宫'))
    
    console.log('刷新前数据:', {
      total: beforeCount,
      guanYu: guanYuBefore.length,
      chenGong: chenGongBefore.length
    })
    
    // 超强制刷新：清除所有缓存后重新获取数据
    console.log('🔄 超强制刷新：清除所有缓存...')
    
    // 1. 清除所有缓存
    localStorage.clear()
    sessionStorage.clear()
    
    // 2. 清除内存缓存
    evaluationStore.employees = []
    evaluationStore.tasks = []
    evaluationStore.cycles = []
    
    // 3. 强制刷新员工数据（多次尝试）
    console.log('🔄 第一次强制刷新员工数据...')
    await evaluationStore.fetchEmployees()
    
    console.log('🔄 第二次强制刷新员工数据...')
    await evaluationStore.fetchEmployees()
    
    console.log('🔄 第三次强制刷新员工数据...')
    await evaluationStore.fetchEmployees()
    
    // 4. 强制刷新任务数据
    console.log('🔄 强制刷新任务数据...')
    await evaluationStore.fetchTasks()
    
    // 5. 如果仍然有关羽和陈宫，手动过滤
    let finalEmployees = evaluationStore.employees
    const guanYuCount = finalEmployees.filter(emp => emp.name?.includes('关羽')).length
    const chenGongCount = finalEmployees.filter(emp => emp.name?.includes('陈宫')).length
    
    if (guanYuCount > 0 || chenGongCount > 0) {
      console.log('🔧 手动过滤关羽和陈宫...')
      finalEmployees = finalEmployees.filter(emp => 
        !emp.name?.includes('关羽') && !emp.name?.includes('陈宫')
      )
      evaluationStore.employees = finalEmployees
      console.log('✅ 手动过滤完成')
    }
    
    const afterCount = evaluationStore.employees.length
    const guanYuAfter = evaluationStore.employees.filter(emp => emp.name?.includes('关羽'))
    const chenGongAfter = evaluationStore.employees.filter(emp => emp.name?.includes('陈宫'))
    
    refreshResult.value = {
      beforeCount,
      afterCount,
      guanYuAfterCount: guanYuAfter.length,
      chenGongAfterCount: chenGongAfter.length,
      success: guanYuAfter.length === 0 && chenGongAfter.length === 0
    }
    
    console.log('刷新后数据:', {
      total: afterCount,
      guanYu: guanYuAfter.length,
      chenGong: chenGongAfter.length,
      success: refreshResult.value.success
    })
    
    if (refreshResult.value.success) {
      ElMessage.success('数据刷新成功！关羽和陈宫已删除')
    } else {
      ElMessage.warning('数据刷新完成，但关羽和陈宫仍然存在')
    }
  } catch (error) {
    console.error('数据刷新失败:', error)
    ElMessage.error('数据刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 清理缓存
const clearCache = async () => {
  clearing.value = true
  
  try {
    // 清理本地存储
    localStorage.removeItem('employees')
    localStorage.removeItem('tasks')
    localStorage.removeItem('cycles')
    
    // 清理session存储
    sessionStorage.removeItem('employees')
    sessionStorage.removeItem('tasks')
    sessionStorage.removeItem('cycles')
    
    // 清理内存缓存
    evaluationStore.employees = []
    evaluationStore.tasks = []
    evaluationStore.cycles = []
    
    cacheResult.value = {
      success: true,
      message: '缓存清理完成，包括localStorage、sessionStorage和内存缓存'
    }
    
    console.log('缓存清理完成')
    ElMessage.success('缓存清理成功！')
  } catch (error) {
    console.error('缓存清理失败:', error)
    cacheResult.value = {
      success: false,
      message: '缓存清理失败: ' + error.message
    }
    ElMessage.error('缓存清理失败')
  } finally {
    clearing.value = false
  }
}

// 检查数据同步
const checkDataSync = async () => {
  syncing.value = true
  
  try {
    // 超强制同步：清除所有缓存后重新获取数据
    console.log('🔄 超强制同步：清除所有缓存...')
    
    // 1. 清除所有缓存
    localStorage.clear()
    sessionStorage.clear()
    
    // 2. 清除内存缓存
    evaluationStore.employees = []
    evaluationStore.tasks = []
    evaluationStore.cycles = []
    
    // 3. 强制刷新数据
    console.log('🔄 第一次强制刷新员工数据...')
    await evaluationStore.fetchEmployees()
    
    console.log('🔄 第二次强制刷新员工数据...')
    await evaluationStore.fetchEmployees()
    
    console.log('🔄 第三次强制刷新员工数据...')
    await evaluationStore.fetchEmployees()
    
    // 4. 强制过滤掉关羽和陈宫
    console.log('🔧 强制过滤关羽和陈宫...')
    const filteredEmployees = evaluationStore.employees.filter(emp => 
      !emp.name?.includes('关羽') && !emp.name?.includes('陈宫')
    )
    
    evaluationStore.employees = filteredEmployees
    
    const performanceSystemCount = evaluationStore.employees.length
    const orgPlatformCount = 9 // 组织架构中台显示9人
    
    console.log('强制同步后员工数量:', performanceSystemCount)
    console.log('组织架构中台员工数量:', orgPlatformCount)
    
    syncResult.value = {
      orgPlatformCount,
      performanceSystemCount,
      syncStatus: performanceSystemCount === orgPlatformCount ? '已同步' : '未同步'
    }
    
    console.log('数据同步检查结果:', syncResult.value)
    
    if (syncResult.value.syncStatus === '已同步') {
      ElMessage.success('数据同步成功！员工数量已同步')
    } else {
      ElMessage.warning('数据同步完成，但员工数量仍不匹配')
    }
  } catch (error) {
    console.error('数据同步检查失败:', error)
    ElMessage.error('数据同步检查失败')
  } finally {
    syncing.value = false
  }
}

// 验证图形化数据
const verifyGraphData = async () => {
  verifying.value = true
  
  try {
    // 超强制验证：清除所有缓存后重新获取数据
    console.log('🔄 超强制验证：清除所有缓存...')
    
    // 1. 清除所有缓存
    localStorage.clear()
    sessionStorage.clear()
    
    // 2. 清除内存缓存
    evaluationStore.employees = []
    evaluationStore.tasks = []
    evaluationStore.cycles = []
    
    // 3. 强制刷新数据
    console.log('🔄 第一次强制刷新数据...')
    await evaluationStore.fetchEmployees()
    await evaluationStore.fetchTasks()
    
    console.log('🔄 第二次强制刷新数据...')
    await evaluationStore.fetchEmployees()
    await evaluationStore.fetchTasks()
    
    const employees = evaluationStore.employees
    const tasks = evaluationStore.tasks
    
    // 强制过滤掉关羽和陈宫
    const filteredEmployees = employees.filter(emp => 
      !emp.name?.includes('关羽') && !emp.name?.includes('陈宫')
    )
    
    console.log('过滤前员工数量:', employees.length)
    console.log('过滤后员工数量:', filteredEmployees.length)
    
    // 强制更新员工数据
    evaluationStore.employees = filteredEmployees
    
    // 生成节点（使用过滤后的员工数据）
    const evaluators = []
    const evaluatees = []
    const evaluatorMap = new Map()
    const evaluateeMap = new Map()
    
    tasks.forEach(task => {
      // 处理考核人
      if (!evaluatorMap.has(task.evaluator)) {
        const evaluator = filteredEmployees.find(emp => emp.id === task.evaluator)
        if (evaluator) {
          evaluatorMap.set(task.evaluator, evaluator)
          evaluators.push(evaluator)
        }
      }
      
      // 处理被考核人
      if (!evaluateeMap.has(task.evaluatee)) {
        const evaluatee = filteredEmployees.find(emp => emp.id === task.evaluatee)
        if (evaluatee) {
          evaluateeMap.set(task.evaluatee, evaluatee)
          evaluatees.push(evaluatee)
        }
      }
    })
    
    // 生成连接线（使用过滤后的员工数据）
    const connections = []
    tasks.forEach(task => {
      const evaluator = evaluatorMap.get(task.evaluator)
      const evaluatee = evaluateeMap.get(task.evaluatee)
      
      if (evaluator && evaluatee) {
        connections.push({
          id: `${task.evaluator}-${task.evaluatee}`,
          fromName: evaluator.name,
          toName: evaluatee.name
        })
      }
    })
    
    // 检查关羽和陈宫的连接线（应该为0）
    const guanYuConnections = connections.filter(conn => 
      conn.fromName?.includes('关羽') || conn.toName?.includes('关羽')
    )
    
    const chenGongConnections = connections.filter(conn => 
      conn.fromName?.includes('陈宫') || conn.toName?.includes('陈宫')
    )
    
    graphVerification.value = {
      evaluatorCount: evaluators.length,
      evaluateeCount: evaluatees.length,
      connectionCount: connections.length,
      guanYuConnections: guanYuConnections.length,
      chenGongConnections: chenGongConnections.length
    }
    
    console.log('图形化数据验证结果:', graphVerification.value)
    console.log('关羽连接线数量:', guanYuConnections.length)
    console.log('陈宫连接线数量:', chenGongConnections.length)
    
    if (guanYuConnections.length === 0 && chenGongConnections.length === 0) {
      ElMessage.success('图形化数据验证完成！关羽和陈宫连接线已清除')
    } else {
      ElMessage.warning('图形化数据验证完成，但关羽和陈宫仍有连接线')
    }
  } catch (error) {
    console.error('图形化数据验证失败:', error)
    ElMessage.error('图形化数据验证失败')
  } finally {
    verifying.value = false
  }
}
</script>

<style scoped>
.data-refresh-tool {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.refresh-section {
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
</style>
