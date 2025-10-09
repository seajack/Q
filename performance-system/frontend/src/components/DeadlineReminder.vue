<template>
  <div class="deadline-reminder">
    <!-- 提醒卡片 -->
    <el-card v-if="upcomingDeadlines.length > 0" class="reminder-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon color="#F56C6C" size="20">
            <component :is="Icons.Warning" />
          </el-icon>
          <span class="card-title">截止日期提醒</span>
          <el-badge :value="upcomingDeadlines.length" type="danger" />
        </div>
      </template>
      
      <div class="reminder-content">
        <div 
          v-for="deadline in upcomingDeadlines" 
          :key="deadline.id"
          class="deadline-item"
          :class="getDeadlineClass(deadline)"
        >
          <div class="deadline-info">
            <div class="deadline-title">{{ deadline.title }}</div>
            <div class="deadline-meta">
              <span class="deadline-time">{{ formatDeadline(deadline.deadline) }}</span>
              <el-tag :type="getDeadlineTagType(deadline)" size="small">
                {{ getDeadlineStatus(deadline) }}
              </el-tag>
            </div>
          </div>
          
          <div class="deadline-actions">
            <el-button 
              type="primary" 
              size="small"
              @click="handleDeadlineAction(deadline)"
            >
              {{ getActionText(deadline) }}
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 设置提醒对话框 -->
    <el-dialog
      v-model="showReminderDialog"
      title="设置提醒"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="reminderForm" label-width="100px">
        <el-form-item label="提醒类型">
          <el-radio-group v-model="reminderForm.type">
            <el-radio value="deadline">截止日期</el-radio>
            <el-radio value="custom">自定义</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="提醒时间">
          <el-select v-model="reminderForm.time" placeholder="选择提醒时间">
            <el-option label="1小时前" value="1h" />
            <el-option label="2小时前" value="2h" />
            <el-option label="1天前" value="1d" />
            <el-option label="3天前" value="3d" />
            <el-option label="1周前" value="1w" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="提醒方式">
          <el-checkbox-group v-model="reminderForm.methods">
            <el-checkbox value="email">邮件</el-checkbox>
            <el-checkbox value="sms">短信</el-checkbox>
            <el-checkbox value="system">系统通知</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="提醒内容">
          <el-input
            v-model="reminderForm.message"
            type="textarea"
            :rows="3"
            placeholder="请输入提醒内容..."
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showReminderDialog = false">取消</el-button>
        <el-button type="primary" @click="saveReminder">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, markRaw } from 'vue'
import { Warning } from '@element-plus/icons-vue'

// 使用 markRaw 防止图标组件被转换为响应式对象
const Icons = markRaw({
  Warning
})
import { ElMessage } from 'element-plus'

// 响应式数据
const upcomingDeadlines = ref<any[]>([])
const showReminderDialog = ref(false)
const reminderForm = ref({
  type: 'deadline',
  time: '1d',
  methods: ['system'],
  message: ''
})

// 计算属性
const getDeadlineClass = (deadline: any) => {
  const hoursLeft = getHoursLeft(deadline.deadline)
  if (hoursLeft <= 0) return 'overdue'
  if (hoursLeft <= 24) return 'urgent'
  if (hoursLeft <= 72) return 'warning'
  return 'normal'
}

const getDeadlineTagType = (deadline: any) => {
  const hoursLeft = getHoursLeft(deadline.deadline)
  if (hoursLeft <= 0) return 'danger'
  if (hoursLeft <= 24) return 'warning'
  if (hoursLeft <= 72) return 'info'
  return 'success'
}

const getDeadlineStatus = (deadline: any) => {
  const hoursLeft = getHoursLeft(deadline.deadline)
  if (hoursLeft <= 0) return '已过期'
  if (hoursLeft <= 24) return '紧急'
  if (hoursLeft <= 72) return '即将到期'
  return '正常'
}

const getActionText = (deadline: any) => {
  const hoursLeft = getHoursLeft(deadline.deadline)
  if (hoursLeft <= 0) return '查看详情'
  return '立即处理'
}

// 方法
const loadUpcomingDeadlines = async () => {
  try {
    // 调用真实API获取截止日期提醒数据
    const { statsApi } = await import('@/utils/api')
    const response = await statsApi.deadlineReminders()
    
    if (response && response.deadlines) {
      upcomingDeadlines.value = response.deadlines
    } else {
      // 如果API调用失败，显示空数组
      upcomingDeadlines.value = []
    }
  } catch (error) {
    console.error('加载截止日期失败:', error)
    // 如果API调用失败，显示空数组
    upcomingDeadlines.value = []
  }
}

const getHoursLeft = (deadline: string) => {
  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diff = deadlineDate.getTime() - now.getTime()
  return Math.floor(diff / (1000 * 60 * 60))
}

const formatDeadline = (deadline: string) => {
  const date = new Date(deadline)
  const hoursLeft = getHoursLeft(deadline)
  
  if (hoursLeft <= 0) {
    return `已过期 ${date.toLocaleString('zh-CN')}`
  } else if (hoursLeft < 24) {
    return `${hoursLeft}小时后 (${date.toLocaleString('zh-CN')})`
  } else {
    const days = Math.floor(hoursLeft / 24)
    return `${days}天后 (${date.toLocaleString('zh-CN')})`
  }
}

const handleDeadlineAction = (deadline: any) => {
  const hoursLeft = getHoursLeft(deadline.deadline)
  
  if (hoursLeft <= 0) {
    ElMessage.warning('该任务已过期，请查看详情')
    // 跳转到详情页面
  } else {
    ElMessage.info('正在跳转到任务页面...')
    // 跳转到任务处理页面
  }
}

const saveReminder = async () => {
  try {
    // 模拟API调用
    console.log('保存提醒设置:', reminderForm.value)
    ElMessage.success('提醒设置已保存')
    showReminderDialog.value = false
  } catch (error) {
    console.error('保存提醒设置失败:', error)
    ElMessage.error('保存失败')
  }
}

// 生命周期
onMounted(() => {
  loadUpcomingDeadlines()
})
</script>

<style scoped>
.deadline-reminder {
  margin-bottom: 16px;
}

.reminder-card {
  border-left: 4px solid #F56C6C;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-title {
  font-weight: 600;
  color: #303133;
}

.reminder-content {
  max-height: 300px;
  overflow-y: auto;
}

.deadline-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s;
}

.deadline-item:hover {
  background: #f8f9fa;
}

.deadline-item.urgent {
  background: #fef0f0;
  border-color: #f56c6c;
}

.deadline-item.warning {
  background: #fdf6ec;
  border-color: #e6a23c;
}

.deadline-item.overdue {
  background: #fef0f0;
  border-color: #f56c6c;
  opacity: 0.8;
}

.deadline-info {
  flex: 1;
  min-width: 0;
}

.deadline-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  font-size: 14px;
}

.deadline-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #606266;
}

.deadline-time {
  margin-right: 8px;
}

.deadline-actions {
  flex-shrink: 0;
  margin-left: 12px;
}
</style>
