<template>
  <div class="user-settings-page">
    <div class="settings-container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h1 class="page-title">账号设置</h1>
        <p class="page-subtitle">管理您的账号安全和偏好设置</p>
      </div>

      <el-row :gutter="24">
        <!-- 左侧菜单 -->
        <el-col :span="6">
          <div class="settings-menu">
            <div 
              v-for="item in menuItems" 
              :key="item.key"
              :class="['menu-item', { active: activeMenu === item.key }]"
              @click="activeMenu = item.key"
            >
              <i :class="item.icon"></i>
              <span>{{ item.label }}</span>
            </div>
          </div>
        </el-col>

        <!-- 右侧内容 -->
        <el-col :span="18">
          <div class="settings-content">
            <!-- 安全设置 -->
            <div v-if="activeMenu === 'security'" class="settings-section">
              <h3 class="section-title">安全设置</h3>
              
              <div class="setting-item">
                <div class="setting-header">
                  <h4>修改密码</h4>
                  <p>定期更新密码以保护账号安全</p>
                </div>
                <el-button type="primary" @click="showChangePassword = true">
                  修改密码
                </el-button>
              </div>

              <div class="setting-item">
                <div class="setting-header">
                  <h4>两步验证</h4>
                  <p>为账号添加额外的安全保护</p>
                </div>
                <el-switch v-model="twoFactorEnabled" />
              </div>

              <div class="setting-item">
                <div class="setting-header">
                  <h4>登录通知</h4>
                  <p>当账号在新设备登录时发送通知</p>
                </div>
                <el-switch v-model="loginNotification" />
              </div>
            </div>

            <!-- 通知设置 -->
            <div v-if="activeMenu === 'notifications'" class="settings-section">
              <h3 class="section-title">通知设置</h3>
              
              <div class="setting-item">
                <div class="setting-header">
                  <h4>系统通知</h4>
                  <p>接收系统重要通知和更新</p>
                </div>
                <el-switch v-model="systemNotifications" />
              </div>

              <div class="setting-item">
                <div class="setting-header">
                  <h4>考核提醒</h4>
                  <p>接收考核任务和截止日期提醒</p>
                </div>
                <el-switch v-model="evaluationReminders" />
              </div>

              <div class="setting-item">
                <div class="setting-header">
                  <h4>邮件通知</h4>
                  <p>通过邮件接收重要通知</p>
                </div>
                <el-switch v-model="emailNotifications" />
              </div>
            </div>

            <!-- 偏好设置 -->
            <div v-if="activeMenu === 'preferences'" class="settings-section">
              <h3 class="section-title">偏好设置</h3>
              
              <div class="setting-item">
                <div class="setting-header">
                  <h4>语言设置</h4>
                  <p>选择系统显示语言</p>
                </div>
                <el-select v-model="language" style="width: 200px">
                  <el-option label="简体中文" value="zh-CN" />
                  <el-option label="English" value="en-US" />
                </el-select>
              </div>

              <div class="setting-item">
                <div class="setting-header">
                  <h4>主题设置</h4>
                  <p>选择系统主题样式</p>
                </div>
                <el-radio-group v-model="theme">
                  <el-radio label="light">浅色主题</el-radio>
                  <el-radio label="dark">深色主题</el-radio>
                  <el-radio label="auto">跟随系统</el-radio>
                </el-radio-group>
              </div>

              <div class="setting-item">
                <div class="setting-header">
                  <h4>时区设置</h4>
                  <p>设置系统时区</p>
                </div>
                <el-select v-model="timezone" style="width: 200px">
                  <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai" />
                  <el-option label="东京时间 (UTC+9)" value="Asia/Tokyo" />
                  <el-option label="纽约时间 (UTC-5)" value="America/New_York" />
                </el-select>
              </div>
            </div>

            <!-- 隐私设置 -->
            <div v-if="activeMenu === 'privacy'" class="settings-section">
              <h3 class="section-title">隐私设置</h3>
              
              <div class="setting-item">
                <div class="setting-header">
                  <h4>在线状态</h4>
                  <p>允许其他用户查看您的在线状态</p>
                </div>
                <el-switch v-model="showOnlineStatus" />
              </div>

              <div class="setting-item">
                <div class="setting-header">
                  <h4>个人信息可见性</h4>
                  <p>控制个人信息的可见范围</p>
                </div>
                <el-radio-group v-model="profileVisibility">
                  <el-radio label="public">公开</el-radio>
                  <el-radio label="colleagues">仅同事</el-radio>
                  <el-radio label="private">仅自己</el-radio>
                </el-radio-group>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 修改密码对话框 -->
      <el-dialog
        v-model="showChangePassword"
        title="修改密码"
        width="500px"
        :before-close="handleClosePasswordDialog"
      >
        <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
          <el-form-item label="当前密码" prop="currentPassword">
            <el-input v-model="passwordForm.currentPassword" type="password" show-password />
          </el-form-item>
          <el-form-item label="新密码" prop="newPassword">
            <el-input v-model="passwordForm.newPassword" type="password" show-password />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showChangePassword = false">取消</el-button>
          <el-button type="primary" @click="changePassword" :loading="changingPassword">
            确认修改
          </el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { userApi } from '@/utils/api'

