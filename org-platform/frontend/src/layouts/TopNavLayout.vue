<template>
  <div class="topnav-layout">
    <header class="topbar">
      <div class="brand" @click="go('/')">
        <span class="logo">OP</span>
        <span class="name">Org Platform</span>
      </div>
      <nav class="menu">
        <RouterLink to="/dashboard" class="item" :class="isActive('/dashboard')">仪表板</RouterLink>
        <RouterLink to="/departments" class="item" :class="isActive('/departments')">部门</RouterLink>
        <RouterLink to="/positions" class="item" :class="isActive('/positions')">职位</RouterLink>
        <RouterLink to="/employees" class="item" :class="isActive('/employees')">员工</RouterLink>
        <RouterLink to="/organization-tree" class="item" :class="isActive('/organization-tree')">组织架构</RouterLink>
        <RouterLink to="/position-templates" class="item" :class="isActive('/position-templates')">职位模板</RouterLink>
        <RouterLink to="/workflow-rules" class="item" :class="isActive('/workflow-rules')">工作流规则</RouterLink>
        <RouterLink to="/workflow-list" class="item" :class="isActive('/workflow-list')">工作流管理</RouterLink>
        <RouterLink to="/intelligent-analysis" class="item" :class="isActive('/intelligent-analysis')">智能分析</RouterLink>
        <RouterLink to="/dictionaries" class="item" :class="isActive('/dictionaries')">数据字典</RouterLink>
        <RouterLink to="/configs" class="item" :class="isActive('/configs')">系统配置</RouterLink>
        <RouterLink to="/integration-management" class="item" :class="isActive('/integration-management')">集成管理</RouterLink>
        <RouterLink to="/permission-management" class="item" :class="isActive('/permission-management')">权限管理</RouterLink>
        <RouterLink to="/tenant-management" class="item" :class="isActive('/tenant-management')">多租户管理</RouterLink>
      </nav>
      <div class="spacer" />
      <div class="actions">
        <el-input v-model="q" size="small" placeholder="搜索..." @keyup.enter="onSearch" style="width:200px" />
        <el-tooltip :content="themeStore.isDark() ? '切换到浅色模式' : '切换到深色模式'" placement="bottom">
          <div class="theme-toggle" @click="themeStore.toggleTheme()">
            <el-icon v-if="themeStore.isDark()"><Sunny /></el-icon>
            <el-icon v-else><Moon /></el-icon>
          </div>
        </el-tooltip>
      </div>
    </header>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { Sunny, Moon } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const q = ref('')
const themeStore = useThemeStore()

const isActive = (path:string) => route.path.startsWith(path) ? 'active' : ''
const go = (path:string) => router.push(path)
const onSearch = () => {
  if (!q.value) return
  // 这里预留搜索路由或弹窗
}
</script>

<style scoped>
.topnav-layout { 
  height: 100vh; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden;
}
.topbar {
  position: sticky; top: 0; z-index: 50;
  display: flex; align-items: center; gap: 16px;
  padding: 10px 16px; 
  background: var(--header-bg); 
  color: var(--header-text); 
  border-bottom: 1px solid var(--header-border);
  flex-shrink: 0;
  transition: background-color 0.3s, color 0.3s, border-color 0.3s;
}
.brand { display:flex; align-items:center; gap:10px; cursor:pointer; }
.logo { display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; border-radius:6px; background:var(--brand); color:#0b1220; font-weight:800; }
.name { font-weight: 700; letter-spacing: .2px; color: var(--header-text); }
.menu { display:flex; gap: 8px; margin-left: 8px; flex-wrap: wrap; }
.item { color:var(--muted); text-decoration:none; padding:6px 10px; border-radius:8px; font-size:13px; transition: all .2s; }
.item:hover { color:var(--menu-hover-text); background: var(--menu-hover-bg); }
.item.active { color:var(--menu-active-text); background:var(--menu-active-bg); }
.spacer { flex:1; }
.actions { display:flex; align-items:center; gap:12px; }
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--menu-hover-bg);
  color: var(--text);
  cursor: pointer;
  transition: all 0.3s;
}
.theme-toggle:hover {
  background: var(--brand);
  color: white;
  transform: rotate(30deg);
}
.content { 
  flex: 1; 
  padding: 16px; 
  background: var(--bg); 
  overflow-y: auto;
  overflow-x: hidden;
  transition: background-color 0.3s;
}

/* 内容卡片样式 */
:deep(.card) { 
  background: var(--card-bg); 
  border: 1px solid var(--border); 
  border-radius: 12px; 
  overflow: hidden;
  transition: background-color 0.3s, border-color 0.3s;
}
:deep(.row) { display:flex; align-items:center; justify-content:space-between; }
:deep(.toolbar) { display:flex; align-items:center; gap:8px; flex-wrap: wrap; }
:deep(h3) { color: var(--text); transition: color 0.3s; }
</style>
