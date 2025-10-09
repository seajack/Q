<template>
  <div class="topnav-layout">
    <header class="topbar">
      <div class="topbar-inner" style="max-width: 1200px; margin: 0 auto; padding: 0 16px;">
        <div class="brand">
          <svg class="logo" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-label="Logo" role="img">
            <defs>
              <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" :stop-color="brand400" />
                <stop offset="100%" :stop-color="brand600" />
              </linearGradient>
            </defs>
            <rect x="2" y="2" width="20" height="20" rx="6" fill="url(#g)" />
            <path d="M7 13l3-3 3 3 4-4" fill="none" :stroke="brand700" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <span>绩效考核系统</span>
        </div>
        <div class="toolbar desktop-only">
          <div class="search">
            <input v-model.trim="keyword" placeholder="搜索员工、部门、指标…" class="input" />
            <span class="icon">🔍</span>
          </div>
        </div>
        <div class="toolbar">
          <select v-model="period" class="select">
            <option>2025 Q3</option><option>2025 Q2</option><option>2025 Q1</option><option>2024 Q4</option>
          </select>
          <RouterLink class="btn" to="/tasks">筛选</RouterLink>
          <!-- 通知中心 -->
          <NotificationCenter />
          <!-- 引导式操作流程 -->
          <GuidedWorkflow ref="guidedWorkflowRef" />
          <button class="btn btn-secondary" @click="startGuidedTour" title="开始引导">
            <span>🎯</span>
            引导
          </button>
          <button class="btn btn-primary" @click="onCreate">新增评审</button>
          
          <!-- 用户菜单 -->
          <div class="user-menu-container">
            <el-dropdown trigger="click" @command="handleCommand">
              <div class="user-profile">
                <div class="avatar-display">
                  <div class="avatar-circle" v-if="!userInfo.avatar">
                    {{ userInfo.name ? userInfo.name.charAt(0).toUpperCase() : 'U' }}
                  </div>
                  <img v-else :src="userInfo.avatar" alt="头像" class="avatar-image" style="display: block !important; visibility: visible !important; opacity: 1 !important; width: 28px !important; height: 28px !important; border-radius: 50% !important; border: 2px solid #e5e7eb !important;" />
                </div>
                <div class="user-info">
                  <div class="username">{{ userInfo.name }}</div>
                  <div class="role">{{ userInfo.role }}</div>
                </div>
                <i class="el-icon-caret-bottom"></i>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                  <el-dropdown-item command="settings">账号设置</el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
      <nav class="mainnav">
        <div class="mainnav-inner" style="max-width: 1200px; margin: 0 auto; padding: 0 16px;">
          <RouterLink class="link" to="/dashboard-new">首页</RouterLink>
          <RouterLink class="link" to="/dashboard-new">考核看板</RouterLink>
          <RouterLink class="link" to="/cycles">考核周期</RouterLink>
          <RouterLink class="link" to="/indicators">考核指标</RouterLink>
          <RouterLink class="link" to="/rules">考核规则</RouterLink>
          <RouterLink class="link" to="/multidimensional-evaluation">多维度评估</RouterLink>
          <RouterLink class="link" to="/evaluation-dimensions">评估维度</RouterLink>
          <RouterLink class="link" to="/tasks">考核任务</RouterLink>
          <RouterLink class="link" to="/manual-assignments">手动分配</RouterLink>
          <RouterLink class="link" to="/manual-evaluation">手动分配评分</RouterLink>
          <RouterLink class="link" to="/position-weights">职级权重配置</RouterLink>
          <RouterLink class="link" to="/employees">员工档案</RouterLink>
          <RouterLink class="link" to="/organization">组织架构</RouterLink>
          <RouterLink class="link" to="/results">报表中心</RouterLink>
          <RouterLink class="link" to="/settings">系统设置</RouterLink>
        </div>
      </nav>
    </header>

    <main style="width: 100%; padding: 24px 200px; flex: 1; overflow-y: auto; overflow-x: hidden;">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import NotificationCenter from '@/components/NotificationCenter.vue'
import GuidedWorkflow from '@/components/GuidedWorkflow.vue'

const period = ref('2025 Q3')
const keyword = ref('')
const guidedWorkflowRef = ref()

