<template>
  <svg class="workflow-connection" :style="svgStyle">
    <!-- 连接路径 -->
    <path
      :d="pathData"
      :class="[
        'connection-path',
        `connection-${connection.type || 'default'}`,
        { 'connection-active': isActive }
      ]"
      @click="onSelect"
      @contextmenu.prevent="onContextMenu"
    />
    
    <!-- 箭头 -->
    <defs>
      <marker
        :id="`arrowhead-${connection.id}`"
        markerWidth="10"
        markerHeight="7"
        refX="9"
        refY="3.5"
        orient="auto"
      >
        <polygon
          points="0 0, 10 3.5, 0 7"
          :class="`arrow-${connection.type || 'default'}`"
        />
      </marker>
    </defs>
    
    <!-- 连接标签 -->
    <g v-if="connection.label" class="connection-label">
      <rect
        :x="labelPosition.x - labelWidth / 2"
        :y="labelPosition.y - 10"
        :width="labelWidth"
        height="20"
        rx="10"
        class="label-background"
      />
      <text
        :x="labelPosition.x"
        :y="labelPosition.y + 4"
        text-anchor="middle"
        class="label-text"
      >
        {{ connection.label }}
      </text>
    </g>
    
    <!-- 删除按钮 -->
    <g v-if="isSelected" class="delete-button">
      <circle
        :cx="labelPosition.x + labelWidth / 2 + 15"
        :cy="labelPosition.y"
        r="8"
        class="delete-bg"
        @click.stop="onDelete"
      />
      <text
        :x="labelPosition.x + labelWidth / 2 + 15"
        :y="labelPosition.y + 3"
        text-anchor="middle"
        class="delete-icon"
        @click.stop="onDelete"
      >
        ×
      </text>
    </g>
  </svg>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface WorkflowConnection {
  id: string
  sourceId: string
  targetId: string
  sourcePort?: string
  targetPort?: string
  type?: 'success' | 'failure' | 'default'
  label?: string
}

interface WorkflowNode {
  id: string
  x: number
  y: number
  type: string
}

interface Props {
  connection: WorkflowConnection
  nodes: WorkflowNode[]
  selected?: boolean
}

interface Emits {
  (e: 'select', connection: WorkflowConnection): void
  (e: 'delete', connectionId: string): void
}

const props = withDefaults(defineProps<Props>(), {
  selected: false
})

const emit = defineEmits<Emits>()

const isSelected = ref(false)
const isActive = ref(false)

// 计算属性
const sourceNode = computed(() => {
  return props.nodes.find(node => node.id === props.connection.sourceId)
})

const targetNode = computed(() => {
  return props.nodes.find(node => node.id === props.connection.targetId)
})

const sourcePoint = computed(() => {
  if (!sourceNode.value) return { x: 0, y: 0 }
  
  const node = sourceNode.value
  let x = node.x + 120 // 节点宽度的右边缘
  let y = node.y + 40  // 节点高度的中心
  
  // 根据端口类型调整位置
  if (props.connection.sourcePort === 'success') {
    y = node.y + 20 // 上方端口
  } else if (props.connection.sourcePort === 'failure') {
    y = node.y + 60 // 下方端口
  }
  
  return { x, y }
})

const targetPoint = computed(() => {
  if (!targetNode.value) return { x: 0, y: 0 }
  
  const node = targetNode.value
  const x = node.x // 节点左边缘
  const y = node.y + 40 // 节点高度的中心
  
  return { x, y }
})

const pathData = computed(() => {
  const start = sourcePoint.value
  const end = targetPoint.value
  
  if (!start || !end) return ''
  
  const dx = end.x - start.x
  const dy = end.y - start.y
  
  // 计算控制点，创建平滑的贝塞尔曲线
  const controlPoint1X = start.x + Math.max(50, Math.abs(dx) * 0.5)
  const controlPoint1Y = start.y
  const controlPoint2X = end.x - Math.max(50, Math.abs(dx) * 0.5)
  const controlPoint2Y = end.y
  
  return `M ${start.x} ${start.y} C ${controlPoint1X} ${controlPoint1Y}, ${controlPoint2X} ${controlPoint2Y}, ${end.x} ${end.y}`
})

const svgStyle = computed(() => {
  const start = sourcePoint.value
  const end = targetPoint.value
  
  if (!start || !end) return {}
  
  const minX = Math.min(start.x, end.x) - 20
  const minY = Math.min(start.y, end.y) - 20
  const maxX = Math.max(start.x, end.x) + 20
  const maxY = Math.max(start.y, end.y) + 20
  
  return {
    position: 'absolute',
    left: minX + 'px',
    top: minY + 'px',
    width: (maxX - minX) + 'px',
    height: (maxY - minY) + 'px',
    pointerEvents: 'none'
  }
})

const labelPosition = computed(() => {
  const start = sourcePoint.value
  const end = targetPoint.value
  
  if (!start || !end) return { x: 0, y: 0 }
  
  return {
    x: (start.x + end.x) / 2,
    y: (start.y + end.y) / 2
  }
})

const labelWidth = computed(() => {
  if (!props.connection.label) return 0
  return props.connection.label.length * 8 + 16 // 估算文字宽度
})

// 方法
const onSelect = () => {
  isSelected.value = !isSelected.value
  emit('select', props.connection)
}

const onDelete = () => {
  emit('delete', props.connection.id)
}

const onContextMenu = () => {
  // 显示右键菜单
  console.log('连接线右键菜单')
}

// 动画效果
const animateConnection = () => {
  isActive.value = true
  setTimeout(() => {
    isActive.value = false
  }, 1000)
}

// 暴露方法给父组件
defineExpose({
  animateConnection
})
</script>

<style scoped>
.workflow-connection {
  pointer-events: none;
  z-index: 1;
}

.connection-path {
  fill: none;
  stroke-width: 2;
  cursor: pointer;
  pointer-events: stroke;
  transition: all 0.2s ease;
}

.connection-default {
  stroke: #3b82f6;
  marker-end: url(#arrowhead-default);
}

.connection-success {
  stroke: #10b981;
  marker-end: url(#arrowhead-success);
}

.connection-failure {
  stroke: #ef4444;
  marker-end: url(#arrowhead-failure);
}

.connection-path:hover {
  stroke-width: 3;
  filter: drop-shadow(0 0 6px currentColor);
}

.connection-active {
  stroke-dasharray: 10 5;
  animation: dash 1s linear infinite;
}

@keyframes dash {
  to {
    stroke-dashoffset: -15;
  }
}

.arrow-default {
  fill: #3b82f6;
}

.arrow-success {
  fill: #10b981;
}

.arrow-failure {
  fill: #ef4444;
}

.connection-label {
  pointer-events: none;
}

.label-background {
  fill: white;
  stroke: #e5e7eb;
  stroke-width: 1;
}

.label-text {
  font-size: 12px;
  font-weight: 500;
  fill: #374151;
}

.delete-button {
  cursor: pointer;
  pointer-events: all;
}

.delete-bg {
  fill: #ef4444;
  stroke: white;
  stroke-width: 2;
}

.delete-bg:hover {
  fill: #dc2626;
}

.delete-icon {
  font-size: 12px;
  font-weight: bold;
  fill: white;
  cursor: pointer;
}
</style>
