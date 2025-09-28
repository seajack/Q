<template>
  <div class="form-validator">
    <!-- 表单容器 -->
    <el-form
      ref="formRef"
      :model="formData"
      :rules="validationRules"
      :label-width="labelWidth"
      :label-position="labelPosition"
      :size="size"
      :disabled="disabled"
      @validate="handleValidate"
    >
      <slot :form-data="formData" :errors="errors" :is-valid="isValid" />
    </el-form>
    
    <!-- 错误提示面板 -->
    <div v-if="showErrorPanel && errors.length > 0" class="error-panel">
      <div class="error-header">
        <el-icon><Warning /></el-icon>
        <span>请修正以下错误：</span>
        <button class="close-btn" @click="closeErrorPanel">×</button>
      </div>
      <div class="error-list">
        <div 
          v-for="(error, index) in errors" 
          :key="index"
          class="error-item"
          @click="scrollToField(error.field)"
        >
          <el-icon class="error-icon"><CircleClose /></el-icon>
          <span class="error-text">{{ error.message }}</span>
          <span class="error-field">{{ error.field }}</span>
        </div>
      </div>
    </div>
    
    <!-- 实时验证提示 -->
    <div v-if="showRealtimeValidation" class="realtime-validation">
      <div class="validation-status">
        <el-icon v-if="isValid" class="status-icon success"><Check /></el-icon>
        <el-icon v-else class="status-icon error"><Close /></el-icon>
        <span class="status-text">
          {{ isValid ? '表单验证通过' : `${errors.length} 个错误需要修正` }}
        </span>
      </div>
    </div>
    
    <!-- 字段级验证提示 -->
    <div v-if="fieldErrors.length > 0" class="field-errors">
      <div 
        v-for="fieldError in fieldErrors" 
        :key="fieldError.field"
        class="field-error"
        :data-field="fieldError.field"
      >
        <el-icon><Warning /></el-icon>
        <span>{{ fieldError.message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { Warning, CircleClose, Check, Close } from '@element-plus/icons-vue'
import { ElMessage, ElForm } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// Props
interface Props {
  modelValue: any
  rules?: FormRules
  labelWidth?: string
  labelPosition?: 'left' | 'right' | 'top'
  size?: 'large' | 'default' | 'small'
  disabled?: boolean
  showErrorPanel?: boolean
  showRealtimeValidation?: boolean
  validateOnChange?: boolean
  validateOnBlur?: boolean
  scrollToError?: boolean
  errorPanelPosition?: 'top' | 'bottom'
}

const props = withDefaults(defineProps<Props>(), {
  labelWidth: '120px',
  labelPosition: 'right',
  size: 'default',
  disabled: false,
  showErrorPanel: true,
  showRealtimeValidation: true,
  validateOnChange: true,
  validateOnBlur: true,
  scrollToError: true,
  errorPanelPosition: 'top'
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: any]
  'validate': [isValid: boolean, errors: any[]]
  'field-validate': [field: string, isValid: boolean, message: string]
  'submit': [formData: any]
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const formData = ref(props.modelValue || {})
const errors = ref<any[]>([])
const fieldErrors = ref<any[]>([])
const isValid = ref(true)
const showErrorPanel = ref(false)

// 计算属性
const validationRules = computed(() => props.rules || {})

// 方法
const validateForm = async (): Promise<boolean> => {
  if (!formRef.value) return false
  
  try {
    const valid = await formRef.value.validate()
    errors.value = []
    fieldErrors.value = []
    isValid.value = true
    showErrorPanel.value = false
    
    emit('validate', true, [])
    return true
  } catch (error: any) {
    const formErrors = error || []
    errors.value = formErrors
    fieldErrors.value = formErrors
    isValid.value = false
    showErrorPanel.value = true
    
    emit('validate', false, formErrors)
    
    // 滚动到第一个错误字段
    if (props.scrollToError && formErrors.length > 0) {
      scrollToField(formErrors[0].field)
    }
    
    return false
  }
}

const validateField = async (field: string): Promise<boolean> => {
  if (!formRef.value) return false
  
  try {
    await formRef.value.validateField(field)
    // 清除该字段的错误
    fieldErrors.value = fieldErrors.value.filter(error => error.field !== field)
    return true
  } catch (error: any) {
    const fieldError = {
      field,
      message: error.message || '验证失败',
      type: 'error'
    }
    
    // 更新字段错误
    const existingIndex = fieldErrors.value.findIndex(e => e.field === field)
    if (existingIndex >= 0) {
      fieldErrors.value[existingIndex] = fieldError
    } else {
      fieldErrors.value.push(fieldError)
    }
    
    emit('field-validate', field, false, fieldError.message)
    return false
  }
}

const clearValidation = () => {
  if (formRef.value) {
    formRef.value.clearValidate()
  }
  errors.value = []
  fieldErrors.value = []
  isValid.value = true
  showErrorPanel.value = false
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  clearValidation()
}

const submitForm = async () => {
  const valid = await validateForm()
  if (valid) {
    emit('submit', formData.value)
  }
}

const scrollToField = (fieldName: string) => {
  nextTick(() => {
    const fieldElement = document.querySelector(`[data-field="${fieldName}"]`) || 
                       document.querySelector(`[name="${fieldName}"]`) ||
                       document.querySelector(`#${fieldName}`)
    
    if (fieldElement) {
      fieldElement.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      })
      
      // 高亮字段
      fieldElement.classList.add('field-highlight')
      setTimeout(() => {
        fieldElement.classList.remove('field-highlight')
      }, 2000)
    }
  })
}

const closeErrorPanel = () => {
  showErrorPanel.value = false
}

const handleValidate = (prop: string, isValid: boolean, message: string) => {
  emit('field-validate', prop, isValid, message)
}

// 监听表单数据变化
watch(() => props.modelValue, (newValue) => {
  formData.value = newValue || {}
}, { deep: true })

watch(formData, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

// 监听验证规则变化
watch(() => props.rules, (newRules) => {
  if (formRef.value && newRules) {
    formRef.value.clearValidate()
  }
})

// 暴露方法
defineExpose({
  validateForm,
  validateField,
  clearValidation,
  resetForm,
  submitForm,
  scrollToField,
  formRef
})
</script>

<style scoped>
.form-validator {
  position: relative;
}

/* 错误提示面板 */
.error-panel {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  min-width: 300px;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fee2e2;
  border-bottom: 1px solid #fecaca;
  border-radius: 8px 8px 0 0;
  font-weight: 600;
  color: #dc2626;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #dc2626;
  cursor: pointer;
  margin-left: auto;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-list {
  max-height: 300px;
  overflow-y: auto;
}

.error-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #fecaca;
}

.error-item:hover {
  background: #fef2f2;
}

.error-item:last-child {
  border-bottom: none;
}

.error-icon {
  color: #dc2626;
  font-size: 16px;
}

.error-text {
  flex: 1;
  color: #dc2626;
  font-size: 14px;
}

.error-field {
  color: #9ca3af;
  font-size: 12px;
  font-family: monospace;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
}

/* 实时验证状态 */
.realtime-validation {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 999;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 12px 16px;
}

.validation-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.status-icon {
  font-size: 16px;
}

.status-icon.success {
  color: #10b981;
}

.status-icon.error {
  color: #ef4444;
}

.status-text {
  font-weight: 500;
}

/* 字段级错误提示 */
.field-errors {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 100;
}

.field-error {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 4px;
  color: #dc2626;
  font-size: 12px;
  margin-bottom: 4px;
}

.field-error:last-child {
  margin-bottom: 0;
}

/* 字段高亮效果 */
:global(.field-highlight) {
  animation: fieldHighlight 2s ease-in-out;
}

@keyframes fieldHighlight {
  0% { background-color: transparent; }
  25% { background-color: #fef3c7; }
  50% { background-color: #fde68a; }
  75% { background-color: #fef3c7; }
  100% { background-color: transparent; }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-panel {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
  
  .realtime-validation {
    bottom: 10px;
    right: 10px;
    left: 10px;
  }
  
  .error-header {
    padding: 10px 12px;
    font-size: 14px;
  }
  
  .error-item {
    padding: 10px 12px;
  }
  
  .error-text {
    font-size: 13px;
  }
  
  .error-field {
    font-size: 11px;
  }
}

/* 深色主题支持 */
@media (prefers-color-scheme: dark) {
  .error-panel {
    background: #1f2937;
    border-color: #374151;
  }
  
  .error-header {
    background: #374151;
    border-color: #4b5563;
    color: #fca5a5;
  }
  
  .error-item:hover {
    background: #374151;
  }
  
  .error-field {
    background: #4b5563;
    color: #d1d5db;
  }
  
  .realtime-validation {
    background: #1f2937;
    color: white;
  }
  
  .field-error {
    background: #374151;
    border-color: #4b5563;
    color: #fca5a5;
  }
}
</style>
