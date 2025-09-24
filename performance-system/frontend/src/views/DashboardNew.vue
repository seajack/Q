<template>
  <div>
    <main class="container" style="padding:24px 16px">
      <!-- 顶部操作条（简版） -->
      <div class="row" style="margin-bottom:16px">
        <h2 style="margin:0;font-size:20px">考核看板</h2>
        <div class="toolbar">
          <select v-model="period" class="select">
            <option>2025 Q3</option>
            <option>2025 Q2</option>
            <option>2025 Q1</option>
            <option>2024 Q4</option>
          </select>
          <input v-model.trim="keyword" placeholder="搜索员工、部门、指标…" class="input" />
          <button class="btn btn-primary" @click="onCreate">新增评审</button>
        </div>
      </div>

      <!-- KPI 卡片 -->
      <section class="grid grid-4">
        <div class="card kpi">
          <div class="kpi-top"><span>已完成评审</span><span class="badge" style="background:#ecfdf5;color:#047857">+12%</span></div>
          <div class="kpi-val"><h3>{{ kpi.doneRate }}%</h3><div style="height:32px;width:32px;border-radius:8px;background:linear-gradient(135deg,#34d399,#14b8a6)"></div></div>
          <div style="margin-top:10px;height:6px;border-radius:8px;background:#e5e7eb"><div :style="{height:'6px',width:kpi.doneRate+'%',background:'linear-gradient(90deg,#34d399,#14b8a6)',borderRadius:'8px'}"></div></div>
        </div>
        <div class="card kpi">
          <div class="kpi-top"><span>平均评分</span><span class="badge" style="background:#fffbeb;color:#b45309">{{ kpi.avgScore }}</span></div>
          <div class="kpi-val"><h3>{{ kpi.avgGrade }}</h3><div style="height:32px;width:32px;border-radius:8px;background:linear-gradient(135deg,#f59e0b,#f97316)"></div></div>
          <div style="margin-top:8px;font-size:12px;color:#6b7280"><span style="display:inline-block;height:8px;width:8px;background:var(--brand-600);border-radius:2px;margin-right:8px"></span>高分集中于产品与平台</div>
        </div>
        <div class="card kpi">
          <div class="kpi-top"><span>待评审</span><span class="badge" style="background:#e6f4fb;color:var(--brand-700)">-5 人</span></div>
          <div class="kpi-val"><h3>{{ kpi.pending }} 人</h3><div style="height:32px;width:32px;border-radius:8px;background:linear-gradient(135deg,var(--brand-400),var(--brand-600))"></div></div>
          <div style="margin-top:10px;display:grid;grid-template-columns:repeat(5,1fr);gap:4px">
            <div style="height:6px;border-radius:6px;background:var(--brand-600);opacity:.9"></div>
            <div style="height:6px;border-radius:6px;background:var(--brand-600);opacity:.7"></div>
            <div style="height:6px;border-radius:6px;background:var(--brand-600);opacity:.5"></div>
            <div style="height:6px;border-radius:6px;background:var(--brand-600);opacity:.4"></div>
            <div style="height:6px;border-radius:6px;background:var(--brand-600);opacity:.3"></div>
          </div>
        </div>
        <div class="card kpi">
          <div class="kpi-top"><span>异常波动</span><span class="badge" style="background:#ffe4e6;color:#be123c">{{ kpi.anomaly }} 员工</span></div>
          <div class="kpi-val"><h3>{{ kpi.anomalyRate }}%</h3><div style="height:32px;width:32px;border-radius:8px;background:linear-gradient(135deg,#fb7185,#ef4444)"></div></div>
          <div style="margin-top:8px;font-size:12px;color:#6b7280">近两期评分差异 > 1.0</div>
        </div>
      </section>

      <!-- 图表区 -->
      <section class="grid grid-3 mt-6">
        <div class="card" style="padding:16px; grid-column: span 2">
          <div class="row"><h3 style="margin:0;font-size:16px">评分分布</h3><button class="btn" @click="exportChart('dist')">导出</button></div>
          <div ref="distRef" class="chart"></div>
        </div>
        <div class="card" style="padding:16px;">
          <div class="row"><h3 style="margin:0;font-size:16px">部门完成度</h3><span style="font-size:12px;color:#6b7280">目标 100%</span></div>
          <div ref="deptRef" class="chart"></div>
        </div>
      </section>

      <!-- 表格（与原型一致的交互：排序/分页） -->
      <section class="mt-8">
        <div class="row">
          <h3 style="margin:0;font-size:16px">员工绩效</h3>
          <div class="toolbar">
            <span style="font-size:12px;color:#6b7280">每页</span>
            <select v-model.number="size" @change="loadList" class="select">
              <option :value="5">5</option>
              <option :value="10">10</option>
              <option :value="20">20</option>
            </select>
            <span style="font-size:12px;color:#6b7280">条</span>
          </div>
        </div>
        <div class="table-wrap mt-6">
          <table>
            <thead>
              <tr>
                <th><button class="btn" @click="toggleSort('name')">员工 ▲▼</button></th>
                <th><button class="btn" @click="toggleSort('dept')">部门 ▲▼</button></th>
                <th><button class="btn" @click="toggleSort('target')">目标达成 ▲▼</button></th>
                <th><button class="btn" @click="toggleSort('grade')">评分 ▲▼</button></th>
                <th>状态</th>
                <th style="text-align:right">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(r,i) in items" :key="r.id">
                <td>
                  <div style="display:flex;align-items:center;gap:12px">
                    <span :style="avatarStyle(r)">{{ r.name?.[0] || '?' }}</span>
                    <div>
                      <div style="font-weight:600">{{ r.name || '—' }}</div>
                      <div style="font-size:12px;color:#6b7280">{{ r.role || '—' }}</div>
                    </div>
                  </div>
                </td>
                <td style="font-size:14px">{{ r.dept || '—' }}</td>
                <td style="font-size:14px">{{ r.target ?? '—' }}<span v-if="r.target != null">%</span></td>
                <td :style="{color:gradeColor(r),fontWeight:'600'}">{{ r.grade || '—' }}</td>
                <td><span class="badge" :style="badgeStyle(r)">{{ r.status || '—' }}</span></td>
                <td style="text-align:right">
                  <div class="toolbar">
                    <button class="btn" @click="onView(r)">详情</button>
                    <button class="btn btn-primary" @click="onEdit(r)">编辑</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="row" style="margin-top:12px;font-size:12px;color:#374151">
          <div>共 {{ total }} 人 · 第 {{ page }} 页</div>
          <div class="toolbar">
            <button class="btn" @click="prev">上一页</button>
            <button class="btn" @click="next">下一页</button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { ref, onMounted, watch } from 'vue'
