<template>
  <div class="container" style="padding:24px 16px">
    <!-- 标题/工具条 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">组织架构</h3>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索姓名/部门/职位" clearable style="width:240px" @keyup.enter="reload" />
        <el-select v-model="status" placeholder="状态" style="width:140px" @change="reload">
          <el-option label="全部" value="" />
          <el-option label="在职" value="active" />
          <el-option label="试用" value="probation" />
          <el-option label="离职" value="inactive" />
        </el-select>
        <el-button type="primary" @click="reload">查询</el-button>
      </div>
    </div>

    <div class="grid" style="grid-template-columns: 320px 1fr; gap:16px">
      <!-- 左侧组织树卡片 -->
      <div class="card" style="padding:12px">
        <div class="row" style="margin-bottom:8px">
          <strong>部门树</strong>
          <el-button text size="small" @click="expandAll">展开</el-button>
        </div>
        <div class="tree-wrap" style="max-height:520px;overflow:auto">
          <el-tree
            :data="deptTree"
            node-key="id"
            :props="{ label:'name', children:'children' }"
            :default-expanded-keys="expandedKeys"
            highlight-current
            @node-click="onNodeClick"
          >
            <template #default="{ node, data }">
              <div class="tree-node" :class="{ 'employee-node': data.type === 'employee' }">
                <div class="tree-node-main">
                  <span class="tree-node-name">{{ data.name }}</span>
                  <span v-if="data.type === 'department'" class="tree-node-count">{{ data.employee_count || 0 }} 人</span>
                  <span v-else-if="data.type === 'employee'" class="employee-info">
                    <span class="position-info">{{ data.position_name || '未分配' }}<span v-if="data.position_level" class="position-level"> L{{ data.position_level }}</span></span>
                  </span>
                </div>
                <p v-if="data.type === 'department' && data.children?.length" class="tree-node-meta">
                  子部门 {{ data.children.filter(child => child.type === 'department').length }}
                </p>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 右侧成员列表卡片 -->
      <div class="card">
        <div class="table-wrap">
          <el-table :data="rows" v-loading="loading" border stripe>
            <el-table-column prop="name" label="姓名" min-width="180">
              <template #default="{ row }">
                <div style="display:flex;align-items:center;gap:10px">
                  <span :style="avatar(row)">{{ (row.name||'?')[0] }}</span>
                  <div>
                    <div style="font-weight:600">{{ row.name }}</div>
                    <div style="font-size:12px;color:#6b7280">
                      {{ row.position_name || '-' }}<span v-if="row.position_level" style="color:#0ea5e9;font-weight:600;background:#e0f2fe;padding:1px 4px;border-radius:4px;margin-left:4px">L{{ row.position_level }}</span>
                    </div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="department_name" label="部门" min-width="180" />
            <el-table-column prop="email" label="邮箱" min-width="220" />
            <el-table-column prop="phone" label="电话" width="160" />
          </el-table>
        </div>
        <div class="row" style="padding:12px 16px">
          <el-pagination
            background
            layout="prev, pager, next"
            :current-page="page"
            :page-size="size"
            :total="total"
            @current-change="onPageChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { orgPlatformApi } from '@/utils/api'

const loading = ref(false)
const rows = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const size = ref(10)

const keyword = ref('')
const status = ref('')

const deptTree = ref<any[]>([])
const expandedKeys = ref<any[]>([])
const currentDept = ref<any>(null)

const loadTree = async () => {
  try {
    console.log('正在加载组织架构树...')
    const res = await orgPlatformApi.departments.fullTree()
    console.log('API响应:', res)
    
    // 处理不同的数据格式
    let data: any[] = []
    if (Array.isArray(res.data)) {
      data = res.data
    } else if (res.data && Array.isArray(res.data.results)) {
      data = res.data.results
    } else if (res.data && Array.isArray(res.data.data)) {
      data = res.data.data
    }
    
    console.log('解析后的数据:', data)
    console.log('数据类型:', typeof data, '是否为数组:', Array.isArray(data))
    
    if (data && data.length > 0) {
      deptTree.value = data
      expandedKeys.value = data.map((n: any) => n.id)
      console.log('组织架构树加载完成，节点数:', data.length)
    } else {
      console.warn('没有获取到组织架构数据')
      deptTree.value = []
      expandedKeys.value = []
    }
  } catch(e) { 
    console.error('加载组织架构树失败:', e)
    // 如果fullTree失败，尝试使用普通的tree API
    try {
      console.log('尝试使用普通tree API...')
      const res = await orgPlatformApi.departments.tree()
      let data: any[] = []
      if (Array.isArray(res.data)) {
        data = res.data
      } else if (res.data && Array.isArray(res.data.results)) {
        data = res.data.results
      }
      deptTree.value = data
      expandedKeys.value = data.map((n: any) => n.id)
      console.log('使用普通tree API成功，节点数:', data.length)
    } catch(e2) {
      console.error('普通tree API也失败:', e2)
      deptTree.value = []
      expandedKeys.value = []
    }
  }
}

