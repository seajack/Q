import type { Router } from 'vue-router'
import { tokenManager, userManager } from '@/utils/auth'
import { ElMessage } from 'element-plus'

// 需要登录的页面路径
const protectedRoutes = [
  '/dashboard',
  '/departments',
  '/positions',
  '/employees',
  '/organization-tree',
  '/configs',
  '/dictionaries',
  '/position-templates',
  '/workflow-rules',
  '/workflow-list',
  '/workflow-designer',
  '/workflow-templates',
  '/intelligent-analysis',
  '/integration-management',
  '/permission-management',
  '/permissions',
  '/roles',
  '/data-permissions',
  '/permission-dashboard',
  '/tenant-management'
]

// 公开页面路径（不需要登录）
const publicRoutes = [
  '/login'
]

export function setupAuthGuards(router: Router) {
  // 全局前置守卫
  router.beforeEach((to, from, next) => {
    const isProtectedRoute = protectedRoutes.some(route => to.path.startsWith(route))
    const isPublicRoute = publicRoutes.includes(to.path)
    const hasToken = tokenManager.hasToken()
    const hasUserInfo = !!userManager.getUserInfo()

    // 如果访问登录页面且已登录，重定向到首页
    if (to.path === '/login' && hasToken && hasUserInfo) {
      next('/dashboard')
      return
    }

    // 如果访问受保护的路由但未登录，重定向到登录页
    if (isProtectedRoute && (!hasToken || !hasUserInfo)) {
      ElMessage.warning('请先登录')
      next('/login')
      return
    }

    // 如果访问公开路由或已登录，允许访问
    if (isPublicRoute || hasToken) {
      next()
      return
    }

    // 默认允许访问
    next()
  })

  // 全局后置钩子
  router.afterEach((to) => {
    // 设置页面标题
    if (to.meta?.title) {
      document.title = `${to.meta.title} - 组织中台系统`
    } else {
      document.title = '组织中台系统'
    }
  })
}

// 检查用户权限
export function checkPermission(permission: string): boolean {
  const userInfo = userManager.getUserInfo()
  if (!userInfo) return false
  
  // 管理员拥有所有权限
  if (userInfo.role === 'admin') return true
  
  // 检查具体权限
  return userInfo.permissions?.includes(permission) || false
}

// 检查用户角色
export function checkRole(role: string): boolean {
  const userInfo = userManager.getUserInfo()
  if (!userInfo) return false
  
  return userInfo.role === role
}

// 登出处理
export function handleLogout(router: Router) {
  // 清除本地存储
  tokenManager.removeToken()
  userManager.removeUserInfo()
  
  // 显示登出消息
  ElMessage.success('已安全退出')
  
  // 重定向到登录页
  router.push('/login')
}
