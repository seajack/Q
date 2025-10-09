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
      console.log('获取部门列表响应:', response)
      
      // 检查响应数据结构
      if (response && response.results) {
        departments.value = response.results
      } else if (Array.isArray(response)) {
        departments.value = response
      } else {
        console.error('部门列表响应数据无效:', response)
        throw new Error('获取部门列表失败')
      }
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
      departmentTree.value = response
    } catch (error) {
      console.error('获取部门树失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchFullOrganizationTree = async () => {
    try {
      loading.value = true
      const response = await departmentApi.fullTree()
      return response
    } catch (error) {
      console.error('获取完整组织架构树失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createDepartment = async (data: Partial<Department>) => {
    try {
      const response = await departmentApi.create(data)
      console.log('创建部门响应:', response)
      
      // 检查响应数据
      if (!response || !response.id) {
        console.error('响应数据无效:', response)
        throw new Error('创建部门响应数据无效')
      }
      
      departments.value.push(response)
      return response
    } catch (error) {
      console.error('创建部门失败:', error)
      throw error
    }
  }

  const updateDepartment = async (id: number, data: Partial<Department>) => {
    try {
      console.log('开始更新部门:', { id, data })
      
      const response = await departmentApi.update(id, data)
      console.log('更新部门响应:', response)
      console.log('响应类型:', typeof response)
      console.log('响应是否为null:', response === null)
      console.log('响应是否为undefined:', response === undefined)
      
      // 处理可能的响应格式问题
      let departmentData = response
      
      // 如果响应是包装格式，提取实际数据
      if (response && typeof response === 'object' && 'data' in response) {
        departmentData = response.data
        console.log('提取的部门数据:', departmentData)
      }
      
      // 如果API调用失败或返回无效数据，尝试重新获取数据
      if (!departmentData || !departmentData.id) {
        console.warn('API响应无效，尝试重新获取部门数据')
        try {
          const freshData = await departmentApi.get(id)
          console.log('重新获取的部门数据:', freshData)
          departmentData = freshData
        } catch (getError) {
          console.error('重新获取部门数据失败:', getError)
          throw new Error('无法获取有效的部门数据')
        }
      }
      
      // 最终检查
      if (!departmentData || !departmentData.id) {
        console.error('最终响应数据无效:', departmentData)
        throw new Error('无法获取有效的部门数据')
      }
      
      const index = departments.value.findIndex(dept => dept.id === id)
      if (index !== -1) {
        departments.value[index] = departmentData
      }
      return departmentData
    } catch (error) {
      console.error('更新部门失败:', error)
      console.error('错误详情:', {
        message: error.message,
        stack: error.stack,
        name: error.name
      })
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
      positions.value = response.results
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
      employees.value = response.results
    } catch (error) {
      console.error('获取员工列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createEmployee = async (data: Partial<Employee>) => {
    try {
      console.log('开始创建员工:', data)
      
      const response = await employeeApi.create(data)
      console.log('创建员工响应:', response)
      
      // 检查响应数据
      if (!response || !response.id) {
        console.error('创建员工响应数据无效:', response)
        throw new Error('创建员工响应数据无效')
      }
      
      employees.value.push(response)
      return response
    } catch (error) {
      console.error('创建员工失败:', error)
      throw error
    }
  }

  const updateEmployee = async (id: number, data: Partial<Employee>) => {
    try {
      console.log('开始更新员工:', { id, data })
      
      const response = await employeeApi.update(id, data)
      console.log('更新员工响应:', response)
      
      // 检查响应数据
      if (!response || !response.id) {
        console.error('更新员工响应数据无效:', response)
        throw new Error('更新员工响应数据无效')
      }
      
      const index = employees.value.findIndex(emp => emp.id === id)
      if (index !== -1) {
        employees.value[index] = response
      }
      return response
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
      stats.value = response
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
    fetchFullOrganizationTree,
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