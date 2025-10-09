<template>
  <div class="login-page">
    <!-- 装饰性几何元素 -->
    <div class="geometric-shape shape-1"></div>
    <div class="geometric-shape shape-2"></div>
    <div class="geometric-shape shape-3"></div>
    
    <div class="login-container">
      <div class="login-grid">
        <!-- 左侧品牌区域 -->
        <div class="brand-section">
          <div class="brand-content">
            <!-- Logo -->
            <div class="logo-container">
              <img src="/logo.jpg" alt="中煤内蒙古能源有限公司" class="logo-image">
            </div>
            
            <!-- 系统名称 -->
            <h1 class="system-title">
              绩效考核管理系统
            </h1>
            <p class="system-subtitle">
              Performance Management System
            </p>
            
            <!-- 企业标语 -->
            <div class="features-list">
              <div class="feature-item">
                <i class="feature-icon">🛡️</i>
                <span>安全可靠的企业级解决方案</span>
              </div>
              <div class="feature-item">
                <i class="feature-icon">📈</i>
                <span>智能化绩效考核管理</span>
              </div>
              <div class="feature-item">
                <i class="feature-icon">👥</i>
                <span>多维度员工评估体系</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧登录表单区域 -->
        <div class="form-section">
          <div class="login-card">
            <!-- 移动端Logo -->
            <div class="mobile-logo">
              <img src="/logo.jpg" alt="中煤内蒙古能源有限公司" class="mobile-logo-image">
              <h2 class="mobile-title">绩效考核管理系统</h2>
            </div>
            
            <!-- 普通登录表单 -->
            <form @submit.prevent="handleNormalLogin" class="login-form">
              <div class="form-header">
                <h2 class="form-title">
                  欢迎登录
                </h2>
                <p class="form-subtitle">
                  请输入您的账户信息
                </p>
              </div>
              
              <!-- 用户名输入 -->
              <div class="form-group">
                <label for="username" class="form-label">
                  用户名 / 邮箱
                </label>
                <div class="input-container">
                  <i class="input-icon">👤</i>
                  <input 
                    type="text" 
                    id="username" 
                    v-model="normalForm.username"
                    class="form-input" 
                    placeholder="请输入用户名或邮箱"
                    required
                  >
                </div>
              </div>
              
              <!-- 密码输入 -->
              <div class="form-group">
                <label for="password" class="form-label">
                  密码
                </label>
                <div class="input-container">
                  <i class="input-icon">🔒</i>
                  <input 
                    :type="showPassword ? 'text' : 'password'"
                    id="password" 
                    v-model="normalForm.password"
                    class="form-input" 
                    placeholder="请输入密码"
                    required
                  >
                  <button 
                    type="button" 
                    class="password-toggle"
                    @click="showPassword = !showPassword"
                  >
                    <i>{{ showPassword ? '🙈' : '👁️' }}</i>
                  </button>
                </div>
              </div>
              
              <!-- 记住我和忘记密码 -->
              <div class="form-options">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="normalForm.remember" class="checkbox">
                  <span>记住我</span>
                </label>
                <a href="#" class="forgot-link">
                  忘记密码？
                </a>
              </div>
              
              <!-- 登录按钮 -->
              <button 
                type="submit" 
                :disabled="isLoading"
                class="login-button"
              >
                <span v-if="!isLoading">
                  🔑 登录系统
                </span>
                <span v-else>
                  ⏳ 登录中...
                </span>
              </button>
            </form>
            
            <!-- 其他登录方式 -->
            <div class="alternative-login">
              <p class="alternative-text">
                或使用以下方式登录
              </p>
              <div class="alternative-buttons">
                <a href="/code-login" class="alt-button">
                  🔐 考核码登录
                </a>
                <button class="alt-button">
                  📱
                </button>
                <button class="alt-button">
                  👆
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 普通登录表单
const normalForm = ref({
  username: '',
  password: '',
  remember: false
})

const showPassword = ref(false)
const isLoading = ref(false)

// 普通登录处理
const handleNormalLogin = async () => {
  if (!normalForm.value.username || !normalForm.value.password) {
    showError('请输入用户名和密码')
    return
  }
  
  isLoading.value = true
  
  try {
    // 这里应该调用实际的登录API
    console.log('普通登录信息:', normalForm.value)
    
    // 模拟登录请求
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    showSuccess('登录成功！正在跳转...')
    
    // 跳转到仪表板
    setTimeout(() => {
      router.push('/dashboard-new')
    }, 2000)
  } catch (error) {
    showError('登录失败，请检查用户名和密码')
  } finally {
    isLoading.value = false
  }
}


