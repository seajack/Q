import { createRouter, createWebHistory } from 'vue-router'
const routes = [
  {
    path: '/',
    redirect: '/dashboard-new'
  },
  {
    path: '/dashboard',
    redirect: '/dashboard-new'
  },
  {
    path: '/dashboard-new',
    name: 'DashboardNew',
    component: () => import('@/views/DashboardNew.vue'),
    meta: { title: '考核看板（新UI）', layout: 'topnav' }
  },
  {
    path: '/cycles',
    name: 'EvaluationCycles',
    component: () => import('@/views/CyclesNew.vue'),
    meta: { title: '考核周期管理', layout: 'topnav' }
  },
  {
    path: '/indicators',
    name: 'EvaluationIndicators',
    component: () => import('@/views/IndicatorsNew.vue'),
    meta: { title: '考核指标管理', layout: 'topnav' }
  },
  {
    path: '/rules',
    name: 'EvaluationRules',
    component: () => import('@/views/RulesNew.vue'),
    meta: { title: '考核规则管理', layout: 'topnav' }
  },
  {
    path: '/employees',
    name: 'Employees',
    component: () => import('@/views/EmployeesNew.vue'),
    meta: { title: '员工管理', layout: 'topnav' }
  },
  {
    path: '/tasks',
    name: 'EvaluationTasks',
    component: () => import('@/views/TasksNew.vue'),
    meta: { title: '考核任务', layout: 'topnav' }
  },
  {
    path: '/manual-assignments',
    name: 'ManualAssignments',
    component: () => import('@/views/ManualAssignments.vue'),
    meta: { title: '手动分配', layout: 'topnav' }
  },
  {
    path: '/evaluation/:code',
    name: 'EvaluationForm',
    component: () => import('@/views/EvaluationForm.vue'),
    meta: { title: '考核评分', layout: 'topnav' },
    props: true
  },
  {
    path: '/results',
    name: 'EvaluationResults',
    component: () => import('@/views/ResultsNew.vue'),
    meta: { title: '考核结果', layout: 'topnav' }
  },
  {
    path: '/organization',
    name: 'OrganizationView',
    component: () => import('@/views/OrganizationNew.vue'),
    meta: { title: '组织架构', layout: 'topnav' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsNew.vue'),
    meta: { title: '系统设置', layout: 'topnav' }
  },
  {
    path: '/permissions',
    name: 'Permissions',
    component: () => import('@/views/PermissionsNew.vue'),
    meta: { title: '权限管理', layout: 'topnav' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router