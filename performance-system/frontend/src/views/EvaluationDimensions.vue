<template>
  <div class="evaluation-dimensions">
    <div class="page-header">
      <h1>评估维度管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><component :is="Icons.Plus" /></el-icon>
          新建维度
        </el-button>
      </div>
    </div>

    <!-- 维度列表 -->
    <div class="dimensions-list">
      <el-table :data="dimensions" v-loading="loading">
        <el-table-column prop="name" label="维度名称" width="200" />
        <el-table-column prop="dimension_type" label="维度类型" width="150">
          <template #default="{ row }">
            <el-tag :type="getDimensionTypeColor(row.dimension_type)">
              {{ getDimensionTypeText(row.dimension_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="weight" label="权重" width="100">
          <template #default="{ row }">
            <span class="weight-value">{{ row.weight }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDimension(row)">查看</el-button>
            <el-button size="small" type="primary" @click="editDimension(row)">编辑</el-button>
            <el-button 
              size="small" 
              :type="row.is_active ? 'warning' : 'success'"
              @click="toggleDimension(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadDimensions"
          @current-change="loadDimensions"
        />
      </div>
    </div>

    <!-- 创建/编辑维度对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingDimension ? '编辑维度' : '新建维度'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="dimensionForm" :rules="dimensionRules" ref="dimensionFormRef" label-width="120px">
        <el-form-item label="维度名称" prop="name">
          <el-input v-model="dimensionForm.name" placeholder="请输入维度名称" />
        </el-form-item>
        <el-form-item label="维度类型" prop="dimension_type">
          <el-select v-model="dimensionForm.dimension_type" placeholder="选择维度类型">
            <el-option label="能力维度" value="capability" />
            <el-option label="态度维度" value="attitude" />
            <el-option label="业绩维度" value="performance" />
            <el-option label="创新维度" value="innovation" />
            <el-option label="领导力维度" value="leadership" />
            <el-option label="团队合作维度" value="teamwork" />
            <el-option label="客户服务维度" value="customer_service" />
            <el-option label="自定义维度" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="权重" prop="weight">
          <el-input-number
            v-model="dimensionForm.weight"
            :min="0"
            :max="1"
            :step="0.01"
            :precision="2"
            placeholder="请输入权重"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="dimensionForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入维度描述"
          />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="dimensionForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDimension" :loading="saving">
          {{ editingDimension ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 维度详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="维度详情"
      width="800px"
    >
      <div v-if="currentDimension" class="dimension-detail">
        <div class="detail-header">
          <h3>{{ currentDimension.name }}</h3>
          <el-tag :type="getDimensionTypeColor(currentDimension.dimension_type)">
            {{ getDimensionTypeText(currentDimension.dimension_type) }}
          </el-tag>
        </div>
        
        <div class="detail-content">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="info-item">
                <label>权重：</label>
                <span class="weight-value">{{ currentDimension.weight }}</span>
              </div>
              <div class="info-item">
                <label>状态：</label>
                <el-tag :type="currentDimension.is_active ? 'success' : 'danger'">
                  {{ currentDimension.is_active ? '启用' : '禁用' }}
                </el-tag>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <label>创建时间：</label>
                <span>{{ formatDateTime(currentDimension.created_at) }}</span>
              </div>
              <div class="info-item">
                <label>更新时间：</label>
                <span>{{ formatDateTime(currentDimension.updated_at) }}</span>
              </div>
            </el-col>
          </el-row>
          
          <div v-if="currentDimension.description" class="description">
            <h4>描述</h4>
            <p>{{ currentDimension.description }}</p>
          </div>
          
          <div v-if="currentDimension.indicators && currentDimension.indicators.length > 0" class="indicators">
            <h4>相关指标</h4>
            <el-table :data="currentDimension.indicators" size="small">
              <el-table-column prop="name" label="指标名称" />
              <el-table-column prop="weight" label="权重" width="100" />
              <el-table-column prop="is_active" label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                    {{ row.is_active ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, markRaw } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

// 使用 markRaw 防止图标组件被转换为响应式对象
const Icons = markRaw({
  Plus
})
import { formatDateTime } from '@/utils/dateUtils'
import { multidimensionalApi } from '@/utils/api'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const editingDimension = ref(null)
const currentDimension = ref(null)

// 数据列表
const dimensions = ref([])

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 表单
const dimensionForm = reactive({
  name: '',
  dimension_type: '',
  weight: 1.0,
  description: '',
  is_active: true
})

const dimensionRules = {
  name: [{ required: true, message: '请输入维度名称', trigger: 'blur' }],
  dimension_type: [{ required: true, message: '请选择维度类型', trigger: 'change' }],
  weight: [
    { required: true, message: '请输入权重', trigger: 'blur' },
    { type: 'number', min: 0, max: 1, message: '权重必须在0-1之间', trigger: 'blur' }
  ]
}

const dimensionFormRef = ref()

// 方法
const loadDimensions = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    const response = await multidimensionalApi.dimensions.list(params)
    dimensions.value = response.results
    pagination.total = response.count
  } catch (error) {
    ElMessage.error('加载维度列表失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  Object.assign(dimensionForm, {
    name: '',
    dimension_type: '',
    weight: 1.0,
    description: '',
    is_active: true
  })
  editingDimension.value = null
  dimensionFormRef.value?.resetFields()
}

const saveDimension = async () => {
  if (!dimensionFormRef.value) return
  
  const valid = await dimensionFormRef.value.validate()
  if (!valid) return
  
  saving.value = true
  try {
    if (editingDimension.value) {
      await multidimensionalApi.dimensions.update(editingDimension.value.id, dimensionForm)
      ElMessage.success('维度更新成功')
    } else {
      await multidimensionalApi.dimensions.create(dimensionForm)
      ElMessage.success('维度创建成功')
    }
    showCreateDialog.value = false
    loadDimensions()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const editDimension = (dimension) => {
  editingDimension.value = dimension
  Object.assign(dimensionForm, {
    name: dimension.name,
    dimension_type: dimension.dimension_type,
    weight: dimension.weight,
    description: dimension.description,
    is_active: dimension.is_active
  })
  showCreateDialog.value = true
}

const viewDimension = async (dimension) => {
  try {
    const response = await multidimensionalApi.dimensions.get(dimension.id)
    currentDimension.value = response.data
    showDetailDialog.value = true
  } catch (error) {
    ElMessage.error('加载维度详情失败')
  }
}

const toggleDimension = async (dimension) => {
  try {
    const action = dimension.is_active ? '禁用' : '启用'
    await ElMessageBox.confirm(`确定要${action}这个维度吗？`, `确认${action}`, {
      type: 'warning'
    })
    
    await multidimensionalApi.dimensions.update(dimension.id, {
      is_active: !dimension.is_active
    })
    
    ElMessage.success(`${action}成功`)
    loadDimensions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`${dimension.is_active ? '禁用' : '启用'}失败`)
    }
  }
}

const getDimensionTypeColor = (type) => {
  const colorMap = {
    capability: 'primary',
    attitude: 'success',
    performance: 'warning',
    innovation: 'danger',
    leadership: 'info',
    teamwork: 'success',
    customer_service: 'warning',
    custom: 'info'
  }
  return colorMap[type] || 'info'
}

const getDimensionTypeText = (type) => {
  const textMap = {
    capability: '能力维度',
    attitude: '态度维度',
    performance: '业绩维度',
    innovation: '创新维度',
    leadership: '领导力维度',
    teamwork: '团队合作维度',
    customer_service: '客户服务维度',
    custom: '自定义维度'
  }
  return textMap[type] || type
}

// 生命周期
onMounted(() => {
  loadDimensions()
})
</script>

<style scoped>
.evaluation-dimensions {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dimensions-list {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.dimension-detail {
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
  }
  
  .detail-content {
    .info-item {
      margin-bottom: 10px;
      
      label {
        font-weight: bold;
        margin-right: 10px;
      }
      
      .weight-value {
        font-size: 18px;
        font-weight: bold;
        color: #409eff;
      }
    }
    
    .description {
      margin-top: 20px;
      padding-top: 20px;
      border-top: 1px solid #eee;
      
      h4 {
        margin-bottom: 10px;
        color: #333;
      }
      
      p {
        line-height: 1.6;
        color: #666;
      }
    }
    
    .indicators {
      margin-top: 20px;
      padding-top: 20px;
      border-top: 1px solid #eee;
      
      h4 {
        margin-bottom: 10px;
        color: #333;
      }
    }
  }
}
</style>
