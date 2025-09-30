<template>
  <div class="flex h-screen bg-gray-50">
    <!-- 侧边栏 -->
    <Sidebar 
      :menu-items="menuItems"
      :user-info="userInfo"
      :current-path="currentPath"
      @nav-click="handleNavClick"
    />
    
    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- 顶部导航 -->
      <Header 
        :title="pageTitle"
        :subtitle="pageSubtitle"
        :show-search="showSearch"
        :search-placeholder="searchPlaceholder"
        :filters="filters"
        :actions="actions"
        @search="handleSearch"
        @filter-change="handleFilterChange"
        @action-click="handleActionClick"
      />
      
      <!-- 主要内容 -->
      <main class="flex-1 overflow-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from '../components/layout/Sidebar.vue'
import Header from '../components/layout/Header.vue'

interface MenuItem {
  key: string
  label: string
  icon: string
  path?: string
  active?: boolean
}

interface UserInfo {
  name: string
  email: string
}

interface Filter {
  key: string
  placeholder: string
  options: Array<{ value: string; label: string }>
  value: string
}

interface Action {
  key: string
  label: string
  icon: string
  type: 'primary' | 'secondary' | 'danger'
  disabled?: boolean
}

interface Props {
  pageTitle: string
  pageSubtitle: string
  showSearch?: boolean
  searchPlaceholder?: string
  filters?: Filter[]
  actions?: Action[]
}

const props = withDefaults(defineProps<Props>(), {
  showSearch: false,
  searchPlaceholder: '搜索...',
  filters: () => [],
  actions: () => []
})

const emit = defineEmits<{
  search: [value: string]
  filterChange: [filter: Filter]
  actionClick: [action: Action]
  navClick: [item: MenuItem]
}>()

const router = useRouter()

// 菜单配置
const menuItems: MenuItem[] = [
  { key: 'dashboard', label: '仪表板', icon: 'fas fa-tachometer-alt', path: '/dashboard' },
  { key: 'cycles', label: '考核周期', icon: 'fas fa-calendar-alt', path: '/cycles' },
  { key: 'tasks', label: '考核任务', icon: 'fas fa-tasks', path: '/tasks' },
  { key: 'indicators', label: '考核指标', icon: 'fas fa-bullseye', path: '/indicators' },
  { key: 'evaluation', label: '评分管理', icon: 'fas fa-star', path: '/evaluation' },
  { key: 'results', label: '结果统计', icon: 'fas fa-chart-bar', path: '/results' },
  { key: 'employees', label: '员工管理', icon: 'fas fa-users', path: '/employees' },
  { key: 'multidimensional', label: '多维度评估', icon: 'fas fa-layer-group', path: '/multidimensional' },
  { key: 'settings', label: '系统设置', icon: 'fas fa-cog', path: '/settings' }
]

// 用户信息
const userInfo: UserInfo = {
  name: '管理员',
  email: 'admin@company.com'
}

const currentPath = computed(() => router.currentRoute.value.path)

const handleNavClick = (item: MenuItem) => {
  if (item.path) {
    router.push(item.path)
  }
  emit('navClick', item)
}

const handleSearch = (value: string) => {
  emit('search', value)
}

const handleFilterChange = (filter: Filter) => {
  emit('filterChange', filter)
}

const handleActionClick = (action: Action) => {
  emit('actionClick', action)
}
</script>

<style scoped>
/* 全局样式 */
</style>
