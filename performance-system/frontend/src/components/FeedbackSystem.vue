<template>
  <div class="feedback-system">
    <!-- 申诉按钮 -->
    <el-button 
      type="warning" 
      @click="showFeedbackDialog = true"
      class="feedback-trigger"
    >
      <el-icon><component :is="Icons.ChatDotRound" /></el-icon>
      申诉反馈
    </el-button>

    <!-- 申诉反馈对话框 -->
    <el-dialog
      v-model="showFeedbackDialog"
      title="申诉反馈"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="feedbackForm" :rules="feedbackRules" ref="feedbackFormRef" label-width="100px">
        <el-form-item label="申诉类型" prop="type">
          <el-radio-group v-model="feedbackForm.type">
            <el-radio value="score">评分申诉</el-radio>
            <el-radio value="process">流程申诉</el-radio>
            <el-radio value="system">系统问题</el-radio>
            <el-radio value="other">其他</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="相关任务" prop="taskId">
          <el-select v-model="feedbackForm.taskId" placeholder="选择相关考核任务" style="width: 100%">
            <el-option 
              v-for="task in relatedTasks" 
              :key="task.id" 
              :label="`${task.evaluatee_name} - ${task.cycle_name}`" 
              :value="task.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="申诉标题" prop="title">
          <el-input v-model="feedbackForm.title" placeholder="请输入申诉标题" maxlength="100" show-word-limit />
        </el-form-item>
        
        <el-form-item label="详细描述" prop="description">
          <el-input
            v-model="feedbackForm.description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述申诉内容，包括具体问题、期望结果等..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="附件上传">
          <el-upload
            v-model:file-list="fileList"
            action="#"
            :auto-upload="false"
            :limit="3"
            :on-exceed="handleExceed"
            accept=".pdf,.doc,.docx,.jpg,.png"
          >
            <el-button type="primary" plain>
              <el-icon><component :is="Icons.Upload" /></el-icon>
              选择文件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持PDF、Word、图片格式，单个文件不超过10MB，最多3个文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="紧急程度" prop="priority">
          <el-radio-group v-model="feedbackForm.priority">
            <el-radio value="low">低</el-radio>
            <el-radio value="medium">中</el-radio>
            <el-radio value="high">高</el-radio>
            <el-radio value="urgent">紧急</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showFeedbackDialog = false">取消</el-button>
        <el-button type="primary" @click="submitFeedback" :loading="submitting">
          提交申诉
        </el-button>
      </template>
    </el-dialog>

    <!-- 申诉记录查看 -->
    <el-dialog
      v-model="showHistoryDialog"
      title="申诉记录"
      width="800px"
    >
      <div class="feedback-history">
        <div class="history-filters">
          <el-select v-model="historyFilter.status" placeholder="状态筛选" style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已关闭" value="closed" />
          </el-select>
          <el-button @click="loadFeedbackHistory">刷新</el-button>
        </div>
        
        <div class="history-list" v-loading="historyLoading">
          <div v-if="feedbackHistory.length === 0" class="empty-state">
            <el-empty description="暂无申诉记录" />
          </div>
          
          <div 
            v-for="item in feedbackHistory" 
            :key="item.id"
            class="history-item"
            :class="getHistoryItemClass(item.status)"
          >
            <div class="item-header">
              <div class="item-title">{{ item.title }}</div>
              <div class="item-meta">
                <el-tag :type="getStatusTagType(item.status)" size="small">
                  {{ getStatusText(item.status) }}
                </el-tag>
                <span class="item-time">{{ formatTime(item.created_at) }}</span>
              </div>
            </div>
            
            <div class="item-content">
              <div class="item-description">{{ item.description }}</div>
              <div class="item-details">
                <span class="detail-item">
                  <strong>类型：</strong>{{ getTypeText(item.type) }}
                </span>
                <span class="detail-item">
                  <strong>优先级：</strong>{{ getPriorityText(item.priority) }}
                </span>
                <span class="detail-item" v-if="item.task_id">
                  <strong>相关任务：</strong>{{ getTaskName(item.task_id) }}
                </span>
              </div>
            </div>
            
            <div class="item-actions">
              <el-button type="text" size="small" @click="viewFeedbackDetail(item)">
                查看详情
              </el-button>
              <el-button 
                v-if="item.status === 'pending'"
                type="text" 
                size="small" 
                @click="cancelFeedback(item.id)"
              >
                撤销申诉
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 申诉详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="申诉详情"
      width="700px"
    >
      <div v-if="currentFeedback" class="feedback-detail">
        <div class="detail-header">
          <h3>{{ currentFeedback.title }}</h3>
          <el-tag :type="getStatusTagType(currentFeedback.status)">
            {{ getStatusText(currentFeedback.status) }}
          </el-tag>
        </div>
        
        <div class="detail-content">
          <div class="detail-section">
            <h4>申诉信息</h4>
            <div class="detail-info">
              <p><strong>类型：</strong>{{ getTypeText(currentFeedback.type) }}</p>
              <p><strong>优先级：</strong>{{ getPriorityText(currentFeedback.priority) }}</p>
              <p><strong>提交时间：</strong>{{ formatTime(currentFeedback.created_at) }}</p>
              <p v-if="currentFeedback.task_id"><strong>相关任务：</strong>{{ getTaskName(currentFeedback.task_id) }}</p>
            </div>
          </div>
          
          <div class="detail-section">
            <h4>详细描述</h4>
            <div class="description-content">{{ currentFeedback.description }}</div>
          </div>
          
          <div class="detail-section" v-if="currentFeedback.attachments?.length">
            <h4>附件</h4>
            <div class="attachments">
              <div v-for="file in currentFeedback.attachments" :key="file.id" class="attachment-item">
                <el-icon><component :is="Icons.Document" /></el-icon>
                <span>{{ file.name }}</span>
                <el-button type="text" size="small">下载</el-button>
              </div>
            </div>
          </div>
          
          <div class="detail-section" v-if="currentFeedback.responses?.length">
            <h4>处理记录</h4>
            <div class="responses">
              <div v-for="response in currentFeedback.responses" :key="response.id" class="response-item">
                <div class="response-header">
                  <span class="response-author">{{ response.author }}</span>
                  <span class="response-time">{{ formatTime(response.created_at) }}</span>
                </div>
                <div class="response-content">{{ response.content }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, markRaw } from 'vue'
