<template>
  <div class="tenant-management">
    <!-- 现代化页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="header-icon">
            <el-icon><Grid /></el-icon>
          </div>
          <div>
            <h1 class="header-title">多租户管理</h1>
            <p class="header-subtitle">企业级多租户架构管理平台</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button class="btn-secondary" @click="exportReport">
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
          <el-button type="primary" class="btn-primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建租户
          </el-button>
        </div>
      </div>
    </header>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-title">总租户数</div>
          <div class="stat-icon primary">
            <el-icon><Grid /></el-icon>
          </div>
        </div>
        <div class="stat-value">{{ pagination.total }}</div>
        <div class="stat-change positive">
          <el-icon><ArrowUp /></el-icon>
          +12% 本月
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-title">活跃租户</div>
          <div class="stat-icon success">
            <el-icon><CircleCheck /></el-icon>
          </div>
        </div>
        <div class="stat-value">{{ getActiveTenants() }}</div>
        <div class="stat-change positive">
          <el-icon><ArrowUp /></el-icon>
          +8% 本月
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-title">总用户数</div>
          <div class="stat-icon primary">
            <el-icon><User /></el-icon>
          </div>
        </div>
        <div class="stat-value">{{ getTotalUsers() }}</div>
        <div class="stat-change positive">
          <el-icon><ArrowUp /></el-icon>
          +15% 本月
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-title">存储使用</div>
          <div class="stat-icon warning">
            <el-icon><DataLine /></el-icon>
          </div>
        </div>
        <div class="stat-value">68%</div>
        <div class="stat-change negative">
          <el-icon><ArrowUp /></el-icon>
          +5% 本月
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="content-left">
        <!-- 租户列表卡片 -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">
              <el-icon><List /></el-icon>
              租户列表
            </h2>
            <div class="header-actions">
              <el-button class="btn-secondary">
                <el-icon><Filter /></el-icon>
                筛选
              </el-button>
            </div>
          </div>
          <div class="card-body">
            <div class="tenant-list">
              <div 
                v-for="tenant in tenants" 
                :key="tenant.id" 
                class="tenant-item"
                @click="viewTenant(tenant)"
              >
                <div class="tenant-avatar">
                  {{ tenant.name.charAt(0).toUpperCase() }}
                </div>
                <div class="tenant-info">
                  <div class="tenant-name">{{ tenant.name }}</div>
                  <div class="tenant-meta">
                    <span><el-icon><User /></el-icon> 用户: {{ tenant.user_count || 0 }}</span>
                    <span><el-icon><Calendar /></el-icon> 创建: {{ formatDate(tenant.created_at) }}</span>
                  </div>
                </div>
                <div class="tenant-status" :class="`status-${tenant.status}`">
                  {{ getStatusText(tenant.status) }}
                </div>
                <div class="tenant-actions" @click.stop>
                  <el-dropdown trigger="click">
                    <el-button size="small" circle>
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item @click="editTenant(tenant)">
                          <el-icon><Edit /></el-icon>
                          编辑
                        </el-dropdown-item>
                        <el-dropdown-item @click="manageUsers(tenant)">
                          <el-icon><User /></el-icon>
                          用户管理
                        </el-dropdown-item>
                        <el-dropdown-item @click="deleteTenant(tenant)" divided>
                          <el-icon><Delete /></el-icon>
                          删除
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="content-right">
        <!-- 快速操作 -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">
              <el-icon><Grid /></el-icon>
              快速操作
            </h3>
          </div>
          <div class="card-body">
            <div class="quick-actions">
              <div class="action-item" @click="showCreateDialog = true">
                <div class="action-icon">
                  <el-icon><Plus /></el-icon>
                </div>
                <div class="action-title">创建租户</div>
                <div class="action-desc">新建企业租户</div>
              </div>

              <div class="action-item" @click="inviteUser">
                <div class="action-icon">
                  <el-icon><UserFilled /></el-icon>
                </div>
                <div class="action-title">邀请用户</div>
                <div class="action-desc">批量邀请用户</div>
              </div>

              <div class="action-item" @click="openSettings">
                <div class="action-icon">
                  <el-icon><Setting /></el-icon>
                </div>
                <div class="action-title">系统配置</div>
                <div class="action-desc">租户系统设置</div>
              </div>

              <div class="action-item" @click="viewAnalytics">
                <div class="action-icon">
                  <el-icon><DataLine /></el-icon>
                </div>
                <div class="action-title">使用分析</div>
                <div class="action-desc">查看使用统计</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 系统状态 -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">
              <el-icon><Monitor /></el-icon>
              系统状态
            </h3>
          </div>
          <div class="card-body">
            <div class="system-status">
              <div class="status-item">
                <span>API服务</span>
                <span class="status-indicator success">
                  <el-icon><CircleCheckFilled /></el-icon>
                  正常
                </span>
              </div>
              <div class="status-item">
                <span>数据库</span>
                <span class="status-indicator success">
                  <el-icon><CircleCheckFilled /></el-icon>
                  正常
                </span>
              </div>
              <div class="status-item">
                <span>缓存服务</span>
                <span class="status-indicator warning">
                  <el-icon><WarningFilled /></el-icon>
                  警告
                </span>
              </div>
              <div class="status-item">
                <span>存储空间</span>
                <span class="status-value">68% 已用</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadTenants"
        @current-change="loadTenants"
      />
    </div>

    <!-- 创建/编辑租户对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEdit ? '编辑租户' : '新建租户'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="tenantForm" :rules="tenantRules" ref="tenantFormRef" label-width="100px">
        <el-form-item label="租户名称" prop="name">
          <el-input v-model="tenantForm.name" placeholder="请输入租户名称" />
        </el-form-item>
        <el-form-item label="租户代码" prop="code">
          <el-input v-model="tenantForm.code" placeholder="请输入租户代码" />
        </el-form-item>
        <el-form-item label="域名" prop="domain">
          <el-input v-model="tenantForm.domain" placeholder="请输入域名" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="tenantForm.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact_name">
          <el-input v-model="tenantForm.contact_name" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系邮箱" prop="contact_email">
          <el-input v-model="tenantForm.contact_email" placeholder="请输入联系邮箱" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="tenantForm.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="最大用户数" prop="max_users">
          <el-input-number v-model="tenantForm.max_users" :min="1" :max="10000" />
        </el-form-item>
        <el-form-item label="最大部门数" prop="max_departments">
          <el-input-number v-model="tenantForm.max_departments" :min="1" :max="1000" />
        </el-form-item>
        <el-form-item label="最大员工数" prop="max_employees">
          <el-input-number v-model="tenantForm.max_employees" :min="1" :max="100000" />
        </el-form-item>
        <el-form-item label="过期时间" prop="expires_at">
          <el-date-picker
            v-model="tenantForm.expires_at"
            type="datetime"
            placeholder="选择过期时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTenant" :loading="saving">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 租户详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="租户详情"
      width="800px"
    >
      <div v-if="selectedTenant" class="tenant-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="租户名称">{{ selectedTenant.name }}</el-descriptions-item>
          <el-descriptions-item label="租户代码">{{ selectedTenant.code }}</el-descriptions-item>
          <el-descriptions-item label="域名">{{ selectedTenant.domain }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedTenant.status)">
              {{ getStatusText(selectedTenant.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="联系人">{{ selectedTenant.contact_name }}</el-descriptions-item>
          <el-descriptions-item label="联系邮箱">{{ selectedTenant.contact_email }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ selectedTenant.contact_phone }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(selectedTenant.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="过期时间">
            {{ selectedTenant.expires_at ? formatDateTime(selectedTenant.expires_at) : '永久' }}
          </el-descriptions-item>
          <el-descriptions-item label="最大用户数">{{ selectedTenant.max_users }}</el-descriptions-item>
          <el-descriptions-item label="最大部门数">{{ selectedTenant.max_departments }}</el-descriptions-item>
          <el-descriptions-item label="最大员工数">{{ selectedTenant.max_employees }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ selectedTenant.description }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 用户管理对话框 -->
    <el-dialog
      v-model="showUserManagementDialog"
      title="用户管理"
      width="1000px"
    >
      <div v-if="selectedTenant" class="user-management">
        <div class="user-actions">
          <el-button type="primary" @click="inviteUser">
            <el-icon><Plus /></el-icon>
            邀请用户
          </el-button>
        </div>
        
        <el-table :data="tenantUsers" v-loading="usersLoading" stripe>
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="email" label="邮箱" width="180" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="{ row }">
              <el-tag :type="getRoleType(row.role)">
                {{ getRoleText(row.role) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '激活' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="can_manage_users" label="管理用户" width="80">
            <template #default="{ row }">
              <el-tag :type="row.can_manage_users ? 'success' : 'info'">
                {{ row.can_manage_users ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="can_manage_departments" label="管理部门" width="80">
            <template #default="{ row }">
              <el-tag :type="row.can_manage_departments ? 'success' : 'info'">
                {{ row.can_manage_departments ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="can_manage_employees" label="管理员工" width="80">
            <template #default="{ row }">
              <el-tag :type="row.can_manage_employees ? 'success' : 'info'">
                {{ row.can_manage_employees ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="can_view_reports" label="查看报表" width="80">
            <template #default="{ row }">
              <el-tag :type="row.can_view_reports ? 'success' : 'info'">
                {{ row.can_view_reports ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" @click="editUserPermissions(row)">权限</el-button>
              <el-button size="small" type="danger" @click="removeUser(row)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Download, ArrowUp, CircleCheck, User,
  List, Filter, Calendar, MoreFilled, Edit, Delete,
  UserFilled, Setting, Monitor, CircleCheckFilled,
  WarningFilled, Grid, DataLine, Lightning
} from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/dateUtils'
import { tenantApi } from '@/utils/api'

// 定义租户类型
interface Tenant {
  id: string
  name: string
  code: string
  domain: string
  status: 'active' | 'suspended' | 'inactive'
  contact_name: string
  contact_email: string
  contact_phone: string
  created_at: string
  expires_at?: string
  max_users: number
  max_departments: number
  max_employees: number
  description: string
  user_count?: number
}

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const usersLoading = ref(false)
const tenants = ref<Tenant[]>([])
const tenantUsers = ref<any[]>([])
const selectedTenant = ref<Tenant | null>(null)

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 对话框状态
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showUserManagementDialog = ref(false)
const isEdit = ref(false)

// 表单数据
const tenantForm = reactive({
  name: '',
  code: '',
  domain: '',
  description: '',
  contact_name: '',
  contact_email: '',
  contact_phone: '',
  max_users: 100,
  max_departments: 50,
  max_employees: 1000,
  expires_at: ''
})

// 表单验证规则
const tenantRules = {
  name: [{ required: true, message: '请输入租户名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入租户代码', trigger: 'blur' }],
  domain: [{ required: true, message: '请输入域名', trigger: 'blur' }],
  contact_name: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  contact_email: [
    { required: true, message: '请输入联系邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const tenantFormRef = ref()

// 新增的方法
const exportReport = () => {
  ElMessage.info('导出报告功能待实现')
}

const getActiveTenants = () => {
  return tenants.value.filter(tenant => tenant.status === 'active').length
}

const getTotalUsers = () => {
  return tenants.value.reduce((total, tenant) => total + (tenant.user_count || 0), 0)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const openSettings = () => {
  ElMessage.info('系统配置功能待实现')
}

const viewAnalytics = () => {
  ElMessage.info('使用分析功能待实现')
}

const inviteUser = () => {
  ElMessage.info('邀请用户功能待实现')
}

// 方法
const loadTenants = async () => {
  try {
    loading.value = true
    
    // 添加模拟数据用于演示
    tenants.value = [
      {
        id: '1',
        name: '阿里巴巴集团',
        code: 'ALI001',
        domain: 'alibaba.com',
        status: 'active',
        contact_name: '张三',
        contact_email: 'zhangsan@alibaba.com',
        contact_phone: '13800138001',
        created_at: '2024-01-15T10:00:00Z',
        expires_at: '2025-01-15T10:00:00Z',
        max_users: 500,
        max_departments: 50,
        max_employees: 1000,
        description: '阿里巴巴集团有限公司',
        user_count: 156
      },
      {
        id: '2',
        name: '腾讯科技',
        code: 'TEN001',
        domain: 'tencent.com',
        status: 'active',
        contact_name: '李四',
        contact_email: 'lisi@tencent.com',
        contact_phone: '13800138002',
        created_at: '2024-02-20T10:00:00Z',
        expires_at: '2025-02-20T10:00:00Z',
        max_users: 300,
        max_departments: 30,
        max_employees: 600,
        description: '深圳市腾讯计算机系统有限公司',
        user_count: 89
      },
      {
        id: '3',
        name: '百度公司',
        code: 'BAI001',
        domain: 'baidu.com',
        status: 'inactive',
        contact_name: '王五',
        contact_email: 'wangwu@baidu.com',
        contact_phone: '13800138003',
        created_at: '2024-03-10T10:00:00Z',
        expires_at: '2025-03-10T10:00:00Z',
        max_users: 200,
        max_departments: 20,
        max_employees: 400,
        description: '北京百度网讯科技有限公司',
        user_count: 67
      },
      {
        id: '4',
        name: '京东集团',
        code: 'JD001',
        domain: 'jd.com',
        status: 'active',
        contact_name: '赵六',
        contact_email: 'zhaoliu@jd.com',
        contact_phone: '13800138004',
        created_at: '2024-01-28T10:00:00Z',
        expires_at: '2025-01-28T10:00:00Z',
        max_users: 400,
        max_departments: 40,
        max_employees: 800,
        description: '北京京东世纪贸易有限公司',
        user_count: 134
      },
      {
        id: '5',
        name: '美团点评',
        code: 'MT001',
        domain: 'meituan.com',
        status: 'suspended',
        contact_name: '孙七',
        contact_email: 'sunqi@meituan.com',
        contact_phone: '13800138005',
        created_at: '2024-02-15T10:00:00Z',
        expires_at: '2025-02-15T10:00:00Z',
        max_users: 250,
        max_departments: 25,
        max_employees: 500,
        description: '北京三快在线科技有限公司',
        user_count: 78
      }
    ]
    pagination.total = tenants.value.length
    
    // 实际API调用（注释掉以使用模拟数据）
    // const response = await tenantApi.list({
    //   page: pagination.page,
    //   page_size: pagination.page_size
    // })
    // tenants.value = response.results
    // pagination.total = response.count
  } catch (error) {
    ElMessage.error('加载租户列表失败')
  } finally {
    loading.value = false
  }
}

const loadTenantUsers = async (tenantId) => {
  try {
    usersLoading.value = true
    const response = await tenantApi.users.list({ tenant: tenantId })
    tenantUsers.value = response.results
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    usersLoading.value = false
  }
}

const viewTenant = (tenant) => {
  selectedTenant.value = tenant
  showDetailDialog.value = true
}

const editTenant = (tenant) => {
  isEdit.value = true
  selectedTenant.value = tenant
  Object.assign(tenantForm, tenant)
  showCreateDialog.value = true
}

const manageUsers = (tenant) => {
  selectedTenant.value = tenant
  showUserManagementDialog.value = true
  loadTenantUsers(tenant.id)
}

const deleteTenant = async (tenant) => {
  try {
    await ElMessageBox.confirm('确定要删除该租户吗？', '确认删除', {
      type: 'warning'
    })
    
    await tenantApi.delete(tenant.id)
    ElMessage.success('删除成功')
    loadTenants()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveTenant = async () => {
  try {
    await tenantFormRef.value.validate()
    saving.value = true
    
    if (isEdit.value) {
      await tenantApi.update(selectedTenant.value.id, tenantForm)
      ElMessage.success('更新成功')
    } else {
      await tenantApi.create(tenantForm)
      ElMessage.success('创建成功')
    }
    
    showCreateDialog.value = false
    loadTenants()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  isEdit.value = false
  selectedTenant.value = null
  Object.assign(tenantForm, {
    name: '',
    code: '',
    domain: '',
    description: '',
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    max_users: 100,
    max_departments: 50,
    max_employees: 1000,
    expires_at: ''
  })
}

// 删除重复的inviteUser函数

const editUserPermissions = (user) => {
  // 编辑用户权限逻辑
  ElMessage.info('编辑用户权限功能待实现')
}

const removeUser = async (user) => {
  try {
    await ElMessageBox.confirm('确定要移除该用户吗？', '确认移除', {
      type: 'warning'
    })
    
    await tenantApi.users.delete(user.id)
    ElMessage.success('移除成功')
    loadTenantUsers(selectedTenant.value.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除失败')
    }
  }
}

// 状态相关方法
const getStatusType = (status) => {
  const statusMap = {
    'active': 'success',
    'suspended': 'warning',
    'inactive': 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'active': '激活',
    'suspended': '暂停',
    'inactive': '未激活'
  }
  return statusMap[status] || status
}

const getRoleType = (role) => {
  const roleMap = {
    'admin': 'danger',
    'manager': 'warning',
    'user': 'info'
  }
  return roleMap[role] || 'info'
}

const getRoleText = (role) => {
  const roleMap = {
    'admin': '管理员',
    'manager': '管理者',
    'user': '普通用户'
  }
  return roleMap[role] || role
}

// 生命周期
onMounted(() => {
  loadTenants()
})
</script>

<style scoped>
/* 现代化色彩系统 - 直接使用颜色值 */

.tenant-management {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 100%);
  min-height: 100vh;
}

/* 现代化页面头部 */
.page-header {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #e2e8f0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  width: 3rem;
  height: 3rem;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.header-title {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.25rem;
}

.header-subtitle {
  color: #475569;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* 现代化按钮 */
.btn-secondary {
  background: white;
  color: #334155;
  border: 1px solid #cbd5e1;
}

.btn-secondary:hover {
  background: #f8fafc;
  border-color: #94a3b8;
}

.btn-primary {
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #e2e8f0;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  transform: translateY(-2px);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stat-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.stat-icon.primary { background: linear-gradient(135deg, #0ea5e9, #0284c7); }
.stat-icon.success { background: linear-gradient(135deg, #10b981, #059669); }
.stat-icon.warning { background: linear-gradient(135deg, #f59e0b, #d97706); }

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.5rem;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.stat-change.positive { color: #10b981; }
.stat-change.negative { color: #ef4444; }

/* 主内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 2rem;
}

.content-left {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.content-right {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 现代化卡片 */
.card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.card-body {
  padding: 1.5rem;
}

/* 租户列表 */
.tenant-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tenant-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
  cursor: pointer;
}

.tenant-item:hover {
  border-color: #cbd5e1;
  background: #f0f9ff;
  transform: translateX(4px);
}

.tenant-avatar {
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1.125rem;
}

.tenant-info {
  flex: 1;
}

.tenant-name {
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 0.25rem;
}

.tenant-meta {
  font-size: 0.875rem;
  color: #475569;
  display: flex;
  gap: 1rem;
}

.tenant-status {
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-active {
  background: #dcfce7;
  color: #166534;
}

.status-inactive {
  background: #fef3c7;
  color: #92400e;
}

.status-suspended {
  background: #fee2e2;
  color: #991b1b;
}

.tenant-actions {
  margin-left: auto;
}

/* 快速操作面板 */
.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.action-item {
  padding: 1rem;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  text-align: center;
  transition: all 0.2s ease;
  cursor: pointer;
}

.action-item:hover {
  border-color: #cbd5e1;
  background: #f0f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}

.action-icon {
  width: 2.5rem;
  height: 2.5rem;
  margin: 0 auto 0.75rem;
  border-radius: 0.75rem;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  transition: all 0.2s ease;
}

.action-item:hover .action-icon {
  background: #e0f2fe;
  color: #0284c7;
}

.action-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: #0f172a;
}

.action-desc {
  font-size: 0.875rem;
  color: #475569;
}

/* 系统状态 */
.system-status {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.status-indicator.success {
  color: #10b981;
}

.status-indicator.warning {
  color: #f59e0b;
}

.status-value {
  font-weight: 500;
  color: #334155;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .content-right {
    order: -1;
  }
}

@media (max-width: 768px) {
  .tenant-management {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
  
  .header-title {
    font-size: 1.5rem;
  }
}

/* 对话框样式保持原有 */
.tenant-detail {
  padding: 16px 0;
}

.user-management {
  padding: 16px 0;
}

.user-actions {
  margin-bottom: 16px;
}
</style>