import { statsApi, employeeApi, resultApi } from '@/utils/api'

// 品牌色
const brand600 = () => getComputedStyle(document.documentElement).getPropertyValue('--brand-600').trim() || '#177fc1'
const brand400 = () => getComputedStyle(document.documentElement).getPropertyValue('--brand-400').trim() || '#59b6ea'
const brand700 = () => getComputedStyle(document.documentElement).getPropertyValue('--brand-700').trim() || '#115f96'

// 顶部交互
const period = ref('2025 Q3')
const keyword = ref('')
let keyTimer: any
watch(keyword, () => { clearTimeout(keyTimer); keyTimer = setTimeout(loadList, 300) })
watch(period, () => { initLoad() })

// KPI 数据
const kpi = ref({ doneRate: 0, avgScore: 0, avgGrade: 'B+', pending: 0, anomaly: 0, anomalyRate: 0 })

// 图表引用
const distRef = ref<HTMLDivElement | null>(null)
const deptRef = ref<HTMLDivElement | null>(null)
let distChart: echarts.ECharts | null = null
let deptChart: echarts.ECharts | null = null

// 表格数据（服务端分页语义，使用现有 API 模拟）
const items = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const sort = ref('name') // or -name

const toggleSort = (k: 'name'|'dept'|'target'|'grade') => {
  const cur = sort.value
  const isCur = cur.replace('-', '') === k
  if (!isCur) sort.value = k
  else sort.value = cur.startsWith('-') ? k : ('-' + k)
  loadList()
}

const prev = () => { if (page.value > 1) { page.value -= 1; loadList() } }
const next = () => { page.value += 1; loadList() }

// 动作
const onCreate = () => alert('打开新增评审弹窗（示意）')
const onView = (r:any) => alert('查看：' + (r.name || r.id))
const onEdit = (r:any) => alert('编辑：' + (r.name || r.id))

// 工具样式
const avatarStyle = (r:any) => ({
  height:'32px', width:'32px', display:'inline-flex', alignItems:'center', justifyContent:'center', borderRadius:'8px', color:'#fff', fontWeight:'700',
  background: 'linear-gradient(135deg, var(--brand-400), var(--brand-600))'
})
const gradeColor = (r:any) => r.status==='已完成' ? '#047857' : (r.status==='进行中' ? '#b45309' : '#be123c')
const badgeStyle = (r:any) => r.status==='已完成' ? 'background:#ecfdf5;color:#047857' : (r.status==='进行中' ? 'background:#fffbeb;color:#b45309' : 'background:#fff1f2;color:#be123c')

