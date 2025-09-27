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
        <el-select v-model="selectedCycle" placeholder="选择考核周期" style="width:200px" @change="reload" clearable>
          <el-option 
            v-for="cycle in cycles" 
            :key="cycle.id" 
            :label="cycle.name" 
            :value="cycle.id" 
          />
        </el-select>
        <el-button type="primary" @click="openCreate">新增分配</el-button>
        <el-button type="success" @click="openBatchCreate">批量分配</el-button>
        <el-button type="warning" @click="generateTasks" :disabled="!selectedCycle && selectedRows.length === 0">生成任务</el-button>
      </div>
    </div>

    <div class="card">
      <div class="table-wrap">
        <el-table 
          :data="rows" 
          v-loading="loading" 
          border 
          stripe
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="cycle_name" label="考核周期" width="150" />
          <el-table-column prop="relation_type" label="关系类型" width="140">
            <template #default="{ row }">{{ relationText(row.relation_type) }}</template>
          </el-table-column>
          <el-table-column prop="evaluator_name" label="评价人" min-width="180" />
          <el-table-column prop="evaluatee_name" label="被评价人" min-width="180" />
          <el-table-column prop="weight" label="权重" width="100" />
          <el-table-column prop="reason" label="分配原因" min-width="200" show-overflow-tooltip />
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
      
      <!-- 批量操作工具栏 -->
      <div v-if="selectedRows.length > 0" class="batch-toolbar" style="padding: 12px 16px; background: #f5f7fa; border-top: 1px solid #e4e7ed;">
        <span style="color: #606266; font-size: 14px;">已选择 {{ selectedRows.length }} 项</span>
        <div class="toolbar" style="gap: 8px;">
          <el-button size="small" type="danger" @click="batchDelete">批量删除</el-button>
          <el-button size="small" @click="clearSelection">取消选择</el-button>
        </div>
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

    <!-- 单个分配对话框 -->
    <el-drawer v-model="drawer" :title="mode==='create'?'新增分配':'编辑分配'" size="520px">
      <el-form :model="form" label-width="100" :rules="formRules" ref="formRef">
        <el-form-item label="考核周期" prop="cycle">
          <el-select v-model="form.cycle" placeholder="请选择考核周期" style="width:100%" filterable>
            <el-option 
              v-for="cycle in cycles" 
              :key="cycle.id" 
              :label="cycle.name" 
              :value="cycle.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="评价人" prop="evaluator">
          <el-select v-model="form.evaluator" placeholder="请选择评价人" style="width:100%" filterable>
            <el-option 
              v-for="employee in employees" 
              :key="employee.id" 
              :label="`${employee.name} (${employee.position_name})`" 
              :value="employee.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="被评价人" prop="evaluatee">
          <el-select v-model="form.evaluatee" placeholder="请选择被评价人" style="width:100%" filterable>
            <el-option 
              v-for="employee in employees" 
              :key="employee.id" 
              :label="`${employee.name} (${employee.position_name})`" 
              :value="employee.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关系类型" prop="relation_type">
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
        <el-form-item label="权重" prop="weight">
          <el-input-number v-model="form.weight" :min="0" :max="100" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="分配原因">
          <el-input v-model="form.reason" type="textarea" :rows="3" placeholder="请输入分配原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display:flex;gap:8px;justify-content:flex-end">
          <el-button @click="drawer=false">取消</el-button>
          <el-button type="primary" @click="save" :loading="saving">保存</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 批量分配对话框 -->
    <el-dialog v-model="batchDialog" title="批量分配" width="800px">
      <el-form :model="batchForm" label-width="100">
        <el-form-item label="考核周期" required>
          <el-select v-model="batchForm.cycle" placeholder="请选择考核周期" style="width:100%">
            <el-option 
              v-for="cycle in cycles" 
              :key="cycle.id" 
              :label="cycle.name" 
              :value="cycle.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关系类型" required>
          <el-select v-model="batchForm.relation_type" style="width:100%">
            <el-option label="上级评下级" value="superior" />
            <el-option label="同级互评" value="peer" />
            <el-option label="下级评上级" value="subordinate" />
            <el-option label="自评" value="self" />
            <el-option label="跨部门上级" value="cross_superior" />
            <el-option label="跨部门同级" value="cross_peer" />
            <el-option label="自定义关系" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="权重" required>
          <el-input-number v-model="batchForm.weight" :min="0" :max="100" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="分配原因">
          <el-input v-model="batchForm.reason" type="textarea" :rows="3" placeholder="请输入分配原因" />
        </el-form-item>
        <el-form-item label="评价关系" required>
          <div style="border: 1px solid #dcdfe6; border-radius: 4px; padding: 12px; max-height: 300px; overflow-y: auto;">
            <div v-for="(item, index) in batchForm.assignments" :key="index" class="assignment-item" style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px; padding: 8px; background: #f5f7fa; border-radius: 4px;">
              <el-select v-model="item.evaluator" placeholder="评价人" style="flex: 1" filterable>
                <el-option 
                  v-for="employee in employees" 
                  :key="employee.id" 
                  :label="`${employee.name} (${employee.position_name})`" 
                  :value="employee.id" 
                />
              </el-select>
              <span style="color: #606266;">评价</span>
              <el-select v-model="item.evaluatee" placeholder="被评价人" style="flex: 1" filterable>
                <el-option 
                  v-for="employee in employees" 
                  :key="employee.id" 
                  :label="`${employee.name} (${employee.position_name})`" 
                  :value="employee.id" 
                />
              </el-select>
              <el-button type="danger" size="small" @click="removeAssignment(index)">删除</el-button>
            </div>
            <el-button type="primary" @click="addAssignment" style="width: 100%;">添加评价关系</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display:flex;gap:8px;justify-content:flex-end">
          <el-button @click="batchDialog=false">取消</el-button>
          <el-button type="primary" @click="batchSave" :loading="saving">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { manualAssignmentApi, cycleApi, employeeApi } from '@/utils/api'

