<template>
  <div class="system-configs-page">
    <!-- 现代化页面头部 -->
    <ModernPageHeader
      title="系统设置"
      subtitle="系统配置与管理中心"
      icon="Setting"
      color="indigo"
    >
      <template #actions>
        <ModernButton type="secondary" icon="Download" @click="exportConfigs">
          导出配置
        </ModernButton>
        <ModernButton type="secondary" icon="Upload" @click="showImportDialog = true">
          导入配置
        </ModernButton>
        <ModernButton type="primary" icon="Plus" @click="showAddDialog = true">
          新增配置
        </ModernButton>
      </template>
    </ModernPageHeader>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <ModernStatCard
        title="总配置数"
        :value="total"
        change="+3 本月"
        change-type="positive"
        icon="Setting"
        icon-type="primary"
      />
      <ModernStatCard
        title="启用配置"
        :value="getActiveConfigs()"
        change="+2 本月"
        change-type="positive"
        icon="CircleCheck"
        icon-type="success"
      />
      <ModernStatCard
        title="配置分类"
        :value="getConfigCategories()"
        change="稳定"
        change-type="positive"
        icon="FolderOpened"
        icon-type="warning"
      />
      <ModernStatCard
        title="安全配置"
        :value="getSecurityConfigs()"
        change="+1 本月"
        change-type="positive"
        icon="Lock"
        icon-type="error"
      />
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 配置分类导航 -->
      <ModernCard title="配置分类" icon="Menu" class="category-nav">
        <div class="category-list">
          <div 
            v-for="category in configCategories" 
            :key="category.value"
            class="category-item"
            :class="{ active: selectedCategory === category.value }"
            @click="selectCategory(category.value)"
          >
            <div class="category-icon" :class="category.iconClass">
              <el-icon><component :is="category.icon" /></el-icon>
            </div>
            <div class="category-info">
              <div class="category-name">{{ category.name }}</div>
              <div class="category-count">{{ getCategoryCount(category.value) }}项</div>
            </div>
          </div>
        </div>
      </ModernCard>

      <!-- 配置列表 -->
      <ModernCard title="配置列表" icon="List" class="config-list">
        <template #actions>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索配置"
            @input="handleSearch"
            clearable
            style="width: 200px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </template>
        
        <div class="config-grid" v-loading="loading">
          <div 
            v-for="config in configs" 
            :key="config.id" 
            class="config-card"
            @click="selectConfig(config)"
          >
            <div class="config-header">
              <div class="config-icon" :class="getConfigIconClass(config.category)">
                <el-icon><component :is="getConfigIcon(config.category)" /></el-icon>
              </div>
              <div class="config-status">
                <el-tag :type="config.is_active ? 'success' : 'danger'" size="small" effect="light">
                  {{ config.is_active ? '启用' : '禁用' }}
                </el-tag>
              </div>
            </div>
            
            <div class="config-info">
              <h4 class="config-title">{{ config.description || '暂无描述' }}</h4>
              <div class="config-value">
                <span class="value-label">配置值</span>
                <span class="value-content">{{ formatConfigValue(config.value, config.data_type) }}</span>
              </div>
              <div class="config-meta">
                <span class="config-type">{{ config.data_type }}</span>
                <span class="config-category">{{ getCategoryName(config.category) }}</span>
              </div>
            </div>
            
            <div class="config-actions">
              <ModernButton type="secondary" icon="Edit" size="small" @click.stop="editConfig(config)">
                编辑
              </ModernButton>
              <ModernButton type="danger" icon="Delete" size="small" @click.stop="deleteConfig(config)">
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
    
    <!-- 新增/编辑配置对话框 -->
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑配置' : '新增配置'" width="600px">
      <el-form :model="configForm" label-width="100px" :rules="configRules" ref="configFormRef">
        <el-form-item label="配置键" prop="key">
          <el-input v-model="configForm.key" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="配置值" prop="value">
          <el-input v-model="configForm.value" type="textarea" />
        </el-form-item>
        <el-form-item label="配置分类" prop="category">
          <el-select v-model="configForm.category">
            <el-option label="组织架构配置" value="organization" />
            <el-option label="职位配置" value="position" />
            <el-option label="员工配置" value="employee" />
            <el-option label="工作流配置" value="workflow" />
            <el-option label="集成配置" value="integration" />
            <el-option label="安全配置" value="security" />
            <el-option label="通知配置" value="notification" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据类型" prop="data_type">
          <el-select v-model="configForm.data_type">
            <el-option label="字符串" value="string" />
            <el-option label="整数" value="integer" />
            <el-option label="布尔值" value="boolean" />
            <el-option label="JSON对象" value="json" />
            <el-option label="列表" value="list" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="configForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="是否必需">
          <el-switch v-model="configForm.is_required" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="configForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 导入配置对话框 -->
    <el-dialog v-model="showImportDialog" title="导入配置" width="600px">
      <el-form>
        <el-form-item label="配置数据">
          <el-input
            v-model="importData"
            type="textarea"
            :rows="10"
            placeholder="请输入JSON格式的配置数据"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="importConfigs">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Setting, OfficeBuilding, User, Connection, Lock, Bell, Operation } from '@element-plus/icons-vue'