// 加载 KPI
const loadKpi = async () => {
  try {
    const res = await statsApi.overview()
    // 兼容字段名
    const data:any = res.data || {}
    kpi.value.doneRate = Math.round((data.completion_rate || 0))
    kpi.value.avgScore = Math.round((data.avg_score || 4) * 10) / 10
    kpi.value.avgGrade = data.avg_grade || 'B+'
    kpi.value.pending = data.pending_tasks || 0
    kpi.value.anomaly = data.anomaly || 0
    kpi.value.anomalyRate = data.anomaly_rate || 0
  } catch (e) { console.error(e) }
}

// 加载表（以员工列表为基准，真实字段映射到原型列）
const loadList = async () => {
  try {
    const params:any = { page: page.value, size: size.value, search: keyword.value || undefined }
    const res = await employeeApi.list(params)
    const arr:any[] = (res.data?.results || res.data || []) as any[]
    items.value = arr.map((x:any) => ({
      id: x.id,
      name: x.name || x.full_name || x.username || '员工',
      role: x.title || x.position || '',
      dept: x.department || x.dept || '',
      target: undefined, // 无对应字段时为空
      grade: undefined,  // 结果页可二次映射
      status: x.status_text || x.status || '进行中'
    }))
    total.value = (res.data?.count ?? arr.length) as number
  } catch (e) { console.error(e) }
}

// 加载图（优先用结果列表做评分分布，部门完成度用员工数占比近似）
const loadCharts = async () => {
  try {
    const res = await resultApi.list({ page: 1, size: 100 })
    const list:any[] = (res.data?.results || res.data || []) as any[]
    const grades = ['C','B-','B','B+','A-','A','A+']
    const counts = new Array(grades.length).fill(0)
    list.forEach((r:any) => {
      const g = (r.grade || r.final_grade || '').toUpperCase()
      const idx = grades.indexOf(g)
      if (idx >= 0) counts[idx]++
    })
    applyDist({ bins: grades, counts })
  } catch (e) {
    // 无结果则用占位数据
    applyDist({ bins: ['C','B-','B','B+','A-','A','A+'], counts: [5,12,22,30,18,9,4] })
  }

  try {
    // 基于当前 items 的部门完成度近似（按人数计）
    const byDept:Record<string, number> = {}
    items.value.forEach(r => { const k=r.dept||'未分配'; byDept[k]=(byDept[k]||0)+1 })
    const labels = Object.keys(byDept).slice(0,5)
    const values = labels.map(l => byDept[l])
    applyDept({ labels, values })
  } catch (e) { console.error(e) }
}

// 图表渲染
const applyDist = (data:{bins:string[];counts:number[]}) => {
  if (!distChart) return
  distChart.setOption({
    grid:{left:40,right:10,top:20,bottom:28}, tooltip:{trigger:'axis'},
    xAxis:{type:'category',data:data.bins}, yAxis:{type:'value',splitLine:{lineStyle:{color:'#eee'}}},
    series:[{type:'bar',data:data.counts, itemStyle:{color:brand600()}, barWidth:'55%'}]
  })
}
const applyDept = (data:{labels:string[];values:number[]}) => {
  if (!deptChart) return
  const pals = [brand600(), brand400(), brand700()]
  deptChart.setOption({
    grid:{left:40,right:10,top:20,bottom:28}, tooltip:{}, xAxis:{type:'value'}, yAxis:{type:'category',data:data.labels},
    series:[{type:'bar',data:data.values, itemStyle:{ color:(p:any)=>pals[p.dataIndex%pals.length] }}]
  })
}

const initCharts = () => {
  distChart = echarts.init(distRef.value!)
  deptChart = echarts.init(deptRef.value!)
  window.addEventListener('resize', ()=>{ distChart && distChart.resize(); deptChart && deptChart.resize(); })
}

const initLoad = async () => {
  await Promise.all([loadKpi(), loadList()])
  await loadCharts()
}

onMounted(async () => {
  initCharts()
  await initLoad()
})
</script>

<style scoped>
.kpi { padding: 16px; }
.kpi-top { display:flex; align-items:center; justify-content:space-between; font-size:12px; color:#6b7280 }
.kpi-val { margin-top:10px; display:flex; align-items:flex-end; justify-content:space-between }
.kpi-val h3 { margin:0; font-size:24px }
</style>
