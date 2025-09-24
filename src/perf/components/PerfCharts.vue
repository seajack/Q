<template>
  <section class="grid grid-3 mt-6">
    <div class="card" style="padding:16px; grid-column: span 2">
      <div class="row">
        <h3 style="margin:0;font-size:16px">评分分布</h3>
        <button class="btn" @click="exportChart('dist')">导出</button>
      </div>
      <div ref="distRef" class="chart"></div>
    </div>
    <div class="card" style="padding:16px;">
      <div class="row">
        <h3 style="margin:0;font-size:16px">部门完成度</h3>
        <span style="font-size:12px;color:#6b7280">目标 100%</span>
      </div>
      <div ref="deptRef" class="chart"></div>
    </div>
  </section>
</template>

<script setup lang="ts">
import * as echarts from 'echarts';
import { onMounted, ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { usePerfStore } from '../stores/perf';

const store = usePerfStore();
const { distribution, deptProgress } = storeToRefs(store);

const distRef = ref<HTMLDivElement | null>(null);
const deptRef = ref<HTMLDivElement | null>(null);
let distChart: echarts.ECharts | null = null;
let deptChart: echarts.ECharts | null = null;

const exportChart = (which: 'dist' | 'dept') => {
  const c = which === 'dist' ? distChart : deptChart;
  if (!c) return;
  const url = c.getDataURL({ type: 'png', pixelRatio: 2, backgroundColor: '#fff' });
  const a = document.createElement('a'); a.href = url; a.download = `${which}.png`; a.click();
};

const applyDist = () => {
  if (!distChart) return;
  const brand = getComputedStyle(document.documentElement).getPropertyValue('--brand-600').trim() || '#177fc1';
  distChart.setOption({
    grid:{left:40,right:10,top:20,bottom:28}, tooltip:{trigger:'axis'},
    xAxis:{type:'category',data: distribution.value.bins}, yAxis:{type:'value',splitLine:{lineStyle:{color:'#eee'}}},
    series:[{type:'bar',data: distribution.value.counts, itemStyle:{color:brand}, barWidth:'55%'}]
  });
};

const applyDept = () => {
  if (!deptChart) return;
  const brand = getComputedStyle(document.documentElement).getPropertyValue('--brand-600').trim() || '#177fc1';
  const pals = [brand, getComputedStyle(document.documentElement).getPropertyValue('--brand-400').trim()||'#59b6ea', getComputedStyle(document.documentElement).getPropertyValue('--brand-700').trim()||'#115f96'];
  deptChart.setOption({
    grid:{left:40,right:10,top:20,bottom:28}, tooltip:{}, xAxis:{type:'value',max:100}, yAxis:{type:'category',data: deptProgress.value.labels},
    series:[{type:'bar',data: deptProgress.value.values, itemStyle:{ color:(p:any)=>pals[p.dataIndex%pals.length] }}]
  });
};

onMounted(() => {
  distChart = echarts.init(distRef.value!);
  deptChart = echarts.init(deptRef.value!);
  applyDist();
  applyDept();
  window.addEventListener('resize', ()=>{ distChart && distChart.resize(); deptChart && deptChart.resize(); });
});

watch(distribution, applyDist, { deep: true });
watch(deptProgress, applyDept, { deep: true });
</script>
