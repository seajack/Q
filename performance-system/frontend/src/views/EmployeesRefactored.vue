<template>
  <AppLayout
    page-title="员工管理"
    page-subtitle="管理员工信息和考核权限"
    :show-search="true"
    search-placeholder="搜索员工..."
    :filters="filters"
    :actions="headerActions"
    @search="handleSearch"
    @filter-change="handleFilterChange"
    @action-click="handleHeaderAction"
  >
    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="metric-card card p-4 text-center">
        <div class="text-2xl font-bold text-gray-900">{{ totalEmployees }}</div>
        <div class="text-sm text-gray-600">总员工数</div>
      </div>
      <div class="metric-card card p-4 text-center">
        <div class="text-2xl font-bold text-green-600">{{ activeEmployees }}</div>
        <div class="text-sm text-gray-600">在职员工</div>
      </div>
      <div class="metric-card card p-4 text-center">
        <div class="text-2xl font-bold text-blue-600">{{ managerCount }}</div>
        <div class="text-sm text-gray-600">管理人员</div>
      </div>
      <div class="metric-card card p-4 text-center">
        <div class="text-2xl font-bold text-purple-600">{{ departmentCount }}</div>
        <div class="text-sm text-gray-600">部门数量</div>
      </div>
    </div>
    
    <!-- 员工列表 -->
    <div class="card">
      <div class="p-6">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-gray-200">
                <th class="text-left py-3 px-4 font-medium text-gray-900">员工信息</th>
                <th class="text-left py-3 px-4 font-medium text-gray-900">部门</th>
                <th class="text-left py-3 px-4 font-medium text-gray-900">职位</th>
                <th class="text-left py-3 px-4 font-medium text-gray-900">职级</th>
                <th class="text-left py-3 px-4 font-medium text-gray-900">权重</th>
                <th class="text-left py-3 px-4 font-medium text-gray-900">状态</th>
                <th class="text-left py-3 px-4 font-medium text-gray-900">最近考核</th>
                <th class="text-left py-3 px-4 font-medium text-gray-900">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="employee in filteredEmployees" 
                :key="employee.employee_id"
                class="employee-row border-b border-gray-100 transition-colors"
              >
                <td class="py-4 px-4">
                  <div class="flex items-center">
                    <div class="w-10 h-10 rounded-full flex items-center justify-center mr-3" :class="getAvatarClass(employee.employee_id)">
                      <i class="fas fa-user text-sm"></i>
                    </div>
                    <div>
                      <div class="font-medium text-gray-900">{{ employee.name }}</div>
                      <div class="text-sm text-gray-600">{{ employee.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="py-4 px-4 text-gray-900">{{ employee.department_name }}</td>
                <td class="py-4 px-4 text-gray-900">{{ employee.position_name }}</td>
                <td class="py-4 px-4">
                  <span class="px-2 py-1 rounded-full text-xs font-medium" :class="getLevelClass(employee.position_level)">
                    {{ employee.position_level }}
                  </span>
                </td>
                <td class="py-4 px-4 font-medium text-gray-900">{{ getWeight(employee.position_level) }}</td>
                <td class="py-4 px-4">
                  <span class="status-badge px-2 py-1 rounded-full text-xs font-medium" :class="employee.is_active ? 'status-active' : 'status-pending'">
                    {{ employee.is_active ? '在职' : '离职' }}
                  </span>
                </td>
                <td class="py-4 px-4 text-gray-600">{{ getLastEvaluation(employee) }}</td>
                <td class="py-4 px-4">
                  <div class="flex space-x-2">
                    <button 
                      class="text-blue-600 hover:text-blue-800 text-sm"
                      @click="handleEdit(employee)"
                    >
                      编辑
                    </button>
                    <button 
                      class="text-green-600 hover:text-green-800 text-sm"
                      @click="handleEvaluate(employee)"
                    >
                      考核
                    </button>
                    <button 
                      class="text-gray-600 hover:text-gray-800 text-sm"
                      @click="handleDetail(employee)"
                    >
                      详情
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- 分页 -->
        <div class="flex items-center justify-between mt-6 pt-6 border-t border-gray-200">
          <div class="text-sm text-gray-600">
            显示 1-{{ Math.min(pageSize, filteredEmployees.length) }} 条，共 {{ total }} 条记录
          </div>
          <div class="flex space-x-2">
            <button 
              class="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
              @click="handlePageChange(currentPage - 1)"
              :disabled="currentPage <= 1"
            >
              上一页
            </button>
            <button 
              class="px-3 py-2 bg-blue-600 text-white rounded-lg text-sm"
              v-for="page in getPageNumbers()"
              :key="page"
              @click="handlePageChange(page)"
              :class="page === currentPage ? 'bg-blue-600' : 'border border-gray-300 hover:bg-gray-50'"
            >
              {{ page }}
            </button>
            <button 
              class="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
              @click="handlePageChange(currentPage + 1)"
              :disabled="currentPage >= Math.ceil(total / pageSize)"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppLayout from '../layouts/AppLayout.vue'
import DataTable from '../components/ui/DataTable.vue'
import MetricCard from '../components/ui/MetricCard.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'
import { useEvaluationStore } from '../stores/evaluation'

const router = useRouter()
const evaluationStore = useEvaluationStore()

// 响应式数据
const searchValue = ref('')
const selectedDepartment = ref('')
const selectedLevel = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 筛选器
const filters = ref([
  {
    key: 'department',
    placeholder: '全部部门',
    value: '',
    options: [
      { value: '', label: '全部部门' },
      { value: 'tech', label: '技术部' },
      { value: 'sales', label: '销售部' },
      { value: 'marketing', label: '市场部' },
      { value: 'hr', label: '人事部' },
      { value: 'finance', label: '财务部' }
    ]
  },
  {
    key: 'level',
    placeholder: '全部职级',
    value: '',
    options: [
      { value: '', label: '全部职级' },
      { value: 'high', label: '高层' },
      { value: 'middle', label: '中层' },
      { value: 'low', label: '基层' }
    ]
  }
])

// 头部操作按钮
const headerActions = ref([
  {
    key: 'sync',
    label: '从中台同步',
    icon: 'fas fa-sync-alt',
    type: 'secondary' as const
  },
  {
    key: 'add-employee',
    label: '添加员工',
    icon: 'fas fa-plus',
    type: 'primary' as const
  }
])

// 表格列配置
const tableColumns = ref([
  { key: 'employee', label: '员工信息', class: 'w-64' },
  { key: 'department', label: '部门', class: 'w-32' },
  { key: 'position', label: '职位', class: 'w-32' },
  { key: 'level', label: '职级', class: 'w-32' },
  { key: 'phone', label: '电话', class: 'w-32' },
  { key: 'status', label: '状态', class: 'w-24' },
  { key: 'actions', label: '操作', class: 'w-32' }
])

// 表格操作按钮
const tableActions = ref([
  {
    key: 'export',
    label: '导出',
    icon: 'fas fa-download',
    type: 'secondary' as const
  },
  {
    key: 'import',
    label: '导入',
    icon: 'fas fa-upload',
    type: 'secondary' as const
  }
])

// 计算属性
const employees = computed(() => evaluationStore.employees)
const loading = computed(() => evaluationStore.loading)

const totalEmployees = computed(() => employees.value?.length || 0)
const activeEmployees = computed(() => employees.value?.filter(emp => emp.is_active).length || 0)
const managerCount = computed(() => employees.value?.filter(emp => emp.position_level?.includes('经理') || emp.position_level?.includes('总监')).length || 0)
const departmentCount = computed(() => new Set(employees.value?.map(emp => emp.department_name)).size || 0)

const filteredEmployees = computed(() => {
  let filtered = employees.value || []
  
  // 搜索过滤
  if (searchValue.value) {
    const search = searchValue.value.toLowerCase()
    filtered = filtered.filter(emp => 
      emp.name.toLowerCase().includes(search) ||
      emp.email.toLowerCase().includes(search) ||
      emp.employee_id.toLowerCase().includes(search)
    )
  }
  
  // 部门过滤
  if (selectedDepartment.value) {
    filtered = filtered.filter(emp => emp.department_name === selectedDepartment.value)
  }
  
  // 职级过滤
  if (selectedLevel.value) {
    filtered = filtered.filter(emp => {
      const level = emp.position_level || ''
      switch (selectedLevel.value) {
        case 'high':
          return level.includes('总监') || level.includes('总经理')
        case 'middle':
          return level.includes('经理') || level.includes('主管')
        case 'low':
          return !level.includes('经理') && !level.includes('总监') && !level.includes('主管')
        default:
          return true
      }
    })
  }
  
  return filtered
})

const total = computed(() => filteredEmployees.value.length)

const getAvatarClass = (employeeId: string) => {
  const colors = [
    'bg-blue-100 text-blue-600',
    'bg-green-100 text-green-600',
    'bg-purple-100 text-purple-600',
    'bg-yellow-100 text-yellow-600',
    'bg-red-100 text-red-600',
    'bg-indigo-100 text-indigo-600'
  ]
  const index = employeeId.charCodeAt(0) % colors.length
  return colors[index]
}

const getLevelType = (level: string) => {
  if (!level) return 'default'
  
  if (level.includes('总监') || level.includes('总经理')) {
    return 'danger'
  } else if (level.includes('经理') || level.includes('主管')) {
    return 'warning'
  } else {
    return 'info'
  }
}

const getLevelClass = (level: string) => {
  if (!level) return 'level-low'
  
  if (level.includes('总监') || level.includes('总经理')) {
    return 'level-high'
  } else if (level.includes('经理') || level.includes('主管')) {
    return 'level-medium'
  } else {
    return 'level-low'
  }
}

const getWeight = (level: string) => {
  if (!level) return '1.0'
  
  if (level.includes('总监') || level.includes('总经理')) {
    return '1.8'
  } else if (level.includes('经理') || level.includes('主管')) {
    return '1.2'
  } else {
    return '1.0'
  }
}

const getLastEvaluation = (employee: any) => {
  // 模拟最近考核时间
  const dates = ['2024-09-28', '2024-09-25', '2024-09-20', '2024-09-15', '2024-08-30']
  const index = employee.employee_id.charCodeAt(0) % dates.length
  return dates[index]
}

const getPageNumbers = () => {
  const totalPages = Math.ceil(total.value / pageSize.value)
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages, start + 4)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
}

// 方法
const handleSearch = (value: string) => {
  searchValue.value = value
}

const handleFilterChange = (filter: any) => {
  if (filter.key === 'department') {
    selectedDepartment.value = filter.value
  } else if (filter.key === 'level') {
    selectedLevel.value = filter.value
  }
}

const handleHeaderAction = async (action: any) => {
  switch (action.key) {
    case 'sync':
      try {
        await evaluationStore.syncEmployees()
        ElMessage.success('员工数据同步成功')
      } catch (error) {
        ElMessage.error('同步失败，请重试')
      }
      break
    case 'add-employee':
      router.push('/employees/create')
      break
  }
}

const handleTableAction = (action: any) => {
  switch (action.key) {
    case 'export':
      console.log('导出员工数据')
      break
    case 'import':
      console.log('导入员工数据')
      break
  }
}

const handleEdit = (employee: any) => {
  router.push(`/employees/${employee.employee_id}/edit`)
}

const handleEvaluate = (employee: any) => {
  router.push(`/evaluation/${employee.employee_id}`)
}

const handleDetail = (employee: any) => {
  router.push(`/employees/${employee.employee_id}`)
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

// 生命周期
onMounted(() => {
  evaluationStore.loadEmployees()
})
</script>

<style scoped>
/* 自定义样式 */
</style>