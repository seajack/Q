<template>
  <div class="code-login-page">
    <div class="login-container">
      <!-- Logo -->
      <div class="logo-section">
        <img src="/logo.jpg" alt="中煤内蒙古能源有限公司" class="logo-image">
        <h1 class="system-title">绩效考核管理系统</h1>
        <!-- <p class="system-subtitle">考核码登录</p> -->
      </div>
      
      <!-- 考核码输入表单 -->
      <form @submit.prevent="handleCodeLogin" class="code-form">
        <div class="form-header">
          <h2 class="form-title">
            请输入16位考核码
          </h2>
          <!-- <p class="form-subtitle">
            支持数字和字母，字母将自动转换为大写
          </p> -->
        </div>
        
          <!-- 考核码输入 -->
          <div class="form-group">
            <!-- <label class="form-label">
              考核码
            </label> -->
            <div class="code-inputs">
              <template v-for="(digit, index) in codeDigits" :key="index">
                <input
                  :ref="`codeInput${index}`"
                  v-model="codeDigits[index]"
                  @input="handleCodeInput(index, $event)"
                  @keydown="handleCodeKeydown(index, $event)"
                  @paste="handleCodePaste"
                  type="text"
                  maxlength="1"
                  class="code-input"
                  :class="{ error: codeError }"
                  placeholder=""
                >
                <!-- 每4位添加分隔符 -->
                <span v-if="(index + 1) % 4 === 0 && index < 15" class="code-separator">-</span>
              </template>
            </div>
          
          <!-- 进度指示器 -->
          <div class="progress-indicator">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
            </div>
            <span class="progress-text">{{ filledCount }}/16</span>
          </div>
          
          <!-- 错误提示 -->
          <div v-if="codeError" class="error-message">
            {{ codeError }}
          </div>
        </div>
        
        <!-- 登录按钮 -->
        <button 
          type="submit" 
          :disabled="isLoading || !isCodeComplete"
          class="login-button"
        >
          <span v-if="!isLoading">
            🔐 验证考核码
          </span>
          <span v-else>
            ⏳ 验证中...
          </span>
        </button>
      </form>
      
      <!-- 返回普通登录 -->
      <div class="back-to-login">
        <a href="/login" class="back-link">
          ← 返回普通登录
        </a>
      </div>
      
      <!-- 帮助信息 -->
      <div class="help-section">
        <div class="help-item">
          <i class="help-icon">💡</i>
          <span>考核码为16位数字或字母，由系统管理员分配</span>
        </div>
        <div class="help-item">
          <i class="help-icon">⌨️</i>
          <span>支持输入小写字母，系统会自动转换为大写</span>
        </div>
        <div class="help-item">
          <i class="help-icon">📞</i>
          <span>如有疑问请联系HR部门：400-123-4567</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { taskApi } from '@/utils/api'

const router = useRouter()

// 考核码登录
const codeDigits = ref(Array(16).fill(''))
const isLoading = ref(false)
const codeError = ref('')

// 计算属性
const isCodeComplete = computed(() => {
  return codeDigits.value.every(digit => digit !== '')
})

const filledCount = computed(() => {
  return codeDigits.value.filter(digit => digit !== '').length
})

const progressPercentage = computed(() => {
  return (filledCount.value / 16) * 100
})

// 考核码登录处理
const handleCodeLogin = async () => {
  if (!isCodeComplete.value) {
    codeError.value = '请输入完整的16位考核码'
    return
  }
  
  isLoading.value = true
  codeError.value = ''
  
  try {
    const code = codeDigits.value.join('')
    console.log('考核码登录:', code)
    
    // 调用后端API验证考核码
    const response = await taskApi.getByCode(code)
    
    if (response.data && response.data.task) {
      showSuccess('考核码验证成功！正在跳转...')
      // 将考核码存储到本地，供后续使用
      localStorage.setItem('evaluationCode', code)
      setTimeout(() => {
        router.push('/dashboard-new')
      }, 2000)
    } else {
      codeError.value = '考核码无效，请检查后重新输入'
      // 清空输入
      codeDigits.value = Array(16).fill('')
      // 聚焦到第一个输入框
      nextTick(() => {
        const firstInput = document.querySelector('.code-input') as HTMLInputElement
        firstInput?.focus()
      })
    }
  } catch (error: any) {
    console.error('考核码验证失败:', error)
    if (error.response && error.response.status === 404) {
      codeError.value = '考核码无效，请检查后重新输入'
    } else {
      codeError.value = '验证失败，请重试'
    }
  } finally {
    isLoading.value = false
  }
}

