<template>
  <header class="topbar">
    <div class="container topbar-inner">
      <div class="brand">
        <img src="/logo.png" alt="Logo" />
        <span>绩效考核系统</span>
      </div>
      <div class="toolbar desktop-only">
        <div class="search">
          <input v-model.trim="perf.keyword" placeholder="搜索员工、部门、指标…" class="input" />
          <span class="icon">🔍</span>
        </div>
      </div>
      <div class="toolbar">
        <select v-model="perf.period" class="select">
          <option>2025 Q3</option>
          <option>2025 Q2</option>
          <option>2025 Q1</option>
          <option>2024 Q4</option>
        </select>
        <RouterLink class="btn" to="/tasks">筛选</RouterLink>
        <button class="btn btn-primary" @click="$emit('create')">新增评审</button>
      </div>
    </div>
    <nav class="mainnav">
      <div class="container mainnav-inner">
        <RouterLink class="link" to="/">首页</RouterLink>
        <RouterLink class="link" to="/dashboard">考核看板</RouterLink>
        <RouterLink class="link" to="/tasks">评审任务</RouterLink>
        <RouterLink class="link" to="/kpi">KPI指标</RouterLink>
        <RouterLink class="link" to="/files">员工档案</RouterLink>
        <RouterLink class="link" to="/org">组织架构</RouterLink>
        <RouterLink class="link" to="/reports">报表中心</RouterLink>
        <RouterLink class="link" to="/settings">系统设置</RouterLink>
      </div>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { watch } from 'vue';
import { usePerfStore } from '../stores/perf';

const store = usePerfStore();
const perf = storeToRefs(store);

// Watch period change -> reload KPI/Charts/List
watch(perf.period, () => {
  store.page = 1;
  store.initLoad();
});

// Debounce search keyword -> reload list
let t: any;
watch(perf.keyword, () => {
  clearTimeout(t);
  t = setTimeout(() => { store.page = 1; store.loadList(); }, 300);
});
</script>

<style scoped>
.topbar { position: sticky; top: 0; z-index: 40; background: #fff; border-bottom: 1px solid var(--border); }
.topbar-inner { height: 56px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.brand { display: flex; align-items: center; gap: 10px; font-weight: 700; color: #111; }
.brand img { height: 32px; width: auto; }
.toolbar { display: flex; align-items: center; gap: 8px; }
.desktop-only { display: none; }
@media (min-width: 768px) { .desktop-only { display: flex; } }
.search { position: relative; }
.search .icon { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; }

.mainnav { background: var(--brand-600); color: #fff; }
.mainnav-inner { height: 48px; display: flex; align-items: center; gap: 18px; overflow: auto; }
.link { color: #fff; text-decoration: none; font-size: 14px; white-space: nowrap; opacity: .95; }
.link.router-link-active { font-weight: 700; text-decoration: underline; }
</style>
