<template>
  <div class="evaluation-indicators">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>考核指标管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建指标
          </el-button>
        </div>
      </template>

      <el-table :data="indicators" v-loading="loading">
        <el-table-column prop="name" label="指标名称" />
        <el-table-column prop="category" label="指标类别">
          <template #default="{ row }">
            <el-tag>{{ getCategoryText(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="weight" label="权重" />
        <el-table-column prop="max_score" label="最高分数" />
        <el-table-column prop="is_active" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small">编辑</el-button>
            <el-button size="small" type="danger">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { useEvaluationStore } from '@/stores/evaluation'

const evaluationStore = useEvaluationStore()
const indicators = computed(() => evaluationStore.indicators)
const loading = computed(() => evaluationStore.loading)

const getCategoryText = (category: string) => {
  const categoryMap = {
    'performance': '工作绩效',
    'ability': '工作能力',
    'attitude': '工作态度',
    'teamwork': '团队合作',
    'innovation': '创新能力'
  }
  return categoryMap[category as keyof typeof categoryMap] || category
}

const showCreateDialog = () => {
  // 实现创建指标对话框
}

onMounted(() => {
  evaluationStore.fetchIndicators()
})
</script>

<style scoped>
.evaluation-indicators {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>