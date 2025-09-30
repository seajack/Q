<template>
  <div class="report-templates">
    <!-- 模板选择器 -->
    <div class="template-selector">
      <div class="template-header">
        <h3>选择报表模板</h3>
        <div class="template-actions">
          <el-button type="success" @click="showCustomBuilder = true" class="action-btn">
            <el-icon><component :is="Icons.Edit" /></el-icon>
            自定义报表
          </el-button>
          <ReportExporter />
        </div>
      </div>
      <div class="template-grid">
        <div 
          v-for="template in reportTemplates" 
          :key="template.id"
          :class="['template-card', { active: selectedTemplate?.id === template.id }]"
          @click="selectTemplate(template)"
        >
          <div class="template-icon">
            <el-icon :size="32" :color="template.color">
              <component :is="template.icon" />
            </el-icon>
          </div>
          <div class="template-info">
            <h4>{{ template.name }}</h4>
            <p>{{ template.description }}</p>
            <div class="template-tags">
              <el-tag 
                v-for="tag in template.tags" 
                :key="tag" 
                size="small" 
                :type="getTagType(tag)"
              >
                {{ tag }}
              </el-tag>
            </div>
          </div>
          <div class="template-actions">
            <el-button size="small" type="primary" @click.stop="previewTemplate(template)">
              预览
            </el-button>
            <el-button size="small" @click.stop="customizeTemplate(template)">
              自定义
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 模板预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      :title="`${currentTemplate?.name} - 预览`"
      width="90%"
      :close-on-click-modal="false"
    >
      <div class="template-preview" v-if="currentTemplate">
        <div class="preview-header">
          <h3>{{ currentTemplate.name }}</h3>
          <p>{{ currentTemplate.description }}</p>
        </div>
        
        <div class="preview-content">
          <!-- 概览模板预览 -->
          <div v-if="currentTemplate.id === 'overview'" class="preview-overview">
            <div class="preview-kpi-grid">
              <div class="preview-kpi-card">
                <div class="kpi-header">
                  <span class="kpi-label">完成率</span>
                  <span class="kpi-badge">85%</span>
                </div>
                <div class="kpi-value">85%</div>
                <div class="kpi-progress">
                  <div class="progress-bar">
                    <div class="progress-fill" style="width: 85%"></div>
                  </div>
                </div>
              </div>
              
              <div class="preview-kpi-card">
                <div class="kpi-header">
                  <span class="kpi-label">平均评分</span>
                  <span class="kpi-badge">B+</span>
                </div>
                <div class="kpi-value">B+</div>
                <div class="kpi-detail">分布见右侧图表</div>
              </div>
            </div>
          </div>

          <!-- 绩效分析模板预览 -->
          <div v-if="currentTemplate.id === 'performance'" class="preview-performance">
            <div class="preview-charts">
              <div class="preview-chart-card">
                <h4>评分分布分析</h4>
                <div class="chart-placeholder">
                  <el-icon :size="48" color="#409eff"><component :is="Icons.PieChart" /></el-icon>
                  <p>评分分布饼图</p>
                </div>
              </div>
              
              <div class="preview-chart-card">
                <h4>部门绩效对比</h4>
                <div class="chart-placeholder">
                  <el-icon :size="48" color="#67c23a"><component :is="Icons.Histogram" /></el-icon>
                  <p>部门对比柱状图</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 趋势分析模板预览 -->
          <div v-if="currentTemplate.id === 'trend'" class="preview-trend">
            <div class="preview-chart-large">
              <h4>绩效完成趋势</h4>
              <div class="chart-placeholder large">
                <el-icon :size="64" color="#e6a23c"><component :is="Icons.TrendCharts" /></el-icon>
                <p>趋势分析折线图</p>
              </div>
            </div>
          </div>

          <!-- 详细数据模板预览 -->
          <div v-if="currentTemplate.id === 'detailed'" class="preview-detailed">
            <div class="preview-table">
              <h4>详细数据表格</h4>
              <div class="table-placeholder">
                <div class="table-header">
                  <div class="header-cell">员工姓名</div>
                  <div class="header-cell">部门</div>
                  <div class="header-cell">评分</div>
                  <div class="header-cell">完成度</div>
                </div>
                <div class="table-row">
                  <div class="table-cell">张三</div>
                  <div class="table-cell">技术部</div>
                  <div class="table-cell">B+</div>
                  <div class="table-cell">85%</div>
                </div>
                <div class="table-row">
                  <div class="table-cell">李四</div>
                  <div class="table-cell">市场部</div>
                  <div class="table-cell">A-</div>
                  <div class="table-cell">92%</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 360度评估模板预览 -->
          <div v-if="currentTemplate.id === '360'" class="preview-360">
            <div class="preview-360-content">
              <div class="radar-chart">
                <h4>360度评估雷达图</h4>
                <div class="chart-placeholder">
                  <el-icon :size="48" color="#f56c6c"><component :is="Icons.DataAnalysis" /></el-icon>
                  <p>多维度评估雷达图</p>
                </div>
              </div>
              
              <div class="evaluation-matrix">
                <h4>评估矩阵</h4>
                <div class="matrix-grid">
                  <div class="matrix-cell high-high">高绩效高潜力</div>
                  <div class="matrix-cell high-low">高绩效低潜力</div>
                  <div class="matrix-cell low-high">低绩效高潜力</div>
                  <div class="matrix-cell low-low">低绩效低潜力</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 对比分析模板预览 -->
          <div v-if="currentTemplate.id === 'comparison'" class="preview-comparison">
            <div class="comparison-charts">
              <div class="comparison-chart">
                <h4>同期对比分析</h4>
                <div class="chart-placeholder">
                  <el-icon :size="48" color="#909399"><component :is="Icons.DataAnalysis" /></el-icon>
                  <p>同期对比柱状图</p>
                </div>
              </div>
              
              <div class="comparison-chart">
                <h4>目标达成率</h4>
                <div class="chart-placeholder">
                  <el-icon :size="48" color="#67c23a"><component :is="Icons.PieChart" /></el-icon>
                  <p>目标达成饼图</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
        <el-button type="primary" @click="useTemplate">使用此模板</el-button>
      </template>
    </el-dialog>

    <!-- 模板自定义对话框 -->
    <el-dialog
      v-model="showCustomizeDialog"
      title="自定义报表模板"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="currentTemplate" class="template-customize">
        <el-form :model="customizeForm" label-width="120px">
          <el-form-item label="模板名称">
            <el-input v-model="customizeForm.name" placeholder="请输入模板名称" />
          </el-form-item>
          
          <el-form-item label="模板描述">
            <el-input 
              v-model="customizeForm.description" 
              type="textarea" 
              :rows="3"
              placeholder="请输入模板描述"
            />
          </el-form-item>
          
          <el-form-item label="包含组件">
            <el-checkbox-group v-model="customizeForm.components">
              <el-checkbox value="kpi">KPI指标卡片</el-checkbox>
              <el-checkbox value="charts">图表分析</el-checkbox>
              <el-checkbox value="tables">数据表格</el-checkbox>
              <el-checkbox value="trends">趋势分析</el-checkbox>
              <el-checkbox value="comparison">对比分析</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          
          <el-form-item label="数据筛选">
            <el-checkbox-group v-model="customizeForm.filters">
              <el-checkbox value="department">按部门筛选</el-checkbox>
              <el-checkbox value="position">按职位筛选</el-checkbox>
              <el-checkbox value="date">按时间筛选</el-checkbox>
              <el-checkbox value="score">按评分筛选</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          
          <el-form-item label="导出格式">
            <el-checkbox-group v-model="customizeForm.exportFormats">
              <el-checkbox value="pdf">PDF</el-checkbox>
              <el-checkbox value="excel">Excel</el-checkbox>
              <el-checkbox value="image">图片</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="showCustomizeDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCustomTemplate">保存模板</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, markRaw } from 'vue'
