<template>
  <div class="evaluation-graph-panel">
    <!-- 面板头部 -->
    <div class="panel-header">
      <h3 class="panel-title">
        <i class="fas fa-project-diagram"></i>
        考核关系图
      </h3>
      <div class="panel-controls">
        <el-button size="small" @click="toggleLayout">
          <i class="fas fa-sitemap"></i>
          {{ layoutType === 'hierarchical' ? '切换为网络图' : '切换为层级图' }}
        </el-button>
        <el-button size="small" @click="resetView">
          <i class="fas fa-expand-arrows-alt"></i>
          重置视图
        </el-button>
        <el-button size="small" @click="exportGraph">
          <i class="fas fa-download"></i>
          导出图片
        </el-button>
      </div>
    </div>

    <!-- 图形化面板容器 -->
    <div class="graph-container" ref="graphContainer">
      <svg 
        class="graph-svg" 
        :width="svgWidth" 
        :height="svgHeight"
        @mousedown="handleMouseDown"
        @mousemove="handleMouseMove"
        @mouseup="handleMouseUp"
        @wheel="handleWheel"
      >
        <!-- 连接线 -->
        <g class="connections">
          <path
            v-for="connection in connections"
            :key="connection.id"
            :d="connection.path"
            :class="['connection-line', connection.status]"
            :stroke-dasharray="connection.dashed ? '5,5' : 'none'"
            @click="selectConnection(connection)"
          />
        </g>

        <!-- 节点组 -->
        <g class="nodes">
          <!-- 考核人节点 -->
          <g
            v-for="evaluator in evaluators"
            :key="`evaluator-${evaluator.id}`"
            :transform="`translate(${evaluator.x}, ${evaluator.y})`"
            class="node-group"
          >
            <!-- 考核人节点 -->
            <circle
              :r="nodeRadius"
              :class="['node-circle', 'evaluator-node', evaluator.status]"
              :fill="getNodeColor(evaluator.status)"
              :stroke="getNodeBorderColor(evaluator.status)"
              :stroke-width="evaluator.selected ? 3 : 2"
              @mousedown="startDrag($event, evaluator, 'evaluator')"
            />
            
            <!-- 考核人姓名 -->
            <text
              :y="nodeRadius + 20"
              class="node-name evaluator-name"
              text-anchor="middle"
            >
              {{ evaluator.name }}
            </text>
            
            <!-- 考核人职位 -->
            <text
              :y="nodeRadius + 35"
              class="node-position evaluator-position"
              text-anchor="middle"
            >
              {{ evaluator.position }}
            </text>

          </g>

          <!-- 被考核人节点 -->
          <g
            v-for="evaluatee in evaluatees"
            :key="`evaluatee-${evaluatee.id}`"
            :transform="`translate(${evaluatee.x}, ${evaluatee.y})`"
            class="node-group"
          >
            <!-- 被考核人节点 -->
            <circle
              :r="nodeRadius"
              :class="['node-circle', 'evaluatee-node', evaluatee.status]"
              :fill="getNodeColor(evaluatee.status)"
              :stroke="getNodeBorderColor(evaluatee.status)"
              :stroke-width="evaluatee.selected ? 3 : 2"
              @mousedown="startDrag($event, evaluatee, 'evaluatee')"
            />
            
            <!-- 被考核人姓名 -->
            <text
              :y="nodeRadius + 20"
              class="node-name evaluatee-name"
              text-anchor="middle"
            >
              {{ evaluatee.name }}
            </text>
            
            <!-- 被考核人职位 -->
            <text
              :y="nodeRadius + 35"
              class="node-position evaluatee-position"
              text-anchor="middle"
            >
              {{ evaluatee.position }}
            </text>
          </g>
        </g>

        <!-- 状态图例 - 移回左上角 -->
        <g class="legend" :transform="`translate(20, 20)`">
          <rect width="200" height="120" fill="rgba(255,255,255,0.9)" stroke="#e2e8f0" rx="8"/>
          <text x="10" y="20" class="legend-title">状态图例</text>
          <g v-for="(status, index) in statusLegend" :key="status.key" :transform="`translate(10, ${35 + index * 20})`">
            <circle :r="8" :fill="status.color" :stroke="status.borderColor" stroke-width="2"/>
            <text x="20" y="5" class="legend-text">{{ status.label }}</text>
          </g>
        </g>
      </svg>
    </div>

    <!-- 详细信息面板 -->
    <div v-if="selectedNode" class="detail-panel">
      <div class="detail-header">
        <h4>{{ selectedNode.name }}</h4>
        <el-button size="small" @click="selectedNode = null">
          <i class="fas fa-times"></i>
        </el-button>
      </div>
      <div class="detail-content">
        <p><strong>职位：</strong>{{ selectedNode.position }}</p>
        <p><strong>部门：</strong>{{ selectedNode.department }}</p>
        <p><strong>状态：</strong>
          <el-tag :type="getStatusType(selectedNode.status)">
            {{ getStatusText(selectedNode.status) }}
          </el-tag>
        </p>
        <div v-if="selectedNode.evaluationCodes" class="evaluation-codes">
          <h5>考核码：</h5>
          <div v-for="code in selectedNode.evaluationCodes" :key="code.id" class="code-item">
            <span class="code-value">{{ code.code }}</span>
            <el-tag size="small" :type="getStatusType(code.status)">
              {{ getStatusText(code.status) }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'

// Props定义
interface Props {
  evaluators?: any[]
  evaluatees?: any[]
  connections?: any[]
}

const props = withDefaults(defineProps<Props>(), {
  evaluators: () => [],
  evaluatees: () => [],
  connections: () => []
})

// Emits定义
const emit = defineEmits<{
  nodeClick: [node: any]
  connectionClick: [connection: any]
}>()

// 响应式数据
const graphContainer = ref<HTMLElement>()
const svgWidth = ref(3000) // 进一步大幅增加宽度以确保右侧节点完全显示
const svgHeight = ref(2200) // 进一步大幅增加高度以支持更多人员
const nodeRadius = ref(25)
const layoutType = ref<'hierarchical' | 'network'>('hierarchical')
const selectedNode = ref(null)
const isDragging = ref(false)
const dragNode = ref(null)
const dragOffset = ref({ x: 0, y: 0 })

// 使用props数据
const evaluators = computed(() => props.evaluators)
const evaluatees = computed(() => props.evaluatees)

// 强制更新触发器
const forceUpdate = ref(0)

// 连接线数据
const connections = computed(() => {
  // 使用forceUpdate来触发重新计算
  forceUpdate.value
  
  console.log('连接线数据:', props.connections)
  console.log('考核人数据:', evaluators.value)
  console.log('被考核人数据:', evaluatees.value)
  
  return props.connections.map(conn => {
    // 获取最新的节点位置
    const fromNode = [...evaluators.value, ...evaluatees.value].find(n => n.id === conn.from.id)
    const toNode = [...evaluators.value, ...evaluatees.value].find(n => n.id === conn.to.id)
    
    console.log('连接线节点查找:', { conn, fromNode, toNode })
    
    if (!fromNode || !toNode) {
      console.warn('找不到连接线节点:', conn)
      return conn
    }
    
    const path = `M ${fromNode.x} ${fromNode.y} Q ${(fromNode.x + toNode.x) / 2} ${Math.min(fromNode.y, toNode.y) - 50} ${toNode.x} ${toNode.y}`
    console.log('连接线路径:', path)
    
    return {
      ...conn,
      path
    }
  })
})

// 状态图例
const statusLegend = ref([
  { key: 'pending', label: '待考核', color: '#fbbf24', borderColor: '#f59e0b' },
  { key: 'in_progress', label: '进行中', color: '#60a5fa', borderColor: '#3b82f6' },
  { key: 'completed', label: '已完成', color: '#34d399', borderColor: '#10b981' },
  { key: 'overdue', label: '已过期', color: '#f87171', borderColor: '#ef4444' }
])

// 方法
const getNodeColor = (status: string) => {
  const colorMap: Record<string, string> = {
    'pending': '#fbbf24',
    'in_progress': '#60a5fa',
    'completed': '#34d399',
    'overdue': '#f87171',
    'active': '#8b5cf6'
  }
  return colorMap[status] || '#9ca3af'
}

const getNodeBorderColor = (status: string) => {
  const colorMap: Record<string, string> = {
    'pending': '#f59e0b',
    'in_progress': '#3b82f6',
    'completed': '#10b981',
    'overdue': '#ef4444',
    'active': '#7c3aed'
  }
  return colorMap[status] || '#6b7280'
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    'pending': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'overdue': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    'pending': '待考核',
    'in_progress': '进行中',
    'completed': '已完成',
    'overdue': '已过期',
    'active': '活跃'
  }
  return textMap[status] || '未知'
}

