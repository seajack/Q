<template>
  <div class="dictionaries-page">
    <!-- 现代化页面头部 -->
    <ModernPageHeader
      title="数据字典"
      subtitle="系统数据字典管理与维护"
      icon="Collection"
      color="indigo"
    >
      <template #actions>
        <ModernButton type="secondary" icon="Download">
          导出字典
        </ModernButton>
        <ModernButton type="primary" icon="Plus" @click="showAddDialog = true">
          新增字典项
        </ModernButton>
      </template>
    </ModernPageHeader>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <ModernStatCard
        title="字典总数"
        :value="total"
        change="+8 本月"
        change-type="positive"
        icon="Collection"
        icon-type="primary"
      />
      <ModernStatCard
        title="活跃字典"
        :value="getActiveDictionaries()"
        change="+6 本月"
        change-type="positive"
        icon="CircleCheck"
        icon-type="success"
      />
      <ModernStatCard
        title="字典分类"
        :value="getDictionaryCategories()"
        change="稳定"
        change-type="positive"
        icon="FolderOpened"
        icon-type="warning"
      />
      <ModernStatCard
        title="父级字典"
        :value="getParentDictionaries()"
        change="+2 本月"
        change-type="positive"
        icon="DataLine"
        icon-type="success"
      />
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 分类导航 -->
      <ModernCard title="字典分类" icon="Menu" class="category-nav">
        <div class="category-list">
          <div 
            v-for="category in dictionaryCategories" 
            :key="category.value"
            class="category-item"
            :class="{ active: selectedCategory === category.value }"
            @click="selectCategory(category.value)"
          >
            <div class="category-icon" :class="category.iconClass">
              <el-icon><component :is="category.icon" /></el-icon>
            </div>
            <div class="category-info">
              <div class="category-name">{{ category.name }}</div>
              <div class="category-count">{{ getCategoryCount(category.value) }}个字典</div>
            </div>
          </div>
        </div>
      </ModernCard>

      <!-- 字典列表 -->
      <ModernCard title="字典列表" icon="List" class="dictionary-list">
        <template #actions>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索字典"
            @input="handleSearch"
            clearable
            style="width: 200px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </template>
        
        <div class="dictionaries-grid" v-loading="loading">
          <div 
            v-for="dictionary in filteredDictionaries" 
            :key="dictionary.id" 
            class="dictionary-card"
            @click="selectDictionary(dictionary)"
          >
            <div class="dictionary-header">
              <div class="dictionary-icon" :class="getDictionaryIconClass(dictionary.category)">
                <el-icon><component :is="getDictionaryIcon(dictionary.category)" /></el-icon>
              </div>
              <div class="dictionary-status">
                <el-tag :type="dictionary.is_active ? 'success' : 'danger'" size="small" effect="light">
                  {{ dictionary.is_active ? '启用' : '禁用' }}
                </el-tag>
              </div>
            </div>
            
            <div class="dictionary-info">
              <h4 class="dictionary-name">{{ dictionary.name }}</h4>
              <div class="dictionary-value" v-if="dictionary.value">
                <span class="value-label">配置值</span>
                <span class="value-content">{{ dictionary.value }}</span>
              </div>
              <div class="dictionary-meta">
                <el-tag :type="getCategoryType(dictionary.category)" size="small" effect="plain">
                  {{ getCategoryName(dictionary.category) }}
                </el-tag>
                <span class="dictionary-sort">排序: {{ dictionary.sort_order }}</span>
              </div>
            </div>
            
            <div class="dictionary-details" v-if="dictionary.parent_name">
              <div class="detail-item">
                <span class="detail-label">父级</span>
                <span class="detail-value">{{ dictionary.parent_name }}</span>
              </div>
            </div>
            
            <div class="dictionary-actions">
              <ModernButton type="secondary" icon="Edit" size="small" @click.stop="editDictionary(dictionary)">
                编辑
              </ModernButton>
              <ModernButton type="danger" icon="Delete" size="small" @click.stop="deleteDictionary(dictionary)">
                删除
              </ModernButton>
            </div>
          </div>
        </div>
        
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
      </ModernCard>
    </div>
    
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
import { ref, onMounted, reactive, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, User, Reading, Trophy, Female, OfficeBuilding, Suitcase, Operation } from '@element-plus/icons-vue'
import { dictionaryApi } from '@/utils/api'
import ModernPageHeader from '@/components/common/ModernPageHeader.vue'
import ModernStatCard from '@/components/common/ModernStatCard.vue'
import ModernCard from '@/components/common/ModernCard.vue'
import ModernButton from '@/components/common/ModernButton.vue'

const dictionaries = ref([])
const parentOptions = ref([])
const loading = ref(false)
const selectedCategory = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedDictionary = ref<any | null>(null)

// 字典分类定义
const dictionaryCategories = [
  { value: '', name: '全部分类', icon: 'Collection', iconClass: 'icon-all' },
  { value: 'employee_status', name: '员工状态', icon: 'User', iconClass: 'icon-employee' },
  { value: 'education_level', name: '学历层次', icon: 'Reading', iconClass: 'icon-education' },
  { value: 'skill_level', name: '技能等级', icon: 'Trophy', iconClass: 'icon-skill' },
  { value: 'marital_status', name: '婚姻状况', icon: 'Female', iconClass: 'icon-marital' },
  { value: 'department_type', name: '部门类型', icon: 'OfficeBuilding', iconClass: 'icon-department' },
  { value: 'position_level', name: '职位级别', icon: 'Suitcase', iconClass: 'icon-position' },
  { value: 'workflow_status', name: '工作流状态', icon: 'Operation', iconClass: 'icon-workflow' }
]

