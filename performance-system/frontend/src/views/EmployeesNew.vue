<template>
  <div class="container" style="padding:24px 16px">
    <!-- 标题/工具条 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">员工档案</h3>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索姓名/邮箱/电话" clearable style="width:240px" @keyup.enter="reload" />
        <el-select v-model="dept" placeholder="部门" filterable style="width:200px" @change="reload">
          <el-option label="全部" value="" />
          <el-option v-for="d in depts" :key="d" :label="d" :value="d" />
        </el-select>
        <el-select v-model="active" placeholder="状态" style="width:140px" @change="reload">
          <el-option label="全部" value="" />
          <el-option label="激活" :value="true" />
          <el-option label="禁用" :value="false" />
        </el-select>
        <el-button @click="syncFromOrg" :loading="syncing">从中台同步</el-button>
      </div>
    </div>

    <!-- 列表卡片 -->
    <div class="card">
      <div class="table-wrap">
        <el-table :data="rows" v-loading="loading" border stripe>
          <el-table-column prop="employee_id" label="员工号" width="120" />
          <el-table-column prop="name" label="姓名" width="160" />
          <el-table-column prop="department_name" label="部门" min-width="180" />
          <el-table-column prop="position_name" label="职位" min-width="160" />
          <el-table-column prop="position_level" label="级别" width="100" />
          <el-table-column prop="email" label="邮箱" min-width="220" />
          <el-table-column prop="phone" label="电话" width="160" />
          <el-table-column prop="is_active" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '激活' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
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
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useEvaluationStore } from '@/stores/evaluation'

const store = useEvaluationStore()
const rows = computed(()=> store.employees)
const loading = computed(()=> store.loading)
const total = computed(()=> rows.value.length)

// 工具条筛选
const keyword = ref('')
const dept = ref('')
const active = ref<any>('')
const depts = computed(()=> Array.from(new Set(rows.value.map(r=> r.department_name).filter(Boolean))))

const page = ref(1)
const size = ref(10)
const ordering = ref('') // 预留排序字段

const load = async () => {
  // 使用服务端筛选：page/search/ordering/department_name/is_active
  const params:any = { page: page.value }
  if (keyword.value) params.search = keyword.value
  if (ordering.value) params.ordering = ordering.value
  if (dept.value) params.department_name = dept.value
  if (active.value !== '') params.is_active = active.value
  await store.fetchEmployees(params)
}
const reload = () => { page.value = 1; load() }
const onPageChange = (p:number) => { page.value = p; load() }

const syncing = ref(false)
const syncFromOrg = async () => {
  try { syncing.value = true; await store.syncEmployees(); await load() } finally { syncing.value = false }
}

onMounted(load)
</script>
