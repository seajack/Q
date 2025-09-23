import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  EvaluationCycle, 
  EvaluationIndicator, 
  Employee, 
  EvaluationTask, 
  EvaluationResult,
  EvaluationStats,
  OrgEmployee,
  OrgDepartment
} from '@/types'
import { 
  cycleApi, 
  indicatorApi, 
  employeeApi, 
  taskApi, 
  resultApi, 
  statsApi,
  orgPlatformApi 
} from '@/utils/api'

export const useEvaluationStore = defineStore('evaluation', () => {
  // 状态
  const cycles = ref<EvaluationCycle[]>([])
  const indicators = ref<EvaluationIndicator[]>([])
  const employees = ref<Employee[]>([])
  const tasks = ref<EvaluationTask[]>([])
  const results = ref<EvaluationResult[]>([])
  const stats = ref<EvaluationStats | null>(null)
  const loading = ref(false)

  // 组织架构数据
  const orgEmployees = ref<OrgEmployee[]>([])
  const orgDepartments = ref<OrgDepartment[]>([])
  const orgDepartmentTree = ref<OrgDepartment[]>([])

  // 计算属性
  const activeCycles = computed(() => 
    cycles.value.filter(cycle => cycle.status === 'active')
  )
  
  const activeIndicators = computed(() => 
    indicators.value.filter(indicator => indicator.is_active)
  )
  
  const activeEmployees = computed(() => 
    employees.value.filter(emp => emp.is_active)
  )

  // 考核周期相关方法
  const fetchCycles = async (params?: any) => {
    try {
      loading.value = true
      const response = await cycleApi.list(params)
      cycles.value = response.data.results
    } catch (error) {
      console.error('获取考核周期失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createCycle = async (data: Partial<EvaluationCycle>) => {
    try {
      const response = await cycleApi.create(data)
      cycles.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('创建考核周期失败:', error)
      throw error
    }
  }

  const updateCycle = async (id: number, data: Partial<EvaluationCycle>) => {
    try {
      const response = await cycleApi.update(id, data)
      const index = cycles.value.findIndex(cycle => cycle.id === id)
      if (index !== -1) {
        cycles.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新考核周期失败:', error)
      throw error
    }
  }

  const deleteCycle = async (id: number) => {
    try {
      await cycleApi.delete(id)
      const index = cycles.value.findIndex(cycle => cycle.id === id)
      if (index !== -1) {
        cycles.value.splice(index, 1)
      }
    } catch (error) {
      console.error('删除考核周期失败:', error)
      throw error
    }
  }

  // 考核指标相关方法
  const fetchIndicators = async (params?: any) => {
    try {
      loading.value = true
      const response = await indicatorApi.list(params)
      indicators.value = response.data.results
    } catch (error) {
      console.error('获取考核指标失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createIndicator = async (data: Partial<EvaluationIndicator>) => {
    try {
      const response = await indicatorApi.create(data)
      indicators.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('创建考核指标失败:', error)
      throw error
    }
  }

  // 员工相关方法
  const fetchEmployees = async (params?: any) => {
    try {
      loading.value = true
      const response = await employeeApi.list(params)
      employees.value = response.data.results
    } catch (error) {
      console.error('获取员工列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const syncEmployees = async () => {
    try {
      loading.value = true
      await employeeApi.sync()
      await fetchEmployees() // 重新获取同步后的数据
    } catch (error) {
      console.error('同步员工数据失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 组织架构相关方法
  const fetchOrgEmployees = async (params?: any) => {
    try {
      const response = await orgPlatformApi.employees.list(params)
      orgEmployees.value = response.data.results
    } catch (error) {
      console.error('获取组织架构员工数据失败:', error)
      throw error
    }
  }

  const fetchOrgDepartmentTree = async () => {
    try {
      const response = await orgPlatformApi.departments.tree()
      orgDepartmentTree.value = response.data
    } catch (error) {
      console.error('获取组织架构部门树失败:', error)
      throw error
    }
  }

  // 考核任务相关方法
  const fetchTasks = async (params?: any) => {
    try {
      loading.value = true
      const response = await taskApi.list(params)
      tasks.value = response.data.results
    } catch (error) {
      console.error('获取考核任务失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const generateTasksForCycle = async (cycleId: number) => {
    try {
      loading.value = true
      await taskApi.generateForCycle(cycleId)
      await fetchTasks({ cycle: cycleId }) // 重新获取任务
    } catch (error) {
      console.error('生成考核任务失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const getTaskByCode = async (code: string) => {
    try {
      const response = await taskApi.getByCode(code)
      return response.data
    } catch (error) {
      console.error('根据考核码获取任务失败:', error)
      throw error
    }
  }

  // 考核结果相关方法
  const fetchResults = async (params?: any) => {
    try {
      loading.value = true
      const response = await resultApi.list(params)
      results.value = response.data.results
    } catch (error) {
      console.error('获取考核结果失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const calculateResults = async (cycleId: number) => {
    try {
      loading.value = true
      await resultApi.calculate(cycleId)
      await fetchResults({ cycle: cycleId }) // 重新获取结果
    } catch (error) {
      console.error('计算考核结果失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 统计相关方法
  const fetchStats = async () => {
    try {
      const response = await statsApi.overview()
      stats.value = response.data
    } catch (error) {
      console.error('获取统计信息失败:', error)
      throw error
    }
  }

  return {
    // 状态
    cycles,
    indicators,
    employees,
    tasks,
    results,
    stats,
    loading,
    orgEmployees,
    orgDepartments,
    orgDepartmentTree,
    
    // 计算属性
    activeCycles,
    activeIndicators,
    activeEmployees,
    
    // 方法
    fetchCycles,
    createCycle,
    updateCycle,
    deleteCycle,
    
    fetchIndicators,
    createIndicator,
    
    fetchEmployees,
    syncEmployees,
    
    fetchOrgEmployees,
    fetchOrgDepartmentTree,
    
    fetchTasks,
    generateTasksForCycle,
    getTaskByCode,
    
    fetchResults,
    calculateResults,
    
    fetchStats
  }
})