<template>
  <div class="role-management">
    <div class="management-header">
      <h2>角色管理</h2>
      <p>定义角色和分配权限</p>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="showAddDialog = true">
          新增角色
        </el-button>
      </div>
    </div>

    <!-- 角色列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索角色"
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
      
      <el-table :data="filteredRoles" stripe v-loading="loading">
        <el-table-column prop="name" label="角色名称" min-width="150" />
        <el-table-column prop="code" label="角色编码" min-width="120" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="user_count" label="用户数量" width="100" />
        <el-table-column prop="permission_count" label="权限数量" width="100" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editRole(row)">
              编辑
            </el-button>
            <el-button type="success" size="small" @click="managePermissions(row)">
              权限
            </el-button>
            <el-button type="danger" size="small" @click="deleteRole(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑角色对话框 -->
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑角色' : '新增角色'" width="600px">
      <el-form :model="roleForm" label-width="100px" :rules="roleRules" ref="roleFormRef">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="roleForm.code" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="roleForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="roleForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRole">保存</el-button>
      </template>
    </el-dialog>

    <!-- 角色权限管理对话框 -->
    <el-dialog v-model="showPermissionDialog" title="角色权限管理" width="800px">
      <div class="permission-management">
        <div class="permission-section">
          <h4>可用权限</h4>
          <el-tree
            ref="permissionTree"
            :data="permissionTree"
            :props="treeProps"
            show-checkbox
            node-key="id"
            :default-checked-keys="selectedPermissions"
            @check="handlePermissionCheck"
          />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showPermissionDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRolePermissions">保存</el-button>
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
const showPermissionDialog = ref(false)
const isEdit = ref(false)

const roles = ref([])
const permissions = ref([])
const permissionTree = ref([])
const selectedPermissions = ref([])
const currentRole = ref(null)

const roleForm = reactive({
  name: '',
  code: '',
  description: '',
  is_active: true
})

const roleRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }]
}

const treeProps = {
  children: 'children',
  label: 'name'
}

const filteredRoles = computed(() => {
  if (!searchKeyword.value) return roles.value
  return roles.value.filter((role: any) =>
    role.name.includes(searchKeyword.value) ||
    role.code.includes(searchKeyword.value)
  )
})

const loadRoles = async () => {
  loading.value = true
  try {
    const response = await permissionApi.roles.list()
    roles.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.warn('角色API暂未实现，使用模拟数据')
    // 使用模拟数据
    roles.value = [
      {
        id: 1,
        name: '系统管理员',
        code: 'admin',
        description: '系统管理员角色',
        user_count: 1,
        permission_count: 10,
        is_active: true
      },
      {
        id: 2,
        name: '普通用户',
        code: 'user',
        description: '普通用户角色',
        user_count: 5,
        permission_count: 3,
        is_active: true
      }
    ]
  } finally {
    loading.value = false
  }
}

const loadPermissions = async () => {
  try {
    const response = await permissionApi.permissions.list()
    permissions.value = Array.isArray(response) ? response : []
    buildPermissionTree()
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
        action: 'read'
      },
      {
        id: 2,
        name: '部门管理',
        code: 'department_manage',
        permission_type: 'menu',
        resource: 'department',
        action: 'read'
      }
    ]
    buildPermissionTree()
  }
}

const buildPermissionTree = () => {
  // 构建权限树结构
  const tree: any[] = []
  const categoryMap = new Map()
  
  permissions.value.forEach((permission: any) => {
    const category = permission.permission_type || 'other'
    if (!categoryMap.has(category)) {
      categoryMap.set(category, {
        id: `category_${category}`,
        name: getCategoryName(category),
        children: []
      })
    }
    categoryMap.get(category).children.push({
      id: permission.id,
      name: permission.name,
      code: permission.code
    })
  })
  
  categoryMap.forEach((category) => {
    tree.push(category)
  })
  
  permissionTree.value = tree
}

const getCategoryName = (category: string) => {
  const nameMap: Record<string, string> = {
    menu: '菜单权限',
    api: 'API权限',
    button: '按钮权限',
    data: '数据权限',
    other: '其他权限'
  }
  return nameMap[category] || category
}

const editRole = (role: any) => {
  isEdit.value = true
  Object.assign(roleForm, role)
  showAddDialog.value = true
}

const managePermissions = (role: any) => {
  currentRole.value = role
  selectedPermissions.value = role.permissions || []
  showPermissionDialog.value = true
}

const deleteRole = async (role: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个角色吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await permissionApi.roles.delete(role.id)
    ElMessage.success('删除成功')
    loadRoles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveRole = async () => {
  try {
    if (isEdit.value) {
      await permissionApi.roles.update(roleForm.id, roleForm)
    } else {
      await permissionApi.roles.create(roleForm)
    }
    ElMessage.success('保存成功')
    showAddDialog.value = false
    loadRoles()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handlePermissionCheck = (data: any, checked: any) => {
  selectedPermissions.value = checked.checkedKeys
}

const saveRolePermissions = async () => {
  try {
    await permissionApi.roles.updatePermissions(currentRole.value.id, {
      permissions: selectedPermissions.value
    })
    ElMessage.success('权限分配成功')
    showPermissionDialog.value = false
    loadRoles()
  } catch (error) {
    ElMessage.error('权限分配失败')
  }
}

onMounted(() => {
  loadRoles()
  loadPermissions()
})
</script>

<style scoped>
.role-management {
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

.permission-management {
  max-height: 400px;
  overflow-y: auto;
}

.permission-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}
</style>
