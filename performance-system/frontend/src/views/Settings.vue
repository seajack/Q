<template>
  <div class="settings">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">系统设置</h1>
      <p class="page-description">配置系统参数和基础设置</p>
    </div>

    <el-row :gutter="24">
      <el-col :xs="24" :lg="16">
        <el-card class="settings-card">
          <template #header>
            <h3>基础设置</h3>
          </template>
          <el-form :model="settings" label-width="120px" class="settings-form">
            <el-form-item label="系统名称">
              <el-input v-model="settings.systemName" placeholder="请输入系统名称" />
            </el-form-item>
            <el-form-item label="系统描述">
              <el-input 
                v-model="settings.systemDescription" 
                type="textarea" 
                :rows="3"
                placeholder="请输入系统描述"
              />
            </el-form-item>
            <el-form-item label="默认考核周期">
              <el-select v-model="settings.defaultCycle" placeholder="请选择默认考核周期">
                <el-option label="月度" value="monthly" />
                <el-option label="季度" value="quarterly" />
                <el-option label="半年度" value="semi-annual" />
                <el-option label="年度" value="annual" />
              </el-select>
            </el-form-item>
            <el-form-item label="评分标准">
              <el-radio-group v-model="settings.scoringStandard">
                <el-radio label="five-point">5分制</el-radio>
                <el-radio label="ten-point">10分制</el-radio>
                <el-radio label="percentage">百分制</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="自动提醒">
              <el-switch v-model="settings.autoReminder" />
              <span class="form-tip">开启后系统将自动发送考核提醒</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings">保存设置</el-button>
              <el-button @click="resetSettings">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="info-card">
          <template #header>
            <h3>系统信息</h3>
          </template>
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">系统版本</span>
              <span class="info-value">v1.0.0</span>
            </div>
            <div class="info-item">
              <span class="info-label">最后更新</span>
              <span class="info-value">2024-01-15</span>
            </div>
            <div class="info-item">
              <span class="info-label">数据库状态</span>
              <el-tag type="success" size="small">正常</el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">在线用户</span>
              <span class="info-value">12</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const settings = ref({
  systemName: '绩效考核管理系统',
  systemDescription: '企业级绩效考核管理平台',
  defaultCycle: 'quarterly',
  scoringStandard: 'five-point',
  autoReminder: true
})

const saveSettings = () => {
  ElMessage.success('设置保存成功')
}

const resetSettings = () => {
  settings.value = {
    systemName: '绩效考核管理系统',
    systemDescription: '企业级绩效考核管理平台',
    defaultCycle: 'quarterly',
    scoringStandard: 'five-point',
    autoReminder: true
  }
  ElMessage.info('设置已重置')
}
</script>

<style scoped>
.settings {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.page-description {
  color: #6b7280;
  font-size: 16px;
  margin: 0;
}

.settings-card, .info-card {
  height: fit-content;
}

.settings-card h3, .info-card h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.settings-form {
  padding: 20px 0;
}

.form-tip {
  margin-left: 8px;
  color: #6b7280;
  font-size: 12px;
}

.info-list {
  space-y: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  color: #6b7280;
  font-size: 14px;
}

.info-value {
  color: #1f2937;
  font-weight: 500;
  font-size: 14px;
}
</style>
