<template>
  <div class="data-sync-rules">
    <div class="page-header">
      <h1>数据同步规则</h1>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>
        添加同步规则
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索规则名称"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterType" placeholder="同步类型" clearable @change="handleFilter">
            <el-option label="实时同步" value="realtime" />
            <el-option label="批量同步" value="batch" />
            <el-option label="定时同步" value="scheduled" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterStatus" placeholder="状态" clearable @change="handleFilter">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
            <el-option label="错误" value="error" />
            <el-option label="运行中" value="running" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 同步规则列表 -->
    <el-table :data="syncRules" v-loading="loading" stripe>
      <el-table-column prop="name" label="规则名称" min-width="150" />
      <el-table-column prop="source_system_name" label="源系统" width="120" />
      <el-table-column prop="target_system_name" label="目标系统" width="120" />
      <el-table-column prop="sync_type_display" label="同步类型" width="100" />
      <el-table-column prop="status_display" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ row.status_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="source_table" label="源表" width="120" />
      <el-table-column prop="target_table" label="目标表" width="120" />
      <el-table-column prop="batch_size" label="批次大小" width="100" />
      <el-table-column prop="sync_interval" label="同步间隔(分钟)" width="120" />
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="executeSync(row)">执行同步</el-button>
          <el-button size="small" @click="viewLogs(row)">查看日志</el-button>
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteRule(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑同步规则' : '添加同步规则'"
      width="1000px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规则名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入规则名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="同步类型" prop="sync_type">
              <el-select v-model="form.sync_type" placeholder="请选择同步类型">
                <el-option label="实时同步" value="realtime" />
                <el-option label="批量同步" value="batch" />
                <el-option label="定时同步" value="scheduled" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="源系统" prop="source_system">
              <el-select v-model="form.source_system" placeholder="请选择源系统">
                <el-option
                  v-for="system in systems"
                  :key="system.id"
                  :label="system.name"
                  :value="system.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标系统" prop="target_system">
              <el-select v-model="form.target_system" placeholder="请选择目标系统">
                <el-option
                  v-for="system in systems"
                  :key="system.id"
                  :label="system.name"
                  :value="system.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="源表名" prop="source_table">
              <el-input v-model="form.source_table" placeholder="请输入源表名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标表名" prop="target_table">
              <el-input v-model="form.target_table" placeholder="请输入目标表名" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">字段映射</el-divider>
        <div class="field-mapping">
          <div v-for="(mapping, index) in fieldMappings" :key="index" class="mapping-item">
            <el-row :gutter="10">
              <el-col :span="10">
                <el-input v-model="mapping.source" placeholder="源字段" />
              </el-col>
              <el-col :span="2" style="text-align: center; line-height: 32px;">
                →
              </el-col>
              <el-col :span="10">
                <el-input v-model="mapping.target" placeholder="目标字段" />
              </el-col>
              <el-col :span="2">
                <el-button type="danger" size="small" @click="removeMapping(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-col>
            </el-row>
          </div>
          <el-button type="primary" size="small" @click="addMapping">
            <el-icon><Plus /></el-icon>
            添加映射
          </el-button>
        </div>

        <el-divider content-position="left">同步配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="批次大小" prop="batch_size">
              <el-input-number v-model="form.batch_size" :min="1" :max="10000" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="同步间隔(分钟)" prop="sync_interval">
              <el-input-number v-model="form.sync_interval" :min="1" :max="1440" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="最大重试次数" prop="max_retry_count">
              <el-input-number v-model="form.max_retry_count" :min="0" :max="10" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">数据清洗</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="启用数据清洗">
              <el-switch v-model="form.data_cleaning_enabled" />
            </el-form-item>
          </el-col>
        </el-row>

        <div v-if="form.data_cleaning_enabled" class="cleaning-rules">
          <h4>清洗规则</h4>
          <div v-for="(rule, index) in cleaningRules" :key="index" class="rule-item">
            <el-row :gutter="10">
              <el-col :span="6">
                <el-input v-model="rule.field" placeholder="字段名" />
              </el-col>
              <el-col :span="6">
                <el-select v-model="rule.type" placeholder="规则类型">
                  <el-option label="去除空格" value="trim" />
                  <el-option label="转小写" value="lowercase" />
                  <el-option label="转大写" value="uppercase" />
                  <el-option label="移除特殊字符" value="remove_special_chars" />
                  <el-option label="默认值" value="default_value" />
                </el-select>
              </el-col>
              <el-col :span="6" v-if="rule.type === 'default_value'">
                <el-input v-model="rule.value" placeholder="默认值" />
              </el-col>
              <el-col :span="6">
                <el-button type="danger" size="small" @click="removeCleaningRule(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-col>
            </el-row>
          </div>
          <el-button type="primary" size="small" @click="addCleaningRule">
            <el-icon><Plus /></el-icon>
            添加清洗规则
          </el-button>
        </div>

        <el-divider content-position="left">数据校验</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="启用数据校验">
              <el-switch v-model="form.validation_enabled" />
            </el-form-item>
          </el-col>
        </el-row>

        <div v-if="form.validation_enabled" class="validation-rules">
          <h4>校验规则</h4>
          <div v-for="(rule, index) in validationRules" :key="index" class="rule-item">
            <el-row :gutter="10">
              <el-col :span="6">
                <el-input v-model="rule.field" placeholder="字段名" />
              </el-col>
              <el-col :span="6">
                <el-select v-model="rule.type" placeholder="规则类型">
                  <el-option label="必填" value="required" />
                  <el-option label="邮箱" value="email" />
                  <el-option label="手机号" value="phone" />
                  <el-option label="长度" value="length" />
                </el-select>
              </el-col>
              <el-col :span="6" v-if="rule.type === 'length'">
                <el-input v-model="rule.min_length" placeholder="最小长度" />
              </el-col>
              <el-col :span="6" v-if="rule.type === 'length'">
                <el-input v-model="rule.max_length" placeholder="最大长度" />
              </el-col>
              <el-col :span="6">
                <el-button type="danger" size="small" @click="removeValidationRule(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-col>
            </el-row>
          </div>
          <el-button type="primary" size="small" @click="addValidationRule">
            <el-icon><Plus /></el-icon>
            添加校验规则
          </el-button>
        </div>

        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 同步日志对话框 -->
    <el-dialog
      v-model="logsDialogVisible"
      :title="`${selectedRule?.name} - 同步日志`"
      width="1200px"
    >
      <el-table :data="syncLogs" v-loading="logsLoading" stripe>
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="150" />
        <el-table-column prop="end_time" label="结束时间" width="150" />
        <el-table-column prop="duration_formatted" label="耗时" width="100" />
        <el-table-column prop="total_records" label="总记录数" width="100" />
        <el-table-column prop="success_records" label="成功记录数" width="100" />
        <el-table-column prop="error_records" label="错误记录数" width="100" />
        <el-table-column prop="records_per_second" label="每秒记录数" width="100" />
        <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Delete } from '@element-plus/icons-vue'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const syncRules = ref([])
