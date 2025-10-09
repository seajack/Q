<template>
  <div class="container org-page">
    <div class="org-columns">
      <section class="org-card org-tree-card">
        <div class="panel-header">
          <div class="panel-title">
            <h3>组织树</h3>
            <p>点击节点查看成员</p>
          </div>
          <div class="panel-actions">
            <el-button type="primary" size="small" @click="clearSelection">
              <el-icon><View /></el-icon>
              查看全部
            </el-button>
            <el-button type="success" size="small" @click="refreshTree">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
        <div class="tree-wrapper" v-loading="treeLoading">
          <el-tree
            ref="treeRef"
            class="organization-tree"
            :data="treeData"
            :props="treeProps"
            node-key="id"
            default-expand-all
            highlight-current
            :expand-on-click-node="false"
            @node-click="handleNodeClick"
          >
            <template #default="{ data }">
              <div class="tree-node" :class="{ 'employee-node': data.type === 'employee' }">
                <div class="tree-node-main">
                  <span class="tree-node-name">{{ data.name }}</span>
                  <span v-if="data.type === 'department'" class="tree-node-count">{{ data.employee_count || 0 }} 人</span>
                  <span v-else-if="data.type === 'employee'" class="employee-info">
                    <span class="position-info">{{ data.position_name || '未分配' }}<span v-if="data.position_level" class="position-level"> L{{ data.position_level }}</span></span>
                  </span>
                </div>
                <p v-if="data.type === 'department' && data.children?.length" class="tree-node-meta">
                  子部门 {{ data.children.filter(child => child.type === 'department').length }}
                </p>
              </div>
            </template>
          </el-tree>
        </div>
      </section>

      <section class="org-card org-members-card">
        <div class="panel-header members-header">
          <div class="panel-title">
            <h3>{{ membersTitle }}</h3>
            <p>{{ membersSubtitle }}</p>
          </div>
          <div class="header-actions">
            <el-input
              v-model.trim="keyword"
              class="search-input"
              :prefix-icon="Search"
              placeholder="搜索姓名 / 邮箱 / 岗位"
              clearable
            />
            <el-select v-model="pageSize" class="page-size-select" size="small">
              <el-option
                v-for="size in pageSizeOptions"
                :key="size"
                :label="`${size} 条/页`"
                :value="size"
              />
            </el-select>
          </div>
        </div>

        <!-- 员工详情显示 -->
        <div v-if="selectedEmployee" class="employee-detail-panel">
          <!-- 员工头部信息 -->
          <div class="detail-header">
            <div class="detail-avatar" :style="{ backgroundColor: selectedEmployee._avatarColor }">
              {{ selectedEmployee._initials }}
            </div>
            <div class="detail-info">
              <h3 class="detail-name">{{ selectedEmployee.name }}</h3>
              <p class="detail-id">工号: {{ selectedEmployee.employee_id || '—' }}</p>
              <div class="detail-status">
                <el-tag :type="selectedEmployee._statusMeta.type" effect="light" size="small">
                  {{ selectedEmployee._statusMeta.label }}
                </el-tag>
              </div>
            </div>
            <div class="detail-actions-header">
              <el-button type="primary" size="small" @click="toggleEditMode">
                <el-icon><Edit /></el-icon>
                {{ isEditing ? '保存' : '编辑' }}
              </el-button>
              <el-button v-if="isEditing" size="small" @click="cancelEdit">
                <el-icon><Close /></el-icon>
                取消
              </el-button>
              <el-button size="small" @click="clearSelection">
                <el-icon><Back /></el-icon>
                返回
              </el-button>
            </div>
          </div>
          
          <!-- 员工详细信息 -->
          <div class="detail-content">
            <!-- 基本信息卡片 -->
            <div class="detail-card">
              <div class="card-header">
                <h4 class="card-title">
                  <el-icon><User /></el-icon>
                  基本信息
                </h4>
              </div>
              <div class="card-body">
                <div class="detail-grid">
                  <div class="detail-item">
                    <label>姓名</label>
                    <div v-if="!isEditing" class="detail-value">{{ selectedEmployee.name }}</div>
                    <el-input v-else v-model="editForm.name" size="small" />
                  </div>
                  <div class="detail-item">
                    <label>性别</label>
                    <div v-if="!isEditing" class="detail-value">{{ getGenderLabel(selectedEmployee.gender) }}</div>
                    <el-select v-else v-model="editForm.gender" size="small" style="width: 100%">
                      <el-option label="男" value="male" />
                      <el-option label="女" value="female" />
                    </el-select>
                  </div>
                  <div class="detail-item">
                    <label>出生日期</label>
                    <div v-if="!isEditing" class="detail-value">{{ formatDate(selectedEmployee.birth_date) }}</div>
                    <el-date-picker v-else v-model="editForm.birth_date" type="date" size="small" style="width: 100%" />
                  </div>
                  <div class="detail-item">
                    <label>手机号</label>
                    <div v-if="!isEditing" class="detail-value">{{ selectedEmployee.phone || '—' }}</div>
                    <el-input v-else v-model="editForm.phone" size="small" />
                  </div>
                  <div class="detail-item">
                    <label>邮箱</label>
                    <div v-if="!isEditing" class="detail-value">{{ selectedEmployee.email || '—' }}</div>
                    <el-input v-else v-model="editForm.email" size="small" />
                  </div>
                  <div class="detail-item full-width">
                    <label>地址</label>
                    <div v-if="!isEditing" class="detail-value">{{ selectedEmployee.address || '—' }}</div>
                    <el-input v-else v-model="editForm.address" type="textarea" :rows="2" size="small" />
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 职位信息卡片 -->
            <div class="detail-card">
              <div class="card-header">
                <h4 class="card-title">
                  <el-icon><Briefcase /></el-icon>
                  职位信息
                </h4>
              </div>
              <div class="card-body">
                <div class="detail-grid">
                  <div class="detail-item">
                    <label>部门</label>
                    <div v-if="!isEditing" class="detail-value">{{ selectedEmployee._departmentName }}</div>
                    <el-select v-else v-model="editForm.department_id" size="small" style="width: 100%">
                      <el-option 
                        v-for="dept in departments" 
                        :key="dept.id" 
                        :label="dept.name" 
                        :value="dept.id" 
                      />
                    </el-select>
                  </div>
                  <div class="detail-item">
                    <label>岗位</label>
                    <div v-if="!isEditing" class="detail-value">{{ selectedEmployee._positionName }}</div>
                    <el-select v-else v-model="editForm.position_id" size="small" style="width: 100%">
                      <el-option 
                        v-for="position in positions" 
                        :key="position.id" 
                        :label="position.name" 
                        :value="position.id" 
                      />
                    </el-select>
                  </div>
                  <div class="detail-item">
                    <label>职级</label>
                    <div v-if="!isEditing" class="detail-value">
                      <span class="level-pill" :class="getLevelClass(selectedEmployee._levelLabel)">
                        {{ selectedEmployee._levelLabel }}
                      </span>
                    </div>
                    <el-input v-else v-model="editForm.level" size="small" />
                  </div>
                  <div class="detail-item">
                    <label>直属上级</label>
                    <div v-if="!isEditing" class="detail-value">{{ selectedEmployee.supervisor_name || '—' }}</div>
                    <el-select v-else v-model="editForm.supervisor_id" size="small" style="width: 100%">
                      <el-option 
                        v-for="emp in allEmployees" 
                        :key="emp.id" 
                        :label="emp.name" 
                        :value="emp.id" 
                      />
                    </el-select>
                  </div>
                  <div class="detail-item">
                    <label>入职日期</label>
                    <div v-if="!isEditing" class="detail-value">{{ formatDate(selectedEmployee.hire_date) }}</div>
                    <el-date-picker v-else v-model="editForm.hire_date" type="date" size="small" style="width: 100%" />
                  </div>
                  <div class="detail-item">
                    <label>状态</label>
                    <div v-if="!isEditing" class="detail-value">
                      <el-tag :type="selectedEmployee._statusMeta.type" effect="light" size="small">
                        {{ selectedEmployee._statusMeta.label }}
                      </el-tag>
                    </div>
                    <el-select v-else v-model="editForm.status" size="small" style="width: 100%">
                      <el-option label="在职" value="active" />
                      <el-option label="离职" value="inactive" />
                      <el-option label="试用" value="probation" />
                    </el-select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 员工列表显示 -->
        <el-table
          v-else
          v-loading="membersLoading"
          :data="pagedMembers"
          class="members-table"
          header-row-class-name="members-table-header"
        >
          <el-table-column label="姓名" min-width="220">
            <template #default="{ row }">
              <div class="member-cell">
                <div class="member-avatar" :style="{ backgroundColor: row._avatarColor }">
                  {{ row._initials }}
                </div>
                <div class="member-meta">
                  <span class="member-name">{{ row._lastName }}</span>
                  <span class="member-mail">{{ row.email }}</span>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="部门" min-width="160">
            <template #default="{ row }">
              <span class="cell-text">{{ row._departmentName }}</span>
            </template>
          </el-table-column>

          <el-table-column label="岗位 / 职级" min-width="200">
            <template #default="{ row }">
              <div class="position-level-cell">
                <span class="cell-text">{{ row._positionName }}</span>
                <span class="level-pill" :class="getLevelClass(row._levelLabel)">{{ row._levelLabel }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row._statusMeta.type" effect="light" size="small">
                {{ row._statusMeta.label }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="160" align="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="showEmployeeDetail(row)">详情</el-button>
              <el-button type="primary" link size="small" @click="editEmployee(row)">编辑</el-button>
            </template>
          </el-table-column>

          <template #empty>
            <div class="empty-state">暂无成员数据</div>
          </template>
        </el-table>

        <div class="members-footer">
          <el-pagination
            background
            layout="prev, pager, next"
            :current-page="currentPage"
            :page-size="pageSize"
            :total="pageTotal"
            @current-change="handleCurrentPageChange"
          />
        </div>
      </section>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { ElDialog, ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, View, Edit, Close, Back, User, Briefcase } from '@element-plus/icons-vue'
import { useOrganizationStore } from '@/stores/organization'
import { useRouter } from 'vue-router'

interface TreeNodeItem {
  id: number | string
  name: string
  type?: 'department' | 'employee'
  employee_count?: number
  position_name?: string
  position_level?: number
  employee_id?: string
  status?: string
  children?: TreeNodeItem[]
}

const organizationStore = useOrganizationStore()
const { employees: employeesRef } = storeToRefs(organizationStore)
const router = useRouter()

// 员工选择相关
const selectedEmployee = ref<any>(null)

// 编辑模式相关
const isEditing = ref(false)
const editForm = ref({
  name: '',
  gender: '',
  birth_date: '',
  phone: '',
  email: '',
  address: '',
  department_id: null,
  position_id: null,
  level: '',
  supervisor_id: null,
  hire_date: '',
  status: ''
})

// 数据源
const departments = ref([])
const positions = ref([])
const allEmployees = ref([])

const treeData = ref<TreeNodeItem[]>([])
const treeLoading = ref(false)
const membersLoading = ref(false)
const treeRef = ref()

const treeProps = {
  children: 'children',
  label: 'name'
}

const selectedDeptId = ref<number | null>(null)
const selectedDeptName = ref('')
const keyword = ref('')
const pageSizeOptions = [10, 20, 50]
const pageSize = ref(pageSizeOptions[0])
const currentPage = ref(1)

const employees = computed(() => employeesRef.value ?? [])

const avatarPalette = ['#0f766e', '#2563eb', '#f97316', '#7c3aed', '#e11d48', '#0f172a', '#10b981', '#9333ea']

const statusMap: Record<string, { label: string; type: 'success' | 'info' | 'warning' | 'danger' | 'primary' } > = {
  active: { label: '在职', type: 'success' },
  leave: { label: '休假', type: 'warning' },
  resigned: { label: '离职', type: 'info' },
  retired: { label: '退休', type: 'info' },
  probation: { label: '试用', type: 'primary' },
  default: { label: '未知', type: 'info' }
}

const getInitials = (name: string) => {
  if (!name) return '—'
  const parts = name.trim().split(/\s+/)
  if (parts.length === 1) {
    return parts[0].slice(0, 1).toUpperCase()
  }
  return parts[0].slice(0, 1).toUpperCase()
}

const getLastName = (name: string) => {
  if (!name) return '—'
  const parts = name.trim().split(/\s+/)
  return parts[parts.length - 1]
}

const normalizedEmployees = computed(() => {
  return employees.value.map((emp, index) => {
    const levelLabel = emp.position_level_display || emp.position_name || '—'
    const statusMeta = statusMap[emp.status] || statusMap.default
    return {
      ...emp,
      _initials: getInitials(emp.name),
      _lastName: getLastName(emp.name),
      _avatarColor: avatarPalette[index % avatarPalette.length],
      _departmentName: emp.department_name || '—',
      _positionName: emp.position_name || '—',
      _levelLabel: levelLabel,
      _statusMeta: statusMeta
    }
  })
})

const filteredEmployees = computed(() => {
  let list = normalizedEmployees.value
  if (selectedDeptId.value !== null) {
    list = list.filter(emp => emp.department === selectedDeptId.value)
  }
  const keywordValue = keyword.value.trim().toLowerCase()
  if (keywordValue) {
    list = list.filter(emp => {
      const haystack = [emp.name, emp.email, emp._departmentName, emp._positionName]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
      return haystack.includes(keywordValue)
    })
  }
  return list
})

const pagedMembers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredEmployees.value.slice(start, start + pageSize.value)
})

