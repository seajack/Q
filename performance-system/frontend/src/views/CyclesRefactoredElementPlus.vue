<template>
  <div class="cycles-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">考核周期管理</h1>
        <div class="header-actions">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            创建周期
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ totalCycles }}</div>
              <div class="stat-label">总周期数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value active">{{ activeCycles }}</div>
              <div class="stat-label">进行中</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value completed">{{ completedCycles }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value draft">{{ draftCycles }}</div>
              <div class="stat-label">草稿</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :model="filters" inline>
        <el-form-item label="周期名称">
          <el-input 
            v-model="searchValue" 
            placeholder="搜索周期名称..." 
            clearable 
            @keyup.enter="handleSearch"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="selectedStatus" placeholder="选择状态" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="进行中" value="active" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>考核周期列表</span>
          <div class="header-actions">
            <el-button size="small" @click="handleExport">导出</el-button>
            <el-button size="small" @click="handleImport">导入</el-button>
          </div>
        </div>
      </template>

      <el-table 
        :data="filteredCycles" 
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="周期名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="120" align="center">
          <template #default="{ row }">
            <el-progress 
              :percentage="row.progress" 
              :color="getProgressColor(row.progress)"
              :show-text="false"
            />
            <span class="progress-text">{{ row.progress }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="时间范围" width="200">
          <template #default="{ row }">
            <div class="date-range">
              <div>{{ formatDate(row.start_date) }}</div>
              <div>至 {{ formatDate(row.end_date) }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="participants" label="参与人数" width="100" align="center">
          <template #default="{ row }">
            {{ row.participants || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="evaluation_rule_name" label="考核规则" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <el-button 
              size="small" 
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button 
              v-if="row.status === 'draft'"
              size="small" 
              type="success"
              @click="handleStart(row)"
            >
              启动
            </el-button>
            <el-button 
              v-if="row.status === 'active'"
              size="small" 
              type="warning"
              @click="handlePause(row)"
            >
              暂停
            </el-button>
            <el-button 
              size="small" 
              type="info"
              @click="handleDetail(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { cycleApi } from '../utils/api'

const router = useRouter()

// 响应式数据
const cycles = ref([])
const loading = ref(false)
const searchValue = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const totalCycles = computed(() => cycles.value.length)
const activeCycles = computed(() => cycles.value.filter(cycle => cycle.status === 'active').length)
const completedCycles = computed(() => cycles.value.filter(cycle => cycle.status === 'completed').length)
const draftCycles = computed(() => cycles.value.filter(cycle => cycle.status === 'draft').length)

const filteredCycles = computed(() => {
  let filtered = cycles.value
  
  // 搜索过滤
  if (searchValue.value) {
    const search = searchValue.value.toLowerCase()
    filtered = filtered.filter(cycle => 
      cycle.name.toLowerCase().includes(search) ||
      cycle.description.toLowerCase().includes(search)
    )
  }
  
  // 状态过滤
  if (selectedStatus.value) {
    filtered = filtered.filter(cycle => cycle.status === selectedStatus.value)
  }
  
  return filtered
})

const total = computed(() => filteredCycles.value.length)

// 方法
const loadCycles = async () => {
  try {
    loading.value = true
    const response = await cycleApi.list()
    cycles.value = response.data.results || []
  } catch (error) {
    console.error('加载考核周期失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 搜索逻辑已在计算属性中处理
}

const handleReset = () => {
  searchValue.value = ''
  selectedStatus.value = ''
}

const handleCreate = () => {
  router.push('/cycles/create')
}

const handleEdit = (cycle: any) => {
  router.push(`/cycles/${cycle.id}/edit`)
}

const handleStart = async (cycle: any) => {
  try {
    await ElMessageBox.confirm('确认启动此考核周期？', '确认操作', {
      type: 'warning'
    })
    await cycleApi.start(cycle.id)
    ElMessage.success('考核周期已启动')
    loadCycles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('启动失败')
    }
  }
}

const handlePause = async (cycle: any) => {
  try {
    await ElMessageBox.confirm('确认暂停此考核周期？', '确认操作', {
      type: 'warning'
    })
    await cycleApi.pause(cycle.id)
    ElMessage.success('考核周期已暂停')
    loadCycles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('暂停失败')
    }
  }
}

const handleDetail = (cycle: any) => {
  router.push(`/cycles/${cycle.id}`)
}

const handleExport = () => {
  console.log('导出考核周期数据')
  ElMessage.success('导出功能开发中')
}

const handleImport = () => {
  console.log('导入考核周期数据')
  ElMessage.success('导入功能开发中')
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

// 工具方法
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'draft': '草稿',
    'active': '进行中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    'draft': 'info',
    'active': 'success',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return typeMap[status] || 'default'
}

const getProgressColor = (progress: number) => {
  if (progress < 30) return '#f56c6c'
  if (progress < 70) return '#e6a23c'
  return '#67c23a'
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadCycles()
})
</script>

<style scoped>
.cycles-page {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-value.active {
  color: #67c23a;
}

.stat-value.completed {
  color: #67c23a;
}

.stat-value.draft {
  color: #e6a23c;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.date-range {
  font-size: 12px;
  line-height: 1.4;
}

.progress-text {
  font-size: 12px;
  color: #666;
  margin-left: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
