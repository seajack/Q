<template>
  <div class="workflow-list">
    <div class="page-header">
      <div class="header-content">
        <h2>工作流管理</h2>
        <p>管理和设计您的业务流程</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="createWorkflow">
          新建工作流
        </el-button>
        <el-button :icon="Upload" @click="importWorkflow">
          导入工作流
        </el-button>
      </div>
    </div>

    <!-- 快速入口卡片 -->
    <div class="quick-actions">
      <div class="action-card" @click="goToDesigner">
        <div class="card-icon">
          <el-icon><Edit /></el-icon>
        </div>
        <div class="card-content">
          <h3>流程设计器</h3>
          <p>拖拽式可视化流程设计</p>
        </div>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="action-card" @click="goToTemplates">
        <div class="card-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="card-content">
          <h3>流程模板</h3>
          <p>使用预设模板快速创建</p>
        </div>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="action-card" @click="goToAnalysis">
        <div class="card-icon">
          <el-icon><DataAnalysis /></el-icon>
        </div>
        <div class="card-content">
          <h3>智能分析</h3>
          <p>组织架构智能分析平台</p>
        </div>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- 工作流列表 -->
    <div class="workflow-content">
      <div class="content-header">
        <h3>我的工作流</h3>
        <div class="toolbar">
          <el-input
            v-model="searchQuery"
            placeholder="搜索工作流..."
            :prefix-icon="Search"
            style="width: 300px"
            @input="handleSearch"
          />
          <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="草稿" value="draft" />
            <el-option label="激活" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </div>
      </div>

      <div class="workflow-grid">
        <div 
          v-for="workflow in filteredWorkflows" 
          :key="workflow.id"
          class="workflow-card"
          @click="editWorkflow(workflow.id)"
        >
          <div class="card-header">
            <div class="workflow-info">
              <h4>{{ workflow.name }}</h4>
              <p>{{ workflow.description }}</p>
            </div>
            <el-dropdown @command="handleCommand" trigger="click">
              <el-button text :icon="MoreFilled" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="`edit:${workflow.id}`">编辑</el-dropdown-item>
                  <el-dropdown-item :command="`copy:${workflow.id}`">复制</el-dropdown-item>
                  <el-dropdown-item :command="`export:${workflow.id}`">导出</el-dropdown-item>
                  <el-dropdown-item :command="`delete:${workflow.id}`" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <div class="card-stats">
            <div class="stat-item">
              <span class="stat-label">节点数:</span>
              <span class="stat-value">{{ workflow.node_count }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">版本:</span>
              <span class="stat-value">{{ workflow.current_version }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">执行次数:</span>
              <span class="stat-value">{{ workflow.execution_count }}</span>
            </div>
          </div>

          <div class="card-footer">
            <el-tag :type="getStatusType(workflow.status)" size="small">
              {{ getStatusText(workflow.status) }}
            </el-tag>
            <span class="update-time">{{ formatDate(workflow.updated_at) }}</span>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="filteredWorkflows.length === 0" class="empty-state">
          <el-empty description="暂无工作流">
            <el-button type="primary" @click="createWorkflow">创建第一个工作流</el-button>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- 创建工作流对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建工作流" width="500px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入工作流名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="createForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入工作流描述"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="createForm.category" placeholder="选择分类" style="width: 100%">
            <el-option label="审批流程" value="approval" />
            <el-option label="数据处理" value="data" />
            <el-option label="通知流程" value="notification" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 模板选择对话框 -->
    <el-dialog v-model="showTemplateDialog" title="选择流程模板" width="800px">
      <div class="template-selection">
        <el-row :gutter="20">
          <el-col :span="8" v-for="template in templates" :key="template.id">
            <div class="template-card" @click="useTemplate(template)">
              <div class="template-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="template-info">
                <h4>{{ template.name }}</h4>
                <p>{{ template.description }}</p>
                <div class="template-meta">
                  <el-tag :type="getCategoryType(template.category)" size="small">
                    {{ getCategoryName(template.category) }}
                  </el-tag>
                  <span class="usage-count">{{ template.usage_count }}次使用</span>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <template #footer>
        <el-button @click="showTemplateDialog = false">取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Upload, Edit, Document, DataAnalysis, ArrowRight,
  Search, MoreFilled
} from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const searchQuery = ref('')
const statusFilter = ref('')
const showCreateDialog = ref(false)
const showTemplateDialog = ref(false)
const creating = ref(false)
const createFormRef = ref()

const workflows = ref([
  {
    id: '1',
    name: '请假审批流程',
    description: '员工请假申请的标准审批流程',
    status: 'active',
    current_version: 'v1.2.0',
    node_count: 6,
    execution_count: 128,
    updated_at: '2024-01-15T10:30:00Z'
  },
  {
    id: '2',
    name: '报销审批流程',
    description: '员工报销申请的审批流程',
    status: 'active',
    current_version: 'v1.1.0',
    node_count: 4,
    execution_count: 89,
    updated_at: '2024-01-12T14:20:00Z'
  },
  {
    id: '3',
    name: '采购申请流程',
    description: '部门采购申请的审批流程',
    status: 'draft',
    current_version: 'v1.0.0',
    node_count: 8,
    execution_count: 0,
    updated_at: '2024-01-10T09:15:00Z'
  }
])

const createForm = reactive({
  name: '',
  description: '',
  category: ''
})

// 模板数据
const templates = ref([
  {
    id: '1',
    name: '新员工入职模板',
    description: '标准的新员工入职流程模板',
    category: 'hr',
    usage_count: 25
  },
  {
    id: '2',
    name: '员工离职模板',
    description: '标准的员工离职流程模板',
    category: 'hr',
    usage_count: 18
  },
  {
    id: '3',
    name: '请假审批模板',
    description: '员工请假申请的标准审批流程',
    category: 'hr',
    usage_count: 67
  },
  {
    id: '4',
    name: '报销审批模板',
    description: '员工报销申请的审批流程',
    category: 'finance',
    usage_count: 89
  },
  {
    id: '5',
    name: '采购申请模板',
    description: '部门采购申请的审批流程',
    category: 'operations',
    usage_count: 34
  },
  {
    id: '6',
    name: '权限审批模板',
    description: '权限变更审批流程模板',
    category: 'compliance',
    usage_count: 32
  }
])

const createRules = {
  name: [
    { required: true, message: '请输入工作流名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入工作流描述', trigger: 'blur' }
  ]
}

// 计算属性
const filteredWorkflows = computed(() => {
  let result = workflows.value

  if (searchQuery.value) {
    result = result.filter(w => 
      w.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      w.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (statusFilter.value) {
    result = result.filter(w => w.status === statusFilter.value)
  }

  return result
})

// 方法
const goToDesigner = () => {
  router.push('/workflow-designer')
}

const goToTemplates = () => {
  // 显示模板选择对话框
  showTemplateDialog.value = true
}

const goToAnalysis = () => {
  router.push('/intelligent-analysis')
}

const createWorkflow = () => {
  showCreateDialog.value = true
}

const importWorkflow = () => {
  ElMessage.info('导入功能开发中...')
}

// 模板相关方法
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

const useTemplate = (template: any) => {
  ElMessage.success(`正在基于"${template.name}"创建工作流...`)
  showTemplateDialog.value = false
  // 这里可以跳转到工作流设计器，并加载模板数据
  router.push('/workflow-designer')
}

const editWorkflow = (id: string) => {
  router.push(`/workflow-designer/${id}`)
}

const handleSearch = () => {
  // 搜索逻辑已在计算属性中处理
}

const handleCommand = (command: string) => {
  const [action, id] = command.split(':')
  
  switch (action) {
    case 'edit':
      editWorkflow(id)
      break
    case 'copy':
      ElMessage.info('复制功能开发中...')
      break
    case 'export':
      ElMessage.info('导出功能开发中...')
      break
    case 'delete':
      handleDelete(id)
      break
  }
}

const handleDelete = async (id: string) => {
  try {
    await ElMessageBox.confirm('确定要删除这个工作流吗？', '确认删除', {
      type: 'warning'
    })
    
    // 这里调用删除API
    workflows.value = workflows.value.filter(w => w.id !== id)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const handleCreate = async () => {
  try {
    await createFormRef.value?.validate()
    creating.value = true
    
    // 这里调用创建API
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟API调用
    
    showCreateDialog.value = false
    ElMessage.success('工作流创建成功')
    
    // 跳转到设计器
    router.push('/workflow-designer')
  } catch (error) {
    console.error('创建失败:', error)
  } finally {
    creating.value = false
  }
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    draft: 'warning',
    inactive: 'info',
    archived: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    active: '激活',
    draft: '草稿',
    inactive: '停用',
    archived: '归档'
  }
  return textMap[status] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(() => {
  // 加载工作流列表
})
</script>

<style scoped>
.workflow-list {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.header-content h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
}

.header-content p {
  margin: 0;
  color: #6b7280;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.action-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.action-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

.card-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.card-content {
  flex: 1;
}

.card-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.card-content p {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}

.card-arrow {
  color: #9ca3af;
  transition: all 0.2s ease;
}

.action-card:hover .card-arrow {
  color: #3b82f6;
  transform: translateX(4px);
}

.workflow-content {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.content-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
}

.toolbar {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.workflow-grid {
  padding: 1.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1rem;
}

.workflow-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.workflow-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.workflow-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.workflow-info p {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.4;
}

.card-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
}

.stat-label {
  color: #6b7280;
}

.stat-value {
  font-weight: 500;
  color: #111827;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.update-time {
  font-size: 0.75rem;
  color: #9ca3af;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 2rem;
}

/* 模板选择对话框样式 */
.template-selection {
  max-height: 500px;
  overflow-y: auto;
}

.template-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.template-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

.template-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  margin-bottom: 12px;
}

.template-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.template-info p {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.4;
}

.template-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.usage-count {
  font-size: 12px;
  color: #6b7280;
}
</style>
