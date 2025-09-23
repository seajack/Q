<template>
  <div class="positions">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>职位管理</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            新建职位
          </el-button>
        </div>
      </template>
      
      <el-table :data="positions" v-loading="loading">
        <el-table-column prop="name" label="职位名称" />
        <el-table-column prop="code" label="职位编码" />
        <el-table-column prop="department_name" label="所属部门" />
        <el-table-column prop="management_level_display" label="管理层级" width="100" />
        <el-table-column prop="level_display" label="职位级别" width="120" />
        <el-table-column prop="employee_count" label="员工数" width="80" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '活跃' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建/编辑职位对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑职位' : '新建职位'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="职位名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入职位名称" />
        </el-form-item>
        <el-form-item label="职位编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入职位编码" />
        </el-form-item>
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
        <el-form-item label="管理层级" prop="management_level">
          <el-select v-model="form.management_level" placeholder="请选择管理层级" style="width: 100%">
            <el-option label="高层" value="senior" />
            <el-option label="中层" value="middle" />
            <el-option label="基层" value="junior" />
          </el-select>
        </el-form-item>
        <el-form-item label="职位级别" prop="level">
          <el-select v-model="form.level" placeholder="请选择职位级别" style="width: 100%">
            <el-option-group label="高层">
              <el-option label="高层正职" :value="13" />
              <el-option label="高层副职" :value="12" />
              <el-option label="高层助理" :value="11" />
            </el-option-group>
            <el-option-group label="中层">
              <el-option label="中层正职" :value="9" />
              <el-option label="中层副职" :value="8" />
              <el-option label="中层助理" :value="7" />
            </el-option-group>
            <el-option-group label="基层">
              <el-option label="基层正职" :value="4" />
              <el-option label="基层副职" :value="3" />
              <el-option label="基层助理" :value="2" />
              <el-option label="员工" :value="1" />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="职位描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入职位描述"
          />
        </el-form-item>
        <el-form-item label="任职要求" prop="requirements">
          <el-input
            v-model="form.requirements"
            type="textarea"
            :rows="3"
            placeholder="请输入任职要求"
          />
        </el-form-item>
        <el-form-item label="岗位职责" prop="responsibilities">
          <el-input
            v-model="form.responsibilities"
            type="textarea"
            :rows="3"
            placeholder="请输入岗位职责"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="活跃" inactive-text="停用" />
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
import { computed, onMounted, ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { useOrganizationStore } from '@/stores/organization'
import type { Position } from '@/types'

const organizationStore = useOrganizationStore()

const positions = computed(() => organizationStore.positions)
const departments = computed(() => organizationStore.departments)
const loading = computed(() => organizationStore.loading)

// 对话框相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

// 表单数据
const form = reactive<Partial<Position>>({
  name: '',
  code: '',
  department: undefined,
  management_level: 'junior',
  level: 1,
  description: '',
  requirements: '',
  responsibilities: '',
  is_active: true
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入职位名称', trigger: 'blur' },
    { min: 2, max: 50, message: '职位名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入职位编码', trigger: 'blur' },
    { pattern: /^[A-Z0-9_]+$/, message: '职位编码只能包含大写字母、数字和下划线', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请选择所属部门', trigger: 'change' }
  ],
  management_level: [
    { required: true, message: '请选择管理层级', trigger: 'change' }
  ],
  level: [
    { required: true, message: '请选择职位级别', trigger: 'change' }
  ]
}

// 重置表单
const resetForm = () => {
  form.name = ''
  form.code = ''
  form.department = undefined
  form.management_level = 'junior'
  form.level = 1
  form.description = ''
  form.requirements = ''
  form.responsibilities = ''
  form.is_active = true
  formRef.value?.clearValidate()
}

// 打开新建对话框
const openCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (row: Position) => {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      await organizationStore.updatePosition(form.id!, form)
      ElMessage.success('更新职位成功')
    } else {
      await organizationStore.createPosition(form)
      ElMessage.success('创建职位成功')
    }
    
    dialogVisible.value = false
    resetForm()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(isEdit.value ? '更新职位失败' : '创建职位失败')
  } finally {
    submitting.value = false
  }
}

// 删除职位
const handleDelete = async (row: Position) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除职位 "${row.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await organizationStore.deletePosition(row.id)
    ElMessage.success('删除职位成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除职位失败')
    }
  }
}

onMounted(async () => {
  await Promise.all([
    organizationStore.fetchPositions(),
    organizationStore.fetchDepartments()
  ])
})
</script>

<style scoped>
.positions {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>