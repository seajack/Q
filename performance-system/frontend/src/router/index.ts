import { createRouter, createWebHistory } from 'vue-router'
const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '系统登录', layout: 'none' }
  },
  {
    path: '/code-login',
    name: 'CodeLogin',
    component: () => import('@/views/CodeLogin.vue'),
    meta: { title: '考核码登录', layout: 'none' }
  },
  {
    path: '/entry',
    name: 'EntryPage',
    component: () => import('@/views/EntryPage.vue'),
    meta: { title: '系统入口' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '仪表板' }
  },
  {
    path: '/dashboard-new',
    name: 'DashboardNew',
    component: () => import('@/views/DashboardNew.vue'),
    meta: { title: '考核看板（新UI）', layout: 'topnav' }
  },
  {
    path: '/dashboard-refactored',
    name: 'DashboardRefactored',
    component: () => import('@/views/DashboardRefactored.vue'),
    meta: { title: '仪表板（重构版）', layout: 'topnav' }
  },
  {
    path: '/test-dashboard',
    name: 'TestDashboard',
    component: () => import('@/views/TestDashboard.vue'),
    meta: { title: '考核看板数据测试', layout: 'topnav' }
  },
  {
    path: '/cycles',
    name: 'EvaluationCycles',
    component: () => import('@/views/CyclesModern.vue'),
    meta: { title: '考核周期管理', layout: 'topnav' }
  },
  {
    path: '/cycles-refactored',
    name: 'CyclesRefactored',
    component: () => import('@/views/CyclesRefactored.vue'),
    meta: { title: '考核周期管理（重构版）', layout: 'topnav' }
  },
  {
    path: '/cycles-elementplus',
    name: 'CyclesElementPlus',
    component: () => import('@/views/CyclesRefactoredElementPlus.vue'),
    meta: { title: '考核周期管理（Element Plus版）', layout: 'topnav' }
  },
  {
    path: '/cycles-modern',
    name: 'CyclesModern',
    component: () => import('@/views/CyclesModern.vue'),
    meta: { title: '考核周期管理（现代化版）', layout: 'topnav' }
  },
  {
    path: '/indicators',
    name: 'EvaluationIndicators',
    component: () => import('@/views/IndicatorsNew.vue'),
    meta: { title: '考核指标管理', layout: 'topnav' }
  },
  {
    path: '/indicators-refactored',
    name: 'IndicatorsRefactored',
    component: () => import('@/views/IndicatorsRefactored.vue'),
    meta: { title: '考核指标管理（重构版）', layout: 'topnav' }
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
    path: '/employees-refactored',
    name: 'EmployeesRefactored',
    component: () => import('@/views/EmployeesRefactored.vue'),
    meta: { title: '员工管理（重构版）', layout: 'topnav' }
  },
  {
    path: '/employee-onboarding',
    name: 'EmployeeOnboarding',
    component: () => import('@/views/EmployeeOnboarding.vue'),
    meta: { title: '入职管理', layout: 'topnav' }
  },
  {
    path: '/employee-offboarding',
    name: 'EmployeeOffboarding',
    component: () => import('@/views/EmployeeOffboarding.vue'),
    meta: { title: '离职管理', layout: 'topnav' }
  },
  {
    path: '/tasks',
    name: 'EvaluationTasks',
    component: () => import('@/views/TasksNew.vue'),
    meta: { title: '考核任务', layout: 'topnav' }
  },
  {
    path: '/tasks-refactored',
    name: 'TasksRefactored',
    component: () => import('@/views/TasksRefactored.vue'),
    meta: { title: '考核任务（重构版）', layout: 'topnav' }
  },
  {
    path: '/evaluation-entry',
    name: 'EvaluationEntry',
    component: () => import('@/views/EvaluationEntry.vue'),
    meta: { title: '考核入口' }
  },
  {
    path: '/evaluation-login',
    name: 'EvaluationLogin',
    component: () => import('@/views/EvaluationLogin.vue'),
    meta: { title: '考核码登录' }
  },
  {
    path: '/evaluation',
    name: 'Evaluation',
    component: () => import('@/views/Evaluation.vue'),
    meta: { title: '我的考核任务' }
  },
  {
    path: '/evaluation-tasks',
    name: 'EvaluatorTasks',
    component: () => import('@/views/EvaluationTasks.vue'),
    meta: { title: '我的考核任务' }
  },
  {
    path: '/manual-assignments',
    name: 'ManualAssignments',
    component: () => import('@/views/ManualAssignments.vue'),
    meta: { title: '手动分配', layout: 'topnav' }
  },
  {
    path: '/manual-evaluation',
    name: 'ManualEvaluation',
    component: () => import('@/views/ManualEvaluation.vue'),
    meta: { title: '手动分配评分', layout: 'topnav' }
  },
  {
    path: '/position-weights',
    name: 'PositionWeights',
    component: () => import('@/views/PositionWeights.vue'),
    meta: { title: '职级权重配置', layout: 'topnav' }
  },
  {
    path: '/evaluation/:id',
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
    path: '/results-refactored',
    name: 'ResultsRefactored',
    component: () => import('@/views/ResultsRefactored.vue'),
    meta: { title: '考核结果（重构版）', layout: 'topnav' }
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
    path: '/settings-refactored',
    name: 'SettingsRefactored',
    component: () => import('@/views/SettingsRefactored.vue'),
    meta: { title: '系统设置（重构版）', layout: 'topnav' }
  },
  {
    path: '/integration',
    name: 'IntegrationManagement',
    component: () => import('@/views/IntegrationManagement.vue'),
    meta: { title: '集成管理', layout: 'topnav' }
  },
  {
    path: '/permissions',
    name: 'Permissions',
    component: () => import('@/views/PermissionsNew.vue'),
    meta: { title: '权限管理', layout: 'topnav' }
  },
  {
    path: '/multidimensional-evaluation',
    name: 'MultidimensionalEvaluation',
    component: () => import('@/views/MultidimensionalEvaluation.vue'),
    meta: { title: '多维度评估', layout: 'topnav' }
  },
  {
    path: '/multidimensional-refactored',
    name: 'MultidimensionalRefactored',
    component: () => import('@/views/MultidimensionalRefactored.vue'),
    meta: { title: '多维度评估（重构版）', layout: 'topnav' }
  },
  {
    path: '/evaluation-dimensions',
    name: 'EvaluationDimensions',
    component: () => import('@/views/EvaluationDimensions.vue'),
    meta: { title: '评估维度管理', layout: 'topnav' }
  },
  {
    path: '/user-profile',
    name: 'UserProfile',
    component: () => import('@/views/UserProfile.vue'),
    meta: { title: '个人信息', layout: 'topnav' }
  },
  {
    path: '/user-settings',
    name: 'UserSettings',
    component: () => import('@/views/UserSettings.vue'),
    meta: { title: '账号设置', layout: 'topnav' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router