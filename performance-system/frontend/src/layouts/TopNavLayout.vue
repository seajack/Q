<template>
  <div class="topnav-layout">
    <header class="topbar">
      <div class="topbar-inner" style="max-width: 1200px; margin: 0 auto; padding: 0 16px;">
        <div class="brand">
          <svg class="logo" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-label="Logo" role="img">
            <defs>
              <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" :stop-color="brand400" />
                <stop offset="100%" :stop-color="brand600" />
              </linearGradient>
            </defs>
            <rect x="2" y="2" width="20" height="20" rx="6" fill="url(#g)" />
            <path d="M7 13l3-3 3 3 4-4" fill="none" :stroke="brand700" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <span>绩效考核系统</span>
        </div>
        <div class="toolbar desktop-only">
          <div class="search">
            <input v-model.trim="keyword" placeholder="搜索员工、部门、指标…" class="input" />
            <span class="icon">🔍</span>
          </div>
        </div>
        <div class="toolbar">
          <select v-model="period" class="select">
            <option>2025 Q3</option><option>2025 Q2</option><option>2025 Q1</option><option>2024 Q4</option>
          </select>
          <RouterLink class="btn" to="/tasks">筛选</RouterLink>
          <!-- 通知中心 -->
          <NotificationCenter />
          <!-- 引导式操作流程 -->
          <GuidedWorkflow ref="guidedWorkflowRef" />
          <button class="btn btn-secondary" @click="startGuidedTour" title="开始引导">
            <span>🎯</span>
            引导
          </button>
          <button class="btn btn-primary" @click="onCreate">新增评审</button>
        </div>
      </div>
      <nav class="mainnav">
        <div class="mainnav-inner" style="max-width: 1200px; margin: 0 auto; padding: 0 16px;">
          <RouterLink class="link" to="/dashboard-new">首页</RouterLink>
          <RouterLink class="link" to="/dashboard-new">考核看板</RouterLink>
          <RouterLink class="link" to="/cycles">考核周期</RouterLink>
          <RouterLink class="link" to="/indicators">考核指标</RouterLink>
          <RouterLink class="link" to="/rules">考核规则</RouterLink>
          <RouterLink class="link" to="/tasks">考核任务</RouterLink>
          <RouterLink class="link" to="/manual-assignments">手动分配</RouterLink>
          <RouterLink class="link" to="/manual-evaluation">手动分配评分</RouterLink>
          <RouterLink class="link" to="/position-weights">职级权重配置</RouterLink>
          <RouterLink class="link" to="/employees">员工档案</RouterLink>
          <RouterLink class="link" to="/organization">组织架构</RouterLink>
          <RouterLink class="link" to="/results">报表中心</RouterLink>
          <RouterLink class="link" to="/settings">系统设置</RouterLink>
        </div>
      </nav>
    </header>

    <main style="width: 100%; padding: 24px 200px; flex: 1; overflow-y: auto; overflow-x: hidden;">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import NotificationCenter from '@/components/NotificationCenter.vue'
import GuidedWorkflow from '@/components/GuidedWorkflow.vue'
const period = ref('2025 Q3')
const keyword = ref('')
const guidedWorkflowRef = ref()
const onCreate = () => alert('打开新增评审弹窗（示意）')

// 手动触发引导
const startGuidedTour = () => {
  if (guidedWorkflowRef.value) {
    guidedWorkflowRef.value.startGuidedTour()
  }
}
const brand600 = computed(()=> getComputedStyle(document.documentElement).getPropertyValue('--brand-600').trim() || '#177fc1')
const brand400 = computed(()=> getComputedStyle(document.documentElement).getPropertyValue('--brand-400').trim() || '#59b6ea')
const brand700 = computed(()=> getComputedStyle(document.documentElement).getPropertyValue('--brand-700').trim() || '#115f96')
</script>

<style scoped>
.topnav-layout { 
  height: 100vh; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden;
}
.topbar { 
  position: sticky; 
  top: 0; 
  z-index: 40; 
  background: #fff; 
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.topbar-inner { height: 56px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.brand { display: flex; align-items: center; gap: 10px; font-weight: 700; color: #111; }
.brand .logo { height: 28px; width: 28px; }
.toolbar { display: flex; align-items: center; gap: 8px; }
.desktop-only { display: none; }
@media (min-width: 768px) { .desktop-only { display: flex; } }
.search { position: relative; }
.search .icon { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; }
.mainnav { 
  background: var(--brand-600); 
  color: #fff;
  flex-shrink: 0;
}
.mainnav-inner { height: 48px; display: flex; align-items: center; gap: 18px; overflow: auto; }
.link { color: #fff; text-decoration: none; font-size: 14px; white-space: nowrap; opacity: .95; }
.link.router-link-active { font-weight: 700; text-decoration: underline; }
</style>
