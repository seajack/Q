import { createRouter, createWebHistory } from 'vue-router';
import PerformanceDashboard from '../pages/PerformanceDashboard.vue';

const Placeholder = (name: string) => ({
  name,
  template: `<main class='container' style='padding:24px 16px'>
    <div class='card' style='padding:20px'>
      <h3 style='margin:0 0 8px 0'>${name}</h3>
      <p style='margin:0;color:#6b7280'>此页面为占位，后续接入真实功能。</p>
    </div>
  </main>`
});

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: PerformanceDashboard },
    { path: '/tasks', component: Placeholder('评审任务') },
    { path: '/kpi', component: Placeholder('KPI 指标') },
    { path: '/files', component: Placeholder('员工档案') },
    { path: '/org', component: Placeholder('组织架构') },
    { path: '/reports', component: Placeholder('报表中心') },
    { path: '/settings', component: Placeholder('系统设置') },
  ]
});
