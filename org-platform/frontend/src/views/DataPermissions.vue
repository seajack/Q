<template>
  <div class="data-permissions">
    <div class="page-header">
      <h1>数据权限管理</h1>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>
        添加数据权限
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索权限名称"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterType" placeholder="权限类型" clearable @change="handleFilter">
            <el-option label="读取权限" value="read" />
            <el-option label="写入权限" value="write" />
            <el-option label="删除权限" value="delete" />
            <el-option label="导出权限" value="export" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterScope" placeholder="数据范围" clearable @change="handleFilter">
            <el-option label="全部数据" value="all" />
            <el-option label="本部门数据" value="dept" />
            <el-option label="本部门及下级数据" value="dept_and_child" />
            <el-option label="本人数据" value="self" />
            <el-option label="自定义范围" value="custom" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 数据权限列表 -->
    <el-table :data="dataPermissions" v-loading="loading" stripe>
      <el-table-column prop="name" label="权限名称" min-width="150" />
      <el-table-column prop="permission_type_display" label="权限类型" width="120" />
      <el-table-column prop="scope_type_display" label="数据范围" width="150" />
      <el-table-column prop="resource_type" label="资源类型" width="120" />
      <el-table-column prop="resource_id" label="资源ID" width="100" />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_by_name" label="创建者" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="150" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetails(row)">详情</el-button>
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deletePermission(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑数据权限' : '添加数据权限'"
      width="800px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="权限名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入权限名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="权限类型" prop="permission_type">
              <el-select v-model="form.permission_type" placeholder="请选择权限类型">
                <el-option label="读取权限" value="read" />
                <el-option label="写入权限" value="write" />
                <el-option label="删除权限" value="delete" />
                <el-option label="导出权限" value="export" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数据范围" prop="scope_type">
              <el-select v-model="form.scope_type" placeholder="请选择数据范围" @change="handleScopeChange">
                <el-option label="全部数据" value="all" />
                <el-option label="本部门数据" value="dept" />
                <el-option label="本部门及下级数据" value="dept_and_child" />
                <el-option label="本人数据" value="self" />
                <el-option label="自定义范围" value="custom" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="资源类型" prop="resource_type">
              <el-input v-model="form.resource_type" placeholder="如：employee, department" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="资源ID" prop="resource_id">
          <el-input v-model="form.resource_id" placeholder="可选，指定特定资源ID" />
        </el-form-item>

        <!-- 自定义范围配置 -->
        <el-form-item v-if="form.scope_type === 'custom'" label="自定义范围配置">
          <el-card>
            <el-form-item label="部门范围">
              <el-select v-model="form.custom_scope.departments" multiple placeholder="选择部门">
                <el-option
                  v-for="dept in departments"
                  :key="dept.id"
                  :label="dept.name"
                  :value="dept.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="用户范围">
              <el-select v-model="form.custom_scope.users" multiple placeholder="选择用户">
                <el-option
                  v-for="user in users"
                  :key="user.id"
                  :label="user.username"
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
          </el-card>
        </el-form-item>

        <!-- 字段权限配置 -->
        <el-form-item label="字段权限配置">
          <el-card>
            <div class="field-permissions">
              <div v-for="(field, index) in form.field_permissions" :key="index" class="field-item">
                <el-row :gutter="10">
                  <el-col :span="6">
                    <el-input v-model="field.name" placeholder="字段名" />
                  </el-col>
                  <el-col :span="4">
                    <el-select v-model="field.permission">
                      <el-option label="可见" value="visible" />
                      <el-option label="只读" value="readonly" />
                      <el-option label="隐藏" value="hidden" />
                      <el-option label="脱敏" value="masked" />
                    </el-select>
                  </el-col>
                  <el-col :span="4">
                    <el-input v-model="field.masking_rule" placeholder="脱敏规则" />
                  </el-col>
                  <el-col :span="4">
                    <el-button @click="removeField(index)" type="danger" size="small">删除</el-button>
                  </el-col>
                </el-row>
              </div>
              <el-button @click="addField" type="primary" size="small">添加字段</el-button>
            </div>
          </el-card>
        </el-form-item>

        <!-- 数据脱敏配置 -->
        <el-form-item label="数据脱敏配置">
          <el-card>
            <div class="data-masking">
              <el-form-item label="手机号脱敏">
                <el-switch v-model="form.data_masking.phone" />
              </el-form-item>
              <el-form-item label="邮箱脱敏">
                <el-switch v-model="form.data_masking.email" />
              </el-form-item>
              <el-form-item label="身份证脱敏">
                <el-switch v-model="form.data_masking.id_card" />
              </el-form-item>
              <el-form-item label="自定义脱敏规则">
                <el-input v-model="form.data_masking.custom_rule" placeholder="自定义脱敏规则" />
              </el-form-item>
            </div>
          </el-card>
        </el-form-item>

        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入权限描述" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="数据权限详情"
      width="600px"
    >
      <div v-if="currentPermission">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="权限名称">{{ currentPermission.name }}</el-descriptions-item>
          <el-descriptions-item label="权限类型">{{ currentPermission.permission_type_display }}</el-descriptions-item>
          <el-descriptions-item label="数据范围">{{ currentPermission.scope_type_display }}</el-descriptions-item>
          <el-descriptions-item label="资源类型">{{ currentPermission.resource_type }}</el-descriptions-item>
          <el-descriptions-item label="资源ID">{{ currentPermission.resource_id || '全部' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentPermission.is_active ? 'success' : 'info'">
              {{ currentPermission.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建者">{{ currentPermission.created_by_name }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentPermission.created_at }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="currentPermission.field_permissions && Object.keys(currentPermission.field_permissions).length > 0">
          <h4>字段权限配置</h4>
          <el-table :data="Object.entries(currentPermission.field_permissions)" size="small">
            <el-table-column prop="0" label="字段名" />
            <el-table-column prop="1" label="权限类型" />
          </el-table>
        </div>

        <div v-if="currentPermission.data_masking && Object.keys(currentPermission.data_masking).length > 0">
          <h4>数据脱敏配置</h4>
          <el-table :data="Object.entries(currentPermission.data_masking)" size="small">
            <el-table-column prop="0" label="脱敏类型" />
            <el-table-column prop="1" label="配置" />
          </el-table>
        </div>
      </div>
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
const dataPermissions = ref([])
const departments = ref([])
const users = ref([])
const searchQuery = ref('')
const filterType = ref('')
const filterScope = ref('')

// 对话框
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const currentPermission = ref(null)

// 表单数据
const form = reactive({
  name: '',
  permission_type: '',
  scope_type: '',
  resource_type: '',
  resource_id: '',
  custom_scope: {
    departments: [],
    users: []
  },
  field_permissions: [],
  data_masking: {
    phone: false,
    email: false,
    id_card: false,
    custom_rule: ''
  },
  is_active: true,
  description: ''
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入权限名称', trigger: 'blur' }],
  permission_type: [{ required: true, message: '请选择权限类型', trigger: 'change' }],
  scope_type: [{ required: true, message: '请选择数据范围', trigger: 'change' }],
  resource_type: [{ required: true, message: '请输入资源类型', trigger: 'blur' }]
}

// 方法
const loadDataPermissions = async () => {
  loading.value = true
  try {
    const params = {
      search: searchQuery.value,
      permission_type: filterType.value,
      scope_type: filterScope.value
    }
    const response = await api.get('/permission/data-permissions/', { params })
    dataPermissions.value = response.data.results
  } catch (error) {
    ElMessage.error('加载数据权限列表失败')
  } finally {
    loading.value = false
  }
}

const loadDepartments = async () => {
  try {
    const response = await api.get('/api/departments/')
    departments.value = response.data.results
  } catch (error) {
    console.error('加载部门列表失败:', error)
  }
}

const loadUsers = async () => {
  try {
    const response = await api.get('/api/users/')
    users.value = response.data.results
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

const handleSearch = () => {
  loadDataPermissions()
}

const handleFilter = () => {
  loadDataPermissions()
}

const handleScopeChange = (value: string) => {
  if (value !== 'custom') {
    form.custom_scope = { departments: [], users: [] }
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

const viewDetails = (row: any) => {
  currentPermission.value = row
  detailDialogVisible.value = true
}

const resetForm = () => {
  Object.assign(form, {
    name: '',
    permission_type: '',
    scope_type: '',
    resource_type: '',
    resource_id: '',
    custom_scope: {
      departments: [],
      users: []
    },
    field_permissions: [],
    data_masking: {
      phone: false,
      email: false,
      id_card: false,
      custom_rule: ''
    },
    is_active: true,
    description: ''
  })
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const addField = () => {
  form.field_permissions.push({
    name: '',
    permission: 'visible',
    masking_rule: ''
  })
}

const removeField = (index: number) => {
  form.field_permissions.splice(index, 1)
}

const save = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    const url = isEdit.value ? `/permission/data-permissions/${form.id}/` : '/permission/data-permissions/'
    const method = isEdit.value ? 'put' : 'post'
    
    await api[method](url, form)
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadDataPermissions()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const deletePermission = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该数据权限吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/permission/data-permissions/${row.id}/`)
    ElMessage.success('删除成功')
    loadDataPermissions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 生命周期
onMounted(() => {
  loadDataPermissions()
  loadDepartments()
  loadUsers()
})
</script>

<style scoped>
.data-permissions {
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

.field-permissions {
  max-height: 300px;
  overflow-y: auto;
}

.field-item {
  margin-bottom: 10px;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.data-masking {
  padding: 10px;
}
</style>