// 考核码输入处理
const handleCodeInput = (index: number, event: Event) => {
  const target = event.target as HTMLInputElement
  let value = target.value
  
  // 只允许数字和字母，自动转换为大写
  if (!/^[0-9A-Za-z]*$/.test(value)) {
    target.value = ''
    return
  }
  
  // 转换为大写
  value = value.toUpperCase()
  target.value = value
  codeDigits.value[index] = value
  
  // 自动跳转到下一个输入框
  if (value && index < 15) {
    nextTick(() => {
      // 使用更可靠的方式查找下一个输入框
      const allInputs = document.querySelectorAll('.code-input')
      const nextInput = allInputs[index + 1] as HTMLInputElement
      if (nextInput) {
        nextInput.focus()
        nextInput.select() // 选中下一个输入框的内容，方便直接输入
      }
    })
  }
}

// 考核码键盘事件处理
const handleCodeKeydown = (index: number, event: KeyboardEvent) => {
  const target = event.target as HTMLInputElement
  
  // 处理退格键
  if (event.key === 'Backspace' && !target.value && index > 0) {
    const allInputs = document.querySelectorAll('.code-input')
    const prevInput = allInputs[index - 1] as HTMLInputElement
    if (prevInput) {
      prevInput.focus()
      prevInput.select()
    }
  }
  
  // 处理删除键
  if (event.key === 'Delete' && target.value) {
    target.value = ''
    codeDigits.value[index] = ''
  }
  
  // 处理左箭头键
  if (event.key === 'ArrowLeft' && index > 0) {
    const allInputs = document.querySelectorAll('.code-input')
    const prevInput = allInputs[index - 1] as HTMLInputElement
    if (prevInput) {
      prevInput.focus()
      prevInput.select()
    }
  }
  
  // 处理右箭头键
  if (event.key === 'ArrowRight' && index < 15) {
    const allInputs = document.querySelectorAll('.code-input')
    const nextInput = allInputs[index + 1] as HTMLInputElement
    if (nextInput) {
      nextInput.focus()
      nextInput.select()
    }
  }
}

// 考核码粘贴处理
const handleCodePaste = (event: ClipboardEvent) => {
  event.preventDefault()
  const pastedData = event.clipboardData?.getData('text') || ''
  
  // 只保留数字和字母，转换为大写，最多16位，支持带分隔符的格式
  const characters = pastedData.replace(/[^0-9A-Za-z]/g, '').toUpperCase().slice(0, 16)
  
  // 清空所有输入框
  codeDigits.value = Array(16).fill('')
  
  // 填充到输入框
  for (let i = 0; i < characters.length && i < 16; i++) {
    codeDigits.value[i] = characters[i]
  }
  
  // 更新输入框显示
  nextTick(() => {
    const allInputs = document.querySelectorAll('.code-input')
    for (let i = 0; i < characters.length && i < 16; i++) {
      const input = allInputs[i] as HTMLInputElement
      if (input) {
        input.value = characters[i]
      }
    }
  })
  
  // 聚焦到下一个空输入框或最后一个输入框
  const nextEmptyIndex = characters.length < 16 ? characters.length : 15
  nextTick(() => {
    const allInputs = document.querySelectorAll('.code-input')
    const nextInput = allInputs[nextEmptyIndex] as HTMLInputElement
    if (nextInput) {
      nextInput.focus()
      nextInput.select()
    }
  })
}

// 显示错误信息
const showError = (message: string) => {
  // 创建错误提示元素
  const errorDiv = document.createElement('div')
  errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce'
  errorDiv.innerHTML = `<i class="w-5 h-5 inline mr-2">⚠️</i>${message}`
  
  document.body.appendChild(errorDiv)
  
  // 3秒后移除
  setTimeout(() => {
    errorDiv.remove()
  }, 3000)
}

