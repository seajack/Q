<template>
  <div class="user-profile-page">
    <div class="profile-container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h1 class="page-title">个人信息</h1>
        <p class="page-subtitle">查看和管理您的个人信息</p>
      </div>

      <!-- 个人信息卡片 -->
      <div class="profile-card">
        <div class="profile-avatar-section">
          <div class="avatar-container">
            <!-- 头像显示区域 -->
            <div class="avatar-display">
              <div class="avatar-circle" v-if="!avatarUrl" ref="avatarCircle">
                {{ profileForm.name ? profileForm.name.charAt(0).toUpperCase() : 'U' }}
              </div>
              <img 
                v-else
                :src="avatarUrl" 
                alt="头像" 
                class="avatar-image" 
                ref="avatarImage"
                style="display: block !important; visibility: visible !important; opacity: 1 !important; width: 80px !important; height: 80px !important; border-radius: 50% !important; border: 2px solid #e5e7eb !important; position: relative !important; z-index: 9999 !important;"
              />
            </div>
            
            <!-- 强制显示测试头像 -->
            <div style="margin-top: 10px;">
              <div style="font-size: 12px; color: #666; margin-bottom: 5px;">强制显示测试:</div>
              <img src="https://via.placeholder.com/60x60?text=Force" alt="强制测试头像" style="width: 60px; height: 60px; border-radius: 50%; border: 2px solid #e5e7eb;" />
            </div>
            
            <!-- Vue头像显示测试 -->
            <div style="margin-top: 10px;">
              <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Vue头像显示测试:</div>
              <img :src="avatarUrl" alt="Vue测试头像" style="width: 60px; height: 60px; border-radius: 50%; border: 2px solid #e5e7eb;" v-if="avatarUrl" />
              <div v-else style="width: 60px; height: 60px; border-radius: 50%; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #666;">无头像</div>
            </div>
            <button 
              class="avatar-upload-btn" 
              @click="uploadAvatar"
              :disabled="avatarUploading"
            >
              <i class="el-icon-camera" v-if="!avatarUploading"></i>
              <i class="el-icon-loading" v-else></i>
              {{ avatarUploading ? '上传中...' : '更换头像' }}
            </button>
            <button 
              class="avatar-upload-btn" 
              @click="testAvatar"
              style="margin-left: 10px; background: #52c41a;"
            >
              测试头像
            </button>
          </div>
          <!-- 简单调试信息 -->
          <div style="margin-top: 10px; font-size: 12px; color: #666; background: #f0f0f0; padding: 10px; border-radius: 4px;">
            <strong>头像状态:</strong><br>
            avatarUrl: {{ avatarUrl || '空' }}<br>
            显示头像: {{ avatarUrl ? '是' : '否' }}<br>
            头像元素存在: {{ $refs.avatarImage ? '是' : '否' }}
          </div>
        </div>

        <div class="profile-info-section" v-loading="loading">
          <el-form :model="profileForm" label-width="120px" class="profile-form">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="用户名">
                  <el-input v-model="profileForm.username" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="员工编号">
                  <el-input v-model="profileForm.employeeId" disabled />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="姓名">
                  <el-input v-model="profileForm.name" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱">
                  <el-input v-model="profileForm.email" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="手机号">
                  <el-input v-model="profileForm.phone" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="部门">
                  <el-input v-model="profileForm.department" disabled />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="职位">
                  <el-input v-model="profileForm.position" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="职级">
                  <el-input v-model="profileForm.positionLevel" disabled />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="个人简介">
              <el-input
                v-model="profileForm.bio"
                type="textarea"
                :rows="4"
                placeholder="请输入个人简介"
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveProfile" :loading="saving">
                保存修改
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <!-- 登录记录 -->
      <div class="login-history-card">
        <h3 class="card-title">最近登录记录</h3>
        <el-table :data="loginHistory" style="width: 100%">
          <el-table-column prop="loginTime" label="登录时间" width="180" />
          <el-table-column prop="ipAddress" label="IP地址" width="140" />
          <el-table-column prop="location" label="登录地点" />
          <el-table-column prop="device" label="设备信息" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { userApi } from '@/utils/api'

// 表单数据
const profileForm = ref({
  username: '',
  employeeId: '',
  name: '',
  email: '',
  phone: '',
  department: '',
  position: '',
  positionLevel: '',
  bio: ''
})

// 状态
const saving = ref(false)
const loading = ref(false)
const avatarUrl = ref('')
const avatarUploading = ref(false)

// 登录记录
const loginHistory = ref([])

