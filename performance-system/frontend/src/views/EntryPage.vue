<template>
  <div class="entry-page">
    <div class="container">
      <div class="header">
        <h1 class="title">绩效考核系统</h1>
        <p class="subtitle">请选择您的身份</p>
      </div>
      
      <div class="options">
        <div class="option-card" @click="goToAdmin">
          <div class="card-icon">
            <i class="el-icon-s-tools"></i>
          </div>
          <h3>管理员入口</h3>
          <p>系统管理、数据维护、结果查看</p>
          <div class="card-footer">
            <span class="access-type">管理员权限</span>
          </div>
        </div>
        
        <div class="option-card" @click="goToEvaluation">
          <div class="card-icon">
            <i class="el-icon-user"></i>
          </div>
          <h3>考核人员入口</h3>
          <p>输入考核码，完成考核任务</p>
          <div class="card-footer">
            <span class="access-type">考核码登录</span>
          </div>
        </div>
      </div>
      
      <div class="help-section">
        <h4>使用说明</h4>
        <div class="help-items">
          <div class="help-item">
            <i class="el-icon-info"></i>
            <span>管理员：使用系统管理功能，查看考核结果</span>
          </div>
          <div class="help-item">
            <i class="el-icon-key"></i>
            <span>考核人员：使用16位考核码登录，完成考核任务</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goToAdmin = () => {
  router.push('/dashboard-new')
}

const goToEvaluation = () => {
  router.push('/evaluation-entry')
}
</script>

<style scoped>
.entry-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 60px 40px;
  max-width: 800px;
  width: 100%;
  text-align: center;
}

.header {
  margin-bottom: 50px;
}

.title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 15px 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.2rem;
  color: #7f8c8d;
  margin: 0;
}

.options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 50px;
}

.option-card {
  background: #f8f9fa;
  border-radius: 16px;
  padding: 40px 30px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.option-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.option-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.option-card:hover::before {
  transform: scaleX(1);
}

.card-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
}

.option-card h3 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 15px 0;
}

.option-card p {
  color: #7f8c8d;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.card-footer {
  display: flex;
  justify-content: center;
}

.access-type {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.help-section {
  border-top: 1px solid #e1e8ed;
  padding-top: 30px;
}

.help-section h4 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin: 0 0 20px 0;
}

.help-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.help-item {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #7f8c8d;
  font-size: 0.95rem;
}

.help-item i {
  font-size: 1.2rem;
  color: #667eea;
  min-width: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 40px 20px;
    margin: 10px;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .options {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .option-card {
    padding: 30px 20px;
  }
  
  .card-icon {
    width: 60px;
    height: 60px;
    font-size: 1.5rem;
  }
  
  .option-card h3 {
    font-size: 1.3rem;
  }
}

@media (max-width: 480px) {
  .entry-page {
    padding: 10px;
  }
  
  .container {
    padding: 30px 15px;
  }
  
  .title {
    font-size: 1.8rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .option-card {
    padding: 25px 15px;
  }
}
</style>
