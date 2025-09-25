<template>
  <div class="container">
    <!-- 顶部工具条：标题 + 新建按钮 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">职位管理</h3>
      <div class="toolbar">
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          新建职位
        </el-button>
      </div>
    </div>

    <div class="card">
      <div class="table-wrap">
        <el-table :data="positions" v-loading="loading" border stripe>
          <el-table-column label="职位" min-width="240">
            <template #default="{ row }">
              <div class="pos-name">
                <span class="pos-avatar" :class="getAvatarClass(row.name)">{{ (row.name || '').charAt(0).toUpperCase() }}</span>
                <div class="pos-meta">
                  <span class="pos-title">{{ row.name }}</span>
                  <span class="pos-code">{{ row.code }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="管理层级" width="140" align="center">
            <template #default="{ row }">
              <el-tag effect="plain" class="level-pill" :type="getManagementType(row.management_level)">
                {{ getManagementLabel(row.management_level) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="职位级别" width="160" align="center">
            <template #default="{ row }">
              <span class="level-chip">{{ row.level_display || '未设置' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="department_name" label="所属部门" min-width="160">
            <template #default="{ row }">
              <span class="dept-name-text">{{ row.department_name || '未分配' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="employee_count" label="员工数" width="100" align="center" />
          <el-table-column label="状态" width="110" align="center">
            <template #default="{ row }">
              <el-tag effect="plain" :type="row.is_active ? 'success' : 'danger'" class="status-pill">
                {{ row.is_active ? '活跃' : '停用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
                <el-button size="small" type="primary" link @click="openCloneDialog(row)">复制</el-button>
                <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

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
        <el-form-item label="所属部门">
          <el-select v-model="form.department" placeholder="请选择部门（可选）" style="width: 100%" clearable>
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
          <div style="font-size: 12px; color: #999; margin-top: 4px;">
            部门关联为可选，可以不选择部门
          </div>
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

const openCloneDialog = (row: Position) => {
  isEdit.value = false
  Object.assign(form, {
    ...row,
    id: undefined,
    name: `${row.name}（副本）`,
    code: generateCloneCode(row.code),
    department: row.department,
    is_active: true
  })
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

const generateCloneCode = (original?: string) => {
  const base = (original || 'NEW').toUpperCase().replace(/[^A-Z0-9_]/g, '_')
  const withSuffix = `${base}_COPY`
  return withSuffix.replace(/__+/g, '_').replace(/_COPY_?COPY/g, '_COPY')
}

const managementTagMap: Record<string, { type: 'danger' | 'warning' | 'primary'; label: string }> = {
  senior: { type: 'danger', label: '高层' },
  middle: { type: 'warning', label: '中层' },
  junior: { type: 'primary', label: '基层' }
}

const getManagementType = (level?: string) => {
  return (managementTagMap[level ?? 'junior'] || managementTagMap.junior).type
}

const getManagementLabel = (level?: string) => {
  return (managementTagMap[level ?? 'junior'] || managementTagMap.junior).label
}

const avatarPalette = ['c1', 'c2', 'c3', 'c4', 'c5', 'c6']

const getAvatarClass = (name: string = '') => {
  const trimmed = name.trim()
  const code = trimmed ? trimmed.toUpperCase().charCodeAt(0) : 65
  return avatarPalette[code % avatarPalette.length]
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.table-wrap { padding: 16px; }
</style>