import { configApi } from '@/utils/api'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'

// 定义配置类型
interface Config {
  id: string
  key: string
  value: string
  category: string
  data_type: string
  description?: string
  is_active: boolean
  is_required: boolean
}

const configs = ref<Config[]>([])
const loading = ref(false)
const selectedCategory = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showAddDialog = ref(false)
const showImportDialog = ref(false)
const isEdit = ref(false)
const importData = ref('')
const selectedConfig = ref<Config | null>(null)

// 配置分类定义
const configCategories = [
  { value: '', name: '全部配置', icon: 'Setting', iconClass: 'icon-all' },
  { value: 'organization', name: '组织架构', icon: 'OfficeBuilding', iconClass: 'icon-organization' },
  { value: 'position', name: '职位管理', icon: 'User', iconClass: 'icon-position' },
  { value: 'employee', name: '员工管理', icon: 'User', iconClass: 'icon-employee' },
  { value: 'workflow', name: '工作流程', icon: 'Workflow', iconClass: 'icon-workflow' },
  { value: 'integration', name: '系统集成', icon: 'Connection', iconClass: 'icon-integration' },
  { value: 'security', name: '安全配置', icon: 'Lock', iconClass: 'icon-security' },
  { value: 'notification', name: '通知设置', icon: 'Bell', iconClass: 'icon-notification' }
]

// 统计方法
const getActiveConfigs = () => {
  return configs.value.filter(config => config.is_active).length
}

const getConfigCategories = () => {
  const categories = new Set(configs.value.map(config => config.category))
  return categories.size
}

const getSecurityConfigs = () => {
  return configs.value.filter(config => config.category === 'security').length
}

const getCategoryCount = (category: string) => {
  if (!category) return configs.value.length
  return configs.value.filter(config => config.category === category).length
}

// 选择分类
const selectCategory = (category: string) => {
  selectedCategory.value = category
  currentPage.value = 1
  loadConfigs()
}

// 选择配置
const selectConfig = (config: Config) => {
  selectedConfig.value = config
}

// 获取配置图标
const getConfigIcon = (category: string) => {
  const iconMap = {
    organization: 'OfficeBuilding',
    position: 'User',
    employee: 'User',
    workflow: 'Workflow',
    integration: 'Connection',
    security: 'Lock',
    notification: 'Bell'
  }
  return iconMap[category] || 'Setting'
}

const getConfigIconClass = (category) => {
  const classMap = {
    organization: 'icon-organization',
    position: 'icon-position',
    employee: 'icon-employee',
    workflow: 'icon-workflow',
    integration: 'icon-integration',
    security: 'icon-security',
    notification: 'icon-notification'
  }
  return classMap[category] || 'icon-default'
}

// 格式化配置值显示
const formatConfigValue = (value, dataType) => {
  if (!value) return '未设置'
  if (dataType === 'json') {
    try {
      return JSON.stringify(JSON.parse(value), null, 2).substring(0, 100) + '...'
    } catch {
      return value.substring(0, 100) + '...'
    }
  }
  if (dataType === 'boolean') {
    return value === 'true' ? '是' : '否'
  }
  return value.length > 50 ? value.substring(0, 50) + '...' : value
}

const configForm = reactive({
  key: '',
  value: '',
  category: 'organization',
  data_type: 'string',
  description: '',
  is_required: false,
  is_active: true
})

const configRules = {
  key: [{ required: true, message: '请输入配置键', trigger: 'blur' }],
  value: [{ required: true, message: '请输入配置值', trigger: 'blur' }],
  category: [{ required: true, message: '请选择配置分类', trigger: 'change' }],
  data_type: [{ required: true, message: '请选择数据类型', trigger: 'change' }]
}

