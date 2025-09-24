<template>
  <div class="permissions">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">权限管理</h1>
      <p class="page-description">管理系统用户角色和权限配置</p>
    </div>

    <el-row :gutter="24">
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
          
          <el-table :data="roles" class="roles-table">
            <el-table-column prop="name" label="角色名称" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="userCount" label="用户数量" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                  {{ row.status === 'active' ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
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

      <el-col :xs="24" :lg="8">
        <el-card class="users-card">
          <template #header>
            <h3>用户管理</h3>
          </template>
          
          <div class="user-list">
            <div v-for="user in users" :key="user.id" class="user-item">
              <el-avatar :size="40" :src="user.avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <div class="user-info">
                <div class="user-name">{{ user.name }}</div>
                <div class="user-role">{{ user.role }}</div>
              </div>
              <el-tag :type="user.status === 'active' ? 'success' : 'info'" size="small">
                {{ user.status === 'active' ? '在线' : '离线' }}
              </el-tag>
            </div>
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
      </el-form>
      <template #footer>
        <el-button @click="showAddRoleDialog = false">取消</el-button>
        <el-button type="primary" @click="addRole">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, User } from '@element-plus/icons-vue'

const showAddRoleDialog = ref(false)

const roles = ref([
  {
    id: 1,
    name: '系统管理员',
    description: '拥有系统所有权限',
    userCount: 2,
    status: 'active'
  },
  {
    id: 2,
    name: 'HR管理员',
    description: '负责员工考核管理',
    userCount: 5,
    status: 'active'
  },
  {
    id: 3,
    name: '部门经理',
    description: '管理本部门员工考核',
    userCount: 12,
    status: 'active'
  },
  {
    id: 4,
    name: '普通员工',
    description: '参与考核评分',
    userCount: 150,
    status: 'active'
  }
])

const users = ref([
  {
    id: 1,
    name: '张三',
    role: '系统管理员',
    avatar: '',
    status: 'active'
  },
  {
    id: 2,
    name: '李四',
    role: 'HR管理员',
    avatar: '',
    status: 'active'
  },
  {
    id: 3,
    name: '王五',
    role: '部门经理',
    avatar: '',
    status: 'offline'
  },
  {
    id: 4,
    name: '赵六',
    role: '普通员工',
    avatar: '',
    status: 'active'
  }
])

const newRole = ref({
  name: '',
  description: ''
})

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
    status: 'active'
  })
  
  newRole.value = { name: '', description: '' }
  showAddRoleDialog.value = false
  ElMessage.success('角色添加成功')
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
</script>

<style scoped>
.permissions {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.page-description {
  color: #6b7280;
  font-size: 16px;
  margin: 0;
}

.roles-card, .users-card {
  height: fit-content;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
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
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.user-item:hover {
  border-color: #3b82f6;
  background-color: #f8fafc;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 500;
  color: #1f2937;
  font-size: 14px;
}

.user-role {
  color: #6b7280;
  font-size: 12px;
}
</style>
