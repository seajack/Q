import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/TopNavLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表板' }
      },
      {
        path: 'departments',
        name: 'Departments',
        component: () => import('@/views/Departments.vue'),
        meta: { title: '部门管理' }
      },
      {
        path: 'positions',
        name: 'Positions',
        component: () => import('@/views/Positions.vue'),
        meta: { title: '职位管理' }
      },
      {
        path: 'employees',
        name: 'Employees',
        component: () => import('@/views/Employees.vue'),
        meta: { title: '员工管理' }
      },
      {
        path: 'organization-tree',
        name: 'OrganizationTree',
        component: () => import('@/views/OrganizationTree.vue'),
        meta: { title: '组织架构树' }
      },
      {
        path: 'configs',
        name: 'SystemConfigs',
        component: () => import('@/views/SystemConfigs.vue'),
        meta: { title: '系统配置' }
      },
      {
        path: 'dictionaries',
        name: 'Dictionaries',
        component: () => import('@/views/Dictionaries.vue'),
        meta: { title: '数据字典' }
      },
      {
        path: 'position-templates',
        name: 'PositionTemplates',
        component: () => import('@/views/PositionTemplates.vue'),
        meta: { title: '职位模板' }
      },
      {
        path: 'workflow-rules',
        name: 'WorkflowRules',
        component: () => import('@/views/WorkflowRules.vue'),
        meta: { title: '工作流规则' }
      },
      {
        path: 'integration-management',
        name: 'IntegrationManagement',
        component: () => import('@/views/IntegrationManagement.vue'),
        meta: { title: '集成管理' }
      },
      {
        path: 'integration-dashboard',
        name: 'IntegrationDashboard',
        component: () => import('@/views/IntegrationDashboard.vue'),
        meta: { title: '集成仪表板' }
      },
      {
        path: 'integration-systems',
        name: 'IntegrationSystems',
        component: () => import('@/views/IntegrationSystems.vue'),
        meta: { title: '集成系统' }
      },
      {
        path: 'api-gateways',
        name: 'APIGateways',
        component: () => import('@/views/APIGateways.vue'),
        meta: { title: 'API网关' }
      },
      {
        path: 'data-sync-rules',
        name: 'DataSyncRules',
        component: () => import('@/views/DataSyncRules.vue'),
        meta: { title: '数据同步规则' }
      },
      {
        path: 'permission-management',
        name: 'PermissionManagement',
        component: () => import('@/views/PermissionManagement.vue'),
        meta: { title: '权限管理' }
      },
      {
        path: 'permissions',
        name: 'Permissions',
        component: () => import('@/views/Permissions.vue'),
        meta: { title: '权限管理' }
      },
      {
        path: 'roles',
        name: 'Roles',
        component: () => import('@/views/Roles.vue'),
        meta: { title: '角色管理' }
      },
      {
        path: 'data-permissions',
        name: 'DataPermissions',
        component: () => import('@/views/DataPermissions.vue'),
        meta: { title: '数据权限' }
      },
      {
        path: 'permission-dashboard',
        name: 'PermissionDashboard',
        component: () => import('@/views/PermissionDashboard.vue'),
        meta: { title: '权限仪表板' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router