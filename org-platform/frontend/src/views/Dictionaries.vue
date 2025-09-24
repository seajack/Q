<template>
  <div class="dictionaries">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据字典管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="showAddDialog = true">
              新增字典项
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 字典分类筛选 -->
      <el-row class="filter-row">
        <el-col :span="6">
          <el-select v-model="selectedCategory" placeholder="选择字典分类" @change="loadDictionaries">
            <el-option label="全部" value="" />
            <el-option label="员工状态" value="employee_status" />
            <el-option label="学历层次" value="education_level" />
            <el-option label="技能等级" value="skill_level" />
            <el-option label="婚姻状况" value="marital_status" />
            <el-option label="部门类型" value="department_type" />
            <el-option label="职位级别" value="position_level" />
            <el-option label="工作流状态" value="workflow_status" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索字典项"
            @input="handleSearch"
            clearable
          />
        </el-col>
        <el-col :span="6">
          <el-button @click="loadDictionaries">刷新</el-button>
        </el-col>
      </el-row>
      
      <!-- 字典列表 -->
      <el-table :data="dictionaries" v-loading="loading" style="margin-top: 20px">
        <el-table-column prop="code" label="编码" width="150" />
        <el-table-column prop="name" label="名称" width="200" />
        <el-table-column prop="value" label="值" width="150" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)">
              {{ getCategoryName(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="parent_name" label="父级" width="150" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="editDictionary(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteDictionary(row)">删除</el-button>
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
    
    <!-- 新增/编辑字典项对话框 -->
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑字典项' : '新增字典项'" width="600px">
      <el-form :model="dictionaryForm" label-width="100px" :rules="dictionaryRules" ref="dictionaryFormRef">
        <el-form-item label="编码" prop="code">
          <el-input v-model="dictionaryForm.code" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="dictionaryForm.name" />
        </el-form-item>
        <el-form-item label="值">
          <el-input v-model="dictionaryForm.value" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="dictionaryForm.category">
            <el-option label="员工状态" value="employee_status" />
            <el-option label="学历层次" value="education_level" />
            <el-option label="技能等级" value="skill_level" />
            <el-option label="婚姻状况" value="marital_status" />
            <el-option label="部门类型" value="department_type" />
            <el-option label="职位级别" value="position_level" />
            <el-option label="工作流状态" value="workflow_status" />
          </el-select>
        </el-form-item>
        <el-form-item label="父级">
          <el-select v-model="dictionaryForm.parent" placeholder="选择父级字典项">
            <el-option label="无" :value="null" />
            <el-option
              v-for="item in parentOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="dictionaryForm.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="dictionaryForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="dictionaryForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDictionary">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dictionaryApi } from '@/utils/api'

const dictionaries = ref([])
const parentOptions = ref([])
const loading = ref(false)
const selectedCategory = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showAddDialog = ref(false)
const isEdit = ref(false)

const dictionaryForm = reactive({
  code: '',
  name: '',
  value: '',
  category: 'employee_status',
  parent: null,
  sort_order: 0,
  description: '',
  is_active: true
})

const dictionaryRules = {
  code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

const loadDictionaries = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...(selectedCategory.value && { category: selectedCategory.value }),
      ...(searchKeyword.value && { search: searchKeyword.value })
    }
    const response = await dictionaryApi.getDictionaries(params)
    dictionaries.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error('加载字典数据失败')
  } finally {
    loading.value = false
  }
}

const loadParentOptions = async () => {
  try {
    const response = await dictionaryApi.getDictionaries({ page_size: 1000 })
    parentOptions.value = response.data.results
  } catch (error) {
    console.error('加载父级选项失败', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadDictionaries()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadDictionaries()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadDictionaries()
}

const getCategoryType = (category: string) => {
  const types = {
    employee_status: 'primary',
    education_level: 'success',
    skill_level: 'warning',
    marital_status: 'info',
    department_type: 'danger',
    position_level: 'success',
    workflow_status: 'info'
  }
  return types[category] || 'default'
}

const getCategoryName = (category: string) => {
  const names = {
    employee_status: '员工状态',
    education_level: '学历层次',
    skill_level: '技能等级',
    marital_status: '婚姻状况',
    department_type: '部门类型',
    position_level: '职位级别',
    workflow_status: '工作流状态'
  }
  return names[category] || category
}

const editDictionary = (dictionary: any) => {
  isEdit.value = true
  Object.assign(dictionaryForm, dictionary)
  showAddDialog.value = true
}

const deleteDictionary = async (dictionary: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个字典项吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await dictionaryApi.deleteDictionary(dictionary.id)
    ElMessage.success('删除成功')
    loadDictionaries()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveDictionary = async () => {
  try {
    if (isEdit.value) {
      await dictionaryApi.updateDictionary(dictionaryForm.id, dictionaryForm)
    } else {
      await dictionaryApi.createDictionary(dictionaryForm)
    }
    ElMessage.success('保存成功')
    showAddDialog.value = false
    loadDictionaries()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 监听分类变化，更新父级选项
watch(() => dictionaryForm.category, (newCategory) => {
  if (newCategory) {
    loadParentOptions()
  }
})

onMounted(() => {
  loadDictionaries()
  loadParentOptions()
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
