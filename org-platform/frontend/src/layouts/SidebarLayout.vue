<template>
  <div class="app-container" :class="{ 'sidebar-collapsed': isCollapsed }">
    <!-- 侧边菜单 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-container">
          <div class="logo-icon">
            <img src="/logo.svg" alt="企业Logo" class="logo-image">
          </div>
          <div class="logo-text" v-show="!isCollapsed">组织中台</div>
        </div>
        <div class="collapse-btn" @click="toggleSidebar">
          <el-icon><component :is="isCollapsed ? 'Expand' : 'Fold'" /></el-icon>
        </div>
      </div>

      <el-scrollbar class="menu-scrollbar">
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapsed"
          :collapse-transition="false"
          class="sidebar-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataBoard /></el-icon>
            <template #title>仪表板</template>
          </el-menu-item>

          <el-sub-menu index="org">
            <template #title>
              <el-icon><OfficeBuilding /></el-icon>
              <span>组织管理</span>
            </template>
            <el-menu-item index="/departments">部门管理</el-menu-item>
            <el-menu-item index="/positions">职位管理</el-menu-item>
            <el-menu-item index="/organization-tree">组织架构</el-menu-item>
            <el-menu-item index="/position-templates">职位模板</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="employee">
            <template #title>
              <el-icon><User /></el-icon>
              <span>人员管理</span>
            </template>
            <el-menu-item index="/employees">员工列表</el-menu-item>
            <el-menu-item index="/employee-onboarding">入职管理</el-menu-item>
            <el-menu-item index="/employee-offboarding">离职管理</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="workflow">
            <template #title>
              <el-icon><Connection /></el-icon>
              <span>工作流管理</span>
            </template>
            <el-menu-item index="/workflow-rules">工作流规则</el-menu-item>
            <el-menu-item index="/workflow-list">工作流列表</el-menu-item>
            <el-menu-item index="/workflow-templates">流程模板</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/intelligent-analysis">
            <el-icon><TrendCharts /></el-icon>
            <template #title>智能分析</template>
          </el-menu-item>

          <el-sub-menu index="system">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </template>
            <el-menu-item index="/dictionaries">数据字典</el-menu-item>
            <el-menu-item index="/configs">系统配置</el-menu-item>
            <el-menu-item index="/integration-management">集成管理</el-menu-item>
            <el-menu-item index="/permission-management">权限管理</el-menu-item>
            <el-menu-item index="/tenant-management">多租户管理</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-scrollbar>

      <div class="sidebar-footer" v-show="!isCollapsed">
        <div class="environment-tag">
          <el-tag size="small" effect="plain" type="info">生产环境</el-tag>
        </div>
        <div class="version-info">v2.0.0</div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部导航栏 -->
      <header class="top-navbar">
        <div class="navbar-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index">
              {{ item }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="navbar-right">
          <div class="search-box">
            <el-input
              v-model="searchQuery"
              placeholder="全局搜索..."
              prefix-icon="Search"
              clearable
              @keyup.enter="handleSearch"
            />
          </div>

          <div class="action-item">
            <el-tooltip content="消息通知" placement="bottom">
              <el-badge :value="3" class="notification-badge">
                <el-icon><Bell /></el-icon>
              </el-badge>
            </el-tooltip>
          </div>

          <div class="action-item">
            <el-tooltip :content="isDark ? '切换到浅色模式' : '切换到深色模式'" placement="bottom">
              <div class="theme-toggle" @click="toggleTheme">
                <el-icon><component :is="isDark ? 'Sunny' : 'Moon'" /></el-icon>
              </div>
            </el-tooltip>
          </div>

          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-profile">
              <div class="avatar">
                <span>{{ userInitials }}</span>
              </div>
              <div class="user-info" v-show="!isCollapsed">
                <div class="username">{{ userName }}</div>
                <div class="role">{{ userRole }}</div>
              </div>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人信息
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>账号设置
                </el-dropdown-item>
                <el-dropdown-item command="help">
                  <el-icon><QuestionFilled /></el-icon>帮助中心
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 页面内容区 -->
      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import {
  Fold, Expand, DataBoard, OfficeBuilding, User, Connection,
  TrendCharts, Setting, Bell, Search, ArrowDown, Moon, Sunny,
  QuestionFilled, SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()

// 侧边栏状态
const isCollapsed = ref(false)
const activeMenu = ref('')
const breadcrumbs = ref<string[]>([])

// 用户信息
const userName = ref('管理员')
const userRole = ref('系统管理员')
const userInitials = computed(() => userName.value.slice(0, 2))

// 搜索
const searchQuery = ref('')

// 主题
const isDark = computed(() => themeStore.isDark())

// 菜单映射表
const menuMap: Record<string, string[]> = {
  '/dashboard': ['仪表板'],
  '/departments': ['组织管理', '部门管理'],
  '/positions': ['组织管理', '职位管理'],
  '/organization-tree': ['组织管理', '组织架构'],
  '/position-templates': ['组织管理', '职位模板'],
  '/employees': ['人员管理', '员工列表'],
  '/employee-onboarding': ['人员管理', '入职管理'],
  '/employee-offboarding': ['人员管理', '离职管理'],
  '/workflow-rules': ['工作流管理', '工作流规则'],
  '/workflow-list': ['工作流管理', '工作流列表'],
  '/workflow-templates': ['工作流管理', '流程模板'],
  '/intelligent-analysis': ['智能分析'],
  '/dictionaries': ['系统设置', '数据字典'],
  '/configs': ['系统设置', '系统配置'],
  '/integration-management': ['系统设置', '集成管理'],
  '/permission-management': ['系统设置', '权限管理'],
  '/tenant-management': ['系统设置', '多租户管理']
}

// 侧边栏折叠控制
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('sidebarCollapsed', String(isCollapsed.value))
}

// 菜单选择处理
const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  breadcrumbs.value = menuMap[index] || ['首页']
  router.push(index)
}

