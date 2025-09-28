<template>
  <div class="custom-report-builder">
    <!-- 构建器头部 -->
    <div class="builder-header">
      <div class="header-left">
        <h3>自定义报表构建器</h3>
        <p>拖拽组件到画布中，构建您的专属报表</p>
      </div>
      <div class="header-actions">
        <el-button @click="previewReport">预览报表</el-button>
        <el-button type="primary" @click="saveReport">保存报表</el-button>
        <el-button type="success" @click="exportReport">导出报表</el-button>
      </div>
    </div>

    <div class="builder-content">
      <!-- 组件库 -->
      <div class="component-library">
        <h4>组件库</h4>
        <div class="component-categories">
          <div class="category">
            <h5>基础组件</h5>
            <div class="component-list">
              <div 
                v-for="component in basicComponents" 
                :key="component.type"
                class="component-item"
                draggable="true"
                @dragstart="onDragStart($event, component)"
              >
                <el-icon :size="20">
                  <component :is="component.icon" />
                </el-icon>
                <span>{{ component.name }}</span>
              </div>
            </div>
          </div>
          
          <div class="category">
            <h5>图表组件</h5>
            <div class="component-list">
              <div 
                v-for="component in chartComponents" 
                :key="component.type"
                class="component-item"
                draggable="true"
                @dragstart="onDragStart($event, component)"
              >
                <el-icon :size="20">
                  <component :is="component.icon" />
                </el-icon>
                <span>{{ component.name }}</span>
              </div>
            </div>
          </div>
          
          <div class="category">
            <h5>数据组件</h5>
            <div class="component-list">
              <div 
                v-for="component in dataComponents" 
                :key="component.type"
                class="component-item"
                draggable="true"
                @dragstart="onDragStart($event, component)"
              >
                <el-icon :size="20">
                  <component :is="component.icon" />
                </el-icon>
                <span>{{ component.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 画布区域 -->
      <div class="canvas-area">
        <div 
          class="report-canvas"
          @drop="onDrop"
          @dragover="onDragOver"
          @dragenter="onDragEnter"
        >
          <div v-if="reportComponents.length === 0" class="empty-canvas">
            <el-icon :size="48" color="#c0c4cc"><DocumentAdd /></el-icon>
            <p>拖拽组件到这里开始构建报表</p>
          </div>
          
          <div 
            v-for="(component, index) in reportComponents" 
            :key="component.id"
            class="canvas-component"
            :class="{ active: selectedComponent?.id === component.id }"
            @click="selectComponent(component)"
          >
            <div class="component-header">
              <span class="component-title">{{ component.name }}</span>
              <div class="component-actions">
                <el-button size="small" type="text" @click="configureComponent(component)">
                  <el-icon><Setting /></el-icon>
                </el-button>
                <el-button size="small" type="text" @click="duplicateComponent(component)">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
                <el-button size="small" type="text" @click="removeComponent(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            
            <div class="component-content">
              <!-- KPI卡片组件 -->
              <div v-if="component.type === 'kpi-card'" class="kpi-preview">
                <div class="kpi-item">
                  <div class="kpi-label">{{ component.config.title || 'KPI指标' }}</div>
                  <div class="kpi-value">{{ component.config.value || '85%' }}</div>
                </div>
              </div>
              
              <!-- 图表组件 -->
              <div v-else-if="component.type.startsWith('chart-')" class="chart-preview">
                <div class="chart-placeholder">
                  <el-icon :size="32" :color="component.config.color || '#409eff'">
                    <component :is="component.icon" />
                  </el-icon>
                  <p>{{ component.name }}</p>
                </div>
              </div>
              
              <!-- 表格组件 -->
              <div v-else-if="component.type === 'data-table'" class="table-preview">
                <div class="table-header">
                  <div class="header-cell">姓名</div>
                  <div class="header-cell">部门</div>
                  <div class="header-cell">评分</div>
                </div>
                <div class="table-row">
                  <div class="table-cell">张三</div>
                  <div class="table-cell">技术部</div>
                  <div class="table-cell">B+</div>
                </div>
              </div>
              
              <!-- 文本组件 -->
              <div v-else-if="component.type === 'text'" class="text-preview">
                <h4>{{ component.config.title || '标题' }}</h4>
                <p>{{ component.config.content || '文本内容' }}</p>
              </div>
              
              <!-- 图片组件 -->
              <div v-else-if="component.type === 'image'" class="image-preview">
                <div class="image-placeholder">
                  <el-icon :size="32" color="#c0c4cc"><Picture /></el-icon>
                  <p>图片组件</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 属性面板 -->
      <div class="property-panel">
        <h4>属性设置</h4>
        <div v-if="selectedComponent" class="property-content">
          <el-form :model="selectedComponent.config" label-width="80px">
            <el-form-item label="组件名称">
              <el-input v-model="selectedComponent.name" />
            </el-form-item>
            
            <!-- KPI卡片配置 -->
            <template v-if="selectedComponent.type === 'kpi-card'">
              <el-form-item label="标题">
                <el-input v-model="selectedComponent.config.title" />
              </el-form-item>
              <el-form-item label="数值">
                <el-input v-model="selectedComponent.config.value" />
              </el-form-item>
              <el-form-item label="颜色">
                <el-color-picker v-model="selectedComponent.config.color" />
              </el-form-item>
            </template>
            
            <!-- 图表配置 -->
            <template v-else-if="selectedComponent.type.startsWith('chart-')">
              <el-form-item label="图表标题">
                <el-input v-model="selectedComponent.config.title" />
              </el-form-item>
              <el-form-item label="数据源">
                <el-select v-model="selectedComponent.config.dataSource" placeholder="选择数据源">
                  <el-option label="绩效数据" value="performance" />
                  <el-option label="完成率数据" value="completion" />
                  <el-option label="评分数据" value="scores" />
                </el-select>
              </el-form-item>
              <el-form-item label="图表类型">
                <el-select v-model="selectedComponent.config.chartType" placeholder="选择图表类型">
                  <el-option label="柱状图" value="bar" />
                  <el-option label="折线图" value="line" />
                  <el-option label="饼图" value="pie" />
                  <el-option label="雷达图" value="radar" />
                </el-select>
              </el-form-item>
            </template>
            
            <!-- 表格配置 -->
            <template v-else-if="selectedComponent.type === 'data-table'">
              <el-form-item label="表格标题">
                <el-input v-model="selectedComponent.config.title" />
              </el-form-item>
              <el-form-item label="显示列">
                <el-checkbox-group v-model="selectedComponent.config.columns">
                  <el-checkbox value="name">姓名</el-checkbox>
                  <el-checkbox value="department">部门</el-checkbox>
                  <el-checkbox value="score">评分</el-checkbox>
                  <el-checkbox value="completion">完成度</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="分页大小">
                <el-input-number v-model="selectedComponent.config.pageSize" :min="10" :max="100" />
              </el-form-item>
            </template>
            
            <!-- 文本配置 -->
            <template v-else-if="selectedComponent.type === 'text'">
              <el-form-item label="标题">
                <el-input v-model="selectedComponent.config.title" />
              </el-form-item>
              <el-form-item label="内容">
                <el-input 
                  v-model="selectedComponent.config.content" 
                  type="textarea" 
                  :rows="4"
                />
              </el-form-item>
              <el-form-item label="字体大小">
                <el-input-number v-model="selectedComponent.config.fontSize" :min="12" :max="24" />
              </el-form-item>
            </template>
          </el-form>
        </div>
        <div v-else class="no-selection">
          <p>请选择一个组件进行配置</p>
        </div>
      </div>
    </div>

    <!-- 组件配置对话框 -->
    <el-dialog
      v-model="showConfigDialog"
      :title="`配置 ${currentConfigComponent?.name}`"
      width="600px"
    >
      <div v-if="currentConfigComponent" class="config-content">
        <el-form :model="currentConfigComponent.config" label-width="100px">
          <!-- 根据组件类型显示不同的配置选项 -->
          <template v-if="currentConfigComponent.type === 'kpi-card'">
            <el-form-item label="KPI标题">
              <el-input v-model="currentConfigComponent.config.title" />
            </el-form-item>
            <el-form-item label="数值">
              <el-input v-model="currentConfigComponent.config.value" />
            </el-form-item>
            <el-form-item label="单位">
              <el-input v-model="currentConfigComponent.config.unit" />
            </el-form-item>
            <el-form-item label="背景色">
              <el-color-picker v-model="currentConfigComponent.config.backgroundColor" />
            </el-form-item>
            <el-form-item label="文字色">
              <el-color-picker v-model="currentConfigComponent.config.textColor" />
            </el-form-item>
          </template>
          
          <template v-else-if="currentConfigComponent.type.startsWith('chart-')">
            <el-form-item label="图表标题">
              <el-input v-model="currentConfigComponent.config.title" />
            </el-form-item>
            <el-form-item label="数据源">
              <el-select v-model="currentConfigComponent.config.dataSource" style="width: 100%">
                <el-option label="绩效数据" value="performance" />
                <el-option label="完成率数据" value="completion" />
                <el-option label="评分数据" value="scores" />
                <el-option label="部门数据" value="department" />
              </el-select>
            </el-form-item>
            <el-form-item label="图表类型">
              <el-select v-model="currentConfigComponent.config.chartType" style="width: 100%">
                <el-option label="柱状图" value="bar" />
                <el-option label="折线图" value="line" />
                <el-option label="饼图" value="pie" />
                <el-option label="雷达图" value="radar" />
                <el-option label="散点图" value="scatter" />
              </el-select>
            </el-form-item>
            <el-form-item label="显示图例">
              <el-switch v-model="currentConfigComponent.config.showLegend" />
            </el-form-item>
            <el-form-item label="显示数据标签">
              <el-switch v-model="currentConfigComponent.config.showLabel" />
            </el-form-item>
          </template>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="showConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存配置</el-button>
      </template>
    </el-dialog>

    <!-- 报表预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      title="报表预览"
      width="90%"
      :close-on-click-modal="false"
    >
      <div class="report-preview">
        <div class="preview-header">
          <h3>{{ reportTitle }}</h3>
          <p>{{ reportDescription }}</p>
        </div>
        
        <div class="preview-content">
          <div 
            v-for="component in reportComponents" 
            :key="component.id"
            class="preview-component"
          >
            <!-- 这里渲染实际的组件内容 -->
            <div class="component-title">{{ component.name }}</div>
            <div class="component-preview">
              <p>组件预览内容...</p>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
        <el-button type="primary" @click="exportReport">导出报表</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { 
  DocumentAdd, 
  Setting, 
  CopyDocument, 
  Delete, 
  Picture,
  DataAnalysis,
  PieChart,
  TrendCharts,
  Document,
  Histogram
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const reportComponents = ref<any[]>([])
const selectedComponent = ref<any>(null)
const showConfigDialog = ref(false)
const showPreviewDialog = ref(false)
const currentConfigComponent = ref<any>(null)

const reportTitle = ref('自定义报表')
const reportDescription = ref('通过拖拽组件构建的个性化报表')

// 组件库数据
const basicComponents = ref([
  { type: 'kpi-card', name: 'KPI卡片', icon: DataAnalysis },
  { type: 'text', name: '文本', icon: Document },
  { type: 'image', name: '图片', icon: Picture }
])

const chartComponents = ref([
  { type: 'chart-bar', name: '柱状图', icon: Histogram },
  { type: 'chart-line', name: '折线图', icon: TrendCharts },
  { type: 'chart-pie', name: '饼图', icon: PieChart },
  { type: 'chart-radar', name: '雷达图', icon: DataAnalysis },
  { type: 'chart-histogram', name: '直方图', icon: Histogram }
])

const dataComponents = ref([
  { type: 'data-table', name: '数据表格', icon: Document },
  { type: 'data-list', name: '数据列表', icon: Document }
])

// 方法
const onDragStart = (event: DragEvent, component: any) => {
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/json', JSON.stringify(component))
  }
}

const onDragOver = (event: DragEvent) => {
  event.preventDefault()
}

const onDragEnter = (event: DragEvent) => {
  event.preventDefault()
}

const onDrop = (event: DragEvent) => {
  event.preventDefault()
  
  try {
    const componentData = JSON.parse(event.dataTransfer?.getData('application/json') || '{}')
    if (componentData.type) {
      addComponent(componentData)
    }
  } catch (error) {
    console.error('拖拽数据解析失败:', error)
  }
}

const addComponent = (componentTemplate: any) => {
  const newComponent = {
    id: `component_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    type: componentTemplate.type,
    name: componentTemplate.name,
    icon: componentTemplate.icon,
    config: getDefaultConfig(componentTemplate.type)
  }
  
  reportComponents.value.push(newComponent)
  ElMessage.success(`已添加 ${componentTemplate.name} 组件`)
}

const getDefaultConfig = (type: string) => {
  const configs: Record<string, any> = {
    'kpi-card': {
      title: 'KPI指标',
      value: '85%',
      unit: '%',
      backgroundColor: '#409eff',
      textColor: '#ffffff'
    },
    'chart-bar': {
      title: '柱状图',
      dataSource: 'performance',
      chartType: 'bar',
      showLegend: true,
      showLabel: false
    },
    'chart-line': {
      title: '折线图',
      dataSource: 'performance',
      chartType: 'line',
      showLegend: true,
      showLabel: false
    },
    'chart-pie': {
      title: '饼图',
      dataSource: 'performance',
      chartType: 'pie',
      showLegend: true,
      showLabel: true
    },
    'data-table': {
      title: '数据表格',
      columns: ['name', 'department', 'score'],
      pageSize: 20
    },
    'text': {
      title: '标题',
      content: '文本内容',
      fontSize: 16
    }
  }
  
  return configs[type] || {}
}

const selectComponent = (component: any) => {
  selectedComponent.value = component
}

const configureComponent = (component: any) => {
  currentConfigComponent.value = component
  showConfigDialog.value = true
}

const duplicateComponent = (component: any) => {
  const duplicatedComponent = {
    ...component,
    id: `component_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    name: `${component.name} (副本)`
  }
  
  const index = reportComponents.value.findIndex(c => c.id === component.id)
  reportComponents.value.splice(index + 1, 0, duplicatedComponent)
  ElMessage.success('组件已复制')
}

const removeComponent = (index: number) => {
  reportComponents.value.splice(index, 1)
  if (selectedComponent.value && selectedComponent.value.id === reportComponents.value[index]?.id) {
    selectedComponent.value = null
  }
  ElMessage.success('组件已删除')
}

const saveConfig = () => {
  ElMessage.success('配置已保存')
  showConfigDialog.value = false
}

const previewReport = () => {
  if (reportComponents.value.length === 0) {
    ElMessage.warning('请先添加组件到报表中')
    return
  }
  showPreviewDialog.value = true
}

const saveReport = () => {
  if (reportComponents.value.length === 0) {
    ElMessage.warning('请先添加组件到报表中')
    return
  }
  
  const reportData = {
    title: reportTitle.value,
    description: reportDescription.value,
    components: reportComponents.value,
    createdAt: new Date().toISOString()
  }
  
  // 模拟保存报表
  console.log('保存报表:', reportData)
  ElMessage.success('报表已保存')
}

const exportReport = () => {
  if (reportComponents.value.length === 0) {
    ElMessage.warning('请先添加组件到报表中')
    return
  }
  
  ElMessage.success('报表导出功能开发中...')
}
</script>

<style scoped>
.custom-report-builder {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.builder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
}

.header-left h3 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 18px;
}

.header-left p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.builder-content {
  flex: 1;
  display: grid;
  grid-template-columns: 250px 1fr 300px;
  gap: 1px;
  background: #e4e7ed;
}

.component-library {
  background: #ffffff;
  padding: 16px;
  overflow-y: auto;
}

.component-library h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
}

