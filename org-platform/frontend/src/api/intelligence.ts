/**
 * 智能分析API服务
 */

import request from '@/utils/request'

export interface AnalysisResult {
  category: string
  score: number
  level: string
  description: string
  details: Record<string, any>
  recommendations: string[]
}

export interface OptimizationRecommendation {
  id: string
  priority: 'high' | 'medium' | 'low'
  category: string
  title: string
  description: string
  expected_benefit: string
  implementation_cost: number
  timeframe: string
  impacted_departments: string[]
  metrics: Record<string, any>
}

export interface OrganizationAnalysis {
  overall_score: number
  health_level: string
  analysis_results: AnalysisResult[]
  recommendations: OptimizationRecommendation[]
  metrics: Record<string, any>
  timestamp: string
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
  from_cache?: boolean
}

export const intelligenceApi = {
  /**
   * 获取组织架构智能分析结果
   */
  async getAnalysis(): Promise<ApiResponse<OrganizationAnalysis>> {
    return request.get('/simple-intelligence/analysis/')
  },

  /**
   * 获取组织关键指标
   */
  async getMetrics(): Promise<ApiResponse<Record<string, any>>> {
    return request.get('/intelligence/metrics/')
  },

  /**
   * 刷新分析结果
   */
  async refreshAnalysis(): Promise<ApiResponse<OrganizationAnalysis>> {
    return request.post('/intelligence/refresh/')
  },

  /**
   * 获取特定部门的分析结果
   */
  async getDepartmentAnalysis(departmentId: number): Promise<ApiResponse<any>> {
    return request.get(`/intelligence/departments/${departmentId}/`)
  },

  /**
   * 获取优化建议列表
   */
  async getSuggestions(): Promise<ApiResponse<{
    total_count: number
    by_priority: {
      high: OptimizationRecommendation[]
      medium: OptimizationRecommendation[]
      low: OptimizationRecommendation[]
    }
    summary: {
      high_priority: number
      medium_priority: number
      low_priority: number
    }
  }>> {
    return request.get('/simple-intelligence/suggestions/')
  },

  /**
   * 获取分析历史记录
   */
  async getAnalysisHistory(): Promise<ApiResponse<Array<{
    date: string
    overall_score: number
    health_level: string
    key_changes: string[]
  }>>> {
    return request.get('/intelligence/history/')
  },

  /**
   * 模拟组织变更的影响
   */
  async simulateChanges(changes: Array<{
    type: string
    target: string
    action: string
    parameters: Record<string, any>
  }>): Promise<ApiResponse<{
    current_score: number
    predicted_score: number
    improvement: number
    affected_metrics: Record<string, string>
    risks: string[]
    timeline: string
  }>> {
    return request.post('/intelligence/simulate/', { changes })
  },

  /**
   * 获取行业基准对比
   */
  async getBenchmarkComparison(): Promise<ApiResponse<{
    comparison: Record<string, {
      current: number
      benchmark: number
      difference: number
      status: 'above' | 'below' | 'equal'
    }>
    overall_assessment: string
    industry: string
    company_size: string
  }>> {
    return request.get('/intelligence/benchmark/')
  },

  /**
   * 导出分析报告
   */
  async exportReport(format: 'pdf' | 'excel' = 'pdf'): Promise<Blob> {
    const response = await request.post('/intelligence/export/', { format }, { responseType: 'blob' })
    return response
  },

  /**
   * 获取组织架构图数据
   */
  async getOrganizationChart(): Promise<ApiResponse<{
    nodes: Array<{
      id: string
      name: string
      type: string
      level: number
      employee_count: number
      efficiency_score: number
      parent_id?: string
    }>
    edges: Array<{
      source: string
      target: string
      type: string
    }>
  }>> {
    return request.get('/intelligence/org-chart/')
  },

  /**
   * 获取效率热图数据
   */
  async getEfficiencyHeatmap(): Promise<ApiResponse<{
    departments: Array<{
      id: string
      name: string
      efficiency_score: number
      communication_score: number
      resource_utilization: number
      coordinates: { x: number; y: number }
    }>
    metrics: {
      avg_efficiency: number
      max_efficiency: number
      min_efficiency: number
    }
  }>> {
    return request.get('/intelligence/heatmap/')
  },

  /**
   * 获取智能推荐的组织架构方案
   */
  async getRecommendedStructure(): Promise<ApiResponse<{
    current_structure: any
    recommended_structure: any
    changes: Array<{
      type: 'add' | 'remove' | 'modify' | 'merge'
      target: string
      description: string
      impact: string
    }>
    benefits: {
      efficiency_improvement: number
      cost_reduction: number
      communication_improvement: number
    }
  }>> {
    return request.get('/intelligence/recommended-structure/')
  },

  /**
   * 保存用户反馈
   */
  async saveFeedback(feedback: {
    analysis_id: string
    rating: number
    comments: string
    helpful_suggestions: string[]
    improvement_areas: string[]
  }): Promise<ApiResponse<{ message: string }>> {
    return request.post('/intelligence/feedback/', feedback)
  },

  /**
   * 获取智能分析配置
   */
  async getAnalysisConfig(): Promise<ApiResponse<{
    analysis_weights: Record<string, number>
    thresholds: Record<string, number>
    enabled_features: string[]
    update_frequency: number
  }>> {
    return request.get('/intelligence/config/')
  },

  /**
   * 更新智能分析配置
   */
  async updateAnalysisConfig(config: {
    analysis_weights?: Record<string, number>
    thresholds?: Record<string, number>
    enabled_features?: string[]
    update_frequency?: number
  }): Promise<ApiResponse<{ message: string }>> {
    return request.put('/intelligence/config/', config)
  }
}

export default intelligenceApi