const pageTotal = computed(() => filteredEmployees.value.length)

const membersTitle = computed(() => {
  if (selectedEmployee.value) {
    return '员工详情'
  }
  return selectedDeptName.value || '全部成员'
})
const membersSubtitle = computed(() => {
  if (selectedEmployee.value) {
    return selectedEmployee.value.name
  }
  return `共 ${pageTotal.value} 人`
})

const normalizeTree = (nodes: any[]): TreeNodeItem[] => {
  if (!Array.isArray(nodes)) return []
  return nodes
    .filter(item => item)
    .map(item => ({
      id: item.id,
      name: item.name,
      type: item.type,
      employee_count: item.employee_count ?? 0,
      position_name: item.position_name,
      position_level: item.position_level,
      employee_id: item.employee_id,
      status: item.status,
      children: normalizeTree(item.children || [])
    }))
}

const refreshTree = async () => {
  try {
    treeLoading.value = true
    const raw = await organizationStore.fetchFullOrganizationTree()
    const source = Array.isArray(raw?.data)
      ? raw.data
      : Array.isArray(raw?.results)
        ? raw.results
        : Array.isArray(raw)
          ? raw
          : []
    // 使用normalizeTree处理数据，包含员工节点
    treeData.value = normalizeTree(source)
  } catch (error) {
    console.error('刷新组织架构树失败:', error)
  } finally {
    treeLoading.value = false
  }
}