// 统计方法
const getActiveDictionaries = () => {
  return dictionaries.value.filter(d => d.is_active).length
}

const getDictionaryCategories = () => {
  const categories = new Set(dictionaries.value.map(d => d.category))
  return categories.size
}

const getParentDictionaries = () => {
  return dictionaries.value.filter(d => !d.parent).length
}

const getCategoryCount = (category: string) => {
  if (!category) return dictionaries.value.length
  return dictionaries.value.filter(d => d.category === category).length
}

// 选择分类
const selectCategory = (category: string) => {
  selectedCategory.value = category
  currentPage.value = 1
  loadDictionaries()
}

// 选择字典
const selectDictionary = (dictionary: any) => {
  selectedDictionary.value = dictionary
}

// 过滤字典
const filteredDictionaries = computed(() => {
  let filtered = dictionaries.value
  if (selectedCategory.value) {
    filtered = filtered.filter(d => d.category === selectedCategory.value)
  }
  return filtered
})

// 获取字典图标
const getDictionaryIcon = (category: string) => {
  const iconMap = {
    employee_status: 'User',
    education_level: 'Reading',
    skill_level: 'Trophy',
    marital_status: 'Female',
    department_type: 'OfficeBuilding',
    position_level: 'Suitcase',
    workflow_status: 'Operation'
  }
  return iconMap[category] || 'Collection'
}

const getDictionaryIconClass = (category: string) => {
  const classMap = {
    employee_status: 'icon-employee',
    education_level: 'icon-education',
    skill_level: 'icon-skill',
    marital_status: 'icon-marital',
    department_type: 'icon-department',
    position_level: 'icon-position',
    workflow_status: 'icon-workflow'
  }
  return classMap[category] || 'icon-default'
}

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
    dictionaries.value = response.results
    total.value = response.count
  } catch (error) {
    ElMessage.error('加载字典数据失败')
  } finally {
    loading.value = false
  }
}

const loadParentOptions = async () => {
  try {
    const response = await dictionaryApi.getDictionaries({ page_size: 1000 })
    parentOptions.value = response.results
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
.dictionaries-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
  min-height: 100vh;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* 主内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 1.5rem;
}

/* 分类导航 */
.category-nav {
  height: fit-content;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.category-item:hover {
  background: #f8fafc;
  border-color: #e2e8f0;
}

.category-item.active {
  background: #eef2ff;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgb(99 102 241 / 0.1);
}

.category-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.125rem;
}

.icon-all { background: linear-gradient(135deg, #6366f1, #4f46e5); }
.icon-employee { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.icon-education { background: linear-gradient(135deg, #10b981, #059669); }
.icon-skill { background: linear-gradient(135deg, #f59e0b, #d97706); }
.icon-marital { background: linear-gradient(135deg, #ec4899, #db2777); }
.icon-department { background: linear-gradient(135deg, #14b8a6, #0d9488); }
.icon-position { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.icon-workflow { background: linear-gradient(135deg, #ef4444, #dc2626); }

.category-info {
  flex: 1;
}

.category-name {
  font-weight: 500;
  color: #111827;
  margin-bottom: 0.25rem;
}

.category-count {
  font-size: 0.75rem;
  color: #6b7280;
}

/* 字典列表 */
.dictionary-list {
  height: fit-content;
}

.dictionaries-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.dictionary-card {
  background: white;
  border-radius: 8px;
  padding: 0.75rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

/* 移除顶部蓝色横条 */

.dictionary-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #6366f1;
}

.dictionary-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.dictionary-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.icon-default { background: linear-gradient(135deg, #6366f1, #4f46e5); }

.dictionary-status {
  display: flex;
  align-items: center;
}

.dictionary-info {
  margin-bottom: 0.75rem;
}

.dictionary-name {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.25rem 0;
}

.dictionary-value {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.dictionary-value .value-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.dictionary-value .value-content {
  font-size: 0.875rem;
  font-weight: 500;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Courier New', monospace;
  color: #1f2937;
  background: #f8fafc;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  text-align: right;
  min-width: 80px;
  display: inline-block;
}

.dictionary-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.dictionary-sort {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background: #f3f4f6;
  border-radius: 0.25rem;
  color: #6b7280;
  font-weight: 500;
}

.dictionary-details {
  margin-bottom: 0.75rem;
  min-height: 1.5rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 0.75rem;
  color: #111827;
  font-weight: 500;
  max-width: 60%;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dictionary-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.dictionary-card:hover .dictionary-actions {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .category-nav {
    order: 2;
  }
  
  .dictionary-list {
    order: 1;
  }
  
  .category-list {
    flex-direction: row;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .dictionaries-page {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .dictionaries-grid {
    grid-template-columns: 1fr;
  }
  
  .dictionary-actions {
    opacity: 1;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .category-list {
    flex-direction: column;
  }
}
</style>
