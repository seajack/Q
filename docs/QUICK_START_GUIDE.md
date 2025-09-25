# 组织架构中台系统快速入门指南

## 🚀 快速开始

### 环境准备

#### 系统要求
- Python 3.11+
- Node.js 18+
- SQLite/MySQL/PostgreSQL
- Git

#### 开发环境
- IDE: VS Code / PyCharm
- 浏览器: Chrome / Firefox
- 数据库管理工具: DBeaver / Navicat

### 安装部署

#### 1. 克隆项目
```bash
git clone https://github.com/seajack/Q.git
cd Q/org-platform
```

#### 2. 后端部署
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 初始化配置数据
python manage.py init_config_data

# 创建超级用户
python manage.py createsuperuser

# 启动后端服务
python manage.py runserver 0.0.0.0:8001
```

#### 3. 前端部署
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 4. 访问系统
- 前端地址：http://localhost:3000
- 后端API：http://localhost:8001/api/
- 管理后台：http://localhost:8001/admin/

## 📚 核心功能快速上手

### 1. 组织架构管理

#### 创建部门
1. 进入"部门管理"页面
2. 点击"新增部门"
3. 填写部门信息：
   - 部门名称：技术部
   - 上级部门：选择上级部门
   - 部门类型：技术部门
   - 部门描述：负责技术开发工作
4. 保存部门

#### 创建职位
1. 进入"职位管理"页面
2. 点击"新增职位"
3. 填写职位信息：
   - 职位名称：高级工程师
   - 所属部门：选择部门
   - 职位级别：8
   - 管理层级：中层
   - 职位类型：正职
4. 保存职位

#### 添加员工
1. 进入"员工管理"页面
2. 点击"新增员工"
3. 填写员工信息：
   - 姓名：张三
   - 工号：EMP001
   - 部门：技术部
   - 职位：高级工程师
   - 直接上级：选择上级
4. 保存员工

### 2. 工作流规则配置

#### 创建审批流程
1. 进入"工作流规则"页面
2. 点击"新增规则"
3. 填写基本信息：
   - 规则名称：员工入职审批流程
   - 规则类型：审批流程
   - 优先级：10
4. 配置触发条件：
   - 选择"事件触发"
   - 事件类型：员工创建
5. 配置执行动作：
   - 选择"创建审批"
   - 审批流程：直接上级 → HR经理
6. 保存规则

#### 创建通知规则
1. 进入"工作流规则"页面
2. 点击"新增规则"
3. 填写基本信息：
   - 规则名称：新员工入职通知
   - 规则类型：通知规则
4. 配置触发条件：
   - 选择"事件触发"
   - 事件类型：员工创建
5. 配置执行动作：
   - 选择"发送通知"
   - 通知类型：邮件
   - 接收人：HR部门
6. 保存规则

### 3. 数据字典管理

#### 添加字典项
1. 进入"数据字典"页面
2. 选择字典分类：员工状态
3. 点击"新增字典项"
4. 填写字典信息：
   - 编码：active
   - 名称：在职
   - 值：1
   - 描述：正常在职状态
5. 保存字典项

#### 使用字典项
在表单中使用字典项：
```vue
<template>
  <el-select v-model="form.employeeStatus" placeholder="请选择员工状态">
    <el-option
      v-for="option in employeeStatusOptions"
      :key="option.code"
      :label="option.name"
      :value="option.code"
    />
  </el-select>
</template>
```

### 4. 系统配置管理

#### 添加系统配置
1. 进入"系统配置"页面
2. 点击"新增配置"
3. 填写配置信息：
   - 配置键：max_department_levels
   - 配置值：5
   - 配置分类：组织架构配置
   - 数据类型：整数
   - 描述：最大部门层级数
4. 保存配置

#### 使用系统配置
```python
# 后端获取配置
from organizations.models import SystemConfig