// 用户信息状态
const userInfo = ref({
  username: 'Admin',
  name: '系统管理员',
  role: '系统管理员',
  avatar: ''
})

const onCreate = () => {
  // 新增评审功能：跳转到考核周期管理页面
  window.location.href = '/cycles'
}

// 加载用户信息
const loadUserInfo = () => {
  try {
    const user = localStorage.getItem('user')
    console.log('TopNavLayout加载用户信息，localStorage数据:', user)
    if (user) {
      const userData = JSON.parse(user)
      console.log('解析后的用户数据:', userData)
      userInfo.value = {
        username: userData.username || 'Admin',
        name: userData.name || '系统管理员',
        role: userData.role || '系统管理员',
        avatar: userData.avatar || ''
      }
      console.log('更新后的userInfo:', userInfo.value)
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// 用户菜单处理
const handleCommand = (command: string) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      window.location.href = '/login'
    }).catch(() => {})
  } else if (command === 'profile') {
    window.location.href = '/user-profile'
  } else if (command === 'settings') {
    window.location.href = '/user-settings'
  }
}

// 手动触发引导
const startGuidedTour = () => {
  if (guidedWorkflowRef.value) {
    guidedWorkflowRef.value.startGuidedTour()
  }
}

onMounted(() => {
  loadUserInfo()
  
  // 监听用户信息更新事件
  window.addEventListener('userInfoUpdated', (event: any) => {
    console.log('TopNavLayout收到用户信息更新事件:', event.detail)
    if (event.detail) {
      // 更新用户信息
      if (event.detail.avatar) {
        console.log('更新头像:', event.detail.avatar)
        userInfo.value.avatar = event.detail.avatar
      }
      if (event.detail.name) {
        userInfo.value.name = event.detail.name
      }
      if (event.detail.role) {
        userInfo.value.role = event.detail.role
      }
      if (event.detail.username) {
        userInfo.value.username = event.detail.username
      }
    }
    // 重新加载完整的用户信息
    loadUserInfo()
  })
})

const brand600 = computed(()=> getComputedStyle(document.documentElement).getPropertyValue('--brand-600').trim() || '#177fc1')
const brand400 = computed(()=> getComputedStyle(document.documentElement).getPropertyValue('--brand-400').trim() || '#59b6ea')
const brand700 = computed(()=> getComputedStyle(document.documentElement).getPropertyValue('--brand-700').trim() || '#115f96')
</script>

<style scoped>
.topnav-layout { 
  height: 100vh; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden;
}
.topbar { 
  position: sticky; 
  top: 0; 
  z-index: 40; 
  background: #fff; 
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.topbar-inner { height: 56px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.brand { display: flex; align-items: center; gap: 10px; font-weight: 700; color: #111; }
.brand .logo { height: 28px; width: 28px; }
.toolbar { display: flex; align-items: center; gap: 8px; }
.desktop-only { display: none; }
@media (min-width: 768px) { .desktop-only { display: flex; } }
.search { position: relative; }
.search .icon { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; }
.mainnav { 
  background: var(--brand-600); 
  color: #fff;
  flex-shrink: 0;
}
.mainnav-inner { height: 48px; display: flex; align-items: center; gap: 18px; overflow: auto; }
.link { color: #fff; text-decoration: none; font-size: 14px; white-space: nowrap; opacity: .95; }
.link.router-link-active { font-weight: 700; text-decoration: underline; }

/* 用户菜单样式 */
.user-menu-container {
  margin-left: 12px;
  padding-left: 12px;
  border-left: 1px solid #e2e8f0;
}

.user-profile {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.user-profile:hover {
  background-color: #f5f5f5;
}

.avatar-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 12px;
  margin-right: 8px;
}

.avatar-display {
  display: flex;
  align-items: center;
  margin-right: 8px;
}

.avatar-image {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e5e7eb;
  display: block;
  visibility: visible;
  opacity: 1;
}

.user-info {
  margin-right: 8px;
}

.username {
  font-size: 13px;
  font-weight: 500;
  color: #262626;
  line-height: 1.2;
}

.role {
  font-size: 11px;
  color: #8c8c8c;
  line-height: 1.2;
}
</style>
