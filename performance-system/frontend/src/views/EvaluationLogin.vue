<template>
  <div class="evaluation-login">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h2>考核评价系统</h2>
          <p>请输入您的考核码</p>
        </div>
        
        <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleLogin">
          <el-form-item prop="evaluationCode">
            <el-input
              v-model="form.evaluationCode"
              placeholder="请输入16位考核码"
              size="large"
              maxlength="16"
              show-word-limit
              clearable
            >
              <template #prefix>
                <el-icon><Key /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              :loading="loading"
              @click="handleLogin"
              style="width: 100%"
            >
              进入评价系统
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-footer">
          <p class="help-text">
            <el-icon><InfoFilled /></el-icon>
            考核码由系统管理员分配，如有疑问请联系HR部门
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElForm } from 'element-plus'
import { Key, InfoFilled } from '@element-plus/icons-vue'
import { taskApi } from '@/utils/api'

const router = useRouter()
const formRef = ref<InstanceType<typeof ElForm>>()
const loading = ref(false)

const form = reactive({
  evaluationCode: ''
})

const rules = {
  evaluationCode: [
    { required: true, message: '请输入考核码', trigger: 'blur' },
    { min: 16, max: 16, message: '考核码必须为16位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 验证考核码并获取考核人信息
    const response = await taskApi.getEvaluatorTasks(form.evaluationCode)
    
    if (response.data && response.data.evaluator) {
      // 保存考核人信息到sessionStorage
      sessionStorage.setItem('evaluator_info', JSON.stringify(response.data.evaluator))
      sessionStorage.setItem('evaluation_code', form.evaluationCode)
      
      ElMessage.success(`欢迎，${response.data.evaluator.name}！`)
      
      // 跳转到评价页面
      router.push({
        name: 'EvaluatorTasks',
        query: { code: form.evaluationCode }
      })
    } else {
      ElMessage.error('考核码无效，请检查后重试')
    }
    
  } catch (error: any) {
    console.error('登录失败:', error)
    if (error.response?.status === 404) {
      ElMessage.error('考核码不存在，请检查后重试')
    } else {
      ElMessage.error('登录失败，请重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.evaluation-login {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
}

.login-header p {
  color: #666;
  margin: 0;
  font-size: 14px;
}

.login-footer {
  margin-top: 20px;
  text-align: center;
}

.help-text {
  color: #999;
  font-size: 12px;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

:deep(.el-input__inner) {
  height: 48px;
  font-size: 16px;
}

:deep(.el-button--large) {
  height: 48px;
  font-size: 16px;
}
</style>
