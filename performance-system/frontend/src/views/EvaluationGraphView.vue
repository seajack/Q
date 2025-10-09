<template>
  <div class="evaluation-graph-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">
            <i class="fas fa-project-diagram"></i>
            考核关系可视化
          </h1>
          <p class="page-subtitle">图形化展示考核人员关系和任务分配</p>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="refreshData">
            <i class="fas fa-sync-alt"></i>
            刷新数据
          </el-button>
          <el-button @click="exportReport">
            <i class="fas fa-download"></i>
            导出报告
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon evaluator-icon">
          <i class="fas fa-user-tie"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ evaluatorCount }}</div>
          <div class="stat-label">考核人</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon evaluatee-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ evaluateeCount }}</div>
          <div class="stat-label">被考核人</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon task-icon">
          <i class="fas fa-tasks"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ totalTasks }}</div>
          <div class="stat-label">考核任务</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon connection-icon">
          <i class="fas fa-link"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ connectionCount }}</div>
          <div class="stat-label">考核关系</div>
        </div>
      </div>
    </div>

    <!-- 筛选和视图控制 -->
    <div class="controls-panel">
      <div class="controls-left">
        <el-select v-model="selectedCycle" placeholder="选择考核周期" style="width: 200px">
          <el-option label="全部周期" value="" />
          <el-option 
            v-for="cycle in cycles" 
            :key="cycle.id" 
            :label="cycle.name" 
            :value="cycle.id"
          />
        </el-select>
        
        <el-select v-model="selectedStatus" placeholder="筛选状态" style="width: 150px">
          <el-option label="全部状态" value="" />
          <el-option label="待考核" value="pending" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="已完成" value="completed" />
          <el-option label="已过期" value="overdue" />
        </el-select>
        
        <el-select v-model="selectedDepartment" placeholder="筛选部门" style="width: 150px">
          <el-option label="全部部门" value="" />
          <el-option 
            v-for="dept in departments" 
            :key="dept" 
            :label="dept" 
            :value="dept"
          />
        </el-select>
      </div>
      
      <div class="controls-right">
        <el-button-group>
          <el-button 
            :type="viewMode === 'graph' ? 'primary' : 'default'"
            @click="viewMode = 'graph'"
          >
            <i class="fas fa-project-diagram"></i>
            图形视图
          </el-button>
          <el-button 
            :type="viewMode === 'table' ? 'primary' : 'default'"
            @click="viewMode = 'table'"
          >
            <i class="fas fa-table"></i>
            表格视图
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container" v-loading="loading" element-loading-text="正在加载考核数据...">
        <!-- 内容区域 -->
      </div>
      
      <!-- 图形化视图 -->
      <div v-else-if="viewMode === 'graph'" class="graph-view">
        <EvaluationGraphPanel 
          :evaluators="filteredEvaluators"
          :evaluatees="filteredEvaluatees"
          :connections="filteredConnections"
          @connection-click="handleConnectionClick"
        />
      </div>
      
      <!-- 表格视图 -->
      <div v-else class="table-view">
        <el-table 
          :data="filteredTasks" 
          v-loading="loading"
          border 
          stripe
          style="width: 100%"
        >
          <el-table-column type="index" label="序号" width="80" align="center" />
          <el-table-column prop="evaluation_code" label="考核码" width="180" />
          <el-table-column prop="evaluator_name" label="考核人" width="200">
            <template #default="{ row }">
              <div class="employee-info">
                <div class="employee-name">{{ row.evaluator_name }}</div>
                <div class="employee-position">{{ row.evaluator_position }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="evaluatee_name" label="被考核人" width="200">
            <template #default="{ row }">
              <div class="employee-info">
                <div class="employee-name">{{ row.evaluatee_name }}</div>
                <div class="employee-position">{{ row.evaluatee_position }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="relation_type" label="关系类型" width="120">
            <template #default="{ row }">
              <el-tag>{{ getRelationText(row.relation_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="deadline" label="截止时间" width="160">
            <template #default="{ row }">
              {{ formatDate(row.deadline) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" @click="viewDetails(row)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useEvaluationStore } from '@/stores/evaluation'
import { taskApi, cycleApi, employeeApi } from '@/utils/api'
import type { EvaluationTask, EvaluationCycle, Employee } from '@/types'
import EvaluationGraphPanel from '@/components/EvaluationGraphPanel.vue'

// 使用store
const evaluationStore = useEvaluationStore()

// 响应式数据
const loading = ref(false)
const viewMode = ref<'graph' | 'table'>('graph')
const selectedCycle = ref('')
const selectedStatus = ref('')
const selectedDepartment = ref('')

// 数据
const cycles = ref<EvaluationCycle[]>([])
const departments = ref<string[]>([])
const employees = ref<Employee[]>([])
const tasks = ref<EvaluationTask[]>([])

// 图形化数据
const evaluators = ref<any[]>([])
const evaluatees = ref<any[]>([])
const connections = ref<any[]>([])

// 计算属性
const evaluatorCount = computed(() => evaluators.value.length)
const evaluateeCount = computed(() => evaluatees.value.length)
const totalTasks = computed(() => tasks.value.length)
const connectionCount = computed(() => connections.value.length)

const filteredEvaluators = computed(() => {
  let filtered = evaluators.value
  
  // 强制过滤掉关羽和陈宫
  filtered = filtered.filter(e => 
    !e.name?.includes('关羽') && !e.name?.includes('陈宫')
  )
  
  if (selectedDepartment.value) {
    filtered = filtered.filter(e => e.department === selectedDepartment.value)
  }
  
  return filtered
})

const filteredEvaluatees = computed(() => {
  let filtered = evaluatees.value
  
  // 强制过滤掉关羽和陈宫
  filtered = filtered.filter(e => 
    !e.name?.includes('关羽') && !e.name?.includes('陈宫')
  )
  
  if (selectedDepartment.value) {
    filtered = filtered.filter(e => e.department === selectedDepartment.value)
  }
  
  return filtered
})

const filteredTasks = computed(() => {
  let filtered = tasks.value
  
  // 强制过滤掉关羽和陈宫的任务
  filtered = filtered.filter(t => 
    !t.evaluator_name?.includes('关羽') && 
    !t.evaluator_name?.includes('陈宫') &&
    !t.evaluatee_name?.includes('关羽') && 
    !t.evaluatee_name?.includes('陈宫')
  )
  
  if (selectedStatus.value) {
    filtered = filtered.filter(t => t.status === selectedStatus.value)
  }
  
  if (selectedCycle.value) {
    filtered = filtered.filter(t => t.cycle === Number(selectedCycle.value))
  }
  
  return filtered
})

const filteredConnections = computed(() => {
  return connections.value.filter(conn => {
    const task = tasks.value.find(t => t.id === conn.taskId)
    if (!task) return false
    
    // 强制过滤掉关羽和陈宫的连接线
    if (task.evaluator_name?.includes('关羽') || 
        task.evaluator_name?.includes('陈宫') ||
        task.evaluatee_name?.includes('关羽') || 
        task.evaluatee_name?.includes('陈宫')) {
      return false
    }
    
    if (selectedStatus.value && task.status !== selectedStatus.value) return false
    if (selectedCycle.value && task.cycle !== Number(selectedCycle.value)) return false
    
    return true
  })
})

// 数据加载方法
const loadData = async () => {
  loading.value = true
  try {
    // 强制刷新数据 - 清除缓存
    console.log('🔄 强制刷新数据，清除缓存...')
    
    // 加载考核周期
    await evaluationStore.fetchCycles()
    cycles.value = evaluationStore.cycles
    
    // 强制刷新员工数据 - 清除缓存
    console.log('🔄 强制刷新员工数据...')
    await evaluationStore.fetchEmployees()
    
    // 再次强制刷新，确保获取最新数据
    console.log('🔄 再次强制刷新员工数据...')
    await evaluationStore.fetchEmployees()
    
    const rawEmployees = evaluationStore.employees
    console.log('📊 获取到的员工数据:', rawEmployees)
    console.log('📊 员工总数:', rawEmployees.length)
    
    // 超强制过滤处理 - 直接删除关羽和陈宫
    console.log('🚀 开始超强制过滤处理...')
    console.log('原始员工数据:', rawEmployees)
    
    // 直接过滤掉关羽和陈宫
    const filteredEmployees = rawEmployees.filter(emp => 
      !emp.name?.includes('关羽') && !emp.name?.includes('陈宫')
    )
    
    console.log('过滤前员工数量:', rawEmployees.length)
    console.log('过滤后员工数量:', filteredEmployees.length)
    
    // 检查过滤结果
    const guanYuAfter = filteredEmployees.filter(emp => emp.name?.includes('关羽'))
    const chenGongAfter = filteredEmployees.filter(emp => emp.name?.includes('陈宫'))
    
    console.log('过滤后关羽数量:', guanYuAfter.length)
    console.log('过滤后陈宫数量:', chenGongAfter.length)
    
    if (guanYuAfter.length === 0 && chenGongAfter.length === 0) {
      console.log('✅ 关羽和陈宫已成功过滤')
    } else {
      console.error('❌ 关羽和陈宫过滤失败')
    }
    
    // 强制更新员工数据
    employees.value = filteredEmployees
    
    // 加载考核任务
    await evaluationStore.fetchTasks()
    tasks.value = evaluationStore.tasks
    
    console.log('加载的任务数据:', tasks.value)
    console.log('任务数量:', tasks.value.length)
    
    // 检查关羽和陈宫相关的任务
    const guanYuTasks = tasks.value.filter(task => 
      task.evaluator_name?.includes('关羽') || task.evaluatee_name?.includes('关羽')
    )
    const chenGongTasks = tasks.value.filter(task => 
      task.evaluator_name?.includes('陈宫') || task.evaluatee_name?.includes('陈宫')
    )
    
    console.log('关羽相关任务:', guanYuTasks)
    console.log('陈宫相关任务:', chenGongTasks)
    
    // 处理图形化数据
    processGraphData()
    
    // 提取部门列表
    departments.value = [...new Set(employees.value.map(emp => emp.department_name))]
    
    ElMessage.success('数据加载成功')
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

// 处理图形化数据
const processGraphData = () => {
  console.log('开始处理图形数据...')
  console.log('任务数据:', tasks.value)
  console.log('员工数据:', employees.value)
  
  // 强制去重处理：确保每个员工只有一个记录
  const uniqueEmployees = new Map()
  
  employees.value.forEach((emp, index) => {
    const key = emp.name
    if (!uniqueEmployees.has(key)) {
      uniqueEmployees.set(key, emp)
      console.log(`添加员工 ${index + 1}:`, emp.name, emp.id)
    } else {
      console.log(`跳过重复员工 ${index + 1}:`, emp.name, emp.id, '已存在:', uniqueEmployees.get(key).id)
    }
  })
  
  // 特殊处理：强制只保留一个关羽和一个陈宫
  const guanYuEmployees = employees.value.filter(emp => emp.name?.includes('关羽'))
  const chenGongEmployees = employees.value.filter(emp => emp.name?.includes('陈宫'))
  
  console.log('原始关羽员工:', guanYuEmployees)
  console.log('原始陈宫员工:', chenGongEmployees)
  
  // 如果有关羽，只保留第一个
  if (guanYuEmployees.length > 0) {
    const firstGuanYu = guanYuEmployees[0]
    uniqueEmployees.set('关羽', firstGuanYu)
    console.log('强制保留关羽:', firstGuanYu.name, firstGuanYu.id)
  }
  
  // 如果有陈宫，只保留第一个
  if (chenGongEmployees.length > 0) {
    const firstChenGong = chenGongEmployees[0]
    uniqueEmployees.set('陈宫', firstChenGong)
    console.log('强制保留陈宫:', firstChenGong.name, firstChenGong.id)
  }
  
  const deduplicatedEmployees = Array.from(uniqueEmployees.values())
  console.log('去重后的员工数据:', deduplicatedEmployees)
  console.log('去重前员工数量:', employees.value.length)
  console.log('去重后员工数量:', deduplicatedEmployees.length)
  
  // 最终检查关羽和陈宫的去重情况
  const finalGuanYu = deduplicatedEmployees.filter(emp => emp.name?.includes('关羽'))
  const finalChenGong = deduplicatedEmployees.filter(emp => emp.name?.includes('陈宫'))
  console.log('最终关羽数量:', finalGuanYu.length, finalGuanYu)
  console.log('最终陈宫数量:', finalChenGong.length, finalChenGong)
  
  // 处理考核人数据
  const evaluatorMap = new Map()
  const evaluateeMap = new Map()
  
  tasks.value.forEach((task, index) => {
    // 处理考核人 - 使用姓名匹配而不是ID匹配
    const evaluatorKey = task.evaluator_name || task.evaluator
    if (!evaluatorMap.has(evaluatorKey)) {
      const evaluator = deduplicatedEmployees.find(emp => emp.name === task.evaluator_name)
      console.log('查找考核人:', { taskEvaluatorId: task.evaluator, taskEvaluatorName: task.evaluator_name, foundEvaluator: evaluator })
      
      if (evaluator) {
        evaluatorMap.set(evaluatorKey, {
          id: evaluator.id, // 使用实际员工数据的ID
          name: evaluator.name,
          position: evaluator.position_name,
          department: evaluator.department_name,
          status: 'active',
          x: 300, // 调整左侧列位置，适应更大的SVG
          y: 300 + evaluatorMap.size * 200, // 垂直排列，间距200px，起始位置300px
          selected: false
        })
      } else {
        console.warn('未找到考核人:', task.evaluator, task.evaluator_name)
      }
    }
    
    
    // 处理被考核人 - 使用姓名匹配而不是ID匹配
    const evaluateeKey = task.evaluatee_name || task.evaluatee
    if (!evaluateeMap.has(evaluateeKey)) {
      const evaluatee = deduplicatedEmployees.find(emp => emp.name === task.evaluatee_name)
      console.log('查找被考核人:', { taskEvaluateeId: task.evaluatee, taskEvaluateeName: task.evaluatee_name, foundEvaluatee: evaluatee })
      
      if (evaluatee) {
        evaluateeMap.set(evaluateeKey, {
          id: evaluatee.id, // 使用实际员工数据的ID
          name: evaluatee.name,
          position: evaluatee.position_name,
          department: evaluatee.department_name,
          status: task.status,
          x: 2200, // 进一步调整右侧列位置，确保有足够空间显示完整节点
          y: 300 + evaluateeMap.size * 200, // 垂直排列，间距200px，起始位置300px
          selected: false
        })
      } else {
        console.warn('未找到被考核人:', task.evaluatee, task.evaluatee_name)
      }
    }
  })
  
  evaluators.value = Array.from(evaluatorMap.values())
  evaluatees.value = Array.from(evaluateeMap.values())
  
  console.log('生成的考核人:', evaluators.value)
  console.log('生成的被考核人:', evaluatees.value)
  
  // 生成连接线数据 - 使用姓名匹配
  connections.value = tasks.value.map((task, index) => {
    const evaluator = evaluators.value.find(e => e.name === task.evaluator_name)
    const evaluatee = evaluatees.value.find(e => e.name === task.evaluatee_name)
    
    console.log('处理连接线:', { 
      taskId: task.id,
      evaluatorId: task.evaluator,
      evaluateeId: task.evaluatee,
      evaluatorName: task.evaluator_name,
      evaluateeName: task.evaluatee_name,
      evaluator,
      evaluatee
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
      console.log('生成的连接线:', connection)
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
  
  // 动态调整SVG尺寸
  adjustSvgSize()
  
  // 强制调整SVG尺寸以确保完全显示
  nextTick(() => {
    forceAdjustSvgSize()
    
    // 再次检查并调整，确保完全显示
    setTimeout(() => {
      forceAdjustSvgSize()
    }, 100)
  })
}

// 动态调整SVG尺寸
const adjustSvgSize = () => {
  const allNodes = [...evaluators.value, ...evaluatees.value]
  if (allNodes.length === 0) return
  
  // 计算所有节点的边界
  const minX = Math.min(...allNodes.map(n => n.x))
  const maxX = Math.max(...allNodes.map(n => n.x))
  const minY = Math.min(...allNodes.map(n => n.y))
  const maxY = Math.max(...allNodes.map(n => n.y))
  
  // 添加边距
  const padding = 100
  const requiredWidth = maxX - minX + padding * 2
  const requiredHeight = maxY - minY + padding * 2
  
  console.log('节点边界:', { minX, maxX, minY, maxY })
  console.log('所需尺寸:', { requiredWidth, requiredHeight })
  
  // 设置最小SVG尺寸，确保有足够空间
  const minWidth = 3000 // 进一步大幅增加最小宽度以确保右侧节点完全显示
  const minHeight = 2200 // 进一步大幅增加最小高度以支持更多人员
  
  // 计算实际需要的SVG尺寸，确保所有节点都能完全显示
  const actualRequiredWidth = Math.max(minWidth, maxX + 300) // 右侧留300px边距
  const actualRequiredHeight = Math.max(minHeight, maxY + 200) // 底部留200px边距
  
  console.log('实际需要的SVG尺寸:', { actualRequiredWidth, actualRequiredHeight })
  console.log('当前SVG尺寸:', { minWidth, minHeight })
  
  // 如果节点超出当前SVG边界，调整位置
  if (maxX > minWidth - 200 || maxY > minHeight - 100) {
    console.log('节点超出边界，调整位置...')
    const offsetX = Math.max(0, maxX - minWidth + 250) // 增加右侧边距
    const offsetY = Math.max(0, maxY - minHeight + 150) // 增加底部边距
    
    // 调整所有节点位置
    evaluators.value.forEach(node => {
      node.x = Math.max(100, node.x - offsetX) // 左侧留100px边距
      node.y = Math.max(100, node.y - offsetY) // 顶部留100px边距
    })
    
    evaluatees.value.forEach(node => {
      node.x = Math.max(100, node.x - offsetX) // 左侧留100px边距
      node.y = Math.max(100, node.y - offsetY) // 顶部留100px边距
    })
    
    console.log('调整后的节点位置:', [...evaluators.value, ...evaluatees.value])
    console.log('调整偏移量:', { offsetX, offsetY })
  }
}

// 方法
const refreshData = async () => {
  await loadData()
}

// 强制调整SVG尺寸以确保完全显示
const forceAdjustSvgSize = () => {
  console.log('🔄 强制调整SVG尺寸...')
  
  // 计算所有节点的边界
  const allNodes = [...evaluators.value, ...evaluatees.value]
  if (allNodes.length === 0) return
  
  const minX = Math.min(...allNodes.map(n => n.x))
  const maxX = Math.max(...allNodes.map(n => n.x))
  const minY = Math.min(...allNodes.map(n => n.y))
  const maxY = Math.max(...allNodes.map(n => n.y))
  
  console.log('节点边界:', { minX, maxX, minY, maxY })
  
  // 计算需要的SVG尺寸，增加更多边距
  const requiredWidth = maxX - minX + 800 // 左右各留400px边距
  const requiredHeight = maxY - minY + 600 // 上下各留300px边距
  
  console.log('需要的SVG尺寸:', { requiredWidth, requiredHeight })
  
  // 如果节点超出边界，强制调整位置
  const maxAllowedX = 3000 - 400 // 右侧留400px边距
  const maxAllowedY = 2200 - 300 // 底部留300px边距
  
  if (maxX > maxAllowedX || maxY > maxAllowedY) {
    console.log('节点超出边界，强制调整位置...')
    
    // 计算调整偏移量
    const offsetX = Math.max(0, maxX - maxAllowedX)
    const offsetY = Math.max(0, maxY - maxAllowedY)
    
    console.log('调整偏移量:', { offsetX, offsetY })
    
    // 调整所有节点位置
    evaluators.value.forEach(node => {
      node.x = Math.max(200, node.x - offsetX) // 左侧留200px边距
      node.y = Math.max(200, node.y - offsetY) // 顶部留200px边距
    })
    
    evaluatees.value.forEach(node => {
      node.x = Math.max(200, node.x - offsetX) // 左侧留200px边距
      node.y = Math.max(200, node.y - offsetY) // 顶部留200px边距
    })
    
    // 更新连接线
    connections.value.forEach(conn => {
      conn.from.x = Math.max(200, conn.from.x - offsetX)
      conn.from.y = Math.max(200, conn.from.y - offsetY)
      conn.to.x = Math.max(200, conn.to.x - offsetX)
      conn.to.y = Math.max(200, conn.to.y - offsetY)
    })
    
    console.log('✅ 节点位置已强制调整，确保完全显示')
    console.log('调整后的节点位置:', [...evaluators.value, ...evaluatees.value])
  }
}

const exportReport = () => {
  ElMessage.success('报告导出功能开发中')
}


const handleConnectionClick = (connection: any) => {
  console.log('连接点击:', connection)
  ElMessage.info(`点击了连接: ${connection.id}`)
}


const viewDetails = (task: any) => {
  console.log('查看详情:', task)
  ElMessage.info(`查看任务详情: ${task.evaluation_code}`)
}

const getRelationText = (relation: string) => {
  const relationMap: Record<string, string> = {
    'superior': '上级评下级',
    'peer': '同级互评',
    'subordinate': '下级评上级'
  }
  return relationMap[relation] || relation
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    'pending': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'overdue': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待考核',
    'in_progress': '进行中',
    'completed': '已完成',
    'overdue': '已过期'
  }
  return statusMap[status] || '未知'
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 监听筛选条件变化
watch([selectedCycle, selectedStatus, selectedDepartment], () => {
  // 当筛选条件变化时，重新处理图形化数据
  if (tasks.value.length > 0) {
    processGraphData()
  }
})

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.evaluation-graph-view {
  min-height: 100vh;
  background: #f8fafc;
  padding: 24px;
}

.page-header {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
  overflow: hidden;
}


.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-subtitle {
  margin: 0;
  font-size: 16px;
  color: #64748b;
}

.header-right {
  display: flex;
  gap: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.evaluator-icon {
  background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
}

.evaluatee-icon {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
}

.task-icon {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
}

.connection-icon {
  background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.controls-panel {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.controls-left {
  display: flex;
  gap: 16px;
  align-items: center;
}

.controls-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.main-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  min-height: 600px;
}

.loading-container {
  height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.graph-view {
  height: 600px;
}

.table-view {
  padding: 24px;
}

.employee-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.employee-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.employee-position {
  font-size: 12px;
  color: #64748b;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .evaluation-graph-view {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-right {
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .controls-panel {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .controls-left {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .controls-right {
    justify-content: center;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-number {
    font-size: 24px;
  }
}
</style>
