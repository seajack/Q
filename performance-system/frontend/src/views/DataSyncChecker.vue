<template>
  <div class="data-sync-checker">
    <h1>数据同步检查工具</h1>
    
    <div class="check-section">
      <h2>1. 组织架构中台数据检查</h2>
      <el-button type="primary" @click="checkOrgPlatformData" :loading="checking">
        检查组织架构中台数据
      </el-button>
      
      <div v-if="orgPlatformData">
        <h3>组织架构中台员工数据:</h3>
        <div class="data-info">
          <p><strong>总员工数:</strong> {{ orgPlatformData.totalCount }}</p>
          <p><strong>活跃员工数:</strong> {{ orgPlatformData.activeCount }}</p>
        </div>
        
        <div class="employee-list">
          <h4>员工列表:</h4>
          <div v-for="emp in orgPlatformData.employees" :key="emp.id" class="employee-item">
            <p><strong>姓名:</strong> {{ emp.name }}</p>
            <p><strong>部门:</strong> {{ emp.department_name }}</p>
            <p><strong>职位:</strong> {{ emp.position_name }}</p>
            <p><strong>级别:</strong> {{ emp.position_level }}</p>
            <p><strong>状态:</strong> {{ emp.status }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="check-section">
      <h2>2. 绩效考核系统数据检查</h2>
      <el-button type="success" @click="checkPerformanceSystemData" :loading="checking">
        检查绩效考核系统数据
      </el-button>
      
      <div v-if="performanceSystemData">
        <h3>绩效考核系统员工数据:</h3>
        <div class="data-info">
          <p><strong>总员工数:</strong> {{ performanceSystemData.totalCount }}</p>
          <p><strong>活跃员工数:</strong> {{ performanceSystemData.activeCount }}</p>
        </div>
        
        <div class="employee-list">
          <h4>员工列表:</h4>
          <div v-for="emp in performanceSystemData.employees" :key="emp.id" class="employee-item">
            <p><strong>姓名:</strong> {{ emp.name }}</p>
            <p><strong>部门:</strong> {{ emp.department_name }}</p>
            <p><strong>职位:</strong> {{ emp.position_name }}</p>
            <p><strong>级别:</strong> {{ emp.position_level }}</p>
            <p><strong>状态:</strong> {{ emp.status }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="check-section">
      <h2>3. 数据同步对比</h2>
      <el-button type="warning" @click="compareDataSync" :loading="checking">
        对比数据同步情况
      </el-button>
      
      <div v-if="syncComparison">
        <h3>数据同步对比结果:</h3>
        <div class="comparison-info">
          <div class="comparison-item">
            <h4>组织架构中台:</h4>
            <p>员工数量: {{ syncComparison.orgPlatformCount }}</p>
            <p>部门数量: {{ syncComparison.orgPlatformDepartments }}</p>
          </div>
          
          <div class="comparison-item">
            <h4>绩效考核系统:</h4>
            <p>员工数量: {{ syncComparison.performanceSystemCount }}</p>
            <p>部门数量: {{ syncComparison.performanceSystemDepartments }}</p>
          </div>
          
          <div class="comparison-item">
            <h4>同步状态:</h4>
            <p :class="syncComparison.syncStatus === '已同步' ? 'sync-success' : 'sync-error'">
              {{ syncComparison.syncStatus }}
            </p>
          </div>
        </div>
        
        <div v-if="syncComparison.missingEmployees.length > 0" class="missing-employees">
          <h4>缺失的员工:</h4>
          <div v-for="emp in syncComparison.missingEmployees" :key="emp.id" class="missing-employee">
            <p><strong>姓名:</strong> {{ emp.name }}</p>
            <p><strong>部门:</strong> {{ emp.department_name }}</p>
            <p><strong>职位:</strong> {{ emp.position_name }}</p>
          </div>
        </div>
        
        <div v-if="syncComparison.extraEmployees.length > 0" class="extra-employees">
          <h4>多余的员工:</h4>
          <div v-for="emp in syncComparison.extraEmployees" :key="emp.id" class="extra-employee">
            <p><strong>姓名:</strong> {{ emp.name }}</p>
            <p><strong>部门:</strong> {{ emp.department_name }}</p>
            <p><strong>职位:</strong> {{ emp.position_name }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="check-section">
      <h2>4. 何进数据专项检查</h2>
      <el-button type="info" @click="checkHeJinData" :loading="checking">
        检查何进数据
      </el-button>
      
      <div v-if="heJinData">
        <h3>何进数据检查结果:</h3>
        <div class="hejin-info">
          <div class="hejin-item">
            <h4>组织架构中台:</h4>
            <p v-if="heJinData.orgPlatformFound">
              <strong>状态:</strong> 已找到
            </p>
            <p v-else>
              <strong>状态:</strong> 未找到
            </p>
            <div v-if="heJinData.orgPlatformEmployee">
              <p><strong>姓名:</strong> {{ heJinData.orgPlatformEmployee.name }}</p>
              <p><strong>部门:</strong> {{ heJinData.orgPlatformEmployee.department_name }}</p>
              <p><strong>职位:</strong> {{ heJinData.orgPlatformEmployee.position_name }}</p>
              <p><strong>级别:</strong> {{ heJinData.orgPlatformEmployee.position_level }}</p>
            </div>
          </div>
          
          <div class="hejin-item">
            <h4>绩效考核系统:</h4>
            <p v-if="heJinData.performanceSystemFound">
              <strong>状态:</strong> 已找到
            </p>
            <p v-else>
              <strong>状态:</strong> 未找到
            </p>
            <div v-if="heJinData.performanceSystemEmployee">
              <p><strong>姓名:</strong> {{ heJinData.performanceSystemEmployee.name }}</p>
              <p><strong>部门:</strong> {{ heJinData.performanceSystemEmployee.department_name }}</p>
              <p><strong>职位:</strong> {{ heJinData.performanceSystemEmployee.position_name }}</p>
              <p><strong>级别:</strong> {{ heJinData.performanceSystemEmployee.position_level }}</p>
            </div>
          </div>
          
          <div class="hejin-item">
            <h4>同步状态:</h4>
            <p :class="heJinData.syncStatus === '已同步' ? 'sync-success' : 'sync-error'">
              {{ heJinData.syncStatus }}
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="check-section">
      <h2>5. 强制数据同步</h2>
      <el-button type="danger" @click="forceDataSync" :loading="syncing">
        强制数据同步
      </el-button>
      
      <div v-if="syncResult">
        <h3>强制同步结果:</h3>
        <div class="sync-result">
          <p><strong>同步状态:</strong> {{ syncResult.success ? '成功' : '失败' }}</p>
          <p><strong>消息:</strong> {{ syncResult.message }}</p>
          <p v-if="syncResult.syncedCount"><strong>同步数量:</strong> {{ syncResult.syncedCount }}</p>
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
const syncing = ref(false)
const orgPlatformData = ref(null)
const performanceSystemData = ref(null)
const syncComparison = ref(null)
const heJinData = ref(null)
const syncResult = ref(null)

// 检查组织架构中台数据
const checkOrgPlatformData = async () => {
  checking.value = true
  
  try {
    // 模拟从组织架构中台获取数据
    const response = await fetch('http://127.0.0.1:8000/api/employees/')
    if (response.ok) {
      const data = await response.json()
      const employees = data.results || []
      
      orgPlatformData.value = {
        totalCount: employees.length,
        activeCount: employees.filter(emp => emp.status === 'active').length,
        employees: employees
      }
      
      console.log('组织架构中台数据:', orgPlatformData.value)
      ElMessage.success('组织架构中台数据检查完成')
    } else {
      ElMessage.error('无法连接到组织架构中台')
    }
  } catch (error) {
    console.error('组织架构中台数据检查失败:', error)
    ElMessage.error('组织架构中台数据检查失败')
  } finally {
    checking.value = false
  }
}

// 检查绩效考核系统数据
const checkPerformanceSystemData = async () => {
  checking.value = true
  
  try {
    await evaluationStore.fetchEmployees()
    const employees = evaluationStore.employees
    
    performanceSystemData.value = {
      totalCount: employees.length,
      activeCount: employees.filter(emp => emp.status === 'active').length,
      employees: employees
    }
    
    console.log('绩效考核系统数据:', performanceSystemData.value)
    ElMessage.success('绩效考核系统数据检查完成')
  } catch (error) {
    console.error('绩效考核系统数据检查失败:', error)
    ElMessage.error('绩效考核系统数据检查失败')
  } finally {
    checking.value = false
  }
}

// 对比数据同步情况
const compareDataSync = async () => {
  checking.value = true
  
  try {
    // 获取组织架构中台数据
    const orgResponse = await fetch('http://127.0.0.1:8000/api/employees/')
    const orgData = await orgResponse.json()
    const orgEmployees = orgData.results || []
    
    // 获取绩效考核系统数据
    await evaluationStore.fetchEmployees()
    const perfEmployees = evaluationStore.employees
    
    // 对比数据
    const orgEmployeeNames = orgEmployees.map(emp => emp.name)
    const perfEmployeeNames = perfEmployees.map(emp => emp.name)
    
    const missingEmployees = orgEmployees.filter(emp => 
      !perfEmployeeNames.includes(emp.name)
    )
    
    const extraEmployees = perfEmployees.filter(emp => 
      !orgEmployeeNames.includes(emp.name)
    )
    
    const departments = [...new Set(orgEmployees.map(emp => emp.department_name))]
    const perfDepartments = [...new Set(perfEmployees.map(emp => emp.department_name))]
    
    syncComparison.value = {
      orgPlatformCount: orgEmployees.length,
      performanceSystemCount: perfEmployees.length,
      orgPlatformDepartments: departments.length,
      performanceSystemDepartments: perfDepartments.length,
      syncStatus: orgEmployees.length === perfEmployees.length ? '已同步' : '未同步',
      missingEmployees: missingEmployees,
      extraEmployees: extraEmployees
    }
    
    console.log('数据同步对比结果:', syncComparison.value)
    ElMessage.success('数据同步对比完成')
  } catch (error) {
    console.error('数据同步对比失败:', error)
    ElMessage.error('数据同步对比失败')
  } finally {
    checking.value = false
  }
}

// 检查何进数据
const checkHeJinData = async () => {
  checking.value = true
  
  try {
    // 获取组织架构中台数据
    const orgResponse = await fetch('http://127.0.0.1:8000/api/employees/')
    const orgData = await orgResponse.json()
    const orgEmployees = orgData.results || []
    
    // 获取绩效考核系统数据
    await evaluationStore.fetchEmployees()
    const perfEmployees = evaluationStore.employees
    
    // 查找何进
    const orgHeJin = orgEmployees.find(emp => emp.name?.includes('何进'))
    const perfHeJin = perfEmployees.find(emp => emp.name?.includes('何进'))
    
    heJinData.value = {
      orgPlatformFound: !!orgHeJin,
      orgPlatformEmployee: orgHeJin,
      performanceSystemFound: !!perfHeJin,
      performanceSystemEmployee: perfHeJin,
      syncStatus: (!!orgHeJin && !!perfHeJin) ? '已同步' : '未同步'
    }
    
    console.log('何进数据检查结果:', heJinData.value)
    ElMessage.success('何进数据检查完成')
  } catch (error) {
    console.error('何进数据检查失败:', error)
    ElMessage.error('何进数据检查失败')
  } finally {
    checking.value = false
  }
}

// 强制数据同步
const forceDataSync = async () => {
  syncing.value = true
  
  try {
    // 调用绩效考核系统的同步接口
    const response = await fetch('/api/employees/sync/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const result = await response.json()
      syncResult.value = {
        success: true,
        message: result.message,
        syncedCount: result.synced_count
      }
      
      ElMessage.success('强制数据同步成功')
    } else {
      syncResult.value = {
        success: false,
        message: '强制数据同步失败'
      }
      
      ElMessage.error('强制数据同步失败')
    }
  } catch (error) {
    console.error('强制数据同步失败:', error)
    syncResult.value = {
      success: false,
      message: '强制数据同步失败: ' + error.message
    }
    
    ElMessage.error('强制数据同步失败')
  } finally {
    syncing.value = false
  }
}
</script>

<style scoped>
.data-sync-checker {
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

.data-info {
  margin: 20px 0;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.employee-list {
  margin: 20px 0;
}

.employee-item {
  margin: 15px 0;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  border-left: 4px solid #007bff;
}

.comparison-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.comparison-item {
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.sync-success {
  color: #28a745;
  font-weight: bold;
}

.sync-error {
  color: #dc3545;
  font-weight: bold;
}

.missing-employees, .extra-employees {
  margin: 20px 0;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.missing-employees {
  border-left: 4px solid #ffc107;
}

.extra-employees {
  border-left: 4px solid #dc3545;
}

.missing-employee, .extra-employee {
  margin: 10px 0;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.hejin-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.hejin-item {
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.sync-result {
  margin: 20px 0;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}
</style>