const toggleLayout = () => {
  layoutType.value = layoutType.value === 'hierarchical' ? 'network' : 'hierarchical'
  ElMessage.success(`已切换到${layoutType.value === 'hierarchical' ? '层级' : '网络'}布局`)
}

const resetView = () => {
  // 重置视图逻辑
  console.log('重置视图...')
  
  // 重新计算所有节点位置，确保都在可视区域内
  const allNodes = [...evaluators.value, ...evaluatees.value]
  if (allNodes.length > 0) {
    // 计算节点边界
    const minX = Math.min(...allNodes.map(n => n.x))
    const maxX = Math.max(...allNodes.map(n => n.x))
    const minY = Math.min(...allNodes.map(n => n.y))
    const maxY = Math.max(...allNodes.map(n => n.y))
    
    // 计算缩放比例，确保所有节点都在可视区域内
    const scaleX = Math.min(1, (svgWidth.value - 100) / (maxX - minX + 50))
    const scaleY = Math.min(1, (svgHeight.value - 100) / (maxY - minY + 50))
    const scale = Math.min(scaleX, scaleY, 1)
    
    console.log('缩放比例:', scale)
    
    if (scale < 1) {
      // 应用缩放
      allNodes.forEach(node => {
        node.x = (node.x - minX) * scale + 50
        node.y = (node.y - minY) * scale + 50
      })
      
      // 强制更新连接线
      forceUpdate.value++
    }
  }
  
  ElMessage.success('视图已重置')
}

