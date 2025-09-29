<template>
  <div class="modern-stat-card">
    <div class="stat-header">
      <div class="stat-title">{{ title }}</div>
      <div class="stat-icon" :class="iconType">
        <el-icon><component :is="icon" /></el-icon>
      </div>
    </div>
    <div class="stat-value">{{ value }}</div>
    <div class="stat-change" :class="changeType">
      <el-icon><ArrowUp v-if="changeType === 'positive'" /><ArrowDown v-else /></el-icon>
      {{ change }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'

interface Props {
  title: string
  value: string | number
  change: string
  changeType: 'positive' | 'negative'
  icon: string
  iconType?: 'primary' | 'success' | 'warning' | 'error'
}

withDefaults(defineProps<Props>(), {
  iconType: 'primary'
})
</script>

<style scoped>
.modern-stat-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #e2e8f0;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.modern-stat-card:hover {
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  transform: translateY(-2px);
}

.modern-stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #0ea5e9, #0284c7);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stat-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.stat-icon.primary { background: linear-gradient(135deg, #0ea5e9, #0284c7); }
.stat-icon.success { background: linear-gradient(135deg, #10b981, #059669); }
.stat-icon.warning { background: linear-gradient(135deg, #f59e0b, #d97706); }
.stat-icon.error { background: linear-gradient(135deg, #ef4444, #dc2626); }

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.5rem;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.stat-change.positive { color: #10b981; }
.stat-change.negative { color: #ef4444; }
</style>
