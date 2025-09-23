<template>
  <div class="employees">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>员工管理</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            新建员工
          </el-button>
        </div>
      </template>
      
      <el-table :data="employees" v-loading="loading">
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="employee_id" label="员工号" />
        <el-table-column prop="department_name" label="部门" />
        <el-table-column prop="position_name" label="职位" />
        <el-table-column prop="supervisor_name" label="直接上级" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

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
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { useOrganizationStore } from '@/stores/organization'
import type { Employee } from '@/types'

const organizationStore = useOrganizationStore()

const employees = computed(() => organizationStore.employees)
const departments = computed(() => organizationStore.departments)
const positions = computed(() => organizationStore.positions)
const loading = computed(() => organizationStore.loading)

// 对话框相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

// 表单数据接口定义
interface EmployeeForm extends Partial<Employee> {
  username?: string;
  password?: string;
}

const form = reactive<EmployeeForm>({
  name: '',
  employee_id: '',
  gender: 'M',
  birth_date: null,
  phone: '',
  email: '',
  address: '',
  department: undefined,
  position: undefined,
  supervisor: undefined,
  hire_date: null,
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
  // 移除部门过滤，返回所有激活的职位
  return positions.value.filter(pos => pos.is_active)
})

const availableSupervisors = computed(() => {
  // 返回所有激活状态的员工（除了当前编辑的员工）
  // 不再限制必须在同一部门
  const activeEmployees = employees.value.filter(emp => 
    emp.id !== form.id && 
    emp.status === 'active'
  )
  
  console.log('可选上级:', {
    totalEmployees: employees.value.length,
    activeEmployees: activeEmployees.length,
    currentFormId: form.id,
    currentDepartment: form.department
  })
  
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
  form.birth_date = null
  form.phone = ''
  form.email = ''
  form.address = ''
  form.department = undefined
  form.position = undefined
  form.supervisor = undefined
  form.hire_date = null
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
      
      // 如果已经是正确格式的字符串，直接返回
      if (typeof date === 'string' && date.match(/^\d{4}-\d{2}-\d{2}$/)) {
        return date
      }
      
      // 如果是 Date 对象，转换为 YYYY-MM-DD 格式
      if (date instanceof Date && !isNaN(date.getTime())) {
        return date.toISOString().split('T')[0]
      }
      
      // 其他情况返回 null
      console.warn('无法格式化日期:', date)
      return null
    }
    
    const submitData = {
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
    
    // 只在新建时或者用户名不为空时才发送username字段
    if (!isEdit.value || (form.username && form.username.trim())) {
      submitData.username = form.username
    }
    
    console.log('原始表单数据:', {
      birth_date: form.birth_date,
      hire_date: form.hire_date,
      department: form.department,
      position: form.position,
      name: form.name,
      employee_id: form.employee_id
    })
    console.log('提交数据:', submitData)
    
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

// 删除员工
const handleDelete = async (row: Employee) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除员工 "${row.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
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
    // 部门变化时，只重置上级选择（不再重置职位）
    form.supervisor = undefined
    
    // 清除上级字段的验证错误
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
.employees {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>