import { 
  DataAnalysis, 
  PieChart, 
  TrendCharts, 
  Document, 
  Histogram,
  Edit
} from '@element-plus/icons-vue'

// 使用 markRaw 防止图标组件被转换为响应式对象
const Icons = markRaw({
  DataAnalysis,
  PieChart,
  TrendCharts,
  Document,
  Histogram,
  Edit
})
import { ElMessage } from 'element-plus'
import ReportExporter from './ReportExporter.vue'

// 响应式数据
const selectedTemplate = ref<any>(null)
const showPreviewDialog = ref(false)
const showCustomizeDialog = ref(false)
const showCustomBuilder = ref(false)
const currentTemplate = ref<any>(null)

const customizeForm = reactive({
  name: '',
  description: '',
  components: [] as string[],
  filters: [] as string[],
  exportFormats: [] as string[]
})

// 报表模板数据
const reportTemplates = ref([
  {
    id: 'overview',
    name: '概览报表',
    description: '包含KPI指标、完成率、平均评分等核心指标的概览报表',
    icon: Icons.DataAnalysis,
    color: '#409eff',
    tags: ['KPI', '概览', '核心指标'],
    components: ['kpi', 'charts'],
    filters: ['department', 'date'],
    exportFormats: ['pdf', 'excel']
  },
  {
    id: 'performance',
    name: '绩效分析报表',
    description: '详细的绩效分析，包含评分分布、部门对比等深度分析',
    icon: Icons.PieChart,
    color: '#67c23a',
    tags: ['绩效', '分析', '分布'],
    components: ['charts', 'tables'],
    filters: ['department', 'position', 'score'],
    exportFormats: ['pdf', 'excel', 'image']
  },
  {
    id: 'trend',
    name: '趋势分析报表',
    description: '展示绩效完成趋势、月度对比等时间序列分析',
    icon: Icons.TrendCharts,
    color: '#e6a23c',
    tags: ['趋势', '时间序列', '对比'],
    components: ['trends', 'charts'],
    filters: ['date', 'department'],
    exportFormats: ['pdf', 'excel']
  },
  {
    id: 'detailed',
    name: '详细数据报表',
    description: '包含所有详细数据的表格形式报表，支持筛选和排序',
    icon: Icons.Document,
    color: '#909399',
    tags: ['详细', '数据', '表格'],
    components: ['tables'],
    filters: ['department', 'position', 'date', 'score'],
    exportFormats: ['excel', 'pdf']
  },
  {
    id: '360',
    name: '360度评估报表',
    description: '多维度评估分析，包含雷达图、评估矩阵等',
    icon: Icons.DataAnalysis,
    color: '#f56c6c',
    tags: ['360度', '多维度', '评估'],
    components: ['charts', 'tables'],
    filters: ['department', 'position'],
    exportFormats: ['pdf', 'excel', 'image']
  },
  {
    id: 'comparison',
    name: '对比分析报表',
    description: '同期对比、目标达成率等对比分析报表',
    icon: Icons.Histogram,
    color: '#8b5cf6',
    tags: ['对比', '同期', '目标'],
    components: ['comparison', 'charts'],
    filters: ['date', 'department'],
    exportFormats: ['pdf', 'excel']
  }
])

