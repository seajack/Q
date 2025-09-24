<template>
  <div class="container">
    <!-- 顶部工具条：标题 + 新增模板按钮 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">职位模板管理</h3>
      <div class="toolbar">
        <el-button type="primary" @click="showAddDialog = true">新增模板</el-button>
      </div>
    </div>

    <div class="card">
      <div class="table-wrap">
        <!-- 模板筛选 -->
        <el-row class="filter-row">
          <el-col :span="6">
            <el-select v-model="selectedLevel" placeholder="选择管理层级" @change="loadTemplates">
              <el-option label="全部" value="" />
              <el-option label="高层" value="senior" />
              <el-option label="中层" value="middle" />
              <el-option label="基层" value="junior" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索模板名称"
              @input="handleSearch"
              clearable
            />
          </el-col>
          <el-col :span="6">
            <el-button @click="loadTemplates">刷新</el-button>
          </el-col>
        </el-row>

        <!-- 模板列表 -->
        <el-table :data="templates" v-loading="loading" border stripe style="margin-top: 12px">
          <el-table-column prop="name" label="模板名称" width="200" />
          <el-table-column prop="description" label="描述" width="300" />
          <el-table-column prop="management_level" label="管理层级" width="120">
            <template #default="{ row }">
              <el-tag :type="getLevelType(row.management_level)">
                {{ getLevelName(row.management_level) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="level" label="职位级别" width="100" />
          <el-table-column prop="default_requirements" label="默认要求" width="300" />
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button size="small" @click="editTemplate(row)">编辑</el-button>
              <el-button size="small" type="success" @click="createPositionFromTemplate(row)">创建职位</el-button>
              <el-button size="small" type="danger" @click="deleteTemplate(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="row" style="padding-top:12px">
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
      </div>
    </div>

    <!-- 新增/编辑模板对话框 -->
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑模板' : '新增模板'" width="800px">
      <el-form :model="templateForm" label-width="120px" :rules="templateRules" ref="templateFormRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模板名称" prop="name">
              <el-input v-model="templateForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="管理层级" prop="management_level">
              <el-select v-model="templateForm.management_level">
                <el-option label="高层" value="senior" />
                <el-option label="中层" value="middle" />
                <el-option label="基层" value="junior" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职位级别" prop="level">
              <el-input-number v-model="templateForm.level" :min="1" :max="20" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否启用">
              <el-switch v-model="templateForm.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="描述">
          <el-input v-model="templateForm.description" type="textarea" />
        </el-form-item>
        
        <el-form-item label="默认要求">
          <el-input v-model="templateForm.default_requirements" type="textarea" />
        </el-form-item>
        
        <el-form-item label="默认职责">
          <el-input v-model="templateForm.default_responsibilities" type="textarea" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate">保存</el-button>
      </template>
    </el-dialog>

    <!-- 基于模板创建职位对话框 -->
    <el-dialog v-model="showCreatePositionDialog" title="基于模板创建职位" width="600px">
      <el-form :model="positionForm" label-width="100px" :rules="positionRules" ref="positionFormRef">
        <el-form-item label="职位名称" prop="name">
          <el-input v-model="positionForm.name" />
        </el-form-item>
        <el-form-item label="职位编码" prop="code">
          <el-input v-model="positionForm.code" />
        </el-form-item>
        <el-form-item label="所属部门" prop="department">
          <el-select v-model="positionForm.department" placeholder="选择部门">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职位描述">
          <el-input v-model="positionForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreatePositionDialog = false">取消</el-button>
        <el-button type="primary" @click="createPosition">创建职位</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { templateApi, departmentApi } from '@/utils/api'

const templates = ref<any[]>([])
const departments = ref<any[]>([])
const loading = ref(false)
const selectedLevel = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showAddDialog = ref(false)
const showCreatePositionDialog = ref(false)
const isEdit = ref(false)
const selectedTemplate = ref<any | null>(null)

const templateForm = reactive({
  name: '',
  description: '',
  management_level: 'junior',
  level: 1,
  default_requirements: '',
  default_responsibilities: '',
  is_active: true
})

const positionForm = reactive({
  name: '',
  code: '',
  department: null,
  description: ''
})

const templateRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  management_level: [{ required: true, message: '请选择管理层级', trigger: 'change' }],
  level: [{ required: true, message: '请输入职位级别', trigger: 'blur' }]
}

const positionRules = {
  name: [{ required: true, message: '请输入职位名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入职位编码', trigger: 'blur' }],
  department: [{ required: true, message: '请选择所属部门', trigger: 'change' }]
}

const loadTemplates = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...(selectedLevel.value && { management_level: selectedLevel.value }),
      ...(searchKeyword.value && { search: searchKeyword.value })
    }
    const response = await templateApi.getTemplates(params)
    templates.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error('加载模板失败')
  } finally {
    loading.value = false
  }
}

const loadDepartments = async () => {
  try {
    const response = await departmentApi.list({ page_size: 1000 })
    departments.value = response.data.results
  } catch (error) {
    ElMessage.error('加载部门失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadTemplates()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadTemplates()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadTemplates()
}

const getLevelType = (level: string) => {
  const types: Record<'senior'|'middle'|'junior', string> = {
    senior: 'danger',
    middle: 'warning',
    junior: 'success'
  }
  return (types as any)[level] || 'default'
}

const getLevelName = (level: string) => {
  const names: Record<'senior'|'middle'|'junior', string> = {
    senior: '高层',
    middle: '中层',
    junior: '基层'
  }
  return (names as any)[level] || level
}

const editingId = ref<number | null>(null)
const editTemplate = (template: any) => {
  isEdit.value = true
  editingId.value = template.id
  Object.assign(templateForm, template)
  showAddDialog.value = true
}

const deleteTemplate = async (template: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个模板吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await templateApi.deleteTemplate(template.id)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const createPositionFromTemplate = (template: any) => {
  selectedTemplate.value = template
  positionForm.name = template.name
  positionForm.description = template.description
  showCreatePositionDialog.value = true
}

const saveTemplate = async () => {
  try {
    if (isEdit.value) {
      await templateApi.updateTemplate(templateForm.id, templateForm)
    } else {
      await templateApi.createTemplate(templateForm)
    }
    ElMessage.success('保存成功')
    showAddDialog.value = false
    loadTemplates()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const createPosition = async () => {
  try {
    await templateApi.createPositionFromTemplate(selectedTemplate.value.id, positionForm)
    ElMessage.success('职位创建成功')
    showCreatePositionDialog.value = false
  } catch (error) {
    ElMessage.error('创建职位失败')
  }
}

onMounted(() => {
  loadTemplates()
  loadDepartments()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-row {
  margin-bottom: 20px;
}
</style>
