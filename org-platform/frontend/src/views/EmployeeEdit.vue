<template>
  <div class="employee-edit">
    <div class="page-header">
      <h1 class="page-title">编辑员工</h1>
      <div class="page-actions">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="saveEmployee" :loading="saving">
          保存
        </el-button>
      </div>
    </div>

    <div class="edit-content">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="edit-form"
      >
        <div class="form-section">
          <h3 class="section-title">基本信息</h3>
          <div class="form-grid">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
            
            <el-form-item label="性别" prop="gender">
              <el-select v-model="form.gender" placeholder="请选择性别">
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="出生日期" prop="birth_date">
              <el-date-picker
                v-model="form.birth_date"
                type="date"
                placeholder="请选择出生日期"
                style="width: 100%"
              />
            </el-form-item>
            
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入手机号" />
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
            
            <el-form-item label="地址" prop="address" class="full-width">
              <el-input
                v-model="form.address"
                type="textarea"
                :rows="3"
                placeholder="请输入地址"
              />
            </el-form-item>
          </div>
        </div>

        <div class="form-section">
          <h3 class="section-title">职位信息</h3>
          <div class="form-grid">
            <el-form-item label="部门" prop="department_id">
              <el-select v-model="form.department_id" placeholder="请选择部门">
                <el-option
                  v-for="dept in departments"
                  :key="dept.id"
                  :label="dept.name"
                  :value="dept.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="岗位" prop="position_id">
              <el-select v-model="form.position_id" placeholder="请选择岗位">
                <el-option
                  v-for="position in positions"
                  :key="position.id"
                  :label="position.name"
                  :value="position.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="职级" prop="level">
              <el-input v-model="form.level" placeholder="请输入职级" />
            </el-form-item>
            
            <el-form-item label="直属上级" prop="supervisor_id">
              <el-select v-model="form.supervisor_id" placeholder="请选择直属上级">
                <el-option
                  v-for="emp in allEmployees"
                  :key="emp.id"
                  :label="emp.name"
                  :value="emp.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="入职日期" prop="hire_date">
              <el-date-picker
                v-model="form.hire_date"
                type="date"
                placeholder="请选择入职日期"
                style="width: 100%"
              />
            </el-form-item>
            
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态">
                <el-option label="在职" value="active" />
                <el-option label="离职" value="inactive" />
                <el-option label="试用" value="probation" />
              </el-select>
            </el-form-item>
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

const formRef = ref()
const saving = ref(false)
const employeeId = route.params.id as string

// 表单数据
const form = ref({
  name: '',
  gender: '',
  birth_date: '',
  phone: '',
  email: '',
  address: '',
  department_id: null,
  position_id: null,
  level: '',
  supervisor_id: null,
  hire_date: '',
  status: ''
})

// 数据源
const departments = ref([])
const positions = ref([])
const allEmployees = ref([])

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  department_id: [
    { required: true, message: '请选择部门', trigger: 'change' }
  ],
  position_id: [
    { required: true, message: '请选择岗位', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 加载员工数据
const loadEmployee = async () => {
  try {
    const response = await fetch(`/api/employees/${employeeId}/`)
    if (response.ok) {
      const employee = await response.json()
      form.value = {
        name: employee.name || '',
        gender: employee.gender || '',
        birth_date: employee.birth_date || '',
        phone: employee.phone || '',
        email: employee.email || '',
        address: employee.address || '',
        department_id: employee.department_id || null,
        position_id: employee.position_id || null,
        level: employee.level || '',
        supervisor_id: employee.supervisor_id || null,
        hire_date: employee.hire_date || '',
        status: employee.status || ''
      }
    } else {
      ElMessage.error('加载员工信息失败')
    }
  } catch (error) {
    console.error('加载员工信息失败:', error)
    ElMessage.error('加载员工信息失败')
  }
}

// 加载基础数据
const loadBaseData = async () => {
  try {
    const [deptResponse, posResponse, empResponse] = await Promise.all([
      fetch('/api/departments/'),
      fetch('/api/positions/'),
      fetch('/api/employees/')
    ])
    
    if (deptResponse.ok) {
      const deptData = await deptResponse.json()
      departments.value = deptData.results || deptData
    }
    
    if (posResponse.ok) {
      const posData = await posResponse.json()
      positions.value = posData.results || posData
    }
    
    if (empResponse.ok) {
      const empData = await empResponse.json()
      allEmployees.value = empData.results || empData
    }
  } catch (error) {
    console.error('加载基础数据失败:', error)
    ElMessage.error('加载基础数据失败')
  }
}

// 保存员工
const saveEmployee = async () => {
  try {
    await formRef.value.validate()
    saving.value = true
    
    // 准备更新数据，只包含需要更新的字段
    const updateData = {
      name: form.value.name,
      gender: form.value.gender,
      birth_date: form.value.birth_date,
      phone: form.value.phone,
      email: form.value.email,
      address: form.value.address,
      department: form.value.department_id,
      position: form.value.position_id,
      supervisor: form.value.supervisor_id,
      hire_date: form.value.hire_date,
      status: form.value.status
    }
    
    const response = await fetch(`/api/employees/${employeeId}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updateData)
    })
    
    if (response.ok) {
      ElMessage.success('员工信息更新成功')
      goBack()
    } else {
      const errorData = await response.json()
      console.error('保存失败:', errorData)
      ElMessage.error(`保存失败: ${JSON.stringify(errorData)}`)
    }
  } catch (error) {
    console.error('保存员工信息失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 返回
const goBack = () => {
  router.back()
}

onMounted(async () => {
  await Promise.all([
    loadEmployee(),
    loadBaseData()
  ])
})
</script>

<style scoped>
.employee-edit {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.page-actions {
  display: flex;
  gap: 12px;
}

.edit-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.edit-form {
  padding: 24px;
}

.form-section {
  margin-bottom: 32px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #e2e8f0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.full-width {
  grid-column: 1 / -1;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .page-actions {
    justify-content: center;
  }
}
</style>