import { ChatDotRound, Upload, Document } from '@element-plus/icons-vue'

// 使用 markRaw 防止图标组件被转换为响应式对象
const Icons = markRaw({
  ChatDotRound,
  Upload,
  Document
})
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, UploadFile } from 'element-plus'

// 响应式数据
const showFeedbackDialog = ref(false)
const showHistoryDialog = ref(false)
const showDetailDialog = ref(false)
const submitting = ref(false)
const historyLoading = ref(false)
const feedbackFormRef = ref<FormInstance>()
const fileList = ref<UploadFile[]>([])

const feedbackForm = reactive({
  type: '',
  taskId: '',
  title: '',
  description: '',
  priority: 'medium'
})

const feedbackRules = {
  type: [{ required: true, message: '请选择申诉类型', trigger: 'change' }],
  taskId: [{ required: true, message: '请选择相关任务', trigger: 'change' }],
  title: [{ required: true, message: '请输入申诉标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入详细描述', trigger: 'blur' }],
  priority: [{ required: true, message: '请选择紧急程度', trigger: 'change' }]
}

const relatedTasks = ref<any[]>([])
const feedbackHistory = ref<any[]>([])
const currentFeedback = ref<any>(null)
const historyFilter = reactive({
  status: ''
})

// 方法
const loadRelatedTasks = async () => {
  try {
    // 模拟API调用
    const mockTasks = [
      { id: 1, evaluatee_name: '张三', cycle_name: '2025 Q1考核' },
      { id: 2, evaluatee_name: '李四', cycle_name: '2025 Q1考核' },
      { id: 3, evaluatee_name: '王五', cycle_name: '2025 Q1考核' }
    ]
    relatedTasks.value = mockTasks
  } catch (error) {
    console.error('加载相关任务失败:', error)
  }
}

