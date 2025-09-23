<template>
  <div class="employees">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>员工管理</span>
          <el-button type="primary" @click="syncFromOrg">
            <el-icon><Refresh /></el-icon>
            从中台同步
          </el-button>
        </div>
      </template>

      <el-table :data="employees" v-loading="loading">
        <el-table-column prop="employee_id" label="员工号" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="department_name" label="部门" />
        <el-table-column prop="position_name" label="职位" />
        <el-table-column prop="position_level" label="职位级别" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="is_active" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { useEvaluationStore } from '@/stores/evaluation'

const evaluationStore = useEvaluationStore()
const employees = computed(() => evaluationStore.employees)
const loading = computed(() => evaluationStore.loading)

const syncFromOrg = async () => {
  try {
    await evaluationStore.syncEmployees()
    ElMessage.success('员工数据同步成功')
  } catch (error) {
    ElMessage.error('同步失败，请重试')
  }
}

onMounted(() => {
  evaluationStore.fetchEmployees()
})
</script>

<style scoped>
.employees {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>