// 方法
const selectTemplate = (template: any) => {
  selectedTemplate.value = template
  ElMessage.success(`已选择模板：${template.name}`)
}

const previewTemplate = (template: any) => {
  currentTemplate.value = template
  showPreviewDialog.value = true
}

const customizeTemplate = (template: any) => {
  currentTemplate.value = template
  customizeForm.name = template.name
  customizeForm.description = template.description
  customizeForm.components = [...template.components]
  customizeForm.filters = [...template.filters]
  customizeForm.exportFormats = [...template.exportFormats]
  showCustomizeDialog.value = true
}

const useTemplate = () => {
  if (currentTemplate.value) {
    ElMessage.success(`已应用模板：${currentTemplate.value.name}`)
    showPreviewDialog.value = false
    // 这里可以触发父组件的模板应用事件
    // emit('template-selected', currentTemplate.value)
  }
}

const saveCustomTemplate = () => {
  if (!customizeForm.name.trim()) {
    ElMessage.warning('请输入模板名称')
    return
  }
  
  if (customizeForm.components.length === 0) {
    ElMessage.warning('请至少选择一个组件')
    return
  }
  
  if (customizeForm.exportFormats.length === 0) {
    ElMessage.warning('请至少选择一种导出格式')
    return
  }
  
  // 模拟保存自定义模板
  const customTemplate = {
    id: `custom_${Date.now()}`,
    name: customizeForm.name,
    description: customizeForm.description,
    icon: Icons.DataAnalysis,
    color: '#8b5cf6',
    tags: ['自定义'],
    components: customizeForm.components,
    filters: customizeForm.filters,
    exportFormats: customizeForm.exportFormats,
    isCustom: true
  }
  
  reportTemplates.value.push(customTemplate)
  ElMessage.success('自定义模板保存成功')
  showCustomizeDialog.value = false
}

const getTagType = (tag: string) => {
  const typeMap: Record<string, string> = {
    'KPI': 'primary',
    '概览': 'success',
    '核心指标': 'info',
    '绩效': 'warning',
    '分析': 'danger',
    '分布': 'success',
    '趋势': 'primary',
    '时间序列': 'info',
    '对比': 'warning',
    '详细': 'success',
    '数据': 'info',
    '表格': 'primary',
    '360度': 'danger',
    '多维度': 'warning',
    '评估': 'success',
    '自定义': 'info'
  }
  return typeMap[tag] || 'info'
}
</script>

