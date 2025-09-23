import axios from 'axios'
import type { ApiResponse, Department, Position, Employee, OrganizationStats } from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 部门API
export const departmentApi = {
  // 获取部门列表
  list: (params?: any) => api.get<ApiResponse<Department[]>>('/departments/', { params }),
  
  // 获取部门树
  tree: () => api.get<Department[]>('/departments/tree/'),
  
  // 创建部门
  create: (data: Partial<Department>) => api.post<Department>('/departments/', data),
  
  // 获取部门详情
  get: (id: number) => api.get<Department>(`/departments/${id}/`),
  
  // 更新部门
  update: (id: number, data: Partial<Department>) => 
    api.put<Department>(`/departments/${id}/`, data),
  
  // 删除部门
  delete: (id: number) => api.delete(`/departments/${id}/`),
  
  // 获取部门员工
  employees: (id: number) => api.get<Employee[]>(`/departments/${id}/employees/`),
}

// 职位API
export const positionApi = {
  // 获取职位列表
  list: (params?: any) => api.get<ApiResponse<Position[]>>('/positions/', { params }),
  
  // 创建职位
  create: (data: Partial<Position>) => api.post<Position>('/positions/', data),
  
  // 获取职位详情
  get: (id: number) => api.get<Position>(`/positions/${id}/`),
  
  // 更新职位
  update: (id: number, data: Partial<Position>) => 
    api.put<Position>(`/positions/${id}/`, data),
  
  // 删除职位
  delete: (id: number) => api.delete(`/positions/${id}/`),
  
  // 获取职位员工
  employees: (id: number) => api.get<Employee[]>(`/positions/${id}/employees/`),
}

// 员工API
export const employeeApi = {
  // 获取员工列表
  list: (params?: any) => api.get<ApiResponse<Employee[]>>('/employees/', { params }),
  
  // 获取组织架构树
  orgTree: () => api.get<Employee[]>('/employees/org_tree/'),
  
  // 创建员工
  create: (data: Partial<Employee>) => api.post<Employee>('/employees/', data),
  
  // 获取员工详情
  get: (id: number) => api.get<Employee>(`/employees/${id}/`),
  
  // 更新员工
  update: (id: number, data: Partial<Employee>) => 
    api.put<Employee>(`/employees/${id}/`, data),
  
  // 删除员工
  delete: (id: number) => api.delete(`/employees/${id}/`),
  
  // 获取员工下属
  subordinates: (id: number) => api.get<Employee[]>(`/employees/${id}/subordinates/`),
}

// 统计API
export const statsApi = {
  // 获取组织架构统计
  overview: () => api.get<OrganizationStats>('/stats/overview/'),
}

export default api