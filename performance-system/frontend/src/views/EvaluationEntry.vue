<template>
  <div class="evaluation-entry">
    <div class="entry-container">
      <div class="header">
        <h1 class="title">绩效考核系统</h1>
        <p class="subtitle">请输入您的考核码</p>
      </div>
      
      <div class="code-input-section">
        <div class="code-input-container">
          <div class="code-input-group">
            <template v-for="(group, index) in codeGroups" :key="index">
              <input
                :ref="`input-${index}`"
                v-model="codeGroups[index]"
                type="text"
                class="code-input"
                :class="{ 'error': hasError }"
                maxlength="4"
                @input="onInput(index, $event)"
                @keydown="onKeydown(index, $event)"
                @paste="onPaste"
                :placeholder="`${index + 1}组`"
              />
              <span v-if="index < 3" class="separator">-</span>
            </template>
          </div>
        </div>
        
        <div class="code-display">
          <div class="code-text">{{ formattedCode }}</div>
        </div>
        
        <div v-if="hasError" class="error-message">
          {{ errorMessage }}
        </div>
        
        <div class="actions">
          <el-button 
            type="primary" 
            size="large" 
            :disabled="!isCodeComplete || loading"
            :loading="loading"
            @click="enterEvaluation"
            class="enter-button"
          >
            {{ loading ? '验证中...' : '进入考核' }}
          </el-button>
          
          <el-button 
            size="large" 
            @click="clearCode"
            class="clear-button"
          >
            清空
          </el-button>
        </div>
      </div>
      
      <div class="help-section">
        <div class="help-item">
          <i class="el-icon-info"></i>
          <span>考核码为16位字符，分为4组，每组4位</span>
        </div>
        <div class="help-item">
          <i class="el-icon-question"></i>
          <span>如：ABCD-EFGH-IJKL-MNOP</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { taskApi } from '@/utils/api'

const router = useRouter()

// 响应式数据
const codeGroups = ref(['', '', '', ''])
const loading = ref(false)
const hasError = ref(false)
const errorMessage = ref('')

// 计算属性
const formattedCode = computed(() => {
  return codeGroups.value.join('-')
})

const isCodeComplete = computed(() => {
  return codeGroups.value.every(group => group.length === 4)
})

// 输入处理
const onInput = (index: number, event: Event) => {
  const target = event.target as HTMLInputElement
  let value = target.value.toUpperCase()
  
  // 只允许字母和数字
  value = value.replace(/[^A-Z0-9]/g, '')
  
  codeGroups.value[index] = value
  
  // 清除错误状态
  if (hasError.value) {
    hasError.value = false
    errorMessage.value = ''
  }
  
  // 自动跳转到下一个输入框
  if (value.length === 4 && index < 3) {
    nextTick(() => {
      const nextInput = document.querySelector(`input[ref="input-${index + 1}"]`) as HTMLInputElement
      if (nextInput) {
        nextInput.focus()
      }
    })
  }
}

// 键盘事件处理
const onKeydown = (index: number, event: KeyboardEvent) => {
  // 退格键处理
  if (event.key === 'Backspace' && codeGroups.value[index] === '' && index > 0) {
    nextTick(() => {
      const prevInput = document.querySelector(`input[ref="input-${index - 1}"]`) as HTMLInputElement
      if (prevInput) {
        prevInput.focus()
      }
    })
  }
  
  // 回车键处理
  if (event.key === 'Enter' && isCodeComplete.value) {
    enterEvaluation()
  }
}

// 粘贴处理
const onPaste = (event: ClipboardEvent) => {
  event.preventDefault()
  const pastedText = event.clipboardData?.getData('text') || ''
  const cleanText = pastedText.replace(/[^A-Z0-9]/g, '').toUpperCase()
  
  if (cleanText.length === 16) {
    for (let i = 0; i < 4; i++) {
      codeGroups.value[i] = cleanText.substring(i * 4, (i + 1) * 4)
    }
  } else {
    ElMessage.warning('请粘贴完整的16位考核码')
  }
}