const loadList = async () => {
  try {
    loading.value = true
    const params:any = { page: page.value, size: size.value }
    if (keyword.value) params.search = keyword.value
    if (status.value) params.status = status.value
    if (currentDept.value?.id) params.department_id = currentDept.value.id
    const res = await orgPlatformApi.employees.list(params)
    const data:any = res.data
    rows.value = data.results || data || []
    total.value = data.count ?? rows.value.length
  } finally {
    loading.value = false
  }
}

const reload = () => { page.value = 1; loadList() }
const onNodeClick = (node:any) => { 
  // 只有部门节点才能被选择
  if (node?.type === 'department') {
    currentDept.value = node; 
    reload() 
  }
}
const onPageChange = (p:number) => { page.value = p; loadList() }

const expandAll = () => { expandedKeys.value = collectIds(deptTree.value) }
const collectIds = (arr:any[]):any[] => arr.flatMap(n => [n.id, ...(n.children?collectIds(n.children):[])])

const statusText = (s:string)=> ({active:'在职', probation:'试用', inactive:'离职'} as any)[s] || s
const statusType = (s:string)=> ({active:'success', probation:'warning', inactive:'info'} as any)[s] || 'info'

const avatar = (r:any)=> ({ height:'28px', width:'28px', display:'inline-flex', alignItems:'center', justifyContent:'center', borderRadius:'8px', color:'#fff', fontWeight:'700', background:'linear-gradient(135deg,var(--brand-400),var(--brand-600))' })

onMounted(async () => { await loadTree(); await loadList(); })
</script>

<style scoped>
/* 确保树容器有足够宽度 */
.tree-wrap {
  min-width: 300px;
  width: 100%;
}

/* 确保树节点有足够空间 */
:deep(.el-tree) {
  width: 100%;
}

:deep(.el-tree-node__content) {
  width: 100%;
  min-height: 48px;
  padding: 0;
}

:deep(.el-tree-node__expand-icon) {
  margin-right: 8px;
}
.tree-node {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
  cursor: pointer;
  min-height: 48px;
  width: 100%;
  box-sizing: border-box;
}

.tree-node:hover {
  background-color: var(--el-color-primary-light-9);
}

.tree-node-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-height: 28px;
  width: 100%;
  box-sizing: border-box;
}

.tree-node-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
  font-size: 14px;
  flex: 1;
  min-width: 0;
  max-width: calc(100% - 80px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.tree-node-count {
  font-size: 12px;
  color: var(--el-text-color-regular);
  background-color: var(--el-color-primary-light-8);
  padding: 2px 6px;
  border-radius: 10px;
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 40px;
  text-align: center;
}

.tree-node-meta {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin: 0;
  line-height: 1.2;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 员工节点样式 */
.employee-node {
  background-color: #f0f9ff;
  border-left: 3px solid #0ea5e9;
  margin-left: 8px;
  border-radius: 6px;
  min-height: 48px;
  width: 100%;
  box-sizing: border-box;
}

.employee-node:hover {
  background-color: #e0f2fe;
}

.employee-info {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-size: 12px;
  flex-shrink: 0;
  min-width: 140px;
  max-width: 140px;
  width: 140px;
}

.position-info {
  color: #64748b;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100px;
  flex: 1;
  min-width: 0;
}

.position-level {
  color: #0ea5e9;
  font-weight: 600;
  background-color: #e0f2fe;
  padding: 1px 4px;
  border-radius: 4px;
  margin-left: 4px;
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 30px;
}
</style>
