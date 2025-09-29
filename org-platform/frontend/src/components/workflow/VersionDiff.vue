<template>
  <div class="version-diff">
    <div class="diff-header">
      <div class="version-info">
        <div class="source-version">
          <h4>源版本: {{ sourceVersion?.version_name }}</h4>
          <p>{{ sourceVersion?.description }}</p>
        </div>
        <div class="diff-arrow">
          <el-icon><Right /></el-icon>
        </div>
        <div class="target-version">
          <h4>目标版本: {{ targetVersion?.version_name }}</h4>
          <p>{{ targetVersion?.description }}</p>
        </div>
      </div>
    </div>

    <div class="diff-content">
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 节点差异 -->
        <el-tab-pane label="节点变更" name="nodes">
          <div class="diff-section">
            <!-- 新增节点 -->
            <div v-if="differences?.nodes?.added?.length > 0" class="change-group added">
              <h5 class="change-title">
                <el-icon><Plus /></el-icon>
                新增节点 ({{ differences.nodes.added.length }})
              </h5>
              <div class="change-list">
                <div 
                  v-for="node in differences.nodes.added" 
                  :key="node.node_id"
                  class="change-item"
                >
                  <div class="node-preview">
                    <el-icon class="node-icon">
                      <component :is="getNodeIcon(node.node_type)" />
                    </el-icon>
                    <div class="node-info">
                      <div class="node-name">{{ node.name }}</div>
                      <div class="node-type">{{ getNodeTypeName(node.node_type) }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 删除节点 -->
            <div v-if="differences?.nodes?.removed?.length > 0" class="change-group removed">
              <h5 class="change-title">
                <el-icon><Minus /></el-icon>
                删除节点 ({{ differences.nodes.removed.length }})
              </h5>
              <div class="change-list">
                <div 
                  v-for="node in differences.nodes.removed" 
                  :key="node.node_id"
                  class="change-item"
                >
                  <div class="node-preview">
                    <el-icon class="node-icon">
                      <component :is="getNodeIcon(node.node_type)" />
                    </el-icon>
                    <div class="node-info">
                      <div class="node-name">{{ node.name }}</div>
                      <div class="node-type">{{ getNodeTypeName(node.node_type) }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 修改节点 -->
            <div v-if="differences?.nodes?.modified?.length > 0" class="change-group modified">
              <h5 class="change-title">
                <el-icon><Edit /></el-icon>
                修改节点 ({{ differences.nodes.modified.length }})
              </h5>
              <div class="change-list">
                <div 
                  v-for="change in differences.nodes.modified" 
                  :key="change.node_id"
                  class="change-item"
                >
                  <div class="node-comparison">
                    <div class="before-after">
                      <div class="before">
                        <div class="label">修改前</div>
                        <div class="node-preview">
                          <el-icon class="node-icon">
                            <component :is="getNodeIcon(change.source.node_type)" />
                          </el-icon>
                          <div class="node-info">
                            <div class="node-name">{{ change.source.name }}</div>
                            <div class="node-type">{{ getNodeTypeName(change.source.node_type) }}</div>
                          </div>
                        </div>
                      </div>
                      
                      <div class="arrow">
                        <el-icon><Right /></el-icon>
                      </div>
                      
                      <div class="after">
                        <div class="label">修改后</div>
                        <div class="node-preview">
                          <el-icon class="node-icon">
                            <component :is="getNodeIcon(change.target.node_type)" />
                          </el-icon>
                          <div class="node-info">
                            <div class="node-name">{{ change.target.name }}</div>
                            <div class="node-type">{{ getNodeTypeName(change.target.node_type) }}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- 详细变更 -->
                    <div class="change-details">
                      <el-collapse>
                        <el-collapse-item title="查看详细变更" name="details">
                          <div class="property-changes">
                            <div v-for="(value, key) in getPropertyChanges(change.source, change.target)" :key="key" class="property-change">
                              <div class="property-name">{{ key }}:</div>
                              <div class="property-values">
                                <span class="old-value">{{ value.old }}</span>
                                <el-icon><Right /></el-icon>
                                <span class="new-value">{{ value.new }}</span>
                              </div>
                            </div>
                          </div>
                        </el-collapse-item>
                      </el-collapse>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 连接差异 -->
        <el-tab-pane label="连接变更" name="connections">
          <div class="diff-section">
            <!-- 新增连接 -->
            <div v-if="differences?.connections?.added?.length > 0" class="change-group added">
              <h5 class="change-title">
                <el-icon><Plus /></el-icon>
                新增连接 ({{ differences.connections.added.length }})
              </h5>
              <div class="change-list">
                <div 
                  v-for="connection in differences.connections.added" 
                  :key="connection.connection_id"
                  class="change-item"
                >
                  <div class="connection-preview">
                    <div class="connection-info">
                      <span class="source-node">{{ getNodeName(connection.source_id) }}</span>
                      <el-icon class="connection-arrow"><Right /></el-icon>
                      <span class="target-node">{{ getNodeName(connection.target_id) }}</span>
                    </div>
                    <div v-if="connection.label" class="connection-label">
                      {{ connection.label }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 删除连接 -->
            <div v-if="differences?.connections?.removed?.length > 0" class="change-group removed">
              <h5 class="change-title">
                <el-icon><Minus /></el-icon>
                删除连接 ({{ differences.connections.removed.length }})
              </h5>
              <div class="change-list">
                <div 
                  v-for="connection in differences.connections.removed" 
                  :key="connection.connection_id"
                  class="change-item"
                >
                  <div class="connection-preview">
                    <div class="connection-info">
                      <span class="source-node">{{ getNodeName(connection.source_id) }}</span>
                      <el-icon class="connection-arrow"><Right /></el-icon>
                      <span class="target-node">{{ getNodeName(connection.target_id) }}</span>
                    </div>
                    <div v-if="connection.label" class="connection-label">
                      {{ connection.label }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 统计信息 -->
        <el-tab-pane label="变更统计" name="statistics">
          <div class="diff-statistics">
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-icon added">
                  <el-icon><Plus /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ getTotalAdded() }}</div>
                  <div class="stat-label">新增项目</div>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon removed">
                  <el-icon><Minus /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ getTotalRemoved() }}</div>
                  <div class="stat-label">删除项目</div>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon modified">
                  <el-icon><Edit /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ getTotalModified() }}</div>
                  <div class="stat-label">修改项目</div>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon total">
                  <el-icon><DataAnalysis /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ getTotalChanges() }}</div>
                  <div class="stat-label">总变更数</div>
                </div>
              </div>
            </div>
            
            <!-- 变更摘要 -->
            <div class="change-summary">
              <h5>变更摘要</h5>
              <div class="summary-content">
                <p v-if="getTotalChanges() === 0" class="no-changes">
                  两个版本之间没有差异
                </p>
                <div v-else class="summary-text">
                  <p>
                    此次更新包含 <strong>{{ getTotalChanges() }}</strong> 项变更，
                    其中新增 <strong>{{ getTotalAdded() }}</strong> 项，
                    删除 <strong>{{ getTotalRemoved() }}</strong> 项，
                    修改 <strong>{{ getTotalModified() }}</strong> 项。
                  </p>
                  
                  <div class="impact-analysis">
                    <h6>影响分析</h6>
                    <ul>
                      <li v-if="differences?.nodes?.added?.length > 0">
                        新增了 {{ differences.nodes.added.length }} 个节点，可能会影响工作流的执行路径
                      </li>
                      <li v-if="differences?.nodes?.removed?.length > 0">
                        删除了 {{ differences.nodes.removed.length }} 个节点，请确保相关业务逻辑已迁移
                      </li>
                      <li v-if="differences?.connections?.added?.length > 0">
                        新增了 {{ differences.connections.added.length }} 个连接，工作流路径发生变化
                      </li>
                      <li v-if="differences?.connections?.removed?.length > 0">
                        删除了 {{ differences.connections.removed.length }} 个连接，部分执行路径可能中断
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  Right, Plus, Minus, Edit, DataAnalysis,
  VideoPlay, Timer, Check, Bell, Database, 
  Branch, CircleCheck, CircleClose 
} from '@element-plus/icons-vue'

