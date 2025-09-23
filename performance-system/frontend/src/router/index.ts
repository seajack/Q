import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '仪表板' }
  },
  {
    path: '/cycles',
    name: 'EvaluationCycles',
    component: () => import('@/views/EvaluationCycles.vue'),
    meta: { title: '考核周期管理' }
  },
  {
    path: '/indicators',
    name: 'EvaluationIndicators',
    component: () => import('@/views/EvaluationIndicators.vue'),
    meta: { title: '考核指标管理' }
  },
  {
    path: '/rules',
    name: 'EvaluationRules',
    component: () => import('@/views/EvaluationRules.vue'),
    meta: { title: '考核规则管理' }
  },
  {
    path: '/employees',
    name: 'Employees',
    component: () => import('@/views/Employees.vue'),
    meta: { title: '员工管理' }
  },
  {
    path: '/tasks',
    name: 'EvaluationTasks',
    component: () => import('@/views/EvaluationTasks.vue'),
    meta: { title: '考核任务' }
  },
  {
    path: '/evaluation/:code',
    name: 'EvaluationForm',
    component: () => import('@/views/EvaluationForm.vue'),
    meta: { title: '考核评分' },
    props: true
  },
  {
    path: '/results',
    name: 'EvaluationResults',
    component: () => import('@/views/EvaluationResults.vue'),
    meta: { title: '考核结果' }
  },
  {
    path: '/organization',
    name: 'OrganizationView',
    component: () => import('@/views/OrganizationView.vue'),
    meta: { title: '组织架构' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router