<template>
  <div class="data-permission-management">
    <div class="management-header">
      <h2>数据权限管理</h2>
      <p>控制数据访问范围</p>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="showAddDialog = true">
          新增数据权限
        </el-button>
      </div>
    </div>

    <!-- 数据权限列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据权限列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索数据权限"
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
      
      <el-table :data="filteredDataPermissions" stripe v-loading="loading">
        <el-table-column prop="user_name" label="用户" min-width="120" />
        <el-table-column prop="permission_type" label="权限类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getPermissionType(row.permission_type)">
              {{ getPermissionTypeText(row.permission_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource" label="资源" min-width="150" />
        <el-table-column prop="conditions" label="条件" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ formatConditions(row.conditions) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editDataPermission(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="deleteDataPermission(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑数据权限对话框 -->
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑数据权限' : '新增数据权限'" width="600px">
      <el-form :model="dataPermissionForm" label-width="100px" :rules="dataPermissionRules" ref="dataPermissionFormRef">
        <el-form-item label="用户" prop="user">
          <el-select v-model="dataPermissionForm.user" placeholder="选择用户">
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="权限类型" prop="permission_type">
          <el-select v-model="dataPermissionForm.permission_type">
            <el-option label="全部数据" value="all" />
            <el-option label="部门数据" value="department" />
            <el-option label="个人数据" value="self" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="资源" prop="resource">
          <el-input v-model="dataPermissionForm.resource" placeholder="如：employee, department" />
        </el-form-item>
        <el-form-item label="条件" v-if="dataPermissionForm.permission_type === 'custom'">
          <el-input v-model="dataPermissionForm.conditions" type="textarea" placeholder="JSON格式的条件" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="dataPermissionForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDataPermission">保存</el-button>
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

const dataPermissions = ref([])
const users = ref([])

const dataPermissionForm = reactive({
  user: null,
  permission_type: 'all',
  resource: '',
  conditions: {},
  is_active: true
})

const dataPermissionRules = {
  user: [{ required: true, message: '请选择用户', trigger: 'change' }],
  permission_type: [{ required: true, message: '请选择权限类型', trigger: 'change' }],
  resource: [{ required: true, message: '请输入资源', trigger: 'blur' }]
}

const filteredDataPermissions = computed(() => {
  if (!searchKeyword.value) return dataPermissions.value
  return dataPermissions.value.filter((permission: any) =>
    permission.user_name.includes(searchKeyword.value) ||
    permission.resource.includes(searchKeyword.value)
  )
})

const loadDataPermissions = async () => {
  loading.value = true
  try {
    const response = await permissionApi.dataPermissions.list()
    dataPermissions.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.warn('数据权限API暂未实现，使用模拟数据')
    // 使用模拟数据
    dataPermissions.value = [
      {
        id: 1,
        user_name: 'admin',
        permission_type: 'all',
        resource: 'employee',
        conditions: {},
        is_active: true
      },
      {
        id: 2,
        user_name: 'user1',
        permission_type: 'department',
        resource: 'employee',
        conditions: { department_id: 1 },
        is_active: true
      }
    ]
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  try {
    const response = await permissionApi.users.list()
    users.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.warn('用户API暂未实现，使用模拟数据')
    // 使用模拟数据
    users.value = [
      { id: 1, username: 'admin' },
      { id: 2, username: 'user1' },
      { id: 3, username: 'user2' }
    ]
  }
}

const editDataPermission = (permission: any) => {
  isEdit.value = true
  Object.assign(dataPermissionForm, permission)
  showAddDialog.value = true
}

const deleteDataPermission = async (permission: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个数据权限吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await permissionApi.dataPermissions.delete(permission.id)
    ElMessage.success('删除成功')
    loadDataPermissions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveDataPermission = async () => {
  try {
    if (isEdit.value) {
      await permissionApi.dataPermissions.update(dataPermissionForm.id, dataPermissionForm)
    } else {
      await permissionApi.dataPermissions.create(dataPermissionForm)
    }
    ElMessage.success('保存成功')
    showAddDialog.value = false
    loadDataPermissions()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const getPermissionType = (type: string) => {
  const typeMap: Record<string, string> = {
    all: 'success',
    department: 'primary',
    self: 'warning',
    custom: 'info'
  }
  return typeMap[type] || 'default'
}

const getPermissionTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    all: '全部',
    department: '部门',
    self: '个人',
    custom: '自定义'
  }
  return textMap[type] || type
}

const formatConditions = (conditions: any) => {
  if (!conditions || typeof conditions !== 'object') return '-'
  return JSON.stringify(conditions)
}

onMounted(() => {
  loadDataPermissions()
  loadUsers()
})
</script>

<style scoped>
.data-permission-management {
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
