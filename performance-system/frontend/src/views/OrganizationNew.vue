<template>
  <div class="container" style="padding:24px 16px">
    <!-- 标题/工具条 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">组织架构</h3>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索姓名/部门/职位" clearable style="width:240px" @keyup.enter="reload" />
        <el-select v-model="status" placeholder="状态" style="width:140px" @change="reload">
          <el-option label="全部" value="" />
          <el-option label="在职" value="active" />
          <el-option label="试用" value="probation" />
          <el-option label="离职" value="inactive" />
        </el-select>
        <el-button type="primary" @click="reload">查询</el-button>
      </div>
    </div>

    <div class="grid" style="grid-template-columns: 320px 1fr; gap:16px">
      <!-- 左侧组织树卡片 -->
      <div class="card" style="padding:12px">
        <div class="row" style="margin-bottom:8px">
          <strong>部门树</strong>
          <el-button text size="small" @click="expandAll">展开</el-button>
        </div>
        <div class="tree-wrap" style="max-height:520px;overflow:auto">
          <el-tree
            :data="deptTree"
            node-key="id"
            :props="{ label:'name', children:'children' }"
            :default-expanded-keys="expandedKeys"
            highlight-current
            @node-click="onDeptClick"
          />
        </div>
      </div>

      <!-- 右侧成员列表卡片 -->
      <div class="card">
        <div class="table-wrap">
          <el-table :data="rows" v-loading="loading" border stripe>
            <el-table-column prop="name" label="姓名" min-width="180">
              <template #default="{ row }">
                <div style="display:flex;align-items:center;gap:10px">
                  <span :style="avatar(row)">{{ (row.name||'?')[0] }}</span>
                  <div>
                    <div style="font-weight:600">{{ row.name }}</div>
                    <div style="font-size:12px;color:#6b7280">{{ row.position_name || '-' }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="department_name" label="部门" min-width="180" />
            <el-table-column prop="position_level" label="级别" width="100" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="email" label="邮箱" min-width="220" />
            <el-table-column prop="phone" label="电话" width="160" />
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
    const res = await orgPlatformApi.departments.tree()
    const data:any = res.data || []
    deptTree.value = data
    expandedKeys.value = (data || []).map((n:any)=> n.id)
  } catch(e) { console.error(e) }
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
const onDeptClick = (node:any) => { currentDept.value = node; reload() }
const onPageChange = (p:number) => { page.value = p; loadList() }

const expandAll = () => { expandedKeys.value = collectIds(deptTree.value) }
const collectIds = (arr:any[]):any[] => arr.flatMap(n => [n.id, ...(n.children?collectIds(n.children):[])])

const statusText = (s:string)=> ({active:'在职', probation:'试用', inactive:'离职'} as any)[s] || s
const statusType = (s:string)=> ({active:'success', probation:'warning', inactive:'info'} as any)[s] || 'info'

const avatar = (r:any)=> ({ height:'28px', width:'28px', display:'inline-flex', alignItems:'center', justifyContent:'center', borderRadius:'8px', color:'#fff', fontWeight:'700', background:'linear-gradient(135deg,var(--brand-400),var(--brand-600))' })

onMounted(async () => { await loadTree(); await loadList(); })
</script>
