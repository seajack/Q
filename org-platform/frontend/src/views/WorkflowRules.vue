<template>
  <div class="workflow-rules">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>工作流规则管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="showAddDialog = true">
              新增规则
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 规则筛选 -->
      <el-row class="filter-row">
        <el-col :span="6">
          <el-select v-model="selectedType" placeholder="选择规则类型" @change="loadRules">
            <el-option label="全部" value="" />
            <el-option label="审批流程" value="approval" />
            <el-option label="通知规则" value="notification" />
            <el-option label="数据同步" value="sync" />
            <el-option label="权限控制" value="permission" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索规则名称"
            @input="handleSearch"
            clearable
          />
        </el-col>
        <el-col :span="6">
          <el-button @click="loadRules">刷新</el-button>
        </el-col>
      </el-row>
      
      <!-- 规则列表 -->
      <el-table :data="rules" v-loading="loading" style="margin-top: 20px">
        <el-table-column prop="name" label="规则名称" width="200" />
        <el-table-column prop="description" label="描述" width="300" />
        <el-table-column prop="rule_type" label="规则类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeType(row.rule_type)">
              {{ getTypeName(row.rule_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="editRule(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteRule(row)">删除</el-button>
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
    
    <!-- 新增/编辑规则对话框 -->
    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑规则' : '新增规则'" width="800px">
      <el-form :model="ruleForm" label-width="120px" :rules="ruleRules" ref="ruleFormRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规则名称" prop="name">
              <el-input v-model="ruleForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规则类型" prop="rule_type">
              <el-select v-model="ruleForm.rule_type">
                <el-option label="审批流程" value="approval" />
                <el-option label="通知规则" value="notification" />
                <el-option label="数据同步" value="sync" />
                <el-option label="权限控制" value="permission" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-input-number v-model="ruleForm.priority" :min="1" :max="100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否启用">
              <el-switch v-model="ruleForm.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="描述">
          <el-input v-model="ruleForm.description" type="textarea" />
        </el-form-item>
        
        <el-form-item label="触发条件">
          <el-input v-model="triggerConditionsText" type="textarea" placeholder="请输入JSON格式的触发条件" />
        </el-form-item>
        
        <el-form-item label="动作配置">
          <el-input v-model="actionConfigText" type="textarea" placeholder="请输入JSON格式的动作配置" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { workflowApi } from '@/utils/api'

const rules = ref([])
const loading = ref(false)
const selectedType = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showAddDialog = ref(false)
const isEdit = ref(false)

const ruleForm = reactive({
  name: '',
  description: '',
  rule_type: 'approval',
  priority: 1,
  trigger_conditions: {},
  action_config: {},
  is_active: true
})

const triggerConditionsText = ref('')
const actionConfigText = ref('')

const ruleRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  rule_type: [{ required: true, message: '请选择规则类型', trigger: 'change' }],
  priority: [{ required: true, message: '请输入优先级', trigger: 'blur' }]
}

const loadRules = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...(selectedType.value && { rule_type: selectedType.value }),
      ...(searchKeyword.value && { search: searchKeyword.value })
    }
    const response = await workflowApi.getRules(params)
    rules.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error('加载规则失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadRules()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadRules()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadRules()
}

const getTypeType = (type: string) => {
  const types = {
    approval: 'primary',
    notification: 'success',
    sync: 'warning',
    permission: 'danger'
  }
  return types[type] || 'default'
}

const getTypeName = (type: string) => {
  const names = {
    approval: '审批流程',
    notification: '通知规则',
    sync: '数据同步',
    permission: '权限控制'
  }
  return names[type] || type
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const editRule = (rule: any) => {
  isEdit.value = true
  Object.assign(ruleForm, rule)
  triggerConditionsText.value = JSON.stringify(rule.trigger_conditions, null, 2)
  actionConfigText.value = JSON.stringify(rule.action_config, null, 2)
  showAddDialog.value = true
}

const deleteRule = async (rule: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个规则吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await workflowApi.deleteRule(rule.id)
    ElMessage.success('删除成功')
    loadRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveRule = async () => {
  try {
    // 解析JSON配置
    if (triggerConditionsText.value) {
      ruleForm.trigger_conditions = JSON.parse(triggerConditionsText.value)
    }
    if (actionConfigText.value) {
      ruleForm.action_config = JSON.parse(actionConfigText.value)
    }
    
    if (isEdit.value) {
      await workflowApi.updateRule(ruleForm.id, ruleForm)
    } else {
      await workflowApi.createRule(ruleForm)
    }
    ElMessage.success('保存成功')
    showAddDialog.value = false
    loadRules()
  } catch (error) {
    ElMessage.error('保存失败，请检查JSON格式')
  }
}

onMounted(() => {
  loadRules()
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
