# 绩效考核系统技术文档

## 📋 目录

1. [系统架构](#系统架构)
2. [技术栈](#技术栈)
3. [数据库设计](#数据库设计)
4. [API接口文档](#api接口文档)
5. [前端组件架构](#前端组件架构)
6. [部署指南](#部署指南)
7. [开发指南](#开发指南)

---

## 🏗️ 系统架构

### 整体架构图
```
┌─────────────────┐    ┌─────────────────┐
│   组织架构系统    │    │   绩效考核系统    │
│                 │    │                 │
│  Frontend: Vue  │    │  Frontend: Vue  │
│  Backend: Django│    │  Backend: Django│
│  Port: 3002     │    │  Port: 3001     │
│  API: 8000      │    │  API: 8001      │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                    │
            ┌─────────────────┐
            │   共享数据库     │
            │    SQLite       │
            └─────────────────┘
```

### 系统交互流程
1. **组织架构系统** - 管理员工、部门、职位信息
2. **绩效考核系统** - 通过API调用获取组织架构数据
3. **数据同步** - 实时同步员工和职位信息
4. **权重配置** - 基于职位信息配置评分权重

---

## 🛠️ 技术栈

### 前端技术
- **Vue.js 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript超集
- **Element Plus** - Vue 3 UI组件库
- **Vite** - 现代化构建工具
- **Pinia** - Vue状态管理库
- **Vue Router** - 官方路由管理器

### 后端技术
- **Django 4.2** - Python Web框架
- **Django REST Framework** - API开发框架
- **SQLite** - 轻量级数据库
- **Python 3.8+** - 编程语言

### 开发工具
- **Node.js 16+** - JavaScript运行时
- **npm** - 包管理器
- **Git** - 版本控制
- **VS Code** - 推荐IDE

---

## 🗄️ 数据库设计

### 核心数据表

#### 1. 考核周期 (EvaluationCycle)
```python
class EvaluationCycle(models.Model):
    name = models.CharField('名称', max_length=200)
    description = models.TextField('描述', blank=True)
    start_date = models.DateField('开始时间')
    end_date = models.DateField('结束时间')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES)
    evaluation_rule = models.ForeignKey('EvaluationRule', on_delete=models.CASCADE)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
```

#### 2. 考核任务 (EvaluationTask)
```python
class EvaluationTask(models.Model):
    cycle = models.ForeignKey(EvaluationCycle, on_delete=models.CASCADE)
    evaluator = models.ForeignKey('organizations.Employee', on_delete=models.CASCADE)
    evaluatee = models.ForeignKey('organizations.Employee', on_delete=models.CASCADE)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES)
    evaluation_code = models.CharField('考核码', max_length=20, unique=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
```

#### 3. 评分记录 (EvaluationScore)
```python
class EvaluationScore(models.Model):
    task = models.ForeignKey(EvaluationTask, on_delete=models.CASCADE)
    indicator = models.ForeignKey(EvaluationIndicator, on_delete=models.CASCADE)
    score = models.IntegerField('原始评分')
    weighted_score = models.DecimalField('加权评分', max_digits=5, decimal_places=2)
    comment = models.TextField('评价意见', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
```

#### 4. 职级权重 (PositionWeight)
```python
class PositionWeight(models.Model):
    position_id = models.IntegerField('职位ID')
    position_name = models.CharField('职位名称', max_length=100)
    position_level = models.IntegerField('职位级别')
    weight = models.DecimalField('权重', max_digits=5, decimal_places=2)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
```

### 数据关系图
```
EvaluationCycle (1) ──→ (N) EvaluationTask
EvaluationTask (1) ──→ (N) EvaluationScore
EvaluationTask (N) ──→ (1) Employee (evaluator)
EvaluationTask (N) ──→ (1) Employee (evaluatee)
PositionWeight (N) ──→ (1) Position
```

---

## 🔌 API接口文档

### 基础URL
- **组织架构系统**: http://localhost:8000/api/
- **绩效考核系统**: http://localhost:8001/api/

### 核心API端点

#### 考核周期管理
```http
GET    /api/cycles/                    # 获取考核周期列表
POST   /api/cycles/                    # 创建考核周期
GET    /api/cycles/{id}/               # 获取考核周期详情
PUT    /api/cycles/{id}/               # 更新考核周期
DELETE /api/cycles/{id}/               # 删除考核周期
POST   /api/cycles/{id}/generate_tasks/ # 生成考核任务
```

#### 考核任务管理
```http
GET    /api/tasks/                     # 获取考核任务列表
GET    /api/tasks/by-code/{code}/      # 根据考核码获取任务
POST   /api/tasks/{id}/submit_scores/  # 提交评分
```

#### 职级权重配置
```http
GET    /api/position-weights/          # 获取权重配置列表
POST   /api/position-weights/          # 创建权重配置
PUT    /api/position-weights/{id}/     # 更新权重配置
DELETE /api/position-weights/{id}/     # 删除权重配置
POST   /api/position-weights/bulk-update/ # 批量更新权重
GET    /api/position-weights/default-weights/ # 获取默认权重
```

### API响应格式
```json
{
  "count": 100,
  "next": "http://api.example.com/items/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "示例数据",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

## 🎨 前端组件架构

### 组件层次结构
```
App.vue
├── TopNavLayout.vue
│   ├── TopNav.vue
│   └── RouterView
│       ├── Dashboard.vue
│       ├── CyclesNew.vue
│       ├── Tasks.vue
│       ├── PositionWeights.vue
│       ├── Evaluation.vue
│       └── EvaluationForm.vue
```

### 核心组件说明

#### 1. TopNavLayout.vue
- **功能**: 顶部导航布局组件
- **包含**: 导航菜单、用户信息、系统标题
- **样式**: 响应式设计，支持移动端

#### 2. CyclesNew.vue
- **功能**: 考核周期管理页面
- **特性**: 表格展示、分页、搜索、操作按钮
- **组件**: el-table, el-pagination, el-button

#### 3. PositionWeights.vue
- **功能**: 职级权重配置页面
- **特性**: 权重编辑、批量更新、默认权重加载
- **组件**: el-table, el-input-number, el-button

#### 4. Evaluation.vue
- **功能**: 考核任务列表页面
- **特性**: 任务筛选、状态显示、操作按钮
- **组件**: el-table, el-tag, el-button

#### 5. EvaluationForm.vue
- **功能**: 评分表单页面
- **特性**: 指标评分、意见填写、权重显示
- **组件**: el-form, el-input, el-rate

### 状态管理 (Pinia)

#### 考核状态管理
```typescript
// stores/evaluation.ts
export const useEvaluationStore = defineStore('evaluation', {
  state: () => ({
    cycles: [] as Cycle[],
    tasks: [] as Task[],
    loading: false
  }),
  
  actions: {
    async loadCycles() {
      this.loading = true
      try {
        const res = await cycleApi.list()
        this.cycles = res.data.results
      } finally {
        this.loading = false
      }
    }
  }
})
```

---

## 🚀 部署指南

### 开发环境部署

#### 1. 克隆项目
```bash
git clone <repository-url>
cd performance-system
```

#### 2. 安装依赖
```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 前端依赖
cd ../frontend
npm install
```

#### 3. 数据库迁移
```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

#### 4. 启动服务
```bash
# 启动后端
python manage.py runserver 8001

# 启动前端
npm run dev
```

### 生产环境部署

#### Docker部署
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用代码
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 启动服务
CMD ["gunicorn", "performance_system.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### Nginx配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 👨‍💻 开发指南

### 开发环境设置

#### 1. 代码规范
```bash
# 前端代码格式化
npm run lint
npm run format

# 后端代码检查
pip install flake8 black
flake8 .
black .
```

#### 2. 测试
```bash
# 前端测试
npm run test

# 后端测试
python manage.py test
```

#### 3. 数据库管理
```bash
# 创建迁移文件
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 查看迁移状态
python manage.py showmigrations
```

### 新功能开发流程

#### 1. 后端API开发
```python
# 1. 定义模型
class NewModel(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

# 2. 创建序列化器
class NewModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewModel
        fields = '__all__'

# 3. 创建视图
class NewModelViewSet(viewsets.ModelViewSet):
    queryset = NewModel.objects.all()
    serializer_class = NewModelSerializer
```

#### 2. 前端组件开发
```vue
<template>
  <div class="new-component">
    <el-table :data="data" v-loading="loading">
      <el-table-column prop="name" label="名称" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const data = ref([])
const loading = ref(false)

onMounted(() => {
  loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    // API调用
  } finally {
    loading.value = false
  }
}
</script>
```

### 调试技巧

#### 1. 前端调试
```javascript
// 控制台调试
console.log('调试信息:', data)

// Vue DevTools
// 安装Vue DevTools浏览器扩展
```

#### 2. 后端调试
```python
# Django调试
import logging
logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug('调试信息: %s', data)
    return Response(data)
```

#### 3. 数据库调试
```python
# 查看SQL查询
from django.db import connection
print(connection.queries)
```

---

## 📊 性能优化

### 前端优化
- **代码分割**: 使用动态导入
- **懒加载**: 路由级别的懒加载
- **缓存**: 合理使用浏览器缓存
- **压缩**: 生产环境代码压缩

### 后端优化
- **数据库索引**: 为常用查询字段添加索引
- **查询优化**: 使用select_related和prefetch_related
- **缓存**: 使用Redis缓存热点数据
- **分页**: 大数据量使用分页查询

### 系统监控
- **日志记录**: 完整的操作日志
- **性能监控**: 响应时间监控
- **错误追踪**: 异常信息收集
- **资源监控**: CPU、内存使用情况

---

## 🔒 安全考虑

### 数据安全
- **输入验证**: 所有用户输入进行验证
- **SQL注入防护**: 使用ORM防止SQL注入
- **XSS防护**: 前端输入过滤
- **CSRF防护**: 使用CSRF令牌

### 访问控制
- **权限管理**: 基于角色的权限控制
- **会话管理**: 安全的会话处理
- **API认证**: JWT或Session认证
- **HTTPS**: 生产环境使用HTTPS

---

*技术文档版本: v1.0.0*  
*最后更新: 2025年9月27日*
