<template>
  <div class="workflow-designer">
    <!-- 顶部工具栏 -->
    <div class="designer-header">
      <div class="header-left">
        <el-icon class="header-icon"><Grid /></el-icon>
        <div>
          <h1 class="header-title">工作流设计器</h1>
          <p class="header-subtitle">拖拽式流程设计平台</p>
        </div>
      </div>
      
      <div class="header-actions">
        <el-tag type="info" size="small">版本: {{ currentVersion }}</el-tag>
        <el-button type="primary" :icon="Grid" @click="saveWorkflow" :loading="saving">
          保存
        </el-button>
        <el-button type="success" :icon="VideoPlay" @click="testWorkflow">
          测试
        </el-button>
        <el-button :icon="Grid" @click="showVersionDialog = true">
          版本
        </el-button>
      </div>
    </div>

    <div class="designer-body">
      <!-- 左侧工具面板 -->
      <div class="left-panel">
        <!-- 节点库 -->
        <div class="node-library">
          <h3 class="panel-title">
            <el-icon><Grid /></el-icon>
            节点库
          </h3>
          
          <div class="node-categories">
            <div v-for="category in nodeCategories" :key="category.name" class="node-category">
              <h4 class="category-title">{{ category.name }}</h4>
              <div class="node-grid">
                <div 
                  v-for="node in category.nodes" 
                  :key="node.type"
                  class="node-item"
                  :class="`node-${node.type}`"
                  draggable="true"
                  @dragstart="onNodeDragStart($event, node)"
                >
                  <el-icon class="node-icon">
                    <component :is="node.icon" />
                  </el-icon>
                  <div class="node-label">{{ node.label }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 属性面板 -->
        <div class="property-panel">
          <h3 class="panel-title">
            <el-icon><Setting /></el-icon>
            属性配置
          </h3>
          
          <div v-if="selectedNode" class="property-form">
            <el-form :model="selectedNode" label-width="80px" size="small">
              <el-form-item label="节点名称">
                <el-input v-model="selectedNode.name" />
              </el-form-item>
              
              <el-form-item label="描述">
                <el-input v-model="selectedNode.description" type="textarea" :rows="2" />
              </el-form-item>
              
              <!-- 动态属性配置 -->
              <component 
                :is="getNodeConfigComponent(selectedNode.type)"
                v-model="selectedNode.config"
                @change="onNodeConfigChange"
              />
            </el-form>
          </div>
          
          <div v-else class="no-selection">
            <el-empty description="请选择一个节点" :image-size="60" />
          </div>
        </div>
      </div>

      <!-- 中间画布区域 -->
      <div class="canvas-area">
        <!-- 画布工具栏 -->
        <div class="canvas-toolbar">
          <div class="toolbar-left">
            <el-button-group size="small">
              <el-button :icon="Pointer" :type="tool === 'select' ? 'primary' : ''" @click="tool = 'select'" />
              <el-button :icon="Pointer" :type="tool === 'pan' ? 'primary' : ''" @click="tool = 'pan'" />
            </el-button-group>
            
            <el-divider direction="vertical" />
            
            <el-button-group size="small">
              <el-button :icon="RefreshLeft" @click="undo" :disabled="!canUndo" />
              <el-button :icon="RefreshRight" @click="redo" :disabled="!canRedo" />
            </el-button-group>
            
            <el-divider direction="vertical" />
            
            <div class="zoom-controls">
              <span class="zoom-label">缩放:</span>
              <el-button size="small" :icon="Minus" @click="zoomOut" />
              <span class="zoom-value">{{ Math.round(zoom * 100) }}%</span>
              <el-button size="small" :icon="Plus" @click="zoomIn" />
            </div>
          </div>
          
          <div class="toolbar-right">
            <el-tag :type="workflowStatus.type" size="small">
              {{ workflowStatus.text }}
            </el-tag>
          </div>
        </div>

        <!-- 画布 -->
        <div 
          ref="canvas" 
          class="workflow-canvas"
          @drop="onCanvasDrop"
          @dragover.prevent
          @click="onCanvasClick"
        >
          <div 
            class="canvas-content"
            :style="{ transform: `scale(${zoom}) translate(${panX}px, ${panY}px)` }"
          >
            <!-- 工作流节点 -->
            <WorkflowNode
              v-for="node in workflow.nodes"
              :key="node.id"
              :node="node"
              :selected="selectedNode?.id === node.id"
              @select="selectNode"
              @update="updateNode"
              @delete="deleteNode"
            />
            
            <!-- 连接线 -->
            <WorkflowConnection
              v-for="connection in workflow.connections"
              :key="connection.id"
              :connection="connection"
              :nodes="workflow.nodes"
              @delete="deleteConnection"
            />
          </div>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="right-panel">
        <!-- 版本管理 -->
        <div class="version-panel">
          <h3 class="panel-title">
            <el-icon><Grid /></el-icon>
            版本管理
          </h3>
          
          <div class="version-list">
            <div 
              v-for="version in versions" 
              :key="version.id"
              class="version-item"
              :class="{ active: version.id === currentVersion }"
            >
              <div class="version-header">
                <span class="version-name">{{ version.name }}</span>
                <span class="version-date">{{ formatDate(version.createdAt) }}</span>
              </div>
              <div class="version-description">{{ version.description }}</div>
              
              <div v-if="version.id !== currentVersion" class="version-actions">
                <el-button size="small" text @click="rollbackVersion(version.id)">
                  回滚
                </el-button>
                <el-button size="small" text @click="compareVersion(version.id)">
                  对比
                </el-button>
              </div>
            </div>
          </div>
          
          <el-button type="primary" size="small" class="create-version-btn" @click="createVersion">
            创建新版本
          </el-button>
        </div>

        <!-- 测试面板 -->
        <div class="test-panel">
          <h3 class="panel-title">
            <el-icon><VideoPlay /></el-icon>
            测试执行
          </h3>
          
          <!-- 测试配置 -->
          <div class="test-config">
            <h4 class="config-title">测试数据</h4>
            <el-form :model="testData" size="small">
              <el-form-item label="申请人">
                <el-input v-model="testData.applicant" />
              </el-form-item>
              <el-form-item label="类型">
                <el-select v-model="testData.type" style="width: 100%">
                  <el-option label="请假申请" value="leave" />
                  <el-option label="报销申请" value="expense" />
                </el-select>
              </el-form-item>
            </el-form>
          </div>
          
          <!-- 执行控制 -->
          <div class="test-controls">
            <el-button 
              type="primary" 
              size="small" 
              :loading="testing"
              @click="startTest"
              style="flex: 1"
            >
              开始测试
            </el-button>
            <el-button size="small" :icon="Grid" @click="stopTest" />
          </div>
          
          <!-- 执行日志 -->
          <div class="test-logs">
            <div class="log-content">
              <div 
                v-for="(log, index) in testLogs" 
                :key="index"
                class="log-item"
                :class="log.type"
              >
                [{{ formatTime(log.timestamp) }}] {{ log.message }}
              </div>
            </div>
          </div>
          
          <!-- 性能统计 -->
          <div v-if="testStats" class="test-stats">
            <h4 class="stats-title">执行统计</h4>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-label">执行时间:</span>
                <span class="stat-value">{{ testStats.duration }}秒</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">节点数量:</span>
                <span class="stat-value">{{ testStats.nodeCount }}个</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">成功率:</span>
                <span class="stat-value success">{{ testStats.successRate }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 版本对话框 -->
    <el-dialog v-model="showVersionDialog" title="版本管理" width="600px">
      <VersionManager 
        :versions="versions"
        :current="currentVersion"
        @create="onVersionCreate"
        @rollback="onVersionRollback"
        @compare="onVersionCompare"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Grid, Setting, VideoPlay,
  Pointer, RefreshLeft, RefreshRight, Minus, Plus
} from '@element-plus/icons-vue'

// 组件导入
import WorkflowNode from '@/components/workflow/WorkflowNode.vue'
import WorkflowConnection from '@/components/workflow/WorkflowConnection.vue'
import VersionManager from '@/components/workflow/VersionManager.vue'

// 响应式数据
const canvas = ref<HTMLElement>()
const selectedNode = ref(null)
const tool = ref('select')
const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)
const saving = ref(false)
const testing = ref(false)
const showVersionDialog = ref(false)

