<template>
  <div class="evaluation-rules">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>考核规则管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建规则
          </el-button>
        </div>
      </template>

      <el-table :data="evaluationRules" v-loading="loading">
        <el-table-column prop="name" label="规则名称" />
        <el-table-column prop="description" label="规则描述" show-overflow-tooltip />
        <el-table-column prop="evaluation_scope" label="评价范围" width="120">
          <template #default="{ row }">
            <el-tag>{{ getScopeText(row.evaluation_scope) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="relation_types" label="评价关系" width="200">
          <template #default="{ row }">
            <el-tag 
              v-for="type in row.relation_types" 
              :key="type" 
              size="small" 
              style="margin-right: 4px;"
            >
              {{ getRelationText(type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button size="small" @click="editRule(row)">编辑</el-button>
            <el-button size="small" @click="viewWeights(row)">权重配置</el-button>
            <el-button 
              size="small" 
              :type="row.is_active ? 'warning' : 'success'"
              @click="toggleStatus(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" type="danger" @click="deleteRule(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      :title="isEdit ? '编辑考核规则' : '新建考核规则'"
      v-model="dialogVisible"
      width="800px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规则名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入规则名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="评价范围" prop="evaluation_scope">
              <el-select v-model="formData.evaluation_scope" placeholder="请选择评价范围" style="width: 100%">
                <el-option
                  v-for="item in scopeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="规则描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="2"
            placeholder="请输入规则描述"
          />
        </el-form-item>

        <el-form-item label="评价关系" prop="relation_types">
          <el-checkbox-group v-model="formData.relation_types">
            <el-checkbox
              v-for="item in relationOptions"
              :key="item.value"
              :label="item.value"
            >
              {{ item.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最大评价人数" prop="max_evaluators_per_relation">
              <el-input-number
                v-model="formData.max_evaluators_per_relation"
                :min="1"
                :max="20"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最少评价人数" prop="min_evaluators_per_relation">
              <el-input-number
                v-model="formData.min_evaluators_per_relation"
                :min="1"
                :max="20"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="职位级别差距">
          <el-input-number
            v-model="formData.position_level_diff_limit"
            :min="0"
            :max="10"
            style="width: 200px"
          />
          <span class="form-tip">允许的职位级别差距，0表示必须同级</span>
        </el-form-item>

        <el-form-item label="特殊设置">
          <el-checkbox v-model="formData.allow_cross_department">允许跨部门评价</el-checkbox>
          <el-checkbox v-model="formData.allow_cross_unit">允许跨单位评价</el-checkbox>
          <el-checkbox v-model="formData.allow_self_evaluation">允许自评</el-checkbox>
        </el-form-item>

        <el-form-item label="权重配置">
          <div class="weight-config">
            <div
              v-for="relationType in formData.relation_types"
              :key="relationType"
              class="weight-item"
            >
              <span class="weight-label">{{ getRelationText(relationType) }}：</span>
              <el-input-number
                v-model="formData.relation_weights[relationType]"
                :min="0"
                :max="1"
                :step="0.1"
                :precision="2"
                size="small"
                style="width: 120px"
              />
            </div>
            <div class="weight-total">
              总权重：{{ totalWeight.toFixed(2) }}
              <el-tag :type="totalWeight === 1 ? 'success' : 'warning'">
                {{ totalWeight === 1 ? '正确' : '需调整' }}
              </el-tag>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="状态">
          <el-switch
            v-model="formData.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 权重配置对话框 -->
    <el-dialog
      title="权重配置详情"
      v-model="weightDialogVisible"
      width="500px"
    >
      <div v-if="selectedRule">
        <div class="weight-detail">
          <h4>{{ selectedRule.name }} - 权重分配</h4>
          <el-table :data="weightTableData" size="small">
            <el-table-column prop="relation" label="评价关系" />
            <el-table-column prop="weight" label="权重" />
            <el-table-column prop="percentage" label="百分比" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useEvaluationStore } from '@/stores/evaluation'
import type { EvaluationRule } from '@/types'

const evaluationStore = useEvaluationStore()

const dialogVisible = ref(false)
const weightDialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref()
const currentRule = ref<EvaluationRule | null>(null)
const selectedRule = ref<EvaluationRule | null>(null)

const formData = reactive({
  name: '',
  description: '',
  relation_types: [] as string[],
  evaluation_scope: 'department',
  max_evaluators_per_relation: 3,
  min_evaluators_per_relation: 1,
  relation_weights: {} as Record<string, number>,
  allow_cross_department: false,
  allow_cross_unit: false,
  allow_self_evaluation: false,
  position_level_diff_limit: 2,
  is_active: true
})

const scopeOptions = [
  { label: '本部门', value: 'department' },
  { label: '本单位', value: 'unit' },
  { label: '全公司', value: 'company' },
  { label: '跨部门', value: 'cross_department' },
  { label: '跨单位', value: 'cross_unit' },
  { label: '手动选择', value: 'manual' }
]

const relationOptions = [
  { label: '上级评下级', value: 'superior' },
  { label: '同级互评', value: 'peer' },
  { label: '下级评上级', value: 'subordinate' },
  { label: '自评', value: 'self' },
  { label: '跨部门上级', value: 'cross_superior' },
  { label: '跨部门同级', value: 'cross_peer' },
  { label: '自定义关系', value: 'custom' }
]

const formRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  evaluation_scope: [{ required: true, message: '请选择评价范围', trigger: 'change' }],
  relation_types: [{ required: true, message: '请选择至少一种评价关系', trigger: 'change' }],
  max_evaluators_per_relation: [{ required: true, message: '请输入最大评价人数', trigger: 'blur' }],
  min_evaluators_per_relation: [{ required: true, message: '请输入最少评价人数', trigger: 'blur' }]
}

const evaluationRules = computed(() => {
  const rules = evaluationStore.evaluationRules
  return Array.isArray(rules) ? rules : []
})
const loading = computed(() => evaluationStore.loading)

// 计算总权重
const totalWeight = computed(() => {
  return Object.values(formData.relation_weights).reduce((sum, weight) => sum + (weight || 0), 0)
})

// 权重表格数据
const weightTableData = computed(() => {
  if (!selectedRule.value || !selectedRule.value.relation_weights) return []
  
  return Object.entries(selectedRule.value.relation_weights).map(([relation, weight]) => ({
    relation: getRelationText(relation),
    weight: weight,
    percentage: `${(weight * 100).toFixed(1)}%`
  }))
})

// 监听评价关系变化，自动调整权重
watch(() => formData.relation_types, (newTypes) => {
  // 移除已删除关系的权重
  Object.keys(formData.relation_weights).forEach(key => {
    if (!newTypes.includes(key)) {
      delete formData.relation_weights[key]
    }
  })
  
  // 为新增关系添加默认权重
  newTypes.forEach(type => {
    if (!(type in formData.relation_weights)) {
      formData.relation_weights[type] = 1 / newTypes.length
    }
  })
}, { deep: true })

const getScopeText = (scope: string) => {
  const scopeMap = {
    'department': '本部门',
    'unit': '本单位',
    'company': '全公司',
    'cross_department': '跨部门',
    'cross_unit': '跨单位',
    'manual': '手动选择'
  }
  return scopeMap[scope as keyof typeof scopeMap] || scope
}

const getRelationText = (relation: string) => {
  const relationMap = {
    'superior': '上级评下级',
    'peer': '同级互评',
    'subordinate': '下级评上级',
    'self': '自评',
    'cross_superior': '跨部门上级',
    'cross_peer': '跨部门同级',
    'custom': '自定义关系'
  }
  return relationMap[relation as keyof typeof relationMap] || relation
}

const showCreateDialog = () => {
  isEdit.value = false
  currentRule.value = null
  resetForm()
  dialogVisible.value = true
}

const editRule = (rule: EvaluationRule) => {
  isEdit.value = true
  currentRule.value = rule
  formData.name = rule.name
  formData.description = rule.description
  formData.relation_types = [...rule.relation_types]
  formData.evaluation_scope = rule.evaluation_scope
  formData.max_evaluators_per_relation = rule.max_evaluators_per_relation
  formData.min_evaluators_per_relation = rule.min_evaluators_per_relation
  formData.relation_weights = { ...rule.relation_weights }
  formData.allow_cross_department = rule.allow_cross_department
  formData.allow_cross_unit = rule.allow_cross_unit
  formData.allow_self_evaluation = rule.allow_self_evaluation
  formData.position_level_diff_limit = rule.position_level_diff_limit
  formData.is_active = rule.is_active
  dialogVisible.value = true
}

const viewWeights = (rule: EvaluationRule) => {
  selectedRule.value = rule
  weightDialogVisible.value = true
}

const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.relation_types = []
  formData.evaluation_scope = 'department'
  formData.max_evaluators_per_relation = 3
  formData.min_evaluators_per_relation = 1
  formData.relation_weights = {}
  formData.allow_cross_department = false
  formData.allow_cross_unit = false
  formData.allow_self_evaluation = false
  formData.position_level_diff_limit = 2
  formData.is_active = true
  formRef.value?.clearValidate()
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()
    
    // 验证权重总和
    if (Math.abs(totalWeight.value - 1) > 0.01) {
      ElMessage.error('权重总和必须等于1.00')
      return
    }
    
    submitting.value = true
    
    if (isEdit.value && currentRule.value) {
      await evaluationStore.updateEvaluationRule(currentRule.value.id, formData)
      ElMessage.success('更新成功')
    } else {
      await evaluationStore.createEvaluationRule(formData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    await loadData()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

const toggleStatus = async (rule: EvaluationRule) => {
  try {
    const newStatus = !rule.is_active
    await evaluationStore.updateEvaluationRule(rule.id, { is_active: newStatus })
    ElMessage.success(`${newStatus ? '启用' : '禁用'}成功`)
    await loadData()
  } catch (error) {
    console.error('状态更新失败:', error)
    ElMessage.error('操作失败，请重试')
  }
}

const deleteRule = async (rule: EvaluationRule) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除规则"${rule.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await evaluationStore.deleteEvaluationRule(rule.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

const loadData = async () => {
  try {
    await evaluationStore.fetchEvaluationRules()
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.evaluation-rules {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.weight-config {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 12px;
  background-color: #fafafa;
}

.weight-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.weight-label {
  width: 120px;
  font-size: 14px;
}

.weight-total {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
  font-weight: bold;
}

.weight-detail h4 {
  margin-bottom: 16px;
  color: #409eff;
}
</style>