const fetchMembers = async () => {
  try {
    membersLoading.value = true
    await organizationStore.fetchEmployees({ page: 1, page_size: 200 })
  } catch (error) {
    console.error('获取成员列表失败:', error)
  } finally {
    membersLoading.value = false
  }
}

const handleNodeClick = (data: TreeNodeItem) => {
  if (data?.type === 'department') {
    selectedDeptId.value = data?.id ?? null
    selectedDeptName.value = data?.name ?? ''
    currentPage.value = 1
    // 清除员工选择
    selectedEmployee.value = null
  } else if (data?.type === 'employee') {
    // 点击员工节点在右侧显示详情
    showEmployeeDetail(data)
    // 清除部门选择
    selectedDeptId.value = null
    selectedDeptName.value = ''
  }
}

const clearSelection = () => {
  selectedDeptId.value = null
  selectedDeptName.value = ''
  selectedEmployee.value = null
  currentPage.value = 1
  treeRef.value?.setCurrentKey(null)
}

const handleCurrentPageChange = (page: number) => {
  currentPage.value = page
}

const getLevelClass = (label: string) => {
  if (!label || label === '—') return 'pill-default'
  
  // 根据职级标识判断颜色
  if (/^(M1[0-9]|高管|总监|副总|CEO|CTO|CFO)/i.test(label)) return 'pill-executive'
  if (/^(M[7-9]|部门经理|总经理助理|主管)/i.test(label)) return 'pill-manager'
  if (/^(M[4-6]|组长|主办|资深)/i.test(label)) return 'pill-senior'
  if (/^(M[1-3]|专员|助理|初级)/i.test(label)) return 'pill-junior'
  if (/^(P[7-9]|高级工程师|架构师|专家)/i.test(label)) return 'pill-expert'
  if (/^(P[4-6]|工程师|分析师)/i.test(label)) return 'pill-professional'
  if (/^(P[1-3]|初级工程师|实习)/i.test(label)) return 'pill-entry'
  
  return 'pill-default'
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'success',
    leave: 'warning',
    resigned: 'info',
    retired: 'info',
    probation: 'primary'
  }
  return statusMap[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '在职',
    leave: '休假',
    resigned: '离职',
    retired: '退休',
    probation: '试用'
  }
  return statusMap[status] || '未知'
}