// 工作流数据
const workflow = reactive({
  id: '',
  name: '新工作流',
  nodes: [],
  connections: []
})

const currentVersion = ref('v1.0.0')
const versions = ref([
  {
    id: 'v1.0.0',
    name: 'v1.0.0',
    description: '初始版本',
    createdAt: new Date(),
    workflow: { ...workflow }
  }
])

// 测试数据
const testData = reactive({
  applicant: '张三',
  type: 'leave'
})

const testLogs = ref([])
const testStats = ref(null)

// 节点类别定义
const nodeCategories = ref([
  {
    name: '触发器',
    nodes: [
      { type: 'start', label: '开始', icon: 'VideoPlay' },
      { type: 'timer', label: '定时', icon: 'Timer' }
    ]
  },
  {
    name: '处理器',
    nodes: [
      { type: 'approval', label: '审批', icon: 'Check' },
      { type: 'notification', label: '通知', icon: 'Bell' },
      { type: 'data', label: '数据', icon: 'Database' },
      { type: 'condition', label: '条件', icon: 'Grid' }
    ]
  },
  {
    name: '结束器',
    nodes: [
      { type: 'end', label: '结束', icon: 'CircleCheck' },
      { type: 'error', label: '错误', icon: 'CircleClose' }
    ]
  }
])

