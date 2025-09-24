<template>
  <div class="container" style="padding:24px 16px">
    <!-- 工具条 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">报表中心</h3>
      <div class="toolbar">
        <el-select v-model="cycleId" placeholder="考核周期" style="width:200px" @change="reloadAll">
          <el-option v-for="c in cycles" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-input v-model="keyword" placeholder="搜索姓名/部门" clearable style="width:240px" @keyup.enter="reloadTable" />
        <el-button type="primary" @click="doExport">导出</el-button>
      </div>
    </div>

    <!-- KPI 卡片 -->
    <section class="grid grid-4">
      <div class="card kpi">
        <div class="kpi-top"><span>完成率</span><span class="badge" style="background:#ecfdf5;color:#047857">目标 100%</span></div>
        <div class="kpi-val"><h3>{{ kpi.completion_rate ?? 0 }}%</h3><div style="height:32px;width:32px;border-radius:8px;background:linear-gradient(135deg,#34d399,#14b8a6)"></div></div>
        <div style="margin-top:10px;height:6px;border-radius:8px;background:#e5e7eb"><div :style="{height:'6px',width:(kpi.completion_rate||0)+'%',background:'linear-gradient(90deg,#34d399,#14b8a6)',borderRadius:'8px'}"></div></div>
      </div>
      <div class="card kpi">
        <div class="kpi-top"><span>平均评分</span><span class="badge" style="background:#fffbeb;color:#b45309">{{ kpi.avg_score ?? '-' }}</span></div>
        <div class="kpi-val"><h3>{{ kpi.avg_grade ?? '-' }}</h3><div style="height:32px;width:32px;border-radius:8px;background:linear-gradient(135deg,#f59e0b,#f97316)"></div></div>
        <div style="margin-top:8px;font-size:12px;color:#6b7280">分布见右侧图</div>
      </div>
      <div class="card kpi">
        <div class="kpi-top"><span>已完成任务</span><span class="badge" style="background:#e6f4fb;color:var(--brand-700)">实时</span></div>
        <div class="kpi-val"><h3>{{ kpi.completed_tasks ?? 0 }}</h3><div style="height:32px;width:32px;border-radius:8px;background:linear-gradient(135deg,var(--brand-400),var(--brand-600))"></div></div>
        <div style="margin-top:8px;font-size:12px;color:#6b7280">周期内已完成数量</div>
      </div>
      <div class="card kpi">
        <div class="kpi-top"><span>活跃周期</span><span class="badge" style="background:#ffe4e6;color:#be123c">总 {{ kpi.total_cycles ?? '-' }}</span></div>
        <div class="kpi-val"><h3>{{ kpi.active_cycles ?? 0 }}</h3><div style="height:32px;width:32px;border-radius:8px;background:linear-gradient(135deg,#fb7185,#ef4444)"></div></div>
        <div style="margin-top:8px;font-size:12px;color:#6b7280">当前活跃周期</div>
      </div>
    </section>

    <!-- 图表区 -->
    <section class="grid grid-3 mt-6">
      <div class="card" style="padding:16px; grid-column: span 2">
        <div class="row"><h3 style="margin:0;font-size:16px">评分分布</h3><button class="btn" @click="exportChart('dist')">导出图</button></div>
        <div ref="distRef" class="chart"></div>
      </div>
      <div class="card" style="padding:16px;">
        <div class="row"><h3 style="margin:0;font-size:16px">部门完成度</h3><span style="font-size:12px;color:#6b7280">目标 100%</span></div>
        <div ref="deptRef" class="chart"></div>
      </div>
    </section>

    <!-- 结果表格 -->
    <section class="mt-8">
      <div class="card">
        <div class="table-wrap">
          <el-table :data="rows" v-loading="loading" border stripe>
            <el-table-column prop="employee_name" label="员工" min-width="180" />
            <el-table-column prop="department" label="部门" min-width="160" />
            <el-table-column prop="score" label="评分" width="100" />
            <el-table-column prop="grade" label="等级" width="100" />
            <el-table-column prop="updated_at" label="更新时间" min-width="180" />
          </el-table>
        </div>
        <div class="row" style="padding:12px 16px">
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
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { statsApi, resultApi, cycleApi } from '@/utils/api'

// 筛选
const cycles = ref<any[]>([])
const cycleId = ref<any>('')
const keyword = ref('')

// KPI
const kpi = ref<any>({})

// 图表
const distRef = ref<HTMLDivElement|null>(null)
const deptRef = ref<HTMLDivElement|null>(null)
let distChart: echarts.ECharts | null = null
let deptChart: echarts.ECharts | null = null

