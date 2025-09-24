<template>
  <div class="container" style="padding:24px 16px">
    <!-- 标题/工具条 -->
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">权限管理</h3>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索用户/角色" clearable style="width:240px" @keyup.enter="reload" />
        <el-select v-model="role" placeholder="角色" filterable style="width:160px" @change="reload">
          <el-option label="全部" value="" />
          <el-option v-for="r in roles" :key="r" :label="r" :value="r" />
        </el-select>
        <el-select v-model="status" placeholder="状态" style="width:140px" @change="reload">
          <el-option label="全部" value="" />
          <el-option label="启用" value="enabled" />
          <el-option label="禁用" value="disabled" />
        </el-select>
        <el-button type="primary" @click="openAssign">分配权限</el-button>
      </div>
    </div>

    <!-- 列表卡片 -->
    <div class="card">
      <div class="table-wrap">
        <el-table :data="rows" v-loading="loading" border stripe>
          <el-table-column prop="user_name" label="用户" min-width="180" />
          <el-table-column prop="role" label="角色" width="160" />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.status==='enabled' ? 'success' : 'info'">{{ row.status==='enabled' ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" min-width="180" />
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <div class="toolbar">
                <el-button size="small" @click="view(row)">详情</el-button>
                <el-button size="small" type="primary" @click="edit(row)">编辑</el-button>
              </div>
            </template>
          </el-table-column>
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

    <!-- 分配/编辑 抽屉（示意） -->
    <el-drawer v-model="drawer" :title="mode==='assign'?'分配权限':'编辑权限'" size="460px">
      <el-form :model="form" label-width="100">
        <el-form-item label="用户">
          <el-input v-model="form.user_name" placeholder="用户名/邮箱" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" filterable style="width:100%">
            <el-option v-for="r in roles" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.enabled" active-text="启用" inactive-text="禁用" />
        </el-form-item>
        <el-form-item label="权限范围">
          <el-checkbox-group v-model="form.scopes">
            <el-checkbox label="查看" />
            <el-checkbox label="新增" />
            <el-checkbox label="编辑" />
            <el-checkbox label="删除" />
            <el-checkbox label="导出" />
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display:flex;gap:8px;justify-content:flex-end">
          <el-button @click="drawer=false">取消</el-button>
          <el-button type="primary" @click="save">保存</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 筛选
const keyword = ref('')
const role = ref('')
const status = ref('')
const roles = ref<string[]>(['管理员','人事','主管','员工'])

// 表格
const loading = ref(false)
const rows = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const size = ref(10)

const load = async () => {
  try {
    loading.value = true
    // TODO: 替换为真实权限接口：permissionsApi.list({ page,size,search:keyword.value,role:role.value,status:status.value })
    // 先用占位数据
    rows.value = [
      { user_name:'admin', role:'管理员', status:'enabled', updated_at:'2025-09-01 12:00' },
      { user_name:'wang', role:'员工', status:'enabled', updated_at:'2025-09-02 09:30' },
      { user_name:'li', role:'主管', status:'disabled', updated_at:'2025-09-03 10:15' },
    ]
    total.value = rows.value.length
  } finally { loading.value = false }
}

const reload = () => { page.value = 1; load() }
const onPageChange = (p:number) => { page.value = p; load() }

// 抽屉
const drawer = ref(false)
const mode = ref<'assign'|'edit'>('assign')
const form = ref<any>({ user_name:'', role:'员工', enabled:true, scopes:['查看'] })
const openAssign = () => { mode.value='assign'; form.value={ user_name:'', role:'员工', enabled:true, scopes:['查看'] }; drawer.value=true }
const view = (row:any) => { console.log('view', row) }
const edit = (row:any) => { mode.value='edit'; form.value={ user_name: row.user_name, role: row.role, enabled: row.status==='enabled', scopes:['查看','编辑'] }; drawer.value=true }
const save = () => { drawer.value=false /* TODO: permissionsApi.assign/update */ }

onMounted(load)
</script>