// 计算属性
const workflowStatus = computed(() => {
  if (testing.value) {
    return { type: 'warning', text: '测试中' }
  }
  if (workflow.nodes.length === 0) {
    return { type: 'info', text: '空工作流' }
  }
  return { type: 'success', text: '已保存' }
})

const canUndo = computed(() => {
  // 实现撤销逻辑
  return false
})

const canRedo = computed(() => {
  // 实现重做逻辑
  return false
})

// 方法
const onNodeDragStart = (event: DragEvent, node: any) => {
  event.dataTransfer?.setData('application/json', JSON.stringify(node))
}

const onCanvasDrop = (event: DragEvent) => {
  event.preventDefault()
  const nodeData = JSON.parse(event.dataTransfer?.getData('application/json') || '{}')
  
  const rect = canvas.value?.getBoundingClientRect()
  if (rect) {
    const x = (event.clientX - rect.left) / zoom.value - panX.value
    const y = (event.clientY - rect.top) / zoom.value - panY.value
    
    addNode(nodeData, x, y)
  }
}

const addNode = (nodeData: any, x: number, y: number) => {
  const newNode = {
    id: generateId(),
    type: nodeData.type,
    name: nodeData.label,
    x,
    y,
    config: getDefaultConfig(nodeData.type)
  }
  
  workflow.nodes.push(newNode)
  ElMessage.success('节点已添加')
}

const selectNode = (node: any) => {
  selectedNode.value = node
}

const updateNode = (nodeId: string, updates: any) => {
  const node = workflow.nodes.find(n => n.id === nodeId)
  if (node) {
    Object.assign(node, updates)
  }
}

const deleteNode = (nodeId: string) => {
  const index = workflow.nodes.findIndex(n => n.id === nodeId)
  if (index > -1) {
    workflow.nodes.splice(index, 1)
    // 删除相关连接
    workflow.connections = workflow.connections.filter(
      c => c.sourceId !== nodeId && c.targetId !== nodeId
    )
  }
}

