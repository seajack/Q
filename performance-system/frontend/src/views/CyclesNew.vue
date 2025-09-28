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
          <el-table-column prop="name" label="名称" width="180" show-overflow-tooltip />
          <el-table-column prop="description" label="描述" min-width="160" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="考核规则" width="140" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.evaluation_rule_name" :title="row.evaluation_rule_name">{{ row.evaluation_rule_name }}</span>
              <span v-else class="text-gray-400">未设置</span>
            </template>
          </el-table-column>
          <el-table-column label="考核指标" min-width="180" show-overflow-tooltip>
            <template #default="{ row }">
              <div style="display: flex; flex-wrap: wrap; gap: 4px;">
                <el-tag 
                  v-for="indicator in (row.evaluation_indicators || []).slice(0, 2)" 
                  :key="indicator.id"
                  size="small"
                  style="margin: 0;"
                >
                  {{ indicator.name }}
                </el-tag>
                <el-tag v-if="(row.evaluation_indicators || []).length > 2" size="small" type="info">
                  +{{ (row.evaluation_indicators || []).length - 2 }}
                </el-tag>
                <span v-if="!row.evaluation_indicators || row.evaluation_indicators.length === 0" class="text-gray-400">未设置</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="时间" width="200">
            <template #default="{ row }">
              <div style="font-size: 12px; line-height: 1.4;">
                <div>{{ row.start_date }}</div>
                <div style="color: #999;">~ {{ row.end_date }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="300" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" @click="view(row)">详情</el-button>
                <el-button size="small" type="primary" @click="edit(row)">编辑</el-button>
                <el-button size="small" type="success" @click="generateTasks(row)">生成任务</el-button>
                <el-button size="small" type="info" @click="viewTasks(row)">查看任务</el-button>
                <el-button size="small" type="warning" @click="exportCodes(row)">导出</el-button>
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
    <el-dialog v-model="dialogVisible" :title="dialogMode==='create'?'创建考核周期':'编辑考核周期'" width="600px">
      <FormValidator
        v-model="form"
        :rules="validationRules"
        :show-error-panel="true"
        :show-realtime-validation="true"
        :scroll-to-error="true"
        @validate="handleFormValidate"
        @submit="handleFormSubmit"
      >
        <template #default="{ formData, errors, isValid }">
          <el-form :model="formData" label-width="100px" :rules="validationRules">
            <el-form-item label="名称" prop="name" data-field="name">
              <el-input 
                v-model="formData.name" 
                placeholder="请输入考核周期名称"
                :class="{ 'is-error': errors.some(e => e.field === 'name') }"
              />
              <div v-if="errors.some(e => e.field === 'name')" class="field-error-message">
                {{ errors.find(e => e.field === 'name')?.message }}
              </div>
            </el-form-item>
            
            <el-form-item label="描述" prop="description" data-field="description">
              <el-input 
                v-model="formData.description" 
                type="textarea"
                :rows="3"
                placeholder="请输入考核周期描述"
                :class="{ 'is-error': errors.some(e => e.field === 'description') }"
              />
              <div v-if="errors.some(e => e.field === 'description')" class="field-error-message">
                {{ errors.find(e => e.field === 'description')?.message }}
              </div>
            </el-form-item>
            
            <el-form-item label="开始日期" prop="start_date" data-field="start_date">
              <el-date-picker 
                v-model="formData.start_date" 
                type="date" 
                placeholder="选择开始日期"
                style="width: 100%"
                :class="{ 'is-error': errors.some(e => e.field === 'start_date') }"
              />
              <div v-if="errors.some(e => e.field === 'start_date')" class="field-error-message">
                {{ errors.find(e => e.field === 'start_date')?.message }}
              </div>
            </el-form-item>
            
            <el-form-item label="结束日期" prop="end_date" data-field="end_date">
              <el-date-picker 
                v-model="formData.end_date" 
                type="date" 
                placeholder="选择结束日期"
                style="width: 100%"
                :class="{ 'is-error': errors.some(e => e.field === 'end_date') }"
              />
              <div v-if="errors.some(e => e.field === 'end_date')" class="field-error-message">
                {{ errors.find(e => e.field === 'end_date')?.message }}
              </div>
            </el-form-item>
            
            <el-form-item label="考核规则" prop="evaluation_rule" data-field="evaluation_rule">
              <el-select 
                v-model="formData.evaluation_rule" 
                placeholder="请选择考核规则" 
                style="width: 100%"
                :class="{ 'is-error': errors.some(e => e.field === 'evaluation_rule') }"
              >
                <el-option 
                  v-for="rule in evaluationRules" 
                  :key="rule.id" 
                  :label="rule.name" 
                  :value="rule.id"
                  :disabled="!rule.is_active"
                />
              </el-select>
              <div v-if="errors.some(e => e.field === 'evaluation_rule')" class="field-error-message">
                {{ errors.find(e => e.field === 'evaluation_rule')?.message }}
              </div>
            </el-form-item>
            
            <el-form-item label="考核指标" prop="evaluation_indicators" data-field="evaluation_indicators">
              <el-select 
                v-model="formData.evaluation_indicators" 
                placeholder="请选择考核指标" 
                multiple 
                style="width: 100%"
                collapse-tags
                collapse-tags-tooltip
                :class="{ 'is-error': errors.some(e => e.field === 'evaluation_indicators') }"
              >
                <el-option 
                  v-for="indicator in evaluationIndicators" 
                  :key="indicator.id" 
                  :label="indicator.name" 
                  :value="indicator.id"
                  :disabled="!indicator.is_active"
                />
              </el-select>
              <div v-if="errors.some(e => e.field === 'evaluation_indicators')" class="field-error-message">
                {{ errors.find(e => e.field === 'evaluation_indicators')?.message }}
              </div>
            </el-form-item>
          </el-form>
        </template>
      </FormValidator>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useEvaluationStore } from '@/stores/evaluation'
