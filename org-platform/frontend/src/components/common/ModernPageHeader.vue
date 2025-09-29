<template>
  <header class="modern-page-header">
    <div class="header-content">
      <div class="header-left">
        <div class="header-icon" :style="{ background: iconGradient }">
          <el-icon><component :is="icon" /></el-icon>
        </div>
        <div>
          <h2 class="header-title">{{ title }}</h2>
          <p class="header-subtitle">{{ subtitle }}</p>
        </div>
      </div>
      <div class="header-actions">
        <slot name="actions" />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  subtitle: string
  icon: string
  color?: 'blue' | 'purple' | 'green' | 'indigo' | 'emerald'
}

const props = withDefaults(defineProps<Props>(), {
  color: 'blue'
})

const iconGradient = computed(() => {
  const gradients = {
    blue: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
    purple: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
    green: 'linear-gradient(135deg, #10b981, #059669)',
    indigo: 'linear-gradient(135deg, #6366f1, #4f46e5)',
    emerald: 'linear-gradient(135deg, #10b981, #059669)'
  }
  return gradients[props.color]
})
</script>

<style scoped>
.modern-page-header {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #e2e8f0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.header-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.25rem;
}

.header-subtitle {
  color: #475569;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-title {
    font-size: 1.5rem;
  }
}
</style>