const showEmployeeDetail = (employee: any) => {
  // 提取真实的员工ID（如果是emp_X格式，提取数字部分）
  const realEmployeeId = typeof employee.id === 'string' && employee.id.startsWith('emp_') 
    ? parseInt(employee.id.replace('emp_', '')) 
    : employee.id
  
  // 为员工数据添加必要的显示字段
  const employeeData = {
    ...employee,
    id: realEmployeeId, // 使用真实的数字ID
    _avatarColor: avatarPalette[Math.abs(realEmployeeId) % avatarPalette.length],
    _initials: getInitials(employee.name),
    _departmentName: employee.department_name || '—',
    _positionName: employee.position_name || '—',
    _levelLabel: employee.level_display || '—',
    _statusMeta: statusMap[employee.status] || statusMap.default
  }
  selectedEmployee.value = employeeData
  // 不在弹窗中显示，而是在右侧显示
}

const editEmployee = (employee: any) => {
  // 提取真实的员工ID（如果是emp_X格式，提取数字部分）
  const realEmployeeId = typeof employee.id === 'string' && employee.id.startsWith('emp_') 
    ? parseInt(employee.id.replace('emp_', '')) 
    : employee.id
  
  // 跳转到员工编辑页面
  router.push(`/employees/${realEmployeeId}/edit`)
}

