<template>
  <div class="container">
    <!-- 页面头部 -->
    <div class="header">
      <div class="header-title">
        <span class="header-icon">🏢</span>
        组织架构管理
      </div>
      <div class="header-actions">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input 
            v-model="keyword" 
            type="text" 
            class="search-input" 
            placeholder="搜索部门或员工..."
            @keyup.enter="reload"
          >
        </div>
        <button class="btn btn-secondary">
          <span>📊</span>
          统计
        </button>
        <button class="btn btn-primary">
          <span>⚙️</span>
          设置
        </button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-grid">
      <!-- 左侧部门树 -->
      <div class="tree-panel">
        <div class="tree-header">
          <div class="tree-title">
            <span class="tree-icon">🌳</span>
            部门树
        </div>
          <div class="tree-actions">
            <button class="btn btn-secondary" style="padding: var(--space-2);" @click="expandAll">
              <span>📂</span>
            </button>
            <button class="btn btn-secondary" style="padding: var(--space-2);">
              <span>📁</span>
            </button>
          </div>
        </div>
        <div class="tree-content">
          <el-tree
            :data="deptTree"
            node-key="id"
            :props="{ label:'name', children:'children' }"
            :default-expanded-keys="expandedKeys"
            highlight-current
            @node-click="onNodeClick"
            class="enhanced-tree"
          >
            <template #default="{ node, data }">
              <div 
                class="tree-node-content" 
                :class="{ 'selected': currentDept?.id === data.id }"
                :data-level="node.level"
                :data-type="data.type"
              >
                <div class="tree-node-icon">
                  <span v-if="data.type === 'department'">🏢</span>
                  <span v-else-if="data.type === 'employee'">👤</span>
                  <span v-else>📁</span>
                </div>
                <div class="tree-node-info">
                  <div class="tree-node-name">{{ data.name }}</div>
                  <div class="tree-node-meta" v-if="data.type === 'department'">
                    <span v-if="data.children?.length">{{ data.children.filter((child: any) => child.type === 'department').length }}个子部门</span>
                    <span v-if="data.children?.length && data.employee_count">•</span>
                    <span>{{ data.employee_count || 0 }}人</span>
                  </div>
                  <div class="tree-node-meta" v-else-if="data.type === 'employee'">
                    <span>{{ data.position_name || '未分配' }}</span>
                    <span v-if="data.position_level" class="position-level">L{{ data.position_level }}</span>
                  </div>
                </div>
                <div class="tree-node-badge" v-if="data.type === 'department'">
                  <span class="badge badge-primary">{{ data.employee_count || 0 }}人</span>
                </div>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 右侧成员列表 -->
      <div class="members-panel">
        <div class="members-header">
          <div class="members-title">
            <span class="members-icon">👥</span>
            成员列表
            <span class="badge badge-primary">{{ total }}人</span>
                    </div>
          <div class="tree-actions">
            <button class="btn btn-secondary" style="padding: var(--space-2);">
              <span>🔍</span>
            </button>
            <button class="btn btn-secondary" style="padding: var(--space-2);">
              <span>⬇️</span>
            </button>
                  </div>
                </div>
        <div class="members-content" v-loading="loading">
          
          <div 
            v-for="row in rows" 
            :key="row.id" 
            class="employee-card"
          >
            <div class="employee-avatar">{{ (row.name||'?')[0] }}</div>
            <div class="employee-info">
              <div class="employee-name">{{ row.name }}</div>
              <div class="employee-position">
                <span class="status-indicator" :class="getStatusClass(row.status)"></span>
                <span>{{ row.position_name || '未分配' }}</span>
                <span v-if="row.position_level" class="badge badge-primary">L{{ row.position_level }}</span>
        </div>
              <div class="employee-contact" v-if="row.email || row.phone">
                <div class="contact-item" v-if="row.email">
                  <span>📧</span>
                  <span>{{ row.email }}</span>
                </div>
                <div class="contact-item" v-if="row.phone">
                  <span>📞</span>
                  <span>{{ row.phone }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="pagination-wrapper">
          <el-pagination
            background
            layout="prev, pager, next"
            :current-page="page"
            :page-size="size"
            :total="total"
            @current-change="onPageChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { orgPlatformApi } from '@/utils/api'

const loading = ref(false)
const rows = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const size = ref(10)

const keyword = ref('')
const status = ref('')

const deptTree = ref<any[]>([])
const expandedKeys = ref<any[]>([])
const currentDept = ref<any>(null)

const loadTree = async () => {
  try {
    console.log('正在加载组织架构树...')
    const res = await orgPlatformApi.departments.fullTree()
    console.log('API响应:', res)
    
    // 处理不同的数据格式
    let data: any[] = []
    if (Array.isArray(res.data)) {
      data = res.data
    } else if (res.data && Array.isArray((res.data as any).results)) {
      data = (res.data as any).results
    } else if (res.data && Array.isArray((res.data as any).data)) {
      data = (res.data as any).data
    }
    
    console.log('解析后的数据:', data)
    console.log('数据类型:', typeof data, '是否为数组:', Array.isArray(data))
    
    if (data && data.length > 0) {
      deptTree.value = data
      expandedKeys.value = data.map((n: any) => n.id)
      console.log('组织架构树加载完成，节点数:', data.length)
    } else {
      console.warn('没有获取到组织架构数据')
      deptTree.value = []
      expandedKeys.value = []
    }
  } catch(e) { 
    console.error('加载组织架构树失败:', e)
    // 如果fullTree失败，尝试使用普通的tree API
    try {
      console.log('尝试使用普通tree API...')
      const res = await orgPlatformApi.departments.tree()
      let data: any[] = []
      if (Array.isArray(res.data)) {
        data = res.data
      } else if (res.data && Array.isArray((res.data as any).results)) {
        data = (res.data as any).results
      }
      deptTree.value = data
      expandedKeys.value = data.map((n: any) => n.id)
      console.log('使用普通tree API成功，节点数:', data.length)
    } catch(e2) {
      console.error('普通tree API也失败:', e2)
      deptTree.value = []
      expandedKeys.value = []
    }
  }
}

const loadList = async () => {
  try {
    loading.value = true
    const params:any = { page: page.value, size: size.value }
    if (keyword.value) params.search = keyword.value
    if (status.value) params.status = status.value
    if (currentDept.value?.id) params.department_id = currentDept.value.id
    const res = await orgPlatformApi.employees.list(params)
    const data:any = res.data
    rows.value = data.results || data || []
    total.value = data.count ?? rows.value.length
  } finally {
    loading.value = false
  }
}

const reload = () => { page.value = 1; loadList() }
const onNodeClick = (node:any) => { 
  // 只有部门节点才能被选择
  if (node?.type === 'department') {
    currentDept.value = node; 
    reload() 
  }
}
const onPageChange = (p:number) => { page.value = p; loadList() }

const expandAll = () => { expandedKeys.value = collectIds(deptTree.value) }
const collectIds = (arr:any[]):any[] => arr.flatMap(n => [n.id, ...(n.children?collectIds(n.children):[])])

const statusText = (s:string)=> ({active:'在职', probation:'试用', inactive:'离职'} as any)[s] || s
const statusType = (s:string)=> ({active:'success', probation:'warning', inactive:'info'} as any)[s] || 'info'

const getStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '',
    probation: 'away',
    inactive: 'offline',
    leave: 'away'
  }
  return statusMap[status] || ''
}

