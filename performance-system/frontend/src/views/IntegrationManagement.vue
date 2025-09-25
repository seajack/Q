<template>
  <div class="integration-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">集成管理</h1>
      <p class="page-description">管理系统集成配置和数据同步</p>
    </div>

    <el-row :gutter="24">
      <!-- 集成配置 -->
      <el-col :xs="24" :lg="16">
        <el-card class="integration-card">
          <template #header>
            <div class="card-header">
              <h3>集成配置</h3>
              <el-button type="primary" @click="showAddIntegrationDialog = true">
                <el-icon><Plus /></el-icon>
                添加集成
              </el-button>
            </div>
          </template>
          
          <div class="integration-list">
            <div 
              v-for="integration in integrations" 
              :key="integration.id" 
              class="integration-item"
            >
              <div class="integration-info">
                <div class="integration-icon">
                  <el-icon><component :is="integration.icon" /></el-icon>
                </div>
                <div class="integration-details">
                  <h4>{{ integration.name }}</h4>
                  <p>{{ integration.description }}</p>
                  <div class="integration-meta">
                    <el-tag :type="getStatusType(integration.status)" size="small">
                      {{ getStatusText(integration.status) }}
                    </el-tag>
                    <span class="integration-type">{{ integration.type }}</span>
                  </div>
                </div>
              </div>
              <div class="integration-actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="testConnection(integration)"
                >
                  测试连接
                </el-button>
                <el-button 
                  type="warning" 
                  size="small" 
                  @click="editIntegration(integration)"
                >
                  编辑
                </el-button>
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="deleteIntegration(integration)"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 数据同步状态 -->
      <el-col :xs="24" :lg="8">
        <el-card class="sync-status-card">
          <template #header>
            <h3>数据同步状态</h3>
          </template>
          
          <div class="sync-stats">
            <div class="sync-stat-item">
              <div class="stat-icon success">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ syncStats.successful }}</div>
                <div class="stat-label">成功同步</div>
              </div>
            </div>
            
            <div class="sync-stat-item">
              <div class="stat-icon warning">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ syncStats.failed }}</div>
                <div class="stat-label">同步失败</div>
              </div>
            </div>
            
            <div class="sync-stat-item">
              <div class="stat-icon info">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ syncStats.pending }}</div>
                <div class="stat-label">待同步</div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 最近同步记录 -->
        <el-card class="sync-logs-card">
          <template #header>
            <h3>最近同步记录</h3>
          </template>
          
          <div class="sync-logs">
            <div 
              v-for="log in syncLogs" 
              :key="log.id" 
              class="sync-log-item"
            >
              <div class="log-icon">
                <el-icon :class="getLogIconClass(log.status)">
                  <component :is="getLogIcon(log.status)" />
                </el-icon>
              </div>
              <div class="log-content">
                <p class="log-message">{{ log.message }}</p>
                <span class="log-time">{{ formatTime(log.createdAt) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加集成对话框 -->
    <el-dialog v-model="showAddIntegrationDialog" title="添加集成" width="600px">
      <el-form :model="newIntegration" label-width="100px">
        <el-form-item label="集成名称">
          <el-input v-model="newIntegration.name" placeholder="请输入集成名称" />
        </el-form-item>
        <el-form-item label="集成类型">
          <el-select v-model="newIntegration.type" placeholder="请选择集成类型">
            <el-option label="组织架构中台" value="org-platform" />
            <el-option label="HR系统" value="hr-system" />
            <el-option label="财务系统" value="finance-system" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="API地址">
          <el-input v-model="newIntegration.apiUrl" placeholder="请输入API地址" />
        </el-form-item>
        <el-form-item label="认证方式">
          <el-radio-group v-model="newIntegration.authType">
            <el-radio label="token">Token认证</el-radio>
            <el-radio label="basic">基础认证</el-radio>
            <el-radio label="oauth">OAuth2</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            v-model="newIntegration.description" 
            type="textarea" 
            placeholder="请输入集成描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddIntegrationDialog = false">取消</el-button>
        <el-button type="primary" @click="addIntegration">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Plus, Check, Warning, Clock, 
  Document, Setting, Connection, DataBoard
} from '@element-plus/icons-vue'

// 数据状态
const showAddIntegrationDialog = ref(false)
const integrations = ref([
  {
    id: 1,
    name: '组织架构中台',
    description: '企业组织架构数据同步',
    type: 'org-platform',
    status: 'active',
    icon: 'OfficeBuilding',
    apiUrl: 'http://127.0.0.1:8001/api'
  },
  {
    id: 2,
    name: 'HR系统',
    description: '人力资源管理系统集成',
    type: 'hr-system',
    status: 'inactive',
    icon: 'User',
    apiUrl: 'http://hr.example.com/api'
  },
  {
    id: 3,
    name: '财务系统',
    description: '财务数据同步',
    type: 'finance-system',
    status: 'error',
    icon: 'Money',
    apiUrl: 'http://finance.example.com/api'
  }
])

const syncStats = ref({
  successful: 156,
  failed: 3,
  pending: 12
})

const syncLogs = ref([
  {
    id: 1,
    message: '组织架构数据同步成功',
    status: 'success',
    createdAt: new Date(Date.now() - 1000 * 60 * 5)
  },
  {
    id: 2,
    message: '员工信息同步失败',
    status: 'error',
    createdAt: new Date(Date.now() - 1000 * 60 * 15)
  },
  {
    id: 3,
    message: '部门数据同步中',
    status: 'pending',
    createdAt: new Date(Date.now() - 1000 * 60 * 30)
  }
])

const newIntegration = ref({
  name: '',
  type: '',
  apiUrl: '',
  authType: 'token',
  description: ''
})

// 方法
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'active': 'success',
    'inactive': 'info',
    'error': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'active': '已连接',
    'inactive': '未连接',
    'error': '连接错误'
  }
  return statusMap[status] || status
}

