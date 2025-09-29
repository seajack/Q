/**
 * 工作流设计器API服务
 */

import request from '@/utils/request'

export interface WorkflowNode {
  node_id: string
  node_type: string
  name: string
  x: number
  y: number
  config: Record<string, any>
}

export interface WorkflowConnection {
  connection_id: string
  source_id: string
  target_id: string
  source_port?: string
  target_port?: string
  connection_type?: string
  label?: string
}

export interface WorkflowDesign {
  id: string
  name: string
  description: string
  category?: string
  nodes: WorkflowNode[]
  connections: WorkflowConnection[]
  canvas_config: Record<string, any>
  status: string
  current_version: string
  created_by: string
  created_by_name: string
  created_at: string
  updated_at: string
  execution_count: number
  success_rate: number
  node_count: number
  connection_count: number
}

export interface WorkflowVersion {
  id: string
  workflow: string
  workflow_name: string
  version_name: string
  description: string
  nodes_snapshot: WorkflowNode[]
  connections_snapshot: WorkflowConnection[]
  canvas_snapshot: Record<string, any>
  changes: Array<{
    id: string
    type: 'add' | 'remove' | 'modify'
    description: string
  }>
  tags: string[]
  created_by: string
  created_by_name: string
  created_at: string
  is_current: boolean
}

export interface WorkflowExecution {
  id: string
  workflow: string
  workflow_name: string
  version?: string
  version_name?: string
  execution_id: string
  status: string
  input_data: Record<string, any>
  output_data: Record<string, any>
  execution_logs: Array<{
    timestamp: string
    level: string
    message: string
    node_id?: string
  }>
  error_message?: string
  started_at: string
  completed_at?: string
  duration?: number
  current_node?: string
  execution_context: Record<string, any>
}