// 显示成功信息
const showSuccess = (message: string) => {
  // 创建成功提示元素
  const successDiv = document.createElement('div')
  successDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce'
  successDiv.innerHTML = `<i class="w-5 h-5 inline mr-2">✅</i>${message}`
  
  document.body.appendChild(successDiv)
  
  // 3秒后移除
  setTimeout(() => {
    successDiv.remove()
  }, 3000)
}

onMounted(() => {
  // 聚焦到第一个输入框
  const firstInput = document.querySelector('.code-input') as HTMLInputElement
  firstInput?.focus()
})
</script>

<style scoped>
/* 考核码登录页面整体样式 */
.code-login-page {
  font-family: 'Inter', 'Poppins', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
  background: #ffffff;
  min-height: 100vh;
  overflow: hidden;
  position: relative;
}

/* 动态背景粒子效果 */
.code-login-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 20%, #3b82f6 0%, transparent 20%),
    radial-gradient(circle at 80% 80%, #ef4444 0%, transparent 25%),
    radial-gradient(circle at 40% 60%, #10b981 0%, transparent 15%),
    radial-gradient(circle at 60% 40%, #f59e0b 0%, transparent 18%),
    radial-gradient(circle at 10% 70%, #8b5cf6 0%, transparent 22%),
    radial-gradient(circle at 90% 30%, #06b6d4 0%, transparent 16%);
  animation: backgroundShift 8s ease-in-out infinite;
  will-change: transform, opacity;
  transform: translateZ(0);
}

.code-login-page::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(45deg, #3b82f6 0%, transparent 50%, #ef4444 100%),
    linear-gradient(-45deg, #10b981 0%, transparent 50%, #f59e0b 100%),
    linear-gradient(90deg, #8b5cf6 0%, transparent 30%, #06b6d4 100%);
  animation: backgroundShift 12s ease-in-out infinite reverse;
  will-change: transform, opacity;
  transform: translateZ(0);
}

/* 额外的动态线条和圆点 */
.code-login-page {
  position: relative;
}

.code-login-page::before {
  z-index: 1;
}

.code-login-page::after {
  z-index: 2;
}

/* 添加动态线条 */
.code-login-page::before {
  background-image: 
    radial-gradient(circle at 20% 20%, #3b82f6 0%, transparent 30%),
    radial-gradient(circle at 80% 80%, #ef4444 0%, transparent 35%),
    radial-gradient(circle at 40% 60%, #10b981 0%, transparent 25%),
    radial-gradient(circle at 60% 40%, #f59e0b 0%, transparent 28%),
    radial-gradient(circle at 10% 70%, #8b5cf6 0%, transparent 32%),
    radial-gradient(circle at 90% 30%, #06b6d4 0%, transparent 26%),
    /* 添加线条效果 */
    linear-gradient(0deg, transparent 0%, #3b82f6 3%, transparent 6%),
    linear-gradient(90deg, transparent 0%, #ef4444 2%, transparent 4%),
    linear-gradient(45deg, transparent 0%, #10b981 2%, transparent 4%),
    linear-gradient(-45deg, transparent 0%, #f59e0b 2%, transparent 4%);
  background-size: 200% 200%, 200% 200%, 200% 200%, 200% 200%, 200% 200%, 200% 200%, 200% 200%, 200% 200%, 200% 200%, 200% 200%;
  animation: backgroundShift 6s ease-in-out infinite, lineMove 4s linear infinite;
}

.code-login-page::after {
  background-image: 
    linear-gradient(45deg, #3b82f6 0%, transparent 50%, #ef4444 100%),
    linear-gradient(-45deg, #10b981 0%, transparent 50%, #f59e0b 100%),
    linear-gradient(90deg, #8b5cf6 0%, transparent 30%, #06b6d4 100%),
    /* 添加更多线条 */
    linear-gradient(30deg, transparent 0%, #3b82f6 2%, transparent 4%),
    linear-gradient(-30deg, transparent 0%, #ef4444 2%, transparent 4%),
    linear-gradient(60deg, transparent 0%, #10b981 2%, transparent 4%);
  background-size: 300% 300%, 300% 300%, 300% 300%, 300% 300%, 300% 300%, 300% 300%;
  animation: backgroundShift 8s ease-in-out infinite reverse, lineMove 5s linear infinite reverse;
}

@keyframes backgroundShift {
  0%, 100% { 
    opacity: 1; 
    transform: scale(1) rotate(0deg) translateX(0px) translateY(0px);
  }
  25% { 
    opacity: 0.9; 
    transform: scale(1.3) rotate(8deg) translateX(30px) translateY(-20px);
  }
  50% { 
    opacity: 0.7; 
    transform: scale(0.7) rotate(-5deg) translateX(-25px) translateY(25px);
  }
  75% { 
    opacity: 0.95; 
    transform: scale(1.15) rotate(3deg) translateX(15px) translateY(-10px);
  }
}

@keyframes lineMove {
  0% { 
    background-position: 0% 0%, 100% 0%, 0% 100%, 100% 100%, 50% 50%, 0% 50%, 0% 0%, 100% 0%, 0% 100%, 100% 100%;
  }
  25% { 
    background-position: 25% 25%, 75% 25%, 25% 75%, 75% 75%, 25% 25%, 25% 75%, 25% 0%, 75% 0%, 25% 100%, 75% 100%;
  }
  50% { 
    background-position: 50% 50%, 50% 50%, 50% 50%, 50% 50%, 50% 50%, 50% 50%, 50% 0%, 50% 0%, 50% 100%, 50% 100%;
  }
  75% { 
    background-position: 75% 75%, 25% 75%, 75% 25%, 25% 25%, 75% 75%, 75% 25%, 75% 0%, 25% 0%, 75% 100%, 25% 100%;
  }
  100% { 
    background-position: 100% 100%, 0% 100%, 100% 0%, 0% 0%, 100% 100%, 100% 0%, 100% 0%, 0% 0%, 100% 100%, 0% 100%;
  }
}

/* 登录容器 */
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: slideIn 800ms ease-out;
  text-align: center;
  position: relative;
  z-index: 10;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

/* Logo区域 */
.logo-section {
  margin-bottom: 30px;
  text-align: center;
  animation: slideInDown 1000ms ease-out;
}

.logo-image {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  box-shadow: 
    0 20px 40px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  object-fit: cover;
  margin-bottom: 16px;
  animation: logoFloat 4s ease-in-out infinite;
  transition: transform 300ms ease, box-shadow 300ms ease;
  will-change: transform;
}

.logo-image:hover {
  transform: scale(1.05);
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.35),
    0 0 0 1px rgba(255, 255, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.system-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  animation: titleGlow 4s ease-in-out infinite alternate;
  will-change: filter;
}

.system-subtitle {
  font-size: 16px;
  color: #64748b;
  margin-bottom: 0;
  line-height: 1.4;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

@keyframes logoFloat {
  0%, 100% { 
    transform: translateY(0px) scale(1); 
  }
  25% { 
    transform: translateY(-5px) scale(1.02); 
  }
  50% { 
    transform: translateY(-8px) scale(1.01); 
  }
  75% { 
    transform: translateY(-3px) scale(1.015); 
  }
}

@keyframes titleGlow {
  0%, 100% { 
    filter: brightness(1) drop-shadow(0 0 0px rgba(59, 130, 246, 0)); 
  }
  50% { 
    filter: brightness(1.05) drop-shadow(0 0 8px rgba(59, 130, 246, 0.3)); 
  }
}

/* 表单样式 */
.code-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.form-header {
  text-align: center;
}

.form-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  animation: titleSlide 1000ms ease-out;
}

.form-subtitle {
  color: #64748b;
  font-size: 14px;
  line-height: 1.5;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  animation: subtitleFade 1200ms ease-out;
}

@keyframes titleSlide {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes subtitleFade {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-label {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  line-height: 1.4;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 考核码输入 - 16位一行排列 */
.code-inputs {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: center;
  gap: 4px;
  max-width: 800px;
  margin: 0 auto;
  overflow-x: auto;
}


.code-input {
  width: 35px;
  height: 40px;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
  color: #1f2937;
  transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
  font-family: 'Courier New', monospace;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 分隔符样式 */
.code-separator {
  font-size: 18px;
  font-weight: 700;
  color: #6b7280;
  margin: 0 2px;
  user-select: none;
  flex-shrink: 0;
}


.code-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 
    0 0 0 4px rgba(102, 126, 234, 0.15),
    0 4px 8px rgba(102, 126, 234, 0.2);
  transform: scale(1.05);
  background: #f8fafc;
}

.code-input:hover {
  border-color: #cbd5e1;
  transform: scale(1.02);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.code-input.error {
  border-color: #ef4444;
  background: #fef2f2;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* 进度指示器 */
.progress-indicator {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(203, 213, 225, 0.5);
  animation: progressSlide 1000ms ease-out;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6 0%, #1e40af 50%, #1d4ed8 100%);
  border-radius: 6px;
  transition: width 500ms cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  min-width: 40px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

@keyframes progressSlide {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.error-message {
  color: #dc2626;
  font-size: 14px;
  text-align: center;
  margin-top: 12px;
  font-weight: 500;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  padding: 14px 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #1e40af 50%, #1d4ed8 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 400ms cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 8px 16px -5px rgba(59, 130, 246, 0.4),
    0 4px 6px -2px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
  animation: buttonSlide 1000ms ease-out;
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 600ms ease;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 
    0 15px 25px -5px rgba(102, 126, 234, 0.5),
    0 8px 10px -2px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.login-button:hover:not(:disabled)::before {
  left: 100%;
}

.login-button:active:not(:disabled) {
  transform: scale(0.98);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 50%, #4b5563 100%);
}

@keyframes buttonSlide {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 返回登录链接 */
.back-to-login {
  margin-top: 24px;
  text-align: center;
}

.back-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 16px;
  font-weight: 500;
  transition: color 200ms ease;
}

.back-link:hover {
  color: #1d4ed8;
}

/* 帮助信息 */
.help-section {
  margin-top: 24px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(203, 213, 225, 0.5);
  backdrop-filter: blur(10px);
  animation: helpSlide 1000ms ease-out;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.help-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #374151;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.help-item:last-child {
  margin-bottom: 0;
}

.help-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

@keyframes helpSlide {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 动画效果 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% { 
    transform: translateY(0px) rotate(0deg); 
  }
  50% { 
    transform: translateY(-20px) rotate(180deg); 
  }
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 输入框逐个出现动画 */
.code-input {
  animation: inputAppear 0.3s ease-out;
  animation-fill-mode: both;
}

.code-input:nth-child(1) { animation-delay: 0.1s; }
.code-input:nth-child(2) { animation-delay: 0.15s; }
.code-input:nth-child(3) { animation-delay: 0.2s; }
.code-input:nth-child(4) { animation-delay: 0.25s; }
.code-input:nth-child(5) { animation-delay: 0.3s; }
.code-input:nth-child(6) { animation-delay: 0.35s; }
.code-input:nth-child(7) { animation-delay: 0.4s; }
.code-input:nth-child(8) { animation-delay: 0.45s; }
.code-input:nth-child(9) { animation-delay: 0.5s; }
.code-input:nth-child(10) { animation-delay: 0.55s; }
.code-input:nth-child(11) { animation-delay: 0.6s; }
.code-input:nth-child(12) { animation-delay: 0.65s; }
.code-input:nth-child(13) { animation-delay: 0.7s; }
.code-input:nth-child(14) { animation-delay: 0.75s; }
.code-input:nth-child(15) { animation-delay: 0.8s; }
.code-input:nth-child(16) { animation-delay: 0.85s; }

@keyframes inputAppear {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .code-inputs {
    gap: 3px;
    padding: 12px;
    max-width: 600px;
    overflow-x: auto;
  }
  
  .code-input {
    width: 30px;
    height: 35px;
    font-size: 14px;
  }
  
  .code-separator {
    font-size: 16px;
    margin: 0 1px;
  }
  
  .system-title {
    font-size: 24px;
  }
  
  .form-title {
    font-size: 20px;
  }
  
  .logo-image {
    width: 60px;
    height: 60px;
  }
}

@media (max-width: 480px) {
  .code-inputs {
    gap: 2px;
    padding: 8px;
    max-width: 400px;
    overflow-x: auto;
  }
  
  .code-input {
    width: 25px;
    height: 30px;
    font-size: 12px;
  }
  
  .code-separator {
    font-size: 14px;
    margin: 0 1px;
  }
  
  .system-title {
    font-size: 20px;
  }
  
  .form-title {
    font-size: 18px;
  }
  
  .logo-image {
    width: 50px;
    height: 50px;
  }
}
</style>