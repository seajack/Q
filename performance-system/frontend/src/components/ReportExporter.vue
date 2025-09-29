<template>
  <div class="report-exporter">
    <!-- 导出按钮 -->
    <el-button 
      type="primary" 
      @click="showExportDialog = true"
      :loading="exporting"
    >
      <el-icon><Download /></el-icon>
      导出报表
    </el-button>

    <!-- 导出对话框 -->
    <el-dialog
      v-model="showExportDialog"
      title="导出报表"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="export-content">
        <!-- 报表信息 -->
        <div class="report-info">
          <h4>报表信息</h4>
          <el-form :model="exportForm" label-width="100px">
            <el-form-item label="报表名称">
              <el-input v-model="exportForm.reportName" placeholder="请输入报表名称" />
            </el-form-item>
            <el-form-item label="报表描述">
              <el-input 
                v-model="exportForm.description" 
                type="textarea" 
                :rows="2"
                placeholder="请输入报表描述"
              />
            </el-form-item>
            <el-form-item label="生成时间">
              <el-date-picker
                v-model="exportForm.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-form>
        </div>

        <!-- 导出格式选择 -->
        <div class="export-formats">
          <h4>导出格式</h4>
          <div class="format-options">
            <div 
              v-for="format in exportFormats" 
              :key="format.type"
              :class="['format-option', { active: selectedFormats.includes(format.type) }]"
              @click="toggleFormat(format.type)"
            >
              <div class="format-icon">
                <el-icon :size="24" :color="format.color">
                  <component :is="format.icon" />
                </el-icon>
              </div>
              <div class="format-info">
                <h5>{{ format.name }}</h5>
                <p>{{ format.description }}</p>
              </div>
              <div class="format-checkbox">
                <el-checkbox 
                  :model-value="selectedFormats.includes(format.type)"
                  @change="toggleFormat(format.type)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 导出选项 -->
        <div class="export-options">
          <h4>导出选项</h4>
          <el-form :model="exportForm" label-width="120px">
            <el-form-item label="包含图表">
              <el-switch v-model="exportForm.includeCharts" />
            </el-form-item>
            <el-form-item label="包含数据表">
              <el-switch v-model="exportForm.includeTables" />
            </el-form-item>
            <el-form-item label="包含原始数据">
              <el-switch v-model="exportForm.includeRawData" />
            </el-form-item>
            <el-form-item label="水印设置">
              <el-input v-model="exportForm.watermark" placeholder="请输入水印文字（可选）" />
            </el-form-item>
            <el-form-item label="页面设置">
              <el-select v-model="exportForm.pageSize" placeholder="选择页面大小" style="width: 100%">
                <el-option label="A4" value="A4" />
                <el-option label="A3" value="A3" />
                <el-option label="Letter" value="Letter" />
              </el-select>
            </el-form-item>
            <el-form-item label="方向">
              <el-radio-group v-model="exportForm.orientation">
                <el-radio value="portrait">纵向</el-radio>
                <el-radio value="landscape">横向</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </div>

        <!-- 数据筛选 -->
        <div class="data-filters">
          <h4>数据筛选</h4>
          <el-form :model="exportForm" label-width="100px">
            <el-form-item label="部门筛选">
              <el-select 
                v-model="exportForm.departments" 
                multiple 
                placeholder="选择部门"
                style="width: 100%"
              >
                <el-option label="技术部" value="tech" />
                <el-option label="市场部" value="marketing" />
                <el-option label="人事部" value="hr" />
                <el-option label="财务部" value="finance" />
              </el-select>
            </el-form-item>
            <el-form-item label="职位筛选">
              <el-select 
                v-model="exportForm.positions" 
                multiple 
                placeholder="选择职位"
                style="width: 100%"
              >
                <el-option label="经理" value="manager" />
                <el-option label="主管" value="supervisor" />
                <el-option label="专员" value="specialist" />
                <el-option label="助理" value="assistant" />
              </el-select>
            </el-form-item>
            <el-form-item label="评分范围">
              <el-slider
                v-model="exportForm.scoreRange"
                range
                :min="0"
                :max="100"
                :step="5"
                show-stops
                show-input
              />
            </el-form-item>
          </el-form>
        </div>
      </div>

      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" @click="startExport" :loading="exporting">
          开始导出
        </el-button>
      </template>
    </el-dialog>

    <!-- 导出进度对话框 -->
    <el-dialog
      v-model="showProgressDialog"
      title="导出进度"
      width="400px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <div class="export-progress">
        <div class="progress-info">
          <h4>{{ currentExportTask?.name }}</h4>
          <p>{{ currentExportTask?.description }}</p>
        </div>
        
        <div class="progress-bar">
          <el-progress 
            :percentage="exportProgress" 
            :status="exportStatus"
            :stroke-width="8"
          />
          <div class="progress-text">
            {{ progressText }}
          </div>
        </div>
        
        <div class="export-tasks" v-if="exportTasks.length > 0">
          <h5>导出任务</h5>
          <div class="task-list">
            <div 
              v-for="task in exportTasks" 
              :key="task.id"
              class="task-item"
              :class="task.status"
            >
              <el-icon>
                <component :is="getTaskIcon(task.status)" />
              </el-icon>
              <span>{{ task.name }}</span>
              <el-tag :type="getTaskTagType(task.status)" size="small">
                {{ getTaskStatusText(task.status) }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 导出完成对话框 -->
    <el-dialog
      v-model="showCompleteDialog"
      title="导出完成"
      width="500px"
    >
      <div class="export-complete">
        <div class="complete-icon">
          <el-icon :size="48" color="#67c23a">
            <CircleCheck />
          </el-icon>
        </div>
        <div class="complete-info">
          <h3>导出成功！</h3>
          <p>报表已成功导出，共生成 {{ completedExports.length }} 个文件</p>
        </div>
        
        <div class="export-files">
          <h4>生成的文件</h4>
          <div class="file-list">
            <div 
              v-for="file in completedExports" 
              :key="file.id"
              class="file-item"
            >
              <el-icon :color="getFileIconColor(file.type)">
                <component :is="getFileIcon(file.type)" />
              </el-icon>
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-size">{{ file.size }}</div>
              </div>
              <div class="file-actions">
                <el-button type="text" size="small" @click="downloadFile(file)">
                  下载
                </el-button>
                <el-button type="text" size="small" @click="previewFile(file)">
                  预览
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showCompleteDialog = false">关闭</el-button>
        <el-button type="primary" @click="downloadAllFiles">下载全部</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { 
  Download, 
  Document, 
  Picture, 
  DataAnalysis,
  CircleCheck,
  Loading,
  Check,
  Close
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import { saveAs } from 'file-saver'

// 响应式数据
const showExportDialog = ref(false)
const showProgressDialog = ref(false)
const showCompleteDialog = ref(false)
const exporting = ref(false)
const exportProgress = ref(0)
const exportStatus = ref<'success' | 'exception' | 'warning' | undefined>()

const exportForm = reactive({
  reportName: '绩效考核报表',
  description: '',
  dateRange: [] as any[],
  includeCharts: true,
  includeTables: true,
  includeRawData: false,
  watermark: '',
  pageSize: 'A4',
  orientation: 'portrait',
  departments: [] as string[],
  positions: [] as string[],
  scoreRange: [0, 100]
})

const selectedFormats = ref<string[]>(['pdf'])

const exportFormats = ref([
  {
    type: 'pdf',
    name: 'PDF文档',
    description: '适合打印和分享的PDF格式',
    icon: Document,
    color: '#f56c6c'
  },
  {
    type: 'excel',
    name: 'Excel表格',
    description: '可编辑的数据表格格式',
    icon: DataAnalysis,
    color: '#67c23a'
  },
  {
    type: 'image',
    name: '图片文件',
    description: 'PNG/JPEG格式的图片文件',
    icon: Picture,
    color: '#409eff'
  }
])

const exportTasks = ref<any[]>([])
const currentExportTask = ref<any>(null)
const completedExports = ref<any[]>([])

// 计算属性
const progressText = computed(() => {
  if (exportStatus.value === 'success') return '导出完成'
  if (exportStatus.value === 'exception') return '导出失败'
  return `正在导出... ${exportProgress.value}%`
})

// 方法
const toggleFormat = (formatType: string) => {
  const index = selectedFormats.value.indexOf(formatType)
  if (index > -1) {
    selectedFormats.value.splice(index, 1)
  } else {
    selectedFormats.value.push(formatType)
  }
}

const startExport = async () => {
  if (selectedFormats.value.length === 0) {
    ElMessage.warning('请至少选择一种导出格式')
    return
  }
  
  if (!exportForm.reportName.trim()) {
    ElMessage.warning('请输入报表名称')
    return
  }
  
  showExportDialog.value = false
  showProgressDialog.value = true
  exporting.value = true
  exportProgress.value = 0
  exportStatus.value = undefined
  
  // 初始化导出任务
  exportTasks.value = selectedFormats.value.map(format => ({
    id: `task_${format}_${Date.now()}`,
    name: getFormatName(format),
    description: `正在生成${getFormatName(format)}文件...`,
    status: 'pending',
    format
  }))
  
  try {
    // 模拟导出过程
    for (let i = 0; i < exportTasks.value.length; i++) {
      const task = exportTasks.value[i]
      currentExportTask.value = task
      task.status = 'processing'
      
      // 模拟处理时间
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 执行实际导出
      const result = await exportToFormat(task.format)
      
      if (result.success) {
        task.status = 'completed'
        completedExports.value.push(result.file)
      } else {
        task.status = 'failed'
      }
      
      exportProgress.value = Math.round(((i + 1) / exportTasks.value.length) * 100)
    }
    
    exportStatus.value = 'success'
    exporting.value = false
    
    // 延迟显示完成对话框
    setTimeout(() => {
      showProgressDialog.value = false
      showCompleteDialog.value = true
    }, 1000)
    
  } catch (error) {
    console.error('导出失败:', error)
    exportStatus.value = 'exception'
    exporting.value = false
    ElMessage.error('导出失败，请重试')
  }
}

const exportToFormat = async (format: string) => {
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
  const fileName = `${exportForm.reportName}_${timestamp}`
  
  switch (format) {
    case 'pdf':
      return await exportToPDF(fileName)
    case 'excel':
      return await exportToExcel(fileName)
    case 'image':
      return await exportToImage(fileName)
    default:
      throw new Error(`不支持的导出格式: ${format}`)
  }
}

const exportToPDF = async (fileName: string) => {
  try {
    // 创建PDF文档
    const pdf = new jsPDF({
      orientation: exportForm.orientation,
      unit: 'mm',
      format: exportForm.pageSize.toLowerCase()
    })
    
    // 添加标题
    pdf.setFontSize(20)
    pdf.text(exportForm.reportName, 20, 30)
    
    // 添加描述
    if (exportForm.description) {
      pdf.setFontSize(12)
      pdf.text(exportForm.description, 20, 40)
    }
    
    // 添加水印
    if (exportForm.watermark) {
      pdf.setFontSize(10)
      pdf.setTextColor(200, 200, 200)
      pdf.text(exportForm.watermark, 20, pdf.internal.pageSize.height - 20)
    }
    
    // 添加内容（这里需要根据实际数据生成）
    pdf.setFontSize(14)
    pdf.text('绩效考核数据', 20, 60)
    
    // 生成PDF文件
    const pdfBlob = pdf.output('blob')
    const fileSize = formatFileSize(pdfBlob.size)
    
    return {
      success: true,
      file: {
        id: `pdf_${Date.now()}`,
        name: `${fileName}.pdf`,
        type: 'pdf',
        size: fileSize,
        blob: pdfBlob
      }
    }
  } catch (error) {
    console.error('PDF导出失败:', error)
    return { success: false, error }
  }
}

const exportToExcel = async (fileName: string) => {
  try {
    // 准备Excel数据
    const excelData = [
      ['员工姓名', '部门', '职位', '评分', '完成度', '考核时间'],
      ['张三', '技术部', '工程师', 'B+', '85%', '2024-01-15'],
      ['李四', '市场部', '经理', 'A-', '92%', '2024-01-15'],
      ['王五', '人事部', '专员', 'B', '78%', '2024-01-15']
    ]
    
    // 创建工作簿
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.aoa_to_sheet(excelData)
    
    // 设置列宽
    const colWidths = [
      { wch: 12 }, // 员工姓名
      { wch: 10 }, // 部门
      { wch: 12 }, // 职位
      { wch: 8 },  // 评分
      { wch: 10 }, // 完成度
      { wch: 15 }  // 考核时间
    ]
    ws['!cols'] = colWidths
    
    // 添加工作表
    XLSX.utils.book_append_sheet(wb, ws, '绩效考核数据')
    
    // 生成Excel文件
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([wbout], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    
    const fileSize = formatFileSize(blob.size)
    
    return {
      success: true,
      file: {
        id: `excel_${Date.now()}`,
        name: `${fileName}.xlsx`,
        type: 'excel',
        size: fileSize,
        blob
      }
    }
  } catch (error) {
    console.error('Excel导出失败:', error)
    return { success: false, error }
  }
}

const exportToImage = async (fileName: string) => {
  try {
    // 这里需要根据实际的报表内容生成图片
    // 使用html2canvas将DOM转换为图片
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    if (!ctx) throw new Error('无法创建画布上下文')
    
    // 设置画布尺寸
    canvas.width = 800
    canvas.height = 600
    
    // 绘制背景
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    // 绘制标题
    ctx.fillStyle = '#303133'
    ctx.font = '24px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(exportForm.reportName, canvas.width / 2, 50)
    
    // 绘制内容
    ctx.font = '16px Arial'
    ctx.textAlign = 'left'
    ctx.fillText('绩效考核数据图表', 50, 100)
    
    // 转换为Blob
    const blob = await new Promise<Blob>((resolve) => {
      canvas.toBlob((blob) => {
        resolve(blob!)
      }, 'image/png')
    })
    
    const fileSize = formatFileSize(blob.size)
    
    return {
      success: true,
      file: {
        id: `image_${Date.now()}`,
        name: `${fileName}.png`,
        type: 'image',
        size: fileSize,
        blob
      }
    }
  } catch (error) {
    console.error('图片导出失败:', error)
    return { success: false, error }
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFormatName = (format: string) => {
  const formatMap: Record<string, string> = {
    pdf: 'PDF文档',
    excel: 'Excel表格',
    image: '图片文件'
  }
  return formatMap[format] || format
}

const getTaskIcon = (status: string) => {
  const iconMap: Record<string, any> = {
    pending: Loading,
    processing: Loading,
    completed: Check,
    failed: Close
  }
  return iconMap[status] || Loading
}

const getTaskTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'info',
    processing: 'primary',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

const getTaskStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || status
}

const getFileIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    pdf: Document,
    excel: DataAnalysis,
    image: Picture
  }
  return iconMap[type] || Document
}

const getFileIconColor = (type: string) => {
  const colorMap: Record<string, string> = {
    pdf: '#f56c6c',
    excel: '#67c23a',
    image: '#409eff'
  }
  return colorMap[type] || '#909399'
}

const downloadFile = (file: any) => {
  const url = URL.createObjectURL(file.blob)
  const link = document.createElement('a')
  link.href = url
  link.download = file.name
  link.click()
  URL.revokeObjectURL(url)
}

const previewFile = (file: any) => {
  if (file.type === 'image') {
    const url = URL.createObjectURL(file.blob)
    window.open(url, '_blank')
  } else {
    ElMessage.info('预览功能开发中...')
  }
}

const downloadAllFiles = () => {
  completedExports.value.forEach(file => {
    downloadFile(file)
  })
  ElMessage.success('开始下载所有文件')
}
</script>

<style scoped>
.report-exporter {
  display: inline-block;
}

.export-content {
  max-height: 500px;
  overflow-y: auto;
}

.report-info,
.export-formats,
.export-options,
.data-filters {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.report-info h4,
.export-formats h4,
.export-options h4,
.data-filters h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.format-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.format-option {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.format-option:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.format-option.active {
  border-color: #409eff;
  background: #e6f7ff;
}

.format-icon {
  margin-right: 16px;
  flex-shrink: 0;
}

.format-info {
  flex: 1;
}

.format-info h5 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 16px;
}

.format-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.format-checkbox {
  flex-shrink: 0;
}

.export-progress {
  text-align: center;
}

.progress-info {
  margin-bottom: 24px;
}

.progress-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 18px;
}

.progress-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.progress-bar {
  margin-bottom: 24px;
}

.progress-text {
  margin-top: 8px;
  color: #606266;
  font-size: 14px;
}

.export-tasks h5 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
  text-align: left;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  background: #f8f9fa;
}

.task-item.processing {
  background: #e6f7ff;
}

.task-item.completed {
  background: #f6ffed;
}

.task-item.failed {
  background: #fff2f0;
}

.task-item span {
  flex: 1;
  color: #303133;
  font-size: 14px;
}

.export-complete {
  text-align: center;
}

.complete-icon {
  margin-bottom: 16px;
}

.complete-info h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 20px;
}

.complete-info p {
  margin: 0 0 24px 0;
  color: #606266;
  font-size: 14px;
}

.export-files {
  text-align: left;
}

.export-files h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #f8f9fa;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.file-size {
  color: #909399;
  font-size: 12px;
}

.file-actions {
  display: flex;
  gap: 8px;
}
</style>
