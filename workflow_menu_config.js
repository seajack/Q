/**
 * 工作流设计器菜单配置
 * 将此配置添加到您的主菜单配置中
 */

export const workflowMenuConfig = {
  id: 'workflow',
  title: '工作流管理',
  icon: 'Workflow',
  children: [
    {
      id: 'workflow-designer',
      title: '流程设计器',
      icon: 'Edit',
      path: '/workflow-designer',
      component: 'WorkflowDesigner'
    },
    {
      id: 'workflow-list',
      title: '工作流列表',
      icon: 'List',
      path: '/workflow-list',
      component: 'WorkflowList'
    },
    {
      id: 'workflow-templates',
      title: '流程模板',
      icon: 'Document',
      path: '/workflow-templates',
      component: 'WorkflowTemplates'
    },
    {
      id: 'workflow-executions',
      title: '执行记录',
      icon: 'DataAnalysis',
      path: '/workflow-executions',
      component: 'WorkflowExecutions'
    }
  ]
}

// 使用示例：
// 在您的主菜单配置中添加：
// {
//   ...otherMenuItems,
//   ...workflowMenuConfig
// }