const loading = ref(false)
const saving = ref(false)
const rows = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const ordering = ref('')

const keyword = ref('')
const relation = ref('')
const selectedCycle = ref('')
const cycleId = ref('')

// 数据源
const cycles = ref<any[]>([])
const employees = ref<any[]>([])

// 表格选择
const selectedRows = ref<any[]>([])

// 表单验证规则
const formRules = {
  cycle: [{ required: true, message: '请选择考核周期', trigger: 'change' }],
  evaluator: [{ required: true, message: '请选择评价人', trigger: 'change' }],
  evaluatee: [{ required: true, message: '请选择被评价人', trigger: 'change' }],
  relation_type: [{ required: true, message: '请选择关系类型', trigger: 'change' }],
  weight: [{ required: true, message: '请输入权重', trigger: 'blur' }]
}

const load = async () => {
  try {
    loading.value = true
    const params:any = { page: page.value, page_size: pageSize.value }
    if (keyword.value) params.search = keyword.value
    if (ordering.value) params.ordering = ordering.value
    if (relation.value) params.relation_type = relation.value
    if (selectedCycle.value) params.cycle = selectedCycle.value
    const res = await manualAssignmentApi.list(params)
    const data:any = res.data
    rows.value = data.results || data || []
    total.value = data.count ?? rows.value.length
  } finally { loading.value = false }
}

// 加载基础数据
const loadCycles = async () => {
  try {
    const res = await cycleApi.list()
    cycles.value = res.data.results || res.data || []
  } catch (error) {
    console.error('加载考核周期失败:', error)
  }
}

const loadEmployees = async () => {
  try {
    const res = await employeeApi.list({ page_size: 1000 })
    employees.value = res.data.results || res.data || []
  } catch (error) {
    console.error('加载员工列表失败:', error)
  }
}

const reload = () => { page.value = 1; load() }
const onPageChange = (p:number) => { page.value = p; load() }

// 单个分配对话框
const drawer = ref(false)
const mode = ref<'create'|'edit'>('create')
const form = ref<any>({ cycle:'', evaluator:'', evaluatee:'', relation_type:'superior', weight:1, reason:'' })
const formRef = ref()

// 批量分配对话框
const batchDialog = ref(false)
const batchForm = ref<any>({
  cycle: '',
  relation_type: 'superior',
  weight: 1,
  reason: '',
  assignments: []
})

const openCreate = () => { 
  mode.value='create'
  form.value={ cycle:'', evaluator:'', evaluatee:'', relation_type:'superior', weight:1, reason:'' }
  drawer.value=true 
}

const edit = (row:any) => { 
  mode.value='edit'
  form.value={ 
    id:row.id, 
    cycle:row.cycle, 
    evaluator:row.evaluator, 
    evaluatee:row.evaluatee, 
    relation_type:row.relation_type, 
    weight:row.weight, 
    reason:row.reason||'' 
  }
  drawer.value=true 
}

