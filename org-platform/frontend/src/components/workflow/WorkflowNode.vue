<template>
  <div 
    class="workflow-node"
    :class="[
      `node-${node.type}`,
      { 
        'node-selected': selected,
        'node-executing': executing,
        'node-error': hasError
      }
    ]"
    :style="{ 
      left: node.x + 'px', 
      top: node.y + 'px',
      zIndex: selected ? 1000 : 1
    }"
    @mousedown="onMouseDown"
    @click.stop="onSelect"
    @contextmenu.prevent="onContextMenu"
  >
    <!-- 节点主体 -->
    <div class="node-body">
      <!-- 节点图标 -->
      <div class="node-icon">
        <el-icon>
          <component :is="getNodeIcon(node.type)" />
        </el-icon>
      </div>
      
      <!-- 节点标题 -->
      <div class="node-title">{{ node.name }}</div>
      
      <!-- 执行状态指示器 -->
      <div v-if="executing" class="execution-indicator">
        <el-icon class="spinning"><Loading /></el-icon>
      </div>
      
      <!-- 错误指示器 -->
      <div v-if="hasError" class="error-indicator">
        <el-icon><Warning /></el-icon>
      </div>
    </div>
    
    <!-- 连接点 -->
    <div 
      v-if="hasInputPort" 
      class="connection-port input-port"
      @mousedown.stop="onPortMouseDown('input')"
    >
      <div class="port-dot"></div>
    </div>
    
    <div 
      v-if="hasOutputPort" 
      class="connection-port output-port"
      @mousedown.stop="onPortMouseDown('output')"
    >
      <div class="port-dot"></div>
    </div>
    
    <!-- 多输出端口（条件节点） -->
    <div 
      v-if="node.type === 'condition'" 
      class="connection-port output-port success-port"
      style="top: 25%; right: -8px;"
      @mousedown.stop="onPortMouseDown('success')"
    >
      <div class="port-dot success"></div>
      <div class="port-label">是</div>
    </div>
    
    <div 
      v-if="node.type === 'condition'" 
      class="connection-port output-port failure-port"
      style="top: 75%; right: -8px;"
      @mousedown.stop="onPortMouseDown('failure')"
    >
      <div class="port-dot failure"></div>
      <div class="port-label">否</div>
    </div>
    
    <!-- 选中时的操作按钮 -->
    <div v-if="selected" class="node-actions">
      <el-button 
        size="small" 
        circle 
        type="primary" 
        :icon="Edit" 
        @click.stop="onEdit"
      />
      <el-button 
        size="small" 
        circle 
        type="danger" 
        :icon="Delete" 
        @click.stop="onDelete"
      />
    </div>
    
    <!-- 右键菜单 -->
    <el-dropdown 
      ref="contextMenu"
      trigger="contextmenu"
      @command="onContextCommand"
    >
      <span></span>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="edit" :icon="Edit">编辑</el-dropdown-item>
          <el-dropdown-item command="copy" :icon="CopyDocument">复制</el-dropdown-item>
          <el-dropdown-item command="delete" :icon="Delete" divided>删除</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { 
  Edit, Delete, CopyDocument, Loading, Warning,
  VideoPlay, Timer, Check, Bell, 
  CircleCheck, CircleClose 
} from '@element-plus/icons-vue'

interface WorkflowNode {
  id: string
  type: string
  name: string
  x: number
  y: number
  config: Record<string, any>
}

interface Props {
  node: WorkflowNode
  selected?: boolean
  executing?: boolean
  hasError?: boolean
}

interface Emits {
  (e: 'select', node: WorkflowNode): void
  (e: 'update', nodeId: string, updates: Partial<WorkflowNode>): void
  (e: 'delete', nodeId: string): void
  (e: 'connect', sourceId: string, targetId: string, sourcePort?: string, targetPort?: string): void
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  executing: false,
  hasError: false
})

const emit = defineEmits<Emits>()

const contextMenu = ref()
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

// 计算属性
const hasInputPort = computed(() => {
  return !['start', 'timer'].includes(props.node.type)
})

const hasOutputPort = computed(() => {
  return !['end', 'error'].includes(props.node.type)
})