onMounted(async () => { await loadTree(); await loadList(); })
</script>

<style scoped>
/* 导入美化主题 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* CSS变量定义 */
:root {
  /* 主色调 */
  --primary: #3b82f6;
  --primary-light: #60a5fa;
  --primary-dark: #1d4ed8;
  --primary-bg: #eff6ff;
  
  /* 辅助色 */
  --secondary: #64748b;
  --secondary-light: #94a3b8;
  --secondary-bg: #f8fafc;
  
  /* 成功色 */
  --success: #10b981;
  --success-light: #34d399;
  --success-bg: #ecfdf5;
  
  /* 警告色 */
  --warning: #f59e0b;
  --warning-light: #fbbf24;
  --warning-bg: #fffbeb;
  
  /* 危险色 */
  --danger: #ef4444;
  --danger-light: #f87171;
  --danger-bg: #fef2f2;
  
  /* 中性色 */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  
  /* 背景色 */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  
  /* 文字色 */
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;
  --text-inverse: #ffffff;
  
  /* 边框色 */
  --border-light: #e5e7eb;
  --border-medium: #d1d5db;
  --border-dark: #9ca3af;
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  
  /* 圆角 */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  
  /* 间距 */
  --space-1: 0.125rem;
  --space-2: 0.25rem;
  --space-3: 0.375rem;
  --space-4: 0.5rem;
  --space-5: 0.75rem;
  --space-6: 1rem;
  --space-8: 1.25rem;
  --space-10: 1.5rem;
  --space-12: 2rem;
  
  /* 字体 */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  
  /* 过渡动画 */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 250ms ease-in-out;
  --transition-slow: 350ms ease-in-out;
}

