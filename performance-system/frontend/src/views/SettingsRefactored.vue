<template>
  <AppLayout
    page-title="系统设置"
    page-subtitle="配置系统参数和基础设置"
    :actions="headerActions"
    @action-click="handleHeaderAction"
  >
    <!-- 设置分类导航 -->
    <div class="mb-8">
      <div class="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        <button 
          v-for="tab in settingTabs" 
          :key="tab.key"
          class="flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors"
          :class="activeTab === tab.key ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
          @click="activeTab = tab.key"
        >
          <i :class="tab.icon" class="mr-2"></i>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- 基础信息设置 -->
    <div v-if="activeTab === 'basic'" class="space-y-6">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-6">基础信息</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">系统名称</label>
            <input 
              v-model="basic.name" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="绩效考核系统"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">默认周期</label>
            <select 
              v-model="basic.default_cycle" 
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">选择周期</option>
              <option v-for="cycle in cycles" :key="cycle.id" :value="cycle.id">
                {{ cycle.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">系统描述</label>
            <textarea 
              v-model="basic.description" 
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="系统功能描述"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">系统版本</label>
            <input 
              v-model="basic.version" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="v1.0.0"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 品牌与外观设置 -->
    <div v-if="activeTab === 'brand'" class="space-y-6">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-6">品牌与外观</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">主色调</label>
            <div class="flex space-x-2">
              <div 
                v-for="color in brandColors" 
                :key="color.name"
                class="w-12 h-12 rounded-lg cursor-pointer border-2 transition-all"
                :class="selectedBrandColor === color.name ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-300'"
                :style="{ backgroundColor: color.value }"
                @click="selectedBrandColor = color.name"
              ></div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">主题模式</label>
            <div class="flex space-x-2">
              <button 
                class="px-4 py-2 rounded-lg border transition-colors"
                :class="themeMode === 'light' ? 'bg-blue-100 border-blue-300 text-blue-700' : 'bg-gray-100 border-gray-300 text-gray-700'"
                @click="themeMode = 'light'"
              >
                浅色模式
              </button>
              <button 
                class="px-4 py-2 rounded-lg border transition-colors"
                :class="themeMode === 'dark' ? 'bg-blue-100 border-blue-300 text-blue-700' : 'bg-gray-100 border-gray-300 text-gray-700'"
                @click="themeMode = 'dark'"
              >
                深色模式
              </button>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">布局模式</label>
            <select 
              v-model="layoutMode" 
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="sidebar">侧边栏模式</option>
              <option value="top">顶部导航模式</option>
              <option value="compact">紧凑模式</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- 接口配置设置 -->
    <div v-if="activeTab === 'api'" class="space-y-6">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-6">接口配置</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">绩效API Base</label>
            <input 
              v-model="api.perf" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="http://127.0.0.1:8002"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">组织中台API Base</label>
            <input 
              v-model="api.org" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="http://127.0.0.1:8001/api"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">超时时间 (秒)</label>
            <input 
              v-model="api.timeout" 
              type="number" 
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="30"
            />
          </div>
          <div class="p-3 bg-blue-50 rounded-lg">
            <p class="text-sm text-blue-700">
              <i class="fas fa-info-circle mr-1"></i>
              说明：当前前端通过 Vite 代理访问 `/api` 与 `/org-api`，如需持久修改，请更新 `vite.config.ts`。
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 权限管理设置 -->
    <div v-if="activeTab === 'permissions'" class="space-y-6">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-6">权限管理</h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h4 class="font-medium text-gray-900">系统管理员权限</h4>
              <p class="text-sm text-gray-600">拥有系统最高权限</p>
            </div>
            <button class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors">
              配置权限
            </button>
          </div>
          <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h4 class="font-medium text-gray-900">部门经理权限</h4>
              <p class="text-sm text-gray-600">管理本部门考核事务</p>
            </div>
            <button class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors">
              配置权限
            </button>
          </div>
          <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h4 class="font-medium text-gray-900">HR专员权限</h4>
              <p class="text-sm text-gray-600">负责考核流程管理</p>
            </div>
            <button class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors">
              配置权限
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据管理设置 -->
    <div v-if="activeTab === 'data'" class="space-y-6">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-6">数据管理</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">数据备份频率</label>
            <select 
              v-model="data.backup_frequency" 
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="daily">每日</option>
              <option value="weekly">每周</option>
              <option value="monthly">每月</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">数据保留期限 (天)</label>
            <input 
              v-model="data.retention_days" 
              type="number" 
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="365"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">自动清理日志</label>
            <div class="flex items-center">
              <input 
                v-model="data.auto_clean_logs" 
                type="checkbox" 
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">启用自动清理</span>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">数据加密</label>
            <div class="flex items-center">
              <input 
                v-model="data.encryption_enabled" 
                type="checkbox" 
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">启用数据加密</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="flex justify-end space-x-4 mt-8">
      <button 
        class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        @click="handleReset"
      >
        重置
      </button>
      <button 
        class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        @click="handleSave"
      >
        保存设置
      </button>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AppLayout from '../layouts/AppLayout.vue'
import { settingsApi, cycleApi } from '../utils/api'

// 响应式数据
const activeTab = ref('basic')
const loading = ref(false)

// 设置分类
const settingTabs = ref([
  { key: 'basic', label: '基础信息', icon: 'fas fa-cog' },
  { key: 'brand', label: '品牌外观', icon: 'fas fa-palette' },
  { key: 'api', label: '接口配置', icon: 'fas fa-plug' },
  { key: 'permissions', label: '权限管理', icon: 'fas fa-shield-alt' },
  { key: 'data', label: '数据管理', icon: 'fas fa-database' }
])

// 基础信息
const basic = ref({
  name: '绩效考核系统',
  default_cycle: '',
  description: '',
  version: 'v1.0.0'
})

// 品牌设置
const selectedBrandColor = ref('blue')
const themeMode = ref('light')
const layoutMode = ref('sidebar')

const brandColors = ref([
  { name: 'blue', value: '#3b82f6' },
  { name: 'green', value: '#10b981' },
  { name: 'purple', value: '#8b5cf6' },
  { name: 'red', value: '#ef4444' },
  { name: 'orange', value: '#f59e0b' }
])

// 接口配置
const api = ref({
  perf: 'http://127.0.0.1:8002',
  org: 'http://127.0.0.1:8001/api',
  timeout: 30
})

// 数据管理
const data = ref({
  backup_frequency: 'daily',
  retention_days: 365,
  auto_clean_logs: true,
  encryption_enabled: true
})

// 其他数据
const cycles = ref([])

// 头部操作按钮
const headerActions = ref([
  {
    key: 'refresh',
    label: '刷新',
    icon: 'fas fa-sync-alt',
    type: 'secondary' as const
  },
  {
    key: 'export',
    label: '导出配置',
    icon: 'fas fa-download',
    type: 'primary' as const
  }
])

// 方法
const loadSettings = async () => {
  try {
    loading.value = true
    const response = await settingsApi.get()
    const settings = response.data
    
    // 更新设置数据
    if (settings.basic) {
      basic.value = { ...basic.value, ...settings.basic }
    }
    if (settings.api) {
      api.value = { ...api.value, ...settings.api }
    }
    if (settings.data) {
      data.value = { ...data.value, ...settings.data }
    }
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载设置失败')
  } finally {
    loading.value = false
  }
}

const loadCycles = async () => {
  try {
    const response = await cycleApi.list()
    cycles.value = response.data.results || []
  } catch (error) {
    console.error('加载考核周期失败:', error)
  }
}

const handleHeaderAction = (action: any) => {
  switch (action.key) {
    case 'refresh':
      loadSettings()
      break
    case 'export':
      handleExport()
      break
  }
}

const handleSave = async () => {
  try {
    loading.value = true
    const settings = {
      basic: basic.value,
      brand: {
        color: selectedBrandColor.value,
        theme: themeMode.value,
        layout: layoutMode.value
      },
      api: api.value,
      data: data.value
    }
    
    await settingsApi.update(settings)
    ElMessage.success('设置保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  ElMessage.info('重置功能开发中')
}

const handleExport = () => {
  console.log('导出系统配置')
  ElMessage.success('导出功能开发中')
}

// 生命周期
onMounted(() => {
  loadSettings()
  loadCycles()
})
</script>

<style scoped>
/* 自定义样式 */
</style>
