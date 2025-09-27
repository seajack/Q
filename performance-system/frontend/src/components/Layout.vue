<template>
  <div class="modern-app-layout">
    <!-- 现代化侧边栏 -->
    <aside :class="sidebarClasses" class="modern-sidebar">
      <div class="sidebar-header">
        <div class="logo-section">
          <div class="logo-icon">
            <el-icon class="logo-icon-svg"><TrendCharts /></el-icon>
          </div>
          <transition name="logo-text" mode="out-in">
            <div v-if="!isCollapsed" class="logo-content">
              <h1 class="logo-title">绩效管理</h1>
              <p class="logo-subtitle">Performance System</p>
            </div>
          </transition>
        </div>
        <button 
          class="collapse-button" 
          @click="toggleSidebar"
          :aria-label="isCollapsed ? '展开侧边栏' : '收起侧边栏'"
        >
          <el-icon>
            <component :is="isCollapsed ? 'Expand' : 'Fold'" />
          </el-icon>
        </button>
      </div>
      
      <nav class="sidebar-navigation" role="navigation">
        <el-menu
          :default-active="activeMenu"
          class="modern-sidebar-menu"
          :collapse="isCollapsed"
          :unique-opened="true"
          router
          :collapse-transition="true"
        >
          <!-- 仪表板 -->
          <el-menu-item index="/dashboard" class="modern-sidebar-item">
            <template #title>
              <el-icon class="menu-icon"><House /></el-icon>
              <span class="menu-text">仪表板</span>
            </template>
          </el-menu-item>

          <!-- 考核管理 -->
          <el-sub-menu index="evaluation" class="modern-sidebar-submenu">
            <template #title>
              <el-icon class="menu-icon"><Document /></el-icon>
              <span class="menu-text">考核管理</span>
            </template>
            <el-menu-item index="/cycles" class="modern-sidebar-subitem">
              <el-icon class="submenu-icon"><Calendar /></el-icon>
              <template #title>考核周期</template>
            </el-menu-item>
            <el-menu-item index="/indicators" class="modern-sidebar-subitem">
              <el-icon class="submenu-icon"><DataBoard /></el-icon>
              <template #title>考核指标</template>
            </el-menu-item>
            <el-menu-item index="/rules" class="modern-sidebar-subitem">
              <el-icon class="submenu-icon"><Setting /></el-icon>
              <template #title>考核规则</template>
            </el-menu-item>
            <el-menu-item index="/tasks" class="modern-sidebar-subitem">
              <el-icon class="submenu-icon"><List /></el-icon>
              <template #title>考核任务</template>
            </el-menu-item>
          </el-sub-menu>

          <!-- 人员管理 -->
          <el-sub-menu index="personnel" class="modern-sidebar-submenu">
            <template #title>
              <el-icon class="menu-icon"><User /></el-icon>
              <span class="menu-text">人员管理</span>
            </template>
            <el-menu-item index="/employees" class="modern-sidebar-subitem">
              <el-icon class="submenu-icon"><UserFilled /></el-icon>
              <template #title>员工管理</template>
            </el-menu-item>
            <el-menu-item index="/organization" class="modern-sidebar-subitem">
              <el-icon class="submenu-icon"><OfficeBuilding /></el-icon>
              <template #title>组织架构</template>
            </el-menu-item>
          </el-sub-menu>

          <!-- 考核结果 -->
          <el-menu-item index="/results" class="modern-sidebar-item">
            <template #title>
              <el-icon class="menu-icon"><TrendCharts /></el-icon>
              <span class="menu-text">考核结果</span>
            </template>
          </el-menu-item>

          <!-- 系统管理 -->
          <el-sub-menu index="system" class="modern-sidebar-submenu">
            <template #title>
              <el-icon class="menu-icon"><Tools /></el-icon>
              <span class="menu-text">系统管理</span>
            </template>
            <el-menu-item index="/integration" class="modern-sidebar-subitem">
              <el-icon class="submenu-icon"><Connection /></el-icon>
              <template #title>集成管理</template>
            </el-menu-item>
            <el-menu-item index="/permissions" class="modern-sidebar-subitem">
              <el-icon class="submenu-icon"><Lock /></el-icon>
              <template #title>权限管理</template>
            </el-menu-item>
            <el-menu-item index="/settings" class="modern-sidebar-subitem">
              <el-icon class="submenu-icon"><Setting /></el-icon>
              <template #title>基础设置</template>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </nav>
    </aside>

    <!-- 主内容区域 -->
    <div class="main-container">
      <!-- 现代化顶部导航栏 -->
      <header class="modern-header">
        <div class="header-left">
          <!-- 面包屑导航 -->
          <nav class="modern-breadcrumb" aria-label="面包屑导航">
            <el-breadcrumb separator="/" class="breadcrumb-nav">
              <el-breadcrumb-item 
                v-for="(item, index) in breadcrumbs" 
                :key="item.path"
                :to="index === breadcrumbs.length - 1 ? null : item.path"
                :class="{ active: index === breadcrumbs.length - 1 }"
              >
                {{ item.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </nav>
        </div>
        
        <div class="header-right">
          <!-- 全局搜索 -->
          <div class="search-container">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索功能、数据..."
              class="global-search"
              :prefix-icon="Search"
              clearable
              @keyup.enter="handleSearch"
            />
          </div>
          
          <!-- 快捷操作 -->
          <div class="quick-actions">
            <!-- 通知中心 -->
            <el-dropdown trigger="click" class="notification-dropdown">
              <div class="action-button">
                <el-badge :value="notificationCount" :hidden="notificationCount === 0">
                  <el-button type="text" :icon="Bell" circle size="large" />
                </el-badge>
              </div>
              <template #dropdown>
                <el-dropdown-menu class="notification-menu">
                  <div class="notification-header">
                    <h4>通知中心</h4>
                    <el-button type="text" size="small">全部已读</el-button>
                  </div>
                  <div class="notification-list">
                    <div 
                      v-for="notification in notifications" 
                      :key="notification.id"
                      class="notification-item"
                    >
                      <el-icon class="notification-icon" :class="`icon-${notification.type}`">
                        <component :is="getNotificationIcon(notification.type)" />
                      </el-icon>
                      <div class="notification-content">
                        <p class="notification-title">{{ notification.title }}</p>
                        <span class="notification-time">{{ formatTime(notification.time) }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="notification-footer">
                    <el-button type="text" size="small">查看全部</el-button>
                  </div>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            
            <!-- 用户菜单 -->
            <el-dropdown trigger="click" class="user-dropdown">
              <div class="user-profile">
                <el-avatar :size="36" :src="userAvatar" class="user-avatar">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <div v-if="!isCollapsed" class="user-info">
                  <span class="user-name">{{ userName }}</span>
                  <span class="user-role">{{ userRole }}</span>
                </div>
                <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu class="user-menu">
                  <el-dropdown-item class="user-menu-item">
                    <el-icon><User /></el-icon>
                    <span>个人中心</span>
                  </el-dropdown-item>
                  <el-dropdown-item class="user-menu-item">
                    <el-icon><Setting /></el-icon>
                    <span>账户设置</span>
                  </el-dropdown-item>
                  <el-dropdown-item class="user-menu-item">
                    <el-icon><QuestionFilled /></el-icon>
                    <span>帮助中心</span>
                  </el-dropdown-item>
                  <el-dropdown-item divided class="user-menu-item logout">
                    <el-icon><SwitchButton /></el-icon>
                    <span>退出登录</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="page-content modern-scrollbar">
        <div class="content-wrapper">
          <router-view v-slot="{ Component }">
            <transition name="page" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>

    <!-- 移动端遮罩 -->
    <div 
      v-if="isMobile && !isCollapsed" 
      class="mobile-overlay"
      @click="closeSidebar"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { 
  House, Calendar, DataBoard, Setting, User, Document, 
  TrendCharts, OfficeBuilding, List, UserFilled, Tools, 
  Lock, Search, Bell, ArrowDown, SwitchButton, QuestionFilled,
  Expand, Fold, Message, WarningFilled, InfoFilled
} from '@element-plus/icons-vue'

const route = useRoute()

// 侧边栏状态
const isCollapsed = ref(false)
const isMobile = ref(false)

// 搜索功能
const searchKeyword = ref('')

// 用户信息
const userName = ref('管理员')
const userRole = ref('系统管理员')
const userAvatar = ref('')

// 通知相关
const notificationCount = ref(3)
const notifications = ref([
  {
    id: 1,
    type: 'info',
    title: '新的考核周期已创建',
    time: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2小时前
  },
  {
    id: 2,
    type: 'warning',
    title: '有考核任务待处理',
    time: new Date(Date.now() - 4 * 60 * 60 * 1000) // 4小时前
  },
  {
    id: 3,
    type: 'success',
    title: '考核结果已生成',
    time: new Date(Date.now() - 24 * 60 * 60 * 1000) // 1天前
  }
])

// 计算属性
const sidebarClasses = computed(() => [
  'modern-sidebar',
  {
    'collapsed': isCollapsed.value,
    'mobile': isMobile.value
  }
])

const sidebarWidth = computed(() => isCollapsed.value ? '64px' : '240px')

// 面包屑导航
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  const items = matched.map(item => ({
    path: item.path,
    title: item.meta?.title || ''
  }))
  
  // 添加首页
  if (items.length === 0 || items[0].path !== '/dashboard') {
    items.unshift({ path: '/dashboard', title: '首页' })
  }
  
  return items
})

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 方法
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  if (isMobile.value && !isCollapsed.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

const closeSidebar = () => {
  if (isMobile.value) {
    isCollapsed.value = true
    document.body.style.overflow = ''
  }
}

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    console.log('搜索:', searchKeyword.value)
    // 实现搜索逻辑
  }
}

