<template>
  <div class="workflow-rules-page">
    <!-- 现代化页面头部 -->
    <ModernPageHeader
      title="工作流规则"
      subtitle="智能化工作流规则管理与配置"
      icon="SetUp"
      color="purple"
    >
      <template #actions>
        <ModernButton type="secondary" icon="Download">
          导出规则
        </ModernButton>
        <ModernButton type="primary" icon="Plus" @click="showAddDialog = true">
          新增规则
        </ModernButton>
      </template>
    </ModernPageHeader>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <ModernStatCard
        title="规则总数"
        :value="total"
        change="+5 本月"
        change-type="positive"
        icon="SetUp"
        icon-type="primary"
      />
      <ModernStatCard
        title="活跃规则"
        :value="getActiveRules()"
        change="+3 本月"
        change-type="positive"
        icon="CircleCheck"
        icon-type="success"
      />
      <ModernStatCard
        title="规则类型"
        :value="getRuleTypes()"
        change="稳定"
        change-type="positive"
        icon="FolderOpened"
        icon-type="warning"
      />
      <ModernStatCard
        title="执行次数"
        :value="getTotalExecutions()"
        change="+128 本月"
        change-type="positive"
        icon="DataAnalysis"
        icon-type="success"
      />
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 规则类型分类 -->
      <ModernCard title="规则类型" icon="Menu" class="type-nav">
        <div class="type-list">
          <div 
            v-for="type in ruleTypes" 
            :key="type.value"
            class="type-item"
            :class="{ active: selectedType === type.value }"
            @click="selectType(type.value)"
          >
            <div class="type-icon" :class="type.iconClass">
              <el-icon><component :is="type.icon" /></el-icon>
            </div>
            <div class="type-info">
              <div class="type-name">{{ type.name }}</div>
              <div class="type-count">{{ getTypeCount(type.value) }}个规则</div>
            </div>
          </div>
        </div>
      </ModernCard>

      <!-- 规则列表 -->
      <ModernCard title="规则列表" icon="List" class="rule-list">
        <template #actions>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索规则"
            @input="handleSearch"
            clearable
            style="width: 200px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </template>
        
        <div class="rules-grid" v-loading="loading">
          <div 
            v-for="rule in filteredRules" 
            :key="rule.id" 
            class="rule-card"
            @click="selectRule(rule)"
          >
            <div class="rule-header">
              <div class="rule-icon" :class="getRuleIconClass(rule.rule_type)">
                <el-icon><component :is="getRuleIcon(rule.rule_type)" /></el-icon>
              </div>
              <div class="rule-status">
                <el-tag :type="rule.is_active ? 'success' : 'danger'" size="small" effect="light">
                  {{ rule.is_active ? '启用' : '禁用' }}
                </el-tag>
              </div>
            </div>
            
            <div class="rule-info">
              <h4 class="rule-name">{{ rule.name }}</h4>
              <p class="rule-description">{{ rule.description || '暂无描述' }}</p>
              <div class="rule-meta">
                <el-tag :type="getTypeType(rule.rule_type)" size="small" effect="plain">
                  {{ getTypeName(rule.rule_type) }}
                </el-tag>
                <span class="rule-priority">优先级: {{ rule.priority }}</span>
              </div>
            </div>
            
            <div class="rule-details">
              <div class="detail-item">
                <span class="detail-label">创建时间</span>
                <span class="detail-value">{{ formatDate(rule.created_at) }}</span>
              </div>
            </div>
            
            <div class="rule-actions">
              <ModernButton type="secondary" icon="Edit" size="small" @click.stop="editRule(rule)">
                编辑
              </ModernButton>
              <ModernButton type="danger" icon="Delete" size="small" @click.stop="deleteRule(rule)">
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
    
    <!-- 新增/编辑规则对话框 -->
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑规则' : '新增规则'" width="800px">
      <el-form :model="ruleForm" label-width="120px" :rules="ruleRules" ref="ruleFormRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规则名称" prop="name">
              <el-input v-model="ruleForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规则类型" prop="rule_type">
              <el-select v-model="ruleForm.rule_type">
                <el-option label="审批流程" value="approval" />
                <el-option label="通知规则" value="notification" />
                <el-option label="数据同步" value="sync" />
                <el-option label="权限控制" value="permission" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-input-number v-model="ruleForm.priority" :min="1" :max="100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否启用">
              <el-switch v-model="ruleForm.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="描述">
          <el-input v-model="ruleForm.description" type="textarea" />
        </el-form-item>
        
        <el-form-item label="触发条件">
          <el-tabs v-model="activeTab" type="border-card">
            <el-tab-pane label="可视化配置" name="visual">
              <WorkflowConfigBuilder
                v-model:trigger-conditions="visualTriggerConditions"
                v-model:actions="visualActions"
              />
            </el-tab-pane>
            <el-tab-pane label="JSON配置" name="json">
              <el-input v-model="triggerConditionsText" type="textarea" placeholder="请输入JSON格式的触发条件" />
            </el-tab-pane>
          </el-tabs>
        </el-form-item>
        
        <el-form-item label="动作配置">
          <el-tabs v-model="actionTab" type="border-card">
            <el-tab-pane label="可视化配置" name="visual">
              <div class="action-config-section">
                <div v-if="visualActions.length === 0" class="empty-actions">
                  <el-empty description="暂无动作配置，请先配置触发条件" />
                </div>
                <div v-else class="actions-preview">
                  <div
                    v-for="(action, index) in visualActions"
                    :key="index"
                    class="action-preview-item"
                  >
                    <el-tag :type="getActionTypeColor(action.type)" size="small">
                      {{ getActionTypeName(action.type) }}
                    </el-tag>
                    <span class="action-preview-text">{{ formatActionText(action) }}</span>
                  </div>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="JSON配置" name="json">
              <el-input v-model="actionConfigText" type="textarea" placeholder="请输入JSON格式的动作配置" />
            </el-tab-pane>
          </el-tabs>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, SetUp, User, OfficeBuilding, Suitcase, Lock, Connection, DataAnalysis, Bell, Cpu } from '@element-plus/icons-vue'
