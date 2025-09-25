import axios from 'axios'
import type { 
  ApiResponse, 
  EvaluationCycle, 
  EvaluationIndicator,
  EvaluationRule,
  Employee, 
  EvaluationTask, 
  EvaluationScore, 
  EvaluationResult,
  OrgEmployee,
  OrgDepartment,
  EvaluationStats
} from '@/types'

// 创建绩效考核系统API实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 创建组织架构中台API实例
const orgApi = axios.create({
  baseURL: '/org-api',
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

orgApi.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Org API Error:', error)
    return Promise.reject(error)
  }
)

// 考核周期API
export const cycleApi = {
  list: (params?: any) => api.get<ApiResponse<EvaluationCycle[]>>('/cycles/', { params }),
  create: (data: Partial<EvaluationCycle>) => api.post<EvaluationCycle>('/cycles/', data),
  get: (id: number) => api.get<EvaluationCycle>(`/cycles/${id}/`),
  update: (id: number, data: Partial<EvaluationCycle>) => api.put<EvaluationCycle>(`/cycles/${id}/`, data),
  delete: (id: number) => api.delete(`/cycles/${id}/`),
  generateTasks: (id: number) => api.post(`/cycles/${id}/generate_tasks/`),
}

// 考核指标API
export const indicatorApi = {
  list: (params?: any) => api.get<ApiResponse<EvaluationIndicator[]>>('/indicators/', { params }),
  create: (data: Partial<EvaluationIndicator>) => api.post<EvaluationIndicator>('/indicators/', data),
  get: (id: number) => api.get<EvaluationIndicator>(`/indicators/${id}/`),
  update: (id: number, data: Partial<EvaluationIndicator>) => api.put<EvaluationIndicator>(`/indicators/${id}/`, data),
  delete: (id: number) => api.delete(`/indicators/${id}/`),
}

// 考核规则API
export const ruleApi = {
  list: (params?: any) => api.get<ApiResponse<EvaluationRule[]>>('/rules/', { params }),
  create: (data: Partial<EvaluationRule>) => api.post<EvaluationRule>('/rules/', data),
  get: (id: number) => api.get<EvaluationRule>(`/rules/${id}/`),
  update: (id: number, data: Partial<EvaluationRule>) => api.put<EvaluationRule>(`/rules/${id}/`, data),
  delete: (id: number) => api.delete(`/rules/${id}/`),
  createDefaults: () => api.post('/rules/create_defaults/'),
}

// 员工API（本地）
export const employeeApi = {
  list: (params?: any) => api.get<ApiResponse<Employee[]>>('/employees/', { params }),
  sync: () => api.post('/employees/sync/'),
  get: (id: number) => api.get<Employee>(`/employees/${id}/`),
}

// 考核任务API
export const taskApi = {
  list: (params?: any) => api.get<ApiResponse<EvaluationTask[]>>('/tasks/', { params }),
  create: (data: Partial<EvaluationTask>) => api.post<EvaluationTask>('/tasks/', data),
  get: (id: number) => api.get<EvaluationTask>(`/tasks/${id}/`),
  update: (id: number, data: Partial<EvaluationTask>) => api.put<EvaluationTask>(`/tasks/${id}/`, data),
  delete: (id: number) => api.delete(`/tasks/${id}/`),
  generateForCycle: (cycleId: number) => api.post(`/tasks/generate-for-cycle/`, { cycle_id: cycleId }),
  getByCode: (code: string) => api.get(`/tasks/by-code/${code}/`),
}

// 手动分配API（Manual Assignments）
export const manualAssignmentApi = {
  list: (params?: any) => api.get<ApiResponse<any[]>>('/manual-assignments/', { params }),
  create: (data: any) => api.post<any>('/manual-assignments/', data),
  get: (id: number) => api.get<any>(`/manual-assignments/${id}/`),
  update: (id: number, data: any) => api.put<any>(`/manual-assignments/${id}/`, data),
  delete: (id: number) => api.delete(`/manual-assignments/${id}/`),
}

// 考核结果API
export const resultApi = {
  list: (params?: any) => api.get<ApiResponse<EvaluationResult[]>>('/results/', { params }),
  get: (id: number) => api.get<EvaluationResult>(`/results/${id}/`),
  calculateCycleResults: (cycleId: number) => api.post(`/results/calculate_cycle_results/`, { cycle_id: cycleId }),
  export: (cycleId: number) => api.get(`/results/export/`, { 
    params: { cycle_id: cycleId },
    responseType: 'blob'
  }),
}

// 统计API
export const statsApi = {
  overview: () => api.get<EvaluationStats>('/stats/overview/'),
  cycleStats: (cycleId: number) => api.get(`/stats/cycle/${cycleId}/`),
}

// 组织架构中台API
export const orgPlatformApi = {
  // 员工相关
  employees: {
    list: (params?: any) => orgApi.get<ApiResponse<OrgEmployee[]>>('/employees/', { params }),
    get: (id: number) => orgApi.get<OrgEmployee>(`/employees/${id}/`),
    orgTree: () => orgApi.get<OrgEmployee[]>('/employees/org_tree/'),
  },
  
  // 部门相关
  departments: {
    list: (params?: any) => orgApi.get<ApiResponse<OrgDepartment[]>>('/departments/', { params }),
    tree: () => orgApi.get<OrgDepartment[]>('/departments/tree/'),
    get: (id: number) => orgApi.get<OrgDepartment>(`/departments/${id}/`),
  },
}

export default api