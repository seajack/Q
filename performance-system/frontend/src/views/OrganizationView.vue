<template>
  <div class="organization-view">
    <el-card>
      <template #header>
        <span>组织架构视图（来自中台）</span>
      </template>
      
      <el-tree
        :data="departmentTree"
        :props="treeProps"
        default-expand-all
        class="org-tree"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <el-icon><OfficeBuilding /></el-icon>
            <span class="node-label">{{ data.name }}</span>
            <el-tag size="small">{{ data.employee_count }}人</el-tag>
          </div>
        </template>
      </el-tree>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { OfficeBuilding } from '@element-plus/icons-vue'
import { useEvaluationStore } from '@/stores/evaluation'

const evaluationStore = useEvaluationStore()
const departmentTree = computed(() => evaluationStore.orgDepartmentTree)

const treeProps = {
  children: 'children',
  label: 'name'
}

onMounted(() => {
  evaluationStore.fetchOrgDepartmentTree()
})
</script>

<style scoped>
.organization-view {
  padding: 20px;
}

.org-tree {
  margin-top: 20px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-label {
  flex: 1;
}
</style>