const systems = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const filterType = ref('')
const filterStatus = ref('')

// 对话框
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

// 表单数据
const form = reactive({
  name: '',
  source_system: '',
  target_system: '',
  sync_type: 'batch',
  source_table: '',
  target_table: '',
  field_mapping: {},
  filter_conditions: {},
  batch_size: 1000,
  sync_interval: 60,
  max_retry_count: 3,
  data_cleaning_enabled: true,
  cleaning_rules: [],
  validation_enabled: true,
  validation_rules: [],
  monitoring_enabled: true,
  alert_on_error: true,
  alert_on_delay: true,
  delay_threshold: 30,
  description: ''
})

// 字段映射
const fieldMappings = ref([])

// 清洗规则
const cleaningRules = ref([])

// 校验规则
const validationRules = ref([])

// 同步日志
const logsDialogVisible = ref(false)
const selectedRule = ref(null)
const syncLogs = ref([])
const logsLoading = ref(false)

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  source_system: [{ required: true, message: '请选择源系统', trigger: 'change' }],
  target_system: [{ required: true, message: '请选择目标系统', trigger: 'change' }],
  sync_type: [{ required: true, message: '请选择同步类型', trigger: 'change' }],
  source_table: [{ required: true, message: '请输入源表名', trigger: 'blur' }],
  target_table: [{ required: true, message: '请输入目标表名', trigger: 'blur' }]
}

// 方法
const loadSyncRules = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
      sync_type: filterType.value,
      status: filterStatus.value
    }
    const response = await api.get('/integration/sync-rules/', { params })
    syncRules.value = response.results
    total.value = response.count
  } catch (error) {
    ElMessage.error('加载同步规则失败')
  } finally {
    loading.value = false
  }
}

