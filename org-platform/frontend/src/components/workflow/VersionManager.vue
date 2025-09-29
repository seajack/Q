<template>
  <div class="version-manager">
    <!-- 版本列表 -->
    <div class="version-list">
      <div class="list-header">
        <h4>版本历史</h4>
        <el-button type="primary" size="small" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建版本
        </el-button>
      </div>
      
      <div class="version-timeline">
        <div 
          v-for="(version, index) in sortedVersions" 
          :key="version.id"
          class="version-item"
          :class="{ 
            'current-version': version.id === current,
            'selected-version': selectedVersions.includes(version.id)
          }"
        >
          <!-- 时间线连接线 -->
          <div v-if="index < sortedVersions.length - 1" class="timeline-line"></div>
          
          <!-- 版本节点 -->
          <div class="version-node">
            <div class="version-dot" :class="getVersionStatus(version)"></div>
            
            <div class="version-content">
              <div class="version-header">
                <div class="version-info">
                  <h5 class="version-name">
                    {{ version.name }}
                    <el-tag v-if="version.id === current" type="success" size="small">当前</el-tag>
                  </h5>
                  <div class="version-meta">
                    <span class="version-author">{{ version.author || '系统' }}</span>
                    <span class="version-date">{{ formatDate(version.createdAt) }}</span>
                  </div>
                </div>
                
                <div class="version-actions">
                  <el-dropdown @command="onVersionAction" trigger="click">
                    <el-button size="small" text>
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item 
                          :command="`checkout:${version.id}`"
                          :disabled="version.id === current"
                        >
                          <el-icon><Switch /></el-icon>
                          切换到此版本
                        </el-dropdown-item>
                        <el-dropdown-item :command="`compare:${version.id}`">
                          <el-icon><Edit /></el-icon>
                          与当前版本对比
                        </el-dropdown-item>
                        <el-dropdown-item 
                          :command="`rollback:${version.id}`"
                          :disabled="version.id === current"
                        >
                          <el-icon><RefreshLeft /></el-icon>
                          回滚到此版本
                        </el-dropdown-item>
                        <el-dropdown-item 
                          :command="`delete:${version.id}`"
                          :disabled="version.id === current || sortedVersions.length <= 1"
                          divided
                        >
                          <el-icon><Delete /></el-icon>
                          删除版本
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </div>
              
              <div class="version-description">{{ version.description }}</div>
              
              <!-- 版本统计 -->
              <div class="version-stats">
                <div class="stat-item">
                  <el-icon><Grid /></el-icon>
                  <span>{{ getNodeCount(version) }} 个节点</span>
                </div>
                <div class="stat-item">
                  <el-icon><Connection /></el-icon>
                  <span>{{ getConnectionCount(version) }} 个连接</span>
                </div>
              </div>
              
              <!-- 变更摘要 -->
              <div v-if="version.changes && version.changes.length > 0" class="version-changes">
                <div class="changes-header">
                  <el-icon><EditPen /></el-icon>
                  <span>变更摘要</span>
                </div>
                <div class="changes-list">
                  <div 
                    v-for="change in version.changes.slice(0, 3)" 
                    :key="change.id"
                    class="change-item"
                    :class="`change-${change.type}`"
                  >
                    <el-icon>
                      <Plus v-if="change.type === 'add'" />
                      <Minus v-else-if="change.type === 'remove'" />
                      <Edit v-else />
                    </el-icon>
                    <span>{{ change.description }}</span>
                  </div>
                  <div v-if="version.changes.length > 3" class="more-changes">
                    +{{ version.changes.length - 3 }} 更多变更
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 版本对比 -->
    <div v-if="showComparison" class="version-comparison">
      <div class="comparison-header">
        <h4>版本对比</h4>
        <el-button size="small" text @click="showComparison = false">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
      
      <div class="comparison-content">
        <VersionDiff 
          :source-version="comparisonVersions.source"
          :target-version="comparisonVersions.target"
        />
      </div>
    </div>
    
    <!-- 创建版本对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      title="创建新版本" 
      width="500px"
      @close="resetCreateForm"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="80px">
        <el-form-item label="版本号" prop="name">
          <el-input 
            v-model="createForm.name" 
            placeholder="例如: v1.2.0"
          />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="createForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="描述此版本的主要变更..."
          />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-select 
            v-model="createForm.tags" 
            multiple 
            filterable 
            allow-create 
            placeholder="添加标签"
            style="width: 100%"
          >
            <el-option label="功能增强" value="feature" />
            <el-option label="问题修复" value="bugfix" />
            <el-option label="性能优化" value="performance" />
            <el-option label="重大更新" value="major" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createVersion" :loading="creating">
          创建版本
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, MoreFilled, Switch, RefreshLeft, Delete,
  Grid, Connection, EditPen, Edit, Minus, Close
} from '@element-plus/icons-vue'

interface WorkflowVersion {
  id: string
  name: string
  description: string
  author?: string
  createdAt: Date
  workflow: any
  changes?: Array<{
    id: string
    type: 'add' | 'remove' | 'modify'
    description: string
  }>
  tags?: string[]
}

interface Props {
  versions: WorkflowVersion[]
  current: string
}