.component-categories {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.category h5 {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 14px;
  font-weight: 600;
}

.component-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.component-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.3s;
}

.component-item:hover {
  background: #e6f7ff;
  border-color: #409eff;
}

.component-item:active {
  cursor: grabbing;
}

.canvas-area {
  background: #ffffff;
  padding: 16px;
  overflow-y: auto;
}

.report-canvas {
  min-height: 100%;
  background: #ffffff;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 20px;
  position: relative;
}

.empty-canvas {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #c0c4cc;
}

.empty-canvas p {
  margin: 12px 0 0 0;
  font-size: 14px;
}

.canvas-component {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 16px;
  background: #ffffff;
  transition: all 0.3s;
}

.canvas-component:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.canvas-component.active {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.component-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.component-title {
  font-weight: 600;
  color: #303133;
}

.component-actions {
  display: flex;
  gap: 4px;
}

.component-content {
  padding: 16px;
}

.kpi-preview {
  display: flex;
  justify-content: center;
}

.kpi-item {
  text-align: center;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #409eff;
}

.kpi-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
}

.chart-preview {
  display: flex;
  justify-content: center;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 120px;
  background: #f8f9fa;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  color: #909399;
}

.chart-placeholder p {
  margin: 8px 0 0 0;
  font-size: 12px;
}