config = SystemConfig.objects.get(key='max_department_levels')
max_levels = int(config.value)
```

```javascript
// 前端获取配置
const config = await configApi.getConfig('max_department_levels')
const maxLevels = parseInt(config.value)
```

## 🎯 常用场景示例

### 场景1：新员工入职流程

#### 1. 创建员工
- 填写基本信息
- 选择部门和职位
- 设置直接上级

#### 2. 自动触发工作流
- 发送入职通知
- 创建审批流程
- 自动分配权限

#### 3. 审批处理
- 直接上级审批
- HR经理审批
- 完成入职流程

### 场景2：部门调整流程

#### 1. 调整部门结构
- 创建新部门
- 调整部门关系
- 更新部门信息

#### 2. 自动通知相关人员
- 部门成员通知
- 相关部门通知
- HR部门通知

#### 3. 数据同步
- 同步到其他系统
- 更新相关数据
- 记录变更历史

### 场景3：职位变更流程

#### 1. 申请职位变更
- 填写变更申请
- 选择目标职位
- 提交审批

#### 2. 多级审批
- 直接上级审批
- 部门经理审批
- 总经理审批（如需要）

#### 3. 执行变更
- 更新职位信息
- 调整权限
- 通知相关人员

## 🔧 开发指南

### 1. 后端开发

#### 创建新的API接口
```python
# 在 views.py 中添加
from rest_framework import viewsets
from .models import YourModel
from .serializers import YourSerializer

class YourViewSet(viewsets.ModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourSerializer
```

#### 创建新的数据模型
```python
# 在 models.py 中添加
from django.db import models

class YourModel(models.Model):
    name = models.CharField('名称', max_length=100)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '您的模型'
        verbose_name_plural = '您的模型'
```

#### 创建新的序列化器
```python
# 在 serializers.py 中添加
from rest_framework import serializers
from .models import YourModel

class YourSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = '__all__'
```

### 2. 前端开发

#### 创建新的页面组件
```vue
<template>
  <div class="your-component">
    <el-card>
      <template #header>
        <span>您的组件</span>
      </template>
      <!-- 组件内容 -->
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const data = ref([])
const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    // 加载数据
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
```

#### 创建新的API服务
```typescript
// 在 utils/api.ts 中添加
export const yourApi = {
  list: (params?: any) => api.get<ApiResponse<YourType[]>>('/your-endpoint/', { params }),
  create: (data: Partial<YourType>) => api.post<YourType>('/your-endpoint/', data),
  get: (id: number) => api.get<YourType>(`/your-endpoint/${id}/`),
  update: (id: number, data: Partial<YourType>) => api.put<YourType>(`/your-endpoint/${id}/`, data),
  delete: (id: number) => api.delete(`/your-endpoint/${id}/`),
}
```

### 3. 数据库操作

#### 创建数据库迁移
```bash
# 创建迁移文件
python manage.py makemigrations

# 应用迁移
python manage.py migrate
```

#### 数据库查询
```python
# 基本查询
from organizations.models import Employee

# 获取所有员工
employees = Employee.objects.all()

# 按条件查询
active_employees = Employee.objects.filter(status='active')

# 关联查询
employees_with_department = Employee.objects.select_related('department')

# 聚合查询
from django.db.models import Count
department_stats = Employee.objects.values('department').annotate(count=Count('id'))
```

## 🐛 故障排除

### 1. 常见错误

#### 后端错误
- **数据库连接错误**：检查数据库配置
- **迁移错误**：运行 `python manage.py migrate`
- **依赖错误**：运行 `pip install -r requirements.txt`

#### 前端错误
- **依赖错误**：运行 `npm install`
- **构建错误**：检查 Node.js 版本
- **API错误**：检查后端服务是否启动

### 2. 调试技巧

#### 后端调试
```python
# 使用 Django 调试工具
import pdb; pdb.set_trace()

# 查看 SQL 查询
from django.db import connection
print(connection.queries)
```

#### 前端调试
```javascript
// 使用浏览器调试工具
console.log('调试信息')

// 使用 Vue 调试工具
// 安装 Vue DevTools 浏览器扩展
```

### 3. 性能优化

#### 数据库优化
```python
# 使用 select_related 减少查询次数
employees = Employee.objects.select_related('department', 'position')

# 使用 prefetch_related 预加载关联数据
departments = Department.objects.prefetch_related('employees')
```

#### 前端优化
```javascript
// 使用懒加载
const LazyComponent = defineAsyncComponent(() => import('./LazyComponent.vue'))

// 使用缓存
const cachedData = useMemo(() => expensiveCalculation(data), [data])
```

## 📞 技术支持

### 联系方式
- 技术支持邮箱：support@company.com
- 技术文档：https://docs.company.com
- 问题反馈：https://github.com/seajack/Q/issues

### 社区支持
- GitHub Issues：https://github.com/seajack/Q/issues
- 技术论坛：https://forum.company.com
- 微信群：扫描二维码加入

### 版本信息
- 当前版本：v1.0.0
- 最后更新：2024-01-01
- 兼容性：Python 3.11+, Node.js 18+

---

**通过本指南，您应该能够快速上手组织架构中台系统。如有任何问题，请随时联系技术支持团队。**
