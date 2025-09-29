<template>
  <div class="employees-page">
    <!-- 现代化页面头部 -->
    <ModernPageHeader
      title="员工管理"
      subtitle="企业人员信息与组织架构管理"
      icon="User"
      color="blue"
    >
      <template #actions>
        <ModernButton type="secondary" icon="Download">
          导出员工
        </ModernButton>
        <ModernButton type="primary" icon="Plus" @click="openCreateDialog">
          新建员工
        </ModernButton>
      </template>
    </ModernPageHeader>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <ModernStatCard
        title="总员工数"
        :value="employees.length"
        change="+8 本月"
        change-type="positive"
        icon="User"
        icon-type="primary"
      />
      <ModernStatCard
        title="在职人员"
        :value="getActiveEmployees()"
        change="+5 本月"
        change-type="positive"
        icon="CircleCheck"
        icon-type="success"
      />
      <ModernStatCard
        title="本月入职"
        :value="getNewHires()"
        change="+8 人"
        change-type="positive"
        icon="UserFilled"
        icon-type="primary"
      />
      <ModernStatCard
        title="部门数量"
        :value="departments.length"
        change="稳定"
        change-type="positive"
        icon="OfficeBuilding"
        icon-type="warning"
      />
    </div>

    <!-- 主内容区域 -->
    <ModernCard title="员工列表" icon="List">
      <template #actions>
        <ModernButton type="secondary" icon="Filter" size="small">
          筛选
        </ModernButton>
        <ModernButton type="secondary" icon="Refresh" size="small" @click="loadData">
          刷新
        </ModernButton>
      </template>
      
      <div class="employees-grid" v-loading="loading">
        <div 
          v-for="employee in employees" 
          :key="employee.id" 
          class="employee-card"
          @click="selectEmployee(employee)"
        >
          <div class="employee-header">
            <div class="employee-avatar" :class="getAvatarClass(employee.name)">
              {{ (employee.name || '').charAt(0).toUpperCase() }}
            </div>
            <div class="employee-status">
              <el-tag :type="getStatusType(employee.status)" size="small" effect="light">
                {{ getStatusText(employee.status) }}
              </el-tag>
            </div>
          </div>
          
          <div class="employee-info">
            <h4 class="employee-name">{{ employee.name }}</h4>
            <p class="employee-id">{{ employee.employee_id }}</p>
            <p class="employee-position">{{ employee.position_name || '暂无职位' }}</p>
            <p class="employee-department">{{ employee.department_name || '暂无部门' }}</p>
          </div>
          
          <div class="employee-contact">
            <div class="contact-item" v-if="employee.phone">
              <el-icon><Phone /></el-icon>
              <span>{{ employee.phone }}</span>
            </div>
            <div class="contact-item" v-if="employee.email">
              <el-icon><Message /></el-icon>
              <span>{{ employee.email }}</span>
            </div>
          </div>
          
          <div class="employee-actions">
            <ModernButton type="secondary" icon="Edit" size="small" @click.stop="openEditDialog(employee)">
              编辑
            </ModernButton>
            <ModernButton type="danger" icon="Delete" size="small" @click.stop="handleDelete(employee)">
              删除
            </ModernButton>
          </div>
        </div>
      </div>
    </ModernCard>

    <!-- 新建/编辑员工对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑员工' : '新建员工'"
      width="800px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="员工号" prop="employee_id">
              <el-input v-model="form.employee_id" placeholder="请输入员工号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%">
                <el-option label="男" value="M" />
                <el-option label="女" value="F" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期">
              <el-date-picker
                v-model="form.birth_date"
                type="date"
                placeholder="请选择出生日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入手机号（可选）" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入邮箱（可选）" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属部门" prop="department">
              <el-select v-model="form.department" placeholder="请选择部门" style="width: 100%">
                <el-option
                  v-for="dept in departments"
                  :key="dept.id"
                  :label="dept.name"
                  :value="dept.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职位" prop="position">
              <el-select
                v-model="form.position"
                placeholder="请选择职位"
                style="width: 100%"
              >
                <el-option
                  v-for="pos in filteredPositions"
                  :key="pos.id"
                  :label="pos.name"
                  :value="pos.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="直接上级">
              <el-select v-model="form.supervisor" placeholder="请选择上级" style="width: 100%" clearable>
                <el-option
                  v-for="emp in availableSupervisors"
                  :key="emp.id"
                  :label="`${emp.name} - ${emp.position_name}`"
                  :value="emp.id"
                >
                  <span>{{ emp.name }}</span>
                  <span style="float: right; color: #8492a6; font-size: 13px">
                    {{ emp.position_name }}
                  </span>
                </el-option>
              </el-select>
              <div style="font-size: 12px; color: #999; margin-top: 4px;">
                可以选择任意部门的员工作为上级
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入职日期" prop="hire_date">
              <el-date-picker
                v-model="form.hire_date"
                type="date"
                placeholder="请选择入职日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="员工状态">
              <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="在职" value="active" />
                <el-option label="请假" value="leave" />
                <el-option label="离职" value="resigned" />
                <el-option label="退休" value="retired" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="!isEdit">
            <el-form-item label="用户名">
              <el-input
                v-model="form.username"
                placeholder="默认为员工号"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="地址">
          <el-input
            v-model="form.address"
            type="textarea"
            :rows="2"
            placeholder="请输入地址"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, reactive, watch } from 'vue'
