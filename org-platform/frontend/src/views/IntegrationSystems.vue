<template>
  <div class="integration-systems">
    <div class="page-header">
      <h1>集成系统管理</h1>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>
        添加系统
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索系统名称"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterType" placeholder="系统类型" clearable @change="handleFilter">
            <el-option label="绩效考核系统" value="performance" />
            <el-option label="OA系统" value="oa" />
            <el-option label="财务系统" value="finance" />
            <el-option label="CRM系统" value="crm" />
            <el-option label="ERP系统" value="erp" />
            <el-option label="人力资源系统" value="hr" />
            <el-option label="自定义系统" value="custom" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterStatus" placeholder="状态" clearable @change="handleFilter">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
            <el-option label="错误" value="error" />
            <el-option label="测试中" value="testing" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 系统列表 -->
    <el-table :data="systems" v-loading="loading" stripe>
      <el-table-column prop="name" label="系统名称" min-width="150" />
      <el-table-column prop="system_type_display" label="系统类型" width="120" />
      <el-table-column prop="base_url" label="系统地址" min-width="200" show-overflow-tooltip />
      <el-table-column prop="status_display" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ row.status_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="auth_type" label="认证类型" width="100" />
      <el-table-column prop="last_sync_time" label="最后同步" width="150">
        <template #default="{ row }">
          {{ row.last_sync_time ? formatDate(row.last_sync_time) : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="testConnection(row)">测试连接</el-button>
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteSystem(row)">删除</el-button>
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
      :title="isEdit ? '编辑系统' : '添加系统'"
      width="800px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="系统名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入系统名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="系统类型" prop="system_type">
              <el-select v-model="form.system_type" placeholder="请选择系统类型">
                <el-option label="绩效考核系统" value="performance" />
                <el-option label="OA系统" value="oa" />
                <el-option label="财务系统" value="finance" />
                <el-option label="CRM系统" value="crm" />
                <el-option label="ERP系统" value="erp" />
                <el-option label="人力资源系统" value="hr" />
                <el-option label="自定义系统" value="custom" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="系统地址" prop="base_url">
          <el-input v-model="form.base_url" placeholder="请输入系统地址，如：http://example.com" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="API版本" prop="api_version">
              <el-input v-model="form.api_version" placeholder="如：v1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="认证类型" prop="auth_type">
              <el-select v-model="form.auth_type" @change="handleAuthTypeChange">
                <el-option label="无认证" value="none" />
                <el-option label="基础认证" value="basic" />
                <el-option label="Token认证" value="token" />
                <el-option label="OAuth2" value="oauth2" />
                <el-option label="API Key" value="api_key" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 认证配置 -->
        <div v-if="form.auth_type !== 'none'" class="auth-config">
          <h4>认证配置</h4>
          <div v-if="form.auth_type === 'basic'">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名" prop="auth_config.username">
                  <el-input v-model="form.auth_config.username" placeholder="请输入用户名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="密码" prop="auth_config.password">
                  <el-input v-model="form.auth_config.password" type="password" placeholder="请输入密码" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          <div v-else-if="form.auth_type === 'token'">
            <el-form-item label="Token" prop="auth_config.token">
              <el-input v-model="form.auth_config.token" placeholder="请输入Token" />
            </el-form-item>
          </div>
          <div v-else-if="form.auth_type === 'api_key'">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="API Key" prop="auth_config.api_key">
                  <el-input v-model="form.auth_config.api_key" placeholder="请输入API Key" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Key名称" prop="auth_config.key_name">
                  <el-input v-model="form.auth_config.key_name" placeholder="如：X-API-Key" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </div>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="超时时间(秒)" prop="timeout">
              <el-input-number v-model="form.timeout" :min="1" :max="300" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="重试次数" prop="retry_count">
              <el-input-number v-model="form.retry_count" :min="0" :max="10" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="限流(请求/分钟)" prop="rate_limit">
              <el-input-number v-model="form.rate_limit" :min="1" :max="10000" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="启用同步">
              <el-switch v-model="form.sync_enabled" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="同步间隔(分钟)" prop="sync_interval">
              <el-input-number v-model="form.sync_interval" :min="1" :max="1440" :disabled="!form.sync_enabled" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="启用监控">
              <el-switch v-model="form.monitoring_enabled" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="健康检查地址" prop="health_check_url">
              <el-input v-model="form.health_check_url" placeholder="如：/health" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="告警邮箱" prop="alert_email">
          <el-input v-model="form.alert_email" placeholder="请输入告警邮箱" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入系统描述" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
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
  system_type: '',
  base_url: '',
  api_version: 'v1',
  auth_type: 'none',
  auth_config: {},
  timeout: 30,
  retry_count: 3,
  rate_limit: 100,
  sync_enabled: false,
  sync_interval: 60,
  monitoring_enabled: true,
  health_check_url: '',
  alert_email: '',
  description: ''
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入系统名称', trigger: 'blur' }],
  system_type: [{ required: true, message: '请选择系统类型', trigger: 'change' }],
  base_url: [{ required: true, message: '请输入系统地址', trigger: 'blur' }],
  'auth_config.username': [
    { required: true, message: '请输入用户名', trigger: 'blur', 
      validator: (rule: any, value: any, callback: any) => {
        if (form.auth_type === 'basic' && !value) {
          callback(new Error('基础认证需要用户名'))
        } else {
          callback()
        }
      }
    }
  ],
  'auth_config.password': [
    { required: true, message: '请输入密码', trigger: 'blur',
      validator: (rule: any, value: any, callback: any) => {
        if (form.auth_type === 'basic' && !value) {
          callback(new Error('基础认证需要密码'))
        } else {
          callback()
        }
      }
    }
  ],
  'auth_config.token': [
    { required: true, message: '请输入Token', trigger: 'blur',
      validator: (rule: any, value: any, callback: any) => {
        if (form.auth_type === 'token' && !value) {
          callback(new Error('Token认证需要Token'))
        } else {
          callback()
        }
      }
    }
  ],
  'auth_config.api_key': [
    { required: true, message: '请输入API Key', trigger: 'blur',
      validator: (rule: any, value: any, callback: any) => {
        if (form.auth_type === 'api_key' && !value) {
          callback(new Error('API Key认证需要API Key'))
        } else {
          callback()
        }
      }
    }
  ]
}

// 方法
const loadSystems = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
      system_type: filterType.value,
      status: filterStatus.value
    }
    const response = await api.get('/integration/systems/', { params })
    systems.value = response.results
    total.value = response.count
  } catch (error) {
    ElMessage.error('加载系统列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadSystems()
}

const handleFilter = () => {
  currentPage.value = 1
  loadSystems()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadSystems()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadSystems()
}

const openCreate = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const edit = (row: any) => {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

const resetForm = () => {
  Object.assign(form, {
    name: '',
    system_type: '',
    base_url: '',
    api_version: 'v1',
    auth_type: 'none',
    auth_config: {},
    timeout: 30,
    retry_count: 3,
    rate_limit: 100,
    sync_enabled: false,
    sync_interval: 60,
    monitoring_enabled: true,
    health_check_url: '',
    alert_email: '',
    description: ''
  })
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const handleAuthTypeChange = () => {
  form.auth_config = {}
}

const save = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    const url = isEdit.value ? `/integration/systems/${form.id}/` : '/integration/systems/'
    const method = isEdit.value ? 'put' : 'post'
    
    await api[method](url, form)
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadSystems()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const testConnection = async (row: any) => {
  try {
    const response = await api.post(`/integration/systems/${row.id}/test_connection/`)
    if (response.data.success) {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error(`连接测试失败: ${response.data.message}`)
    }
  } catch (error) {
    ElMessage.error('连接测试失败')
  }
}

const deleteSystem = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该系统吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/integration/systems/${row.id}/`)
    ElMessage.success('删除成功')
    loadSystems()
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
    testing: 'warning'
  }
  return statusMap[status] || 'info'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString()
}

// 生命周期
onMounted(() => {
  loadSystems()
})
</script>

<style scoped>
.integration-systems {
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

.auth-config {
  margin: 20px 0;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.auth-config h4 {
  margin: 0 0 15px 0;
  color: #606266;
}
</style>
