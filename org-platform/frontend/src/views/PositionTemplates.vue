<template>
  <div class="position-templates-page">
    <!-- 现代化页面头部 -->
    <ModernPageHeader
      title="职位模板"
      subtitle="标准化职位模板管理与应用"
      icon="Document"
      color="green"
    >
      <template #actions>
        <ModernButton type="secondary" icon="Download">
          导出模板
        </ModernButton>
        <ModernButton type="primary" icon="Plus" @click="showAddDialog = true">
          新增模板
        </ModernButton>
      </template>
    </ModernPageHeader>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <ModernStatCard
        title="模板总数"
        :value="total"
        change="+2 本月"
        change-type="positive"
        icon="Document"
        icon-type="primary"
      />
      <ModernStatCard
        title="活跃模板"
        :value="getActiveTemplates()"
        change="+1 本月"
        change-type="positive"
        icon="CircleCheck"
        icon-type="success"
      />
      <ModernStatCard
        title="使用次数"
        :value="getTotalUsage()"
        change="+15 本月"
        change-type="positive"
        icon="DataAnalysis"
        icon-type="warning"
      />
      <ModernStatCard
        title="管理层级"
        :value="getManagementLevels()"
        change="稳定"
        change-type="positive"
        icon="TrendCharts"
        icon-type="success"
      />
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 层级分类 -->
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
              <div class="level-count">{{ getLevelCount(level.value) }}个模板</div>
            </div>
          </div>
        </div>
      </ModernCard>

      <!-- 模板列表 -->
      <ModernCard title="模板列表" icon="List" class="template-list">
        <template #actions>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索模板"
            @input="handleSearch"
            clearable
            style="width: 200px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </template>
        
        <div class="templates-grid" v-loading="loading">
          <div 
            v-for="template in filteredTemplates" 
            :key="template.id" 
            class="template-card"
            @click="selectTemplate(template)"
          >
            <div class="template-header">
              <div class="template-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="template-status">
                <el-tag :type="template.is_active ? 'success' : 'danger'" size="small" effect="light">
                  {{ template.is_active ? '启用' : '禁用' }}
                </el-tag>
              </div>
            </div>
            
            <div class="template-info">
              <h4 class="template-name">{{ template.name }}</h4>
              <p class="template-description">{{ template.description || '暂无描述' }}</p>
              <div class="template-meta">
                <el-tag :type="getLevelType(template.management_level)" size="small" effect="plain">
                  {{ getLevelName(template.management_level) }}
                </el-tag>
                <span class="template-level">L{{ template.level }}</span>
              </div>
            </div>
            
            <div class="template-details">
              <div class="detail-item" v-if="template.default_requirements">
                <span class="detail-label">默认要求</span>
                <span class="detail-value">{{ template.default_requirements.substring(0, 50) }}...</span>
              </div>
            </div>
            
            <div class="template-actions">
              <ModernButton type="secondary" icon="Edit" size="small" @click.stop="editTemplate(template)">
                编辑
              </ModernButton>
              <ModernButton type="primary" icon="Plus" size="small" @click.stop="createPositionFromTemplate(template)">
                创建职位
              </ModernButton>
              <ModernButton type="danger" icon="Delete" size="small" @click.stop="deleteTemplate(template)">
                删除
              </ModernButton>
            </div>
          </div>
        </div>
        
        <!-- 分页 -->
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          style="margin-top: 20px; text-align: right"
        />
      </ModernCard>
    </div>

    <!-- 新增/编辑模板对话框 -->
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑模板' : '新增模板'" width="800px">
      <el-form :model="templateForm" label-width="120px" :rules="templateRules" ref="templateFormRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模板名称" prop="name">
              <el-input v-model="templateForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="管理层级" prop="management_level">
              <el-select v-model="templateForm.management_level">
                <el-option label="高层" value="senior" />
                <el-option label="中层" value="middle" />
                <el-option label="基层" value="junior" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职位级别" prop="level">
              <el-input-number v-model="templateForm.level" :min="1" :max="20" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否启用">
              <el-switch v-model="templateForm.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="描述">
          <el-input v-model="templateForm.description" type="textarea" />
        </el-form-item>
        
        <el-form-item label="默认要求">
          <el-input v-model="templateForm.default_requirements" type="textarea" />
        </el-form-item>
        
        <el-form-item label="默认职责">
          <el-input v-model="templateForm.default_responsibilities" type="textarea" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate">保存</el-button>
      </template>
    </el-dialog>

    <!-- 基于模板创建职位对话框 -->
    <el-dialog v-model="showCreatePositionDialog" title="基于模板创建职位" width="600px">
      <el-form :model="positionForm" label-width="100px" :rules="positionRules" ref="positionFormRef">
        <el-form-item label="职位名称" prop="name">
          <el-input v-model="positionForm.name" />
        </el-form-item>
        <el-form-item label="职位编码" prop="code">
          <el-input v-model="positionForm.code" />
        </el-form-item>
        <el-form-item label="所属部门" prop="department">
          <el-select v-model="positionForm.department" placeholder="选择部门">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职位描述">
          <el-input v-model="positionForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreatePositionDialog = false">取消</el-button>
        <el-button type="primary" @click="createPosition">创建职位</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { templateApi, departmentApi } from '@/utils/api'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'

