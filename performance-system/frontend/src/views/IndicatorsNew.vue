<template>
  <div class="container" style="padding:24px 16px">
    <!-- 标题/工具条 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">考核指标</h3>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索名称/描述" clearable style="width:240px" @keyup.enter="reload" />
        <el-select v-model="category" placeholder="指标类别" style="width:160px" @change="reload">
          <el-option label="全部" value="" />
          <el-option label="工作绩效" value="performance" />
          <el-option label="工作能力" value="ability" />
          <el-option label="工作态度" value="attitude" />
          <el-option label="团队合作" value="teamwork" />
          <el-option label="创新能力" value="innovation" />
        </el-select>
        <el-select v-model="group" placeholder="分组" style="width:140px" @change="reload">
          <el-option v-for="g in groups" :key="g" :label="g" :value="g" />
        </el-select>
        <el-select v-model="enabled" placeholder="状态" style="width:140px" @change="reload">
          <el-option label="全部" value="" />
          <el-option label="启用" :value="true" />
          <el-option label="停用" :value="false" />
        </el-select>
        <el-button type="primary" @click="openCreate">新增指标</el-button>
      </div>
    </div>

    <!-- 列表卡片 -->
    <div class="card">
      <div class="table-wrap">
        <el-table :data="rows" v-loading="loading" border stripe>
          <el-table-column prop="name" label="名称" min-width="220" />
          <el-table-column prop="type" label="类型" width="120">
            <template #default="{ row }">
              <el-tag>{{ typeText(row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="group" label="分组" width="160" />
          <el-table-column prop="weight" label="权重" width="100">
            <template #default="{ row }">{{ row.weight ?? '-' }}</template>
          </el-table-column>
          <el-table-column prop="enabled" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" min-width="180">
            <template #default="{ row }">
              <div class="time-info">
                <div class="time-main">{{ formatDateTime(row.updated_at) }}</div>
                <div class="time-relative">{{ formatRelativeTime(row.updated_at) }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <div class="toolbar">
                <el-button size="small" @click="view(row)">详情</el-button>
                <el-button size="small" type="primary" @click="edit(row)">编辑</el-button>
              </div>
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

    <!-- 新增/编辑 抽屉（示意） -->
    <el-drawer v-model="drawer" :title="mode==='create'?'新增指标':'编辑指标'" size="420px">
      <el-form :model="form" label-width="80">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" style="width:100%">
            <el-option label="KPI" value="kpi" />
            <el-option label="OKR" value="okr" />
            <el-option label="行为" value="behavior" />
          </el-select>
        </el-form-item>
        <el-form-item label="分组"><el-input v-model="form.group" /></el-form-item>
        <el-form-item label="权重"><el-input v-model.number="form.weight" type="number" /></el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.enabled" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display:flex;gap:8px;justify-content:flex-end">
          <el-button @click="drawer=false">取消</el-button>
          <el-button type="primary" @click="save">保存</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { indicatorApi } from '@/utils/api'
import { formatDateTime, formatRelativeTime } from '@/utils/dateUtils'

const loading = ref(false)
const rows = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const ordering = ref('') // 预留排序字段，后端支持 ordering

// 工具条筛选
const keyword = ref('')
const category = ref('')
const group = ref('')
const enabled = ref<any>('')
const groups = ref<string[]>(['通用','产品','平台','销售'])

const load = async () => {
  try {
    loading.value = true
    // 与后端保持一致：仅传递 page / page_size / search / ordering
    const params:any = { page: page.value, page_size: size.value }
    if (keyword.value) params.search = keyword.value
    if (ordering.value) params.ordering = ordering.value
    if (category.value) params.category = category.value
    if (enabled.value !== '') params.is_active = enabled.value
    const res = await indicatorApi.list(params)
    const data:any = res.data
    let list:any[] = data.results || data || []
    // 前端本地过滤：分组（后端未暴露该字段）
    if (group.value) list = list.filter(x => (x.group||'') === group.value)
    rows.value = list
    total.value = data.count ?? list.length
  } finally {
    loading.value = false
  }
}

const reload = () => { page.value = 1; load() }
const onPageChange = (p:number) => { page.value = p; load() }

// 抽屉
const drawer = ref(false)
const mode = ref<'create'|'edit'>('create')
// 与后端字段对齐：name, category, description, weight, max_score, is_active
const form = ref<any>({ name:'', category:'performance', description:'', group:'', weight:1, max_score:100, is_active:true })

const openCreate = () => { 
  mode.value='create'; 
  form.value={ name:'', category:'performance', description:'', group:'', weight:1, max_score:100, is_active:true };
  drawer.value=true 
}
const view = (row:any) => { console.log('view', row) }
const edit = (row:any) => { 
  mode.value='edit'; 
  // 兼容历史字段命名
  form.value={ 
    id: row.id,
    name: row.name,
    category: row.category,
    description: row.description ?? '',
    group: row.group ?? '', // 前端自定义分组
    weight: row.weight ?? 1,
    max_score: row.max_score ?? 100,
    is_active: row.is_active ?? row.enabled ?? true
  };
  drawer.value=true 
}
const save = async () => { 
  try {
    const payload = { 
      name: form.value.name,
      category: form.value.category,
      description: form.value.description,
      weight: form.value.weight,
      max_score: form.value.max_score,
      is_active: !!form.value.is_active
    }
    if (mode.value==='create') {
      await indicatorApi.create(payload)
      ElMessage.success('新增指标成功')
    } else {
      await indicatorApi.update(form.value.id, payload)
      ElMessage.success('编辑指标成功')
    }
    drawer.value=false
    await reload()
  } catch (e:any) {
    console.error(e)
    ElMessage.error('保存失败，请重试')
  }
}

const typeText = (t:string) => ({performance:'工作绩效', ability:'工作能力', attitude:'工作态度', teamwork:'团队合作', innovation:'创新能力'} as any)[t] || t

onMounted(load)
</script>

<style scoped>
.time-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.time-main {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.time-relative {
  font-size: 12px;
  color: #909399;
}
</style>