interface Emits {
  (e: 'create', version: Omit<WorkflowVersion, 'id' | 'createdAt'>): void
  (e: 'rollback', versionId: string): void
  (e: 'compare', sourceId: string, targetId: string): void
  (e: 'delete', versionId: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const selectedVersions = ref<string[]>([])
const showComparison = ref(false)
const showCreateDialog = ref(false)
const creating = ref(false)
const createFormRef = ref()

const comparisonVersions = reactive({
  source: null as WorkflowVersion | null,
  target: null as WorkflowVersion | null
})

const createForm = reactive({
  name: '',
  description: '',
  tags: [] as string[]
})

const createRules = {
  name: [
    { required: true, message: '请输入版本号', trigger: 'blur' },
    { pattern: /^v?\d+\.\d+\.\d+$/, message: '版本号格式不正确', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入版本描述', trigger: 'blur' }
  ]
}

// 计算属性
const sortedVersions = computed(() => {
  return [...props.versions].sort((a, b) => 
    new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  )
})

// 方法
const getVersionStatus = (version: WorkflowVersion) => {
  if (version.id === props.current) return 'current'
  return 'normal'
}

const getNodeCount = (version: WorkflowVersion) => {
  return version.workflow?.nodes?.length || 0
}

const getConnectionCount = (version: WorkflowVersion) => {
  return version.workflow?.connections?.length || 0
}

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date))
}

const onVersionAction = async (command: string) => {
  const [action, versionId] = command.split(':')
  
  switch (action) {
    case 'checkout':
      await checkoutVersion(versionId)
      break
    case 'compare':
      await compareVersion(versionId)
      break
    case 'rollback':
      await rollbackVersion(versionId)
      break
    case 'delete':
      await deleteVersion(versionId)
      break
  }
}

const checkoutVersion = async (versionId: string) => {
  try {
    await ElMessageBox.confirm('切换版本将丢失当前未保存的更改，是否继续？', '确认切换')
    emit('rollback', versionId)
    ElMessage.success('版本切换成功')
  } catch {
    // 用户取消
  }
}

const compareVersion = (versionId: string) => {
  const sourceVersion = props.versions.find(v => v.id === versionId)
  const targetVersion = props.versions.find(v => v.id === props.current)
  
  if (sourceVersion && targetVersion) {
    comparisonVersions.source = sourceVersion
    comparisonVersions.target = targetVersion
    showComparison.value = true
    emit('compare', versionId, props.current)
  }
}

const rollbackVersion = async (versionId: string) => {
  try {
    await ElMessageBox.confirm(
      '回滚操作将创建一个新版本，原版本不会被删除。是否继续？', 
      '确认回滚'
    )
    emit('rollback', versionId)
    ElMessage.success('版本回滚成功')
  } catch {
    // 用户取消
  }
}

const deleteVersion = async (versionId: string) => {
  try {
    await ElMessageBox.confirm('删除版本后无法恢复，是否确认删除？', '确认删除', {
      type: 'warning'
    })
    emit('delete', versionId)
    ElMessage.success('版本删除成功')
  } catch {
    // 用户取消
  }
}

const createVersion = async () => {
  try {
    await createFormRef.value?.validate()
    creating.value = true
    
    const newVersion = {
      name: createForm.name,
      description: createForm.description,
      tags: createForm.tags,
      author: '当前用户' // 实际应用中从用户信息获取
    }
    
    emit('create', newVersion)
    showCreateDialog.value = false
    ElMessage.success('版本创建成功')
  } catch (error) {
    console.error('版本创建失败:', error)
  } finally {
    creating.value = false
  }
}

const resetCreateForm = () => {
  createForm.name = ''
  createForm.description = ''
  createForm.tags = []
  createFormRef.value?.resetFields()
}

// 生成下一个版本号
const generateNextVersion = () => {
  if (props.versions.length === 0) return 'v1.0.0'
  
  const latestVersion = sortedVersions.value[0]
  const match = latestVersion.name.match(/v?(\d+)\.(\d+)\.(\d+)/)
  
  if (match) {
    const [, major, minor, patch] = match
    return `v${major}.${minor}.${parseInt(patch) + 1}`
  }
  
  return 'v1.0.0'
}

// 监听创建对话框打开，自动生成版本号
const onCreateDialogOpen = () => {
  createForm.name = generateNextVersion()
}
</script>

<style scoped>
.version-manager {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.version-list {
  flex: 1;
  overflow-y: auto;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.list-header h4 {
  margin: 0;
  font-weight: 600;
  color: #374151;
}

.version-timeline {
  position: relative;
}

.version-item {
  position: relative;
  margin-bottom: 1.5rem;
}

.timeline-line {
  position: absolute;
  left: 12px;
  top: 24px;
  width: 2px;
  height: calc(100% + 1.5rem);
  background: #e5e7eb;
  z-index: 1;
}

.version-node {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  position: relative;
  z-index: 2;
}

.version-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  margin-top: 4px;
}

.version-dot.current {
  background: #10b981;
  border-color: #10b981;
}

.version-dot.normal {
  background: #6b7280;
  border-color: #6b7280;
}

.version-content {
  flex: 1;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.current-version .version-content {
  border-color: #10b981;
  background: #f0fdf4;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.version-name {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.version-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.version-description {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.4;
  margin-bottom: 0.75rem;
}

.version-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.version-changes {
  border-top: 1px solid #e5e7eb;
  padding-top: 0.75rem;
}

.changes-header {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.changes-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.change-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
}

.change-add {
  color: #10b981;
}

.change-remove {
  color: #ef4444;
}

.change-modify {
  color: #f59e0b;
}

.more-changes {
  font-size: 0.75rem;
  color: #6b7280;
  font-style: italic;
  margin-left: 1rem;
}

.version-comparison {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
  margin-top: 1rem;
}

.comparison-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.comparison-header h4 {
  margin: 0;
  font-weight: 600;
  color: #374151;
}
</style>