interface WorkflowNode {
  node_id: string
  node_type: string
  name: string
  x: number
  y: number
  config: Record<string, any>
}

interface WorkflowConnection {
  connection_id: string
  source_id: string
  target_id: string
  source_port?: string
  target_port?: string
  connection_type?: string
  label?: string
}

interface WorkflowVersion {
  id: string
  version_name: string
  description: string
  nodes_snapshot: WorkflowNode[]
  connections_snapshot: WorkflowConnection[]
}

interface VersionDifferences {
  nodes: {
    added: WorkflowNode[]
    removed: WorkflowNode[]
    modified: Array<{
      node_id: string
      source: WorkflowNode
      target: WorkflowNode
    }>
  }
  connections: {
    added: WorkflowConnection[]
    removed: WorkflowConnection[]
    modified: Array<{
      connection_id: string
      source: WorkflowConnection
      target: WorkflowConnection
    }>
  }
}

interface Props {
  sourceVersion: WorkflowVersion
  targetVersion: WorkflowVersion
  differences?: VersionDifferences
}

const props = defineProps<Props>()

const activeTab = ref('nodes')

// 节点类型映射
const nodeTypeMap = {
  start: '开始',
  timer: '定时器',
  approval: '审批',
  notification: '通知',
  data: '数据处理',
  condition: '条件判断',
  end: '结束',
  error: '错误处理'
}

// 节点图标映射
const nodeIconMap = {
  start: VideoPlay,
  timer: Timer,
  approval: Check,
  notification: Bell,
  data: Database,
  condition: Branch,
  end: CircleCheck,
  error: CircleClose
}

