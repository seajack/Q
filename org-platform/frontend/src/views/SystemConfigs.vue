<template>
  <div class="system-configs">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统配置管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="showAddDialog = true">
              新增配置
            </el-button>
            <el-button @click="exportConfigs">导出配置</el-button>
            <el-button @click="showImportDialog = true">导入配置</el-button>
          </div>
        </div>
      </template>
      
      <!-- 配置分类筛选 -->
      <el-row class="filter-row">
        <el-col :span="6">
          <el-select v-model="selectedCategory" placeholder="选择配置分类" @change="loadConfigs">
            <el-option label="全部" value="" />
            <el-option label="组织架构配置" value="organization" />
            <el-option label="职位配置" value="position" />
            <el-option label="员工配置" value="employee" />
            <el-option label="工作流配置" value="workflow" />
            <el-option label="集成配置" value="integration" />
            <el-option label="安全配置" value="security" />
            <el-option label="通知配置" value="notification" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索配置键或描述"
            @input="handleSearch"
            clearable
          />
        </el-col>
      </el-row>
      
      <!-- 配置列表 -->
      <el-table :data="configs" v-loading="loading" style="margin-top: 20px">
        <el-table-column prop="key" label="配置键" width="200" />
        <el-table-column prop="value" label="配置值" width="300" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)">
              {{ getCategoryName(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="data_type" label="数据类型" width="100" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="editConfig(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteConfig(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; text-align: right"
      />
    </el-card>
    
    <!-- 新增/编辑配置对话框 -->
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑配置' : '新增配置'" width="600px">
      <el-form :model="configForm" label-width="100px" :rules="configRules" ref="configFormRef">
        <el-form-item label="配置键" prop="key">
          <el-input v-model="configForm.key" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="配置值" prop="value">
          <el-input v-model="configForm.value" type="textarea" />
        </el-form-item>
        <el-form-item label="配置分类" prop="category">
          <el-select v-model="configForm.category">
            <el-option label="组织架构配置" value="organization" />
            <el-option label="职位配置" value="position" />
            <el-option label="员工配置" value="employee" />
            <el-option label="工作流配置" value="workflow" />
            <el-option label="集成配置" value="integration" />
            <el-option label="安全配置" value="security" />
            <el-option label="通知配置" value="notification" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据类型" prop="data_type">
          <el-select v-model="configForm.data_type">
            <el-option label="字符串" value="string" />
            <el-option label="整数" value="integer" />
            <el-option label="布尔值" value="boolean" />
            <el-option label="JSON对象" value="json" />
            <el-option label="列表" value="list" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="configForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="是否必需">
          <el-switch v-model="configForm.is_required" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="configForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 导入配置对话框 -->
    <el-dialog v-model="showImportDialog" title="导入配置" width="600px">
      <el-form>
        <el-form-item label="配置数据">
          <el-input
            v-model="importData"
            type="textarea"
            :rows="10"
            placeholder="请输入JSON格式的配置数据"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="importConfigs">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { configApi } from '@/utils/api'

const configs = ref([])
const loading = ref(false)
const selectedCategory = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showAddDialog = ref(false)
const showImportDialog = ref(false)
const isEdit = ref(false)
const importData = ref('')

const configForm = reactive({
  key: '',
  value: '',
  category: 'organization',
  data_type: 'string',
  description: '',
  is_required: false,
  is_active: true
})

const configRules = {
  key: [{ required: true, message: '请输入配置键', trigger: 'blur' }],
  value: [{ required: true, message: '请输入配置值', trigger: 'blur' }],
  category: [{ required: true, message: '请选择配置分类', trigger: 'change' }],
  data_type: [{ required: true, message: '请选择数据类型', trigger: 'change' }]
}

const loadConfigs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...(selectedCategory.value && { category: selectedCategory.value }),
      ...(searchKeyword.value && { search: searchKeyword.value })
    }
    const response = await configApi.getConfigs(params)
    configs.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadConfigs()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadConfigs()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadConfigs()
}

const getCategoryType = (category: string) => {
  const types = {
    organization: 'primary',
    position: 'success',
    employee: 'warning',
    workflow: 'info',
    integration: 'danger',
    security: 'danger',
    notification: 'success'
  }
  return types[category] || 'default'
}

const getCategoryName = (category: string) => {
  const names = {
    organization: '组织架构',
    position: '职位',
    employee: '员工',
    workflow: '工作流',
    integration: '集成',
    security: '安全',
    notification: '通知'
  }
  return names[category] || category
}

const editConfig = (config: any) => {
  isEdit.value = true
  Object.assign(configForm, config)
  showAddDialog.value = true
}

const deleteConfig = async (config: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个配置吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await configApi.deleteConfig(config.id)
    ElMessage.success('删除成功')
    loadConfigs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveConfig = async () => {
  try {
    if (isEdit.value) {
      await configApi.updateConfig(configForm.id, configForm)
    } else {
      await configApi.createConfig(configForm)
    }
    ElMessage.success('保存成功')
    showAddDialog.value = false
    loadConfigs()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const exportConfigs = async () => {
  try {
    const response = await configApi.exportConfigs()
    const dataStr = JSON.stringify(response.data, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'configs.json'
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const importConfigs = async () => {
  try {
    const data = JSON.parse(importData.value)
    await configApi.importConfigs({ configs: data })
    ElMessage.success('导入成功')
    showImportDialog.value = false
    loadConfigs()
  } catch (error) {
    ElMessage.error('导入失败，请检查JSON格式')
  }
}

onMounted(() => {
  loadConfigs()
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