const submitFeedback = async () => {
  if (!feedbackFormRef.value) return
  
  try {
    await feedbackFormRef.value.validate()
    submitting.value = true
    
    // 模拟API调用
    console.log('提交申诉:', feedbackForm, fileList.value)
    
    ElMessage.success('申诉提交成功，我们会在24小时内处理')
    showFeedbackDialog.value = false
    resetForm()
    
  } catch (error) {
    console.error('提交申诉失败:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  feedbackForm.type = ''
  feedbackForm.taskId = ''
  feedbackForm.title = ''
  feedbackForm.description = ''
  feedbackForm.priority = 'medium'
  fileList.value = []
  feedbackFormRef.value?.resetFields()
}

const loadFeedbackHistory = async () => {
  try {
    historyLoading.value = true
    
    // 模拟API调用
    const mockHistory = [
      {
        id: 1,
        type: 'score',
        title: '评分不公申诉',
        description: '我的考核评分明显偏低，希望重新评估',
        priority: 'high',
        status: 'processing',
        task_id: 1,
        created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        attachments: [],
        responses: [
          {
            id: 1,
            author: 'HR部门',
            content: '我们已收到您的申诉，正在调查中',
            created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
          }
        ]
      },
      {
        id: 2,
        type: 'process',
        title: '考核流程问题',
        description: '考核流程存在不合理之处',
        priority: 'medium',
        status: 'resolved',
        task_id: 2,
        created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        attachments: [],
        responses: []
      }
    ]
    
    feedbackHistory.value = mockHistory
    
  } catch (error) {
    console.error('加载申诉记录失败:', error)
  } finally {
    historyLoading.value = false
  }
}

const viewFeedbackDetail = (item: any) => {
  currentFeedback.value = item
  showDetailDialog.value = true
}

const cancelFeedback = async (feedbackId: number) => {
  try {
    await ElMessageBox.confirm('确定要撤销此申诉吗？', '确认撤销', {
      type: 'warning'
    })
    
    // 模拟API调用
    console.log('撤销申诉:', feedbackId)
    ElMessage.success('申诉已撤销')
    loadFeedbackHistory()
    
  } catch (error) {
    // 用户取消
  }
}

const handleExceed = () => {
  ElMessage.warning('最多只能上传3个文件')
}

// 工具方法
const getTypeText = (type: string) => {
  const typeMap = {
    score: '评分申诉',
    process: '流程申诉',
    system: '系统问题',
    other: '其他'
  }
  return typeMap[type as keyof typeof typeMap] || type
}

const getPriorityText = (priority: string) => {
  const priorityMap = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急'
  }
  return priorityMap[priority as keyof typeof priorityMap] || priority
}

const getStatusText = (status: string) => {
  const statusMap = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已解决',
    closed: '已关闭'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const getStatusTagType = (status: string) => {
  const typeMap = {
    pending: 'warning',
    processing: 'primary',
    resolved: 'success',
    closed: 'info'
  }
  return typeMap[status as keyof typeof typeMap] || 'info'
}

const getHistoryItemClass = (status: string) => {
  return `status-${status}`
}

const getTaskName = (taskId: number) => {
  const task = relatedTasks.value.find(t => t.id === taskId)
  return task ? `${task.evaluatee_name} - ${task.cycle_name}` : '未知任务'
}

const formatTime = (dateTime: string) => {
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadRelatedTasks()
  loadFeedbackHistory()
})
</script>

<style scoped>
.feedback-system {
  display: inline-block;
}

.feedback-trigger {
  margin-left: 8px;
}

.feedback-history {
  max-height: 500px;
  overflow-y: auto;
}

.history-filters {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.history-item {
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #ffffff;
  transition: all 0.3s;
}

.history-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.history-item.status-pending {
  border-left: 4px solid #e6a23c;
}

.history-item.status-processing {
  border-left: 4px solid #409eff;
}

.history-item.status-resolved {
  border-left: 4px solid #67c23a;
}

.history-item.status-closed {
  border-left: 4px solid #909399;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.item-title {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-time {
  font-size: 12px;
  color: #909399;
}

.item-content {
  margin-bottom: 12px;
}

.item-description {
  color: #606266;
  line-height: 1.5;
  margin-bottom: 8px;
}

.item-details {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.item-actions {
  display: flex;
  gap: 8px;
}

.feedback-detail {
  max-height: 500px;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-header h3 {
  margin: 0;
  color: #303133;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.detail-info p {
  margin: 4px 0;
  color: #606266;
  font-size: 14px;
}

.description-content {
  color: #606266;
  line-height: 1.6;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.attachments {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
}

.responses {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.response-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.response-author {
  font-weight: 600;
  color: #303133;
}

.response-time {
  font-size: 12px;
  color: #909399;
}

.response-content {
  color: #606266;
  line-height: 1.5;
}
</style>