// 显示错误信息
const showError = (message: string) => {
  // 创建错误提示元素
  const errorDiv = document.createElement('div')
  errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce'
  errorDiv.innerHTML = `<i data-lucide="alert-circle" class="w-5 h-5 inline mr-2"></i>${message}`
  
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
  successDiv.innerHTML = `<i data-lucide="check-circle" class="w-5 h-5 inline mr-2"></i>${message}`
  
  document.body.appendChild(successDiv)
  
  // 3秒后移除
  setTimeout(() => {
    successDiv.remove()
  }, 3000)
}

onMounted(() => {
  // 初始化Lucide图标
  if (window.lucide) {
    window.lucide.createIcons()
  }
})
</script>

<style scoped>
/* 登录页面整体样式 */
.login-page {
  font-family: 'Inter', 'Poppins', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
  background: linear-gradient(135deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%);
  min-height: 100vh;
  overflow: hidden;
  position: relative;
}

/* 装饰性几何元素 */
.geometric-shape {
  position: absolute;
  background: linear-gradient(45deg, rgba(59, 130, 246, 0.1), rgba(99, 102, 241, 0.1));
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 120px;
  height: 120px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 80px;
  height: 80px;
  top: 60%;
  left: 5%;
  animation-delay: 2s;
}

.shape-3 {
  width: 100px;
  height: 100px;
  top: 30%;
  right: 15%;
  animation-delay: 4s;
}

/* 登录容器 */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: slideIn 800ms ease-out;
}

.login-grid {
  width: 100%;
  max-width: 1200px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
  min-height: 100vh;
}

/* 左侧品牌区域 */
.brand-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: white;
  padding: 40px;
  animation: slideInLeft 600ms ease-out 200ms both;
}

.brand-content {
  max-width: 500px;
}

.logo-container {
  margin-bottom: 32px;
}

.logo-image {
  width: 96px;
  height: 96px;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  object-fit: cover;
  animation: fadeInScale 1000ms ease-out;
}

.system-title {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 8px;
  line-height: 1.2;
}

.system-subtitle {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 32px;
  line-height: 1.4;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
}

.feature-icon {
  font-size: 20px;
  width: 24px;
  text-align: center;
}

/* 右侧表单区域 */
.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  animation: slideInRight 600ms ease-out 400ms both;
}

.login-card {
  width: 100%;
  max-width: 480px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* 移动端Logo */
.mobile-logo {
  display: none;
  text-align: center;
  margin-bottom: 32px;
}

.mobile-logo-image {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  object-fit: cover;
  margin-bottom: 16px;
}

.mobile-title {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}


/* 表单样式 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-title {
  font-size: 30px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
  line-height: 1.2;
}

.form-subtitle {
  color: #6b7280;
  font-size: 16px;
  line-height: 1.5;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  line-height: 1.4;
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  font-size: 16px;
  color: #9ca3af;
  z-index: 1;
}

.form-input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  color: #1f2937;
  background: #ffffff;
  transition: all 300ms ease;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  transform: scale(1.02);
}

.password-toggle {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  font-size: 16px;
  transition: color 200ms ease;
}

.password-toggle:hover {
  color: #6b7280;
}


/* 表单选项 */
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
}

.checkbox {
  width: 16px;
  height: 16px;
  accent-color: #3b82f6;
}

.forgot-link {
  font-size: 14px;
  color: #3b82f6;
  text-decoration: none;
  transition: color 200ms ease;
}

.forgot-link:hover {
  color: #1d4ed8;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  padding: 12px 16px;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 300ms ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4), 0 4px 6px -2px rgba(59, 130, 246, 0.1);
}

.login-button:active:not(:disabled) {
  transform: scale(0.95);
}

.login-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 其他登录方式 */
.alternative-login {
  text-align: center;
  margin-top: 24px;
}

.alternative-text {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 16px;
}

.alternative-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.alt-button {
  padding: 12px 20px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 200ms ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
}

.alt-button:hover {
  background: #f9fafb;
  border-color: #9ca3af;
  color: #374151;
}

.alt-button:first-child {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border-color: #3b82f6;
}

.alt-button:first-child:hover {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
  border-color: #1d4ed8;
  color: white;
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

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
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

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-grid {
    grid-template-columns: 1fr;
    gap: 0;
  }
  
  .brand-section {
    display: none;
  }
  
  .mobile-logo {
    display: block;
  }
  
  .form-section {
    padding: 20px;
  }
}

@media (max-width: 640px) {
  .login-container {
    padding: 16px;
  }
  
  .login-card {
    padding: 24px;
  }
  
  .form-title {
    font-size: 24px;
  }
  
}
</style>