export interface WorkflowTemplate {
  id: string
  name: string
  description: string
  category: string
  nodes: WorkflowNode[]
  connections: WorkflowConnection[]
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export const workflowApi = {
  /**
   * 获取工作流列表
   */
  async getWorkflows(): Promise<ApiResponse<WorkflowDesign[]>> {
    return request({
      url: '/api/workflow-designs/',
      method: 'get'
    })
  },

  /**
   * 获取工作流详情
   */
  async getWorkflow(id: string): Promise<ApiResponse<WorkflowDesign>> {
    return request({
      url: `/api/workflow-designs/${id}/`,
      method: 'get'
    })
  },

  /**
   * 创建工作流
   */
  async createWorkflow(data: {
    name: string
    description: string
    category?: string
  }): Promise<ApiResponse<WorkflowDesign>> {
    return request({
      url: '/api/workflow-designs/',
      method: 'post',
      data
    })
  },

  /**
   * 更新工作流
   */
  async updateWorkflow(id: string, data: Partial<WorkflowDesign>): Promise<ApiResponse<WorkflowDesign>> {
    return request({
      url: `/api/workflow-designs/${id}/`,
      method: 'put',
      data
    })
  },

  /**
   * 删除工作流
   */
  async deleteWorkflow(id: string): Promise<ApiResponse> {
    return request({
      url: `/api/workflow-designs/${id}/`,
      method: 'delete'
    })
  },

  /**
   * 添加节点
   */
  async addNode(workflowId: string, node: WorkflowNode): Promise<ApiResponse> {
    return request({
      url: `/api/workflow-designs/${workflowId}/add_node/`,
      method: 'post',
      data: node
    })
  },

  /**
   * 更新节点
   */
  async updateNode(workflowId: string, nodeId: string, updates: Partial<WorkflowNode>): Promise<ApiResponse> {
    return request({
      url: `/api/workflow-designs/${workflowId}/update_node/`,
      method: 'put',
      data: {
        node_id: nodeId,
        updates
      }
    })
  },

  /**
   * 删除节点
   */
  async deleteNode(workflowId: string, nodeId: string): Promise<ApiResponse> {
    return request({
      url: `/api/workflow-designs/${workflowId}/delete_node/`,
      method: 'delete',
      params: { node_id: nodeId }
    })
  },

  /**
   * 添加连接
   */
  async addConnection(workflowId: string, connection: WorkflowConnection): Promise<ApiResponse> {
    return request({
      url: `/api/workflow-designs/${workflowId}/add_connection/`,
      method: 'post',
      data: connection
    })
  },

  /**
   * 删除连接
   */
  async deleteConnection(workflowId: string, connectionId: string): Promise<ApiResponse> {
    return request({
      url: `/api/workflow-designs/${workflowId}/delete_connection/`,
      method: 'delete',
      params: { connection_id: connectionId }
    })
  },

  /**
   * 验证工作流
   */
  async validateWorkflow(workflowId: string): Promise<ApiResponse<{
    valid: boolean
    errors?: string[]
  }>> {
    return request({
      url: `/api/workflow-designs/${workflowId}/validate/`,
      method: 'post'
    })
  },

  /**
   * 测试工作流
   */
  async testWorkflow(workflowId: string, inputData: Record<string, any>): Promise<ApiResponse<{
    execution: WorkflowExecution
  }>> {
    return request({
      url: `/api/workflow-designs/${workflowId}/test/`,
      method: 'post',
      data: { input_data: inputData }
    })
  },

  /**
   * 获取工作流版本列表
   */
  async getVersions(workflowId: string): Promise<ApiResponse<WorkflowVersion[]>> {
    return request({
      url: `/api/workflow-designs/${workflowId}/versions/`,
      method: 'get'
    })
  },

  /**
   * 创建新版本
   */
  async createVersion(workflowId: string, data: {
    version_name: string
    description: string
    tags?: string[]
  }): Promise<ApiResponse<{ version: WorkflowVersion }>> {
    return request({
      url: `/api/workflow-designs/${workflowId}/create_version/`,
      method: 'post',
      data
    })
  },

  /**
   * 回滚到指定版本
   */
  async rollbackVersion(workflowId: string, versionId: string): Promise<ApiResponse> {
    return request({
      url: `/api/workflow-designs/${workflowId}/rollback/`,
      method: 'post',
      data: { version_id: versionId }
    })
  },

  /**
   * 获取执行历史
   */
  async getExecutions(workflowId: string): Promise<ApiResponse<WorkflowExecution[]>> {
    return request({
      url: `/api/workflow-designs/${workflowId}/executions/`,
      method: 'get'
    })
  },

  /**
   * 获取工作流统计
   */
  async getStatistics(workflowId: string): Promise<ApiResponse<{
    total_executions: number
    successful_executions: number
    success_rate: number
    recent_executions: number
    average_duration: number
    node_count: number
    connection_count: number
    version_count: number
  }>> {
    return request({
      url: `/api/workflow-designs/${workflowId}/statistics/`,
      method: 'get'
    })
  },

  /**
   * 获取工作流模板
   */
  async getTemplates(): Promise<ApiResponse<WorkflowTemplate[]>> {
    return request({
      url: '/api/workflow-templates/',
      method: 'get'
    })
  },

  /**
   * 从模板创建工作流
   */
  async createFromTemplate(data: {
    template_id: string
    name: string
    description?: string
  }): Promise<ApiResponse<{ workflow: WorkflowDesign }>> {
    return request({
      url: '/api/workflow-create-from-template/',
      method: 'post',
      data
    })
  },

  /**
   * 版本对比
   */
  async compareVersions(sourceVersionId: string, targetVersionId: string): Promise<ApiResponse<{
    source_version: WorkflowVersion
    target_version: WorkflowVersion
    differences: {
      nodes: {
        added: WorkflowNode[]
        removed: WorkflowNode[]
        modified: Array<{
          node_id: string
          source: WorkflowNode
          target: WorkflowNode
        }>
      }
      connections: {
        added: WorkflowConnection[]
        removed: WorkflowConnection[]
        modified: Array<{
          connection_id: string
          source: WorkflowConnection
          target: WorkflowConnection
        }>
      }
    }
  }>> {
    return request({
      url: `/api/workflow-versions/${sourceVersionId}/compare/`,
      method: 'get',
      params: { target_version_id: targetVersionId }
    })
  },

  /**
   * 设置当前版本
   */
  async setCurrentVersion(versionId: string): Promise<ApiResponse> {
    return request({
      url: `/api/workflow-versions/${versionId}/set_current/`,
      method: 'post'
    })
  },

  /**
   * 取消执行
   */
  async cancelExecution(executionId: string): Promise<ApiResponse> {
    return request({
      url: `/api/workflow-executions/${executionId}/cancel/`,
      method: 'post'
    })
  },

  /**
   * 获取执行详情
   */
  async getExecution(executionId: string): Promise<ApiResponse<WorkflowExecution>> {
    return request({
      url: `/api/workflow-executions/${executionId}/`,
      method: 'get'
    })
  },

  /**
   * 导出工作流
   */
  async exportWorkflow(workflowId: string, format: 'json' | 'xml' = 'json'): Promise<Blob> {
    const response = await request({
      url: `/api/workflow-designs/${workflowId}/export/`,
      method: 'post',
      data: { format },
      responseType: 'blob'
    })
    return response
  },

  /**
   * 导入工作流
   */
  async importWorkflow(file: File): Promise<ApiResponse<{ workflow: WorkflowDesign }>> {
    const formData = new FormData()
    formData.append('file', file)
    
    return request({
      url: '/api/workflow-import/',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 复制工作流
   */
  async duplicateWorkflow(workflowId: string, newName: string): Promise<ApiResponse<{ workflow: WorkflowDesign }>> {
    return request({
      url: `/api/workflow-designs/${workflowId}/duplicate/`,
      method: 'post',
      data: { name: newName }
    })
  }
}

export default workflowApi
