<template>
  <div class="relation-weight-config">
    <div class="weight-header">
      <span class="label">关系权重配置</span>
      <div class="total-weight">
        总权重：<span :class="['weight-value', totalWeight === 1 ? 'correct' : 'warning']">{{ totalWeight.toFixed(2) }}</span>
        <el-tag :type="totalWeight === 1 ? 'success' : 'warning'" size="small">
          {{ totalWeight === 1 ? '正确' : '需调整' }}
        </el-tag>
      </div>
    </div>
    
    <div class="weight-items">
      <div
        v-for="relationType in relationTypes"
        :key="relationType"
        class="weight-item"
      >
        <div class="weight-label">
          <span>{{ getRelationText(relationType) }}</span>
        </div>
        <div class="weight-input">
          <el-input-number
            v-model="weights[relationType]"
            :min="0"
            :max="1"
            :step="0.1"
            :precision="2"
            size="small"
            style="width: 120px"
            @change="onWeightChange"
          />
          <span class="weight-percentage">{{ ((weights[relationType] || 0) * 100).toFixed(1) }}%</span>
        </div>
      </div>
    </div>
    
    <div class="weight-actions">
      <el-button size="small" @click="resetWeights">重置</el-button>
      <el-button size="small" @click="autoDistribute">平均分配</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, defineProps, defineEmits } from 'vue'

const props = defineProps<{
  relationTypes: string[]
  weights: Record<string, number>
}>()

const emit = defineEmits<{
  'update:weights': [weights: Record<string, number>]
}>()

const weights = ref<Record<string, number>>({})

// 初始化权重
watch(() => props.weights, (newWeights) => {
  weights.value = { ...newWeights }
}, { immediate: true, deep: true })

// 监听权重变化
watch(weights, (newWeights) => {
  emit('update:weights', { ...newWeights })
}, { deep: true })

// 计算总权重
const totalWeight = computed(() => {
  return Object.values(weights.value).reduce((sum, weight) => sum + (weight || 0), 0)
})

// 关系类型文本映射
const getRelationText = (type: string) => {
  const relationMap: Record<string, string> = {
    superior: '上级评下级',
    peer: '同级互评',
    subordinate: '下级评上级',
    self: '自评',
    cross_superior: '跨部门上级',
    cross_peer: '跨部门同级',
    custom: '自定义关系'
  }
  return relationMap[type] || type
}

// 权重变化处理
const onWeightChange = () => {
  // 确保权重在0-1范围内
  Object.keys(weights.value).forEach(key => {
    if (weights.value[key] < 0) weights.value[key] = 0
    if (weights.value[key] > 1) weights.value[key] = 1
  })
}

// 重置权重
const resetWeights = () => {
  Object.keys(weights.value).forEach(key => {
    weights.value[key] = 0
  })
}

// 平均分配权重
const autoDistribute = () => {
  const activeTypes = props.relationTypes.filter(type => weights.value[type] > 0)
  if (activeTypes.length === 0) return
  
  const averageWeight = 1 / activeTypes.length
  activeTypes.forEach(type => {
    weights.value[type] = averageWeight
  })
}
</script>

<style scoped>
.relation-weight-config {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  background-color: #fafafa;
}

.weight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.label {
  font-weight: 500;
  color: #303133;
}

.total-weight {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.weight-value {
  font-weight: 500;
}

.weight-value.correct {
  color: #67c23a;
}

.weight-value.warning {
  color: #e6a23c;
}

.weight-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.weight-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.weight-label {
  flex: 1;
  font-size: 14px;
  color: #606266;
}

.weight-input {
  display: flex;
  align-items: center;
  gap: 12px;
}

.weight-percentage {
  font-size: 12px;
  color: #909399;
  min-width: 40px;
  text-align: right;
}

.weight-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
}
</style>
