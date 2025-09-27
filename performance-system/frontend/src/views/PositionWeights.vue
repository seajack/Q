<template>
  <div class="container" style="padding:24px 16px">
    <div class="row" style="margin-bottom:12px">
      <h3 style="margin:0;font-size:16px">职级权重配置</h3>
      <div class="toolbar">
        <el-button type="primary" @click="loadDefaultWeights">获取默认权重</el-button>
        <el-button type="success" @click="openBatchUpdate">批量更新</el-button>
        <el-button type="warning" @click="reload">刷新</el-button>
      </div>
    </div>

    <div class="card">
      <div class="table-wrap">
        <el-table :data="rows" v-loading="loading" border stripe>
          <el-table-column prop="position_name" label="职位名称" min-width="200" />
          <el-table-column prop="position_level" label="职位级别" width="120">
            <template #default="{ row }">
              <el-tag :type="getLevelType(row.position_level)">
                {{ getLevelText(row.position_level) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="weight" label="权重" width="120">
            <template #default="{ row }">
              <el-input-number 
                v-model="row.weight" 
                :min="0.1" 
                :max="3.0" 
                :step="0.1" 
                :precision="2"
                size="small"
                @change="updateWeight(row)"
                :value-on-clear="1.0"
              />
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="100">
            <template #default="{ row }">
              <el-switch 
                v-model="row.is_active" 
                @change="updateStatus(row)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-tooltip content="编辑权重配置" placement="top">
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="edit(row)"
                    :icon="Edit"
                    class="action-btn edit-btn"
                  >
                    编辑
                  </el-button>
                </el-tooltip>
                <el-tooltip content="删除权重配置" placement="top">
                  <el-popconfirm 
                    title="确认删除该权重配置？" 
                    @confirm="onDelete(row)"
                    confirm-button-text="确认删除"
                    cancel-button-text="取消"
                    confirm-button-type="danger"
                  >
                    <template #reference>
                      <el-button 
                        size="small" 
                        type="danger" 
                        :icon="Delete"
                        class="action-btn delete-btn"
                      >
                        删除
                      </el-button>
                    </template>
                  </el-popconfirm>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div class="row" style="padding:12px 16px">
        <div class="toolbar" style="gap:6px">
          <span style="font-size:12px;color:#6b7280">每页</span>
          <el-select v-model="pageSize" size="small" style="width:90px" @change="reload">
            <el-option :value="10" label="10" />
            <el-option :value="20" label="20" />
            <el-option :value="50" label="50" />
            <el-option :value="100" label="100" />
          </el-select>
          <span style="font-size:12px;color:#6b7280">条</span>
        </div>
        <el-pagination
          background
          layout="prev, pager, next"
          :current-page="page"
          :page-size="pageSize"
          :total="total"
          @current-change="onPageChange"
        />
      </div>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="drawer" :title="mode==='create'?'新增权重':'编辑权重'" size="520px">
      <el-form :model="form" label-width="100" :rules="formRules" ref="formRef">
        <el-form-item label="职位名称" prop="position_name">
          <el-input v-model="form.position_name" placeholder="请输入职位名称" />
        </el-form-item>
        <el-form-item label="职位级别" prop="position_level">
          <el-input-number v-model="form.position_level" :min="0" :max="20" />
        </el-form-item>
        <el-form-item label="权重" prop="weight">
          <el-input-number v-model="form.weight" :min="0.1" :max="3.0" :step="0.1" :precision="2" />
        </el-form-item>
        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="toolbar">
          <el-button @click="drawer=false">取消</el-button>
          <el-button type="primary" @click="save" :loading="saving">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量更新对话框 -->
    <el-dialog v-model="batchDialog" title="批量更新权重" width="800px">
      <div v-if="defaultWeights.length > 0">
        <p style="margin-bottom: 16px; color: #666;">找到 {{ defaultWeights.length }} 个职位的默认权重配置</p>
        <el-table :data="defaultWeights" border stripe>
          <el-table-column prop="position_name" label="职位名称" min-width="200" />
          <el-table-column prop="position_level" label="职位级别" width="120">
            <template #default="{ row }">
              <el-tag :type="getLevelType(row.position_level)">
                {{ getLevelText(row.position_level) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="suggested_weight" label="建议权重" width="120" />
          <el-table-column prop="current_weight" label="当前权重" width="120">
            <template #default="{ row }">
              <span v-if="row.current_weight">{{ row.current_weight }}</span>
              <span v-else style="color: #999;">未设置</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button 
                size="small" 
                type="primary" 
                @click="applyWeight(row)"
                :disabled="row.current_weight === row.suggested_weight"
              >
                应用
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-else class="text-center" style="padding: 40px;">
        <p style="margin-bottom: 16px; color: #999;">暂无默认权重数据</p>
        <el-button type="primary" @click="loadDefaultWeights" :loading="loading">加载默认权重</el-button>
      </div>
      <template #footer>
        <div class="toolbar">
          <el-button @click="batchDialog=false">关闭</el-button>
          <el-button type="success" @click="batchApplyAll" :loading="batchSaving">全部应用</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete } from '@element-plus/icons-vue'
import { positionWeightApi } from '@/utils/api'

const loading = ref(false)
const saving = ref(false)
const batchSaving = ref(false)
const rows = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const drawer = ref(false)
const mode = ref<'create'|'edit'>('create')
const form = ref<any>({ position_name:'', position_level:0, weight:1.0, is_active:true })
const formRef = ref()

const batchDialog = ref(false)
const defaultWeights = ref<any[]>([])

const formRules = {
  position_name: [{ required: true, message: '请输入职位名称', trigger: 'blur' }],
  position_level: [{ required: true, message: '请输入职位级别', trigger: 'blur' }],
  weight: [{ required: true, message: '请输入权重', trigger: 'blur' }]
}

const load = async () => {
  try {
    loading.value = true
    const params: any = { page: page.value, page_size: pageSize.value }
    const res = await positionWeightApi.list(params)
    const data: any = res.data
    console.log('API响应数据:', res.data)
    
    // 处理数据，确保weight字段是数字类型
    const processedRows = (data.results || data || []).map((row: any) => ({
      ...row,
      weight: typeof row.weight === 'string' ? parseFloat(row.weight) : row.weight,
      position_level: typeof row.position_level === 'string' ? parseInt(row.position_level) : row.position_level
    }))
    
    rows.value = processedRows
    total.value = data.count ?? rows.value.length
    console.log('处理后的数据:', rows.value)
    console.log('职位名称示例:', rows.value[0]?.position_name)
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载失败')
  } finally { 
    loading.value = false 
  }
}

const reload = () => { 
  page.value = 1
  load() 
}

const onPageChange = (p: number) => { 
  page.value = p
  load() 
}

const getLevelType = (level: number) => {
  if (level >= 8) return 'danger'
  if (level >= 6) return 'warning'
  if (level >= 4) return 'primary'
  if (level >= 2) return 'success'
  return 'info'
}

const getLevelText = (level: number) => {
  if (level >= 13) return '高层正职'
  if (level >= 11) return '高层副职'
  if (level >= 9) return '中层正职'
  if (level >= 8) return '中层副职'
  if (level >= 4) return '基层正职'
  if (level >= 2) return '基层副职'
  return '普通员工'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const updateWeight = async (row: any) => {
  try {
    await positionWeightApi.update(row.id, { weight: row.weight })
    ElMessage.success('权重更新成功')
  } catch (error) {
    ElMessage.error('权重更新失败')
  }
}

const updateStatus = async (row: any) => {
  try {
    await positionWeightApi.update(row.id, { is_active: row.is_active })
    ElMessage.success('状态更新成功')
  } catch (error) {
    ElMessage.error('状态更新失败')
  }
}

const openCreate = () => {
  mode.value = 'create'
  form.value = { position_name:'', position_level:0, weight:1.0, is_active:true }
  drawer.value = true
}

const edit = (row: any) => {
  mode.value = 'edit'
  form.value = { ...row }
  drawer.value = true
}

const save = async () => {
  try {
    if (!formRef.value) return
    const valid = await formRef.value.validate()
    if (!valid) return

    saving.value = true
    if (mode.value === 'create') {
      await positionWeightApi.create(form.value)
      ElMessage.success('新增成功')
    } else {
      await positionWeightApi.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    }
    drawer.value = false
    reload()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const onDelete = async (row: any) => {
  try {
    await positionWeightApi.delete(row.id)
    ElMessage.success('删除成功')
    reload()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const loadDefaultWeights = async () => {
  try {
    loading.value = true
    console.log('正在获取默认权重...')
    const res = await positionWeightApi.getDefaultWeights()
    console.log('API响应:', res.data)
    
    // 处理默认权重数据，确保数字类型正确
    const processedWeights = (res.data.default_weights || []).map((item: any) => ({
      ...item,
      suggested_weight: typeof item.suggested_weight === 'string' ? parseFloat(item.suggested_weight) : item.suggested_weight,
      current_weight: typeof item.current_weight === 'string' ? parseFloat(item.current_weight) : item.current_weight,
      position_level: typeof item.position_level === 'string' ? parseInt(item.position_level) : item.position_level
    }))
    
    defaultWeights.value = processedWeights
    console.log('默认权重数据:', defaultWeights.value)
    batchDialog.value = true
    ElMessage.success(`成功获取 ${defaultWeights.value.length} 个职位的默认权重`)
  } catch (error) {
    console.error('获取默认权重失败:', error)
    ElMessage.error(`获取默认权重失败: ${error.response?.data?.error || error.message}`)
  } finally {
    loading.value = false
  }
}

const openBatchUpdate = () => {
  if (defaultWeights.value.length === 0) {
    loadDefaultWeights()
  } else {
    batchDialog.value = true
  }
}

const applyWeight = async (row: any) => {
  try {
    await positionWeightApi.create({
      position_id: row.position_id,
      position_name: row.position_name,
      position_level: row.position_level,
      weight: row.suggested_weight,
      is_active: true
    })
    ElMessage.success('权重应用成功')
    row.current_weight = row.suggested_weight
  } catch (error) {
    ElMessage.error('权重应用失败')
  }
}

const batchApplyAll = async () => {
  try {
    batchSaving.value = true
    const weights = defaultWeights.value.map(row => ({
      position_id: row.position_id,
      position_name: row.position_name,
      position_level: row.position_level,
      weight: row.suggested_weight,
      is_active: true
    }))
    
    await positionWeightApi.bulkUpdate({ weights })
    ElMessage.success('批量更新成功')
    batchDialog.value = false
    reload()
  } catch (error) {
    ElMessage.error('批量更新失败')
  } finally {
    batchSaving.value = false
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.action-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: center;
  padding: 4px 0;
}

.action-btn {
  min-width: 70px;
  height: 32px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 6px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.action-btn:hover::before {
  left: 100%;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.edit-btn {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: none;
  color: white;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
}

.edit-btn:hover {
  background: linear-gradient(135deg, #66b1ff 0%, #409eff 100%);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.delete-btn {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
  border: none;
  color: white;
  box-shadow: 0 2px 4px rgba(245, 108, 108, 0.3);
}

.delete-btn:hover {
  background: linear-gradient(135deg, #f78989 0%, #f56c6c 100%);
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.4);
}

.action-btn:active {
  transform: translateY(0);
  transition: all 0.1s;
}
</style>
