<template>
  <div class="container" style="padding:24px 16px">
    <!-- 标题/工具条 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">考核周期</h3>
      <div class="toolbar">
        <el-input v-model="search" placeholder="搜索名称/描述" clearable style="width:240px" @keyup.enter="reload" />
        <el-select v-model="status" placeholder="状态" style="width:140px" @change="reload">
          <el-option label="全部" value="" />
          <el-option label="草稿" value="draft" />
          <el-option label="进行中" value="active" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-button type="primary" @click="openCreate">创建周期</el-button>
      </div>
    </div>

    <!-- 列表卡片 -->
    <div class="card">
      <div class="table-wrap">
        <el-table :data="cycles" v-loading="loading" border stripe>
          <el-table-column prop="name" label="名称" min-width="220" />
          <el-table-column prop="description" label="描述" min-width="260" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="时间" min-width="220">
            <template #default="{ row }">{{ row.start_date }} ~ {{ row.end_date }}</template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
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

    <!-- 创建/编辑弹窗（示意） -->
    <el-dialog v-model="dialogVisible" :title="dialogMode==='create'?'创建考核周期':'编辑考核周期'" width="520px">
      <el-form :model="form" label-width="84">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
        <el-form-item label="开始日期"><el-date-picker v-model="form.start_date" type="date" /></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="form.end_date" type="date" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useEvaluationStore } from '@/stores/evaluation'

const store = useEvaluationStore()
const cycles = computed(()=> store.cycles)
const loading = computed(()=> store.loading)
const total = computed(()=> cycles.value.length)
const page = ref(1)
const size = ref(10)
const ordering = ref('') // 预留排序字段，后端支持 ordering
const search = ref('')
const status = ref('')

const dialogVisible = ref(false)
const dialogMode = ref<'create'|'edit'>('create')
const form = ref<any>({ name:'', description:'', start_date:'', end_date:'' })

const reload = () => {
  const params:any = { page: page.value, page_size: size.value }
  if (search.value) params.search = search.value
  if (ordering.value) params.ordering = ordering.value
  if (status.value) params.status = status.value
  store.fetchCycles(params)
}
const onPageChange = (p:number) => { page.value = p; reload() }

const statusText = (s:string)=> ({draft:'草稿',active:'进行中',completed:'已完成',cancelled:'已取消'} as any)[s] || s
const statusType = (s:string)=> ({draft:'info',active:'success',completed:'warning',cancelled:'danger'} as any)[s] || 'info'

const openCreate = ()=>{ dialogMode.value='create'; form.value={ name:'', description:'', start_date:'', end_date:'', status:'draft' }; dialogVisible.value=true }
const view = (row:any)=>{ console.log('view', row) }
const edit = (row:any)=>{ dialogMode.value='edit'; form.value={ ...row }; dialogVisible.value=true }
const save = async ()=>{
  try {
    // 基础校验
    if (!form.value.name) return ElMessage.error('请填写名称')
    if (!form.value.start_date || !form.value.end_date) return ElMessage.error('请选择开始/结束日期')
    const payload = { 
      name: form.value.name,
      description: form.value.description || '',
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      status: form.value.status || 'draft'
    }
    if (dialogMode.value === 'create') {
      await store.createCycle(payload as any)
      ElMessage.success('创建成功')
    } else {
      await store.updateCycle(form.value.id, payload as any)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    reload()
  } catch (e) {
    console.error(e)
    ElMessage.error('保存失败，请重试')
  }
}

onMounted(()=>{ store.fetchCycles() })
</script>