/* 基础样式重置 */
* {
  box-sizing: border-box;
}

.container {
  max-width: 1400px !important;
  margin: 0 auto !important;
  padding: 24px !important;
  background: #f8fafc !important;
  min-height: 100vh !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  font-size: 14px !important;
  line-height: 1.6 !important;
}

/* 确保所有元素都使用我们的字体 */
.container * {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}


/* 强制应用我们的卡片样式 */
.tree-panel,
.members-panel {
  background: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1) !important;
}

/* 强制应用我们的颜色系统 */
.container {
  --el-color-primary: var(--primary) !important;
  --el-color-primary-light-3: var(--primary-light) !important;
  --el-color-primary-light-5: var(--primary-bg) !important;
  --el-color-primary-light-7: var(--primary-bg) !important;
  --el-color-primary-light-8: var(--primary-bg) !important;
  --el-color-primary-light-9: var(--primary-bg) !important;
  --el-text-color-primary: var(--text-primary) !important;
  --el-text-color-regular: var(--text-secondary) !important;
  --el-text-color-secondary: var(--text-tertiary) !important;
  --el-border-color: var(--border-light) !important;
  --el-border-color-light: var(--border-medium) !important;
  --el-border-color-lighter: var(--border-light) !important;
  --el-fill-color: var(--bg-primary) !important;
  --el-fill-color-light: var(--bg-secondary) !important;
  --el-fill-color-lighter: var(--bg-tertiary) !important;
}

/* 强制应用我们的按钮样式 */
.btn {
  background: var(--secondary-bg) !important;
  color: var(--secondary) !important;
  border: 1px solid var(--border-medium) !important;
  border-radius: var(--radius-md) !important;
  padding: var(--space-2) var(--space-3) !important;
  font-size: 0.75rem !important;
  font-weight: 500 !important;
  cursor: pointer !important;
  transition: all var(--transition-fast) !important;
}

.btn:hover {
  background: var(--gray-100) !important;
  border-color: var(--border-dark) !important;
  transform: translateY(-1px) !important;
}

.btn-primary {
  background: var(--primary) !important;
  color: var(--text-inverse) !important;
  border-color: var(--primary) !important;
}

.btn-primary:hover {
  background: var(--primary-dark) !important;
  border-color: var(--primary-dark) !important;
}

/* 页面头部 */
.header {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  margin-bottom: 24px !important;
  padding: 16px 24px !important;
  background: #ffffff !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1) !important;
  border: 1px solid #e5e7eb !important;
}

.header-title {
  display: flex !important;
  align-items: center !important;
  gap: var(--space-2) !important;
  font-size: 1.25rem !important;
  font-weight: 700 !important;
  color: var(--text-primary) !important;
}

.header-icon {
  font-size: 1.5rem !important;
}

.header-actions {
  display: flex !important;
  align-items: center !important;
  gap: var(--space-4) !important;
}

.search-box {
  position: relative !important;
  width: 300px !important;
}

.search-input {
  width: 100% !important;
  padding: 6px 12px 6px 28px !important;
  border: 1px solid #d1d5db !important;
  border-radius: 6px !important;
  font-size: 12px !important;
  background: #f9fafb !important;
  transition: all 150ms ease-in-out !important;
}

.search-input:focus {
  outline: none !important;
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1) !important;
}

.search-icon {
  position: absolute !important;
  left: 8px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  color: #9ca3af !important;
  font-size: 14px !important;
}

/* 按钮样式 - 强制覆盖 */
.btn {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 6px !important;
  padding: 6px 12px !important;
  border: 1px solid #d1d5db !important;
  border-radius: 6px !important;
  font-weight: 500 !important;
  font-size: 12px !important;
  cursor: pointer !important;
  transition: all 150ms ease-in-out !important;
  text-decoration: none !important;
  background: #f8fafc !important;
  color: #64748b !important;
  min-height: 28px !important;
}

.btn-primary {
  background: #3b82f6 !important;
  color: #ffffff !important;
  border-color: #3b82f6 !important;
}

.btn-primary:hover {
  background: #1d4ed8 !important;
  border-color: #1d4ed8 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1) !important;
}

.btn-secondary {
  background: #f8fafc !important;
  color: #64748b !important;
  border: 1px solid #d1d5db !important;
}

