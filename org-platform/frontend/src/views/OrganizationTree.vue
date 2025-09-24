<template>
  <div class="container">
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">组织架构树</h3>
      <div class="toolbar">
        <el-button type="primary" @click="refreshTree">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div class="card">
      <div class="tree-container" v-loading="loading">
        <el-tree
          :data="organizationTree"
          :props="treeProps"
          node-key="id"
          default-expand-all
          :expand-on-click-node="false"
          class="organization-tree-view"
        >
          <template #default="{ node, data }">
            <div class="tree-node" :class="`node-${data.type}`">
              <el-icon class="node-icon">
                <OfficeBuilding v-if="data.type === 'department'" />
                <User v-else />
              </el-icon>
              <span class="node-label">{{ data.name }}</span>
              <div class="node-info">
                <el-tag v-if="data.type === 'department'" size="small" class="node-tag">
                  {{ data.employee_count || 0 }}人
                </el-tag>
                <el-tag v-else size="small" :type="getPositionTagType(data.position_level)" class="position-tag">
                  {{ data.position_name }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-tree>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh, OfficeBuilding, User } from '@element-plus/icons-vue'
import { useOrganizationStore } from '@/stores/organization'

const organizationStore = useOrganizationStore()

const organizationTree = ref([])
const loading = ref(false)

const treeProps = {
  children: 'children',
  label: 'name'
}

// 根据职位级别返回标签类型
const getPositionTagType = (level: number) => {
  if (level >= 13) return 'danger'  // 高层正职
  if (level >= 11) return 'warning' // 高层
  if (level >= 7) return 'primary'  // 中层
  if (level >= 2) return 'success'  // 基层
  return 'info' // 员工
}

const refreshTree = async () => {
  try {
    loading.value = true
    const data = await organizationStore.fetchFullOrganizationTree()
    organizationTree.value = data
  } catch (error) {
    console.error('刷新组织架构树失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshTree()
})
</script>

<style scoped>
.organization-tree {
  padding: 20px;
}

.tree-container {
  min-height: 400px;
  padding: 20px;
}

.organization-tree-view {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.tree-node {
  display: flex;
  align-items: center;
  flex: 1;
  padding: 6px 0;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.tree-node:hover {
  background-color: #f0f9ff;
}

.node-department {
  font-weight: 600;
  color: #1f2937;
}

.node-employee {
  color: #4b5563;
  margin-left: 8px;
}

.node-icon {
  margin-right: 8px;
  font-size: 16px;
}

.node-department .node-icon {
  color: #3b82f6;
}

.node-employee .node-icon {
  color: #10b981;
}

.node-label {
  flex: 1;
  font-size: 14px;
}

.node-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-tag {
  font-size: 12px;
}

.position-tag {
  font-size: 12px;
  font-weight: 500;
}

/* 根据类型调整缩进 */
:deep(.el-tree-node__content) {
  height: auto;
  min-height: 32px;
  padding: 2px 0;
}

:deep(.el-tree-node__children .el-tree-node__content) {
  padding-left: 30px;
}

/* 员工节点的特殊样式 */
:deep(.node-employee) {
  background-color: #f8fafc;
  border-left: 3px solid #e2e8f0;
  padding-left: 8px;
  margin: 2px 0;
}
</style>