// 通知相关方法
const getNotificationIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    'info': InfoFilled,
    'warning': WarningFilled,
    'success': Document,
    'error': WarningFilled
  }
  return iconMap[type] || InfoFilled
}

const formatTime = (time: Date) => {
  const now = new Date()
  const diff = now.getTime() - time.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else {
    return `${days}天前`
  }
}

// 响应式检测
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    isCollapsed.value = true
  }
}

const handleResize = () => {
  checkMobile()
}

// 监听路由变化
watch(route, (newRoute) => {
  if (isMobile.value) {
    closeSidebar()
  }
}, { immediate: true })

// 生命周期钩子
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* 现代化布局样式 */
.modern-app-layout {
  height: 100vh;
  display: flex;
  background-color: var(--surface-secondary);
  overflow: hidden;
}

/* 现代化侧边栏 */
.modern-sidebar {
  width: 240px;
  background: linear-gradient(180deg, var(--neutral-800) 0%, var(--neutral-900) 100%);
  box-shadow: var(--shadow-2xl);
  transition: all var(--duration-normal) var(--ease-out);
  position: relative;
  z-index: var(--z-fixed);
  display: flex;
  flex-direction: column;
}

.modern-sidebar.collapsed {
  width: 64px;
}

.modern-sidebar.mobile {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: var(--z-modal);
}

