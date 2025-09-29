<template>
  <div class="workflow-templates">
    <!-- 现代化页面头部 -->
    <ModernPageHeader
      title="流程模板管理"
      subtitle="工作流模板配置与管理中心"
      icon="Document"
      color="purple"
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
        title="总模板数"
        :value="total"
        change="+5 本月"
        change-type="positive"
        icon="Document"
        icon-type="primary"
      />
      <ModernStatCard
        title="活跃模板"
        :value="getActiveTemplates()"
        change="+3 本月"
        change-type="positive"
        icon="CircleCheck"
        icon-type="success"
      />
      <ModernStatCard
        title="使用次数"
        :value="getTotalUsage()"
        change="+12% 本月"
        change-type="positive"
        icon="TrendCharts"
        icon-type="primary"
      />
      <ModernStatCard
        title="公开模板"
        :value="getPublicTemplates()"
        change="+2 本月"
        change-type="positive"
        icon="Share"
        icon-type="warning"
      />
    </div>

    <!-- 主内容卡片 -->
    <ModernCard title="模板列表" icon="List">
      <template #actions>
        <ModernButton type="secondary" icon="Filter" size="small">
          筛选
        </ModernButton>
      </template>
      
      <!-- 模板筛选 -->
      <el-row class="filter-row">
        <el-col :span="6">
          <el-select v-model="selectedCategory" placeholder="选择模板分类" @change="loadTemplates">
            <el-option label="全部" value="" />
            <el-option label="人力资源" value="hr" />
            <el-option label="财务管理" value="finance" />
            <el-option label="信息技术" value="it" />
            <el-option label="运营管理" value="operations" />
            <el-option label="合规管理" value="compliance" />
            <el-option label="通用流程" value="general" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索模板名称"
            @input="handleSearch"
            clearable
          />
        </el-col>
        <el-col :span="6">
          <el-button @click="loadTemplates">刷新</el-button>
        </el-col>
      </el-row>
      
      <!-- 模板列表 -->
      <el-table :data="templates" v-loading="loading" style="margin-top: 20px">
        <el-table-column prop="name" label="模板名称" width="200" />
        <el-table-column prop="description" label="描述" width="300" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)">
              {{ getCategoryName(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usage_count" label="使用次数" width="100" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_public" label="公开" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'info'">
              {{ row.is_public ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="useTemplate(row)">使用</el-button>
            <el-button size="small" @click="editTemplate(row)">编辑</el-button>
            <el-button size="small" @click="showTemplatePreview(row)">预览</el-button>
            <el-button size="small" type="danger" @click="deleteTemplate(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
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
    
    <!-- 新增/编辑模板对话框 -->
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑模板' : '新增模板'" width="800px">
      <el-form :model="templateForm" :rules="templateRules" ref="templateFormRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模板名称" prop="name">
              <el-input v-model="templateForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="模板编码" prop="code">
              <el-input v-model="templateForm.code" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模板分类" prop="category">
              <el-select v-model="templateForm.category">
                <el-option label="人力资源" value="hr" />
                <el-option label="财务管理" value="finance" />
                <el-option label="信息技术" value="it" />
                <el-option label="运营管理" value="operations" />
                <el-option label="合规管理" value="compliance" />
                <el-option label="通用流程" value="general" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否公开">
              <el-switch v-model="templateForm.is_public" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="模板描述">
          <el-input v-model="templateForm.description" type="textarea" :rows="3" />
        </el-form-item>
        
        <el-form-item label="工作流定义">
          <el-input v-model="workflowDefinitionText" type="textarea" :rows="10" placeholder="JSON格式的工作流定义" />
        </el-form-item>
        
        <el-form-item label="表单结构">
          <el-input v-model="formSchemaText" type="textarea" :rows="8" placeholder="JSON格式的表单结构" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 模板预览对话框 -->
    <el-dialog v-model="showPreviewDialog" title="模板预览" width="1000px">
      <div class="template-preview">
        <div class="preview-header">
          <h3>{{ currentPreviewTemplate?.name }}</h3>
          <p>{{ currentPreviewTemplate?.description }}</p>
        </div>
        
        <div class="preview-content">
          <el-tabs v-model="activePreviewTab">
            <el-tab-pane label="工作流结构" name="workflow">
              <div class="workflow-preview">
                <el-alert
                  title="工作流节点"
                  type="info"
                  :closable="false"
                  style="margin-bottom: 20px"
                />
                <div v-if="currentPreviewTemplate?.workflow_definition && currentPreviewTemplate.workflow_definition.nodes">
                  <el-tag
                    v-for="node in currentPreviewTemplate.workflow_definition.nodes"
                    :key="node.id"
                    :type="getNodeType(node.type)"
                    style="margin-right: 10px; margin-bottom: 10px"
                  >
                    {{ node.name || node.type }}
                  </el-tag>
                </div>
                <el-empty v-else description="暂无工作流定义" />
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="表单结构" name="form">
              <div class="form-preview">
                <el-alert
                  title="表单字段"
                  type="info"
                  :closable="false"
                  style="margin-bottom: 20px"
                />
                <div v-if="currentPreviewTemplate?.form_schema && currentPreviewTemplate.form_schema.fields">
                  <el-descriptions :column="2" border>
                    <el-descriptions-item
                      v-for="field in currentPreviewTemplate.form_schema.fields"
                      :key="field.name"
                      :label="field.label"
                    >
                      {{ field.type }} - {{ field.required ? '必填' : '选填' }}
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
                <el-empty v-else description="暂无表单结构" />
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="原始数据" name="raw">
              <el-input
                v-model="rawDataText"
                type="textarea"
                :rows="20"
                readonly
                placeholder="原始JSON数据"
              />
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
        <el-button type="primary" @click="useTemplate(currentPreviewTemplate)">使用此模板</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { workflowApi } from '@/utils/api'
import { formatDateTime } from '@/utils/dateUtils'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'

// 定义模板类型
interface Template {
  id: string
  name: string
  code: string
  description: string
  category: string
  is_public: boolean
  is_active: boolean
  usage_count: number
  created_at: string
  workflow_definition?: any
  form_schema?: any
}

const templates = ref<Template[]>([])
const loading = ref(false)
const selectedCategory = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showAddDialog = ref(false)
const showPreviewDialog = ref(false)
const isEdit = ref(false)
const activePreviewTab = ref('workflow')

const templateForm = reactive<Partial<Template>>({
  name: '',
  code: '',
  description: '',
  category: 'general',
  is_public: false,
  is_active: true
})

const workflowDefinitionText = ref('')
const formSchemaText = ref('')
const currentPreviewTemplate = ref<Template | null>(null)
const rawDataText = ref('')

// 统计方法
const getActiveTemplates = () => {
  return templates.value.filter(t => t.is_active).length
}

const getTotalUsage = () => {
  return templates.value.reduce((total, t) => total + (t.usage_count || 0), 0)
}

const getPublicTemplates = () => {
  return templates.value.filter(t => t.is_public).length
}

const templateRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入模板编码', trigger: 'blur' }],
  category: [{ required: true, message: '请选择模板分类', trigger: 'change' }]
}

const loadTemplates = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...(selectedCategory.value && { category: selectedCategory.value }),
      ...(searchKeyword.value && { search: searchKeyword.value })
    }
    const response = await workflowApi.getTemplates(params)
    templates.value = response.results
    total.value = response.count
  } catch (error) {
    ElMessage.error('加载模板失败')
  } finally {
    loading.value = false
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

const getCategoryType = (category: string) => {
  const types = {
    hr: 'primary',
    finance: 'success',
    it: 'warning',
    operations: 'info',
    compliance: 'danger',
    general: 'default'
  }
  return types[category] || 'default'
}

const getCategoryName = (category: string) => {
  const names = {
    hr: '人力资源',
    finance: '财务管理',
    it: '信息技术',
    operations: '运营管理',
    compliance: '合规管理',
    general: '通用流程'
  }
  return names[category] || category
}

const getNodeType = (nodeType: string) => {
  const types = {
    start: 'success',
    end: 'danger',
    approval: 'primary',
    notification: 'warning',
    condition: 'info',
    timer: 'default'
  }
  return types[nodeType] || 'default'
}

const formatDate = (date: string) => {
  return formatDateTime(date)
}

const editTemplate = (template: any) => {
  isEdit.value = true
  Object.assign(templateForm, template)
  workflowDefinitionText.value = JSON.stringify(template.workflow_definition || {}, null, 2)
  formSchemaText.value = JSON.stringify(template.form_schema || {}, null, 2)
  showAddDialog.value = true
}

const showTemplatePreview = (template: Template) => {
  currentPreviewTemplate.value = template
  rawDataText.value = JSON.stringify(template, null, 2)
  showPreviewDialog.value = true
}

const useTemplate = async (template: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要使用模板"${template.name}"吗？这将创建一个新的工作流。`,
      '使用模板',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 这里应该跳转到工作流设计器，并加载模板数据
    ElMessage.success('模板使用成功，正在跳转到设计器...')
    // router.push({ name: 'WorkflowDesigner', query: { template: template.id } })
  } catch (error) {
    // 用户取消
  }
}

const deleteTemplate = async (template: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板"${template.name}"吗？此操作不可恢复。`,
      '删除模板',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await workflowApi.deleteTemplate(template.id)
    ElMessage.success('模板删除成功')
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除模板失败')
    }
  }
}

const saveTemplate = async () => {
  try {
    const formData = {
      ...templateForm,
      workflow_definition: JSON.parse(workflowDefinitionText.value || '{}'),
      form_schema: JSON.parse(formSchemaText.value || '{}')
    }
    
    if (isEdit.value) {
      await workflowApi.updateTemplate(templateForm.id, formData)
      ElMessage.success('模板更新成功')
    } else {
      await workflowApi.createTemplate(formData)
      ElMessage.success('模板创建成功')
    }
    
    showAddDialog.value = false
    loadTemplates()
  } catch (error) {
    ElMessage.error('保存模板失败')
  }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.workflow-templates {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 100%);
  min-height: 100vh;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.filter-row {
  margin-bottom: 20px;
}

.template-preview {
  max-height: 600px;
  overflow-y: auto;
}

.preview-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.preview-header h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.preview-header p {
  margin: 0;
  color: #606266;
}

.workflow-preview,
.form-preview {
  min-height: 200px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .workflow-templates {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