// 主题切换
const toggleTheme = () => {
  themeStore.toggleTheme()
}

// 搜索处理
const handleSearch = () => {
  if (!searchQuery.value) return
  console.log('搜索:', searchQuery.value)
  // 实现搜索逻辑
}

// 用户下拉菜单处理
const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'help':
      window.open('/help', '_blank')
      break
    case 'logout':
      // 实现登出逻辑
      console.log('登出')
      break
  }
}

// 监听路由变化，更新面包屑和活动菜单
watch(
  () => route.path,
  (path) => {
    activeMenu.value = path
    breadcrumbs.value = menuMap[path] || ['首页']
  },
  { immediate: true }
)

onMounted(() => {
  // 从本地存储恢复侧边栏状态
  const savedState = localStorage.getItem('sidebarCollapsed')
  if (savedState !== null) {
    isCollapsed.value = savedState === 'true'
  }
  
  // 初始化活动菜单和面包屑
  activeMenu.value = route.path
  breadcrumbs.value = menuMap[route.path] || ['首页']
})
</script>

<style scoped>
/* 应用容器 */
.app-container {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
  background-color: #f5f7fa;
}

/* 侧边栏 - 强制样式 */
.sidebar {
  width: 240px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #2a3a6f !important;  /* 更灰更暗的蓝灰色 */
  color: #d0e0f0 !important;  /* 稍暗的灰蓝色文字 */
  transition: width 0.3s;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

/* 调试信息 */
.sidebar::after {
  content: "当前侧边栏背景色: #2a3a6f (灰暗色调)";
  position: fixed;
  bottom: 10px;
  left: 10px;
  color: white;
  font-size: 12px;
  background: rgba(0,0,0,0.5);
  padding: 5px;
  border-radius: 3px;
}

.app-container.sidebar-collapsed .sidebar {
  width: 64px;
}

.sidebar-header {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
}

.logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border-radius: 6px;
  transition: all 0.3s;
}

.logo-image {
  height: 20px;
  width: auto;
  background: transparent;
  filter: brightness(1.1) contrast(1.1);
  transition: all 0.3s;
  border-radius: 4px;
}

.app-container.sidebar-collapsed .logo-image {
  height: 16px;
}

/* 暗色主题下的logo优化 */
.dark-theme .logo-image {
  filter: brightness(1.2) contrast(1.2);
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
}

.collapse-btn {
  cursor: pointer;
  font-size: 16px;
  color: #b8c7e8;
  transition: color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

.collapse-btn:hover {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.05);
}

.menu-scrollbar {
  flex: 1;
  overflow-x: hidden;
}

.sidebar-menu {
  border-right: none;
  background-color: transparent;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  height: 50px;
  line-height: 50px;
  color: #b8c7e8;
  background-color: transparent;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.15);
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.08);
}

/* 次级菜单样式修复 - 颜色反转 + 缩进和图标 */
.sidebar-menu :deep(.el-sub-menu .el-menu-item) {
  height: 45px;
  line-height: 45px;
  color: #2a3a6f; /* 使用侧边栏背景色作为文字颜色 */
  background-color: #e3e6e9; /* 使用侧边栏文字颜色作为背景色 */
  padding-left: 60px; /* 增加更多缩进 */
  border-left: 3px solid transparent;
  transition: all 0.3s;
  font-weight: 500;
  position: relative;
}

