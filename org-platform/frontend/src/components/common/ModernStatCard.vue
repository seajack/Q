<template>
  <div class="modern-stat-card" :class="cardType">
    <!-- 背景装饰 -->
    <div class="card-bg-decoration"></div>
    
    <!-- 卡片内容 -->
    <div class="card-content">
      <div class="stat-header">
        <div class="stat-title">{{ title }}</div>
        <div class="stat-icon" :class="iconType">
          <el-icon><component :is="icon" /></el-icon>
        </div>
      </div>
      
      <div class="stat-main">
        <div class="stat-value">{{ value }}</div>
        <div class="stat-subtitle" v-if="subtitle">{{ subtitle }}</div>
      </div>
      
      <div class="stat-footer">
        <div class="stat-change" :class="changeType">
          <el-icon><ArrowUp v-if="changeType === 'positive'" /><ArrowDown v-else /></el-icon>
          {{ change }}
        </div>
        <div class="stat-trend" v-if="trend">
          <div class="trend-line" :class="trendType"></div>
        </div>
      </div>
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
  subtitle?: string
  cardType?: 'systems' | 'gateways' | 'sync' | 'online'
  trend?: boolean
  trendType?: 'up' | 'down' | 'stable'
}

withDefaults(defineProps<Props>(), {
  iconType: 'primary',
  cardType: 'systems',
  trend: false,
  trendType: 'up'
})
</script>

<style scoped>
.modern-stat-card {
  position: relative;
  border-radius: 1.5rem;
  padding: 0;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  min-height: 160px;
}

.modern-stat-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* 卡片类型样式 */
.modern-stat-card.systems {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.modern-stat-card.gateways {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.modern-stat-card.sync {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.modern-stat-card.online {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

/* 背景装饰 */
.card-bg-decoration {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

/* 卡片内容 */
.card-content {
  position: relative;
  z-index: 2;
  padding: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.stat-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  line-height: 1.2;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.modern-stat-card:hover .stat-icon {
  transform: scale(1.1) rotate(5deg);
  background: rgba(255, 255, 255, 0.3);
}

.stat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat-value {
  font-size: 3rem;
  font-weight: 800;
  color: white;
  line-height: 1;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background: linear-gradient(45deg, #ffffff, rgba(255, 255, 255, 0.8));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-subtitle {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  line-height: 1.3;
}

.stat-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s ease;
}

.stat-change:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.stat-change.positive {
  background: rgba(16, 185, 129, 0.2);
  border-color: rgba(16, 185, 129, 0.3);
}

.stat-change.negative {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.3);
}

.stat-trend {
  width: 2rem;
  height: 1rem;
  position: relative;
}

.trend-line {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 1px;
}

.trend-line.up {
  background: linear-gradient(90deg, #10b981, #059669);
}

.trend-line.down {
  background: linear-gradient(90deg, #ef4444, #dc2626);
}

.trend-line.stable {
  background: linear-gradient(90deg, #6b7280, #4b5563);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modern-stat-card {
    min-height: 140px;
  }
  
  .card-content {
    padding: 1rem;
  }
  
  .stat-value {
    font-size: 2.5rem;
  }
  
  .stat-icon {
    width: 2.5rem;
    height: 2.5rem;
    font-size: 1.25rem;
  }
}

/* 动画效果 */
.modern-stat-card {
  animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 为不同卡片添加延迟动画 */
.modern-stat-card:nth-child(1) { animation-delay: 0.1s; }
.modern-stat-card:nth-child(2) { animation-delay: 0.2s; }
.modern-stat-card:nth-child(3) { animation-delay: 0.3s; }
.modern-stat-card:nth-child(4) { animation-delay: 0.4s; }

</style>
