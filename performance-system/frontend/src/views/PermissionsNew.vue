<template>
  <div class="permissions-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">权限管理</h1>
      <p class="page-description">管理系统用户角色和权限配置</p>
    </div>

    <el-row :gutter="24">
      <!-- 角色管理 -->
      <el-col :xs="24" :lg="16">
        <el-card class="roles-card">
          <template #header>
            <div class="card-header">
              <h3>角色管理</h3>
              <el-button type="primary" @click="showAddRoleDialog = true">
                <el-icon><Plus /></el-icon>
                添加角色
              </el-button>
            </div>
          </template>
          
          <el-table :data="roles" class="roles-table" v-loading="loading">
            <el-table-column prop="name" label="角色名称" min-width="150" />
            <el-table-column prop="description" label="描述" min-width="200" />
            <el-table-column prop="userCount" label="用户数量" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.userCount }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="创建时间" width="180" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editRole(row)">
                  编辑
                </el-button>
                <el-button type="warning" size="small" @click="managePermissions(row)">
                  权限
                </el-button>
                <el-button type="danger" size="small" @click="deleteRole(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 用户管理 -->
      <el-col :xs="24" :lg="8">
        <el-card class="users-card">
          <template #header>
            <div class="card-header">
              <h3>用户管理</h3>
              <el-button type="primary" size="small" @click="showAddUserDialog = true">
                <el-icon><Plus /></el-icon>
                添加用户
              </el-button>
            </div>
          </template>
          
          <div class="user-list">
            <div v-for="user in users" :key="user.id" class="user-item">
              <el-avatar :size="40" :src="user.avatar" class="user-avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <div class="user-info">
                <div class="user-name">{{ user.name }}</div>
                <div class="user-role">{{ user.role }}</div>
                <div class="user-status">
                  <el-tag :type="user.status === 'active' ? 'success' : 'info'" size="small">
                    {{ user.status === 'active' ? '在线' : '离线' }}
                  </el-tag>
                </div>
              </div>
              <div class="user-actions">
                <el-button type="text" size="small" @click="editUser(user)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button type="text" size="small" @click="deleteUser(user)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 权限配置 -->
    <el-row :gutter="24" style="margin-top: 24px;">
      <el-col :span="24">
        <el-card class="permissions-card">
          <template #header>
            <h3>权限配置</h3>
          </template>
          
          <div class="permissions-tree">
            <el-tree
              :data="permissionsTree"
              :props="treeProps"
              show-checkbox
              node-key="id"
              :default-checked-keys="checkedPermissions"
              @check="handlePermissionCheck"
            >
              <template #default="{ node, data }">
                <div class="permission-node">
                  <el-icon v-if="data.icon" class="permission-icon">
                    <component :is="data.icon" />
                  </el-icon>
                  <span class="permission-label">{{ data.label }}</span>
                  <el-tag v-if="data.level" :type="getLevelType(data.level)" size="small">
                    {{ data.level }}
                  </el-tag>
                </div>
              </template>
            </el-tree>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加角色对话框 -->
    <el-dialog v-model="showAddRoleDialog" title="添加角色" width="500px">
      <el-form :model="newRole" label-width="80px">
        <el-form-item label="角色名称">
          <el-input v-model="newRole.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newRole.description" type="textarea" placeholder="请输入角色描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="newRole.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddRoleDialog = false">取消</el-button>
        <el-button type="primary" @click="addRole">确定</el-button>
      </template>
    </el-dialog>

    <!-- 添加用户对话框 -->
    <el-dialog v-model="showAddUserDialog" title="添加用户" width="500px">
      <el-form :model="newUser" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="newUser.name" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="newUser.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="newUser.role" placeholder="请选择角色">
            <el-option 
              v-for="role in roles" 
              :key="role.id" 
              :label="role.name" 
              :value="role.name" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="newUser.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddUserDialog = false">取消</el-button>
        <el-button type="primary" @click="addUser">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Plus, User, Edit, Delete, 
  House, Document, Setting, User as UserIcon, 
  Lock, Tools, TrendCharts
} from '@element-plus/icons-vue'

// 数据状态
const loading = ref(false)
const showAddRoleDialog = ref(false)
const showAddUserDialog = ref(false)

const roles = ref([
  {
    id: 1,
    name: '系统管理员',
    description: '拥有系统所有权限',
    userCount: 2,
    status: 'active',
    createdAt: '2024-01-15 10:30:00'
  },
  {
    id: 2,
    name: 'HR管理员',
    description: '负责员工考核管理',
    userCount: 5,
    status: 'active',
    createdAt: '2024-01-15 10:30:00'
  },
  {
    id: 3,
    name: '部门经理',
    description: '管理本部门员工考核',
    userCount: 12,
    status: 'active',
    createdAt: '2024-01-15 10:30:00'
  },
  {
    id: 4,
    name: '普通员工',
    description: '参与考核评分',
    userCount: 150,
    status: 'active',
    createdAt: '2024-01-15 10:30:00'
  }
])