import { workflowApi } from '@/utils/api'
import WorkflowConfigBuilder from '@/components/WorkflowConfigBuilder.vue'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'

const rules = ref([])
const loading = ref(false)
const selectedType = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedRule = ref<any | null>(null)

// 规则类型定义
const ruleTypes = [
  { value: '', name: '全部类型', icon: 'SetUp', iconClass: 'icon-all' },
  { value: 'employee_management', name: '员工管理', icon: 'User', iconClass: 'icon-employee' },
  { value: 'department_management', name: '部门管理', icon: 'OfficeBuilding', iconClass: 'icon-department' },
  { value: 'position_management', name: '职位管理', icon: 'Suitcase', iconClass: 'icon-position' },
  { value: 'permission_management', name: '权限管理', icon: 'Lock', iconClass: 'icon-permission' },
  { value: 'integration', name: '系统集成', icon: 'Connection', iconClass: 'icon-integration' },
  { value: 'data_quality', name: '数据质量', icon: 'DataAnalysis', iconClass: 'icon-data' },
  { value: 'reporting', name: '报表生成', icon: 'Bell', iconClass: 'icon-report' },
  { value: 'automation', name: '自动化', icon: 'Cpu', iconClass: 'icon-auto' }
]

// 统计方法
const getActiveRules = () => {
  return rules.value.filter(r => r.is_active).length
}

const getRuleTypes = () => {
  const types = new Set(rules.value.map(r => r.rule_type))
  return types.size
}

const getTotalExecutions = () => {
  return rules.value.reduce((total, r) => total + (r.execution_count || 0), 0)
}

const getTypeCount = (type: string) => {
  if (!type) return rules.value.length
  return rules.value.filter(r => r.rule_type === type).length
}

// 选择类型
const selectType = (type: string) => {
  selectedType.value = type
  currentPage.value = 1
  loadRules()
}

// 选择规则
const selectRule = (rule: any) => {
  selectedRule.value = rule
}

// 过滤规则
const filteredRules = computed(() => {
  let filtered = rules.value
  if (selectedType.value) {
    filtered = filtered.filter(r => r.rule_type === selectedType.value)
  }
  return filtered
})

// 获取规则图标
const getRuleIcon = (type: string) => {
  const iconMap = {
    employee_management: 'User',
    department_management: 'OfficeBuilding',
    position_management: 'Suitcase',
    permission_management: 'Lock',
    integration: 'Connection',
    data_quality: 'DataAnalysis',
    reporting: 'Bell',
    automation: 'Cpu',
    approval: 'SetUp',
    notification: 'Bell',
    sync: 'Connection',
    permission: 'Lock'
  }
  return iconMap[type] || 'SetUp'
}