const loadConfigs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...(selectedCategory.value && { category: selectedCategory.value }),
      ...(searchKeyword.value && { search: searchKeyword.value })
    }
    const response = await configApi.getConfigs(params)
    configs.value = response.results
    total.value = response.count
  } catch (error) {
    ElMessage.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadConfigs()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadConfigs()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadConfigs()
}

const getCategoryType = (category: string) => {
  const types = {
    organization: 'primary',
    position: 'success',
    employee: 'warning',
    workflow: 'info',
    integration: 'danger',
    security: 'danger',
    notification: 'success'
  }
  return types[category] || 'default'
}

const getCategoryName = (category: string) => {
  const names = {
    organization: '组织架构',
    position: '职位',
    employee: '员工',
    workflow: '工作流',
    integration: '集成',
    security: '安全',
    notification: '通知'
  }
  return names[category] || category
}

const editConfig = (config: any) => {
  isEdit.value = true
  Object.assign(configForm, config)
  showAddDialog.value = true
}

const deleteConfig = async (config: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个配置吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await configApi.deleteConfig(config.id)
    ElMessage.success('删除成功')
    loadConfigs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveConfig = async () => {
  try {
    if (isEdit.value) {
      await configApi.updateConfig(configForm.id, configForm)
    } else {
      await configApi.createConfig(configForm)
    }
    ElMessage.success('保存成功')
    showAddDialog.value = false
    loadConfigs()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const exportConfigs = async () => {
  try {
    const response = await configApi.exportConfigs()
    const dataStr = JSON.stringify(response.data, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'configs.json'
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const importConfigs = async () => {
  try {
    const data = JSON.parse(importData.value)
    await configApi.importConfigs({ configs: data })
    ElMessage.success('导入成功')
    showImportDialog.value = false
    loadConfigs()
  } catch (error) {
    ElMessage.error('导入失败，请检查JSON格式')
  }
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.system-configs-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
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

/* 分类导航 */
.category-nav {
  height: fit-content;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.category-item:hover {
  background: #f8fafc;
  border-color: #e2e8f0;
}

.category-item.active {
  background: #eef2ff;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgb(99 102 241 / 0.1);
}

.category-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.125rem;
}

.icon-all { background: linear-gradient(135deg, #6366f1, #4f46e5); }
.icon-organization { background: linear-gradient(135deg, #0ea5e9, #0284c7); }
.icon-position { background: linear-gradient(135deg, #10b981, #059669); }
.icon-employee { background: linear-gradient(135deg, #f59e0b, #d97706); }
.icon-workflow { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.icon-integration { background: linear-gradient(135deg, #ef4444, #dc2626); }
.icon-security { background: linear-gradient(135deg, #dc2626, #b91c1c); }
.icon-notification { background: linear-gradient(135deg, #10b981, #14b8a6); }

.category-info {
  flex: 1;
}

.category-name {
  font-weight: 500;
  color: #111827;
  margin-bottom: 0.25rem;
}

.category-count {
  font-size: 0.75rem;
  color: #6b7280;
}

/* 配置列表 */
.config-list {
  height: fit-content;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.75rem;
  margin-top: 1rem;
}

.config-card {
  background: white;
  border-radius: 8px;
  padding: 0.75rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.config-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #6366f1;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.config-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.icon-default { background: linear-gradient(135deg, #6366f1, #4f46e5); }

.config-status {
  display: flex;
  align-items: center;
}

.config-info {
  margin-bottom: 1rem;
}

.config-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.config-value {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.config-value .value-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.config-value .value-content {
  font-size: 0.875rem;
  font-weight: 500;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Courier New', monospace;
  color: #1f2937;
  background: #f8fafc;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  text-align: right;
  min-width: 80px;
  display: inline-block;
}

.config-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
}

.config-meta {
  display: flex;
  gap: 0.75rem;
}

.config-type,
.config-category {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  background: #f3f4f6;
  color: #6b7280;
}

.config-value {
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}

.value-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.value-content {
  font-size: 0.875rem;
  color: #111827;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.config-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.config-card:hover .config-actions {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .category-nav {
    order: 2;
  }
  
  .config-list {
    order: 1;
  }
  
  .category-list {
    flex-direction: row;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .system-configs-page {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .config-grid {
    grid-template-columns: 1fr;
  }
  
  .config-actions {
    opacity: 1;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .category-list {
    flex-direction: column;
  }
}
</style>