const getLogIcon = (status: string) => {
  const iconMap: Record<string, string> = {
    'success': 'Check',
    'error': 'Close',
    'pending': 'Clock'
  }
  return iconMap[status] || 'Info'
}

const getLogIconClass = (status: string) => {
  const classMap: Record<string, string> = {
    'success': 'success',
    'error': 'error',
    'pending': 'warning'
  }
  return classMap[status] || ''
}

const formatTime = (date: Date) => {
  return date.toLocaleString('zh-CN')
}

const testConnection = (integration: any) => {
  ElMessage.info(`测试连接: ${integration.name}`)
}

const editIntegration = (integration: any) => {
  ElMessage.info(`编辑集成: ${integration.name}`)
}

const deleteIntegration = (integration: any) => {
  ElMessage.warning(`删除集成: ${integration.name}`)
}

const addIntegration = () => {
  if (!newIntegration.value.name) {
    ElMessage.warning('请输入集成名称')
    return
  }
  
  integrations.value.push({
    id: Date.now(),
    name: newIntegration.value.name,
    description: newIntegration.value.description,
    type: newIntegration.value.type,
    status: 'inactive',
    icon: 'Connection',
    apiUrl: newIntegration.value.apiUrl
  })
  
  newIntegration.value = {
    name: '',
    type: '',
    apiUrl: '',
    authType: 'token',
    description: ''
  }
  
  showAddIntegrationDialog.value = false
  ElMessage.success('集成添加成功')
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.integration-management {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  letter-spacing: -0.5px;
}

.page-description {
  color: var(--text-secondary);
  font-size: 16px;
  margin: 0;
  font-weight: 400;
  line-height: 1.5;
}

.integration-card, .sync-status-card, .sync-logs-card {
  height: fit-content;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.25px;
}

.integration-list {
  space-y: 16px;
}

.integration-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  transition: all 0.3s ease;
  background: var(--bg-primary);
}

.integration-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.integration-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.integration-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--primary-50);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  font-size: 20px;
}

.integration-details h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.integration-details p {
  margin: 0 0 8px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.integration-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.integration-type {
  font-size: 12px;
  color: var(--text-tertiary);
  background: var(--gray-100);
  padding: 2px 8px;
  border-radius: 4px;
}

.integration-actions {
  display: flex;
  gap: 8px;
}

.sync-stats {
  space-y: 16px;
}

.sync-stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--border-light);
  border-radius: 10px;
  background: var(--bg-primary);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.stat-icon.success {
  background: var(--success-50);
  color: var(--success-color);
}

.stat-icon.warning {
  background: var(--warning-50);
  color: var(--warning-color);
}

.stat-icon.info {
  background: var(--info-50);
  color: var(--info-color);
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.sync-logs {
  space-y: 12px;
}

.sync-log-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  background: var(--bg-primary);
}

.log-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.log-icon.success {
  background: var(--success-50);
  color: var(--success-color);
}

.log-icon.error {
  background: var(--danger-50);
  color: var(--danger-color);
}

.log-icon.warning {
  background: var(--warning-50);
  color: var(--warning-color);
}

.log-content {
  flex: 1;
}

.log-message {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.log-time {
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
