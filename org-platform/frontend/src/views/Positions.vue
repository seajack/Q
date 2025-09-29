<template>
  <div class="positions-page">
    <!-- 现代化页面头部 -->
    <ModernPageHeader
      title="职位管理"
      subtitle="企业职位架构与管理体系"
      icon="Suitcase"
      color="green"
    >
      <template #actions>
        <ModernButton type="secondary" icon="Download">
          导出职位
        </ModernButton>
        <ModernButton type="primary" icon="Plus" @click="openCreateDialog">
          新建职位
        </ModernButton>
      </template>
    </ModernPageHeader>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <ModernStatCard
        title="总职位数"
        :value="positions.length"
        change="+3 本月"
        change-type="positive"
        icon="Suitcase"
        icon-type="success"
      />
      <ModernStatCard
        title="活跃职位"
        :value="getActivePositions()"
        change="+2 本月"
        change-type="positive"
        icon="CircleCheck"
        icon-type="success"
      />
      <ModernStatCard
        title="管理层级"
        :value="getManagementLevels()"
        change="稳定"
        change-type="positive"
        icon="TrendCharts"
        icon-type="warning"
      />
      <ModernStatCard
        title="在职人数"
        :value="getTotalEmployees()"
        change="+15 本月"
        change-type="positive"
        icon="User"
        icon-type="primary"
      />
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 管理层级分类 -->
      <ModernCard title="管理层级" icon="DataLine" class="level-nav">
        <div class="level-list">
          <div 
            v-for="level in managementLevels" 
            :key="level.value"
            class="level-item"
            :class="{ active: selectedLevel === level.value }"
            @click="selectLevel(level.value)"
          >
            <div class="level-icon" :class="level.iconClass">
              <el-icon><component :is="level.icon" /></el-icon>
            </div>
            <div class="level-info">
              <div class="level-name">{{ level.name }}</div>
              <div class="level-count">{{ getLevelCount(level.value) }}个职位</div>
            </div>
          </div>
        </div>
      </ModernCard>

      <!-- 职位列表 -->
      <ModernCard title="职位列表" icon="List" class="position-list">
        <template #actions>
          <ModernButton type="secondary" icon="Filter" size="small">
            筛选
          </ModernButton>
          <ModernButton type="secondary" icon="Refresh" size="small" @click="loadData">
            刷新
          </ModernButton>
        </template>
        
        <div class="positions-grid" v-loading="loading">
          <div 
            v-for="position in filteredPositions" 
            :key="position.id" 
            class="position-card"
            @click="selectPosition(position)"
          >
            <div class="position-header">
              <div class="position-avatar" :class="getAvatarClass(position.name)">
                {{ (position.name || '').charAt(0).toUpperCase() }}
              </div>
              <div class="position-status">
                <el-tag :type="position.is_active ? 'success' : 'danger'" size="small" effect="light">
                  {{ position.is_active ? '活跃' : '停用' }}
                </el-tag>
              </div>
            </div>
            
            <div class="position-info">
              <h4 class="position-name">{{ position.name }}</h4>
              <p class="position-code">{{ position.code }}</p>
              <div class="position-meta">
                <el-tag :type="getManagementType(position.management_level)" size="small" effect="plain">
                  {{ getManagementLabel(position.management_level) }}
                </el-tag>
                <span class="position-level">{{ position.level_display || '未设置' }}</span>
              </div>
            </div>
            
            <div class="position-details">
              <div class="detail-item" v-if="position.department_name">
                <el-icon><OfficeBuilding /></el-icon>
                <span>{{ position.department_name }}</span>
              </div>
              <div class="detail-item">
                <el-icon><User /></el-icon>
                <span>{{ position.employee_count || 0 }}人</span>
              </div>
            </div>
            
            <div class="position-actions">
              <ModernButton type="secondary" icon="Edit" size="small" @click.stop="openEditDialog(position)">
                编辑
              </ModernButton>
              <ModernButton type="secondary" icon="CopyDocument" size="small" @click.stop="openCloneDialog(position)">
                复制
              </ModernButton>
              <ModernButton type="danger" icon="Delete" size="small" @click.stop="handleDelete(position)">
                删除
              </ModernButton>
            </div>
          </div>
        </div>
      </ModernCard>
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
import { Plus, OfficeBuilding, User, TrendCharts, Management, Promotion, UserFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { useOrganizationStore } from '@/stores/organization'
import type { Position } from '@/types'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'

const organizationStore = useOrganizationStore()

const positions = computed(() => organizationStore.positions)
const departments = computed(() => organizationStore.departments)
const loading = computed(() => organizationStore.loading)

// 管理层级定义
const managementLevels = [
  { value: '', name: '全部层级', icon: 'Management', iconClass: 'icon-all' },
  { value: 'senior', name: '高层管理', icon: 'TrendCharts', iconClass: 'icon-senior' },
  { value: 'middle', name: '中层管理', icon: 'Promotion', iconClass: 'icon-middle' },
  { value: 'junior', name: '基层管理', icon: 'UserFilled', iconClass: 'icon-junior' }
]

const selectedLevel = ref('')
const selectedPosition = ref<Position | null>(null)

// 统计方法
const getActivePositions = () => {
  return positions.value.filter(pos => pos.is_active).length
}

const getManagementLevels = () => {
  const levels = new Set(positions.value.map(pos => pos.management_level))
  return levels.size
}

const getTotalEmployees = () => {
  return positions.value.reduce((total, pos) => total + (pos.employee_count || 0), 0)
}

const getLevelCount = (level: string) => {
  if (!level) return positions.value.length
  return positions.value.filter(pos => pos.management_level === level).length
}

// 选择层级
const selectLevel = (level: string) => {
  selectedLevel.value = level
}

// 选择职位
const selectPosition = (position: Position) => {
  selectedPosition.value = position
}

// 过滤职位
const filteredPositions = computed(() => {
  if (!selectedLevel.value) return positions.value
  return positions.value.filter(pos => pos.management_level === selectedLevel.value)
})

// 加载数据
const loadData = async () => {
  try {
    await Promise.all([
      organizationStore.fetchPositions(),
      organizationStore.fetchDepartments()
    ])
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

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
.positions-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #ecfdf5 100%);
  min-height: 100vh;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* 主内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 1.5rem;
}

/* 层级导航 */
.level-nav {
  height: fit-content;
}

.level-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.level-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.level-item:hover {
  background: #f8fafc;
  border-color: #e2e8f0;
}

.level-item.active {
  background: #ecfdf5;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgb(16 185 129 / 0.1);
}

.level-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.125rem;
}

.icon-all { background: linear-gradient(135deg, #10b981, #059669); }
.icon-senior { background: linear-gradient(135deg, #ef4444, #dc2626); }
.icon-middle { background: linear-gradient(135deg, #f59e0b, #d97706); }
.icon-junior { background: linear-gradient(135deg, #3b82f6, #2563eb); }

.level-info {
  flex: 1;
}

.level-name {
  font-weight: 500;
  color: #111827;
  margin-bottom: 0.25rem;
}

.level-count {
  font-size: 0.75rem;
  color: #6b7280;
}

/* 职位列表 */
.position-list {
  height: fit-content;
}

.positions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.position-card {
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

.position-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #10b981, #059669);
}

.position-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #10b981;
}

.position-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.position-avatar {
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

.position-avatar.c1 { background: linear-gradient(135deg, #177fc1, #4faee7); }
.position-avatar.c2 { background: linear-gradient(135deg, #ef4444, #f97316); }
.position-avatar.c3 { background: linear-gradient(135deg, #10b981, #14b8a6); }
.position-avatar.c4 { background: linear-gradient(135deg, #f59e0b, #f97316); }
.position-avatar.c5 { background: linear-gradient(135deg, #8b5cf6, #ec4899); }
.position-avatar.c6 { background: linear-gradient(135deg, #64748b, #0ea5e9); }

.position-status {
  display: flex;
  align-items: center;
}

.position-info {
  margin-bottom: 1rem;
}

.position-name {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.25rem 0;
}

.position-code {
  font-size: 0.75rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  display: inline-block;
  margin: 0 0 0.75rem 0;
}

.position-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.position-level {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background: #f3f4f6;
  border-radius: 0.25rem;
  color: #6b7280;
}

.position-details {
  margin-bottom: 1rem;
  min-height: 2.5rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-item span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.position-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.position-card:hover .position-actions {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .level-nav {
    order: 2;
  }
  
  .position-list {
    order: 1;
  }
  
  .level-list {
    flex-direction: row;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .positions-page {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .positions-grid {
    grid-template-columns: 1fr;
  }
  
  .position-actions {
    opacity: 1;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .level-list {
    flex-direction: column;
  }
}
</style>
