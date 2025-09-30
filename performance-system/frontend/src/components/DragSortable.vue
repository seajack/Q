<template>
  <div class="drag-sortable-container">
    <div 
      v-for="(item, index) in items" 
      :key="item.id"
      :class="['sortable-item', { 
        'dragging': draggingIndex === index,
        'drag-over': dragOverIndex === index
      }]"
      :draggable="!disabled"
      @dragstart="handleDragStart($event, index)"
      @dragend="handleDragEnd"
      @dragover="handleDragOver($event, index)"
      @dragenter="handleDragEnter($event, index)"
      @dragleave="handleDragLeave"
      @drop="handleDrop($event, index)"
    >
      <!-- 拖拽手柄 -->
      <div v-if="showHandle" class="drag-handle">
        <el-icon><component :is="Icons.Rank" /></el-icon>
      </div>
      
      <!-- 内容插槽 -->
      <div class="item-content">
        <slot :item="item" :index="index">
          <div class="default-content">
            <h4>{{ item.name || item.title || `项目 ${index + 1}` }}</h4>
            <p v-if="item.description">{{ item.description }}</p>
          </div>
        </slot>
      </div>
      
      <!-- 排序指示器 -->
      <div v-if="showOrder" class="order-indicator">
        <span class="order-number">{{ index + 1 }}</span>
      </div>
    </div>
    
    <!-- 拖拽预览 -->
    <div v-if="isDragging" class="drag-preview" :style="dragPreviewStyle">
      <div class="preview-content">
        <slot :item="draggedItem" :index="draggingIndex">
          <div class="default-content">
            <h4>{{ draggedItem?.name || draggedItem?.title || `项目 ${draggingIndex + 1}` }}</h4>
            <p v-if="draggedItem?.description">{{ draggedItem.description }}</p>
          </div>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, markRaw } from 'vue'
import { Rank } from '@element-plus/icons-vue'

// 使用 markRaw 防止图标组件被转换为响应式对象
const Icons = markRaw({
  Rank
})
import { ElMessage } from 'element-plus'

// Props
interface Props {
  items: any[]
  disabled?: boolean
  showHandle?: boolean
  showOrder?: boolean
  animation?: boolean
  ghostClass?: string
  chosenClass?: string
  dragClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  showHandle: true,
  showOrder: true,
  animation: true,
  ghostClass: 'sortable-ghost',
  chosenClass: 'sortable-chosen',
  dragClass: 'sortable-drag'
})

// Emits
const emit = defineEmits<{
  'update:items': [items: any[]]
  'sort': [newItems: any[], oldIndex: number, newIndex: number]
  'start': [item: any, index: number]
  'end': [item: any, index: number]
}>()

// 响应式数据
const isDragging = ref(false)
const draggingIndex = ref(-1)
const dragOverIndex = ref(-1)
const draggedItem = ref<any>(null)
const dragPreviewStyle = ref({})

// 计算属性
const items = computed({
  get: () => props.items,
  set: (value) => emit('update:items', value)
})

// 拖拽开始
const handleDragStart = (event: DragEvent, index: number) => {
  if (props.disabled) return
  
  draggingIndex.value = index
  draggedItem.value = items.value[index]
  isDragging.value = true
  
  // 设置拖拽数据
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', index.toString())
    
    // 设置拖拽图片
    const dragImage = event.target as HTMLElement
    event.dataTransfer.setDragImage(dragImage, 0, 0)
  }
  
  emit('start', items.value[index], index)
}

// 拖拽结束
const handleDragEnd = () => {
  isDragging.value = false
  draggingIndex.value = -1
  dragOverIndex.value = -1
  draggedItem.value = null
  dragPreviewStyle.value = {}
  
  emit('end', draggedItem.value, draggingIndex.value)
}

