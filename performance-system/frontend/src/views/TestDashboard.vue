<template>
  <div class="test-dashboard">
    <h2>考核看板数据测试</h2>
    
    <div class="test-section">
      <h3>KPI数据</h3>
      <pre>{{ JSON.stringify(kpi, null, 2) }}</pre>
    </div>
    
    <div class="test-section">
      <h3>绩效排名数据</h3>
      <pre>{{ JSON.stringify(performanceRanking, null, 2) }}</pre>
    </div>
    
    <div class="test-section">
      <h3>考核周期数据</h3>
      <pre>{{ JSON.stringify(cycles, null, 2) }}</pre>
    </div>
    
    <div class="test-section">
      <h3>加载状态</h3>
      <p>加载中: {{ loading }}</p>
      <p>错误: {{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { statsApi, cycleApi, taskApi } from '@/utils/api'

const loading = ref(false)
const error = ref('')
const kpi = ref({})
const performanceRanking = ref([])
const cycles = ref([])

const loadData = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // 加载KPI数据
    const kpiRes = await statsApi.overview()
    kpi.value = kpiRes.data || {}
    console.log('KPI数据:', kpi.value)
    
    // 加载考核周期
    const cyclesRes = await cycleApi.list()
    cycles.value = cyclesRes.data.results || []
    console.log('考核周期:', cycles.value)
    
    // 加载绩效排名
    const tasksRes = await taskApi.list({ status: 'completed' })
    performanceRanking.value = tasksRes.data.results || []
    console.log('绩效排名:', performanceRanking.value)
    
  } catch (err) {
    error.value = err.message || '加载数据失败'
    console.error('加载数据失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.test-dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #f9f9f9;
}

.test-section h3 {
  margin-top: 0;
  color: #333;
}

pre {
  background: #fff;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  line-height: 1.4;
}
</style>