// 方法
const getNodeIcon = (type: string) => {
  const iconMap = {
    start: VideoPlay,
    timer: Timer,
    approval: Check,
    notification: Bell,
    data: Check,  // 使用Check图标替代Database
    condition: Check,  // 使用Check图标替代Branch
    end: CircleCheck,
    error: CircleClose
  }
  return iconMap[type] || VideoPlay
}

const onMouseDown = (event: MouseEvent) => {
  if (event.button !== 0) return // 只处理左键
  
  isDragging.value = true
  dragStart.value = {
    x: event.clientX - props.node.x,
    y: event.clientY - props.node.y
  }
  
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  
  event.preventDefault()
}

const onMouseMove = (event: MouseEvent) => {
  if (!isDragging.value) return
  
  const newX = event.clientX - dragStart.value.x
  const newY = event.clientY - dragStart.value.y
  
  emit('update', props.node.id, { x: newX, y: newY })
}

const onMouseUp = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
}

const onSelect = () => {
  emit('select', props.node)
}

const onEdit = () => {
  // 触发编辑事件
  console.log('编辑节点:', props.node.id)
}

const onDelete = () => {
  emit('delete', props.node.id)
}

const onContextMenu = (event: MouseEvent) => {
  // 显示右键菜单
  contextMenu.value?.handleOpen()
}

const onContextCommand = (command: string) => {
  switch (command) {
    case 'edit':
      onEdit()
      break
    case 'copy':
      // 复制节点逻辑
      console.log('复制节点:', props.node.id)
      break
    case 'delete':
      onDelete()
      break
  }
}

const onPortMouseDown = (portType: string) => {
  // 开始连线操作
  console.log('开始连线:', props.node.id, portType)
}
</script>

<style scoped>
.workflow-node {
  position: absolute;
  cursor: move;
  user-select: none;
  transition: all 0.2s ease;
}

.workflow-node:hover {
  transform: scale(1.02);
}

.workflow-node.node-selected {
  transform: scale(1.05);
}

.workflow-node.node-executing .node-body {
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
  animation: pulse 2s infinite;
}

.workflow-node.node-error .node-body {
  border-color: #ef4444;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
}

.node-body {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  min-width: 120px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
}

.node-icon {
  font-size: 2rem;
  margin-bottom: 8px;
  color: #6b7280;
}

.node-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  line-height: 1.2;
}

.execution-indicator {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  background: #3b82f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
}

.error-indicator {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  background: #ef4444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.connection-port {
  position: absolute;
  width: 16px;
  height: 16px;
  cursor: crosshair;
}

.input-port {
  left: -8px;
  top: 50%;
  transform: translateY(-50%);
}

.output-port {
  right: -8px;
  top: 50%;
  transform: translateY(-50%);
}

.port-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #3b82f6;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.port-dot:hover {
  transform: scale(1.2);
}

.port-dot.success {
  background: #10b981;
}

.port-dot.failure {
  background: #ef4444;
}

.port-label {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.75rem;
  color: #6b7280;
  white-space: nowrap;
}

.node-actions {
  position: absolute;
  top: -40px;
  right: 0;
  display: flex;
  gap: 4px;
  opacity: 0;
  animation: fadeIn 0.2s ease forwards;
}

@keyframes fadeIn {
  to { opacity: 1; }
}

/* 节点类型样式 */
.node-start .node-body {
  border-color: #10b981;
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
}

.node-start .node-icon {
  color: #10b981;
}

.node-timer .node-body {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
}

.node-timer .node-icon {
  color: #3b82f6;
}

.node-approval .node-body {
  border-color: #8b5cf6;
  background: linear-gradient(135deg, #f3e8ff, #e9d5ff);
}

.node-approval .node-icon {
  color: #8b5cf6;
}

.node-notification .node-body {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
}

.node-notification .node-icon {
  color: #f59e0b;
}

.node-data .node-body {
  border-color: #6366f1;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
}

.node-data .node-icon {
  color: #6366f1;
}

.node-condition .node-body {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2, #fecaca);
}

.node-condition .node-icon {
  color: #ef4444;
}

.node-end .node-body {
  border-color: #6b7280;
  background: linear-gradient(135deg, #f9fafb, #f3f4f6);
}

.node-end .node-icon {
  color: #6b7280;
}

.node-error .node-body {
  border-color: #f97316;
  background: linear-gradient(135deg, #fff7ed, #fed7aa);
}

.node-error .node-icon {
  color: #f97316;
}
</style>
