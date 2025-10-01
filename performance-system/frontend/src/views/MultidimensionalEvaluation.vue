<template>
  <div class="multidimensional-evaluation">
    <div class="page-header">
      <h1>多维度评估管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><component :is="Icons.Plus" /></el-icon>
          新建评估
        </el-button>
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="filter-section">
      <el-form :model="filters" inline>
        <el-form-item label="评估周期">
          <el-select v-model="filters.cycle_id" placeholder="选择周期" clearable>
            <el-option
              v-for="cycle in cycles"
              :key="cycle.id"
              :label="cycle.name"
              :value="cycle.id"
            />
          </el-select>
          <span style="margin-left: 10px; color: #666;">({{ cycles.length }} 个周期)</span>
        </el-form-item>
        <el-form-item label="评估方法">
          <el-select v-model="filters.method_id" placeholder="选择方法" clearable>
            <el-option
              v-for="method in methods"
              :key="method.id"
              :label="method.name"
              :value="method.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="已提交" value="submitted" />
            <el-option label="已审核" value="reviewed" />
            <el-option label="已确定" value="finalized" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadEvaluations">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 评估列表 -->
    <div class="evaluation-list">
      <el-table :data="evaluations" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="cycle_name" label="考核周期" width="150" />
        <el-table-column prop="evaluator_name" label="评价人" width="120" />
        <el-table-column prop="evaluatee_name" label="被评价人" width="120" />
        <el-table-column prop="evaluation_method_name" label="评估方法" width="150" />
        <el-table-column prop="total_score" label="总分" width="100">
          <template #default="{ row }">
            <span v-if="row.total_score">{{ row.total_score }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="weighted_score" label="加权分" width="100">
          <template #default="{ row }">
            <span v-if="row.weighted_score">{{ row.weighted_score }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
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
            <el-button size="small" @click="viewEvaluation(row)">查看</el-button>
            <el-button 
              v-if="row.status === 'draft'" 
              size="small" 
              type="primary" 
              @click="editEvaluation(row)"
            >
              编辑
            </el-button>
            <el-button 
              v-if="row.status === 'submitted'" 
              size="small" 
              type="success" 
              @click="reviewEvaluation(row)"
            >
              审核
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
          @size-change="loadEvaluations"
          @current-change="loadEvaluations"
        />
      </div>
    </div>

    <!-- 创建/编辑评估对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingEvaluation ? '编辑评估' : '新建评估'"
      width="800px"
      @close="resetForm"
    >
      <el-form :model="evaluationForm" :rules="evaluationRules" ref="evaluationFormRef" label-width="120px">
        <el-form-item label="考核周期" prop="cycle">
          <el-select v-model="evaluationForm.cycle" placeholder="选择考核周期">
            <el-option
              v-for="cycle in cycles"
              :key="cycle.id"
              :label="cycle.name"
              :value="cycle.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="评价人" prop="evaluator">
          <el-select v-model="evaluationForm.evaluator" placeholder="选择评价人">
            <el-option
              v-for="employee in employees"
              :key="employee.id"
              :label="employee.name"
              :value="employee.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="被评价人" prop="evaluatee">
          <el-select v-model="evaluationForm.evaluatee" placeholder="选择被评价人">
            <el-option
              v-for="employee in employees"
              :key="employee.id"
              :label="employee.name"
              :value="employee.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="评估方法" prop="evaluation_method">
          <el-select v-model="evaluationForm.evaluation_method" placeholder="选择评估方法">
            <el-option
              v-for="method in methods"
              :key="method.id"
              :label="method.name"
              :value="method.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="评价意见">
          <el-input
            v-model="evaluationForm.comments"
            type="textarea"
            :rows="3"
            placeholder="请输入评价意见"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEvaluation" :loading="saving">
          {{ editingEvaluation ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 评估详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="评估详情"
      width="1000px"
    >
      <div v-if="currentEvaluation" class="evaluation-detail">
        <div class="detail-header">
          <h3>{{ currentEvaluation.evaluator_name }} 对 {{ currentEvaluation.evaluatee_name }} 的评估</h3>
          <el-tag :type="getStatusType(currentEvaluation.status)">
            {{ getStatusText(currentEvaluation.status) }}
          </el-tag>
        </div>
        
        <div class="detail-content">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="info-item">
                <label>考核周期：</label>
                <span>{{ currentEvaluation.cycle_name }}</span>
              </div>
              <div class="info-item">
                <label>评估方法：</label>
                <span>{{ currentEvaluation.evaluation_method_name }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <label>总分：</label>
                <span class="score">{{ currentEvaluation.total_score || '-' }}</span>
              </div>
              <div class="info-item">
                <label>加权分：</label>
                <span class="score">{{ currentEvaluation.weighted_score || '-' }}</span>
              </div>
            </el-col>
          </el-row>
          
          <div v-if="currentEvaluation.comments" class="comments">
            <h4>评价意见</h4>
            <p>{{ currentEvaluation.comments }}</p>
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
import { multidimensionalApi, orgPlatformApi, cycleApi } from '@/utils/api'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const editingEvaluation = ref(null)
const currentEvaluation = ref(null)

// 数据列表
const evaluations = ref([])
const cycles = ref([])
const methods = ref([])
const employees = ref([])

// 筛选器
const filters = reactive({
  cycle_id: '',
  method_id: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 表单
const evaluationForm = reactive({
  cycle: '',
  evaluator: '',
  evaluatee: '',
  evaluation_method: '',
  comments: ''
})

const evaluationRules = {
  cycle: [{ required: true, message: '请选择考核周期', trigger: 'change' }],
  evaluator: [{ required: true, message: '请选择评价人', trigger: 'change' }],
  evaluatee: [{ required: true, message: '请选择被评价人', trigger: 'change' }],
  evaluation_method: [{ required: true, message: '请选择评估方法', trigger: 'change' }]
}

const evaluationFormRef = ref()

// 方法
const loadEvaluations = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    }
    const response = await multidimensionalApi.evaluations.list(params)
    evaluations.value = response.data.results || []
    pagination.total = response.data.count || 0
  } catch (error) {
    ElMessage.error('加载评估列表失败')
    evaluations.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

const loadCycles = async () => {
  try {
    console.log('开始加载考核周期...')
    const response = await cycleApi.list()
    console.log('考核周期API响应:', response)
    console.log('响应结果:', response.data.results)
    cycles.value = response.data.results || []
    console.log('考核周期数据已设置:', cycles.value)
    console.log('考核周期数量:', cycles.value.length)
  } catch (error) {
    console.error('加载考核周期失败:', error)
    cycles.value = []
  }
}

const loadMethods = async () => {
  try {
    const response = await multidimensionalApi.methods.list()
    methods.value = response.data.results || []
  } catch (error) {
    console.error('加载评估方法失败:', error)
    methods.value = []
  }
}

const loadEmployees = async () => {
  try {
    const response = await orgPlatformApi.employees.list()
    employees.value = response.data.results || []
  } catch (error) {
    console.error('加载员工列表失败:', error)
    employees.value = []
  }
}

const resetFilters = () => {
  Object.assign(filters, {
    cycle_id: '',
    method_id: '',
    status: ''
  })
  loadEvaluations()
}

const resetForm = () => {
  Object.assign(evaluationForm, {
    cycle: '',
    evaluator: '',
    evaluatee: '',
    evaluation_method: '',
    comments: ''
  })
  editingEvaluation.value = null
  evaluationFormRef.value?.resetFields()
}

const saveEvaluation = async () => {
  if (!evaluationFormRef.value) return
  
  const valid = await evaluationFormRef.value.validate()
  if (!valid) return
  
  saving.value = true
  try {
    if (editingEvaluation.value) {
      await multidimensionalApi.evaluations.update(editingEvaluation.value.id, evaluationForm)
      ElMessage.success('评估更新成功')
    } else {
      await multidimensionalApi.evaluations.create(evaluationForm)
      ElMessage.success('评估创建成功')
    }
    showCreateDialog.value = false
    loadEvaluations()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const editEvaluation = (evaluation) => {
  editingEvaluation.value = evaluation
  Object.assign(evaluationForm, {
    cycle: evaluation.cycle,
    evaluator: evaluation.evaluator,
    evaluatee: evaluation.evaluatee,
    evaluation_method: evaluation.evaluation_method,
    comments: evaluation.comments
  })
  showCreateDialog.value = true
}

const viewEvaluation = (evaluation) => {
  currentEvaluation.value = evaluation
  showDetailDialog.value = true
}

const reviewEvaluation = async (evaluation) => {
  try {
    await ElMessageBox.confirm('确定要审核这个评估吗？', '确认审核', {
      type: 'warning'
    })
    
    await multidimensionalApi.evaluations.review(evaluation.id)
    ElMessage.success('审核成功')
    loadEvaluations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('审核失败')
    }
  }
}

const getStatusType = (status) => {
  const statusMap = {
    draft: 'info',
    submitted: 'warning',
    reviewed: 'success',
    finalized: 'success'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    draft: '草稿',
    submitted: '已提交',
    reviewed: '已审核',
    finalized: '已确定'
  }
  return statusMap[status] || status
}

// 生命周期
onMounted(() => {
  loadEvaluations()
  loadCycles()
  loadMethods()
  loadEmployees()
})
</script>

<style scoped>
.multidimensional-evaluation {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-section {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.evaluation-list {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.evaluation-detail {
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
      
      .score {
        font-size: 18px;
        font-weight: bold;
        color: #409eff;
      }
    }
    
    .comments {
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
  }
}

.text-muted {
  color: #999;
}
</style>
