<template>
  <div class="organization-tree">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>组织架构树</span>
          <el-button type="primary" @click="refreshTree">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <div class="tree-container" v-loading="loading">
        <el-tree
          :data="departmentTree"
          :props="treeProps"
          node-key="id"
          default-expand-all
          :expand-on-click-node="false"
          class="department-tree"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <el-icon class="node-icon">
                <OfficeBuilding />
              </el-icon>
              <span class="node-label">{{ data.name }}</span>
              <el-tag size="small" class="node-tag">
                {{ data.employee_count || 0 }}人
              </el-tag>
            </div>
          </template>
        </el-tree>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Refresh, OfficeBuilding } from '@element-plus/icons-vue'
import { useOrganizationStore } from '@/stores/organization'

const organizationStore = useOrganizationStore()

const departmentTree = computed(() => organizationStore.departmentTree)
const loading = computed(() => organizationStore.loading)

const treeProps = {
  children: 'children',
  label: 'name'
}

const refreshTree = () => {
  organizationStore.fetchDepartmentTree()
}

onMounted(() => {
  organizationStore.fetchDepartmentTree()
})
</script>

<style scoped>
.organization-tree {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tree-container {
  min-height: 400px;
  padding: 20px;
}

.department-tree {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.tree-node {
  display: flex;
  align-items: center;
  flex: 1;
  padding: 4px 0;
}

.node-icon {
  margin-right: 8px;
  color: #409eff;
}

.node-label {
  flex: 1;
  font-size: 14px;
}

.node-tag {
  margin-left: 10px;
}
</style>