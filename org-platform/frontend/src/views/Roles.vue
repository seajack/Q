<template>
  <div class="roles">
    <div class="page-header">
      <h1>角色管理</h1>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>
        添加角色
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索角色名称"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterType" placeholder="角色类型" clearable @change="handleFilter">
            <el-option label="系统角色" value="system" />
            <el-option label="自定义角色" value="custom" />
            <el-option label="部门角色" value="department" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterStatus" placeholder="状态" clearable @change="handleFilter">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 角色列表 -->
    <el-table :data="roles" v-loading="loading" stripe>
      <el-table-column prop="name" label="角色名称" min-width="150" />
      <el-table-column prop="code" label="角色编码" width="150" />
      <el-table-column prop="role_type_display" label="角色类型" width="120" />
      <el-table-column prop="level" label="级别" width="80" />
      <el-table-column prop="data_scope_display" label="数据权限" width="120" />
      <el-table-column prop="permissions_count" label="权限数量" width="100" />
      <el-table-column prop="users_count" label="用户数量" width="100" />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewPermissions(row)">权限</el-button>
          <el-button size="small" @click="viewUsers(row)">用户</el-button>
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteRole(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑角色' : '添加角色'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>

        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入角色编码" />
        </el-form-item>

        <el-form-item label="角色类型" prop="role_type">
          <el-select v-model="form.role_type" placeholder="请选择角色类型">
            <el-option label="系统角色" value="system" />
            <el-option label="自定义角色" value="custom" />
            <el-option label="部门角色" value="department" />
          </el-select>
        </el-form-item>

        <el-form-item label="父角色" prop="parent_role">
          <el-select v-model="form.parent_role" placeholder="请选择父角色" clearable>
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="数据权限范围" prop="data_scope">
          <el-select v-model="form.data_scope" placeholder="请选择数据权限范围">
            <el-option label="全部数据权限" value="all" />
            <el-option label="自定义数据权限" value="custom" />
            <el-option label="本部门数据权限" value="dept" />
            <el-option label="本部门及以下数据权限" value="dept_and_child" />
            <el-option label="仅本人数据权限" value="self" />
          </el-select>
        </el-form-item>

        <el-form-item label="角色级别" prop="level">
          <el-input-number v-model="form.level" :min="1" :max="10" />
        </el-form-item>

        <el-form-item label="继承父角色权限">
          <el-switch v-model="form.inherit_permissions" />
        </el-form-item>

        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入角色描述" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 权限分配对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="权限分配"
      width="800px"
    >
      <div class="permission-assignment">
        <div class="permission-tree">
          <el-tree
            ref="permissionTreeRef"
            :data="permissionTree"
            :props="{ label: 'name', children: 'children' }"
            show-checkbox
            node-key="id"
            :default-checked-keys="selectedPermissions"
            @check="handlePermissionCheck"
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePermissions" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 用户分配对话框 -->
    <el-dialog
      v-model="userDialogVisible"
      title="用户分配"
      width="600px"
    >
      <div class="user-assignment">
        <el-transfer
          v-model="selectedUsers"
          :data="allUsers"
          :titles="['可选用户', '已选用户']"
          :button-texts="['移除', '添加']"
          filterable
        />
      </div>

      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUsers" :loading="saving">保存</el-button>
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
const roles = ref([])
const permissionTree = ref([])
const allUsers = ref([])
const searchQuery = ref('')
const filterType = ref('')
const filterStatus = ref('')

// 对话框
const dialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const userDialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const permissionTreeRef = ref()

// 当前操作的角色
const currentRole = ref(null)
const selectedPermissions = ref([])
const selectedUsers = ref([])

// 表单数据
const form = reactive({
  name: '',
  code: '',
  role_type: 'custom',
  parent_role: null,
  data_scope: 'self',
  level: 1,
  inherit_permissions: true,
  is_active: true,
  description: ''
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
  role_type: [{ required: true, message: '请选择角色类型', trigger: 'change' }],
  data_scope: [{ required: true, message: '请选择数据权限范围', trigger: 'change' }],
  level: [{ required: true, message: '请输入角色级别', trigger: 'blur' }]
}

// 方法
const loadRoles = async () => {
  loading.value = true
  try {
    const params = {
      search: searchQuery.value,
      role_type: filterType.value,
      is_active: filterStatus.value
    }
    const response = await api.get('/permission/roles/', { params })
    roles.value = response.results
  } catch (error) {
    ElMessage.error('加载角色列表失败')
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

const loadUsers = async () => {
  try {
    const response = await api.get('/simple-permission/users/')
    allUsers.value = response.data.map(user => ({
      key: user.id,
      label: user.username,
      disabled: false
    }))
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

const handleSearch = () => {
  loadRoles()
}

const handleFilter = () => {
  loadRoles()
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
    code: '',
    role_type: 'custom',
    parent_role: null,
    data_scope: 'self',
    level: 1,
    inherit_permissions: true,
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
    
    const url = isEdit.value ? `/permission/roles/${form.id}/` : '/permission/roles/'
    const method = isEdit.value ? 'put' : 'post'
    
    await api[method](url, form)
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadRoles()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const deleteRole = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该角色吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/permission/roles/${row.id}/`)
    ElMessage.success('删除成功')
    loadRoles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const viewPermissions = async (row: any) => {
  currentRole.value = row
  try {
    const response = await api.get(`/permission/roles/${row.id}/permissions/`)
    selectedPermissions.value = response.data.map(p => p.permission)
  } catch (error) {
    ElMessage.error('加载权限失败')
  }
  permissionDialogVisible.value = true
}

const viewUsers = async (row: any) => {
  currentRole.value = row
  try {
    const response = await api.get(`/permission/roles/${row.id}/users/`)
    selectedUsers.value = response.data.map(ur => ur.user)
  } catch (error) {
    ElMessage.error('加载用户失败')
  }
  userDialogVisible.value = true
}

const handlePermissionCheck = (data: any, checked: any) => {
  // 处理权限选择
}

const savePermissions = async () => {
  try {
    saving.value = true
    const permissionIds = permissionTreeRef.value.getCheckedKeys()
    
    await api.post(`/permission/roles/${currentRole.value.id}/assign_permissions/`, {
      permission_ids: permissionIds
    })
    
    ElMessage.success('权限分配成功')
    permissionDialogVisible.value = false
  } catch (error) {
    ElMessage.error('权限分配失败')
  } finally {
    saving.value = false
  }
}

const saveUsers = async () => {
  try {
    saving.value = true
    
    await api.post(`/permission/roles/${currentRole.value.id}/assign_users/`, {
      user_ids: selectedUsers.value
    })
    
    ElMessage.success('用户分配成功')
    userDialogVisible.value = false
  } catch (error) {
    ElMessage.error('用户分配失败')
  } finally {
    saving.value = false
  }
}

// 生命周期
onMounted(() => {
  loadRoles()
  loadPermissionTree()
  loadUsers()
})
</script>

<style scoped>
.roles {
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

.permission-assignment {
  max-height: 400px;
  overflow-y: auto;
}

.permission-tree {
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.user-assignment {
  max-height: 400px;
}
</style>
