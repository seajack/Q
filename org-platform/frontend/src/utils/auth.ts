import api from './request'

export interface LoginRequest {
  username: string
  password: string
  rememberMe?: boolean
}

export interface LoginResponse {
  token: string
  user: {
    id: number
    username: string
    name: string
    email: string
    role: string
  }
  expiresIn: number
}

export interface UserInfo {
  id: number
  username: string
  name: string
  email: string
  role: string
  avatar?: string
  permissions: string[]
}

// 登录API
export const loginApi = {
  // 用户登录
  login: (data: LoginRequest): Promise<LoginResponse> => {
    return api.post('/auth/login/', data)
  },

  // 获取用户信息
  getUserInfo: (): Promise<UserInfo> => {
    return api.get('/auth/user-info/')
  },

  // 刷新token
  refreshToken: (): Promise<{ token: string; expiresIn: number }> => {
    return api.post('/auth/refresh/')
  },

  // 登出
  logout: (): Promise<void> => {
    return api.post('/auth/logout/')
  },

  // 修改密码
  changePassword: (data: { oldPassword: string; newPassword: string }): Promise<void> => {
    return api.post('/auth/change-password/', data)
  }
}

// Token管理
export const tokenManager = {
  // 设置token
  setToken: (token: string) => {
    localStorage.setItem('access_token', token)
  },

  // 获取token
  getToken: (): string | null => {
    return localStorage.getItem('access_token')
  },

  // 移除token
  removeToken: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
  },

  // 检查token是否存在
  hasToken: (): boolean => {
    return !!tokenManager.getToken()
  }
}

// 用户信息管理
export const userManager = {
  // 设置用户信息
  setUserInfo: (userInfo: UserInfo) => {
    localStorage.setItem('user_info', JSON.stringify(userInfo))
  },

  // 获取用户信息
  getUserInfo: (): UserInfo | null => {
    const userInfo = localStorage.getItem('user_info')
    return userInfo ? JSON.parse(userInfo) : null
  },

  // 移除用户信息
  removeUserInfo: () => {
    localStorage.removeItem('user_info')
  }
}

// 权限检查
export const permissionManager = {
  // 检查是否有权限
  hasPermission: (permission: string): boolean => {
    const userInfo = userManager.getUserInfo()
    if (!userInfo) return false
    return userInfo.permissions.includes(permission) || userInfo.role === 'admin'
  },

  // 检查是否有任一权限
  hasAnyPermission: (permissions: string[]): boolean => {
    const userInfo = userManager.getUserInfo()
    if (!userInfo) return false
    return permissions.some(permission => 
      userInfo.permissions.includes(permission) || userInfo.role === 'admin'
    )
  },

  // 检查是否有所有权限
  hasAllPermissions: (permissions: string[]): boolean => {
    const userInfo = userManager.getUserInfo()
    if (!userInfo) return false
    return permissions.every(permission => 
      userInfo.permissions.includes(permission) || userInfo.role === 'admin'
    )
  }
}
