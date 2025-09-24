<template>
  <div class="empty-state">
    <div class="empty-icon">
      <el-icon :size="iconSize">
        <component :is="icon" />
      </el-icon>
    </div>
    <h3 class="empty-title">{{ title }}</h3>
    <p class="empty-description">{{ description }}</p>
    <div v-if="showAction" class="empty-action">
      <el-button 
        type="primary" 
        :size="buttonSize"
        @click="$emit('action')"
      >
        <el-icon><Plus /></el-icon>
        {{ actionText }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Plus } from '@element-plus/icons-vue'

interface Props {
  icon?: string
  title?: string
  description?: string
  actionText?: string
  showAction?: boolean
  iconSize?: number
  buttonSize?: 'large' | 'default' | 'small'
}

withDefaults(defineProps<Props>(), {
  icon: 'Document',
  title: '暂无数据',
  description: '当前没有相关数据，请稍后再试',
  actionText: '创建新项目',
  showAction: true,
  iconSize: 64,
  buttonSize: 'default'
})

defineEmits<{
  action: []
}>()
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  min-height: 300px;
}

.empty-icon {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--primary-100) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  color: var(--primary-color);
  border: 2px solid var(--primary-200);
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  letter-spacing: -0.25px;
}

.empty-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 24px 0;
  line-height: 1.5;
  max-width: 400px;
}

.empty-action {
  margin-top: 8px;
}

.empty-action .el-button {
  border-radius: 10px;
  font-weight: 500;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>

