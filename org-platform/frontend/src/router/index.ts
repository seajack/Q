import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
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
    path: '/departments',
    name: 'Departments',
    component: () => import('@/views/Departments.vue'),
    meta: { title: '部门管理' }
  },
  {
    path: '/positions',
    name: 'Positions',
    component: () => import('@/views/Positions.vue'),
    meta: { title: '职位管理' }
  },
  {
    path: '/employees',
    name: 'Employees',
    component: () => import('@/views/Employees.vue'),
    meta: { title: '员工管理' }
  },
  {
    path: '/organization-tree',
    name: 'OrganizationTree',
    component: () => import('@/views/OrganizationTree.vue'),
    meta: { title: '组织架构树' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router