// 清空代码
const clearCode = () => {
  codeGroups.value = ['', '', '', '']
  hasError.value = false
  errorMessage.value = ''
  
  // 聚焦到第一个输入框
  nextTick(() => {
    const firstInput = document.querySelector('input[ref="input-0"]') as HTMLInputElement
    if (firstInput) {
      firstInput.focus()
    }
  })
}

// 进入考核
const enterEvaluation = async () => {
  if (!isCodeComplete.value) {
    ElMessage.warning('请输入完整的16位考核码')
    return
  }
  
  loading.value = true
  hasError.value = false
  
  try {
    const code = codeGroups.value.join('')
    console.log('验证考核码:', code)
    const response = await taskApi.getByCode(code)
    console.log('API响应:', response.data)
    
    if (response.data && response.data.task) {
      // 保存考核码到sessionStorage
      sessionStorage.setItem('evaluationCode', code)
      
      ElMessage.success('验证成功，正在进入考核系统...')
      
      // 跳转到考核页面
      router.push('/evaluation')
    } else {
      console.log('响应数据格式不正确:', response.data)
      throw new Error('未找到对应的考核任务')
    }
  } catch (error: any) {
    hasError.value = true
    errorMessage.value = error.response?.data?.error || '考核码无效，请检查后重试'
    ElMessage.error(errorMessage.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.evaluation-entry {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.entry-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 60px 40px;
  max-width: 600px;
  width: 100%;
  text-align: center;
}

.header {
  margin-bottom: 40px;
}

.title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 10px 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.2rem;
  color: #7f8c8d;
  margin: 0;
}

.code-input-section {
  margin-bottom: 40px;
}

.code-input-container {
  margin-bottom: 30px;
}

.code-input-group {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.code-input {
  width: 80px;
  height: 60px;
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  border: 3px solid #e1e8ed;
  border-radius: 12px;
  outline: none;
  transition: all 0.3s ease;
  background: #f8f9fa;
  color: #2c3e50;
}

.code-input:focus {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.code-input.error {
  border-color: #e74c3c;
  background: #fdf2f2;
}

.code-input::placeholder {
  color: #bdc3c7;
  font-size: 0.9rem;
}

.separator {
  font-size: 2rem;
  font-weight: bold;
  color: #bdc3c7;
  margin: 0 5px;
}

.code-display {
  margin-bottom: 20px;
}

.code-text {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  font-family: 'Courier New', monospace;
  letter-spacing: 2px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
  border: 2px solid #e1e8ed;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-message {
  color: #e74c3c;
  font-size: 1rem;
  margin-bottom: 20px;
  padding: 10px;
  background: #fdf2f2;
  border-radius: 8px;
  border: 1px solid #f5c6cb;
}

.actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.enter-button {
  min-width: 150px;
  height: 50px;
  font-size: 1.1rem;
  font-weight: bold;
  border-radius: 25px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.enter-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.enter-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.clear-button {
  min-width: 120px;
  height: 50px;
  font-size: 1.1rem;
  border-radius: 25px;
  border: 2px solid #bdc3c7;
  color: #7f8c8d;
  background: white;
  transition: all 0.3s ease;
}

.clear-button:hover {
  border-color: #95a5a6;
  color: #2c3e50;
  transform: translateY(-2px);
}

.help-section {
  border-top: 1px solid #e1e8ed;
  padding-top: 30px;
}

.help-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 10px;
  color: #7f8c8d;
  font-size: 0.95rem;
}

.help-item i {
  font-size: 1.1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .entry-container {
    padding: 40px 20px;
    margin: 10px;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .code-input {
    width: 70px;
    height: 50px;
    font-size: 1.3rem;
  }
  
  .code-text {
    font-size: 1.5rem;
  }
  
  .actions {
    flex-direction: column;
    align-items: center;
  }
  
  .enter-button,
  .clear-button {
    width: 100%;
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .code-input-group {
    gap: 5px;
  }
  
  .code-input {
    width: 60px;
    height: 45px;
    font-size: 1.1rem;
  }
  
  .separator {
    font-size: 1.5rem;
  }
}
</style>