const saveWorkflow = async () => {
  saving.value = true
  try {
    // 调用API保存工作流
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟API调用
    ElMessage.success('工作流已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const testWorkflow = () => {
  if (workflow.nodes.length === 0) {
    ElMessage.warning('请先添加节点')
    return
  }
  startTest()
}

const startTest = async () => {
  testing.value = true
  testLogs.value = []
  
  try {
    // 模拟测试执行
    addTestLog('info', '工作流开始执行')
    
    for (const node of workflow.nodes) {
      await new Promise(resolve => setTimeout(resolve, 500))
      addTestLog('success', `执行节点: ${node.name}`)
    }
    
    addTestLog('success', '工作流执行完成')
    
    // 生成统计数据
    testStats.value = {
      duration: (workflow.nodes.length * 0.5).toFixed(1),
      nodeCount: workflow.nodes.length,
      successRate: 100
    }
    
  } catch (error) {
    addTestLog('error', '执行失败: ' + error.message)
  } finally {
    testing.value = false
  }
}

const addTestLog = (type: string, message: string) => {
  testLogs.value.push({
    type,
    message,
    timestamp: new Date()
  })
}

const createVersion = async () => {
  const { value: description } = await ElMessageBox.prompt('请输入版本描述', '创建新版本')
  
  if (description) {
    const newVersion = {
      id: `v1.${versions.value.length}.0`,
      name: `v1.${versions.value.length}.0`,
      description,
      createdAt: new Date(),
      workflow: JSON.parse(JSON.stringify(workflow))
    }
    
    versions.value.unshift(newVersion)
    currentVersion.value = newVersion.id
    ElMessage.success('版本创建成功')
  }
}

const rollbackVersion = async (versionId: string) => {
  await ElMessageBox.confirm('确定要回滚到此版本吗？', '确认回滚')
  
  const version = versions.value.find(v => v.id === versionId)
  if (version) {
    Object.assign(workflow, version.workflow)
    currentVersion.value = versionId
    ElMessage.success('回滚成功')
  }
}

// 工具函数
const generateId = () => {
  return 'node_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

const getDefaultConfig = (nodeType: string) => {
  const configs = {
    approval: { approver: 'direct_supervisor', timeout: 24 },
    notification: { type: 'email', template: 'default' },
    condition: { operator: 'equals', value: '' }
  }
  return configs[nodeType] || {}
}

const formatDate = (date: Date) => {
  return date.toLocaleDateString()
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString()
}

// 生命周期
onMounted(() => {
  // 初始化画布
})
</script>

<style scoped>
.workflow-designer {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.designer-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  font-size: 2rem;
}

.header-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.header-subtitle {
  font-size: 0.875rem;
  opacity: 0.9;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.designer-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.left-panel {
  width: 320px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.node-library {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.property-panel {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #374151;
}

.node-categories {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.category-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.node-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.node-item {
  padding: 0.75rem;
  border: 2px solid;
  border-radius: 0.5rem;
  text-align: center;
  cursor: grab;
  transition: all 0.3s ease;
}

.node-item:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.node-icon {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.node-label {
  font-size: 0.75rem;
  font-weight: 500;
}

/* 节点类型样式 */
.node-start { border-color: #10b981; background: #ecfdf5; color: #065f46; }
.node-timer { border-color: #3b82f6; background: #eff6ff; color: #1e40af; }
.node-approval { border-color: #8b5cf6; background: #f3e8ff; color: #5b21b6; }
.node-notification { border-color: #f59e0b; background: #fffbeb; color: #92400e; }
.node-data { border-color: #6366f1; background: #eef2ff; color: #3730a3; }
.node-condition { border-color: #ef4444; background: #fef2f2; color: #991b1b; }
.node-end { border-color: #6b7280; background: #f9fafb; color: #374151; }
.node-error { border-color: #f97316; background: #fff7ed; color: #9a3412; }

.canvas-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.canvas-toolbar {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.zoom-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.zoom-value {
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 3rem;
  text-align: center;
}

.workflow-canvas {
  flex: 1;
  background: #f9fafb;
  background-image: radial-gradient(circle, #e5e7eb 1px, transparent 1px);
  background-size: 20px 20px;
  overflow: hidden;
  position: relative;
}

.canvas-content {
  width: 100%;
  height: 100%;
  transform-origin: 0 0;
}

.right-panel {
  width: 320px;
  background: white;
  border-left: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.version-panel {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.version-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.version-item {
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.version-item.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.version-name {
  font-weight: 500;
}

.version-date {
  font-size: 0.75rem;
  color: #6b7280;
}

.version-description {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.version-actions {
  display: flex;
  gap: 0.5rem;
}

.create-version-btn {
  width: 100%;
}

.test-panel {
  flex: 1;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.test-config {
  background: #f9fafb;
  padding: 0.75rem;
  border-radius: 0.5rem;
}

.config-title {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.test-controls {
  display: flex;
  gap: 0.5rem;
}

.test-logs {
  flex: 1;
  background: #1f2937;
  border-radius: 0.5rem;
  padding: 0.75rem;
  overflow-y: auto;
  min-height: 200px;
}

.log-content {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
}

.log-item {
  margin-bottom: 0.25rem;
  color: #10b981;
}

.log-item.error {
  color: #ef4444;
}

.log-item.warning {
  color: #f59e0b;
}

.test-stats {
  background: #eff6ff;
  padding: 0.75rem;
  border-radius: 0.5rem;
}

.stats-title {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #1e40af;
}

.stats-grid {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
}

.stat-label {
  color: #1e40af;
}

.stat-value {
  font-weight: 500;
}

.stat-value.success {
  color: #10b981;
}

.no-selection {
  text-align: center;
  padding: 2rem 0;
}
</style>
