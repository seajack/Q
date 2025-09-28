<template>
  <div class="guided-workflow">
    <!-- 引导步骤指示器 -->
    <div v-if="showSteps" class="steps-indicator">
      <div class="steps-container">
        <div 
          v-for="(step, index) in steps" 
          :key="step.id"
          :class="['step-item', { 
            'active': currentStep === index,
            'completed': index < currentStep,
            'disabled': index > currentStep
          }]"
          @click="goToStep(index)"
        >
          <div class="step-number">
            <el-icon v-if="index < currentStep"><Check /></el-icon>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="step-content">
            <h4>{{ step.title }}</h4>
            <p>{{ step.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 引导提示框 -->
    <div v-if="showTooltip" class="tooltip-overlay" :style="tooltipStyle">
      <div class="tooltip-content">
        <div class="tooltip-header">
          <h3>{{ currentTooltip.title }}</h3>
          <button class="close-btn" @click="closeTooltip">×</button>
        </div>
        <div class="tooltip-body">
          <p>{{ currentTooltip.content }}</p>
          <div v-if="currentTooltip.image" class="tooltip-image">
            <img :src="currentTooltip.image" :alt="currentTooltip.title" />
          </div>
        </div>
        <div class="tooltip-footer">
          <el-button size="small" @click="prevTooltip" :disabled="tooltipIndex === 0">
            上一步
          </el-button>
          <el-button size="small" @click="nextTooltip" :disabled="tooltipIndex === tooltips.length - 1">
            下一步
          </el-button>
          <el-button type="primary" size="small" @click="completeTooltip">
            {{ tooltipIndex === tooltips.length - 1 ? '完成' : '跳过' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 新手引导遮罩 -->
    <div v-if="showOnboarding" class="onboarding-overlay">
      <div class="onboarding-content">
        <div class="onboarding-header">
          <h2>🎉 欢迎使用绩效考核系统</h2>
          <p>让我们快速了解系统的主要功能</p>
        </div>
        <div class="onboarding-body">
          <div class="feature-grid">
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <h4>考核看板</h4>
              <p>查看整体考核进度和关键指标</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📝</div>
              <h4>任务管理</h4>
              <p>创建和管理考核任务</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📈</div>
              <h4>结果分析</h4>
              <p>查看详细的考核结果和报表</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">⚙️</div>
              <h4>系统设置</h4>
              <p>配置考核规则和权限</p>
            </div>
          </div>
        </div>
        <div class="onboarding-footer">
          <el-button @click="skipOnboarding">跳过引导</el-button>
          <el-button type="primary" @click="startGuidedTour">开始引导</el-button>
        </div>
      </div>
    </div>

    <!-- 操作提示 -->
    <div v-if="showHint" class="hint-bubble" :style="hintStyle">
      <div class="hint-content">
        <span class="hint-text">{{ currentHint }}</span>
        <button class="hint-close" @click="closeHint">×</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const showSteps = ref(false)
const showTooltip = ref(false)
const showOnboarding = ref(false)
const showHint = ref(false)
const currentStep = ref(0)
const tooltipIndex = ref(0)
const currentHint = ref('')
const tooltipStyle = ref({})
const hintStyle = ref({})

// 引导步骤配置
const steps = ref([
  {
    id: 'dashboard',
    title: '考核看板',
    description: '查看整体考核进度和关键指标',
    route: '/dashboard-new',
    element: '.dashboard-container'
  },
  {
    id: 'cycles',
    title: '考核周期',
    description: '创建和管理考核周期',
    route: '/cycles',
    element: '.cycles-section'
  },
  {
    id: 'tasks',
    title: '考核任务',
    description: '分配和管理考核任务',
    route: '/tasks',
    element: '.tasks-section'
  },
  {
    id: 'results',
    title: '考核结果',
    description: '查看和分析考核结果',
    route: '/results',
    element: '.results-section'
  }
])

// 引导提示配置
const tooltips = ref([
  {
    title: '欢迎使用绩效考核系统',
    content: '这是一个功能强大的绩效考核管理系统，帮助您高效管理员工考核流程。',
    element: '.dashboard-title',
    position: 'bottom'
  },
  {
    title: '考核看板功能',
    content: '在这里您可以查看整体考核进度、完成率等关键指标，快速了解系统状态。',
    element: '.kpi-grid',
    position: 'top'
  },
  {
    title: '快捷操作',
    content: '使用这些按钮可以快速创建新的考核周期、查看任务或刷新数据。',
    element: '.header-actions',
    position: 'bottom'
  }
])

// 计算属性
const currentTooltip = computed(() => tooltips.value[tooltipIndex.value])

// 方法
const showOnboardingDialog = () => {
  showOnboarding.value = true
}

const startGuidedTour = () => {
  showOnboarding.value = false
  showSteps.value = true
  showTooltip.value = true
  currentStep.value = 0
  tooltipIndex.value = 0
  updateTooltipPosition()
}

const skipOnboarding = () => {
  showOnboarding.value = false
  ElMessage.success('已跳过引导，您可以随时在设置中重新开始')
}

const goToStep = (index: number) => {
  if (index <= currentStep.value) {
    currentStep.value = index
    tooltipIndex.value = index
    updateTooltipPosition()
  }
}

const nextTooltip = () => {
  if (tooltipIndex.value < tooltips.value.length - 1) {
    tooltipIndex.value++
    updateTooltipPosition()
  }
}

const prevTooltip = () => {
  if (tooltipIndex.value > 0) {
    tooltipIndex.value--
    updateTooltipPosition()
  }
}

const completeTooltip = () => {
  if (tooltipIndex.value === tooltips.value.length - 1) {
    showTooltip.value = false
    showSteps.value = false
    ElMessage.success('引导完成！您已经了解了系统的主要功能')
  } else {
    tooltipIndex.value++
    updateTooltipPosition()
  }
}

const closeTooltip = () => {
  showTooltip.value = false
  showSteps.value = false
}

const updateTooltipPosition = () => {
  const element = document.querySelector(currentTooltip.value.element)
  if (element) {
    const rect = element.getBoundingClientRect()
    const position = currentTooltip.value.position
    
    let top = 0
    let left = 0
    
    if (position === 'bottom') {
      top = rect.bottom + 10
      left = rect.left + rect.width / 2
    } else if (position === 'top') {
      top = rect.top - 10
      left = rect.left + rect.width / 2
    } else {
      top = rect.top + rect.height / 2
      left = rect.right + 10
    }
    
    tooltipStyle.value = {
      top: `${top}px`,
      left: `${left}px`,
      transform: 'translateX(-50%)'
    }
  }
}

const showOperationHint = (message: string, element?: string) => {
  currentHint.value = message
  showHint.value = true
  
  if (element) {
    const el = document.querySelector(element)
    if (el) {
      const rect = el.getBoundingClientRect()
      hintStyle.value = {
        top: `${rect.top - 40}px`,
        left: `${rect.left + rect.width / 2}px`,
        transform: 'translateX(-50%)'
      }
    }
  }
  
  // 3秒后自动关闭
  setTimeout(() => {
    closeHint()
  }, 3000)
}

const closeHint = () => {
  showHint.value = false
}

// 检查是否为新用户
const checkNewUser = () => {
  const isNewUser = !localStorage.getItem('performance_system_visited')
  if (isNewUser) {
    showOnboardingDialog()
    localStorage.setItem('performance_system_visited', 'true')
  }
}

// 生命周期
onMounted(() => {
  checkNewUser()
})

// 暴露方法给父组件
defineExpose({
  showOnboardingDialog,
  startGuidedTour,
  showOperationHint,
  showSteps,
  showTooltip
})
</script>

<style scoped>
.guided-workflow {
  position: relative;
}

/* 步骤指示器 */
.steps-indicator {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 20px;
  max-width: 300px;
}

.steps-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.step-item.active {
  background: #e3f2fd;
  border-color: #2196f3;
}

.step-item.completed {
  background: #e8f5e8;
  border-color: #4caf50;
}

.step-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
  background: #9e9e9e;
  transition: all 0.3s ease;
}

.step-item.active .step-number {
  background: #2196f3;
}

.step-item.completed .step-number {
  background: #4caf50;
}

.step-content h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.step-content p {
  margin: 0;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

/* 引导提示框 */
.tooltip-overlay {
  position: fixed;
  z-index: 1001;
  background: white;
  border-radius: 12px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  max-width: 400px;
  min-width: 300px;
}

.tooltip-content {
  padding: 20px;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tooltip-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tooltip-body p {
  margin: 0 0 16px 0;
  color: #666;
  line-height: 1.6;
}

.tooltip-image {
  text-align: center;
}

.tooltip-image img {
  max-width: 100%;
  border-radius: 8px;
}

.tooltip-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 新手引导遮罩 */
.onboarding-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.onboarding-content {
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
}

.onboarding-header {
  text-align: center;
  padding: 32px 32px 24px;
  border-bottom: 1px solid #eee;
}

.onboarding-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.onboarding-header p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.onboarding-body {
  padding: 32px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.feature-item {
  text-align: center;
  padding: 20px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: #e3f2fd;
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.feature-item h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.feature-item p {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.onboarding-footer {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding: 24px 32px 32px;
  border-top: 1px solid #eee;
}

/* 操作提示 */
.hint-bubble {
  position: fixed;
  z-index: 1002;
  background: #333;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  max-width: 300px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.hint-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hint-text {
  flex: 1;
}

.hint-close {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .steps-indicator {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .onboarding-content {
    margin: 10px;
  }
  
  .onboarding-header,
  .onboarding-body,
  .onboarding-footer {
    padding: 20px;
  }
}
</style>
