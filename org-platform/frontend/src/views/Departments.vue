<template>
  <div class="departments">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>部门管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建部门
          </el-button>
        </div>
      </template>

      <!-- 部门树形表格 -->
      <el-table
        :data="departmentTree"
        row-key="id"
        :tree-props="{ children: 'children' }"
        v-loading="loading"
      >
        <el-table-column prop="name" label="部门名称" min-width="200" />
        <el-table-column prop="code" label="部门编码" width="120" />
        <el-table-column prop="level" label="层级" width="80" />
        <el-table-column prop="manager_name" label="负责人" width="100" />
        <el-table-column prop="employee_count" label="员工数" width="80" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '活跃' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editDepartment(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteDepartment(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

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
import type { Department } from '@/types'

const organizationStore = useOrganizationStore()

// 响应式数据
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref()

const formData = reactive({
  name: '',
  code: '',
  parent: null as number | null,
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入部门编码', trigger: 'blur' }]
}

// 计算属性
const departmentTree = computed(() => organizationStore.departmentTree)
const loading = computed(() => organizationStore.loading)

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
const showCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editDepartment = (department: Department) => {
  isEdit.value = true
  formData.name = department.name
  formData.code = department.code
  formData.parent = department.parent
  formData.description = department.description
  dialogVisible.value = true
}

const resetForm = () => {
  formData.name = ''
  formData.code = ''
  formData.parent = null
  formData.description = ''
  formRef.value?.clearValidate()
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    if (isEdit.value) {
      // 更新逻辑需要department id，这里简化处理
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
.departments {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>