.table-preview {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  background: #f8f9fa;
}

.header-cell {
  padding: 8px 12px;
  font-weight: 600;
  color: #303133;
  border-right: 1px solid #e4e7ed;
  font-size: 12px;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border-top: 1px solid #e4e7ed;
}

.table-cell {
  padding: 8px 12px;
  color: #606266;
  border-right: 1px solid #e4e7ed;
  font-size: 12px;
}

.text-preview h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
}

.text-preview p {
  margin: 0;
  color: #606266;
  line-height: 1.5;
}

.image-preview {
  display: flex;
  justify-content: center;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100px;
  background: #f8f9fa;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  color: #c0c4cc;
}

.image-placeholder p {
  margin: 8px 0 0 0;
  font-size: 12px;
}

.property-panel {
  background: #ffffff;
  padding: 16px;
  overflow-y: auto;
}

.property-panel h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
}

.property-content {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.no-selection {
  text-align: center;
  color: #909399;
  padding: 40px 20px;
}

.config-content {
  max-height: 400px;
  overflow-y: auto;
}

.report-preview {
  max-height: 600px;
  overflow-y: auto;
}

.preview-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.preview-header h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 20px;
}

.preview-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.preview-component {
  margin-bottom: 20px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #f8f9fa;
}

.component-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.component-preview {
  color: #606266;
}
</style>
