<template>
  <div class="notification-center">
    <!-- 通知图标 -->
    <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
      <el-button 
        type="text" 
        @click="showNotifications = true"
        class="notification-trigger"
      >
        <el-icon size="20">
          <Bell />
        </el-icon>
      </el-button>
    </el-badge>

    <!-- 通知抽屉 -->
    <el-drawer
      v-model="showNotifications"
      title="通知中心"
      direction="rtl"
      size="400px"
      :close-on-click-modal="false"
    >
      <div class="notification-content">
        <!-- 通知筛选 -->
        <div class="notification-filters">
          <el-radio-group v-model="filterType" @change="loadNotifications">
            <el-radio value="all">全部</el-radio>
            <el-radio value="unread">未读</el-radio>
            <el-radio value="reminder">提醒</el-radio>
            <el-radio value="deadline">截止</el-radio>
          </el-radio-group>
        </div>

        <!-- 通知列表 -->
        <div class="notification-list" v-loading="loading">
          <div v-if="notifications.length === 0" class="empty-state">
            <el-empty description="暂无通知" />
          </div>
          
          <div 
            v-for="notification in notifications" 
            :key="notification.id"
            class="notification-item"
            :class="{ 'unread': !notification.is_read }"
            @click="handleNotificationClick(notification)"
          >
            <div class="notification-icon">
              <el-icon :color="getNotificationColor(notification.type)">
                <component :is="getNotificationIcon(notification.type)" />
              </el-icon>
            </div>
            
            <div class="notification-content">
              <div class="notification-title">{{ notification.title }}</div>
              <div class="notification-message">{{ notification.message }}</div>
              <div class="notification-meta">
                <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
                <el-tag 
                  :type="getNotificationTagType(notification.type)" 
                  size="small"
                >
                  {{ getNotificationTypeText(notification.type) }}
                </el-tag>
              </div>
            </div>
            
            <div class="notification-actions">
              <el-button 
                v-if="!notification.is_read"
                type="text" 
                size="small"
                @click.stop="markAsRead(notification.id)"
              >
                标记已读
              </el-button>
              <el-button 
                type="text" 
                size="small"
                @click.stop="deleteNotification(notification.id)"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="notification-pagination" v-if="total > 0">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @current-change="loadNotifications"
            @size-change="loadNotifications"
          />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Bell, Warning, Clock, InfoFilled, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const showNotifications = ref(false)
const loading = ref(false)
const notifications = ref<any[]>([])
const unreadCount = ref(0)
const filterType = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 定时器
let refreshTimer: NodeJS.Timeout | null = null

// 计算属性
const getNotificationIcon = (type: string) => {
  const iconMap = {
    reminder: Clock,
    deadline: Warning,
    system: InfoFilled,
    completed: Check
  }
  return iconMap[type as keyof typeof iconMap] || InfoFilled
}

const getNotificationColor = (type: string) => {
  const colorMap = {
    reminder: '#409EFF',
    deadline: '#F56C6C',
    system: '#909399',
    completed: '#67C23A'
  }
  return colorMap[type as keyof typeof colorMap] || '#909399'
}

const getNotificationTagType = (type: string) => {
  const typeMap = {
    reminder: 'primary',
    deadline: 'danger',
    system: 'info',
    completed: 'success'
  }
  return typeMap[type as keyof typeof typeMap] || 'info'
}

const getNotificationTypeText = (type: string) => {
  const textMap = {
    reminder: '提醒',
    deadline: '截止',
    system: '系统',
    completed: '完成'
  }
  return textMap[type as keyof typeof textMap] || '通知'
}

// 方法
const loadNotifications = async () => {
  try {
    loading.value = true
    
    // 模拟API调用
    const mockNotifications = [
      {
        id: 1,
        type: 'deadline',
        title: '考核任务即将截止',
        message: '张三的考核任务将在2小时后截止，请及时完成评分。',
        is_read: false,
        created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString()
      },
      {
        id: 2,
        type: 'reminder',
        title: '考核提醒',
        message: '您有3个待完成的考核任务，请及时处理。',
        is_read: true,
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 3,
        type: 'completed',
        title: '考核完成',
        message: '李四的考核任务已完成，请查看结果。',
        is_read: false,
        created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
      }
    ]
    
    // 根据筛选条件过滤
    let filteredNotifications = mockNotifications
    if (filterType.value === 'unread') {
      filteredNotifications = mockNotifications.filter(n => !n.is_read)
    } else if (filterType.value !== 'all') {
      filteredNotifications = mockNotifications.filter(n => n.type === filterType.value)
    }
    
    notifications.value = filteredNotifications
    unreadCount.value = mockNotifications.filter(n => !n.is_read).length
    total.value = filteredNotifications.length
    
  } catch (error) {
    console.error('加载通知失败:', error)
    ElMessage.error('加载通知失败')
  } finally {
    loading.value = false
  }
}

const handleNotificationClick = (notification: any) => {
  if (!notification.is_read) {
    markAsRead(notification.id)
  }
  
  // 根据通知类型执行相应操作
  switch (notification.type) {
    case 'deadline':
    case 'reminder':
      // 跳转到任务页面
      console.log('跳转到任务页面')
      break
    case 'completed':
      // 跳转到结果页面
      console.log('跳转到结果页面')
      break
  }
}

const markAsRead = async (notificationId: number) => {
  try {
    // 模拟API调用
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
    
    ElMessage.success('已标记为已读')
  } catch (error) {
    console.error('标记已读失败:', error)
    ElMessage.error('操作失败')
  }
}

const deleteNotification = async (notificationId: number) => {
  try {
    // 模拟API调用
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index > -1) {
      const notification = notifications.value[index]
      notifications.value.splice(index, 1)
      
      if (!notification.is_read) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    }
    
    ElMessage.success('通知已删除')
  } catch (error) {
    console.error('删除通知失败:', error)
    ElMessage.error('删除失败')
  }
}

const formatTime = (dateTime: string) => {
  const date = new Date(dateTime)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  return date.toLocaleDateString('zh-CN')
}

// 定时刷新通知
const startRefreshTimer = () => {
  refreshTimer = setInterval(() => {
    loadNotifications()
  }, 30000) // 30秒刷新一次
}

const stopRefreshTimer = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生命周期
onMounted(() => {
  loadNotifications()
  startRefreshTimer()
})

onUnmounted(() => {
  stopRefreshTimer()
})
</script>

<style scoped>
.notification-center {
  position: relative;
}

.notification-badge {
  cursor: pointer;
}

.notification-trigger {
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.notification-trigger:hover {
  background-color: #f5f7fa;
}

.notification-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.notification-filters {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 16px;
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.3s;
  background: #ffffff;
}

.notification-item:hover {
  background: #f8f9fa;
  border-color: #409eff;
}

.notification-item.unread {
  background: #f0f9ff;
  border-color: #409eff;
}

.notification-icon {
  margin-right: 12px;
  margin-top: 2px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  font-size: 14px;
}

.notification-message {
  color: #606266;
  font-size: 13px;
  line-height: 1.4;
  margin-bottom: 8px;
}

.notification-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.notification-time {
  margin-right: 8px;
}

.notification-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-left: 8px;
  flex-shrink: 0;
}

.notification-pagination {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  margin-top: 16px;
}
</style>