const users = ref([
  {
    id: 1,
    name: '张三',
    email: 'zhangsan@company.com',
    role: '系统管理员',
    avatar: '',
    status: 'active'
  },
  {
    id: 2,
    name: '李四',
    email: 'lisi@company.com',
    role: 'HR管理员',
    avatar: '',
    status: 'active'
  },
  {
    id: 3,
    name: '王五',
    email: 'wangwu@company.com',
    role: '部门经理',
    avatar: '',
    status: 'inactive'
  },
  {
    id: 4,
    name: '赵六',
    email: 'zhaoliu@company.com',
    role: '普通员工',
    avatar: '',
    status: 'active'
  }
])

const permissionsTree = ref([
  {
    id: 1,
    label: '系统管理',
    icon: 'Tools',
    level: '模块',
    children: [
      {
        id: 11,
        label: '用户管理',
        icon: 'User',
        level: '功能',
        children: [
          { id: 111, label: '查看用户', level: '操作' },
          { id: 112, label: '添加用户', level: '操作' },
          { id: 113, label: '编辑用户', level: '操作' },
          { id: 114, label: '删除用户', level: '操作' }
        ]
      },
      {
        id: 12,
        label: '角色管理',
        icon: 'Lock',
        level: '功能',
        children: [
          { id: 121, label: '查看角色', level: '操作' },
          { id: 122, label: '添加角色', level: '操作' },
          { id: 123, label: '编辑角色', level: '操作' },
          { id: 124, label: '删除角色', level: '操作' }
        ]
      }
    ]
  },
  {
    id: 2,
    label: '考核管理',
    icon: 'Document',
    level: '模块',
    children: [
      {
        id: 21,
        label: '考核周期',
        icon: 'Calendar',
        level: '功能',
        children: [
          { id: 211, label: '查看周期', level: '操作' },
          { id: 212, label: '创建周期', level: '操作' },
          { id: 213, label: '编辑周期', level: '操作' },
          { id: 214, label: '删除周期', level: '操作' }
        ]
      },
      {
        id: 22,
        label: '考核指标',
        icon: 'DataBoard',
        level: '功能',
        children: [
          { id: 221, label: '查看指标', level: '操作' },
          { id: 222, label: '添加指标', level: '操作' },
          { id: 223, label: '编辑指标', level: '操作' },
          { id: 224, label: '删除指标', level: '操作' }
        ]
      }
    ]
  }
])

const checkedPermissions = ref([111, 112, 121, 122, 211, 212, 221, 222])

const treeProps = {
  children: 'children',
  label: 'label'
}

const newRole = ref({
  name: '',
  description: '',
  status: 'active'
})

const newUser = ref({
  name: '',
  email: '',
  role: '',
  status: 'active'
})

// 方法
const getLevelType = (level: string) => {
  const levelMap: Record<string, string> = {
    '模块': 'primary',
    '功能': 'success',
    '操作': 'info'
  }
  return levelMap[level] || 'info'
}

const addRole = () => {
  if (!newRole.value.name) {
    ElMessage.warning('请输入角色名称')
    return
  }
  
  roles.value.push({
    id: Date.now(),
    name: newRole.value.name,
    description: newRole.value.description,
    userCount: 0,
    status: newRole.value.status,
    createdAt: new Date().toLocaleString()
  })
  
  newRole.value = { name: '', description: '', status: 'active' }
  showAddRoleDialog.value = false
  ElMessage.success('角色添加成功')
}

const addUser = () => {
  if (!newUser.value.name) {
    ElMessage.warning('请输入用户名')
    return
  }
  
  users.value.push({
    id: Date.now(),
    name: newUser.value.name,
    email: newUser.value.email,
    role: newUser.value.role,
    avatar: '',
    status: newUser.value.status
  })
  
  newUser.value = { name: '', email: '', role: '', status: 'active' }
  showAddUserDialog.value = false
  ElMessage.success('用户添加成功')
}

const editRole = (role: any) => {
  ElMessage.info(`编辑角色: ${role.name}`)
}

const managePermissions = (role: any) => {
  ElMessage.info(`管理权限: ${role.name}`)
}

const deleteRole = (role: any) => {
  ElMessage.warning(`删除角色: ${role.name}`)
}

const editUser = (user: any) => {
  ElMessage.info(`编辑用户: ${user.name}`)
}

const deleteUser = (user: any) => {
  ElMessage.warning(`删除用户: ${user.name}`)
}

const handlePermissionCheck = (data: any, checked: any) => {
  console.log('权限变更:', data, checked)
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.permissions-management {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  letter-spacing: -0.5px;
}

.page-description {
  color: var(--text-secondary);
  font-size: 16px;
  margin: 0;
  font-weight: 400;
  line-height: 1.5;
}

.roles-card, .users-card, .permissions-card {
  height: fit-content;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.25px;
}

.roles-table {
  margin-top: 16px;
}

.user-list {
  space-y: 12px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--border-light);
  border-radius: 10px;
  transition: all 0.3s ease;
  background: var(--bg-primary);
}

.user-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.user-avatar {
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
  margin-bottom: 4px;
}

.user-role {
  color: var(--text-secondary);
  font-size: 12px;
  margin-bottom: 4px;
}

.user-status {
  margin-top: 4px;
}

.user-actions {
  display: flex;
  gap: 4px;
}

.permissions-tree {
  max-height: 400px;
  overflow-y: auto;
}

.permission-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.permission-icon {
  color: var(--primary-color);
  font-size: 16px;
}

.permission-label {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }
  
  .user-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .user-actions {
    align-self: flex-end;
  }
}
</style>