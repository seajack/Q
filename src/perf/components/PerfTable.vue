<template>
  <section class="mt-8">
    <div class="row">
      <h3 style="margin:0;font-size:16px">员工绩效</h3>
      <div class="toolbar">
        <span style="font-size:12px;color:#6b7280">每页</span>
        <select v-model.number="size" @change="onSizeChange" class="select">
          <option :value="5">5</option>
          <option :value="10">10</option>
          <option :value="20">20</option>
        </select>
        <span style="font-size:12px;color:#6b7280">条</span>
      </div>
    </div>

    <div class="table-wrap mt-6">
      <table>
        <thead>
          <tr>
            <th><button class="btn" @click="toggleSort('name')">员工 ▲▼</button></th>
            <th><button class="btn" @click="toggleSort('dept')">部门 ▲▼</button></th>
            <th><button class="btn" @click="toggleSort('target')">目标达成 ▲▼</button></th>
            <th><button class="btn" @click="toggleSort('grade')">评分 ▲▼</button></th>
            <th>状态</th>
            <th style="text-align:right">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r,i) in items" :key="r.id">
            <td>
              <div style="display:flex;align-items:center;gap:12px">
                <span :style="avatarStyle(r)">{{ r.name.charAt(0) }}</span>
                <div>
                  <div style="font-weight:600">{{ r.name }}</div>
                  <div style="font-size:12px;color:#6b7280">{{ r.role }}</div>
                </div>
              </div>
            </td>
            <td style="font-size:14px">{{ r.dept }}</td>
            <td style="font-size:14px">{{ r.target }}%</td>
            <td :style="{color:gradeColor(r),fontWeight:'600'}">{{ r.grade }}</td>
            <td><span class="badge" :style="badgeStyle(r)">{{ r.status }}</span></td>
            <td style="text-align:right">
              <div class="toolbar">
                <button class="btn" @click="$emit('view', r)">详情</button>
                <button class="btn btn-primary" @click="$emit('edit', r)">编辑</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="row" style="margin-top:12px;font-size:12px;color:#374151">
      <div>共 {{ total }} 人 · 第 {{ page }} 页</div>
      <div class="toolbar">
        <button class="btn" @click="prev">上一页</button>
        <button class="btn" @click="next">下一页</button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { ref } from 'vue';
import { usePerfStore } from '../stores/perf';

const store = usePerfStore();
const { items, total } = storeToRefs(store);
const page = storeToRefs(store).page;
const size = storeToRefs(store).size;
const sort = storeToRefs(store).sort;

const toggleSort = (k: 'name'|'dept'|'target'|'grade') => {
  // toggle asc/desc by prefix '-'
  const cur = sort.value;
  const isCur = cur.replace('-', '') === k;
  if (!isCur) sort.value = k;
  else sort.value = cur.startsWith('-') ? k : ('-' + k);
  store.loadList();
};

const onSizeChange = () => { store.page = 1; store.loadList(); };
const prev = () => { if (store.page > 1) { store.page -= 1; store.loadList(); } };
const next = () => { store.page += 1; store.loadList(); };

const avatarStyle = (r:any) => ({
  height:'32px', width:'32px', display:'inline-flex', alignItems:'center', justifyContent:'center', borderRadius:'8px', color:'#fff', fontWeight:'700',
  background: r.color==='emerald' ? 'linear-gradient(135deg, var(--brand-400), var(--brand-600))' : (r.color==='amber'?'linear-gradient(135deg, #f59e0b, #f97316)':'linear-gradient(135deg, #d946ef, #ec4899)')
});
const gradeColor = (r:any) => r.status==='已完成' ? '#047857' : (r.status==='进行中' ? '#b45309' : '#be123c');
const badgeStyle = (r:any) => r.status==='已完成' ? 'background:#ecfdf5;color:#047857' : (r.status==='进行中' ? 'background:#fffbeb;color:#b45309' : 'background:#fff1f2;color:#be123c');
</script>
