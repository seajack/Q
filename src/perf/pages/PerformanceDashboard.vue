<template>
  <div>
    <TopNav @create="onCreate" />
    <main class="container" style="padding:24px 16px">
      <!-- KPI -->
      <section class="grid grid-4">
        <div class="card kpi">
          <div class="kpi-top"><span>已完成评审</span><span class="badge" style="background:#ecfdf5;color:#047857">+12%</span></div>
          <div class="kpi-val"><h3>{{store.kpi.doneRate}}%</h3><div style="height:32px;width:32px;border-radius:8px;background:linear-gradient(135deg,#34d399,#14b8a6)"></div></div>
          <div style="margin-top:10px;height:6px;border-radius:8px;background:#e5e7eb"><div :style="{height:'6px',width:store.kpi.doneRate+'%',background:'linear-gradient(90deg,#34d399,#14b8a6)',borderRadius:'8px'}"></div></div>
        </div>
        <div class="card kpi">
          <div class="kpi-top"><span>平均评分</span><span class="badge" style="background:#fffbeb;color:#b45309">{{store.kpi.avgScore}}</span></div>
          <div class="kpi-val"><h3>{{store.kpi.avgGrade}}</h3><div style="height:32px;width:32px;border-radius:8px;background:linear-gradient(135deg,#f59e0b,#f97316)"></div></div>
          <div style="margin-top:8px;font-size:12px;color:#6b7280"><span style="display:inline-block;height:8px;width:8px;background:var(--brand-600);border-radius:2px;margin-right:8px"></span>高分集中于产品与平台</div>
        </div>
        <div class="card kpi">
          <div class="kpi-top"><span>待评审</span><span class="badge" style="background:#e6f4fb;color:var(--brand-700)">-5 人</span></div>
          <div class="kpi-val"><h3>{{store.kpi.pending}} 人</h3><div style="height:32px;width:32px;border-radius:8px;background:linear-gradient(135deg,var(--brand-400),var(--brand-600))"></div></div>
          <div style="margin-top:10px;display:grid;grid-template-columns:repeat(5,1fr);gap:4px">
            <div style="height:6px;border-radius:6px;background:var(--brand-600);opacity:.9"></div>
            <div style="height:6px;border-radius:6px;background:var(--brand-600);opacity:.7"></div>
            <div style="height:6px;border-radius:6px;background:var(--brand-600);opacity:.5"></div>
            <div style="height:6px;border-radius:6px;background:var(--brand-600);opacity:.4"></div>
            <div style="height:6px;border-radius:6px;background:var(--brand-600);opacity:.3"></div>
          </div>
        </div>
        <div class="card kpi">
          <div class="kpi-top"><span>异常波动</span><span class="badge" style="background:#ffe4e6;color:#be123c">{{store.kpi.anomaly}} 员工</span></div>
          <div class="kpi-val"><h3>{{store.kpi.anomalyRate}}%</h3><div style="height:32px;width:32px;border-radius:8px;background:linear-gradient(135deg,#fb7185,#ef4444)"></div></div>
          <div style="margin-top:8px;font-size:12px;color:#6b7280">近两期评分差异 > 1.0</div>
        </div>
      </section>

      <PerfCharts />
      <PerfTable @view="onView" @edit="onEdit" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import TopNav from '../components/TopNav.vue';
import PerfCharts from '../components/PerfCharts.vue';
import PerfTable from '../components/PerfTable.vue';
import { usePerfStore } from '../stores/perf';

const onCreate = () => alert('打开新增评审弹窗（示意）');
const onView = (r:any) => alert('查看：' + r.name);
const onEdit = (r:any) => alert('编辑：' + r.name);

// 初次进入页面请求后端数据
const store = usePerfStore();
onMounted(() => {
  store.initLoad();
});
</script>

<style scoped>
.kpi { padding: 16px; }
.kpi-top { display: flex; align-items: center; justify-content: space-between; font-size: 12px; color: #6b7280; }
.kpi-val { margin-top: 10px; display: flex; align-items: flex-end; justify-content: space-between; }
.kpi-val h3 { margin: 0; font-size: 24px; }
</style>
