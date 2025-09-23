// 用户类型
export interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
}

// 部门类型
export interface Department {
  id: number
  name: string
  code: string
  parent: number | null
  parent_name?: string
  level: number
  sort_order: number
  description: string
  manager: number | null
  manager_name?: string
  full_path?: string
  employee_count?: number
  is_active: boolean
  children?: Department[]
  created_at: string
  updated_at: string
}

// 职位类型
export interface Position {
  id: number
  name: string
  code: string
  department: number
  department_name?: string
  management_level: 'senior' | 'middle' | 'junior'
  level: number
  level_display?: string
  level_display_with_management?: string
  description: string
  requirements: string
  responsibilities: string
  employee_count?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

// 员工类型
export interface Employee {
  id: number
  user: number
  user_info?: User
  employee_id: string
  name: string
  gender: 'M' | 'F'
  birth_date: string | null
  phone: string
  email: string
  address: string
  department: number
  department_name?: string
  position: number
  position_name?: string
  position_level_display?: string
  supervisor: number | null
  supervisor_name?: string
  subordinate_count?: number
  hire_date: string
  status: 'active' | 'leave' | 'resigned' | 'retired'
  avatar: string
  subordinates?: Employee[]
  created_at: string
  updated_at: string
}

// 组织架构统计类型
export interface OrganizationStats {
  total_departments: number
  active_departments: number
  total_positions: number
  active_positions: number
  total_employees: number
  active_employees: number
  department_levels: Array<{ level: number; count: number }>
  position_levels: Array<{ level: number; count: number }>
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