.btn-secondary:hover {
  background: #f3f4f6 !important;
  border-color: #9ca3af !important;
  transform: translateY(-1px) !important;
}

/* 主网格布局 - 强制覆盖 */
.main-grid {
  display: grid !important;
  grid-template-columns: 350px 1fr !important;
  gap: 16px !important;
  height: calc(100vh - 200px) !important;
  width: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
  background: #f8fafc !important;
}

/* 树面板 - 强制覆盖 */
.tree-panel {
  background: #ffffff !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1) !important;
  border: 1px solid #e5e7eb !important;
  overflow: hidden !important;
  width: 100% !important;
  height: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
}

.tree-header {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding: var(--space-3) var(--space-4) !important;
  border-bottom: 1px solid var(--border-light) !important;
  background: var(--bg-tertiary) !important;
}

.tree-title {
  display: flex !important;
  align-items: center !important;
  gap: var(--space-2) !important;
  font-weight: 600 !important;
  color: var(--text-primary) !important;
}

.tree-icon {
  font-size: 1.25rem !important;
}

.members-icon {
  font-size: 1.25rem !important;
}

.tree-actions {
  display: flex !important;
  gap: var(--space-2) !important;
}

.tree-content {
  padding: var(--space-3) !important;
  max-height: calc(100vh - 300px) !important;
  overflow-y: auto !important;
}

/* 树节点样式 - 强制覆盖Element Plus样式 */
:deep(.el-tree) {
  width: 100% !important;
  background: transparent !important;
  font-size: 14px !important;
  padding: 0 !important;
}

:deep(.el-tree-node) {
  margin-bottom: 4px !important;
}

:deep(.el-tree-node__content) {
  width: 100% !important;
  min-height: auto !important;
  padding: 0 !important;
  margin-bottom: 0 !important;
  border: none !important;
  background: transparent !important;
  height: auto !important;
  line-height: normal !important;
}

:deep(.el-tree-node__expand-icon) {
  margin-right: 8px !important;
  color: #6b7280 !important;
  font-size: 12px !important;
}

:deep(.el-tree-node__expand-icon:hover) {
  color: #3b82f6 !important;
}

:deep(.el-tree-node__content:hover) {
  background: transparent !important;
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: transparent !important;
  color: inherit !important;
}

:deep(.el-tree-node__label) {
  width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
  background: transparent !important;
}

/* 强制覆盖Element Plus树组件的所有样式 */
:deep(.el-tree-node__content > .el-tree-node__expand-icon) {
  padding: 0 !important;
  margin: 0 !important;
  margin-right: 8px !important;
}