import { Plus, Phone, Message, UserFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { useOrganizationStore } from '@/stores/organization'
import type { Employee } from '@/types'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'

const organizationStore = useOrganizationStore()

const employees = computed(() => organizationStore.employees)
const departments = computed(() => organizationStore.departments)
const positions = computed(() => organizationStore.positions)
const loading = computed(() => organizationStore.loading)

const palette = ['c1', 'c2', 'c3', 'c4', 'c5', 'c6']

const getAvatarClass = (name: string = '') => {
  const initial = name.trim()
  const code = initial ? initial.toUpperCase().charCodeAt(0) : 65
  return palette[code % palette.length]
}

// 统计方法
const getActiveEmployees = () => {
  return employees.value.filter(emp => emp.status === 'active').length
}

const getNewHires = () => {
  const currentMonth = new Date().getMonth()
  const currentYear = new Date().getFullYear()
  return employees.value.filter(emp => {
    if (!emp.hire_date) return false
    const hireDate = new Date(emp.hire_date)
    return hireDate.getMonth() === currentMonth && hireDate.getFullYear() === currentYear
  }).length
}

// 选中员工
const selectedEmployee = ref<Employee | null>(null)
const selectEmployee = (employee: Employee) => {
  selectedEmployee.value = employee
}

// 对话框相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

// 表单数据接口定义
interface EmployeeForm extends Partial<Employee> {
  username?: string
  password?: string
}

const form = reactive<EmployeeForm>({
  name: '',
  employee_id: '',
  gender: 'M',
  birth_date: undefined,
  phone: '',
  email: '',
  address: '',
  department: undefined,
  position: undefined,
  supervisor: undefined,
  hire_date: undefined,
  status: 'active',
  username: ''
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在2到20个字符之间', trigger: 'blur' }
  ],
  employee_id: [
    { required: true, message: '请输入员工号', trigger: 'blur' },
    { pattern: /^[A-Z0-9]+$/, message: '员工号只能包含大写字母和数字', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请选择部门', trigger: 'change' }
  ],
  position: [
    { required: true, message: '请选择职位', trigger: 'change' }
  ],
  hire_date: [
    { required: true, message: '请选择入职日期', trigger: 'change' }
  ]
}

// 计算属性
const filteredPositions = computed(() => {
  return positions.value.filter(pos => pos.is_active)
})

const availableSupervisors = computed(() => {
  const activeEmployees = employees.value.filter(emp =>
    emp.id !== form.id &&
    emp.status === 'active'
  )

  return activeEmployees
})

// 状态类型和文本获取
const getStatusType = (status: string) => {
  const statusMap = {
    'active': 'success',
    'leave': 'warning',
    'resigned': 'danger',
    'retired': 'info'
  }
  return statusMap[status as keyof typeof statusMap] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap = {
    'active': '在职',
    'leave': '请假',
    'resigned': '离职',
    'retired': '退休'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

// 重置表单
const resetForm = () => {
  form.name = ''
  form.employee_id = ''
  form.gender = 'M'
  form.birth_date = undefined
  form.phone = ''
  form.email = ''
  form.address = ''
  form.department = undefined
  form.position = undefined
  form.supervisor = undefined
  form.hire_date = undefined
  form.status = 'active'
  form.username = ''
  formRef.value?.clearValidate()
}

// 监听员工号变化，自动更新用户名
watch(() => form.employee_id, (newEmployeeId) => {
  if (!isEdit.value && newEmployeeId) {
    form.username = newEmployeeId
  }
})

// 打开新建对话框
const openCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (row: Employee) => {
  isEdit.value = true
  Object.assign(form, {
    ...row,
    birth_date: row.birth_date ? new Date(row.birth_date) : null,
    hire_date: row.hire_date ? new Date(row.hire_date) : null
  })
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    const formatDate = (date: any): string | null => {
      if (!date) return null

      if (typeof date === 'string' && date.match(/^\d{4}-\d{2}-\d{2}$/)) {
        return date
      }

      if (date instanceof Date && !isNaN(date.getTime())) {
        return date.toISOString().split('T')[0]
      }

      return null
    }

    const submitData: Record<string, any> = {
      id: form.id,
      name: form.name,
      employee_id: form.employee_id,
      gender: form.gender,
      birth_date: formatDate(form.birth_date),
      phone: form.phone,
      email: form.email,
      address: form.address,
      department: form.department,
      position: form.position,
      supervisor: form.supervisor,
      hire_date: formatDate(form.hire_date),
      status: form.status
    }

    if (!isEdit.value || (form.username && form.username.trim())) {
      submitData.username = form.username
    }

    if (isEdit.value) {
      await organizationStore.updateEmployee(form.id!, submitData)
      ElMessage.success('更新员工成功')
    } else {
      await organizationStore.createEmployee(submitData)
      ElMessage.success('创建员工成功')
    }

    dialogVisible.value = false
    resetForm()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(isEdit.value ? '更新员工失败' : '创建员工失败')
  } finally {
    submitting.value = false
  }
}

// 加载数据
const loadData = async () => {
  try {
    await organizationStore.fetchEmployees()
    await organizationStore.fetchDepartments()
    await organizationStore.fetchPositions()
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

// 删除员工
const handleDelete = async (row: Employee) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除员工 "${row.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await organizationStore.deleteEmployee(row.id)
    ElMessage.success('删除员工成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除员工失败')
    }
  }
}

// 监听部门变化，重置上级选择
watch(() => form.department, (newDept, oldDept) => {
  if (newDept !== oldDept) {
    form.supervisor = undefined

    if (formRef.value) {
      formRef.value.clearValidate(['supervisor'])
    }
  }
})

onMounted(async () => {
  await Promise.all([
    organizationStore.fetchEmployees(),
    organizationStore.fetchDepartments(),
    organizationStore.fetchPositions()
  ])
})
</script>

<style scoped>
.employees-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
  min-height: 100vh;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* 员工卡片网格 */
.employees-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  padding: 1rem 0;
}

.employee-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.employee-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7);
}

