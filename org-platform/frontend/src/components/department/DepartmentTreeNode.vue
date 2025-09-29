<template>
  <div class="department-tree-node">
    <div 
      class="node-content" 
      :class="{ active: department.id === selectedId }"
      @click="$emit('select', department)"
    >
      <div class="node-toggle" @click.stop="toggleExpanded" v-if="hasChildren">
        <el-icon>
          <ArrowDown v-if="expanded" />
          <ArrowRight v-else />
        </el-icon>
      </div>
      <div class="node-icon">
        <el-icon><OfficeBuilding /></el-icon>
      </div>
      <div class="node-info">
        <div class="node-name">{{ department.name }}</div>
        <div class="node-meta">
          <span class="node-code">{{ department.code }}</span>
          <span class="node-count">{{ department.employee_count || 0 }}人</span>
        </div>
      </div>
      <div class="node-status">
        <div class="status-dot" :class="{ inactive: !department.is_active }"></div>
      </div>
      <div class="node-actions" @click.stop>
        <el-dropdown trigger="click">
          <el-button type="text" size="small">
            <el-icon><MoreFilled /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$emit('edit', department)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-dropdown-item>
              <el-dropdown-item @click="$emit('create-sub', department)">
                <el-icon><Plus /></el-icon>
                新增子部门
              </el-dropdown-item>
              <el-dropdown-item @click="$emit('delete', department)" divided>
                <el-icon><Delete /></el-icon>
                删除
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <div v-if="hasChildren && expanded" class="node-children">
      <DepartmentTreeNode
        v-for="child in department.children"
        :key="child.id"
        :department="child"
        :selected-id="selectedId"
        @select="$emit('select', $event)"
        @edit="$emit('edit', $event)"
        @create-sub="$emit('create-sub', $event)"
        @delete="$emit('delete', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  ArrowDown, 
  ArrowRight, 
  OfficeBuilding, 
  MoreFilled, 
  Edit, 
  Plus, 
  Delete 
} from '@element-plus/icons-vue'
import type { Department } from '@/types'

interface Props {
  department: Department
  selectedId?: number | null
}

const props = defineProps<Props>()

defineEmits<{
  select: [department: Department]
  edit: [department: Department]
  'create-sub': [department: Department]
  delete: [department: Department]
}>()

const expanded = ref(true)

const hasChildren = computed(() => {
  return props.department.children && props.department.children.length > 0
})

const toggleExpanded = () => {
  expanded.value = !expanded.value
}
</script>

<style scoped>
.department-tree-node {
  margin-bottom: 0.5rem;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.node-content:hover {
  background: #f8fafc;
  border-color: #e2e8f0;
}

.node-content.active {
  background: #ecfdf5;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgb(16 185 129 / 0.1);
}

.node-toggle {
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  cursor: pointer;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
}

.node-toggle:hover {
  background: #e5e7eb;
  color: #374151;
}

.node-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.125rem;
}

.node-info {
  flex: 1;
  min-width: 0;
}

.node-name {
  font-weight: 500;
  color: #111827;
  margin-bottom: 0.25rem;
}

.node-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.node-code {
  padding: 0.125rem 0.5rem;
  background: #f3f4f6;
  border-radius: 0.25rem;
}

.node-count {
  color: #059669;
  font-weight: 500;
}

.node-status {
  display: flex;
  align-items: center;
}

.status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.status-dot.inactive {
  background: #ef4444;
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.node-content:hover .node-actions {
  opacity: 1;
}

.node-children {
  margin-left: 2rem;
  padding-left: 1rem;
  border-left: 2px dashed #e5e7eb;
  margin-top: 0.5rem;
}
</style>