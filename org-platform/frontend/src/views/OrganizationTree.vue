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
            <el-link type="primary" @click="clearSelection">查看全部</el-link>
            <el-button text size="small" class="refresh-btn" @click="refreshTree">
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
              <div class="tree-node">
                <div class="tree-node-main">
                  <span class="tree-node-name">{{ data.name }}</span>
                  <span class="tree-node-count">{{ data.employee_count || 0 }} 人</span>
                </div>
                <p v-if="data.children?.length" class="tree-node-meta">
                  子部门 {{ data.children.length }}
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
            <div class="import-actions">
              <el-button type="success" size="small" @click="downloadTemplate">
                <el-icon><Download /></el-icon>
                下载模板
              </el-button>
              <el-button type="primary" size="small" @click="showImportDialog = true">
                <el-icon><Upload /></el-icon>
                导入组织树
              </el-button>
            </div>
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

        <el-table
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

    <!-- 员工详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="员工详情"
      width="600px"
      :before-close="closeDetailDialog"
    >
      <div v-if="selectedEmployee" class="employee-detail">
        <div class="detail-header">
          <div class="detail-avatar" :style="{ backgroundColor: selectedEmployee._avatarColor }">
            {{ selectedEmployee._initials }}
          </div>
          <div class="detail-info">
            <h3 class="detail-name">{{ selectedEmployee.name }}</h3>
            <p class="detail-id">工号: {{ selectedEmployee.employee_id || '—' }}</p>
          </div>
        </div>
        
        <div class="detail-content">
          <div class="detail-section">
            <h4>基本信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>性别</label>
                <span>{{ getGenderLabel(selectedEmployee.gender) }}</span>
              </div>
              <div class="detail-item">
                <label>出生日期</label>
                <span>{{ formatDate(selectedEmployee.birth_date) }}</span>
              </div>
              <div class="detail-item">
                <label>手机号</label>
                <span>{{ selectedEmployee.phone || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>邮箱</label>
                <span>{{ selectedEmployee.email || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>地址</label>
                <span>{{ selectedEmployee.address || '—' }}</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h4>职位信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>部门</label>
                <span>{{ selectedEmployee._departmentName }}</span>
              </div>
              <div class="detail-item">
                <label>岗位</label>
                <span>{{ selectedEmployee._positionName }}</span>
              </div>
              <div class="detail-item">
                <label>职级</label>
                <span class="level-pill" :class="getLevelClass(selectedEmployee._levelLabel)">{{ selectedEmployee._levelLabel }}</span>
              </div>
              <div class="detail-item">
                <label>直属上级</label>
                <span>{{ selectedEmployee.supervisor_name || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>入职日期</label>
                <span>{{ formatDate(selectedEmployee.hire_date) }}</span>
              </div>
              <div class="detail-item">
                <label>状态</label>
                <el-tag :type="selectedEmployee._statusMeta.type" effect="light" size="small">
                  {{ selectedEmployee._statusMeta.label }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeDetailDialog">关闭</el-button>
          <el-button type="primary" @click="editEmployee(selectedEmployee)">编辑</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 导入组织树对话框 -->
    <el-dialog v-model="showImportDialog" title="导入组织树" width="500px">
      <div style="margin-bottom: 20px;">
        <el-upload
          drag
          accept=".xlsx"
          :http-request="uploadFile"
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">拖拽Excel文件或<em>点击上传</em></div>
        </el-upload>
      </div>
      <div style="margin-bottom: 20px;">
        <label style="display: block; margin-bottom: 8px; font-weight: 500;">导入模式：</label>
        <el-select v-model="importMode" placeholder="选择导入模式" style="width: 100%;">
          <el-option label="增量更新" value="incremental" />
          <el-option label="全量替换" value="full" />
        </el-select>
      </div>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="importData">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { ElDialog, ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, Download, Upload } from '@element-plus/icons-vue'
import { useOrganizationStore } from '@/stores/organization'
import { useRouter } from 'vue-router'
import { departmentApi } from '@/utils/api'

interface TreeNodeItem {
  id: number
  name: string
  employee_count?: number
  children?: TreeNodeItem[]
}

const organizationStore = useOrganizationStore()
const { employees: employeesRef } = storeToRefs(organizationStore)
const router = useRouter()

// 详情弹窗相关
const detailDialogVisible = ref(false)
const selectedEmployee = ref<any>(null)

// 导入相关
const showImportDialog = ref(false)
const importMode = ref('incremental')
const importFile = ref(null)

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

const membersTitle = computed(() => selectedDeptName.value || '全部成员')
const membersSubtitle = computed(() => `共 ${pageTotal.value} 人`)

const normalizeTree = (nodes: any[]): TreeNodeItem[] => {
  if (!Array.isArray(nodes)) return []
  return nodes
    .filter(item => item && (item.type !== 'employee'))
    .map(item => ({
      id: item.id,
      name: item.name,
      employee_count: item.employee_count ?? 0,
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
  selectedDeptId.value = data?.id ?? null
  selectedDeptName.value = data?.name ?? ''
  currentPage.value = 1
}

const clearSelection = () => {
  selectedDeptId.value = null
  selectedDeptName.value = ''
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

const showEmployeeDetail = (employee: any) => {
  selectedEmployee.value = employee
  detailDialogVisible.value = true
}

const editEmployee = (employee: any) => {
  // 跳转到员工编辑页面
  router.push(`/employees/${employee.id}/edit`)
}

const closeDetailDialog = () => {
  detailDialogVisible.value = false
  selectedEmployee.value = null
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

const uploadFile = (upload: any) => {
  importFile.value = upload.file
}

const importData = async () => {
  if (!importFile.value) return ElMessage.error('请上传文件')
  const formData = new FormData()
  formData.append('file', importFile.value)
  formData.append('mode', importMode.value)
  try {
    const response = await departmentApi.import(formData)
    const results = response.data.results
    
    // 显示详细的导入结果
    let message = '导入完成！\n'
    if (results.departments) {
      message += `部门：新增${results.departments.created}个，更新${results.departments.updated}个\n`
    }
    if (results.positions) {
      message += `职位：新增${results.positions.created}个，更新${results.positions.updated}个\n`
    }
    if (results.employees) {
      message += `员工：新增${results.employees.created}个，更新${results.employees.updated}个\n`
    }
    
    // 显示错误信息
    const allErrors = []
    if (results.departments?.errors) allErrors.push(...results.departments.errors)
    if (results.positions?.errors) allErrors.push(...results.positions.errors)
    if (results.employees?.errors) allErrors.push(...results.employees.errors)
    
    if (allErrors.length > 0) {
      message += `\n错误信息：\n${allErrors.slice(0, 5).join('\n')}`
      if (allErrors.length > 5) {
        message += `\n...还有${allErrors.length - 5}个错误`
      }
    }
    
    ElMessage.success(message)
    showImportDialog.value = false
    await refreshTree()
    await fetchMembers()
  } catch (e) {
    ElMessage.error('导入失败：' + (e.response?.data?.error || e.message))
  }
}

const downloadTemplate = async () => {
  try {
    const response = await departmentApi.downloadTemplate()
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = 'organization_template.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

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
  gap: 12px;
}

.refresh-btn {
  color: #2563eb !important;
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

.import-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 12px;
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

/* 员工详情弹窗样式 */
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