const onDelete = async (row:any) => { 
  try { 
    await manualAssignmentApi.delete(row.id)
    ElMessage.success('已删除')
    reload() 
  } catch(e){ 
    ElMessage.error('删除失败') 
  } 
}

const save = async () => {
  try {
    // 表单验证
    if (!formRef.value) return
    const valid = await formRef.value.validate()
    if (!valid) return

    saving.value = true
    const payload = { 
      cycle: form.value.cycle, 
      evaluator: form.value.evaluator, 
      evaluatee: form.value.evaluatee, 
      relation_type: form.value.relation_type, 
      weight: form.value.weight, 
      reason: form.value.reason 
    }
    
    
    if (mode.value==='create') { 
      await manualAssignmentApi.create(payload)
      ElMessage.success('新增成功') 
    } else { 
      await manualAssignmentApi.update(form.value.id, payload)
      ElMessage.success('更新成功') 
    }
    drawer.value=false
    reload()
  } catch(e){ 
    console.error(e)
    ElMessage.error('保存失败') 
  } finally {
    saving.value = false
  }
}

// 批量分配相关方法
const openBatchCreate = () => {
  batchForm.value = {
    cycle: '',
    relation_type: 'superior',
    weight: 1,
    reason: '',
    assignments: []
  }
  batchDialog.value = true
}

const addAssignment = () => {
  batchForm.value.assignments.push({
    evaluator: '',
    evaluatee: ''
  })
}

const removeAssignment = (index: number) => {
  batchForm.value.assignments.splice(index, 1)
}

const batchSave = async () => {
  try {
    if (!batchForm.value.cycle || !batchForm.value.relation_type || batchForm.value.assignments.length === 0) {
      ElMessage.error('请填写完整信息')
      return
    }

    saving.value = true
    const promises = batchForm.value.assignments.map((assignment: any) => {
      if (!assignment.evaluator || !assignment.evaluatee) return null
      return manualAssignmentApi.create({
        cycle: batchForm.value.cycle,
        evaluator: assignment.evaluator,
        evaluatee: assignment.evaluatee,
        relation_type: batchForm.value.relation_type,
        weight: batchForm.value.weight,
        reason: batchForm.value.reason
      })
    })

    const validPromises = promises.filter(p => p !== null)
    await Promise.all(validPromises)
    
    ElMessage.success(`成功创建 ${validPromises.length} 个分配`)
    batchDialog.value = false
    reload()
  } catch (error) {
    console.error(error)
    ElMessage.error('批量保存失败')
  } finally {
    saving.value = false
  }
}

// 表格选择相关
const handleSelectionChange = (selection: any[]) => {
  selectedRows.value = selection
}

const clearSelection = () => {
  selectedRows.value = []
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedRows.value.length} 个分配？`, '批量删除', {
      type: 'warning'
    })
    
    const promises = selectedRows.value.map(row => manualAssignmentApi.delete(row.id))
    await Promise.all(promises)
    
    ElMessage.success('批量删除成功')
    clearSelection()
    reload()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 生成考核任务
const generateTasks = async () => {
  try {
    await ElMessageBox.confirm('确认根据当前分配生成考核任务？', '生成任务', {
      type: 'warning'
    })
    
    // 确定要生成任务的周期ID
    let cycleId = selectedCycle.value
    
    // 如果没有选择周期筛选器，但有选中的行，使用选中行的周期
    if (!cycleId && selectedRows.value.length > 0) {
      cycleId = selectedRows.value[0].cycle
    }
    
    if (!cycleId) {
      ElMessage.error('请先选择考核周期或选择要生成任务的分配记录')
      return
    }
    
    saving.value = true
    const response = await manualAssignmentApi.generateTasks({ cycle_id: cycleId })
    
    ElMessage.success(response.data.message)
    reload()
  } catch (error) {
    console.error('生成任务失败:', error)
    ElMessage.error(`生成任务失败: ${error.response?.data?.error || error.message}`)
  } finally {
    saving.value = false
  }
}

const relationText = (t:string) => ({superior:'上级评下级', peer:'同级互评', subordinate:'下级评上级', self:'自评', cross_superior:'跨部门上级', cross_peer:'跨部门同级', custom:'自定义关系'} as any)[t] || t

onMounted(async () => {
  await Promise.all([
    load(),
    loadCycles(),
    loadEmployees()
  ])
})
</script>