// 切换编辑模式
const toggleEditMode = async () => {
  if (isEditing.value) {
    // 保存编辑
    await saveEmployee()
  } else {
    // 进入编辑模式
    await enterEditMode()
  }
}

// 进入编辑模式
const enterEditMode = async () => {
  isEditing.value = true
  // 加载数据源
  await loadEditData()
  // 填充编辑表单
  fillEditForm()
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
  editForm.value = {
    name: '',
    gender: '',
    birth_date: '',
    phone: '',
    email: '',
    address: '',
    department_id: null,
    position_id: null,
    level: '',
    supervisor_id: null,
    hire_date: '',
    status: ''
  }
}

// 填充编辑表单
const fillEditForm = () => {
  if (selectedEmployee.value) {
    editForm.value = {
      name: selectedEmployee.value.name || '',
      gender: selectedEmployee.value.gender || '',
      birth_date: selectedEmployee.value.birth_date || '',
      phone: selectedEmployee.value.phone || '',
      email: selectedEmployee.value.email || '',
      address: selectedEmployee.value.address || '',
      department_id: selectedEmployee.value.department || null,
      position_id: selectedEmployee.value.position || null,
      level: selectedEmployee.value.level || '',
      supervisor_id: selectedEmployee.value.supervisor || null,
      hire_date: selectedEmployee.value.hire_date || '',
      status: selectedEmployee.value.status || ''
    }
  }
}

