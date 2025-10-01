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
  getByTaskId: (taskId: number) => api.get(`/tasks/by-task-id/${taskId}/`),
  getEvaluatorTasks: (code: string) => api.get(`/tasks/evaluator-tasks/${code}/`),
  submitScore: (data: any) => api.post('/scores/', data),
  exportEvaluatorCodes: (cycleId: number) => api.get(`/tasks/export-evaluator-codes/?cycle_id=${cycleId}`, { responseType: 'blob' }),
}

// 手动分配API（Manual Assignments）
export const manualAssignmentApi = {
  list: (params?: any) => api.get<ApiResponse<any[]>>('/manual-assignments/', { params }),
  create: (data: any) => api.post<any>('/manual-assignments/', data),
  get: (id: number) => api.get<any>(`/manual-assignments/${id}/`),
  update: (id: number, data: any) => api.put<any>(`/manual-assignments/${id}/`, data),
  delete: (id: number) => api.delete(`/manual-assignments/${id}/`),
  generateTasks: (data: any) => api.post('/manual-assignments/generate-tasks/', data),
}

// 考核评分API
export const scoreApi = {
  list: (params?: any) => api.get<ApiResponse<any[]>>('/scores/', { params }),
  create: (data: any) => api.post<any>('/scores/', data),
  get: (id: number) => api.get<any>(`/scores/${id}/`),
  update: (id: number, data: any) => api.put<any>(`/scores/${id}/`, data),
  delete: (id: number) => api.delete(`/scores/${id}/`),
  submitTaskScores: (data: any) => api.post('/scores/submit_task_scores/', data),
}

// 职级权重API
export const positionWeightApi = {
  list: (params?: any) => api.get<ApiResponse<any[]>>('/position-weights/', { params }),
  create: (data: any) => api.post<any>('/position-weights/', data),
  get: (id: number) => api.get<any>(`/position-weights/${id}/`),
  update: (id: number, data: any) => api.put<any>(`/position-weights/${id}/`, data),
  delete: (id: number) => api.delete(`/position-weights/${id}/`),
  getDefaultWeights: () => api.get('/position-weights/default-weights/'),
  bulkUpdate: (data: any) => api.post('/position-weights/bulk-update/', data),
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

// 考核结果API (别名，用于重构组件)
export const resultsApi = resultApi

// 统计API
export const statsApi = {
  overview: () => api.get<EvaluationStats>('/stats/overview/'),
  cycleStats: (cycleId: number) => api.get(`/stats/cycle/${cycleId}/`),
  listEmployees: () => api.get('/employees/'),
  getEmployeeSkills: (employeeId: number) => api.get(`/employees/${employeeId}/skills/`),
}

// 系统设置API
export const settingsApi = {
  // 系统配置
  config: {
    get: () => api.get('/settings/config/'),
    update: (data: any) => api.put('/settings/config/', data),
  },
  
  // 用户管理
  users: {
    list: (params?: any) => api.get('/settings/users/', { params }),
    create: (data: any) => api.post('/settings/users/', data),
    get: (id: number) => api.get(`/settings/users/${id}/`),
    update: (id: number, data: any) => api.put(`/settings/users/${id}/`, data),
    delete: (id: number) => api.delete(`/settings/users/${id}/`),
    changePassword: (id: number, data: any) => api.post(`/settings/users/${id}/change_password/`, data),
  },
  
  // 角色权限
  roles: {
    list: (params?: any) => api.get('/settings/roles/', { params }),
    create: (data: any) => api.post('/settings/roles/', data),
    get: (id: number) => api.get(`/settings/roles/${id}/`),
    update: (id: number, data: any) => api.put(`/settings/roles/${id}/`, data),
    delete: (id: number) => api.delete(`/settings/roles/${id}/`),
    permissions: (id: number) => api.get(`/settings/roles/${id}/permissions/`),
    updatePermissions: (id: number, data: any) => api.put(`/settings/roles/${id}/permissions/`, data),
  },
  
  // 系统日志
  logs: {
    list: (params?: any) => api.get('/settings/logs/', { params }),
    get: (id: number) => api.get(`/settings/logs/${id}/`),
    export: (params?: any) => api.get('/settings/logs/export/', { 
      params,
      responseType: 'blob'
    }),
  },
  
  // 数据备份
  backup: {
    list: () => api.get('/settings/backup/'),
    create: () => api.post('/settings/backup/'),
    restore: (id: number) => api.post(`/settings/backup/${id}/restore/`),
    delete: (id: number) => api.delete(`/settings/backup/${id}/`),
  },
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
    fullTree: () => orgApi.get<OrgDepartment[]>('/departments/full_tree/'),
    get: (id: number) => orgApi.get<OrgDepartment>(`/departments/${id}/`),
  },
}