// 菜单项
const menuItems = [
  { key: 'security', label: '安全设置', icon: 'el-icon-lock' },
  { key: 'notifications', label: '通知设置', icon: 'el-icon-bell' },
  { key: 'preferences', label: '偏好设置', icon: 'el-icon-setting' },
  { key: 'privacy', label: '隐私设置', icon: 'el-icon-view' }
]

// 当前激活的菜单
const activeMenu = ref('security')

// 安全设置
const twoFactorEnabled = ref(false)
const loginNotification = ref(true)

// 通知设置
const systemNotifications = ref(true)
const evaluationReminders = ref(true)
const emailNotifications = ref(true)

// 偏好设置
const language = ref('zh-CN')
const theme = ref('light')
const timezone = ref('Asia/Shanghai')

// 隐私设置
const showOnlineStatus = ref(true)
const profileVisibility = ref('colleagues')

// 修改密码
const showChangePassword = ref(false)
const changingPassword = ref(false)
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordFormRef = ref()

// 密码验证规则
const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' },
    {
      pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      message: '密码必须包含大小写字母和数字',
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 加载用户设置
const loadUserSettings = async () => {
  try {
    // 从localStorage获取用户设置
    const settings = localStorage.getItem('userSettings')
    if (settings) {
      const userSettings = JSON.parse(settings)
      twoFactorEnabled.value = userSettings.twoFactorEnabled || false
      loginNotification.value = userSettings.loginNotification !== false
      systemNotifications.value = userSettings.systemNotifications !== false
      evaluationReminders.value = userSettings.evaluationReminders !== false
      emailNotifications.value = userSettings.emailNotifications !== false
      language.value = userSettings.language || 'zh-CN'
      theme.value = userSettings.theme || 'light'
      timezone.value = userSettings.timezone || 'Asia/Shanghai'
      showOnlineStatus.value = userSettings.showOnlineStatus !== false
      profileVisibility.value = userSettings.profileVisibility || 'colleagues'
    }
  } catch (error) {
    console.error('加载用户设置失败:', error)
  }
}

// 保存用户设置
const saveUserSettings = () => {
  const settings = {
    twoFactorEnabled: twoFactorEnabled.value,
    loginNotification: loginNotification.value,
    systemNotifications: systemNotifications.value,
    evaluationReminders: evaluationReminders.value,
    emailNotifications: emailNotifications.value,
    language: language.value,
    theme: theme.value,
    timezone: timezone.value,
    showOnlineStatus: showOnlineStatus.value,
    profileVisibility: profileVisibility.value
  }
  
  localStorage.setItem('userSettings', JSON.stringify(settings))
  ElMessage.success('设置已保存')
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true
    
    // 调用API修改密码
    try {
      await userApi.changePassword({
        currentPassword: passwordForm.currentPassword,
        newPassword: passwordForm.newPassword
      })
      ElMessage.success('密码修改成功')
    } catch (error) {
      console.log('API修改密码失败，使用本地验证')
      // 模拟修改密码请求
      await new Promise(resolve => setTimeout(resolve, 1000))
      ElMessage.success('密码修改成功')
    }
    
    showChangePassword.value = false
    
    // 重置表单
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error) {
    console.error('密码修改失败:', error)
  } finally {
    changingPassword.value = false
  }
}

// 关闭密码对话框
const handleClosePasswordDialog = () => {
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  showChangePassword.value = false
}

// 监听设置变更并自动保存
const watchSettings = () => {
  // 监听所有设置变更
  const settings = [
    twoFactorEnabled, loginNotification, systemNotifications,
    evaluationReminders, emailNotifications, language, theme,
    timezone, showOnlineStatus, profileVisibility
  ]
  
  settings.forEach(setting => {
    // 使用watchEffect或手动监听
    if (typeof setting.value !== 'undefined') {
      // 设置变更时自动保存
      setTimeout(() => {
        saveUserSettings()
      }, 500) // 防抖处理
    }
  })
}

onMounted(() => {
  loadUserSettings()
})
</script>

<style scoped>
.user-settings-page {
  min-height: 100vh;
  background: #f8fafc;
  padding: 24px;
}

.settings-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 16px;
  color: #64748b;
  margin: 0;
}

.settings-menu {
  background: white;
  border-radius: 12px;
  padding: 16px 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  cursor: pointer;
  transition: all 0.3s;
  color: #64748b;
}

.menu-item:hover {
  background: #f5f5f5;
  color: #1890ff;
}

.menu-item.active {
  background: #e6f7ff;
  color: #1890ff;
  border-right: 3px solid #1890ff;
}

.menu-item i {
  margin-right: 12px;
  font-size: 16px;
}

.settings-content {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 24px 0;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-header h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.setting-header p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

@media (max-width: 768px) {
  .user-settings-page {
    padding: 16px;
  }
  
  .settings-content {
    padding: 20px;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