// 加载编辑所需的数据
const loadEditData = async () => {
  try {
    // 加载部门数据
    const deptResponse = await fetch('/api/departments/')
    if (deptResponse.ok) {
      const deptData = await deptResponse.json()
      departments.value = deptData.results || deptData
    }
    
    // 加载职位数据
    const posResponse = await fetch('/api/positions/')
    if (posResponse.ok) {
      const posData = await posResponse.json()
      positions.value = posData.results || posData
    }
    
    // 加载员工数据
    const empResponse = await fetch('/api/employees/')
    if (empResponse.ok) {
      const empData = await empResponse.json()
      allEmployees.value = empData.results || empData
    }
  } catch (error) {
    console.error('加载编辑数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

// 保存员工信息
const saveEmployee = async () => {
  try {
    // 准备更新数据，只包含需要更新的字段
    const updateData = {
      name: editForm.value.name,
      gender: editForm.value.gender,
      birth_date: editForm.value.birth_date || null,
      phone: editForm.value.phone,
      email: editForm.value.email,
      address: editForm.value.address,
      department: editForm.value.department_id,
      position: editForm.value.position_id,
      supervisor: editForm.value.supervisor_id,
      hire_date: editForm.value.hire_date, // hire_date是必需字段，不能为null
      status: editForm.value.status
    }
    
    // 验证必需字段
    if (!updateData.name || !updateData.gender || !updateData.department || !updateData.position || !updateData.hire_date || !updateData.status) {
      ElMessage.error('请填写所有必需字段')
      return
    }
    
    // 过滤掉空值和无效值，但保留必需字段
    const filteredData = Object.fromEntries(
      Object.entries(updateData).filter(([key, value]) => {
        // 必需字段即使为空也要保留
        const requiredFields = ['name', 'gender', 'department', 'position', 'hire_date', 'status']
        if (requiredFields.includes(key)) {
          return true
        }
        // 其他字段过滤空值
        if (value === null || value === undefined || value === '') {
          return false
        }
        return true
      })
    )
    
    console.log('准备更新员工数据:', updateData)
    console.log('过滤后的数据:', filteredData)
    console.log('员工ID:', selectedEmployee.value.id)
    console.log('编辑表单数据:', editForm.value)
    
    const response = await fetch(`/api/employees/${selectedEmployee.value.id}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(filteredData)
    })
    
    console.log('API响应状态:', response.status)
    console.log('API响应头:', response.headers)
    
    if (response.ok) {
      ElMessage.success('员工信息更新成功')
      isEditing.value = false
      // 刷新员工数据
      await refreshTree()
      // 更新选中的员工信息
      const updatedEmployee = await response.json()
      selectedEmployee.value = {
        ...selectedEmployee.value,
        ...updatedEmployee,
        _avatarColor: selectedEmployee.value._avatarColor,
        _initials: selectedEmployee.value._initials,
        _departmentName: updatedEmployee.department_name || '—',
        _positionName: updatedEmployee.position_name || '—',
        _levelLabel: updatedEmployee.level_display || '—',
        _statusMeta: statusMap[updatedEmployee.status] || statusMap.default
      }
    } else {
      // 获取错误详情
      const errorData = await response.json()
      console.error('API错误响应:', errorData)
      console.error('错误状态:', response.status)
      console.error('错误状态文本:', response.statusText)
      
      ElMessage.error(`保存失败: ${errorData.detail || errorData.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('保存员工信息失败:', error)
    ElMessage.error('保存失败')
  }
}


const formatDate = (dateStr: string) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const getGenderLabel = (gender: string) => {
  const genderMap: Record<string, string> = {
    'M': '男',
    'F': '女'
  }
  return genderMap[gender] || '—'
}

watch([pageSize, filteredEmployees], () => {
  const maxPage = Math.max(1, Math.ceil(filteredEmployees.value.length / pageSize.value || 1))
  if (currentPage.value > maxPage) {
    currentPage.value = maxPage
  }
})

watch([keyword, selectedDeptId], () => {
  currentPage.value = 1
})

onMounted(async () => {
  await Promise.all([refreshTree(), fetchMembers()])
})
</script>

<style scoped>
.org-page {
  padding-bottom: 32px;
}

.org-columns {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  align-items: flex-start;
}

.org-card {
  background: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 20px !important;
  padding: 20px !important;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.panel-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827 !important;
}

.panel-title p {
  margin: 4px 0 0;
  font-size: 13px;
  color: #6b7280 !important;
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-actions .el-button {
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 4px;
  font-weight: 500;
}

.panel-actions .el-button--primary {
  background: #3b82f6;
  border-color: #3b82f6;
}

.panel-actions .el-button--primary:hover {
  background: #2563eb;
  border-color: #2563eb;
}

.panel-actions .el-button--success {
  background: #10b981;
  border-color: #10b981;
}

.panel-actions .el-button--success:hover {
  background: #059669;
  border-color: #059669;
}

.tree-wrapper {
  max-height: 640px;
  overflow-y: auto;
  padding-right: 6px;
}

.organization-tree {
  --el-tree-node-hover-bg-color: transparent;
}

:deep(.organization-tree .el-tree-node__content) {
  height: auto;
  min-height: 48px;
  padding: 4px 8px;
  border-radius: 12px;
}

:deep(.organization-tree .el-tree-node__content:hover) {
  background: #f5f7ff !important;
}

.tree-node {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tree-node-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.tree-node-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937 !important;
}

.tree-node-count {
  font-size: 12px;
  color: #2563eb !important;
  background: #ecf2ff;
  padding: 2px 8px;
  border-radius: 12px;
}

.tree-node-meta {
  margin: 0;
  font-size: 12px;
  color: #9ca3af !important;
}

/* 员工节点样式 */
.employee-node {
  background-color: #f9fafb;
  border-left: 3px solid #e5e7eb;
  margin-left: 8px;
  border-radius: 6px;
}

.employee-node:hover {
  background-color: #f3f4f6;
}

.employee-info {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-size: 12px;
}

.position-info {
  color: #64748b;
  font-weight: 500;
}

.position-level {
  color: #0ea5e9;
  font-weight: 600;
  background-color: #e0f2fe;
  padding: 1px 4px;
  border-radius: 4px;
  margin-left: 4px;
}

.employee-status {
  margin: 0;
  display: flex;
  justify-content: flex-end;
}

.org-members-card {
  display: flex;
  flex-direction: column;
}

.members-header {
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.page-size-select {
  width: 120px;
}

.members-table {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.members-table .el-table__header th) {
  background: #f9fafb !important;
  color: #475569 !important;
  font-weight: 600 !important;
}

:deep(.members-table .el-table__cell) {
  padding: 14px 16px !important;
}

.member-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.member-avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  font-size: 14px;
  color: #ffffff !important;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.member-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.member-name {
  font-size: 14px;
  color: #0f172a !important;
  font-weight: 600;
}

.member-mail {
  font-size: 12px;
  color: #6b7280 !important;
}

.cell-text {
  font-size: 14px;
  color: #374151 !important;
}

.position-level-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.level-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  color: #1f2937 !important;
}

.pill-executive {
  background: #fef3c7;
  color: #d97706 !important;
}

.pill-manager {
  background: #e0e7ff;
  color: #4338ca !important;
}

.pill-senior {
  background: #ddd6fe;
  color: #7c3aed !important;
}

.pill-junior {
  background: #fce7f3;
  color: #be185d !important;
}

.pill-expert {
  background: #d1fae5;
  color: #047857 !important;
}

.pill-professional {
  background: #cffafe;
  color: #0f766e !important;
}

.pill-entry {
  background: #f3f4f6;
  color: #6b7280 !important;
}

.pill-default {
  background: #e5e7eb;
  color: #374151 !important;
}

.empty-state {
  padding: 48px 0;
  color: #9ca3af !important;
  font-size: 14px;
}

/* 员工详情面板样式 */
.employee-detail-panel {
  padding: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.employee-detail {
  padding: 8px 0;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 20px;
}

.detail-avatar {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  font-size: 24px;
  color: #ffffff !important;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.detail-info {
  flex: 1;
}

.detail-name {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 600;
  color: #111827 !important;
}

.detail-id {
  margin: 0;
  font-size: 14px;
  color: #6b7280 !important;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-section h4 {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
  color: #374151 !important;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  font-size: 12px;
  font-weight: 500;
  color: #6b7280 !important;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-item span {
  font-size: 14px;
  color: #111827 !important;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.detail-actions {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 员工详情头部样式 */
.detail-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  position: relative;
}

.detail-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  opacity: 0.3;
}

.detail-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
  color: white;
  border: 4px solid rgba(255, 255, 255, 0.3);
  position: relative;
  z-index: 1;
}

.detail-info {
  flex: 1;
  position: relative;
  z-index: 1;
}

.detail-name {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: white;
}

.detail-id {
  font-size: 16px;
  margin: 0 0 12px 0;
  color: rgba(255, 255, 255, 0.9);
}

.detail-status {
  margin-top: 8px;
}

.detail-actions-header {
  display: flex;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.detail-actions-header .el-button {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  backdrop-filter: blur(10px);
}

.detail-actions-header .el-button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.detail-actions-header .el-button--primary {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  border-color: rgba(255, 255, 255, 0.9);
}

.detail-actions-header .el-button--primary:hover {
  background: white;
  color: #667eea;
}

/* 详情内容样式 */
.detail-content {
  padding: 24px;
}

.detail-card {
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 20px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.detail-card:last-child {
  margin-bottom: 0;
}

.card-header {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.card-body {
  padding: 20px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  margin: 0;
}

.detail-value {
  font-size: 15px;
  color: #1e293b;
  padding: 8px 0;
  min-height: 20px;
}

.detail-item .el-input,
.detail-item .el-select,
.detail-item .el-date-picker {
  width: 100%;
}

.detail-item .el-textarea {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .detail-actions-header {
    justify-content: center;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }
}

.members-footer {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1200px) {
  .org-columns {
    grid-template-columns: 1fr;
  }

  .org-tree-card {
    order: 2;
  }

  .org-members-card {
    order: 1;
  }
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .search-input {
    flex: 1;
  }

  .page-size-select {
    width: auto;
  }
}
</style>