/* 侧边栏头部 */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-6) var(--spacing-4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  min-height: 72px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex: 1;
  min-width: 0;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: var(--brand-primary-600);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
  flex-shrink: 0;
}

.logo-icon-svg {
  font-size: 20px;
  color: white;
}

.logo-content {
  min-width: 0;
  flex: 1;
}

.logo-title {
  color: var(--text-inverse);
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  margin: 0;
  line-height: var(--leading-tight);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logo-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: var(--text-xs);
  margin: 0;
  line-height: var(--leading-tight);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.collapse-button {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.collapse-button:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

/* 侧边栏导航 */
.sidebar-navigation {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--spacing-4) var(--spacing-2);
}

.modern-sidebar-menu {
  border: none;
  background: transparent;
  width: 100%;
}

.modern-sidebar-item,
.modern-sidebar-subitem {
  margin: var(--spacing-1) 0;
  border-radius: var(--radius-lg);
  transition: all var(--duration-fast) var(--ease-out);
  position: relative;
}

.modern-sidebar-item .el-menu-item,
.modern-sidebar-subitem .el-menu-item {
  color: rgba(255, 255, 255, 0.75);
  background: transparent;
  border-radius: var(--radius-lg);
  margin: 0;
  font-weight: var(--font-medium);
  padding: var(--spacing-3) var(--spacing-4);
  transition: all var(--duration-fast) var(--ease-out);
}

.modern-sidebar-item .el-menu-item:hover,
.modern-sidebar-subitem .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-inverse);
  transform: translateX(4px);
}

.modern-sidebar-item .el-menu-item.is-active,
.modern-sidebar-subitem .el-menu-item.is-active {
  background: rgba(37, 99, 235, 0.15);
  color: var(--brand-primary-300);
  border-left: 3px solid var(--brand-primary-400);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.modern-sidebar-submenu .el-sub-menu__title {
  color: rgba(255, 255, 255, 0.75);
  background: transparent;
  border-radius: var(--radius-lg);
  margin: var(--spacing-1) 0;
  font-weight: var(--font-medium);
  padding: var(--spacing-3) var(--spacing-4);
  transition: all var(--duration-fast) var(--ease-out);
}

.modern-sidebar-submenu .el-sub-menu__title:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-inverse);
}

.menu-icon,
.submenu-icon {
  font-size: 18px;
  margin-right: var(--spacing-3);
}

.menu-text {
  font-size: var(--text-sm);
}

/* 主内容区域 */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background-color: var(--surface-secondary);
}

/* 现代化顶部导航栏 */
.modern-header {
  background: var(--surface-primary);
  border-bottom: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-6);
  height: 72px;
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.header-left {
  flex: 1;
  min-width: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  flex-shrink: 0;
}

/* 面包屑导航 */
.modern-breadcrumb {
  display: flex;
  align-items: center;
}

.breadcrumb-nav {
  font-size: var(--text-sm);
}

.breadcrumb-nav .el-breadcrumb__item {
  color: var(--text-tertiary);
  transition: color var(--duration-fast) var(--ease-out);
}

.breadcrumb-nav .el-breadcrumb__item:hover {
  color: var(--brand-primary-600);
}