// 计算属性
const allNodes = computed(() => {
  const nodes = new Map()
  
  // 添加源版本节点
  props.sourceVersion?.nodes_snapshot?.forEach(node => {
    nodes.set(node.node_id, node)
  })
  
  // 添加目标版本节点
  props.targetVersion?.nodes_snapshot?.forEach(node => {
    nodes.set(node.node_id, node)
  })
  
  return nodes
})

// 方法
const getNodeIcon = (nodeType: string) => {
  return nodeIconMap[nodeType] || VideoPlay
}

const getNodeTypeName = (nodeType: string) => {
  return nodeTypeMap[nodeType] || nodeType
}

const getNodeName = (nodeId: string) => {
  const node = allNodes.value.get(nodeId)
  return node?.name || nodeId
}

const getPropertyChanges = (sourceNode: WorkflowNode, targetNode: WorkflowNode) => {
  const changes: Record<string, { old: any, new: any }> = {}
  
  // 比较基本属性
  const compareFields = ['name', 'x', 'y', 'node_type']
  
  compareFields.forEach(field => {
    if (sourceNode[field] !== targetNode[field]) {
      changes[field] = {
        old: sourceNode[field],
        new: targetNode[field]
      }
    }
  })
  
  // 比较配置
  const sourceConfig = JSON.stringify(sourceNode.config || {})
  const targetConfig = JSON.stringify(targetNode.config || {})
  
  if (sourceConfig !== targetConfig) {
    changes['config'] = {
      old: sourceConfig,
      new: targetConfig
    }
  }
  
  return changes
}

const getTotalAdded = () => {
  return (props.differences?.nodes?.added?.length || 0) + 
         (props.differences?.connections?.added?.length || 0)
}

const getTotalRemoved = () => {
  return (props.differences?.nodes?.removed?.length || 0) + 
         (props.differences?.connections?.removed?.length || 0)
}

const getTotalModified = () => {
  return (props.differences?.nodes?.modified?.length || 0) + 
         (props.differences?.connections?.modified?.length || 0)
}

const getTotalChanges = () => {
  return getTotalAdded() + getTotalRemoved() + getTotalModified()
}
</script>

<style scoped>
.version-diff {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.diff-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.source-version,
.target-version {
  flex: 1;
}

.source-version h4,
.target-version h4 {
  margin: 0 0 0.5rem 0;
  font-weight: 600;
  color: #374151;
}

.source-version p,
.target-version p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.diff-arrow {
  color: #6b7280;
  font-size: 1.5rem;
}

.diff-content {
  flex: 1;
  overflow: hidden;
}

.diff-section {
  padding: 1rem;
  height: 100%;
  overflow-y: auto;
}

.change-group {
  margin-bottom: 2rem;
}

.change-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.change-group.added .change-title {
  color: #10b981;
}

.change-group.removed .change-title {
  color: #ef4444;
}

.change-group.modified .change-title {
  color: #f59e0b;
}

.change-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.change-item {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
}

.change-group.added .change-item {
  border-left: 4px solid #10b981;
  background: #f0fdf4;
}

.change-group.removed .change-item {
  border-left: 4px solid #ef4444;
  background: #fef2f2;
}

.change-group.modified .change-item {
  border-left: 4px solid #f59e0b;
  background: #fffbeb;
}

.node-preview {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.node-icon {
  font-size: 1.5rem;
  color: #6b7280;
}

.node-info {
  flex: 1;
}

.node-name {
  font-weight: 500;
  color: #374151;
}

.node-type {
  font-size: 0.75rem;
  color: #6b7280;
}

.node-comparison {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.before-after {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.before,
.after {
  flex: 1;
}

.label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.arrow {
  color: #6b7280;
}

.change-details {
  margin-top: 1rem;
}

.property-changes {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.property-change {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.property-name {
  font-weight: 500;
  color: #374151;
  min-width: 80px;
}

.property-values {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.old-value {
  color: #ef4444;
  text-decoration: line-through;
}

.new-value {
  color: #10b981;
  font-weight: 500;
}

.connection-preview {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.connection-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.source-node,
.target-node {
  font-weight: 500;
  color: #374151;
}

.connection-arrow {
  color: #6b7280;
}

.connection-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-style: italic;
}

.diff-statistics {
  padding: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.stat-icon.added {
  background: #10b981;
}

.stat-icon.removed {
  background: #ef4444;
}

.stat-icon.modified {
  background: #f59e0b;
}

.stat-icon.total {
  background: #6366f1;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #374151;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.change-summary {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
}

.change-summary h5 {
  margin: 0 0 1rem 0;
  font-weight: 600;
  color: #374151;
}

.no-changes {
  color: #6b7280;
  font-style: italic;
  text-align: center;
  padding: 2rem;
}

.summary-text {
  line-height: 1.6;
}

.impact-analysis {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.impact-analysis h6 {
  margin: 0 0 0.5rem 0;
  font-weight: 600;
  color: #374151;
}

.impact-analysis ul {
  margin: 0;
  padding-left: 1.5rem;
}

.impact-analysis li {
  margin-bottom: 0.25rem;
  color: #6b7280;
}
</style>