import FormValidator from '@/components/FormValidator.vue'

const store = useEvaluationStore()
const cycles = computed(()=> store.cycles)
const loading = computed(()=> store.loading)
const total = computed(()=> cycles.value.length)
const page = ref(1)
const size = ref(10)
const ordering = ref('') // 预留排序字段，后端支持 ordering
const search = ref('')
const status = ref('')

// 考核规则和指标数据
const evaluationRules = computed(()=> store.evaluationRules)
const evaluationIndicators = computed(()=> store.indicators)

const dialogVisible = ref(false)
const dialogMode = ref<'create'|'edit'>('create')
const form = ref<any>({ 
  name:'', 
  description:'', 
  start_date:'', 
  end_date:'', 
  evaluation_rule: null,
  evaluation_indicators: []
})

// 表单验证规则
const validationRules = {
  name: [
    { required: true, message: '请输入考核周期名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度应在2-50个字符之间', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入考核周期描述', trigger: 'blur' },
    { min: 10, max: 200, message: '描述长度应在10-200个字符之间', trigger: 'blur' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' },
    { 
      validator: (rule: any, value: any, callback: any) => {
        if (value && form.value.end_date && new Date(value) >= new Date(form.value.end_date)) {
          callback(new Error('开始日期必须早于结束日期'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
  ],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' },
    { 
      validator: (rule: any, value: any, callback: any) => {
        if (value && form.value.start_date && new Date(value) <= new Date(form.value.start_date)) {
          callback(new Error('结束日期必须晚于开始日期'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
  ],
  evaluation_rule: [
    { required: true, message: '请选择考核规则', trigger: 'change' }
  ],
  evaluation_indicators: [
    { required: true, message: '请选择至少一个考核指标', trigger: 'change' },
    { 
      validator: (rule: any, value: any, callback: any) => {
        if (!value || value.length === 0) {
          callback(new Error('请选择至少一个考核指标'))
        } else if (value.length > 10) {
          callback(new Error('最多只能选择10个考核指标'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
  ]
}

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

const openCreate = async ()=>{ 
  dialogMode.value='create'; 
  form.value={ 
    name:'', 
    description:'', 
    start_date:'', 
    end_date:'', 
    status:'draft',
    evaluation_rule: null,
    evaluation_indicators: []
  }; 
  
  // 加载考核规则和指标数据
  try {
    await store.fetchEvaluationRules()
    await store.fetchIndicators()
  } catch (error) {
    console.error('加载考核规则和指标失败:', error)
  }
  
  dialogVisible.value=true 
}
const view = (row:any)=>{ console.log('view', row) }
const edit = async (row:any)=>{ 
  dialogMode.value='edit'; 
  form.value={ 
    ...row,
    evaluation_rule: row.evaluation_rule || null,
    evaluation_indicators: row.evaluation_indicators || []
  }; 
  
  // 加载考核规则和指标数据
  try {
    await store.fetchEvaluationRules()
    await store.fetchIndicators()
  } catch (error) {
    console.error('加载考核规则和指标失败:', error)
  }
  
  dialogVisible.value=true 
}

const generateTasks = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要为"${row.name}"生成考核任务吗？`,
      '确认生成',
      { type: 'warning' }
    )
    
    await store.generateTasksForCycle(row.id)
    ElMessage.success('考核任务生成成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('生成任务失败:', error)
      ElMessage.error('生成任务失败，请重试')
    }
  }
}

const viewTasks = (row: any) => {
  // 跳转到评审任务页面，并筛选该周期的任务
  window.open(`/tasks?cycle=${row.id}`, '_blank')
}

const exportCodes = async (row: any) => {
  try {
    const { taskApi } = await import('@/utils/api')
    const response = await taskApi.exportEvaluatorCodes(row.id)
    
    // 创建下载链接
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `考核码分发表_${row.name}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('考核码Excel文件导出成功')
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error(`导出失败: ${error.response?.data?.error || error.message}`)
  }
}
// 表单验证相关方法
const handleFormValidate = (isValid: boolean, errors: any[]) => {
  console.log('表单验证结果:', { isValid, errors })
  if (!isValid) {
    ElMessage.warning(`表单验证失败，请检查 ${errors.length} 个错误`)
  }
}

const handleFormSubmit = async (formData: any) => {
  console.log('表单提交:', formData)
  await save()
}

const save = async ()=>{
  try {
    // 基础校验
    if (!form.value.name) return ElMessage.error('请填写名称')
    if (!form.value.start_date || !form.value.end_date) return ElMessage.error('请选择开始/结束日期')
    if (!form.value.evaluation_rule) return ElMessage.error('请选择考核规则')
    if (!form.value.evaluation_indicators || form.value.evaluation_indicators.length === 0) {
      return ElMessage.error('请选择至少一个考核指标')
    }
    
    // 格式化日期为字符串
    const formatDate = (date: any) => {
      if (date instanceof Date) {
        return date.toISOString().split('T')[0]
      }
      return date
    }
    
    const payload = { 
      name: form.value.name,
      description: form.value.description || '',
      start_date: formatDate(form.value.start_date),
      end_date: formatDate(form.value.end_date),
      status: form.value.status || 'draft',
      evaluation_rule: form.value.evaluation_rule,
      evaluation_indicators: form.value.evaluation_indicators
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
  } catch (e: any) {
    console.error('保存失败:', e)
    // 显示更详细的错误信息
    if (e.response?.data?.detail) {
      ElMessage.error(`保存失败: ${e.response.data.detail}`)
    } else if (e.response?.data?.non_field_errors) {
      ElMessage.error(`保存失败: ${e.response.data.non_field_errors.join(', ')}`)
    } else if (e.response?.data) {
      // 处理字段验证错误
      const errors = Object.values(e.response.data).flat()
      ElMessage.error(`保存失败: ${errors.join(', ')}`)
    } else {
      ElMessage.error('保存失败，请重试')
    }
  }
}

onMounted(()=>{ store.fetchCycles() })
</script>

<style scoped>
.toolbar { display: flex; gap: 8px; align-items: center; }
.row { display: flex; justify-content: space-between; align-items: center; }
.card { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.table-wrap { overflow-x: auto; }
.text-gray-400 { color: #9ca3af; }

/* 表单验证样式 */
.field-error-message {
  color: #f56565;
  font-size: 12px;
  margin-top: 4px;
  line-height: 1.4;
}

.is-error {
  border-color: #f56565 !important;
}

.is-error:focus {
  border-color: #f56565 !important;
  box-shadow: 0 0 0 2px rgba(245, 101, 101, 0.2) !important;
}

/* 表单验证组件样式增强 */
:deep(.el-form-item__error) {
  color: #f56565;
  font-size: 12px;
  line-height: 1.4;
  margin-top: 4px;
}

:deep(.el-input.is-error .el-input__wrapper) {
  border-color: #f56565;
  box-shadow: 0 0 0 1px #f56565;
}

:deep(.el-select.is-error .el-select__wrapper) {
  border-color: #f56565;
  box-shadow: 0 0 0 1px #f56565;
}

:deep(.el-date-editor.is-error) {
  border-color: #f56565;
  box-shadow: 0 0 0 1px #f56565;
}

/* 错误面板样式 */
:deep(.error-panel) {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  min-width: 300px;
}

:deep(.error-header) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fee2e2;
  border-bottom: 1px solid #fecaca;
  border-radius: 8px 8px 0 0;
  font-weight: 600;
  color: #dc2626;
}

:deep(.error-item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #fecaca;
}

:deep(.error-item:hover) {
  background: #fef2f2;
}

:deep(.error-item:last-child) {
  border-bottom: none;
}

/* 实时验证状态 */
:deep(.realtime-validation) {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 999;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 12px 16px;
}

:deep(.validation-status) {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

:deep(.status-icon.success) {
  color: #10b981;
}

:deep(.status-icon.error) {
  color: #ef4444;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.error-panel) {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
  
  :deep(.realtime-validation) {
    bottom: 10px;
    right: 10px;
    left: 10px;
  }
}

.action-buttons {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  min-width: 50px;
  height: 28px;
  font-size: 12px;
  padding: 4px 8px;
}
</style>
