<template>
  <div class="container" style="padding:24px 16px">
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">手动分配</h3>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索评价人/被评价人/原因" clearable style="width:240px" @keyup.enter="reload" />
        <el-select v-model="relation" placeholder="关系类型" style="width:160px" @change="reload">
          <el-option label="全部" value="" />
          <el-option label="上级评下级" value="superior" />
          <el-option label="同级互评" value="peer" />
          <el-option label="下级评上级" value="subordinate" />
          <el-option label="自评" value="self" />
          <el-option label="跨部门上级" value="cross_superior" />
          <el-option label="跨部门同级" value="cross_peer" />
          <el-option label="自定义关系" value="custom" />
        </el-select>
        <el-input v-model="cycleId" placeholder="周期ID" style="width:140px" @keyup.enter="reload" />
        <el-button type="primary" @click="openCreate">新增分配</el-button>
      </div>
    </div>

    <div class="card">
      <div class="table-wrap">
        <el-table :data="rows" v-loading="loading" border stripe>
          <el-table-column prop="cycle" label="周期ID" width="100" />
          <el-table-column prop="relation_type" label="关系类型" width="140">
            <template #default="{ row }">{{ relationText(row.relation_type) }}</template>
          </el-table-column>
          <el-table-column prop="evaluator_name" label="评价人" min-width="180" />
          <el-table-column prop="evaluatee_name" label="被评价人" min-width="180" />
          <el-table-column prop="weight" label="权重" width="100" />
          <el-table-column prop="created_at" label="创建时间" min-width="180" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <div class="toolbar">
                <el-button size="small" @click="edit(row)">编辑</el-button>
                <el-popconfirm title="确认删除该分配？" @confirm="onDelete(row)"><template #reference>
                  <el-button size="small" type="danger">删除</el-button>
                </template></el-popconfirm>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="row" style="padding:12px 16px">
        <div class="toolbar" style="gap:6px">
          <span style="font-size:12px;color:#6b7280">每页</span>
          <el-select v-model="pageSize" size="small" style="width:90px" @change="reload">
            <el-option :value="10" label="10" />
            <el-option :value="20" label="20" />
            <el-option :value="50" label="50" />
            <el-option :value="100" label="100" />
          </el-select>
          <span style="font-size:12px;color:#6b7280">条</span>
        </div>
        <el-pagination
          background
          layout="prev, pager, next"
          :current-page="page"
          :page-size="pageSize"
          :total="total"
          @current-change="onPageChange"
        />
      </div>
    </div>

    <el-drawer v-model="drawer" :title="mode==='create'?'新增分配':'编辑分配'" size="520px">
      <el-form :model="form" label-width="100">
        <el-form-item label="周期ID"><el-input v-model.number="form.cycle" type="number" /></el-form-item>
        <el-form-item label="评价人ID"><el-input v-model.number="form.evaluator" type="number" /></el-form-item>
        <el-form-item label="被评价人ID"><el-input v-model.number="form.evaluatee" type="number" /></el-form-item>
        <el-form-item label="关系类型">
          <el-select v-model="form.relation_type" style="width:100%">
            <el-option label="上级评下级" value="superior" />
            <el-option label="同级互评" value="peer" />
            <el-option label="下级评上级" value="subordinate" />
            <el-option label="自评" value="self" />
            <el-option label="跨部门上级" value="cross_superior" />
            <el-option label="跨部门同级" value="cross_peer" />
            <el-option label="自定义关系" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="权重"><el-input v-model.number="form.weight" type="number" /></el-form-item>
        <el-form-item label="原因"><el-input v-model="form.reason" type="textarea" :rows="3" /></el-form-item>
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
import { manualAssignmentApi } from '@/utils/api'

const loading = ref(false)
const rows = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const ordering = ref('')

const keyword = ref('')
const relation = ref('')
const cycleId = ref('')

const load = async () => {
  try {
    loading.value = true
    const params:any = { page: page.value, page_size: pageSize.value }
    if (keyword.value) params.search = keyword.value
    if (ordering.value) params.ordering = ordering.value
    if (relation.value) params.relation_type = relation.value
    if (cycleId.value) params.cycle = cycleId.value
    const res = await manualAssignmentApi.list(params)
    const data:any = res.data
    rows.value = data.results || data || []
    total.value = data.count ?? rows.value.length
  } finally { loading.value = false }
}

const reload = () => { page.value = 1; load() }
const onPageChange = (p:number) => { page.value = p; load() }

const drawer = ref(false)
const mode = ref<'create'|'edit'>('create')
const form = ref<any>({ cycle:'', evaluator:'', evaluatee:'', relation_type:'superior', weight:1, reason:'' })

const openCreate = () => { mode.value='create'; form.value={ cycle:'', evaluator:'', evaluatee:'', relation_type:'superior', weight:1, reason:'' }; drawer.value=true }
const edit = (row:any) => { mode.value='edit'; form.value={ id:row.id, cycle:row.cycle, evaluator:row.evaluator, evaluatee:row.evaluatee, relation_type:row.relation_type, weight:row.weight, reason:row.reason||'' }; drawer.value=true }
const onDelete = async (row:any) => { try { await manualAssignmentApi.delete(row.id); ElMessage.success('已删除'); reload() } catch(e){ ElMessage.error('删除失败') } }

const save = async () => {
  try {
    const payload = { cycle: form.value.cycle, evaluator: form.value.evaluator, evaluatee: form.value.evaluatee, relation_type: form.value.relation_type, weight: form.value.weight, reason: form.value.reason }
    if (!payload.cycle || !payload.evaluator || !payload.evaluatee) return ElMessage.error('请填写周期与人选')
    if (mode.value==='create') { await manualAssignmentApi.create(payload); ElMessage.success('新增成功') }
    else { await manualAssignmentApi.update(form.value.id, payload); ElMessage.success('更新成功') }
    drawer.value=false
    reload()
  } catch(e){ console.error(e); ElMessage.error('保存失败') }
}

const relationText = (t:string) => ({superior:'上级评下级', peer:'同级互评', subordinate:'下级评上级', self:'自评', cross_superior:'跨部门上级', cross_peer:'跨部门同级', custom:'自定义关系'} as any)[t] || t

onMounted(load)
</script>
