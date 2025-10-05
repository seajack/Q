<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
        <div class="shape shape-5"></div>
      </div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="login-header">
        <div class="logo-section">
          <div class="logo-icon">
            <img src="/logo.jpg" alt="企业Logo" class="logo-image">
          </div>
          <h1 class="system-title">组织架构中台</h1>
          <p class="system-subtitle">企业组织架构管理平台</p>
        </div>
      </div>

      <div class="login-form">
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form-content"
          @submit.prevent="handleLogin"
        >
          <div class="form-group">
            <label class="form-label">用户名</label>
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="User"
                clearable
                class="form-input"
              />
            </el-form-item>
          </div>

          <div class="form-group">
            <label class="form-label">密码</label>
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                clearable
                class="form-input"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
          </div>

          <div class="form-options">
            <el-checkbox v-model="loginForm.rememberMe" class="remember-me">
              记住我
            </el-checkbox>
            <el-link type="primary" class="forgot-password">
              忘记密码？
            </el-link>
          </div>

          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            <span v-if="!loading">登录</span>
            <span v-else>登录中...</span>
          </el-button>

        
          <!-- <div class="test-account-tip">
            <el-alert
              title="测试账号"
              type="info"
              :closable="false"
              show-icon
            >
              <template #default>
                <p>用户名：<strong>admin</strong></p>
                <p>密码：<strong>123456</strong></p>
              </template>
            </el-alert>
          </div> -->
        </el-form>
      </div>

      <div class="login-footer">
        <div class="footer-links">
          <el-link type="info" size="small">帮助中心</el-link>
          <el-divider direction="vertical" />
          <el-link type="info" size="small">隐私政策</el-link>
          <el-divider direction="vertical" />
          <el-link type="info" size="small">服务条款</el-link>
        </div>
        <div class="copyright">
          © 2025 组织中台系统. All rights reserved.
        </div>
      </div>
    </div>

    <!-- 特性展示 -->
    <div class="features-panel">
      <div class="features-content">
        <h3 class="features-title">系统特性</h3>
        <div class="features-list">
          <div class="feature-item">
            <div class="feature-icon">
              <el-icon><OfficeBuilding /></el-icon>
            </div>
            <div class="feature-content">
              <h4>组织架构管理</h4>
              <p>灵活的组织架构设计与管理</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="feature-content">
              <h4>人员信息管理</h4>
              <p>全面的员工信息管理系统</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="feature-content">
              <h4>工作流引擎</h4>
              <p>强大的工作流程自动化</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="feature-content">
              <h4>智能分析</h4>
              <p>数据驱动的组织洞察</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, OfficeBuilding, Connection, TrendCharts } from '@element-plus/icons-vue'
import { loginApi, tokenManager, userManager } from '@/utils/auth'

const router = useRouter()

// 表单数据
const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false
})

// 表单验证规则
const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

// 表单引用
const loginFormRef = ref<FormInstance>()
const loading = ref(false)

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    loading.value = true

    try {
      // 模拟登录验证（用于测试）
      if (loginForm.username === 'admin' && loginForm.password === '123456') {
        // 模拟API响应
        const mockResponse = {
          token: 'mock-jwt-token-' + Date.now(),
          user: {
            id: 1,
            username: 'admin',
            name: '系统管理员',
            email: 'admin@company.com',
            role: 'admin',
            permissions: ['*'] // 管理员拥有所有权限
          },
          expiresIn: 3600
        }

        // 保存token和用户信息
        tokenManager.setToken(mockResponse.token)
        userManager.setUserInfo(mockResponse.user)

        ElMessage.success('登录成功！')
        
        // 跳转到主页面
        router.push('/dashboard')
        return
      } else {
        ElMessage.error('用户名或密码错误')
        return
      }

      // 真实API调用（当后端API可用时）
      // const response = await loginApi.login({
      //   username: loginForm.username,
      //   password: loginForm.password,
      //   rememberMe: loginForm.rememberMe
      // })
    } catch (apiError: any) {
      // API错误处理
      const errorMessage = apiError.response?.data?.message || apiError.message || '登录失败'
      ElMessage.error(errorMessage)
    }
  } catch (validationError) {
    // 表单验证错误
    console.error('表单验证失败:', validationError)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 50%, #2c5aa0 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.floating-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 120px;
  height: 120px;
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.shape-3 {
  width: 60px;
  height: 60px;
  top: 80%;
  left: 20%;
  animation-delay: 4s;
}

.shape-4 {
  width: 100px;
  height: 100px;
  top: 30%;
  right: 30%;
  animation-delay: 1s;
}

.shape-5 {
  width: 140px;
  height: 140px;
  top: 70%;
  left: 60%;
  animation-delay: 3s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* 登录卡片 */
.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 420px;
  max-width: 90vw;
  position: relative;
  z-index: 2;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #4a90e2, #357abd);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(74, 144, 226, 0.3);
  overflow: hidden;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 16px;
}

.system-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c5aa0;
  margin: 0;
  letter-spacing: -0.5px;
}

.system-subtitle {
  font-size: 14px;
  color: #4a90e2;
  margin: 0;
  font-weight: 400;
}

/* 登录表单 */
.login-form {
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #2c5aa0;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
}

.form-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 2px solid #e1e8ed;
  box-shadow: none;
  transition: all 0.3s ease;
  padding: 0 16px;
}

.form-input :deep(.el-input__wrapper:hover) {
  border-color: #4a90e2;
}

.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: #4a90e2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.remember-me {
  color: #4a90e2;
  font-size: 14px;
}

.forgot-password {
  font-size: 14px;
  text-decoration: none;
  color: #4a90e2;
}

.forgot-password:hover {
  color: #357abd;
}

.login-button {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #4a90e2, #357abd);
  border: none;
  box-shadow: 0 8px 20px rgba(74, 144, 226, 0.3);
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(74, 144, 226, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

/* 测试账号提示 */
.test-account-tip {
  margin-top: 20px;
}

.test-account-tip :deep(.el-alert) {
  border-radius: 8px;
  border: 1px solid #e1e8ed;
  background-color: #f8f9fa;
}

.test-account-tip :deep(.el-alert__content) {
  font-size: 13px;
}

.test-account-tip :deep(.el-alert__content p) {
  margin: 4px 0;
  color: #2c5aa0;
}

.test-account-tip :deep(.el-alert__content strong) {
  color: #4a90e2;
  font-weight: 700;
}

/* 登录页脚 */
.login-footer {
  text-align: center;
  margin-top: 30px;
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.copyright {
  font-size: 12px;
  color: #4a90e2;
}

/* 特性展示面板 */
.features-panel {
  position: absolute;
  right: 60px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(74, 144, 226, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px;
  width: 320px;
  border: 1px solid rgba(74, 144, 226, 0.2);
  z-index: 2;
}

.features-title {
  font-size: 20px;
  font-weight: 700;
  color: white;
  margin: 0 0 24px 0;
  text-align: center;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.feature-icon {
  width: 40px;
  height: 40px;
  background: rgba(74, 144, 226, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}

.feature-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0 0 4px 0;
}

.feature-content p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .features-panel {
    display: none;
  }
}

@media (max-width: 768px) {
  .login-card {
    padding: 30px 20px;
    width: 100%;
    max-width: 400px;
  }
  
  .system-title {
    font-size: 24px;
  }
  
  .login-container {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 24px 16px;
  }
  
  .system-title {
    font-size: 20px;
  }
  
  .logo-icon {
    width: 48px;
    height: 48px;
  }
  
  .logo-image {
    width: 32px;
    height: 32px;
  }
}
</style>