const getRuleIconClass = (type: string) => {
  const classMap = {
    employee_management: 'icon-employee',
    department_management: 'icon-department',
    position_management: 'icon-position',
    permission_management: 'icon-permission',
    integration: 'icon-integration',
    data_quality: 'icon-data',
    reporting: 'icon-report',
    automation: 'icon-auto',
    approval: 'icon-approval',
    notification: 'icon-notification',
    sync: 'icon-sync',
    permission: 'icon-permission'
  }
  return classMap[type] || 'icon-default'
}

const showAddDialog = ref(false)
const isEdit = ref(false)

const ruleForm = reactive({
  name: '',
  description: '',
  rule_type: 'approval',
  priority: 1,
  trigger_conditions: {},
  action_config: {},
  is_active: true
})

const triggerConditionsText = ref('')
const actionConfigText = ref('')

// 可视化配置相关
const activeTab = ref('visual')
const actionTab = ref('visual')
const visualTriggerConditions = ref([])
const visualActions = ref([])

const ruleRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  rule_type: [{ required: true, message: '请选择规则类型', trigger: 'change' }],
  priority: [{ required: true, message: '请输入优先级', trigger: 'blur' }]
}

const loadRules = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...(selectedType.value && { rule_type: selectedType.value }),
      ...(searchKeyword.value && { search: searchKeyword.value })
    }
    const response = await workflowApi.getRules(params)
    rules.value = response.results
    total.value = response.count
  } catch (error) {
    ElMessage.error('加载规则失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadRules()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadRules()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadRules()
}

const getTypeType = (type: string) => {
  const types = {
    approval: 'primary',
    notification: 'success',
    sync: 'warning',
    permission: 'danger',
    employee_management: 'primary',
    department_management: 'success',
    position_management: 'warning',
    permission_management: 'danger',
    integration: 'info',
    data_quality: 'warning',
    reporting: 'success',
    automation: 'primary'
  }
  return types[type] || 'default'
}

const getTypeName = (type: string) => {
  const names = {
    approval: '审批流程',
    notification: '通知规则',
    sync: '数据同步',
    permission: '权限控制',
    employee_management: '员工管理',
    department_management: '部门管理',
    position_management: '职位管理',
    permission_management: '权限管理',
    integration: '系统集成',
    data_quality: '数据质量',
    reporting: '报表生成',
    automation: '自动化'
  }
  return names[type] || type
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const editRule = (rule: any) => {
  isEdit.value = true
  Object.assign(ruleForm, rule)
  triggerConditionsText.value = JSON.stringify(rule.trigger_conditions, null, 2)
  actionConfigText.value = JSON.stringify(rule.action_config, null, 2)
  
  // 尝试解析可视化配置
  try {
    if (rule.trigger_conditions && typeof rule.trigger_conditions === 'object') {
      visualTriggerConditions.value = Array.isArray(rule.trigger_conditions) 
        ? rule.trigger_conditions 
        : [rule.trigger_conditions]
    }
    if (rule.action_config && typeof rule.action_config === 'object') {
      visualActions.value = Array.isArray(rule.action_config) 
        ? rule.action_config 
        : [rule.action_config]
    }
  } catch (e) {
    console.warn('解析可视化配置失败，使用JSON配置', e)
  }
  
  showAddDialog.value = true
}

const deleteRule = async (rule: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个规则吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await workflowApi.deleteRule(rule.id)
    ElMessage.success('删除成功')
    loadRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveRule = async () => {
  try {
    // 根据当前选择的标签页决定使用哪种配置方式
    if (activeTab.value === 'visual') {
      // 使用可视化配置
      ruleForm.trigger_conditions = visualTriggerConditions.value
    } else {
      // 使用JSON配置
      if (triggerConditionsText.value) {
        ruleForm.trigger_conditions = JSON.parse(triggerConditionsText.value)
      }
    }
    
    if (actionTab.value === 'visual') {
      // 使用可视化配置
      ruleForm.action_config = visualActions.value
    } else {
      // 使用JSON配置
      if (actionConfigText.value) {
        ruleForm.action_config = JSON.parse(actionConfigText.value)
      }
    }
    
    if (isEdit.value) {
      await workflowApi.updateRule(ruleForm.id, ruleForm)
    } else {
      await workflowApi.createRule(ruleForm)
    }
    ElMessage.success('保存成功')
    showAddDialog.value = false
    loadRules()
  } catch (error) {
    ElMessage.error('保存失败，请检查配置格式')
  }
}

// 获取动作类型名称
const getActionTypeName = (type: string) => {
  const names = {
    notification: '发送通知',
    approval: '创建审批',
    sync: '数据同步',
    permission: '权限变更',
    auto_execute: '自动执行'
  }
  return names[type] || type
}

// 获取动作类型颜色
const getActionTypeColor = (type: string) => {
  const colors = {
    notification: 'success',
    approval: 'primary',
    sync: 'info',
    permission: 'warning',
    auto_execute: 'danger'
  }
  return colors[type] || 'default'
}

// 格式化动作文本
const formatActionText = (action: any) => {
  switch (action.type) {
    case 'notification':
      return `发送${action.notificationType}通知给: ${action.recipients?.join(', ') || '未设置'}`
    case 'approval':
      return `创建审批流程: ${action.approvalFlow?.join(' → ') || '未设置'}`
    case 'sync':
      return `同步到${action.syncTarget}: ${action.syncFields?.join(', ') || '未设置'}`
    case 'permission':
      return `${action.permissionAction}权限: ${action.permissionScope || '未设置'}`
    case 'auto_execute':
      return `自动执行: ${action.executeType || '未设置'}`
    default:
      return '未知动作'
  }
}

onMounted(() => {
  loadRules()
})
</script>

<style scoped>
.workflow-rules-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f3e8ff 100%);
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

/* 类型导航 */
.type-nav {
  height: fit-content;
}

.type-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.type-item:hover {
  background: #f8fafc;
  border-color: #e2e8f0;
}

.type-item.active {
  background: #f3e8ff;
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgb(139 92 246 / 0.1);
}

.type-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.125rem;
}

.icon-all { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.icon-employee { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.icon-department { background: linear-gradient(135deg, #10b981, #059669); }
.icon-position { background: linear-gradient(135deg, #f59e0b, #d97706); }
.icon-permission { background: linear-gradient(135deg, #ef4444, #dc2626); }
.icon-integration { background: linear-gradient(135deg, #06b6d4, #0891b2); }
.icon-data { background: linear-gradient(135deg, #84cc16, #65a30d); }
.icon-report { background: linear-gradient(135deg, #f97316, #ea580c); }
.icon-auto { background: linear-gradient(135deg, #6366f1, #4f46e5); }

.type-info {
  flex: 1;
}

.type-name {
  font-weight: 500;
  color: #111827;
  margin-bottom: 0.25rem;
}

.type-count {
  font-size: 0.75rem;
  color: #6b7280;
}

/* 规则列表 */
.rule-list {
  height: fit-content;
}

.rules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.rule-card {
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

.rule-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8b5cf6, #7c3aed);
}

.rule-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #8b5cf6;
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.rule-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.icon-default { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.icon-approval { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.icon-notification { background: linear-gradient(135deg, #f97316, #ea580c); }
.icon-sync { background: linear-gradient(135deg, #06b6d4, #0891b2); }

.rule-status {
  display: flex;
  align-items: center;
}

.rule-info {
  margin-bottom: 1rem;
}

.rule-name {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.25rem 0;
}

.rule-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
}

.rule-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.rule-priority {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background: #f3f4f6;
  border-radius: 0.25rem;
  color: #6b7280;
  font-weight: 500;
}

.rule-details {
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

.rule-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.rule-card:hover .rule-actions {
  opacity: 1;
}

/* 对话框样式 */
.action-config-section {
  min-height: 200px;
}

.empty-actions {
  text-align: center;
  padding: 40px 0;
}

.actions-preview {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-preview-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background-color: #fafafa;
}

.action-preview-text {
  color: #606266;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .type-nav {
    order: 2;
  }
  
  .rule-list {
    order: 1;
  }
  
  .type-list {
    flex-direction: row;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .workflow-rules-page {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .rules-grid {
    grid-template-columns: 1fr;
  }
  
  .rule-actions {
    opacity: 1;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .type-list {
    flex-direction: column;
  }
}
</style>
