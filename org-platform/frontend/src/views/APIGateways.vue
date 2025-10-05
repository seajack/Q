<template>
  <div class="api-gateways">
    <div class="page-header">
      <h1>API网关管理</h1>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>
        添加网关
      </el-button>
    </div>

    <!-- 网关列表 -->
    <el-table :data="gateways" v-loading="loading" stripe>
      <el-table-column prop="name" label="网关名称" min-width="150" />
      <el-table-column prop="base_url" label="网关地址" min-width="200" show-overflow-tooltip />
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column label="路由数量" width="100">
        <template #default="{ row }">
          <el-tag>{{ row.route_count }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="活跃路由" width="100">
        <template #default="{ row }">
          <el-tag type="success">{{ row.active_route_count }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewRoutes(row)">查看路由</el-button>
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteGateway(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑网关' : '添加网关'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="网关名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入网关名称" />
        </el-form-item>

        <el-form-item label="网关地址" prop="base_url">
          <el-input v-model="form.base_url" placeholder="请输入网关地址" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>

        <el-divider content-position="left">限流配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="启用限流">
              <el-switch v-model="form.rate_limit_enabled" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="每分钟限制" prop="rate_limit_per_minute">
              <el-input-number v-model="form.rate_limit_per_minute" :min="1" :max="10000" :disabled="!form.rate_limit_enabled" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="每小时限制" prop="rate_limit_per_hour">
          <el-input-number v-model="form.rate_limit_per_hour" :min="1" :max="100000" :disabled="!form.rate_limit_enabled" />
        </el-form-item>

        <el-divider content-position="left">监控配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="启用监控">
              <el-switch v-model="form.monitoring_enabled" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="日志级别" prop="log_level">
              <el-select v-model="form.log_level">
                <el-option label="Debug" value="debug" />
                <el-option label="Info" value="info" />
                <el-option label="Warning" value="warning" />
                <el-option label="Error" value="error" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">安全配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="启用CORS">
              <el-switch v-model="form.cors_enabled" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="需要API Key">
              <el-switch v-model="form.api_key_required" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="CORS源" v-if="form.cors_enabled">
          <el-input v-model="corsOriginsText" type="textarea" :rows="3" placeholder="每行一个源，如：http://localhost:3000" />
        </el-form-item>

        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 路由管理对话框 -->
    <el-dialog
      v-model="routesDialogVisible"
      :title="`${selectedGateway?.name} - 路由管理`"
      width="1200px"
    >
      <div class="routes-header">
        <el-button type="primary" @click="openCreateRoute">
          <el-icon><Plus /></el-icon>
          添加路由
        </el-button>
      </div>

      <el-table :data="routes" v-loading="routesLoading" stripe>
        <el-table-column prop="name" label="路由名称" min-width="150" />
        <el-table-column prop="path" label="路径" min-width="150" />
        <el-table-column prop="method" label="方法" width="80">
          <template #default="{ row }">
            <el-tag :type="getMethodType(row.method)">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_url" label="目标地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="rate_limit" label="限流" width="80" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="testRoute(row)">测试</el-button>
            <el-button size="small" @click="editRoute(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteRoute(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 路由创建/编辑对话框 -->
      <el-dialog
        v-model="routeDialogVisible"
        :title="isEditRoute ? '编辑路由' : '添加路由'"
        width="800px"
        append-to-body
        @close="resetRouteForm"
      >
        <el-form :model="routeForm" :rules="routeRules" ref="routeFormRef" label-width="120px">
          <el-form-item label="路由名称" prop="name">
            <el-input v-model="routeForm.name" placeholder="请输入路由名称" />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="路径" prop="path">
                <el-input v-model="routeForm.path" placeholder="如：/api/users" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="请求方法" prop="method">
                <el-select v-model="routeForm.method">
                  <el-option label="GET" value="GET" />
                  <el-option label="POST" value="POST" />
                  <el-option label="PUT" value="PUT" />
                  <el-option label="DELETE" value="DELETE" />
                  <el-option label="PATCH" value="PATCH" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="目标地址" prop="target_url">
            <el-input v-model="routeForm.target_url" placeholder="请输入目标地址" />
          </el-form-item>

          <el-divider content-position="left">限流配置</el-divider>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="限流(请求/分钟)" prop="rate_limit">
                <el-input-number v-model="routeForm.rate_limit" :min="1" :max="10000" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="突发限制" prop="burst_limit">
                <el-input-number v-model="routeForm.burst_limit" :min="1" :max="10000" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">缓存配置</el-divider>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="启用缓存">
                <el-switch v-model="routeForm.cache_enabled" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="缓存时间(秒)" prop="cache_ttl">
                <el-input-number v-model="routeForm.cache_ttl" :min="1" :max="3600" :disabled="!routeForm.cache_enabled" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">认证配置</el-divider>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="需要认证">
                <el-switch v-model="routeForm.auth_required" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态">
                <el-switch v-model="routeForm.is_active" active-text="启用" inactive-text="禁用" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <template #footer>
          <el-button @click="routeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRoute" :loading="routeSaving">保存</el-button>
        </template>
      </el-dialog>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const gateways = ref([])

// 对话框
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

// 表单数据
const form = reactive({
  name: '',
  base_url: '',
  description: '',
  rate_limit_enabled: true,
  rate_limit_per_minute: 1000,
  rate_limit_per_hour: 10000,
  monitoring_enabled: true,
  log_level: 'info',
  cors_enabled: true,
  cors_origins: [],
  api_key_required: false,
  is_active: true
})

// CORS源文本
const corsOriginsText = computed({
  get: () => form.cors_origins.join('\n'),
  set: (value: string) => {
    form.cors_origins = value.split('\n').filter(item => item.trim())
  }
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入网关名称', trigger: 'blur' }],
  base_url: [{ required: true, message: '请输入网关地址', trigger: 'blur' }]
}

// 路由相关
const routesDialogVisible = ref(false)
const selectedGateway = ref(null)
const routes = ref([])
const routesLoading = ref(false)
const routeDialogVisible = ref(false)
const isEditRoute = ref(false)
const routeSaving = ref(false)
const routeFormRef = ref()

const routeForm = reactive({
  name: '',
  path: '',
  method: 'GET',
  target_url: '',
  rate_limit: 100,
  burst_limit: 200,
  cache_enabled: false,
  cache_ttl: 300,
  auth_required: true,
  is_active: true
})

const routeRules = {
  name: [{ required: true, message: '请输入路由名称', trigger: 'blur' }],
  path: [{ required: true, message: '请输入路径', trigger: 'blur' }],
  method: [{ required: true, message: '请选择请求方法', trigger: 'change' }],
  target_url: [{ required: true, message: '请输入目标地址', trigger: 'blur' }]
}

// 方法
const loadGateways = async () => {
  loading.value = true
  try {
    const response = await api.get('/integration/gateways/')
    gateways.value = response.results
  } catch (error) {
    ElMessage.error('加载网关列表失败')
  } finally {
    loading.value = false
  }
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
    base_url: '',
    description: '',
    rate_limit_enabled: true,
    rate_limit_per_minute: 1000,
    rate_limit_per_hour: 10000,
    monitoring_enabled: true,
    log_level: 'info',
    cors_enabled: true,
    cors_origins: [],
    api_key_required: false,
    is_active: true
  })
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const save = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    const url = isEdit.value ? `/integration/gateways/${form.id}/` : '/integration/gateways/'
    const method = isEdit.value ? 'put' : 'post'
    
    await api[method](url, form)
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadGateways()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const deleteGateway = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该网关吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/integration/gateways/${row.id}/`)
    ElMessage.success('删除成功')
    loadGateways()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const viewRoutes = async (gateway: any) => {
  selectedGateway.value = gateway
  routesDialogVisible.value = true
  await loadRoutes(gateway.id)
}

const loadRoutes = async (gatewayId: number) => {
  routesLoading.value = true
  try {
    const response = await api.get(`/integration/gateways/${gatewayId}/routes/`)
    routes.value = response.data
  } catch (error) {
    ElMessage.error('加载路由列表失败')
  } finally {
    routesLoading.value = false
  }
}

const openCreateRoute = () => {
  isEditRoute.value = false
  resetRouteForm()
  routeDialogVisible.value = true
}

const editRoute = (row: any) => {
  isEditRoute.value = true
  Object.assign(routeForm, row)
  routeDialogVisible.value = true
}

const resetRouteForm = () => {
  Object.assign(routeForm, {
    name: '',
    path: '',
    method: 'GET',
    target_url: '',
    rate_limit: 100,
    burst_limit: 200,
    cache_enabled: false,
    cache_ttl: 300,
    auth_required: true,
    is_active: true
  })
  if (routeFormRef.value) {
    routeFormRef.value.resetFields()
  }
}

const saveRoute = async () => {
  if (!routeFormRef.value) return
  
  try {
    await routeFormRef.value.validate()
    routeSaving.value = true
    
    const data = { ...routeForm, gateway: selectedGateway.value.id }
    const url = isEditRoute.value ? `/integration/routes/${routeForm.id}/` : '/integration/routes/'
    const method = isEditRoute.value ? 'put' : 'post'
    
    await api[method](url, data)
    ElMessage.success(isEditRoute.value ? '更新成功' : '创建成功')
    routeDialogVisible.value = false
    loadRoutes(selectedGateway.value.id)
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    routeSaving.value = false
  }
}

const testRoute = async (row: any) => {
  try {
    const response = await api.post(`/integration/routes/${row.id}/test_route/`, {
      data: { test: 'data' }
    })
    if (response.data.success) {
      ElMessage.success('路由测试成功')
    } else {
      ElMessage.error(`路由测试失败: ${response.data.error}`)
    }
  } catch (error) {
    ElMessage.error('路由测试失败')
  }
}

const deleteRoute = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该路由吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/integration/routes/${row.id}/`)
    ElMessage.success('删除成功')
    loadRoutes(selectedGateway.value.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getMethodType = (method: string) => {
  const methodMap: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return methodMap[method] || 'info'
}

// 生命周期
onMounted(() => {
  loadGateways()
})
</script>

<style scoped>
.api-gateways {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.routes-header {
  margin-bottom: 20px;
}
</style>
