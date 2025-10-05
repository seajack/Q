<template>
  <div class="permission-management">
    <div class="management-header">
      <h2>权限管理</h2>
      <p>管理菜单和API权限</p>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="showAddDialog = true">
          新增权限
        </el-button>
      </div>
    </div>

    <!-- 权限列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>权限列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索权限"
              style="width: 200px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
      </template>
      
      <el-table :data="filteredPermissions" stripe v-loading="loading">
        <el-table-column prop="name" label="权限名称" min-width="150" />
        <el-table-column prop="code" label="权限编码" min-width="120" />
        <el-table-column prop="permission_type" label="权限类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getPermissionType(row.permission_type)">
              {{ getPermissionTypeText(row.permission_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource" label="资源" min-width="120" />
        <el-table-column prop="action" label="操作" min-width="100" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editPermission(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="deletePermission(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑权限对话框 -->
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑权限' : '新增权限'" width="600px">
      <el-form :model="permissionForm" label-width="100px" :rules="permissionRules" ref="permissionFormRef">
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="permissionForm.name" />
        </el-form-item>
        <el-form-item label="权限编码" prop="code">
          <el-input v-model="permissionForm.code" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="权限类型" prop="permission_type">
          <el-select v-model="permissionForm.permission_type">
            <el-option label="菜单权限" value="menu" />
            <el-option label="API权限" value="api" />
            <el-option label="按钮权限" value="button" />
            <el-option label="数据权限" value="data" />
          </el-select>
        </el-form-item>
        <el-form-item label="资源" prop="resource">
          <el-input v-model="permissionForm.resource" />
        </el-form-item>
        <el-form-item label="操作" prop="action">
          <el-input v-model="permissionForm.action" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="permissionForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="savePermission">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { permissionApi } from '@/utils/api'

const loading = ref(false)
const searchKeyword = ref('')
const showAddDialog = ref(false)
const isEdit = ref(false)

const permissions = ref([])

const permissionForm = reactive({
  name: '',
  code: '',
  permission_type: 'menu',
  resource: '',
  action: '',
  description: ''
})

const permissionRules = {
  name: [{ required: true, message: '请输入权限名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入权限编码', trigger: 'blur' }],
  permission_type: [{ required: true, message: '请选择权限类型', trigger: 'change' }],
  resource: [{ required: true, message: '请输入资源', trigger: 'blur' }],
  action: [{ required: true, message: '请输入操作', trigger: 'blur' }]
}

const filteredPermissions = computed(() => {
  if (!searchKeyword.value) return permissions.value
  return permissions.value.filter((permission: any) =>
    permission.name.includes(searchKeyword.value) ||
    permission.code.includes(searchKeyword.value) ||
    permission.resource.includes(searchKeyword.value)
  )
})

const loadPermissions = async () => {
  loading.value = true
  try {
    const response = await permissionApi.permissions.list()
    permissions.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.warn('权限API暂未实现，使用模拟数据')
    // 使用模拟数据
    permissions.value = [
      {
        id: 1,
        name: '用户管理',
        code: 'user_manage',
        permission_type: 'menu',
        resource: 'user',
        action: 'read',
        description: '查看用户列表'
      },
      {
        id: 2,
        name: '部门管理',
        code: 'department_manage',
        permission_type: 'menu',
        resource: 'department',
        action: 'read',
        description: '查看部门列表'
      }
    ]
  } finally {
    loading.value = false
  }
}

const editPermission = (permission: any) => {
  isEdit.value = true
  Object.assign(permissionForm, permission)
  showAddDialog.value = true
}

const deletePermission = async (permission: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个权限吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await permissionApi.permissions.delete(permission.id)
    ElMessage.success('删除成功')
    loadPermissions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const savePermission = async () => {
  try {
    if (isEdit.value) {
      await permissionApi.permissions.update(permissionForm.id, permissionForm)
    } else {
      await permissionApi.permissions.create(permissionForm)
    }
    ElMessage.success('保存成功')
    showAddDialog.value = false
    loadPermissions()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const getPermissionType = (type: string) => {
  const typeMap: Record<string, string> = {
    menu: 'primary',
    api: 'success',
    button: 'warning',
    data: 'info'
  }
  return typeMap[type] || 'default'
}

const getPermissionTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    menu: '菜单',
    api: 'API',
    button: '按钮',
    data: '数据'
  }
  return textMap[type] || type
}

onMounted(() => {
  loadPermissions()
})
</script>

<style scoped>
.permission-management {
  padding: 20px;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.management-header h2 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.management-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>