// 拖拽悬停
const handleDragOver = (event: DragEvent, index: number) => {
  event.preventDefault()
  if (props.disabled || draggingIndex.value === index) return
  
  dragOverIndex.value = index
  
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

// 拖拽进入
const handleDragEnter = (event: DragEvent, index: number) => {
  event.preventDefault()
  if (props.disabled || draggingIndex.value === index) return
  
  dragOverIndex.value = index
}

// 拖拽离开
const handleDragLeave = () => {
  dragOverIndex.value = -1
}

// 放置
const handleDrop = (event: DragEvent, newIndex: number) => {
  event.preventDefault()
  if (props.disabled) return
  
  const oldIndex = draggingIndex.value
  if (oldIndex === -1 || oldIndex === newIndex) return
  
  // 执行排序
  const newItems = [...items.value]
  const [movedItem] = newItems.splice(oldIndex, 1)
  newItems.splice(newIndex, 0, movedItem)
  
  // 更新数据
  items.value = newItems
  
  // 触发事件
  emit('sort', newItems, oldIndex, newIndex)
  
  // 显示成功消息
  ElMessage.success(`已移动 ${movedItem.name || movedItem.title || '项目'} 到第 ${newIndex + 1} 位`)
  
  // 重置状态
  handleDragEnd()
}

// 监听拖拽状态变化，更新预览样式
watch(isDragging, (dragging) => {
  if (dragging) {
    updateDragPreview()
  }
})

// 更新拖拽预览样式
const updateDragPreview = () => {
  const draggedElement = document.querySelector('.sortable-item.dragging')
  if (draggedElement) {
    const rect = draggedElement.getBoundingClientRect()
    dragPreviewStyle.value = {
      position: 'fixed',
      top: `${rect.top}px`,
      left: `${rect.left}px`,
      width: `${rect.width}px`,
      height: `${rect.height}px`,
      zIndex: 9999,
      opacity: 0.8,
      transform: 'rotate(5deg)',
      pointerEvents: 'none'
    }
  }
}

// 公开方法
const sortItems = (newOrder: number[]) => {
  const newItems = newOrder.map(index => items.value[index])
  items.value = newItems
  emit('sort', newItems, -1, -1)
}

const moveItem = (fromIndex: number, toIndex: number) => {
  if (fromIndex === toIndex) return
  
  const newItems = [...items.value]
  const [movedItem] = newItems.splice(fromIndex, 1)
  newItems.splice(toIndex, 0, movedItem)
  
  items.value = newItems
  emit('sort', newItems, fromIndex, toIndex)
}

// 暴露方法
defineExpose({
  sortItems,
  moveItem
})
</script>

<style scoped>
.drag-sortable-container {
  position: relative;
}

.sortable-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: move;
  transition: all 0.3s ease;
  position: relative;
}

.sortable-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.sortable-item.dragging {
  opacity: 0.5;
  transform: rotate(5deg);
  z-index: 1000;
}

.sortable-item.drag-over {
  border-color: #10b981;
  background: #f0fdf4;
  transform: translateX(8px);
}

.drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: #9ca3af;
  cursor: grab;
  transition: color 0.3s ease;
}

.drag-handle:hover {
  color: #3b82f6;
}

.drag-handle:active {
  cursor: grabbing;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.default-content h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.default-content p {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.4;
}

.order-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #f3f4f6;
  border-radius: 50%;
  font-weight: 600;
  color: #6b7280;
  font-size: 14px;
}

.sortable-item.dragging .order-indicator {
  background: #3b82f6;
  color: white;
}

.drag-preview {
  position: fixed;
  background: white;
  border: 2px solid #3b82f6;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  pointer-events: none;
}

.preview-content {
  padding: 16px;
}

/* 拖拽动画 */
.sortable-item {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sortable-item.dragging {
  transition: none;
}

/* 禁用状态 */
.sortable-item[draggable="false"] {
  cursor: default;
  opacity: 0.6;
}

.sortable-item[draggable="false"] .drag-handle {
  cursor: default;
  color: #d1d5db;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sortable-item {
    padding: 12px;
    gap: 8px;
  }
  
  .drag-handle {
    width: 20px;
    height: 20px;
  }
  
  .order-indicator {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }
  
  .default-content h4 {
    font-size: 14px;
  }
  
  .default-content p {
    font-size: 13px;
  }
}

/* 拖拽时的全局样式 */
:global(.sortable-ghost) {
  opacity: 0.4;
  background: #f3f4f6;
}

:global(.sortable-chosen) {
  background: #e3f2fd;
  border-color: #3b82f6;
}

:global(.sortable-drag) {
  transform: rotate(5deg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}
</style>