:deep(.el-tree-node__content > .el-tree-node__label) {
  flex: 1 !important;
  width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* 确保我们的自定义内容能正确显示 */
:deep(.el-tree-node__content) {
  display: flex !important;
  align-items: center !important;
  width: 100% !important;
}

/* 隐藏Element Plus的默认标签 */
:deep(.el-tree-node__content > .el-tree-node__label > span) {
  display: none !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content) {
  position: relative !important;
  height: auto !important;
  min-height: 40px !important;
}

:deep(.el-tree-node__content .tree-node-content) {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
  background: transparent !important;
}

/* 确保树节点内容正确显示 */
:deep(.el-tree-node__content) {
  display: block !important;
  width: 100% !important;
  height: auto !important;
  min-height: 40px !important;
  padding: 0 !important;
  margin: 0 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

/* 完全重置Element Plus树组件样式 */
:deep(.el-tree) {
  background: transparent !important;
  font-size: 14px !important;
}

:deep(.el-tree-node) {
  margin-bottom: 4px !important;
}

:deep(.el-tree-node__content) {
  width: 100% !important;
  height: auto !important;
  min-height: 40px !important;
  padding: 0 !important;
  margin: 0 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  position: relative !important;
  display: block !important;
}

:deep(.el-tree-node__expand-icon) {
  display: none !important;
}

:deep(.el-tree-node__label) {
  display: none !important;
}

/* 显示我们的自定义内容 */
.tree-node-content {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 12px 16px !important;
  border-radius: 8px !important;
  cursor: pointer !important;
  transition: all 150ms ease-in-out !important;
  border: 1px solid transparent !important;
  margin-bottom: 14px !important;
  width: 100% !important;
  min-height: 48px !important;
  background: #ffffff !important;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05) !important;
}

/* 树节点层级缩进 */
:deep(.el-tree-node) {
  margin-bottom: 16px !important;
}

:deep(.el-tree-node__children) {
  margin-left: 20px !important;
  border-left: 1px solid #e5e7eb !important;
  padding-left: 16px !important;
  margin-top: 8px !important;
}

/* 员工节点与部门节点的间距 */
:deep(.el-tree-node[data-type="employee"]) {
  margin-top: 12px !important;
  margin-bottom: 8px !important;
}

/* 根据层级和类型设置不同的缩进和样式 */
.tree-node-content[data-level="1"] {
  margin-left: 0 !important;
  background: #ffffff !important;
  border-left: 3px solid #3b82f6 !important;
}

.tree-node-content[data-level="2"] {
  margin-left: 20px !important;
  background: #f8fafc !important;
  border-left: 3px solid #10b981 !important;
}

.tree-node-content[data-level="3"] {
  margin-left: 40px !important;
  background: #f1f5f9 !important;
  border-left: 3px solid #f59e0b !important;
}

.tree-node-content[data-level="4"] {
  margin-left: 60px !important;
  background: #f0f9ff !important;
  border-left: 3px solid #8b5cf6 !important;
}

/* 员工节点特殊样式 */
.tree-node-content[data-type="employee"] {
  background: #ffffff !important;
  border-left: 1px solid #e5e7eb !important;
  font-style: normal !important;
  margin-top: 8px !important;
  margin-bottom: 6px !important;
}

.tree-node-content[data-type="employee"] .tree-node-icon {
  opacity: 0.8 !important;
}

/* 员工节点相对于部门的缩进减少 */
.tree-node-content[data-type="employee"][data-level="2"] {
  margin-left: 12px !important;
}

.tree-node-content[data-type="employee"][data-level="3"] {
  margin-left: 24px !important;
}

.tree-node-content[data-type="employee"][data-level="4"] {
  margin-left: 36px !important;
}

/* 部门节点样式 */
.tree-node-content[data-type="department"] {
  font-weight: 600 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}

/* 强制显示我们的自定义内容 */
:deep(.el-tree-node__content .tree-node-content) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 10 !important;
}


.tree-node-content:hover {
  background: #eff6ff !important;
  border-color: #3b82f6 !important;
  transform: translateX(4px) !important;
}

.tree-node-content.selected {
  background: #eff6ff !important;
  border-color: #3b82f6 !important;
  border-left: 3px solid #3b82f6 !important;
}

.tree-node-icon {
  font-size: 16px !important;
  opacity: 0.8 !important;
  width: 20px !important;
  text-align: center !important;
  flex-shrink: 0 !important;
}

.tree-node-info {
  flex: 1 !important;
  min-width: 0 !important;
}

.tree-node-name {
  font-weight: 500 !important;
  color: #1f2937 !important;
  margin-bottom: 2px !important;
  font-size: 14px !important;
  line-height: 1.4 !important;
}

.tree-node-meta {
  font-size: 10px !important;
  color: #6b7280 !important;
  display: flex !important;
  align-items: center !important;
  gap: 4px !important;
  line-height: 1.4 !important;
}

.tree-node-badge {
  margin-left: auto !important;
  flex-shrink: 0 !important;
}

/* 标签样式 */
.badge {
  display: inline-flex !important;
  align-items: center !important;
  padding: 2px 6px !important;
  border-radius: 4px !important;
  font-size: 10px !important;
  font-weight: 500 !important;
  white-space: nowrap !important;
}

.badge-primary {
  background: #eff6ff !important;
  color: #3b82f6 !important;
}

.badge-success {
  background: #ecfdf5 !important;
  color: #10b981 !important;
}

.badge-warning {
  background: #fffbeb !important;
  color: #f59e0b !important;
}

/* 成员面板 - 强制覆盖 */
.members-panel {
  background: #ffffff !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1) !important;
  border: 1px solid #e5e7eb !important;
  overflow: hidden !important;
  width: 100% !important;
  height: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
}

.members-header {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding: var(--space-3) var(--space-4) !important;
  border-bottom: 1px solid var(--border-light) !important;
  background: var(--bg-tertiary) !important;
}

.members-title {
  display: flex !important;
  align-items: center !important;
  gap: var(--space-2) !important;
  font-weight: 600 !important;
  color: var(--text-primary) !important;
}

.members-content {
  padding: var(--space-3) !important;
  max-height: calc(100vh - 300px) !important;
  overflow-y: auto !important;
}

/* 员工卡片 - 强制覆盖 */
.employee-card {
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  padding: 12px !important;
  margin-bottom: 8px !important;
  background: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 12px !important;
  transition: all 250ms ease-in-out !important;
  min-height: 80px !important;
}

.employee-card:hover {
  border-color: #3b82f6 !important;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1) !important;
  transform: translateY(-2px) !important;
}

.employee-avatar {
  width: 40px !important;
  height: 40px !important;
  border-radius: 50% !important;
  background: linear-gradient(135deg, #3b82f6, #60a5fa) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  color: white !important;
  font-weight: 600 !important;
  font-size: 16px !important;
  flex-shrink: 0 !important;
}

.employee-info {
  flex: 1 !important;
  min-width: 0 !important;
}

.employee-name {
  font-weight: 600 !important;
  color: #1f2937 !important;
  margin-bottom: 4px !important;
  font-size: 14px !important;
  line-height: 1.4 !important;
}

.employee-position {
  font-size: 12px !important;
  color: #6b7280 !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  margin-bottom: 6px !important;
  line-height: 1.4 !important;
}

.employee-contact {
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  font-size: 10px !important;
  color: #9ca3af !important;
  line-height: 1.4 !important;
}

.contact-item {
  display: flex !important;
  align-items: center !important;
  gap: 4px !important;
  font-size: 10px !important;
  color: #9ca3af !important;
}

.status-indicator {
  width: 6px !important;
  height: 6px !important;
  border-radius: 50% !important;
  background: #10b981 !important;
  margin-right: 6px !important;
  flex-shrink: 0 !important;
}

.status-indicator.away {
  background: #f59e0b !important;
}

.status-indicator.offline {
  background: #9ca3af !important;
}

.position-level {
  color: #3b82f6 !important;
  font-weight: 600 !important;
  background: #eff6ff !important;
  padding: 2px 6px !important;
  border-radius: 4px !important;
  margin-left: 4px !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  font-size: 10px !important;
}

.pagination-wrapper {
  padding: 12px 16px !important;
  border-top: 1px solid #e5e7eb !important;
  background: #f1f5f9 !important;
}

/* 滚动条样式 */
.tree-content::-webkit-scrollbar,
.members-content::-webkit-scrollbar {
  width: 6px;
}

.tree-content::-webkit-scrollbar-track,
.members-content::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 3px;
}

.tree-content::-webkit-scrollbar-thumb,
.members-content::-webkit-scrollbar-thumb {
  background: var(--border-medium);
  border-radius: 3px;
}

.tree-content::-webkit-scrollbar-thumb:hover,
.members-content::-webkit-scrollbar-thumb:hover {
  background: var(--border-dark);
}

/* 强制覆盖Element Plus样式 */
:deep(.el-select) {
  width: 120px !important;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border-medium) !important;
  box-shadow: none !important;
  background: var(--bg-primary) !important;
  height: 32px !important;
}

