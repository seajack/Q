<template>
  <div class="drag-test">
    <h1>拖拽测试页面</h1>
    <div class="test-container">
      <svg width="800" height="600" class="test-svg">
        <g class="nodes">
          <g
            v-for="node in testNodes"
            :key="node.id"
            :transform="`translate(${node.x}, ${node.y})`"
            class="node-group"
          >
            <circle
              :r="30"
              :fill="node.color"
              :stroke="node.borderColor"
              stroke-width="2"
              @mousedown="startDrag($event, node)"
            />
            <text
              y="40"
              class="node-name"
              text-anchor="middle"
            >
              {{ node.name }}
            </text>
          </g>
        </g>
        
        <g class="connections">
          <path
            v-for="(conn, index) in connections"
            :key="index"
            :d="conn.path"
            stroke="#f59e0b"
            stroke-width="2"
            fill="none"
          />
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const testNodes = ref([
  { id: 1, name: '节点1', x: 100, y: 100, color: '#7c3aed', borderColor: '#5b21b6' },
  { id: 2, name: '节点2', x: 300, y: 200, color: '#3b82f6', borderColor: '#1d4ed8' },
  { id: 3, name: '节点3', x: 500, y: 150, color: '#10b981', borderColor: '#047857' }
])

const connections = computed(() => {
  return [
    {
      path: `M ${testNodes.value[0].x} ${testNodes.value[0].y} Q ${(testNodes.value[0].x + testNodes.value[1].x) / 2} ${Math.min(testNodes.value[0].y, testNodes.value[1].y) - 50} ${testNodes.value[1].x} ${testNodes.value[1].y}`
    },
    {
      path: `M ${testNodes.value[1].x} ${testNodes.value[1].y} Q ${(testNodes.value[1].x + testNodes.value[2].x) / 2} ${Math.min(testNodes.value[1].y, testNodes.value[2].y) - 50} ${testNodes.value[2].x} ${testNodes.value[2].y}`
    }
  ]
})

const isDragging = ref(false)
const dragNode = ref(null)
const dragOffset = ref({ x: 0, y: 0 })

const startDrag = (event: MouseEvent, node: any) => {
  event.preventDefault()
  event.stopPropagation()
  
  console.log('开始拖拽:', node.name)
  
  isDragging.value = true
  dragNode.value = node
  
  dragOffset.value = {
    x: event.clientX - node.x,
    y: event.clientY - node.y
  }
  
  // 添加全局事件监听
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleMouseMove = (event: MouseEvent) => {
  if (!isDragging.value || !dragNode.value) return
  
  const newX = event.clientX - dragOffset.value.x
  const newY = event.clientY - dragOffset.value.y
  
  // 限制在SVG边界内
  const constrainedX = Math.max(30, Math.min(770, newX))
  const constrainedY = Math.max(30, Math.min(570, newY))
  
  dragNode.value.x = constrainedX
  dragNode.value.y = constrainedY
}

const handleMouseUp = () => {
  isDragging.value = false
  dragNode.value = null
  
  // 移除全局事件监听
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}
</script>

<style scoped>
.drag-test {
  padding: 20px;
}

.test-container {
  border: 1px solid #ccc;
  border-radius: 8px;
  overflow: hidden;
}

.test-svg {
  background: #f8fafc;
}

.node-group {
  cursor: grab;
}

.node-group:active {
  cursor: grabbing;
}

.node-name {
  font-size: 14px;
  font-weight: 600;
  fill: #1e293b;
  pointer-events: none;
  user-select: none;
}
</style>
