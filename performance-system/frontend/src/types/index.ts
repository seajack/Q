// 考核周期类型
export interface EvaluationCycle {
  id: number
  name: string
  description: string
  start_date: string
  end_date: string
  status: 'draft' | 'active' | 'completed' | 'cancelled'
  created_by: number
  created_at: string
  updated_at: string
}

// 考核指标类型
export interface EvaluationIndicator {
  id: number
  name: string
  category: 'performance' | 'ability' | 'attitude' | 'teamwork' | 'innovation'
  description: string
  weight: number | string  // 支持数字和字符串类型
  max_score: number | string  // 支持数字和字符串类型
  is_active: boolean
  created_at: string
  updated_at: string
}

// 考核规则类型
export interface EvaluationRule {
  id: number
  name: string
  description: string
  relation_types: string[]
  evaluation_scope: 'department' | 'unit' | 'company' | 'cross_department' | 'cross_unit' | 'manual'
  max_evaluators_per_relation: number
  min_evaluators_per_relation: number
  relation_weights: Record<string, number>
  allow_cross_department: boolean
  allow_cross_unit: boolean
  allow_self_evaluation: boolean
  position_level_diff_limit: number
  custom_rules: Record<string, any>
  is_active: boolean
  created_at: string
  updated_at: string
}

// 员工类型（从中台同步）
export interface Employee {
  id: number
  employee_id: string
  name: string
  department_id: number
  department_name: string
  position_id: number
  position_name: string
  position_level: number
  supervisor_id?: number
  email: string
  phone: string
  is_active: boolean
  last_sync: string
}

// 考核任务类型
export interface EvaluationTask {
  id: number
  cycle: number
  evaluator: number
  evaluatee: number
  evaluator_name?: string
  evaluatee_name?: string
  evaluator_position?: string
  evaluatee_position?: string
  evaluator_position_level?: number
  evaluatee_position_level?: number
  relation_type: 'superior' | 'peer' | 'subordinate'
  evaluation_code: string
  weight: number
  status: 'pending' | 'in_progress' | 'completed' | 'overdue'
  assigned_at: string
  completed_at?: string
}

// 考核评分类型
export interface EvaluationScore {
  id: number
  task: number
  indicator: number
  indicator_name?: string
  score: number
  comment: string
  created_at: string
  updated_at: string
}

// 考核结果类型
export interface EvaluationResult {
  id: number
  cycle: number
  employee: number
  employee_name?: string
  department_name?: string
  position_name?: string
  total_score: number
  weighted_score: number
  superior_score?: number
  peer_score?: number
  subordinate_score?: number
  rank?: number
  is_final: boolean
  calculated_at: string
}

// 组织架构API响应类型
export interface OrgEmployee {
  id: number
  employee_id: string
  name: string
  department: number
  department_name: string
  position: number
  position_name: string
  supervisor?: number
  supervisor_name?: string
  status: string
  phone: string
  email: string
}

export interface OrgDepartment {
  id: number
  name: string
  code: string
  parent?: number
  level: number
  manager?: number
  manager_name?: string
  employee_count: number
  children?: OrgDepartment[]
}

// API响应类型
export interface ApiResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T
}

// 表格查询参数
export interface TableQuery {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
  [key: string]: any
}

// 考核统计类型
export interface EvaluationStats {
  total_cycles: number
  active_cycles: number
  total_tasks: number
  completed_tasks: number
  completion_rate: number
  average_score: number
  department_stats: Array<{
    department_name: string
    employee_count: number
    completion_rate: number
    average_score: number
  }>
}