:deep(.el-select .el-input__wrapper:hover) {
  border-color: var(--primary) !important;
}

:deep(.el-select .el-input__wrapper.is-focus) {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1) !important;
}

:deep(.el-pagination) {
  justify-content: center !important;
}

:deep(.el-pagination .el-pager li) {
  border-radius: var(--radius-sm) !important;
  margin: 0 2px !important;
}

:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next) {
  border-radius: var(--radius-sm) !important;
}

/* 强制应用我们的颜色系统 */
:deep(.el-loading-mask) {
  background-color: rgba(255, 255, 255, 0.8) !important;
}

:deep(.el-loading-spinner) {
  color: var(--primary) !important;
}

/* 强制覆盖所有Element Plus组件 */
:deep(.el-button) {
  border-radius: var(--radius-md) !important;
  font-weight: 500 !important;
  font-size: 0.75rem !important;
}

:deep(.el-input) {
  border-radius: var(--radius-md) !important;
}

:deep(.el-input__wrapper) {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border-medium) !important;
  box-shadow: none !important;
  background: var(--bg-primary) !important;
}

:deep(.el-input__wrapper:hover) {
  border-color: var(--primary) !important;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1) !important;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }
  
  .tree-panel {
    order: 2;
  }
  
  .members-panel {
    order: 1;
  }
}

@media (max-width: 768px) {
  .container {
    padding: var(--space-4);
  }
  
  .header {
    flex-direction: column;
    gap: var(--space-4);
    align-items: stretch;
  }
  
  .search-box {
    width: 100%;
  }
  
  .main-grid {
    height: auto;
  }
}
</style>
