import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Department, Position, Employee, OrganizationStats } from '@/types'
import { departmentApi, positionApi, employeeApi, statsApi } from '@/utils/api'

export const useOrganizationStore = defineStore('organization', () => {
  // 状态
  const departments = ref<Department[]>([])
  const departmentTree = ref<Department[]>([])
  const positions = ref<Position[]>([])
  const employees = ref<Employee[]>([])
  const stats = ref<OrganizationStats | null>(null)
  const loading = ref(false)

  // 计算属性
  const activeDepartments = computed(() => 
    departments.value.filter(dept => dept.is_active)
  )
  
  const activePositions = computed(() => 
    positions.value.filter(pos => pos.is_active)
  )
  
  const activeEmployees = computed(() => 
    employees.value.filter(emp => emp.status === 'active')
  )

  // 部门相关方法
  const fetchDepartments = async (params?: any) => {
    try {
      loading.value = true
      const response = await departmentApi.list(params)
      departments.value = response.data.results
    } catch (error) {
      console.error('获取部门列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchDepartmentTree = async () => {
    try {
      loading.value = true
      const response = await departmentApi.tree()
      departmentTree.value = response.data
    } catch (error) {
      console.error('获取部门树失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createDepartment = async (data: Partial<Department>) => {
    try {
      const response = await departmentApi.create(data)
      departments.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('创建部门失败:', error)
      throw error
    }
  }

  const updateDepartment = async (id: number, data: Partial<Department>) => {
    try {
      const response = await departmentApi.update(id, data)
      const index = departments.value.findIndex(dept => dept.id === id)
      if (index !== -1) {
        departments.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新部门失败:', error)
      throw error
    }
  }

  const deleteDepartment = async (id: number) => {
    try {
      await departmentApi.delete(id)
      const index = departments.value.findIndex(dept => dept.id === id)
      if (index !== -1) {
        departments.value.splice(index, 1)
      }
    } catch (error) {
      console.error('删除部门失败:', error)
      throw error
    }
  }

  // 职位相关方法
  const fetchPositions = async (params?: any) => {
    try {
      loading.value = true
      const response = await positionApi.list(params)
      positions.value = response.data.results
    } catch (error) {
      console.error('获取职位列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createPosition = async (data: Partial<Position>) => {
    try {
      const response = await positionApi.create(data)
      positions.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('创建职位失败:', error)
      throw error
    }
  }

  const updatePosition = async (id: number, data: Partial<Position>) => {
    try {
      const response = await positionApi.update(id, data)
      const index = positions.value.findIndex(pos => pos.id === id)
      if (index !== -1) {
        positions.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新职位失败:', error)
      throw error
    }
  }

  const deletePosition = async (id: number) => {
    try {
      await positionApi.delete(id)
      const index = positions.value.findIndex(pos => pos.id === id)
      if (index !== -1) {
        positions.value.splice(index, 1)
      }
    } catch (error) {
      console.error('删除职位失败:', error)
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

  const createEmployee = async (data: Partial<Employee>) => {
    try {
      const response = await employeeApi.create(data)
      employees.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('创建员工失败:', error)
      throw error
    }
  }

  const updateEmployee = async (id: number, data: Partial<Employee>) => {
    try {
      const response = await employeeApi.update(id, data)
      const index = employees.value.findIndex(emp => emp.id === id)
      if (index !== -1) {
        employees.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新员工失败:', error)
      throw error
    }
  }

  const deleteEmployee = async (id: number) => {
    try {
      await employeeApi.delete(id)
      const index = employees.value.findIndex(emp => emp.id === id)
      if (index !== -1) {
        employees.value.splice(index, 1)
      }
    } catch (error) {
      console.error('删除员工失败:', error)
      throw error
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
    departments,
    departmentTree,
    positions,
    employees,
    stats,
    loading,
    
    // 计算属性
    activeDepartments,
    activePositions,
    activeEmployees,
    
    // 方法
    fetchDepartments,
    fetchDepartmentTree,
    createDepartment,
    updateDepartment,
    deleteDepartment,
    
    fetchPositions,
    createPosition,
    updatePosition,
    deletePosition,
    
    fetchEmployees,
    createEmployee,
    updateEmployee,
    deleteEmployee,
    
    fetchStats
  }
})