const exportGraph = () => {
  // 导出图片逻辑
  ElMessage.success('图片导出功能开发中')
}

const startDrag = (event: MouseEvent, node: any, type: string) => {
  event.preventDefault()
  event.stopPropagation()
  
  console.log('开始拖拽:', node.name, type)
  
  isDragging.value = true
  dragNode.value = { ...node, type }
  
  const rect = graphContainer.value?.getBoundingClientRect()
  if (rect) {
    dragOffset.value = {
      x: event.clientX - rect.left - node.x,
      y: event.clientY - rect.top - node.y
    }
  }
}

const handleMouseMove = (event: MouseEvent) => {
  if (!isDragging.value || !dragNode.value) return
  
  const rect = graphContainer.value?.getBoundingClientRect()
  if (!rect) return
  
  const newX = event.clientX - rect.left - dragOffset.value.x
  const newY = event.clientY - rect.top - dragOffset.value.y
  
  // 限制在SVG边界内
  const constrainedX = Math.max(nodeRadius.value, Math.min(svgWidth.value - nodeRadius.value, newX))
  const constrainedY = Math.max(nodeRadius.value, Math.min(svgHeight.value - nodeRadius.value, newY))
  
  // 直接修改节点位置
  if (dragNode.value.type === 'evaluator') {
    const evaluator = evaluators.value.find(e => e.id === dragNode.value.id)
    if (evaluator) {
      evaluator.x = constrainedX
      evaluator.y = constrainedY
    }
  } else {
    const evaluatee = evaluatees.value.find(e => e.id === dragNode.value.id)
    if (evaluatee) {
      evaluatee.x = constrainedX
      evaluatee.y = constrainedY
    }
  }
  
  // 强制触发连接线更新
  forceUpdate.value++
}

