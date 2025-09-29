/**
 * 工作流设计器路由配置
 */

export const workflowRoutes = [
  {
    path: '/workflow-designer',
    name: 'WorkflowDesigner',
    component: () => import('@/views/WorkflowDesigner.vue'),
    meta: {
      title: '工作流设计器',
      requiresAuth: true,
      icon: 'Workflow'
    }
  },
  {
    path: '/workflow-designer/:id',
    name: 'WorkflowDesignerEdit',
    component: () => import('@/views/WorkflowDesigner.vue'),
    meta: {
      title: '编辑工作流',
      requiresAuth: true,
      icon: 'Edit'
    }
  },
  {
    path: '/workflow-list',
    name: 'WorkflowList',
    component: () => import('@/views/WorkflowList.vue'),
    meta: {
      title: '工作流列表',
      requiresAuth: true,
      icon: 'List'
    }
  }
]
