<template>
  <div class="modern-empty">
    <div class="modern-empty-icon">
      <slot name="icon">
        <component :is="iconComponent" v-if="iconComponent" />
        <span v-else class="default-icon">📄</span>
      </slot>
    </div>
    <h3 class="modern-empty-title">
      {{ title || '暂无数据' }}
    </h3>
    <p class="modern-empty-description">
      {{ description || '当前没有可显示的内容' }}
    </p>
    <div v-if="$slots.action" class="modern-empty-action">
      <slot name="action"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  Document, 
  User, 
  Calendar, 
  DataBoard,
  FolderOpened 
} from '@element-plus/icons-vue'

interface Props {
  title?: string
  description?: string
  icon?: 'document' | 'user' | 'calendar' | 'data' | 'folder' | string
}

const props = defineProps<Props>()

const iconComponent = computed(() => {
  switch (props.icon) {
    case 'document': return Document
    case 'user': return User
    case 'calendar': return Calendar
    case 'data': return DataBoard
    case 'folder': return FolderOpened
    default: return null
  }
})
</script>

<style scoped>
.modern-empty-action {
  margin-top: var(--spacing-6);
}

.default-icon {
  font-size: 48px;
  opacity: 0.6;
}
</style>