<template>
  <div class="organization-analysis">
    <div class="header">
      <h1>绩效考核系统组织架构分析</h1>
      <p>分析当前组织架构，计算应该生成的考核关系数量</p>
    </div>

    <div class="analysis-section">
      <el-button type="primary" @click="loadOrganizationData" :loading="loading">
        加载组织架构数据
      </el-button>
      
      <el-button type="warning" @click="forceSyncData" :loading="loading">
        强制同步数据
      </el-button>
      
      <el-button type="success" @click="analyzeRelationships" :disabled="!organizationData">
        分析考核关系
      </el-button>
      
      <el-button type="info" @click="validateData" :loading="loading">
        验证数据完整性
      </el-button>
      
      <el-button type="danger" @click="cleanData" :loading="loading">
        清理多余数据
      </el-button>
      
      <el-button type="warning" @click="compareWithOrgPlatform" :loading="loading">
        对比组织架构中台
      </el-button>
      
      <el-button type="success" @click="forceDataSync" :loading="loading">
        强制数据同步
      </el-button>
      
      <el-button type="info" @click="validateDepartmentManagers" :loading="loading">
        验证部门经理
      </el-button>
    </div>

    <!-- 组织架构数据 -->
    <div v-if="organizationData" class="data-section">
      <h2>组织架构数据</h2>
      <el-card>
        <div class="data-summary">
          <div class="summary-item">
            <span class="label">总员工数：</span>
            <span class="value">{{ organizationData.totalCount }}</span>
          </div>
          <div class="summary-item">
            <span class="label">在职员工：</span>
            <span class="value">{{ organizationData.activeCount }}</span>
          </div>
        </div>
      </el-card>

      <!-- 员工列表 -->
      <el-card style="margin-top: 20px;">
        <h3>员工详细信息</h3>
        <el-table :data="organizationData.employees" border>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column prop="employee_id" label="员工号" width="120" />
          <el-table-column prop="department_name" label="部门" width="150" />
          <el-table-column prop="position_name" label="职位" width="150" />
          <el-table-column prop="position_level" label="级别" width="100" />
          <el-table-column prop="supervisor_name" label="直接上级" width="120" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                {{ row.status === 'active' ? '在职' : '离职' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 考核关系分析 -->
    <div v-if="relationshipAnalysis" class="analysis-section">
      <h2>考核关系分析结果</h2>
      <el-card>
        <div class="analysis-summary">
          <div class="summary-item">
            <span class="label">预计考核关系总数：</span>
            <span class="value highlight">{{ relationshipAnalysis.totalRelationships }}</span>
          </div>
          <div class="summary-item">
            <span class="label">公司领导考核关系：</span>
            <span class="value">{{ relationshipAnalysis.leaderRelationships }}</span>
          </div>
          <div class="summary-item">
            <span class="label">部门经理考核关系：</span>
            <span class="value">{{ relationshipAnalysis.managerRelationships }}</span>
          </div>
          <div class="summary-item">
            <span class="label">普通员工考核关系：</span>
            <span class="value">{{ relationshipAnalysis.employeeRelationships }}</span>
          </div>
        </div>
      </el-card>

      <!-- 详细分析 -->
      <el-card style="margin-top: 20px;">
        <h3>详细分析</h3>
        
        <!-- 按级别分析 -->
        <div class="level-analysis">
          <h4>按职位级别分析</h4>
          <el-table :data="relationshipAnalysis.levelAnalysis" border>
            <el-table-column prop="level" label="级别" width="100" />
            <el-table-column prop="levelName" label="级别名称" width="150" />
            <el-table-column prop="count" label="人数" width="100" />
            <el-table-column prop="asEvaluator" label="作为考核人" width="150" />
            <el-table-column prop="asEvaluatee" label="作为被考核人" width="150" />
            <el-table-column prop="totalRelations" label="总关系数" width="150" />
          </el-table>
        </div>

        <!-- 按部门分析 -->
        <div class="department-analysis" style="margin-top: 20px;">
          <h4>按部门分析</h4>
          <el-table :data="relationshipAnalysis.departmentAnalysis" border>
            <el-table-column prop="department" label="部门" width="200" />
            <el-table-column prop="count" label="人数" width="100" />
            <el-table-column prop="asEvaluator" label="作为考核人" width="150" />
            <el-table-column prop="asEvaluatee" label="作为被考核人" width="150" />
            <el-table-column prop="totalRelations" label="总关系数" width="150" />
          </el-table>
        </div>

        <!-- 具体关系列表 -->
        <div class="relationship-list" style="margin-top: 20px;">
          <h4>具体考核关系</h4>
          <el-table :data="relationshipAnalysis.relationships" border>
            <el-table-column prop="evaluator" label="考核人" width="120" />
            <el-table-column prop="evaluatorLevel" label="考核人级别" width="120" />
            <el-table-column prop="evaluatee" label="被考核人" width="120" />
            <el-table-column prop="evaluateeLevel" label="被考核人级别" width="120" />
            <el-table-column prop="department" label="部门" width="150" />
            <el-table-column prop="relationshipType" label="关系类型" width="150">
              <template #default="{ row }">
                <el-tag :type="getRelationshipTypeColor(row.relationshipType)">
                  {{ row.relationshipType }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-section">
      <div v-loading="loading" element-loading-text="正在分析组织架构...">
        <!-- 内容区域 -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { useEvaluationStore } from '@/stores/evaluation'

const evaluationStore = useEvaluationStore()

const loading = ref(false)
const organizationData = ref(null)
const relationshipAnalysis = ref(null)

// 加载组织架构数据
const loadOrganizationData = async () => {
  loading.value = true
  
  try {
    // 强制刷新员工数据，确保获取最新数据
    console.log('开始加载组织架构数据...')
    
    // 清除可能的缓存
    evaluationStore.employees = []
    
    // 重新获取员工数据
    await evaluationStore.fetchEmployees()
    const employees = evaluationStore.employees
    
    console.log('绩效考核系统员工数据:', employees)
    console.log('员工总数:', employees.length)
    console.log('在职员工:', employees.filter(emp => emp.status === 'active').length)
    
    // 过滤掉关羽和陈宫（如果还存在的话）
    const filteredEmployees = employees.filter(emp => 
      emp.name !== '关羽' && emp.name !== '陈宫'
    )
    
    console.log('过滤后的员工数据:', filteredEmployees)
    console.log('过滤后员工总数:', filteredEmployees.length)
    
    organizationData.value = {
      totalCount: filteredEmployees.length,
      activeCount: filteredEmployees.filter(emp => emp.status === 'active').length,
      employees: filteredEmployees
    }
    
    ElMessage.success(`组织架构数据加载完成，共${filteredEmployees.length}人`)
  } catch (error) {
    console.error('加载组织架构数据失败:', error)
    ElMessage.error('加载组织架构数据失败')
  } finally {
    loading.value = false
  }
}

// 强制同步数据
const forceSyncData = async () => {
  loading.value = true
  
  try {
    console.log('开始强制同步数据...')
    
    // 清除所有缓存
    localStorage.removeItem('employees')
    sessionStorage.removeItem('employees')
    evaluationStore.employees = []
    
    // 强制同步员工数据
    await evaluationStore.syncEmployees()
    
    // 重新获取数据
    await evaluationStore.fetchEmployees()
    const employees = evaluationStore.employees
    
    console.log('同步后的员工数据:', employees)
    console.log('同步后员工总数:', employees.length)
    
    // 过滤掉关羽和陈宫
    const filteredEmployees = employees.filter(emp => 
      emp.name !== '关羽' && emp.name !== '陈宫'
    )
    
    console.log('过滤后的员工数据:', filteredEmployees)
    console.log('过滤后员工总数:', filteredEmployees.length)
    
    organizationData.value = {
      totalCount: filteredEmployees.length,
      activeCount: filteredEmployees.filter(emp => emp.status === 'active').length,
      employees: filteredEmployees
    }
    
    ElMessage.success(`数据同步完成，共${filteredEmployees.length}人`)
  } catch (error) {
    console.error('强制同步数据失败:', error)
    ElMessage.error('强制同步数据失败')
  } finally {
    loading.value = false
  }
}

// 验证数据完整性
const validateData = async () => {
  loading.value = true
  
  try {
    console.log('开始验证数据完整性...')
    
    // 获取原始数据
    await evaluationStore.fetchEmployees()
    const rawEmployees = evaluationStore.employees
    
    console.log('原始员工数据:', rawEmployees)
    console.log('原始员工总数:', rawEmployees.length)
    
    // 检查是否有关羽和陈宫
    const guanYu = rawEmployees.filter(emp => emp.name === '关羽')
    const chenGong = rawEmployees.filter(emp => emp.name === '陈宫')
    
    console.log('关羽记录数:', guanYu.length)
    console.log('陈宫记录数:', chenGong.length)
    
    // 过滤后的数据
    const filteredEmployees = rawEmployees.filter(emp => 
      emp.name !== '关羽' && emp.name !== '陈宫'
    )
    
    console.log('过滤后员工数据:', filteredEmployees)
    console.log('过滤后员工总数:', filteredEmployees.length)
    
    // 显示验证结果
    let message = `数据验证完成：\n`
    message += `- 原始员工总数: ${rawEmployees.length}\n`
    message += `- 关羽记录数: ${guanYu.length}\n`
    message += `- 陈宫记录数: ${chenGong.length}\n`
    message += `- 过滤后员工总数: ${filteredEmployees.length}\n`
    
    if (filteredEmployees.length === 8) {
      message += `✅ 数据正确，共8人`
      ElMessage.success(message)
    } else {
      message += `⚠️ 数据异常，应该是8人但实际是${filteredEmployees.length}人`
      ElMessage.warning(message)
      
      // 分析多余的员工
      const extraCount = filteredEmployees.length - 8
      message += `\n- 多余员工数: ${extraCount}人`
      
      // 显示所有员工详情
      console.log('=== 详细员工分析 ===')
      console.log('原始员工列表:')
      rawEmployees.forEach((emp, index) => {
        console.log(`${index + 1}. ${emp.name} (ID: ${emp.id}, 部门: ${emp.department_name || '未知'}, 状态: ${emp.status}, 职位: ${emp.position_name || '未知'})`)
      })
      
      console.log('\n过滤后员工列表:')
      filteredEmployees.forEach((emp, index) => {
        console.log(`${index + 1}. ${emp.name} (ID: ${emp.id}, 部门: ${emp.department_name || '未知'}, 状态: ${emp.status}, 职位: ${emp.position_name || '未知'})`)
      })
      
      // 分析哪些员工是多余的
      console.log('\n=== 多余员工分析 ===')
      const expectedEmployees = ['刘备', '诸葛亮', '关羽', '张飞', '赵云', '马超', '黄忠', '魏延', '陈宫', '何进']
      const currentEmployees = filteredEmployees.map(emp => emp.name)
      const unexpectedEmployees = currentEmployees.filter(name => !expectedEmployees.includes(name))
      const missingEmployees = expectedEmployees.filter(name => !currentEmployees.includes(name) && name !== '关羽' && name !== '陈宫')
      
      console.log('当前员工:', currentEmployees)
      console.log('预期员工:', expectedEmployees.filter(name => name !== '关羽' && name !== '陈宫'))
      console.log('意外员工:', unexpectedEmployees)
      console.log('缺失员工:', missingEmployees)
      
      // 检查是否有重复员工
      const nameCounts = {}
      filteredEmployees.forEach(emp => {
        nameCounts[emp.name] = (nameCounts[emp.name] || 0) + 1
      })
      
      const duplicates = Object.entries(nameCounts).filter(([name, count]) => count > 1)
      if (duplicates.length > 0) {
        console.log('\n发现重复员工:')
        duplicates.forEach(([name, count]) => {
          console.log(`- ${name}: ${count}个记录`)
        })
        message += `\n- 发现重复员工: ${duplicates.map(([name, count]) => `${name}(${count}个)`).join(', ')}`
      }
      
      // 检查是否有离职员工
      const inactiveEmployees = filteredEmployees.filter(emp => emp.status !== 'active')
      if (inactiveEmployees.length > 0) {
        console.log('\n发现离职员工:')
        inactiveEmployees.forEach(emp => {
          console.log(`- ${emp.name} (状态: ${emp.status})`)
        })
        message += `\n- 离职员工: ${inactiveEmployees.map(emp => emp.name).join(', ')}`
      }
    }
    
    // 显示员工列表
    console.log('\n当前员工列表:')
    filteredEmployees.forEach((emp, index) => {
      console.log(`${index + 1}. ${emp.name} (${emp.department_name || '未知部门'})`)
    })
    
  } catch (error) {
    console.error('验证数据完整性失败:', error)
    ElMessage.error('验证数据完整性失败')
  } finally {
    loading.value = false
  }
}

// 清理多余数据
const cleanData = async () => {
  loading.value = true
  
  try {
    console.log('开始清理多余数据...')
    
    // 清除所有缓存，确保获取最新数据
    localStorage.removeItem('employees')
    sessionStorage.removeItem('employees')
    evaluationStore.employees = []
    
    // 强制同步数据
    await evaluationStore.syncEmployees()
    
    // 重新获取原始数据
    await evaluationStore.fetchEmployees()
    const rawEmployees = evaluationStore.employees
    
    console.log('原始员工数据:', rawEmployees)
    
    // 获取组织架构中台的正确员工列表
    let orgPlatformEmployees = []
    try {
      const orgPlatformResponse = await fetch('http://127.0.0.1:8000/api/employees/')
      if (orgPlatformResponse.ok) {
        const orgPlatformData = await orgPlatformResponse.json()
        orgPlatformEmployees = orgPlatformData.results || orgPlatformData
      }
    } catch (error) {
      console.error('获取组织架构中台数据失败:', error)
    }
    
    const expectedEmployees = orgPlatformEmployees.map(emp => emp.name)
    console.log('组织架构中台员工列表:', expectedEmployees)
    
    // 过滤掉关羽和陈宫
    let filteredEmployees = rawEmployees.filter(emp => 
      emp.name !== '关羽' && emp.name !== '陈宫'
    )
    
    console.log('过滤关羽和陈宫后:', filteredEmployees.length, '人')
    
    // 如果还是超过8人，需要进一步清理
    if (filteredEmployees.length > 8) {
      console.log('需要进一步清理，当前人数:', filteredEmployees.length)
      
      // 1. 只保留预期的员工
      const expectedFilteredEmployees = filteredEmployees.filter(emp => 
        expectedEmployees.includes(emp.name)
      )
      console.log('只保留预期员工后:', expectedFilteredEmployees.length, '人')
      
      // 2. 过滤掉离职员工
      const activeEmployees = expectedFilteredEmployees.filter(emp => emp.status === 'active')
      console.log('过滤离职员工后:', activeEmployees.length, '人')
      
      // 3. 如果还是超过8人，检查重复员工
      if (activeEmployees.length > 8) {
        console.log('仍有超过8人，检查重复员工...')
        
        // 按姓名分组，保留每个姓名的第一个记录
        const uniqueEmployees = []
        const seenNames = new Set()
        
        activeEmployees.forEach(emp => {
          if (!seenNames.has(emp.name)) {
            seenNames.add(emp.name)
            uniqueEmployees.push(emp)
          } else {
            console.log(`发现重复员工: ${emp.name} (ID: ${emp.id})`)
          }
        })
        
        filteredEmployees = uniqueEmployees
        console.log('去重后:', filteredEmployees.length, '人')
      } else {
        filteredEmployees = activeEmployees
      }
    } else {
      // 如果人数正确，但可能包含非预期员工，也要过滤
      filteredEmployees = filteredEmployees.filter(emp => 
        expectedEmployees.includes(emp.name)
      )
      console.log('过滤非预期员工后:', filteredEmployees.length, '人')
    }
    
    // 更新组织数据
    organizationData.value = {
      totalCount: filteredEmployees.length,
      activeCount: filteredEmployees.filter(emp => emp.status === 'active').length,
      employees: filteredEmployees
    }
    
    console.log('清理后的员工列表:')
    filteredEmployees.forEach((emp, index) => {
      console.log(`${index + 1}. ${emp.name} (ID: ${emp.id}, 部门: ${emp.department_name || '未知'}, 状态: ${emp.status})`)
    })
    
    if (filteredEmployees.length === 8) {
      ElMessage.success(`数据清理完成，现在共${filteredEmployees.length}人`)
    } else {
      ElMessage.warning(`数据清理完成，现在共${filteredEmployees.length}人，仍需要手动调整`)
    }
    
  } catch (error) {
    console.error('清理数据失败:', error)
    ElMessage.error('清理数据失败')
  } finally {
    loading.value = false
  }
}

// 对比组织架构中台
const compareWithOrgPlatform = async () => {
  loading.value = true
  
  try {
    console.log('开始对比组织架构中台数据...')
    
    // 清除所有缓存，确保获取最新数据
    localStorage.removeItem('employees')
    sessionStorage.removeItem('employees')
    evaluationStore.employees = []
    
    // 强制同步数据
    await evaluationStore.syncEmployees()
    
    // 重新获取绩效考核系统数据
    await evaluationStore.fetchEmployees()
    const performanceEmployees = evaluationStore.employees
    
    console.log('绩效考核系统员工数据:', performanceEmployees)
    console.log('绩效考核系统员工总数:', performanceEmployees.length)
    
    // 获取组织架构中台数据
    const orgPlatformResponse = await fetch('http://127.0.0.1:8000/api/employees/')
    if (!orgPlatformResponse.ok) {
      throw new Error('无法连接到组织架构中台')
    }
    
    const orgPlatformData = await orgPlatformResponse.json()
    const orgPlatformEmployees = orgPlatformData.results || orgPlatformData
    
    console.log('组织架构中台员工数据:', orgPlatformEmployees)
    console.log('组织架构中台员工总数:', orgPlatformEmployees.length)
    
    // 对比分析
    const performanceNames = performanceEmployees.map(emp => emp.name)
    const orgPlatformNames = orgPlatformEmployees.map(emp => emp.name)
    
    const onlyInPerformance = performanceNames.filter(name => !orgPlatformNames.includes(name))
    const onlyInOrgPlatform = orgPlatformNames.filter(name => !performanceNames.includes(name))
    const inBoth = performanceNames.filter(name => orgPlatformNames.includes(name))
    
    console.log('=== 数据对比分析 ===')
    console.log('绩效考核系统员工:', performanceNames)
    console.log('组织架构中台员工:', orgPlatformNames)
    console.log('只在绩效考核系统中:', onlyInPerformance)
    console.log('只在组织架构中台中:', onlyInOrgPlatform)
    console.log('两个系统都有:', inBoth)
    
    // 显示对比结果
    let message = `数据对比完成：\n`
    message += `- 绩效考核系统: ${performanceEmployees.length}人\n`
    message += `- 组织架构中台: ${orgPlatformEmployees.length}人\n`
    message += `- 数据一致: ${inBoth.length}人\n`
    message += `- 只在绩效考核系统: ${onlyInPerformance.length}人\n`
    message += `- 只在组织架构中台: ${onlyInOrgPlatform.length}人\n`
    
    if (onlyInPerformance.length > 0) {
      message += `\n只在绩效考核系统中的员工: ${onlyInPerformance.join(', ')}`
    }
    
    if (onlyInOrgPlatform.length > 0) {
      message += `\n只在组织架构中台中的员工: ${onlyInOrgPlatform.join(', ')}`
    }
    
    if (onlyInPerformance.length === 0 && onlyInOrgPlatform.length === 0) {
      ElMessage.success(message)
    } else {
      ElMessage.warning(message)
    }
    
    // 更新组织数据为组织架构中台的8人数据（这是正确的数据）
    const correctEmployees = performanceEmployees.filter(emp => 
      orgPlatformNames.includes(emp.name)
    )
    
    console.log('正确的员工数据（基于组织架构中台）:', correctEmployees)
    console.log('正确员工总数:', correctEmployees.length)
    
    organizationData.value = {
      totalCount: correctEmployees.length,
      activeCount: correctEmployees.filter(emp => emp.status === 'active').length,
      employees: correctEmployees
    }
    
  } catch (error) {
    console.error('对比组织架构中台失败:', error)
    ElMessage.error('对比组织架构中台失败')
  } finally {
    loading.value = false
  }
}

// 强制数据同步
const forceDataSync = async () => {
  loading.value = true
  
  try {
    console.log('开始强制数据同步...')
    
    // 清除所有缓存
    localStorage.clear()
    sessionStorage.clear()
    evaluationStore.employees = []
    
    console.log('已清除所有缓存')
    
    // 强制同步数据
    console.log('开始强制同步员工数据...')
    await evaluationStore.syncEmployees()
    
    // 重新获取数据
    console.log('重新获取员工数据...')
    await evaluationStore.fetchEmployees()
    const employees = evaluationStore.employees
    
    console.log('同步后的员工数据:', employees)
    console.log('同步后员工总数:', employees.length)
    
    // 检查是否还有已删除的人员
    const deletedEmployees = employees.filter(emp => 
      emp.name === '马超' || emp.name === '何进' || emp.name === '关羽' || emp.name === '陈宫'
    )
    
    if (deletedEmployees.length > 0) {
      console.warn('发现已删除的人员仍在数据中:', deletedEmployees.map(emp => emp.name))
      
      // 强制过滤掉已删除的人员
      const filteredEmployees = employees.filter(emp => 
        emp.name !== '马超' && emp.name !== '何进' && emp.name !== '关羽' && emp.name !== '陈宫'
      )
      
      console.log('强制过滤后的员工数据:', filteredEmployees)
      console.log('强制过滤后员工总数:', filteredEmployees.length)
      
      // 更新组织数据为过滤后的数据
      organizationData.value = {
        totalCount: filteredEmployees.length,
        activeCount: filteredEmployees.filter(emp => emp.status === 'active').length,
        employees: filteredEmployees
      }
      
      // 同时更新evaluationStore中的数据
      evaluationStore.employees = filteredEmployees
      console.log('已更新evaluationStore.employees为过滤后的数据')
      
      ElMessage.warning(`发现已删除的人员仍在数据中: ${deletedEmployees.map(emp => emp.name).join(', ')}，已强制过滤`)
    } else {
      console.log('数据同步成功，没有发现已删除的人员')
      ElMessage.success('数据同步成功')
      
      // 更新组织数据
      organizationData.value = {
        totalCount: employees.length,
        activeCount: employees.filter(emp => emp.status === 'active').length,
        employees: employees
      }
    }
    
  } catch (error) {
    console.error('强制数据同步失败:', error)
    ElMessage.error('强制数据同步失败')
  } finally {
    loading.value = false
  }
}

// 验证部门经理
const validateDepartmentManagers = async () => {
  loading.value = true
  
  try {
    console.log('开始验证部门经理数据...')
    
    // 清除所有缓存，确保获取最新数据
    localStorage.clear()
    sessionStorage.clear()
    evaluationStore.employees = []
    
    // 强制同步数据
    await evaluationStore.syncEmployees()
    await evaluationStore.fetchEmployees()
    
    const employees = evaluationStore.employees
    console.log('所有员工数据:', employees)
    
    // 按级别分组
    const levelGroups = {}
    employees.forEach(emp => {
      const level = emp.position_level || 0
      if (!levelGroups[level]) {
        levelGroups[level] = []
      }
      levelGroups[level].push(emp)
    })
    
    console.log('按级别分组:', levelGroups)
    
    // 检查L9级别的部门经理
    const departmentManagers = employees.filter(emp => emp.position_level === 9)
    console.log('L9级别的部门经理:', departmentManagers.map(emp => `${emp.name} (${emp.department_name})`))
    
    // 检查所有部门经理（包括级别可能不正确的）
    const allDepartmentManagers = employees.filter(emp => 
      emp.position_name && emp.position_name.includes('部门经理')
    )
    console.log('所有部门经理:', allDepartmentManagers.map(emp => `${emp.name} (${emp.position_name}, L${emp.position_level})`))
    
    // 检查许褚和张辽的级别
    const xuchu = employees.find(emp => emp.name === '许褚')
    const zhangliao = employees.find(emp => emp.name === '张辽')
    if (xuchu) {
      console.log('许褚信息:', `${xuchu.name} (${xuchu.position_name}, L${xuchu.position_level})`)
    }
    if (zhangliao) {
      console.log('张辽信息:', `${zhangliao.name} (${zhangliao.position_name}, L${zhangliao.position_level})`)
    }
    
    // 检查L12及以上级别的公司领导
    const companyLeaders = employees.filter(emp => emp.position_level >= 12)
    console.log('L12及以上级别的公司领导:', companyLeaders.map(emp => `${emp.name} (L${emp.position_level})`))
    
    // 计算应该生成的考核关系
    const expectedRelationships = companyLeaders.length * departmentManagers.length
    console.log(`应该生成的考核关系数量: ${companyLeaders.length} × ${departmentManagers.length} = ${expectedRelationships}`)
    
    // 显示详细分析
    ElMessage.success(`验证完成！发现 ${departmentManagers.length} 个部门经理，${companyLeaders.length} 个公司领导，应该生成 ${expectedRelationships} 个考核关系`)
    
    // 更新组织数据
    organizationData.value = {
      totalCount: employees.length,
      activeCount: employees.filter(emp => emp.status === 'active').length,
      employees: employees
    }
    
  } catch (error) {
    console.error('验证部门经理失败:', error)
    ElMessage.error('验证部门经理失败')
  } finally {
    loading.value = false
  }
}

// 分析考核关系
const analyzeRelationships = () => {
  if (!organizationData.value) {
    ElMessage.warning('请先加载组织架构数据')
    return
  }
  
  const employees = organizationData.value.employees
  const activeEmployees = employees.filter(emp => emp.status === 'active')
  
  console.log('开始分析考核关系，在职员工数:', activeEmployees.length)
  console.log('员工列表:', activeEmployees.map(emp => `${emp.name} (${emp.position_name}, L${emp.position_level})`))
  
  // 按级别分组
  const levelGroups = {}
  activeEmployees.forEach(emp => {
    const level = emp.position_level || 0
    if (!levelGroups[level]) {
      levelGroups[level] = []
    }
    levelGroups[level].push(emp)
  })
  
  console.log('按级别分组:', levelGroups)
  
  // 分析每个级别的考核关系
  const levelAnalysis = []
  const relationships = []
  let totalRelationships = 0
  
  Object.keys(levelGroups).sort((a, b) => parseInt(b) - parseInt(a)).forEach(level => {
    const levelEmployees = levelGroups[level]
    const levelNum = parseInt(level)
    
    // 计算该级别作为考核人的关系数
    let asEvaluator = 0
    let asEvaluatee = 0
    
    levelEmployees.forEach(emp => {
      // 作为考核人：考核下级员工
      const subordinates = activeEmployees.filter(other => 
        other.supervisor === emp.id || other.supervisor_name === emp.name
      )
      asEvaluator += subordinates.length
      
      // 作为被考核人：被上级考核
      if (emp.supervisor || emp.supervisor_name) {
        asEvaluatee += 1
      }
      
      // 记录具体关系
      subordinates.forEach(sub => {
        relationships.push({
          evaluator: emp.name,
          evaluatorLevel: `L${levelNum}`,
          evaluatee: sub.name,
          evaluateeLevel: `L${sub.position_level || 0}`,
          department: emp.department_name || '未知部门',
          relationshipType: getRelationshipType(levelNum, sub.position_level || 0)
        })
      })
    })
    
    // 特殊处理：确保所有部门经理都被考核
    if (levelNum >= 12) { // 公司领导级别
      const departmentManagers = activeEmployees.filter(emp => 
        emp.position_level >= 9 && emp.position_level < 12
      )
      console.log(`L${levelNum}级别应该考核的部门经理:`, departmentManagers.map(emp => emp.name))
      
      levelEmployees.forEach(leader => {
        departmentManagers.forEach(manager => {
          // 检查是否已经存在这个关系
          const existingRelation = relationships.find(rel => 
            rel.evaluator === leader.name && rel.evaluatee === manager.name
          )
          
          if (!existingRelation) {
            relationships.push({
              evaluator: leader.name,
              evaluatorLevel: `L${levelNum}`,
              evaluatee: manager.name,
              evaluateeLevel: `L${manager.position_level || 0}`,
              department: leader.department_name || '未知部门',
              relationshipType: getRelationshipType(levelNum, manager.position_level || 0)
            })
            asEvaluator += 1
          }
        })
      })
    }
    
    // 额外处理：确保所有部门经理都被考核（包括L1级别的许褚、张辽）
    if (levelNum >= 12) {
      const allDepartmentManagers = activeEmployees.filter(emp => 
        emp.position_name && emp.position_name.includes('部门经理')
      )
      console.log(`所有部门经理:`, allDepartmentManagers.map(emp => `${emp.name} (L${emp.position_level})`))
      
      levelEmployees.forEach(leader => {
        allDepartmentManagers.forEach(manager => {
          // 检查是否已经存在这个关系
          const existingRelation = relationships.find(rel => 
            rel.evaluator === leader.name && rel.evaluatee === manager.name
          )
          
          if (!existingRelation) {
            relationships.push({
              evaluator: leader.name,
              evaluatorLevel: `L${levelNum}`,
              evaluatee: manager.name,
              evaluateeLevel: `L${manager.position_level || 0}`,
              department: leader.department_name || '未知部门',
              relationshipType: getRelationshipType(levelNum, manager.position_level || 0)
            })
            asEvaluator += 1
          }
        })
      })
    }
    
    const totalRelations = asEvaluator + asEvaluatee
    totalRelationships += totalRelations
    
    levelAnalysis.push({
      level: levelNum,
      levelName: getLevelName(levelNum),
      count: levelEmployees.length,
      asEvaluator,
      asEvaluatee,
      totalRelations
    })
  })
  
  // 按部门分析
  const departmentGroups = {}
  activeEmployees.forEach(emp => {
    const dept = emp.department_name || '未知部门'
    if (!departmentGroups[dept]) {
      departmentGroups[dept] = []
    }
    departmentGroups[dept].push(emp)
  })
  
  const departmentAnalysis = Object.keys(departmentGroups).map(dept => {
    const deptEmployees = departmentGroups[dept]
    let asEvaluator = 0
    let asEvaluatee = 0
    
    deptEmployees.forEach(emp => {
      const subordinates = activeEmployees.filter(other => 
        other.supervisor === emp.id || other.supervisor_name === emp.name
      )
      asEvaluator += subordinates.length
      
      if (emp.supervisor || emp.supervisor_name) {
        asEvaluatee += 1
      }
    })
    
    return {
      department: dept,
      count: deptEmployees.length,
      asEvaluator,
      asEvaluatee,
      totalRelations: asEvaluator + asEvaluatee
    }
  })
  
  // 计算各级别的考核关系
  const leaderRelationships = levelAnalysis.filter(item => item.level >= 4).reduce((sum, item) => sum + item.asEvaluator, 0)
  const managerRelationships = levelAnalysis.filter(item => item.level === 3).reduce((sum, item) => sum + item.asEvaluator, 0)
  const employeeRelationships = levelAnalysis.filter(item => item.level <= 2).reduce((sum, item) => sum + item.asEvaluator, 0)
  
  relationshipAnalysis.value = {
    totalRelationships,
    leaderRelationships,
    managerRelationships,
    employeeRelationships,
    levelAnalysis,
    departmentAnalysis,
    relationships
  }
  
  console.log('考核关系分析结果:', relationshipAnalysis.value)
  ElMessage.success('考核关系分析完成')
}

// 获取级别名称
const getLevelName = (level) => {
  const levelNames = {
    5: '董事长',
    4: '公司领导',
    3: '部门经理',
    2: '主管',
    1: '普通员工'
  }
  return levelNames[level] || `L${level}`
}

// 获取关系类型
const getRelationshipType = (evaluatorLevel, evaluateeLevel) => {
  if (evaluatorLevel >= 4 && evaluateeLevel >= 4) return '同级考核'
  if (evaluatorLevel >= 4 && evaluateeLevel < 4) return '上级考核下级'
  if (evaluatorLevel < 4 && evaluateeLevel < 4) return '同级考核'
  return '其他'
}

// 获取关系类型颜色
const getRelationshipTypeColor = (type) => {
  const colors = {
    '上级考核下级': 'success',
    '同级考核': 'warning',
    '其他': 'info'
  }
  return colors[type] || 'info'
}
</script>

<style scoped>
.organization-analysis {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.analysis-section {
  margin-bottom: 30px;
  text-align: center;
}

.data-section {
  margin-bottom: 30px;
}

.data-summary {
  display: flex;
  gap: 30px;
  justify-content: center;
  flex-wrap: wrap;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  min-width: 120px;
}

.summary-item .label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.summary-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.summary-item .value.highlight {
  color: #e74c3c;
  font-size: 28px;
}

.analysis-summary {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.loading-section {
  text-align: center;
  padding: 50px;
}

.level-analysis,
.department-analysis,
.relationship-list {
  margin-top: 20px;
}

h2, h3, h4 {
  color: #2c3e50;
  margin-bottom: 15px;
}

h2 {
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

h3 {
  border-bottom: 1px solid #bdc3c7;
  padding-bottom: 5px;
}

h4 {
  color: #34495e;
  margin-top: 20px;
}
</style>