const templates = ref<any[]>([])
const departments = ref<any[]>([])
const loading = ref(false)
const selectedLevel = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedTemplate = ref<any | null>(null)

// 管理层级定义
const managementLevels = [
  { value: '', name: '全部层级', icon: 'Document', iconClass: 'icon-all' },
  { value: 'senior', name: '高层管理', icon: 'TrendCharts', iconClass: 'icon-senior' },
  { value: 'middle', name: '中层管理', icon: 'Promotion', iconClass: 'icon-middle' },
  { value: 'junior', name: '基层管理', icon: 'UserFilled', iconClass: 'icon-junior' }
]

// 统计方法
const getActiveTemplates = () => {
  return templates.value.filter(t => t.is_active).length
}

const getTotalUsage = () => {
  return templates.value.reduce((total, t) => total + (t.usage_count || 0), 0)
}

const getManagementLevels = () => {
  const levels = new Set(templates.value.map(t => t.management_level))
  return levels.size
}

const getLevelCount = (level: string) => {
  if (!level) return templates.value.length
  return templates.value.filter(t => t.management_level === level).length
}

// 选择层级
const selectLevel = (level: string) => {
  selectedLevel.value = level
  currentPage.value = 1
  loadTemplates()
}

// 选择模板
const selectTemplate = (template: any) => {
  selectedTemplate.value = template
}

// 过滤模板
const filteredTemplates = computed(() => {
  let filtered = templates.value
  if (selectedLevel.value) {
    filtered = filtered.filter(t => t.management_level === selectedLevel.value)
  }
  return filtered
})

const showAddDialog = ref(false)
const showCreatePositionDialog = ref(false)
const isEdit = ref(false)

const templateForm = reactive({
  name: '',
  description: '',
  management_level: 'junior',
  level: 1,
  default_requirements: '',
  default_responsibilities: '',
  is_active: true
})

const positionForm = reactive({
  name: '',
  code: '',
  department: null,
  description: ''
})

const templateRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  management_level: [{ required: true, message: '请选择管理层级', trigger: 'change' }],
  level: [{ required: true, message: '请输入职位级别', trigger: 'blur' }]
}

const positionRules = {
  name: [{ required: true, message: '请输入职位名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入职位编码', trigger: 'blur' }],
  department: [{ required: true, message: '请选择所属部门', trigger: 'change' }]
}

const loadTemplates = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...(selectedLevel.value && { management_level: selectedLevel.value }),
      ...(searchKeyword.value && { search: searchKeyword.value })
    }
    const response = await templateApi.getTemplates(params)
    templates.value = response.results
    total.value = response.count
  } catch (error) {
    ElMessage.error('加载模板失败')
  } finally {
    loading.value = false
  }
}

const loadDepartments = async () => {
  try {
    const response = await departmentApi.list({ page_size: 1000 })
    departments.value = response.results
  } catch (error) {
    ElMessage.error('加载部门失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadTemplates()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadTemplates()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadTemplates()
}

const getLevelType = (level: string) => {
  const types: Record<'senior'|'middle'|'junior', string> = {
    senior: 'danger',
    middle: 'warning',
    junior: 'success'
  }
  return (types as any)[level] || 'default'
}

const getLevelName = (level: string) => {
  const names: Record<'senior'|'middle'|'junior', string> = {
    senior: '高层',
    middle: '中层',
    junior: '基层'
  }
  return (names as any)[level] || level
}

const editingId = ref<number | null>(null)
const editTemplate = (template: any) => {
  isEdit.value = true
  editingId.value = template.id
  Object.assign(templateForm, template)
  showAddDialog.value = true
}

const deleteTemplate = async (template: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个模板吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await templateApi.deleteTemplate(template.id)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const createPositionFromTemplate = (template: any) => {
  selectedTemplate.value = template
  positionForm.name = template.name
  positionForm.description = template.description
  showCreatePositionDialog.value = true
}

const saveTemplate = async () => {
  try {
    if (isEdit.value) {
      await templateApi.updateTemplate(templateForm.id, templateForm)
    } else {
      await templateApi.createTemplate(templateForm)
    }
    ElMessage.success('保存成功')
    showAddDialog.value = false
    loadTemplates()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const createPosition = async () => {
  try {
    await templateApi.createPositionFromTemplate(selectedTemplate.value.id, positionForm)
    ElMessage.success('职位创建成功')
    showCreatePositionDialog.value = false
  } catch (error) {
    ElMessage.error('创建职位失败')
  }
}

onMounted(() => {
  loadTemplates()
  loadDepartments()
})
</script>

<style scoped>
.position-templates-page {
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

/* 模板列表 */
.template-list {
  height: fit-content;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.template-card {
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

.template-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #10b981, #059669);
}

.template-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #10b981;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.template-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.template-status {
  display: flex;
  align-items: center;
}

.template-info {
  margin-bottom: 1rem;
}

.template-name {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.25rem 0;
}

.template-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
}

.template-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.template-level {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background: #f3f4f6;
  border-radius: 0.25rem;
  color: #6b7280;
  font-weight: 500;
}

.template-details {
  margin-bottom: 1rem;
  min-height: 2rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 0.75rem;
  color: #111827;
  line-height: 1.4;
}

.template-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.template-card:hover .template-actions {
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
  
  .template-list {
    order: 1;
  }
  
  .level-list {
    flex-direction: row;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .position-templates-page {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .template-actions {
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
