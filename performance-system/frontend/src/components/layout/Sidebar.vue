<template>
  <div class="sidebar w-64 p-6 flex flex-col" :class="sidebarClass">
    <!-- Logo区域 -->
    <div class="flex items-center mb-8">
      <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center mr-3 p-1">
        <img src="/logo.svg" alt="Logo" class="w-full h-full object-contain">
      </div>
      <div>
        <h1 class="text-lg font-bold text-gray-900">绩效考核系统</h1>
        <p class="text-sm text-gray-500">Performance System</p>
      </div>
    </div>
    
    <!-- 导航菜单 -->
    <nav class="flex-1">
      <div 
        v-for="item in menuItems" 
        :key="item.key"
        class="nav-item px-4 py-3 flex items-center cursor-pointer rounded-lg mb-1 transition-colors"
        :class="getNavItemClass(item)"
        @click="handleNavClick(item)"
      >
        <i :class="item.icon" class="mr-3"></i>
        <span>{{ item.label }}</span>
      </div>
    </nav>
    
    <!-- 用户信息 -->
    <div class="mt-auto">
      <div class="flex items-center p-3 rounded-lg bg-gray-200">
        <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center mr-3">
          <i class="fas fa-user text-white text-sm"></i>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">{{ userInfo.name }}</p>
          <p class="text-xs text-gray-500">{{ userInfo.email }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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

interface Props {
  menuItems: MenuItem[]
  userInfo: UserInfo
  currentPath?: string
  collapsed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  currentPath: '',
  collapsed: false
})

const emit = defineEmits<{
  navClick: [item: MenuItem]
}>()

const sidebarClass = computed(() => ({
  'bg-gradient-to-b from-gray-50 to-gray-100': true,
  'border-r border-gray-200': true
}))

const getNavItemClass = (item: MenuItem) => {
  const isActive = item.active || props.currentPath === item.path
  return {
    'bg-blue-50 text-blue-700': isActive,
    'text-gray-700 hover:bg-gray-100': !isActive
  }
}

const handleNavClick = (item: MenuItem) => {
  emit('navClick', item)
}
</script>

<style scoped>
.sidebar {
  background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
  border-right: 1px solid #e2e8f0;
}

.nav-item {
  transition: all 0.2s ease;
  border-radius: 8px;
  margin: 4px 0;
}

.nav-item:hover {
  background: rgba(37, 99, 235, 0.1);
}

.nav-item.active {
  background: #2563eb;
  color: white;
}
</style>