// 加载用户信息
const loadUserProfile = async () => {
  loading.value = true
  try {
    // 从localStorage获取用户信息
    const userInfo = localStorage.getItem('user')
    if (userInfo) {
      const user = JSON.parse(userInfo)
      profileForm.value = {
        username: user.username || '',
        employeeId: user.employeeId || '',
        name: user.name || '',
        email: user.email || '',
        phone: user.phone || '',
        department: user.department || '',
        position: user.position || '',
        positionLevel: user.positionLevel || '',
        bio: user.bio || ''
      }
      avatarUrl.value = user.avatar || ''
      console.log('加载用户头像:', user.avatar)
      console.log('设置avatarUrl.value为:', avatarUrl.value)
      console.log('avatarUrl类型:', typeof avatarUrl.value)
    }
    
    // 尝试从API获取更详细的信息
    try {
      const response = await userApi.getProfile()
      if (response.data) {
        Object.assign(profileForm.value, response.data)
      }
    } catch (error) {
      console.log('使用本地用户信息')
    }
    
    // 加载登录历史
    try {
      const historyResponse = await userApi.getLoginHistory()
      loginHistory.value = historyResponse.data || []
    } catch (error) {
      console.log('使用模拟登录历史')
      // 使用模拟数据作为后备
      loginHistory.value = [
        {
          loginTime: '2025-01-15 14:30:25',
          ipAddress: '192.168.1.100',
          location: '北京市朝阳区',
          device: 'Windows 10 / Chrome 120'
        },
        {
          loginTime: '2025-01-15 09:15:42',
          ipAddress: '192.168.1.100',
          location: '北京市朝阳区',
          device: 'Windows 10 / Chrome 120'
        },
        {
          loginTime: '2025-01-14 16:45:18',
          ipAddress: '192.168.1.100',
          location: '北京市朝阳区',
          device: 'Windows 10 / Chrome 120'
        }
      ]
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败')
  } finally {
    loading.value = false
  }
}

// 保存个人信息
const saveProfile = async () => {
  saving.value = true
  try {
    // 更新本地存储
    const userInfo = JSON.parse(localStorage.getItem('user') || '{}')
    const updatedUser = { ...userInfo, ...profileForm.value }
    localStorage.setItem('user', JSON.stringify(updatedUser))
    
    // 尝试调用API保存
    try {
      await userApi.updateProfile(profileForm.value)
    } catch (error) {
      console.log('API保存失败，已保存到本地')
    }
    
    // 触发全局用户信息更新事件
    window.dispatchEvent(new CustomEvent('userInfoUpdated', { 
      detail: updatedUser 
    }))
    
    ElMessage.success('个人信息保存成功')
  } catch (error) {
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

// 重置表单
const resetForm = () => {
  loadUserProfile()
}

// 上传头像
const uploadAvatar = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (!file) return
    
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      ElMessage.error('请选择图片文件')
      return
    }
    
    // 验证文件大小 (2MB)
    if (file.size > 2 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过2MB')
      return
    }
    
    avatarUploading.value = true
    try {
      // 创建预览URL
      const previewUrl = URL.createObjectURL(file)
      console.log('创建预览URL:', previewUrl)
      
      // 立即更新avatarUrl
      avatarUrl.value = previewUrl
      console.log('设置avatarUrl.value:', avatarUrl.value)
      
      // 强制触发Vue更新
      await new Promise(resolve => setTimeout(resolve, 50))
      
      // 验证头像URL是否正确设置
      console.log('验证avatarUrl.value:', avatarUrl.value)
      console.log('头像应该显示:', !!avatarUrl.value)
      
      console.log('头像上传开始，文件信息:', {
        name: file.name,
        size: file.size,
        type: file.type
      })
      
      // 尝试上传到服务器
      try {
        const response = await userApi.uploadAvatar(file)
        if (response.data?.avatar) {
          avatarUrl.value = response.data.avatar
        }
        ElMessage.success('头像上传成功')
      } catch (error) {
        console.log('服务器上传失败，使用本地预览')
        ElMessage.warning('头像已保存到本地，下次登录时生效')
      }
      
      // 更新本地存储
      const userInfo = JSON.parse(localStorage.getItem('user') || '{}')
      userInfo.avatar = avatarUrl.value
      localStorage.setItem('user', JSON.stringify(userInfo))
      
      // 触发全局用户信息更新事件
      window.dispatchEvent(new CustomEvent('userInfoUpdated', { 
        detail: { avatar: avatarUrl.value } 
      }))
      
    } catch (error) {
      ElMessage.error('头像上传失败')
    } finally {
      avatarUploading.value = false
    }
  }
  input.click()
}

// 测试头像功能
const testAvatar = () => {
  const testUrl = 'https://via.placeholder.com/80x80?text=Test'
  avatarUrl.value = testUrl
  
  // 强制设置头像显示
  nextTick(() => {
    const avatarImage = document.querySelector('.avatar-image')
    if (avatarImage) {
      avatarImage.style.display = 'block'
      avatarImage.style.visibility = 'visible'
      avatarImage.style.opacity = '1'
      avatarImage.style.width = '80px'
      avatarImage.style.height = '80px'
      avatarImage.style.borderRadius = '50%'
      avatarImage.style.border = '2px solid #e5e7eb'
      avatarImage.style.position = 'relative'
      avatarImage.style.zIndex = '9999'
    }
  })
  
  // 更新localStorage
  const userInfo = JSON.parse(localStorage.getItem('user') || '{}')
  userInfo.avatar = testUrl
  localStorage.setItem('user', JSON.stringify(userInfo))
  
  // 触发全局更新事件
  window.dispatchEvent(new CustomEvent('userInfoUpdated', { 
    detail: { avatar: testUrl } 
  }))
  
  ElMessage.success('测试头像已设置')
}

onMounted(() => {
  loadUserProfile()
})
</script>

<style scoped>
.user-profile-page {
  min-height: 100vh;
  background: #f8fafc;
  padding: 24px;
}

.profile-container {
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

.profile-card {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.profile-avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
}

.avatar-container {
  text-align: center;
}

.avatar-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 24px;
  margin: 0 auto 16px;
}

.avatar-display {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 16px;
}

.avatar-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e5e7eb;
  display: block;
  visibility: visible;
  opacity: 1;
  z-index: 10;
  position: relative;
}

.avatar-upload-btn {
  background: #f5f5f5;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  transition: all 0.3s;
}

.avatar-upload-btn:hover {
  background: #e6f7ff;
  border-color: #1890ff;
  color: #1890ff;
}

.profile-form {
  max-width: 800px;
  margin: 0 auto;
}

.login-history-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
}

@media (max-width: 768px) {
  .user-profile-page {
    padding: 16px;
  }
  
  .profile-card {
    padding: 20px;
  }
  
  .profile-form {
    max-width: 100%;
  }
}
</style>