// 表格
const loading = ref(false)
const rows = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const pageSize = size // 别名，便于与其它页面一致
const ordering = ref('') // 预留排序字段，后端支持 ordering

const loadCycles = async () => {
  const res = await cycleApi.list()
  const list:any[] = (res.data?.results || res.data || []) as any[]
  cycles.value = list
  if (!cycleId.value && list.length) cycleId.value = list[0].id
}

const loadKpi = async () => {
  const res = await statsApi.overview()
  kpi.value = res.data || {}
}

const loadTable = async () => {
  try {
    loading.value = true
    // 与后端保持一致：仅传递 page / search / ordering
    const params:any = { page: page.value, page_size: pageSize.value }
    if (keyword.value) params.search = keyword.value
    if (ordering.value) params.ordering = ordering.value
    if (cycleId.value) params.cycle = cycleId.value
    const res = await resultApi.list(params)
    const data:any = res.data
    let list:any[] = data.results || data || []
    rows.value = list
    total.value = data.count ?? list.length
  } finally { loading.value = false }
}

const reloadAll = async () => { page.value = 1; await Promise.all([loadKpi(), loadTable(), loadCharts()]) }
const reloadTable = async () => { page.value = 1; await loadTable() }
const onPageChange = async (p:number) => { page.value = p; await loadTable() }

// 图表
const brand600 = () => getComputedStyle(document.documentElement).getPropertyValue('--brand-600').trim() || '#177fc1'
const brand400 = () => getComputedStyle(document.documentElement).getPropertyValue('--brand-400').trim() || '#59b6ea'
const brand700 = () => getComputedStyle(document.documentElement).getPropertyValue('--brand-700').trim() || '#115f96'

const loadCharts = async () => {
  // 用 table 的数据聚合得到分布
  const grades = ['C','B-','B','B+','A-','A','A+']
  const counts = new Array(grades.length).fill(0)
  rows.value.forEach((r:any)=>{ const g=(r.grade||'').toUpperCase(); const i=grades.indexOf(g); if(i>=0) counts[i]++ })
  // 渲染分布
  distChart && distChart.setOption({ grid:{left:40,right:10,top:20,bottom:28}, tooltip:{trigger:'axis'}, xAxis:{type:'category',data:grades}, yAxis:{type:'value',splitLine:{lineStyle:{color:'#eee'}}}, series:[{type:'bar', data:counts, itemStyle:{color:brand600()}, barWidth:'55%'}] })
  // 部门完成度（基于评分记录近似统计）
  const byDept:Record<string, number> = {}
  rows.value.forEach((r:any)=>{ const k=r.department||'未分配'; byDept[k]=(byDept[k]||0)+1 })
  const labels = Object.keys(byDept).slice(0,6)
  const values = labels.map(l=>byDept[l])
  const pals = [brand600(), brand400(), brand700()]
  deptChart && deptChart.setOption({ grid:{left:40,right:10,top:20,bottom:28}, tooltip:{}, xAxis:{type:'value'}, yAxis:{type:'category',data:labels}, series:[{ type:'bar', data:values, itemStyle:{ color:(p:any)=>pals[p.dataIndex%pals.length] } }] })
}

const exportChart = (which:'dist'|'dept') => {
  const c = which==='dist' ? distChart : deptChart
  if (!c) return
  const url = c.getDataURL({ type: 'png', pixelRatio: 2, backgroundColor: '#fff' })
  const a = document.createElement('a'); a.href = url; a.download = which + '.png'; a.click()
}

const doExport = async () => {
  // 调用后端 xlsx 导出接口，优先使用选中的 cycleId
  const res = await resultApi.export(cycleId.value)
  const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const a = document.createElement('a')
  const fname = cycleId.value ? `results_cycle_${cycleId.value}.xlsx` : 'results.xlsx'
  a.href = URL.createObjectURL(blob)
  a.download = fname
  a.click()
  URL.revokeObjectURL(a.href)
}

onMounted(async () => {
  distChart = echarts.init(distRef.value!)
  deptChart = echarts.init(deptRef.value!)
  window.addEventListener('resize', ()=>{ distChart && distChart.resize(); deptChart && deptChart.resize(); })
  await loadCycles()
  await reloadAll()
})
</script>

<style scoped>
.kpi { padding: 16px; }
.kpi-top { display:flex; align-items:center; justify-content:space-between; font-size:12px; color:#6b7280 }
.kpi-val { margin-top:10px; display:flex; align-items:flex-end; justify-content:space-between }
.kpi-val h3 { margin:0; font-size:24px }
</style>
