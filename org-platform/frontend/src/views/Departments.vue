<template>
  <div class="container">
    <!-- 顶部工具条：标题 + 新建按钮 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">部门管理</h3>
      <div class="toolbar">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新建部门
        </el-button>
      </div>
    </div>
    <div class="card">
      <div class="table-wrap">
        <!-- 部门树形表格 -->
        <el-table
          :data="departmentTree"
          row-key="id"
          :tree-props="{ children: 'children' }"
          v-loading="loading"
          border
          stripe
        >
          <el-table-column prop="name" label="部门名称" min-width="200" />
          <el-table-column prop="code" label="部门编码" width="120" />
          <el-table-column prop="level" label="层级" width="80" />
          <el-table-column prop="manager_name" label="负责人" width="100" />
          <el-table-column prop="employee_count" label="员工数" width="80" />
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="editDepartment(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteDepartment(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      :title="isEdit ? '编辑部门' : '新建部门'"
      v-model="dialogVisible"
      width="600px"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="部门编码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入部门编码" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-tree-select
            v-model="formData.parent"
            :data="departmentTreeOptions"
            placeholder="请选择上级部门"
            clearable
            check-strictly
            :render-after-expand="false"
          />
        </el-form-item>
        <el-form-item label="负责人">
          <el-select
            v-model="formData.manager"
            placeholder="请选择负责人（可选）"
            clearable
            filterable
            :loading="loadingEmployees"
          >
            <el-option
              v-for="employee in activeEmployees"
              :key="employee.id"
              :label="`${employee.name} (${employee.position_name || '无职位'})`"
              :value="employee.user"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="部门描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入部门描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useOrganizationStore } from '@/stores/organization'
import type { Department, Employee } from '@/types'

const organizationStore = useOrganizationStore()

// 响应式数据
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const loadingEmployees = ref(false)
const formRef = ref()
const currentDepartmentId = ref<number | null>(null)

const formData = reactive({
  name: '',
  code: '',
  parent: null as number | null,
  manager: null as number | null,
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入部门编码', trigger: 'blur' }]
}

// 计算属性
const departmentTree = computed(() => organizationStore.departmentTree)
const loading = computed(() => organizationStore.loading)
const activeEmployees = computed(() => organizationStore.activeEmployees)

const departmentTreeOptions = computed(() => {
  const buildOptions = (departments: Department[]): any[] => {
    return departments.map(dept => ({
      value: dept.id,
      label: dept.name,
      children: dept.children ? buildOptions(dept.children) : undefined
    }))
  }
  return buildOptions(departmentTree.value)
})

// 方法
const showCreateDialog = async () => {
  isEdit.value = false
  currentDepartmentId.value = null
  resetForm()
  await loadEmployees()
  dialogVisible.value = true
}

const editDepartment = async (department: Department) => {
  isEdit.value = true
  currentDepartmentId.value = department.id
  formData.name = department.name
  formData.code = department.code
  formData.parent = department.parent
  formData.manager = department.manager
  formData.description = department.description
  await loadEmployees()
  dialogVisible.value = true
}

const resetForm = () => {
  formData.name = ''
  formData.code = ''
  formData.parent = null
  formData.manager = null
  formData.description = ''
  formRef.value?.clearValidate()
}

const loadEmployees = async () => {
  try {
    loadingEmployees.value = true
    await organizationStore.fetchEmployees()
  } catch (error) {
    console.error('加载员工列表失败:', error)
  } finally {
    loadingEmployees.value = false
  }
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    if (isEdit.value && currentDepartmentId.value) {
      await organizationStore.updateDepartment(currentDepartmentId.value, formData)
      ElMessage.success('更新成功')
    } else {
      await organizationStore.createDepartment(formData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    await loadData()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

const deleteDepartment = async (department: Department) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除部门"${department.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await organizationStore.deleteDepartment(department.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

const loadData = async () => {
  try {
    await organizationStore.fetchDepartmentTree()
  } catch (error) {
    console.error('加载部门树失败:', error)
    ElMessage.error('加载数据失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.table-wrap { padding: 16px; }
</style>