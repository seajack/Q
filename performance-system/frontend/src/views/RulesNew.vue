<template>
  <div class="container" style="padding:24px 16px">
    <!-- 标题/工具条 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">考核规则</h3>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索名称/描述" clearable style="width:240px" @keyup.enter="reload" />
        <el-select v-model="evaluationScope" placeholder="评价范围" style="width:160px" @change="reload">
          <el-option label="全部" value="" />
          <el-option label="本部门" value="department" />
          <el-option label="本单位" value="unit" />
          <el-option label="全公司" value="company" />
          <el-option label="跨部门" value="cross_department" />
          <el-option label="跨单位" value="cross_unit" />
          <el-option label="手动选择" value="manual" />
        </el-select>
        <el-select v-model="isActive" placeholder="状态" style="width:140px" @change="reload">
          <el-option label="全部" value="" />
          <el-option label="启用" :value="true" />
          <el-option label="停用" :value="false" />
        </el-select>
        <el-button type="primary" @click="openCreate">新增规则</el-button>
      </div>
    </div>

    <!-- 列表卡片 -->
    <div class="card">
      <div class="table-wrap">
        <el-table :data="rows" v-loading="loading" border stripe>
          <el-table-column prop="name" label="规则名称" min-width="220" />
          <el-table-column prop="evaluation_scope" label="评价范围" width="140">
            <template #default="{ row }">{{ scopeText(row.evaluation_scope) }}</template>
          </el-table-column>
          <el-table-column prop="relation_types" label="关系类型" min-width="200">
            <template #default="{ row }">
              <el-tag v-for="r in (row.relation_types||[])" :key="r" style="margin-right:6px">{{ relationText(r) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="110">
            <template #default="{ row }"><el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" min-width="180" />
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
    <el-drawer v-model="drawer" :title="mode==='create'?'新增规则':'编辑规则'" size="520px">
      <el-form :model="form" label-width="100">
        <el-form-item label="规则名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="规则描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="评价范围">
          <el-select v-model="form.evaluation_scope" style="width:100%">
            <el-option label="本部门" value="department" />
            <el-option label="本单位" value="unit" />
            <el-option label="全公司" value="company" />
            <el-option label="跨部门" value="cross_department" />
            <el-option label="跨单位" value="cross_unit" />
            <el-option label="手动选择" value="manual" />
          </el-select>
        </el-form-item>
        <el-form-item label="关系类型">
          <el-select v-model="form.relation_types" multiple style="width:100%">
            <el-option label="上级评下级" value="superior" />
            <el-option label="同级互评" value="peer" />
            <el-option label="下级评上级" value="subordinate" />
            <el-option label="自评" value="self" />
            <el-option label="跨部门上级" value="cross_superior" />
            <el-option label="跨部门同级" value="cross_peer" />
            <el-option label="自定义关系" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
        <el-form-item label="关系权重(JSON)">
          <el-input v-model="form.relation_weights_text" type="textarea" :rows="4" placeholder='例如 {"superior":0.5,"peer":0.3,"subordinate":0.2}' />
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
import { ruleApi } from '@/utils/api'

const loading = ref(false)
const rows = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const ordering = ref('') // 预留排序字段，后端支持 ordering

// 工具条筛选（与后端 filterset 对齐）
const keyword = ref('')
const evaluationScope = ref('')
const isActive = ref<any>('')

const load = async () => {
  try {
    loading.value = true
    // 与后端保持一致：仅传递 page / search / ordering
    const params:any = { page: page.value }
    if (keyword.value) params.search = keyword.value
    if (ordering.value) params.ordering = ordering.value
    if (evaluationScope.value) params.evaluation_scope = evaluationScope.value
    if (isActive.value !== '') params.is_active = isActive.value
    const res = await ruleApi.list(params)
    const data:any = res.data
    const list:any[] = data.results || data || []
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
// 与后端字段对齐
const form = ref<any>({ 
  name: '',
  description: '',
  evaluation_scope: 'department',
  relation_types: ['superior','peer'],
  is_active: true,
  relation_weights_text: '{"superior":0.5,"peer":0.3,"subordinate":0.2}'
})

const openCreate = () => { 
  mode.value='create'; 
  form.value={ name:'', description:'', evaluation_scope:'department', relation_types:['superior','peer'], is_active:true, relation_weights_text:'{"superior":0.5,"peer":0.3,"subordinate":0.2}' };
  drawer.value=true 
}
const view = (row:any) => { console.log('view', row) }
const edit = (row:any) => { 
  mode.value='edit'; 
  form.value={ 
    id: row.id,
    name: row.name,
    description: row.description || '',
    evaluation_scope: row.evaluation_scope || 'department',
    relation_types: Array.isArray(row.relation_types) ? row.relation_types : [],
    is_active: !!row.is_active,
    relation_weights_text: JSON.stringify(row.relation_weights || {}, null, 2)
  };
  drawer.value=true 
}
const save = async () => {
  try {
    if (!form.value.name) return ElMessage.error('请填写规则名称')
    let relation_weights:any = {}
    try { relation_weights = form.value.relation_weights_text ? JSON.parse(form.value.relation_weights_text) : {} } catch { return ElMessage.error('关系权重 JSON 格式不正确') }
    const payload:any = {
      name: form.value.name,
      description: form.value.description || '',
      evaluation_scope: form.value.evaluation_scope,
      relation_types: form.value.relation_types,
      relation_weights,
      is_active: !!form.value.is_active,
    }
    if (mode.value==='create') { await ruleApi.create(payload); ElMessage.success('新增规则成功') }
    else { await ruleApi.update(form.value.id, payload); ElMessage.success('编辑规则成功') }
    drawer.value=false
    await reload()
  } catch (e) {
    console.error(e)
    ElMessage.error('保存失败，请重试')
  }
}

const relationText = (t:string) => ({superior:'上级评下级', peer:'同级互评', subordinate:'下级评上级', self:'自评', cross_superior:'跨部门上级', cross_peer:'跨部门同级', custom:'自定义关系'} as any)[t] || t
const scopeText = (s:string) => ({department:'本部门', unit:'本单位', company:'全公司', cross_department:'跨部门', cross_unit:'跨单位', manual:'手动选择'} as any)[s] || s

onMounted(load)
</script>
