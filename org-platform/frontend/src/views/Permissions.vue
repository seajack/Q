<template>
  <div class="permissions">
    <div class="page-header">
      <h1>权限管理</h1>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>
        添加权限
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
            <el-option label="菜单权限" value="menu" />
            <el-option label="按钮权限" value="button" />
            <el-option label="API权限" value="api" />
            <el-option label="数据权限" value="data" />
            <el-option label="字段权限" value="field" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterLevel" placeholder="权限级别" clearable @change="handleFilter">
            <el-option label="一级权限" :value="1" />
            <el-option label="二级权限" :value="2" />
            <el-option label="三级权限" :value="3" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 权限树形表格 -->
    <el-table 
      :data="permissions" 
      v-loading="loading" 
      stripe
      row-key="id"
      :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
    >
      <el-table-column prop="name" label="权限名称" min-width="200" />
      <el-table-column prop="code" label="权限编码" width="150" />
      <el-table-column prop="permission_type_display" label="权限类型" width="120" />
      <el-table-column prop="level" label="级别" width="80" />
      <el-table-column prop="resource" label="资源标识" width="150" show-overflow-tooltip />
      <el-table-column prop="action" label="操作类型" width="100" />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="addChild(row)">添加子权限</el-button>
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deletePermission(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑权限' : '添加权限'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入权限名称" />
        </el-form-item>

        <el-form-item label="权限编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入权限编码" />
        </el-form-item>

        <el-form-item label="权限类型" prop="permission_type">
          <el-select v-model="form.permission_type" placeholder="请选择权限类型">
            <el-option label="菜单权限" value="menu" />
            <el-option label="按钮权限" value="button" />
            <el-option label="API权限" value="api" />
            <el-option label="数据权限" value="data" />
            <el-option label="字段权限" value="field" />
          </el-select>
        </el-form-item>

        <el-form-item label="父权限" prop="parent">
          <el-tree-select
            v-model="form.parent"
            :data="permissionTree"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="请选择父权限"
            clearable
            check-strictly
          />
        </el-form-item>

        <el-form-item label="资源标识" prop="resource">
          <el-input v-model="form.resource" placeholder="如：/api/users" />
        </el-form-item>

        <el-form-item label="操作类型" prop="action">
          <el-input v-model="form.action" placeholder="如：read, write, delete" />
        </el-form-item>

        <el-form-item label="权限级别" prop="level">
          <el-input-number v-model="form.level" :min="1" :max="5" />
        </el-form-item>

        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" />
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
const permissions = ref([])
const permissionTree = ref([])
const searchQuery = ref('')
const filterType = ref('')
const filterLevel = ref('')

// 对话框
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

// 表单数据
const form = reactive({
  name: '',
  code: '',
  permission_type: '',
  parent: null,
  resource: '',
  action: '',
  level: 1,
  sort_order: 0,
  is_active: true,
  description: ''
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入权限名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入权限编码', trigger: 'blur' }],
  permission_type: [{ required: true, message: '请选择权限类型', trigger: 'change' }],
  level: [{ required: true, message: '请输入权限级别', trigger: 'blur' }]
}

// 方法
const loadPermissions = async () => {
  loading.value = true
  try {
    const params = {
      search: searchQuery.value,
      permission_type: filterType.value,
      level: filterLevel.value
    }
    const response = await api.get('/permission/permissions/', { params })
    permissions.value = response.data.results
  } catch (error) {
    ElMessage.error('加载权限列表失败')
  } finally {
    loading.value = false
  }
}

const loadPermissionTree = async () => {
  try {
    const response = await api.get('/permission/permissions/tree/')
    permissionTree.value = response.data
  } catch (error) {
    console.error('加载权限树失败:', error)
  }
}

const handleSearch = () => {
  loadPermissions()
}

const handleFilter = () => {
  loadPermissions()
}

const openCreate = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const addChild = (parent: any) => {
  isEdit.value = false
  resetForm()
  form.parent = parent.id
  form.level = parent.level + 1
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
    code: '',
    permission_type: '',
    parent: null,
    resource: '',
    action: '',
    level: 1,
    sort_order: 0,
    is_active: true,
    description: ''
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
    
    const url = isEdit.value ? `/permission/permissions/${form.id}/` : '/permission/permissions/'
    const method = isEdit.value ? 'put' : 'post'
    
    await api[method](url, form)
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadPermissions()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const deletePermission = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该权限吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/permission/permissions/${row.id}/`)
    ElMessage.success('删除成功')
    loadPermissions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 生命周期
onMounted(() => {
  loadPermissions()
  loadPermissionTree()
})
</script>

<style scoped>
.permissions {
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
</style>
