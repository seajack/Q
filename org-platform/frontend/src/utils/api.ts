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
  
  // 获取完整组织架构树（包含员工）
  fullTree: () => api.get('/departments/full_tree/'),
  
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
  
  // 下载模板
  downloadTemplate: () => api.get('/departments-template/', { responseType: 'blob' }),
  
  // 导入部门
  import: (formData: FormData) => api.post('/departments-import/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
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

// 系统配置API
export const configApi = {
  // 获取配置列表
  getConfigs: (params?: any) => api.get('/configs/', { params }),
  
  // 创建配置
  createConfig: (data: any) => api.post('/configs/', data),
  
  // 更新配置
  updateConfig: (id: number, data: any) => api.put(`/configs/${id}/`, data),
  
  // 删除配置
  deleteConfig: (id: number) => api.delete(`/configs/${id}/`),
  
  // 按分类获取配置
  getByCategory: (category: string) => api.get(`/configs/by_category/?category=${category}`),
  
  // 批量更新配置
  bulkUpdate: (data: any) => api.post('/configs/bulk_update/', data),
  
  // 导出配置
  exportConfigs: () => api.get('/configs/export/'),
  
  // 导入配置
  importConfigs: (data: any) => api.post('/configs/import_configs/', data),
}

// 数据字典API
export const dictionaryApi = {
  // 获取字典列表
  getDictionaries: (params?: any) => api.get('/dictionaries/', { params }),
  
  // 创建字典项
  createDictionary: (data: any) => api.post('/dictionaries/', data),
  
  // 更新字典项
  updateDictionary: (id: number, data: any) => api.put(`/dictionaries/${id}/`, data),
  
  // 删除字典项
  deleteDictionary: (id: number) => api.delete(`/dictionaries/${id}/`),
  
  // 按分类获取字典
  getByCategory: (category: string) => api.get(`/dictionaries/by_category/?category=${category}`),
  
  // 获取树形结构
  getTree: (category: string) => api.get(`/dictionaries/tree/?category=${category}`),
}

// 职位模板API
export const templateApi = {
  // 获取模板列表
  getTemplates: (params?: any) => api.get('/position-templates/', { params }),
  
  // 创建模板
  createTemplate: (data: any) => api.post('/position-templates/', data),
  
  // 更新模板
  updateTemplate: (id: number, data: any) => api.put(`/position-templates/${id}/`, data),
  
  // 删除模板
  deleteTemplate: (id: number) => api.delete(`/position-templates/${id}/`),
  
  // 基于模板创建职位
  createPositionFromTemplate: (templateId: number, data: any) => 
    api.post(`/position-templates/${templateId}/create_position/`, data),
}

// 工作流规则API
export const workflowApi = {
  // 获取规则列表
  getRules: (params?: any) => api.get('/workflow-rules/', { params }),
  
  // 创建规则
  createRule: (data: any) => api.post('/workflow-rules/', data),
  
  // 更新规则
  updateRule: (id: number, data: any) => api.put(`/workflow-rules/${id}/`, data),
  
  // 删除规则
  deleteRule: (id: number) => api.delete(`/workflow-rules/${id}/`),
}

export default api