const loadSystems = async () => {
  try {
    const response = await api.get('/integration/systems/')
    systems.value = response.results
  } catch (error) {
    ElMessage.error('加载系统列表失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadSyncRules()
}

const handleFilter = () => {
  currentPage.value = 1
  loadSyncRules()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadSyncRules()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadSyncRules()
}

const openCreate = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const edit = (row: any) => {
  isEdit.value = true
  Object.assign(form, row)
  
  // 处理字段映射
  fieldMappings.value = Object.entries(row.field_mapping || {}).map(([source, target]) => ({
    source,
    target
  }))
  
  // 处理清洗规则
  cleaningRules.value = row.cleaning_rules || []
  
  // 处理校验规则
  validationRules.value = row.validation_rules || []
  
  dialogVisible.value = true
}

const resetForm = () => {
  Object.assign(form, {
    name: '',
    source_system: '',
    target_system: '',
    sync_type: 'batch',
    source_table: '',
    target_table: '',
    field_mapping: {},
    filter_conditions: {},
    batch_size: 1000,
    sync_interval: 60,
    max_retry_count: 3,
    data_cleaning_enabled: true,
    cleaning_rules: [],
    validation_enabled: true,
    validation_rules: [],
    monitoring_enabled: true,
    alert_on_error: true,
    alert_on_delay: true,
    delay_threshold: 30,
    description: ''
  })
  
  fieldMappings.value = []
  cleaningRules.value = []
  validationRules.value = []
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const addMapping = () => {
  fieldMappings.value.push({ source: '', target: '' })
}

const removeMapping = (index: number) => {
  fieldMappings.value.splice(index, 1)
}

const addCleaningRule = () => {
  cleaningRules.value.push({ field: '', type: '', value: '' })
}

const removeCleaningRule = (index: number) => {
  cleaningRules.value.splice(index, 1)
}

const addValidationRule = () => {
  validationRules.value.push({ field: '', type: '', min_length: '', max_length: '' })
}

const removeValidationRule = (index: number) => {
  validationRules.value.splice(index, 1)
}

const save = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    // 处理字段映射
    const fieldMapping = {}
    fieldMappings.value.forEach(mapping => {
      if (mapping.source && mapping.target) {
        fieldMapping[mapping.source] = mapping.target
      }
    })
    form.field_mapping = fieldMapping
    
    // 处理清洗规则
    form.cleaning_rules = cleaningRules.value.filter(rule => rule.field && rule.type)
    
    // 处理校验规则
    form.validation_rules = validationRules.value.filter(rule => rule.field && rule.type)
    
    const url = isEdit.value ? `/integration/sync-rules/${form.id}/` : '/integration/sync-rules/'
    const method = isEdit.value ? 'put' : 'post'
    
    await api[method](url, form)
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadSyncRules()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const executeSync = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要执行该同步规则吗？', '确认执行', {
      type: 'warning'
    })
    
    const response = await api.post(`/integration/sync-rules/${row.id}/execute_sync/`)
    if (response.success) {
      ElMessage.success('同步执行成功')
    } else {
      ElMessage.error(`同步执行失败: ${response.error}`)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('同步执行失败')
    }
  }
}

const viewLogs = async (row: any) => {
  selectedRule.value = row
  logsDialogVisible.value = true
  await loadSyncLogs(row.id)
}

const loadSyncLogs = async (ruleId: number) => {
  logsLoading.value = true
  try {
    const response = await api.get(`/integration/sync-rules/${ruleId}/sync_logs/`)
    syncLogs.value = response.data
  } catch (error) {
    ElMessage.error('加载同步日志失败')
  } finally {
    logsLoading.value = false
  }
}

const deleteRule = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该同步规则吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/integration/sync-rules/${row.id}/`)
    ElMessage.success('删除成功')
    loadSyncRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    error: 'danger',
    running: 'warning'
  }
  return statusMap[status] || 'info'
}

// 生命周期
onMounted(() => {
  loadSyncRules()
  loadSystems()
})
</script>

<style scoped>
.data-sync-rules {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-section {
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 4px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.field-mapping,
.cleaning-rules,
.validation-rules {
  margin: 15px 0;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.mapping-item,
.rule-item {
  margin-bottom: 10px;
}

.mapping-item:last-child,
.rule-item:last-child {
  margin-bottom: 0;
}
</style>
