<template>
  <div class="departments-page">
    <!-- 现代化页面头部 -->
    <ModernPageHeader
      title="部门管理"
      subtitle="组织架构与部门信息管理"
      icon="OfficeBuilding"
      color="emerald"
    >
      <template #actions>
        <ModernButton type="secondary" icon="Download">
          导出架构图
        </ModernButton>
        <ModernButton type="primary" icon="Plus" @click="showCreateDialog">
          新建部门
        </ModernButton>
      </template>
    </ModernPageHeader>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <ModernStatCard
        title="总部门数"
        :value="getTotalDepartments()"
        change="+2 本月"
        change-type="positive"
        icon="OfficeBuilding"
        icon-type="success"
      />
      <ModernStatCard
        title="活跃部门"
        :value="getActiveDepartments()"
        change="+1 本月"
        change-type="positive"
        icon="CircleCheck"
        icon-type="success"
      />
      <ModernStatCard
        title="总员工数"
        :value="getTotalEmployees()"
        change="+15 本月"
        change-type="positive"
        icon="User"
        icon-type="primary"
      />
      <ModernStatCard
        title="管理层级"
        :value="getMaxLevel()"
        change="稳定"
        change-type="positive"
        icon="DataLine"
        icon-type="warning"
      />
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 组织架构树 -->
      <ModernCard title="组织架构" icon="DataLine" class="org-tree-card">
        <template #actions>
          <ModernButton type="secondary" icon="Refresh" size="small" @click="loadData">
            刷新
          </ModernButton>
        </template>
        
        <div class="tree-container">
          <div class="tree-nodes" v-loading="loading">
            <div v-for="dept in departmentTree" :key="dept.id" class="tree-node">
              <DepartmentTreeNode 
                :department="dept" 
                :selected-id="selectedDepartmentId"
                @select="selectDepartment"
                @edit="editDepartment"
                @create-sub="createSubDepartment"
                @delete="deleteDepartment"
              />
            </div>
          </div>
        </div>
      </ModernCard>

      <!-- 部门详情面板 -->
      <ModernCard title="部门详情" icon="InfoFilled" class="dept-details-card">
        <template #actions>
          <ModernButton 
            v-if="selectedDepartment" 
            type="secondary" 
            icon="Edit" 
            size="small" 
            @click="editDepartment(selectedDepartment)"
          >
            编辑
          </ModernButton>
        </template>
        
        <div v-if="selectedDepartment" class="dept-details">
          <!-- 部门头部信息 -->
          <div class="dept-header">
            <div class="dept-avatar">
              {{ selectedDepartment.name.charAt(0) }}
            </div>
            <div class="dept-info">
              <div class="dept-name">{{ selectedDepartment.name }}</div>
              <div class="dept-path">{{ getDepartmentPath(selectedDepartment) }}</div>
            </div>
            <div class="dept-status">
              <el-tag :type="selectedDepartment.is_active ? 'success' : 'danger'" effect="light">
                {{ selectedDepartment.is_active ? '启用' : '停用' }}
              </el-tag>
            </div>
          </div>

          <!-- 基本信息 -->
          <div class="info-section">
            <h4 class="section-title">
              <el-icon><InfoFilled /></el-icon>
              基本信息
            </h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">部门编码</span>
                <span class="info-value">{{ selectedDepartment.code }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">层级</span>
                <span class="info-value">第{{ selectedDepartment.level }}级</span>
              </div>
              <div class="info-item">
                <span class="info-label">负责人</span>
                <span class="info-value">{{ selectedDepartment.manager_name || '暂无' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">员工数量</span>
                <span class="info-value">{{ selectedDepartment.employee_count || 0 }}人</span>
              </div>
            </div>
            <div v-if="selectedDepartment.description" class="info-description">
              <span class="info-label">部门描述</span>
              <p class="info-value">{{ selectedDepartment.description }}</p>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-section">
            <ModernButton type="primary" icon="Plus" @click="createSubDepartment(selectedDepartment)">
              新增子部门
            </ModernButton>
            <ModernButton type="secondary" icon="Edit" @click="editDepartment(selectedDepartment)">
              编辑部门
            </ModernButton>
            <ModernButton type="danger" icon="Delete" @click="deleteDepartment(selectedDepartment)">
              删除部门
            </ModernButton>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <el-empty description="请选择一个部门查看详情" />
        </div>
      </ModernCard>
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
import { Plus, InfoFilled } from '@element-plus/icons-vue'
import { useOrganizationStore } from '@/stores/organization'
import type { Department, Employee } from '@/types'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'
import DepartmentTreeNode from '@/components/department/DepartmentTreeNode.vue'

const organizationStore = useOrganizationStore()

// 响应式数据
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const loadingEmployees = ref(false)
const formRef = ref()
const currentDepartmentId = ref<number | null>(null)
const selectedDepartmentId = ref<number | null>(null)
const selectedDepartment = ref<Department | null>(null)

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

// 统计方法
const getTotalDepartments = () => {
  const countDepartments = (depts: Department[]): number => {
    if (!depts || !Array.isArray(depts)) return 0
    return depts.reduce((count, dept) => {
      return count + 1 + (dept.children ? countDepartments(dept.children) : 0)
    }, 0)
  }
  return countDepartments(departmentTree.value || [])
}

const getActiveDepartments = () => {
  const countActive = (depts: Department[]): number => {
    if (!depts || !Array.isArray(depts)) return 0
    return depts.reduce((count, dept) => {
      const current = dept.is_active ? 1 : 0
      const children = dept.children ? countActive(dept.children) : 0
      return count + current + children
    }, 0)
  }
  return countActive(departmentTree.value || [])
}

const getTotalEmployees = () => {
  const countEmployees = (depts: Department[]): number => {
    if (!depts || !Array.isArray(depts)) return 0
    return depts.reduce((count, dept) => {
      const current = dept.employee_count || 0
      const children = dept.children ? countEmployees(dept.children) : 0
      return count + current + children
    }, 0)
  }
  return countEmployees(departmentTree.value || [])
}

const getMaxLevel = () => {
  const findMaxLevel = (depts: Department[], currentMax = 0): number => {
    if (!depts || !Array.isArray(depts)) return currentMax
    return depts.reduce((max, dept) => {
      const deptLevel = dept.level || 0
      const childrenMax = dept.children ? findMaxLevel(dept.children, deptLevel) : deptLevel
      return Math.max(max, childrenMax)
    }, currentMax)
  }
  return findMaxLevel(departmentTree.value || [])
}

const getDepartmentPath = (dept: Department): string => {
  // 简单实现，实际应该根据父级关系构建完整路径
  return `第${dept.level}级部门`
}

const departmentTreeOptions = computed(() => {
  const buildOptions = (departments: Department[]): any[] => {
    if (!departments || !Array.isArray(departments)) return []
    return departments.map(dept => ({
      value: dept.id,
      label: dept.name,
      children: dept.children ? buildOptions(dept.children) : undefined
    }))
  }
  return buildOptions(departmentTree.value || [])
})

// 选择部门
const selectDepartment = (dept: Department) => {
  selectedDepartmentId.value = dept.id
  selectedDepartment.value = dept
}

// 方法
const showCreateDialog = async () => {
  isEdit.value = false
  currentDepartmentId.value = null
  resetForm()
  await loadEmployees()
  dialogVisible.value = true
}

const createSubDepartment = async (parentDepartment: Department) => {
  isEdit.value = false
  currentDepartmentId.value = null
  resetForm()
  formData.parent = parentDepartment.id
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
    console.log('部门树数据:', departmentTree.value)
    console.log('部门树数据类型:', typeof departmentTree.value)
    console.log('部门树是否为数组:', Array.isArray(departmentTree.value))
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
.departments-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0.5rem 2rem 2rem 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #ecfdf5 100%);
  min-height: 100vh;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
  margin-top: 0.5rem;
}

/* 主内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 1.5rem;
}

/* 组织架构树卡片 */
.org-tree-card {
  height: fit-content;
}

.tree-container {
  max-height: 600px;
  overflow-y: auto;
  padding: 0.5rem;
}

.tree-nodes {
  min-height: 200px;
}

.tree-node {
  margin-bottom: 0.5rem;
}

/* 部门详情卡片 */
.dept-details-card {
  height: fit-content;
}

.dept-details {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dept-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  border-radius: 0.5rem;
  border: 1px solid #a7f3d0;
}

.dept-avatar {
  width: 2.5rem;
  height: 2.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
  font-weight: 600;
}

.dept-info {
  flex: 1;
}

.dept-name {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.25rem;
}

.dept-path {
  color: #6b7280;
  font-size: 0.875rem;
}

.dept-status {
  display: flex;
  align-items: center;
}

/* 信息区域 */
.info-section {
  background: #f8fafc;
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
}

.info-description {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.info-description .info-value {
  font-weight: 400;
  line-height: 1.5;
}

/* 操作区域 */
.action-section {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
}

/* 空状态 */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .org-tree-card {
    order: 2;
  }
  
  .dept-details-card {
    order: 1;
  }
}

@media (max-width: 768px) {
  .departments-page {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .dept-header {
    flex-direction: column;
    text-align: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .action-section {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