const handleMouseUp = () => {
  isDragging.value = false
  dragNode.value = null
}

const handleMouseDown = (event: MouseEvent) => {
  // 处理背景点击
  if (event.target === event.currentTarget) {
    selectedNode.value = null
  }
}

const handleWheel = (event: WheelEvent) => {
  // 处理缩放
  if (event.cancelable) {
    event.preventDefault()
  }
}

const selectConnection = (connection: any) => {
  emit('connectionClick', connection)
  ElMessage.info(`选中连接: ${connection.id}`)
}



// 生命周期
onMounted(() => {
  nextTick(() => {
    if (graphContainer.value) {
      const rect = graphContainer.value.getBoundingClientRect()
      // 设置最小尺寸，确保有足够空间显示所有节点
      svgWidth.value = Math.max(rect.width, 1200)
      svgHeight.value = Math.max(rect.height, 1000)
    }
  })
})
</script>

<style scoped>
.evaluation-graph-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-bottom: 1px solid #e2e8f0;
}

.panel-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-controls {
  display: flex;
  gap: 8px;
}

.graph-container {
  flex: 1;
  position: relative;
  overflow: auto;
  background: #f8fafc;
  min-height: 600px;
}

.graph-svg {
  width: 100%;
  height: 100%;
  cursor: grab;
}

.graph-svg:active {
  cursor: grabbing;
}

/* 连接线样式 */
.connection-line {
  fill: none;
  stroke-width: 3;
  stroke-linecap: round;
  cursor: pointer;
  transition: all 0.3s ease;
}

.connection-line.pending {
  stroke: #f59e0b;
}

.connection-line.in_progress {
  stroke: #3b82f6;
}

.connection-line.completed {
  stroke: #10b981;
}

.connection-line.overdue {
  stroke: #ef4444;
}

.connection-line:hover {
  stroke-width: 4;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

/* 节点样式 */
.node-group {
  cursor: pointer;
  transform-origin: center;
}

.node-circle {
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.15));
  transition: filter 0.15s ease;
  transform-origin: center;
  cursor: grab;
}

.node-circle:active {
  cursor: grabbing;
}

.node-group:hover .node-circle {
  filter: drop-shadow(0 3px 10px rgba(0, 0, 0, 0.2));
}

/* 确保文本不会跳出节点 */
.node-name, .node-position {
  pointer-events: none;
  user-select: none;
  transform-origin: center;
}

.node-name {
  font-size: 14px;
  font-weight: 600;
  fill: #1e293b;
  text-anchor: middle;
  dominant-baseline: central;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
  transform-origin: center;
}

.node-position {
  font-size: 12px;
  fill: #64748b;
  text-anchor: middle;
  dominant-baseline: central;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
  transform-origin: center;
}

.evaluator-name {
  fill: #7c3aed;
}

.evaluatee-name {
  fill: #2563eb;
}


/* 图例样式 */
.legend-title {
  font-size: 14px;
  font-weight: 600;
  fill: #1e293b;
}

.legend-text {
  font-size: 12px;
  fill: #64748b;
}

/* 详细信息面板 */
.detail-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 300px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border: 1px solid #e2e8f0;
  z-index: 10;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 12px 12px 0 0;
}

.detail-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.detail-content {
  padding: 20px;
}

.detail-content p {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #64748b;
}

.detail-content strong {
  color: #1e293b;
}

.evaluation-codes {
  margin-top: 16px;
}

.evaluation-codes h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.code-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
  margin-bottom: 8px;
}

.code-value {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .panel-controls {
    justify-content: center;
  }
  
  .detail-panel {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 400px;
  }
  
  .node-name {
    font-size: 12px;
  }
  
  .node-position {
    font-size: 10px;
  }
  
  .code-text {
    font-size: 9px;
  }
}
</style>