// 多维度评估API
export const multidimensionalApi = {
  // 评估维度
  dimensions: {
    list: (params?: any) => api.get('/multidimensional/dimensions/', { params }),
    get: (id: number) => api.get(`/multidimensional/dimensions/${id}/`),
    create: (data: any) => api.post('/multidimensional/dimensions/', data),
    update: (id: number, data: any) => api.put(`/multidimensional/dimensions/${id}/`, data),
    delete: (id: number) => api.delete(`/multidimensional/dimensions/${id}/`),
    active: () => api.get('/multidimensional/dimensions/active/'),
    indicators: (id: number) => api.get(`/multidimensional/dimensions/${id}/indicators/`),
    batchUpdateWeights: (data: any) => api.post('/multidimensional/dimensions/batch_update_weights/', data),
  },
  
  // 评估方法
  methods: {
    list: (params?: any) => api.get('/multidimensional/methods/', { params }),
    get: (id: number) => api.get(`/multidimensional/methods/${id}/`),
    create: (data: any) => api.post('/multidimensional/methods/', data),
    update: (id: number, data: any) => api.put(`/multidimensional/methods/${id}/`, data),
    delete: (id: number) => api.delete(`/multidimensional/methods/${id}/`),
    active: () => api.get('/multidimensional/methods/active/'),
    templates: (id: number) => api.get(`/multidimensional/methods/${id}/templates/`),
  },
  
  // 评估周期类型
  cycleTypes: {
    list: (params?: any) => api.get('/multidimensional/cycle-types/', { params }),
    get: (id: number) => api.get(`/multidimensional/cycle-types/${id}/`),
    create: (data: any) => api.post('/multidimensional/cycle-types/', data),
    update: (id: number, data: any) => api.put(`/multidimensional/cycle-types/${id}/`, data),
    delete: (id: number) => api.delete(`/multidimensional/cycle-types/${id}/`),
    active: () => api.get('/multidimensional/cycle-types/active/'),
  },
  
  // 多维度评估
  evaluations: {
    list: (params?: any) => api.get('/multidimensional/evaluations/', { params }),
    get: (id: number) => api.get(`/multidimensional/evaluations/${id}/`),
    create: (data: any) => api.post('/multidimensional/evaluations/', data),
    update: (id: number, data: any) => api.put(`/multidimensional/evaluations/${id}/`, data),
    delete: (id: number) => api.delete(`/multidimensional/evaluations/${id}/`),
    myEvaluations: (params?: any) => api.get('/multidimensional/evaluations/my_evaluations/', { params }),
    myEvaluated: (params?: any) => api.get('/multidimensional/evaluations/my_evaluated/', { params }),
    submit: (id: number) => api.post(`/multidimensional/evaluations/${id}/submit/`),
    review: (id: number) => api.post(`/multidimensional/evaluations/${id}/review/`),
    finalize: (id: number) => api.post(`/multidimensional/evaluations/${id}/finalize/`),
    statistics: (params?: any) => api.get('/multidimensional/evaluations/statistics/', { params }),
  },
  
  // 评估指标
  indicators: {
    list: (params?: any) => api.get('/multidimensional/indicators/', { params }),
    get: (id: number) => api.get(`/multidimensional/indicators/${id}/`),
    create: (data: any) => api.post('/multidimensional/indicators/', data),
    update: (id: number, data: any) => api.put(`/multidimensional/indicators/${id}/`, data),
    delete: (id: number) => api.delete(`/multidimensional/indicators/${id}/`),
    byDimension: (dimensionId: number) => api.get(`/multidimensional/indicators/by_dimension/?dimension_id=${dimensionId}`),
  },
  
  // 评估模板
  templates: {
    list: (params?: any) => api.get('/multidimensional/templates/', { params }),
    get: (id: number) => api.get(`/multidimensional/templates/${id}/`),
    create: (data: any) => api.post('/multidimensional/templates/', data),
    update: (id: number, data: any) => api.put(`/multidimensional/templates/${id}/`, data),
    delete: (id: number) => api.delete(`/multidimensional/templates/${id}/`),
    active: () => api.get('/multidimensional/templates/active/'),
    default: () => api.get('/multidimensional/templates/default/'),
    copy: (id: number) => api.post(`/multidimensional/templates/${id}/copy/`),
  },
}

export default api