<style scoped>
.report-templates {
  padding: 20px;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.template-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.template-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  color: white;
  border-radius: 8px;
  padding: 8px 16px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn:hover {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  max-width: 1200px;
  margin: 0 auto;
}

.template-card {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 200px;
  position: relative;
  overflow: hidden;
}

.template-card:hover {
  border-color: #409eff;
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.15);
  transform: translateY(-4px);
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
}

.template-card.active {
  border-color: #409eff;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.25);
  transform: translateY(-2px);
}

.template-card.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #409eff, #67c23a);
}

.template-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.template-card:hover .template-icon {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  border-color: #409eff;
  transform: scale(1.05);
}

.template-info {
  flex: 1;
  text-align: center;
}

.template-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.3;
}

.template-info p {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.template-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
  margin-bottom: 8px;
}

.template-tags .el-tag {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
}

.template-actions {
  display: flex;
  gap: 6px;
  justify-content: center;
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.template-actions .el-button {
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.template-actions .el-button--primary {
  background: #409eff;
  border-color: #409eff;
}

.template-actions .el-button--primary:hover {
  background: #337ecc;
  border-color: #337ecc;
  transform: translateY(-1px);
}

.template-actions .el-button:not(.el-button--primary) {
  background: #f8f9fa;
  border-color: #d9d9d9;
  color: #606266;
}

.template-actions .el-button:not(.el-button--primary):hover {
  background: #e9ecef;
  border-color: #409eff;
  color: #409eff;
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .template-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
  }
}

@media (max-width: 768px) {
  .template-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .template-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .template-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .template-card {
    min-height: 180px;
    padding: 14px;
  }
  
  .template-icon {
    width: 40px;
    height: 40px;
    margin-bottom: 10px;
  }
  
  .template-info h4 {
    font-size: 15px;
  }
  
  .template-info p {
    font-size: 12px;
  }
  
  .template-actions {
    flex-direction: column;
    gap: 4px;
  }
  
  .template-actions .el-button {
    width: 100%;
    font-size: 11px;
    padding: 5px 10px;
  }
}

@media (max-width: 480px) {
  .template-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .template-card {
    min-height: 160px;
    padding: 12px;
  }
  
  .template-icon {
    width: 36px;
    height: 36px;
  }
}

.template-preview {
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

.preview-content {
  padding: 20px 0;
}

.preview-kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.preview-kpi-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #f8f9fa;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.kpi-label {
  font-weight: 600;
  color: #303133;
}

.kpi-badge {
  padding: 2px 8px;
  border-radius: 4px;
  background: #67c23a;
  color: white;
  font-size: 12px;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.kpi-progress {
  margin-top: 8px;
}

.progress-bar {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #409eff;
  transition: width 0.3s;
}

.kpi-detail {
  font-size: 12px;
  color: #909399;
}

.preview-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.preview-chart-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: #f8f9fa;
}

.preview-chart-card h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  background: #ffffff;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  color: #909399;
}

.chart-placeholder.large {
  height: 300px;
}

.chart-placeholder p {
  margin: 8px 0 0 0;
  font-size: 14px;
}

.preview-chart-large {
  margin-bottom: 20px;
}

.preview-table {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.preview-table h4 {
  margin: 0;
  padding: 16px;
  background: #f8f9fa;
  color: #303133;
  font-size: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.table-placeholder {
  background: #ffffff;
}

.table-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.header-cell {
  padding: 12px;
  font-weight: 600;
  color: #303133;
  border-right: 1px solid #e4e7ed;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  border-bottom: 1px solid #e4e7ed;
}

.table-cell {
  padding: 12px;
  color: #606266;
  border-right: 1px solid #e4e7ed;
}

.preview-360-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.radar-chart,
.evaluation-matrix {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: #f8f9fa;
}

.radar-chart h4,
.evaluation-matrix h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
}

.matrix-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.matrix-cell {
  padding: 16px;
  text-align: center;
  border-radius: 6px;
  font-weight: 600;
  color: white;
}

.matrix-cell.high-high {
  background: #67c23a;
}

.matrix-cell.high-low {
  background: #e6a23c;
}

.matrix-cell.low-high {
  background: #409eff;
}

.matrix-cell.low-low {
  background: #f56c6c;
}

.comparison-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.comparison-chart {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: #f8f9fa;
}

.comparison-chart h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
}

.template-customize {
  max-height: 500px;
  overflow-y: auto;
}
</style>