.breadcrumb-nav .el-breadcrumb__item.active {
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

/* 搜索容器 */
.search-container {
  position: relative;
}

.global-search {
  width: 320px;
  transition: width var(--duration-normal) var(--ease-out);
}

.global-search:focus-within {
  width: 400px;
}

.global-search .el-input__wrapper {
  background: var(--surface-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  transition: all var(--duration-fast) var(--ease-out);
}

.global-search .el-input__wrapper:hover {
  border-color: var(--border-default);
  background: var(--surface-quaternary);
}

.global-search .el-input__wrapper.is-focus {
  border-color: var(--brand-primary-500);
  box-shadow: var(--shadow-focus);
  background: var(--surface-primary);
}

/* 快捷操作 */
.quick-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.action-button {
  position: relative;
}

.notification-dropdown .el-button,
.user-dropdown .user-profile {
  transition: all var(--duration-fast) var(--ease-out);
}

.notification-dropdown .el-button:hover {
  background: var(--surface-quaternary);
  transform: translateY(-1px);
}

/* 通知下拉菜单 */
.notification-menu {
  width: 320px;
  max-height: 400px;
  overflow: hidden;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4) var(--spacing-4) var(--spacing-2);
  border-bottom: 1px solid var(--border-subtle);
}

.notification-header h4 {
  margin: 0;
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.notification-list {
  max-height: 280px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  border-bottom: 1px solid var(--border-subtle);
  transition: background-color var(--duration-fast) var(--ease-out);
  cursor: pointer;
}

.notification-item:hover {
  background: var(--surface-tertiary);
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-icon {
  width: 20px;
  height: 20px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}

.notification-icon.icon-info {
  background: var(--semantic-info-100);
  color: var(--semantic-info-600);
}

.notification-icon.icon-warning {
  background: var(--semantic-warning-100);
  color: var(--semantic-warning-600);
}

.notification-icon.icon-success {
  background: var(--semantic-success-100);
  color: var(--semantic-success-600);
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  margin: 0 0 var(--spacing-1) 0;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  line-height: var(--leading-tight);
}

.notification-time {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.notification-footer {
  padding: var(--spacing-2) var(--spacing-4);
  border-top: 1px solid var(--border-subtle);
  text-align: center;
}

/* 用户下拉菜单 */
.user-profile {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-xl);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  border: 1px solid transparent;
}

.user-profile:hover {
  background: var(--surface-quaternary);
  border-color: var(--border-subtle);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.user-avatar {
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 0;
}

.user-name {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  line-height: var(--leading-tight);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  line-height: var(--leading-tight);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-arrow {
  font-size: 12px;
  color: var(--text-quaternary);
  transition: transform var(--duration-fast) var(--ease-out);
}

.user-dropdown.is-opened .dropdown-arrow {
  transform: rotate(180deg);
}

.user-menu {
  width: 200px;
}

.user-menu-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-4);
  transition: all var(--duration-fast) var(--ease-out);
}

.user-menu-item:hover {
  background: var(--surface-tertiary);
}

.user-menu-item.logout {
  color: var(--semantic-error-600);
}

.user-menu-item.logout:hover {
  background: var(--semantic-error-50);
}

/* 页面内容 */
.page-content {
  flex: 1;
  overflow-y: auto;
  background: var(--surface-secondary);
}

.content-wrapper {
  padding: var(--spacing-6) var(--spacing-6) var(--spacing-6) 0;
  min-height: 100%;
}

/* 移动端遮罩 */
.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--surface-overlay);
  z-index: var(--z-modal-backdrop);
  backdrop-filter: blur(4px);
}

/* 动画效果 */
.logo-text-enter-active,
.logo-text-leave-active {
  transition: all var(--duration-normal) var(--ease-out);
}

.logo-text-enter-from,
.logo-text-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.page-enter-active,
.page-leave-active {
  transition: all var(--duration-normal) var(--ease-out);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modern-sidebar {
    transform: translateX(-100%);
  }
  
  .modern-sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .modern-header {
    padding: 0 var(--spacing-4);
  }
  
  .global-search {
    width: 200px;
  }
  
  .global-search:focus-within {
    width: 240px;
  }
  
  .user-info {
    display: none;
  }
  
  .content-wrapper {
    padding: var(--spacing-4) var(--spacing-4) var(--spacing-4) 0;
  }
}

@media (max-width: 640px) {
  .global-search {
    width: 160px;
  }
  
  .global-search:focus-within {
    width: 200px;
  }
  
  .search-container {
    order: 1;
    flex: 1;
    max-width: 200px;
  }
  
  .quick-actions {
    order: 2;
  }
}

/* 滚动条优化 */
.sidebar-navigation::-webkit-scrollbar {
  width: 4px;
}

.sidebar-navigation::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-navigation::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-full);
}

.sidebar-navigation::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