.employee-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #0ea5e9;
}

.employee-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.employee-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1rem;
  letter-spacing: 0.05em;
}

.employee-avatar.c1 {
  background: linear-gradient(135deg, #177fc1, #4faee7);
}

.employee-avatar.c2 {
  background: linear-gradient(135deg, #ef4444, #f97316);
}

.employee-avatar.c3 {
  background: linear-gradient(135deg, #10b981, #14b8a6);
}

.employee-avatar.c4 {
  background: linear-gradient(135deg, #f59e0b, #f97316);
}

.employee-avatar.c5 {
  background: linear-gradient(135deg, #8b5cf6, #ec4899);
}

.employee-avatar.c6 {
  background: linear-gradient(135deg, #64748b, #0ea5e9);
}

.employee-status {
  display: flex;
  align-items: center;
}

.employee-info {
  margin-bottom: 1rem;
}

.employee-name {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.25rem 0;
}

.employee-id {
  font-size: 0.75rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  display: inline-block;
  margin: 0 0 0.5rem 0;
}

.employee-position {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin: 0 0 0.25rem 0;
}

.employee-department {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0;
}

.employee-contact {
  margin-bottom: 1rem;
  min-height: 2.5rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.contact-item:last-child {
  margin-bottom: 0;
}

.contact-item span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.employee-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.employee-card:hover .employee-actions {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .employees-page {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .employees-grid {
    grid-template-columns: 1fr;
  }
  
  .employee-actions {
    opacity: 1;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
