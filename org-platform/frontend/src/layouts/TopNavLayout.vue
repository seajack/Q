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
        <RouterLink to="/dictionaries" class="item" :class="isActive('/dictionaries')">数据字典</RouterLink>
        <RouterLink to="/configs" class="item" :class="isActive('/configs')">系统配置</RouterLink>
        <RouterLink to="/integration-management" class="item" :class="isActive('/integration-management')">集成管理</RouterLink>
        <RouterLink to="/permission-management" class="item" :class="isActive('/permission-management')">权限管理</RouterLink>
      </nav>
      <div class="spacer" />
      <div class="actions">
        <el-input v-model="q" size="small" placeholder="搜索..." @keyup.enter="onSearch" style="width:200px" />
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

const route = useRoute()
const router = useRouter()
const q = ref('')

const isActive = (path:string) => route.path.startsWith(path) ? 'active' : ''
const go = (path:string) => router.push(path)
const onSearch = () => {
  if (!q.value) return
  // 这里预留搜索路由或弹窗
}
</script>

<style scoped>
.topnav-layout { min-height: 100vh; display: flex; flex-direction: column; }
.topbar {
  position: sticky; top: 0; z-index: 50;
  display: flex; align-items: center; gap: 16px;
  padding: 10px 16px; background: #ffffff; color: #111827; border-bottom: 1px solid #e5e7eb;
}
.brand { display:flex; align-items:center; gap:10px; cursor:pointer; }
.logo { display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; border-radius:6px; background:#22c55e; color:#0b1220; font-weight:800; }
.name { font-weight: 700; letter-spacing: .2px; }
.menu { display:flex; gap: 8px; margin-left: 8px; flex-wrap: wrap; }
.item { color:#374151; text-decoration:none; padding:6px 10px; border-radius:8px; font-size:13px; transition: all .2s; }
.item:hover { color:#111827; background: #f3f4f6; }
.item.active { color:#0b1220; background:#22c55e; }
.spacer { flex:1; }
.actions { display:flex; align-items:center; gap:8px; }
.content { flex:1; padding: 16px; background:#ffffff; }

/* 内容卡片背景统一浅色 */
:deep(.card) { background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; overflow:hidden; }
:deep(.row) { display:flex; align-items:center; justify-content:space-between; }
:deep(.toolbar) { display:flex; align-items:center; gap:8px; flex-wrap: wrap; }
:deep(h3) { color:#111827; }
</style>
