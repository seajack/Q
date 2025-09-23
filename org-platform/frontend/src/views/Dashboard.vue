<template>
  <div class="dashboard">
    <!-- 导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <h1 class="title">组织架构中台管理系统</h1>
        <el-menu mode="horizontal" :default-active="activeMenu" class="nav-menu" router>
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <span>仪表板</span>
          </el-menu-item>
          <el-menu-item index="/departments">
            <el-icon><OfficeBuilding /></el-icon>
            <span>部门管理</span>
          </el-menu-item>
          <el-menu-item index="/positions">
            <el-icon><UserFilled /></el-icon>
            <span>职位管理</span>
          </el-menu-item>
          <el-menu-item index="/employees">
            <el-icon><User /></el-icon>
            <span>员工管理</span>
          </el-menu-item>
          <el-menu-item index="/organization-tree">
            <el-icon><Grid /></el-icon>
            <span>组织架构</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-container class="main-container">
      <el-main class="main-content">
        <!-- 统计卡片 -->
        <el-row :gutter="20" class="stats-row">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-icon departments">
                  <el-icon><OfficeBuilding /></el-icon>
                </div>
                <div class="stat-info">
                  <h3>{{ stats?.active_departments || 0 }}</h3>
                  <p>活跃部门</p>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-icon positions">
                  <el-icon><UserFilled /></el-icon>
                </div>
                <div class="stat-info">
                  <h3>{{ stats?.active_positions || 0 }}</h3>
                  <p>活跃职位</p>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-icon employees">
                  <el-icon><User /></el-icon>
                </div>
                <div class="stat-info">
                  <h3>{{ stats?.active_employees || 0 }}</h3>
                  <p>在职员工</p>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-icon total">
                  <el-icon><Grid /></el-icon>
                </div>
                <div class="stat-info">
                  <h3>{{ (stats?.active_departments || 0) + (stats?.active_positions || 0) }}</h3>
                  <p>组织单元</p>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 部门层级分布图表 -->
        <el-row :gutter="20" class="chart-row">
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>部门层级分布</span>
                </div>
              </template>
              <div class="chart-content">
                <div v-for="level in stats?.department_levels" :key="level.level" class="level-item">
                  <span class="level-name">第 {{ level.level }} 层</span>
                  <el-progress 
                    :percentage="(level.count / (stats?.active_departments || 1)) * 100"
                    :format="() => `${level.count}个`"
                  />
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>职位级别分布</span>
                </div>
              </template>
              <div class="chart-content">
                <div v-for="level in stats?.position_levels" :key="level.level" class="level-item">
                  <span class="level-name">级别 {{ level.level }}</span>
                  <el-progress 
                    :percentage="(level.count / (stats?.active_positions || 1)) * 100"
                    :format="() => `${level.count}个`"
                    color="#67C23A"
                  />
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 快速操作 -->
        <el-row class="action-row">
          <el-col :span="24">
            <el-card class="action-card">
              <template #header>
                <div class="card-header">
                  <span>快速操作</span>
                </div>
              </template>
              <div class="action-buttons">
                <el-button type="primary" size="large" @click="$router.push('/departments')">
                  <el-icon><Plus /></el-icon>
                  新建部门
                </el-button>
                <el-button type="success" size="large" @click="$router.push('/positions')">
                  <el-icon><Plus /></el-icon>
                  新建职位
                </el-button>
                <el-button type="info" size="large" @click="$router.push('/employees')">
                  <el-icon><Plus /></el-icon>
                  新建员工
                </el-button>
                <el-button type="warning" size="large" @click="$router.push('/organization-tree')">
                  <el-icon><View /></el-icon>
                  查看组织架构
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useOrganizationStore } from '@/stores/organization'
import { 
  House, 
  OfficeBuilding, 
  UserFilled, 
  User, 
  Grid, 
  Plus, 
  View 
} from '@element-plus/icons-vue'

const route = useRoute()
const organizationStore = useOrganizationStore()

const activeMenu = computed(() => route.path)
const stats = computed(() => organizationStore.stats)

onMounted(async () => {
  try {
    await organizationStore.fetchStats()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.title {
  color: #303133;
  font-size: 20px;
  margin: 0;
}

.nav-menu {
  background: none;
  border: none;
}

.main-container {
  background: none;
}

.main-content {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.stat-icon.departments {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.positions {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.employees {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-icon .el-icon {
  font-size: 24px;
}

.stat-info h3 {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
  color: #303133;
}

.stat-info p {
  font-size: 14px;
  color: #909399;
  margin: 5px 0 0 0;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  min-height: 300px;
}

.card-header {
  font-weight: bold;
  color: #303133;
}

.chart-content {
  padding: 20px 0;
}

.level-item {
  margin-bottom: 20px;
}

.level-name {
  display: inline-block;
  width: 80px;
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.action-card {
  text-align: center;
}

.action-buttons {
  padding: 20px 0;
}

.action-buttons .el-button {
  margin: 0 10px;
}
</style>