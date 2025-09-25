<template>
  <div class="workflow-config-builder">
    <!-- 触发条件配置 -->
    <el-card class="config-section">
      <template #header>
        <div class="section-header">
          <span>触发条件配置</span>
          <el-button size="small" type="primary" @click="addTriggerCondition">
            添加条件
          </el-button>
        </div>
      </template>
      
      <div v-if="triggerConditions.length === 0" class="empty-state">
        <el-empty description="暂无触发条件" />
      </div>
      
      <div v-else class="conditions-list">
        <div
          v-for="(condition, index) in triggerConditions"
          :key="index"
          class="condition-item"
        >
          <div class="condition-header">
            <span class="condition-label">条件 {{ index + 1 }}</span>
            <div class="condition-actions">
              <el-button size="small" @click="editCondition(index)">编辑</el-button>
              <el-button size="small" type="danger" @click="removeCondition(index)">删除</el-button>
            </div>
          </div>
          
          <div class="condition-content">
            <el-tag type="info" size="small">{{ getConditionTypeName(condition.type) }}</el-tag>
            <span class="condition-text">{{ formatConditionText(condition) }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 动作配置 -->
    <el-card class="config-section">
      <template #header>
        <div class="section-header">
          <span>动作配置</span>
          <el-button size="small" type="primary" @click="addAction">
            添加动作
          </el-button>
        </div>
      </template>
      
      <div v-if="actions.length === 0" class="empty-state">
        <el-empty description="暂无动作配置" />
      </div>
      
      <div v-else class="actions-list">
        <div
          v-for="(action, index) in actions"
          :key="index"
          class="action-item"
        >
          <div class="action-header">
            <span class="action-label">动作 {{ index + 1 }}</span>
            <div class="action-actions">
              <el-button size="small" @click="editAction(index)">编辑</el-button>
              <el-button size="small" type="danger" @click="removeAction(index)">删除</el-button>
            </div>
          </div>
          
          <div class="action-content">
            <el-tag :type="getActionTypeColor(action.type)" size="small">
              {{ getActionTypeName(action.type) }}
            </el-tag>
            <span class="action-text">{{ formatActionText(action) }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 条件配置对话框 -->
    <el-dialog v-model="showConditionDialog" title="配置触发条件" width="600px">
      <el-form :model="currentCondition" label-width="100px">
        <el-form-item label="条件类型">
          <el-select v-model="currentCondition.type" @change="onConditionTypeChange">
            <el-option label="事件触发" value="event" />
            <el-option label="字段条件" value="field" />
            <el-option label="时间条件" value="time" />
            <el-option label="用户条件" value="user" />
            <el-option label="部门条件" value="department" />
          </el-select>
        </el-form-item>
        
        <!-- 事件触发配置 -->
        <div v-if="currentCondition.type === 'event'">
          <el-form-item label="事件类型">
            <el-select v-model="currentCondition.event">
              <el-option label="员工创建" value="employee_created" />
              <el-option label="员工更新" value="employee_updated" />
              <el-option label="员工离职" value="employee_resigned" />
              <el-option label="部门创建" value="department_created" />
              <el-option label="部门更新" value="department_updated" />
              <el-option label="职位创建" value="position_created" />
              <el-option label="职位更新" value="position_updated" />
            </el-select>
          </el-form-item>
        </div>
        
        <!-- 字段条件配置 -->
        <div v-if="currentCondition.type === 'field'">
          <el-form-item label="字段名称">
            <el-select v-model="currentCondition.field">
              <el-option label="职位级别" value="position_level" />
              <el-option label="部门类型" value="department_type" />
              <el-option label="员工状态" value="employee_status" />
              <el-option label="学历层次" value="education_level" />
              <el-option label="入职时间" value="join_date" />
            </el-select>
          </el-form-item>
          <el-form-item label="比较操作">
            <el-select v-model="currentCondition.operator">
              <el-option label="等于" value="eq" />
              <el-option label="不等于" value="ne" />
              <el-option label="大于" value="gt" />
              <el-option label="大于等于" value="gte" />
              <el-option label="小于" value="lt" />
              <el-option label="小于等于" value="lte" />
              <el-option label="包含" value="in" />
              <el-option label="不包含" value="nin" />
            </el-select>
          </el-form-item>
          <el-form-item label="比较值">
            <el-input v-model="currentCondition.value" placeholder="请输入比较值" />
          </el-form-item>
        </div>
        
        <!-- 时间条件配置 -->
        <div v-if="currentCondition.type === 'time'">
          <el-form-item label="时间类型">
            <el-select v-model="currentCondition.timeType">
              <el-option label="工作时间" value="work_time" />
              <el-option label="非工作时间" value="non_work_time" />
              <el-option label="特定时间" value="specific_time" />
              <el-option label="工作日" value="workday" />
              <el-option label="周末" value="weekend" />
            </el-select>
          </el-form-item>
          <el-form-item v-if="currentCondition.timeType === 'specific_time'" label="具体时间">
            <el-time-picker v-model="currentCondition.specificTime" />
          </el-form-item>
        </div>
        
        <!-- 用户条件配置 -->
        <div v-if="currentCondition.type === 'user'">
          <el-form-item label="用户角色">
            <el-select v-model="currentCondition.role">
              <el-option label="管理员" value="admin" />
              <el-option label="HR" value="hr" />
              <el-option label="部门经理" value="manager" />
              <el-option label="普通员工" value="employee" />
            </el-select>
          </el-form-item>
          <el-form-item label="用户部门">
            <el-select v-model="currentCondition.userDepartment">
              <el-option label="人事部" value="hr" />
              <el-option label="技术部" value="tech" />
              <el-option label="销售部" value="sales" />
              <el-option label="财务部" value="finance" />
            </el-select>
          </el-form-item>
        </div>
        
        <!-- 部门条件配置 -->
        <div v-if="currentCondition.type === 'department'">
          <el-form-item label="部门类型">
            <el-select v-model="currentCondition.departmentType">
              <el-option label="管理部门" value="management" />
              <el-option label="业务部门" value="business" />
              <el-option label="支持部门" value="support" />
              <el-option label="技术部门" value="technical" />
            </el-select>
          </el-form-item>
          <el-form-item label="部门级别">
            <el-input-number v-model="currentCondition.departmentLevel" :min="1" :max="5" />
          </el-form-item>
        </div>
      </el-form>
      
      <template #footer>
        <el-button @click="showConditionDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCondition">保存</el-button>
      </template>
    </el-dialog>

    <!-- 动作配置对话框 -->
    <el-dialog v-model="showActionDialog" title="配置动作" width="600px">
      <el-form :model="currentAction" label-width="100px">
        <el-form-item label="动作类型">
          <el-select v-model="currentAction.type" @change="onActionTypeChange">
            <el-option label="发送通知" value="notification" />
            <el-option label="创建审批" value="approval" />
            <el-option label="数据同步" value="sync" />
            <el-option label="权限变更" value="permission" />
            <el-option label="自动执行" value="auto_execute" />
          </el-select>
        </el-form-item>
        
        <!-- 通知动作配置 -->
        <div v-if="currentAction.type === 'notification'">
          <el-form-item label="通知类型">
            <el-select v-model="currentAction.notificationType">
              <el-option label="邮件通知" value="email" />
              <el-option label="系统通知" value="system" />
              <el-option label="短信通知" value="sms" />
              <el-option label="微信通知" value="wechat" />
            </el-select>
          </el-form-item>
          <el-form-item label="接收人">
            <el-select v-model="currentAction.recipients" multiple>
              <el-option label="直接上级" value="direct_supervisor" />
              <el-option label="部门经理" value="department_manager" />
              <el-option label="HR" value="hr" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>
          <el-form-item label="通知内容">
            <el-input v-model="currentAction.message" type="textarea" />
          </el-form-item>
        </div>
        
        <!-- 审批动作配置 -->
        <div v-if="currentAction.type === 'approval'">
          <el-form-item label="审批流程">
            <el-select v-model="currentAction.approvalFlow" multiple>
              <el-option label="直接上级审批" value="direct_supervisor" />
              <el-option label="部门经理审批" value="department_manager" />
              <el-option label="HR审批" value="hr" />
              <el-option label="总经理审批" value="general_manager" />
            </el-select>
          </el-form-item>
          <el-form-item label="审批时限(小时)">
            <el-input-number v-model="currentAction.timeout" :min="1" :max="168" />
          </el-form-item>
          <el-form-item label="是否必需">
            <el-switch v-model="currentAction.required" />
          </el-form-item>
        </div>
        
        <!-- 数据同步动作配置 -->
        <div v-if="currentAction.type === 'sync'">
          <el-form-item label="同步目标">
            <el-select v-model="currentAction.syncTarget">
              <el-option label="绩效考核系统" value="performance_system" />
              <el-option label="财务系统" value="finance_system" />
              <el-option label="OA系统" value="oa_system" />
              <el-option label="CRM系统" value="crm_system" />
            </el-select>
          </el-form-item>
          <el-form-item label="同步字段">
            <el-select v-model="currentAction.syncFields" multiple>
              <el-option label="基本信息" value="basic_info" />
              <el-option label="组织关系" value="organization" />
              <el-option label="职位信息" value="position" />
              <el-option label="联系方式" value="contact" />
            </el-select>
          </el-form-item>
        </div>
        
        <!-- 权限变更动作配置 -->
        <div v-if="currentAction.type === 'permission'">
          <el-form-item label="权限类型">
            <el-select v-model="currentAction.permissionType">
              <el-option label="系统权限" value="system" />
              <el-option label="数据权限" value="data" />
              <el-option label="功能权限" value="function" />
            </el-select>
          </el-form-item>
          <el-form-item label="权限操作">
            <el-select v-model="currentAction.permissionAction">
              <el-option label="授予权限" value="grant" />
              <el-option label="撤销权限" value="revoke" />
              <el-option label="修改权限" value="modify" />
            </el-select>
          </el-form-item>
          <el-form-item label="权限范围">
            <el-input v-model="currentAction.permissionScope" placeholder="请输入权限范围" />
          </el-form-item>
        </div>
        
        <!-- 自动执行动作配置 -->
        <div v-if="currentAction.type === 'auto_execute'">
          <el-form-item label="执行类型">
            <el-select v-model="currentAction.executeType">
              <el-option label="自动创建账号" value="create_account" />
              <el-option label="自动分配权限" value="assign_permission" />
              <el-option label="自动发送邮件" value="send_email" />
              <el-option label="自动生成报表" value="generate_report" />
            </el-select>
          </el-form-item>
          <el-form-item label="执行参数">
            <el-input v-model="currentAction.executeParams" type="textarea" placeholder="请输入执行参数(JSON格式)" />
          </el-form-item>
        </div>
      </el-form>
      
      <template #footer>
        <el-button @click="showActionDialog = false">取消</el-button>
        <el-button type="primary" @click="saveAction">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, defineProps, defineEmits } from 'vue'

const props = defineProps<{
  triggerConditions: any[]
  actions: any[]
}>()

const emit = defineEmits<{
  'update:triggerConditions': [conditions: any[]]
  'update:actions': [actions: any[]]
}>()

// 对话框状态
const showConditionDialog = ref(false)
const showActionDialog = ref(false)
const editingConditionIndex = ref(-1)
const editingActionIndex = ref(-1)

// 当前编辑的条件和动作
const currentCondition = reactive({
  type: 'event',
  event: '',
  field: '',
  operator: 'eq',
  value: '',
  timeType: '',
  specificTime: null,
  role: '',
  userDepartment: '',
  departmentType: '',
  departmentLevel: 1
})

const currentAction = reactive({
  type: 'notification',
  notificationType: 'email',
  recipients: [],
  message: '',
  approvalFlow: [],
  timeout: 24,
  required: true,
  syncTarget: '',
  syncFields: [],
  permissionType: 'system',
  permissionAction: 'grant',
  permissionScope: '',
  executeType: 'create_account',
  executeParams: ''
})

// 添加条件
const addTriggerCondition = () => {
  editingConditionIndex.value = -1
  resetCurrentCondition()
  showConditionDialog.value = true
}

// 编辑条件
const editCondition = (index: number) => {
  editingConditionIndex.value = index
  Object.assign(currentCondition, props.triggerConditions[index])
  showConditionDialog.value = true
}

// 删除条件
const removeCondition = (index: number) => {
  const newConditions = [...props.triggerConditions]
  newConditions.splice(index, 1)
  emit('update:triggerConditions', newConditions)
}

// 保存条件
const saveCondition = () => {
  const newConditions = [...props.triggerConditions]
  const conditionData = { ...currentCondition }
  
  if (editingConditionIndex.value >= 0) {
    newConditions[editingConditionIndex.value] = conditionData
  } else {
    newConditions.push(conditionData)
  }
  
  emit('update:triggerConditions', newConditions)
  showConditionDialog.value = false
}

// 添加动作
const addAction = () => {
  editingActionIndex.value = -1
  resetCurrentAction()
  showActionDialog.value = true
}

// 编辑动作
const editAction = (index: number) => {
  editingActionIndex.value = index
  Object.assign(currentAction, props.actions[index])
  showActionDialog.value = true
}

// 删除动作
const removeAction = (index: number) => {
  const newActions = [...props.actions]
  newActions.splice(index, 1)
  emit('update:actions', newActions)
}

// 保存动作
const saveAction = () => {
  const newActions = [...props.actions]
  const actionData = { ...currentAction }
  
  if (editingActionIndex.value >= 0) {
    newActions[editingActionIndex.value] = actionData
  } else {
    newActions.push(actionData)
  }
  
  emit('update:actions', newActions)
  showActionDialog.value = false
}

// 重置当前条件
const resetCurrentCondition = () => {
  Object.assign(currentCondition, {
    type: 'event',
    event: '',
    field: '',
    operator: 'eq',
    value: '',
    timeType: '',
    specificTime: null,
    role: '',
    userDepartment: '',
    departmentType: '',
    departmentLevel: 1
  })
}

// 重置当前动作
const resetCurrentAction = () => {
  Object.assign(currentAction, {
    type: 'notification',
    notificationType: 'email',
    recipients: [],
    message: '',
    approvalFlow: [],
    timeout: 24,
    required: true,
    syncTarget: '',
    syncFields: [],
    permissionType: 'system',
    permissionAction: 'grant',
    permissionScope: '',
    executeType: 'create_account',
    executeParams: ''
  })
}

// 条件类型变化处理
const onConditionTypeChange = () => {
  // 根据条件类型重置相关字段
  resetCurrentCondition()
  currentCondition.type = currentCondition.type
}

// 动作类型变化处理
const onActionTypeChange = () => {
  // 根据动作类型重置相关字段
  resetCurrentAction()
  currentAction.type = currentAction.type
}

// 获取条件类型名称
const getConditionTypeName = (type: string) => {
  const names = {
    event: '事件触发',
    field: '字段条件',
    time: '时间条件',
    user: '用户条件',
    department: '部门条件'
  }
  return names[type] || type
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

// 格式化条件文本
const formatConditionText = (condition: any) => {
  switch (condition.type) {
    case 'event':
      return `当事件 "${condition.event}" 发生时`
    case 'field':
      return `字段 "${condition.field}" ${condition.operator} "${condition.value}"`
    case 'time':
      return `时间条件: ${condition.timeType}`
    case 'user':
      return `用户角色: ${condition.role}, 部门: ${condition.userDepartment}`
    case 'department':
      return `部门类型: ${condition.departmentType}, 级别: ${condition.departmentLevel}`
    default:
      return '未知条件'
  }
}

// 格式化动作文本
const formatActionText = (action: any) => {
  switch (action.type) {
    case 'notification':
      return `发送${action.notificationType}通知给: ${action.recipients.join(', ')}`
    case 'approval':
      return `创建审批流程: ${action.approvalFlow.join(' → ')}`
    case 'sync':
      return `同步到${action.syncTarget}: ${action.syncFields.join(', ')}`
    case 'permission':
      return `${action.permissionAction}权限: ${action.permissionScope}`
    case 'auto_execute':
      return `自动执行: ${action.executeType}`
    default:
      return '未知动作'
  }
}
</script>

<style scoped>
.workflow-config-builder {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 20px;
}

.conditions-list,
.actions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.condition-item,
.action-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  background-color: #fafafa;
}

.condition-header,
.action-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.condition-label,
.action-label {
  font-weight: 500;
  color: #303133;
}

.condition-actions,
.action-actions {
  display: flex;
  gap: 8px;
}

.condition-content,
.action-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.condition-text,
.action-text {
  color: #606266;
  font-size: 14px;
}
</style>
