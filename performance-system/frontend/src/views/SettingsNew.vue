<template>
  <div class="container" style="padding:24px 16px">
    <h3 style="margin:0 0 12px 0;font-size:16px">系统设置</h3>

    <!-- 基础信息 -->
    <div class="card" style="padding:16px; margin-bottom:16px">
      <h4 style="margin:0 0 12px 0;font-size:14px">基础信息</h4>
      <el-form :model="basic" label-width="120">
        <el-form-item label="系统名称">
          <el-input v-model="basic.name" placeholder="绩效考核系统" />
        </el-form-item>
        <el-form-item label="默认周期">
          <el-select v-model="basic.default_cycle" placeholder="选择周期" style="width:320px">
            <el-option v-for="c in cycles" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 品牌样式（预览） -->
    <div class="card" style="padding:16px; margin-bottom:16px">
      <h4 style="margin:0 0 12px 0;font-size:14px">品牌与外观</h4>
      <div style="display:flex; gap:12px; flex-wrap:wrap">
        <div class="swatch">
          <div class="swatch-color" style="background:var(--brand-400)"></div>
          <div class="swatch-name">brand-400</div>
        </div>
        <div class="swatch">
          <div class="swatch-color" style="background:var(--brand-600)"></div>
          <div class="swatch-name">brand-600</div>
        </div>
        <div class="swatch">
          <div class="swatch-color" style="background:var(--brand-700)"></div>
          <div class="swatch-name">brand-700</div>
        </div>
      </div>
      <p style="margin-top:12px;color:#6b7280;font-size:12px">如需调整品牌色，可修改 `src/newui/styles/brand.css` 中的 CSS 变量。</p>
    </div>

    <!-- 接口配置 -->
    <div class="card" style="padding:16px; margin-bottom:16px">
      <h4 style="margin:0 0 12px 0;font-size:14px">接口配置</h4>
      <el-form :model="api" label-width="120">
        <el-form-item label="绩效API Base">
          <el-input v-model="api.perf" placeholder="http://127.0.0.1:8002" />
        </el-form-item>
        <el-form-item label="组织中台API Base">
          <el-input v-model="api.org" placeholder="http://127.0.0.1:8001/api" />
        </el-form-item>
        <p style="margin:0;color:#6b7280;font-size:12px">说明：当前前端通过 Vite 代理访问 `/api` 与 `/org-api`，如需持久修改，请更新 `vite.config.ts`。</p>
      </el-form>
    </div>

    <!-- 操作区 -->
    <div class="card" style="padding:12px; display:flex; justify-content:flex-end; gap:8px">
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" @click="onSave">保存</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { cycleApi } from '@/utils/api'

const cycles = ref<any[]>([])
const basic = ref<any>({ name: '绩效考核系统', default_cycle: '' })
const api = ref<any>({ perf: 'http://127.0.0.1:8002', org: 'http://127.0.0.1:8001/api' })

onMounted(async () => {
  try {
    const res = await cycleApi.list()
    const list:any[] = (res.data?.results || res.data || []) as any[]
    cycles.value = list
    if (!basic.value.default_cycle && list.length) basic.value.default_cycle = list[0].id
  } catch(e) { console.error(e) }
})

const onSave = () => {
  // 这里可对接后端保存配置接口。暂作提示。
  console.log('保存设置', { basic: basic.value, api: api.value })
}
const onReset = () => {
  basic.value = { name: '绩效考核系统', default_cycle: basic.value.default_cycle }
  api.value = { perf: 'http://127.0.0.1:8002', org: 'http://127.0.0.1:8001/api' }
}
</script>

<style scoped>
.swatch { width: 92px; border:1px solid var(--border); border-radius:10px; overflow:hidden; background:#fff }
.swatch-color { height:48px }
.swatch-name { text-align:center; font-size:12px; padding:6px 0; color:#374151 }
</style>