/* 为二级菜单添加更美观的图标 */
.sidebar-menu :deep(.el-sub-menu .el-menu-item::before) {
  content: "•";
  position: absolute;
  left: 30px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #2a3a6f;
  transition: all 0.3s;
  font-weight: bold;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item:hover) {
  color: #2a3a6f; /* 保持侧边栏背景色 */
  background-color: #b8c7e8; /* 悬停时背景色稍深 */
  border-left-color: #2a3a6f; /* 边框使用侧边栏背景色 */
  font-weight: 600;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item:hover::before) {
  content: "▶";
  transform: translateY(-50%) translateX(3px); /* 悬停时图标向右移动 */
  color: #2a3a6f;
  font-size: 10px;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item.is-active) {
  color: #2a3a6f; /* 保持侧边栏背景色 */
  background-color: #a0b3d6; /* 激活时背景色更深 */
  border-left-color: #2a3a6f; /* 边框使用侧边栏背景色 */
  font-weight: 600;
  box-shadow: inset 0 0 8px rgba(42, 58, 111, 0.1); /* 内阴影使用侧边栏背景色 */
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item.is-active::before) {
  content: "◆"; /* 激活时显示菱形 */
  transform: translateY(-50%);
  color: #2a3a6f;
  font-size: 10px;
  font-weight: bold;
}

/* 暗色主题下的次级菜单 - 颜色反转 */
.dark-theme .sidebar-menu :deep(.el-sub-menu .el-menu-item) {
  color: #2a3a6f; /* 使用侧边栏背景色作为文字颜色 */
  background-color: #b8c7e8; /* 使用侧边栏文字颜色作为背景色 */
  font-weight: 500;
}

.dark-theme .sidebar-menu :deep(.el-sub-menu .el-menu-item:hover) {
  color: #2a3a6f; /* 保持侧边栏背景色 */
  background-color: #a0b3d6; /* 悬停时背景色稍深 */
  border-left-color: #2a3a6f; /* 边框使用侧边栏背景色 */
  font-weight: 600;
}

.dark-theme .sidebar-menu :deep(.el-sub-menu .el-menu-item.is-active) {
  color: #2a3a6f; /* 保持侧边栏背景色 */
  background-color: #8c9bc7; /* 激活时背景色更深 */
  border-left-color: #2a3a6f; /* 边框使用侧边栏背景色 */
  font-weight: 600;
  box-shadow: inset 0 0 12px rgba(42, 58, 111, 0.15); /* 内阴影使用侧边栏背景色 */
}

.sidebar-footer {
  height: 40px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.environment-tag {
  font-size: 12px;
}

.version-info {
  font-size: 12px;
  color: #8c8c8c;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航栏 */
.top-navbar {
  height: 64px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #ffffff;
  border-bottom: 1px solid #e6e6e6;
}

.navbar-left {
  display: flex;
  align-items: center;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-box {
  width: 240px;
}

.action-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
  color: #606266;
}

.action-item:hover {
  background-color: #f5f7fa;
  color: #409eff;
}

.notification-badge :deep(.el-badge__content) {
  z-index: 1;
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  color: #606266;
}

.theme-toggle:hover {
  background-color: #f5f7fa;
  color: #409eff;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.user-profile:hover {
  background-color: #f5f7fa;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #1a73e8, #5c8df5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  line-height: 1.2;
}

.role {
  font-size: 12px;
  color: #909399;
  line-height: 1.2;
}

.dropdown-icon {
  font-size: 12px;
  color: #909399;
  margin-left: 4px;
}

/* 页面内容区 */
.page-content {
  flex: 1;
  padding: 8px;
  overflow-y: auto;
  background-color: #f5f7fa;
  font-size: 13px;
}

/* 响应式设计 */
@media (max-width: 992px) {
  .sidebar {
    position: fixed;
    z-index: 1001;
    transform: translateX(0);
    transition: transform 0.3s;
  }
  
  .app-container.sidebar-collapsed .sidebar {
    transform: translateX(-100%);
  }
  
  .search-box {
    width: 180px;
  }
}

@media (max-width: 768px) {
  .top-navbar {
    padding: 0 16px;
  }
  
  .search-box {
    display: none;
  }
  
  .page-content {
    padding: 16px;
  }
}

/* 深色主题样式 */
html.dark .app-container {
  background-color: #141414;
}

html.dark .sidebar {
  background-color: #2a3a6f !important;
  color: #b8c7e8 !important;
}

html.dark .top-navbar {
  background-color: #1f1f1f;
  border-bottom: 1px solid #303030;
}

html.dark .page-content {
  background-color: #141414;
}
</style>