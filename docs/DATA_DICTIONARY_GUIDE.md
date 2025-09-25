# 数据字典和系统配置管理指南

## 📋 目录

- [数据字典管理](#数据字典管理)
- [系统配置管理](#系统配置管理)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

## 📚 数据字典管理

### 概述

数据字典是系统中用于管理标准化数据的核心功能，确保数据的一致性和规范性。通过数据字典，可以：

- 统一管理下拉选项
- 确保数据格式一致
- 支持多语言和国际化
- 便于数据统计和分析

### 字典分类详解

#### 1. 员工状态 (employee_status)

管理员工的各种工作状态。

**预定义值**：
```
active     - 在职
leave      - 休假
resigned   - 离职
retired    - 退休
suspended  - 停职
```

**使用场景**：
- 员工状态筛选
- 考勤管理
- 薪资计算
- 报表统计

**配置示例**：
```json
{
  "category": "employee_status",
  "code": "active",
  "name": "在职",
  "value": "1",
  "description": "正常在职状态",
  "sort_order": 1,
  "is_active": true
}
```

#### 2. 学历层次 (education_level)

管理员工的教育背景。

**预定义值**：
```
doctor     - 博士
master     - 硕士
bachelor   - 本科
college    - 专科
high_school - 高中
middle_school - 初中
elementary - 小学
```

**使用场景**：
- 员工档案管理
- 招聘要求设置
- 培训计划制定
- 统计分析

**配置示例**：
```json
{
  "category": "education_level",
  "code": "bachelor",
  "name": "本科",
  "value": "4",
  "description": "本科学历",
  "sort_order": 3,
  "is_active": true
}
```

#### 3. 技能等级 (skill_level)

管理员工的专业技能水平。

**预定义值**：
```
expert      - 专家级
senior      - 高级
intermediate - 中级
junior      - 初级
beginner    - 入门级
```

**使用场景**：
- 技能评估
- 培训计划
- 职业发展
- 项目分配

**配置示例**：
```json
{
  "category": "skill_level",
  "code": "senior",
  "name": "高级",
  "value": "4",
  "description": "高级技能水平",
  "sort_order": 2,
  "is_active": true
}
```

#### 4. 婚姻状况 (marital_status)

管理员工的婚姻信息。

**预定义值**：
```
single    - 未婚
married   - 已婚
divorced  - 离异
widowed   - 丧偶
```

**使用场景**：
- 员工档案
- 福利管理
- 统计分析
- 法律合规

#### 5. 部门类型 (department_type)

管理部门的分类。

**预定义值**：
```
management - 管理部门
business   - 业务部门
support    - 支持部门
technical  - 技术部门
finance    - 财务部门
hr         - 人事部门
```

**使用场景**：
- 组织架构管理
- 权限分配
- 报表统计
- 预算管理

#### 6. 职位级别 (position_level)

管理职位的等级体系。

**预定义值**：
```
13 - 高层正职
12 - 高层副职
11 - 高层助理
9  - 中层正职
8  - 中层副职
7  - 中层助理
4  - 基层正职
3  - 基层副职
2  - 基层助理
1  - 员工
```

**使用场景**：
- 职位管理
- 权限控制
- 审批流程
- 薪资体系

#### 7. 工作流状态 (workflow_status)

管理工作流的执行状态。

**预定义值**：
```
pending    - 待处理
processing - 处理中
completed  - 已完成
rejected   - 已拒绝
cancelled  - 已取消
expired    - 已过期
```

**使用场景**：
- 工作流监控
- 状态跟踪
- 报表统计
- 性能分析

### 字典管理操作

#### 1. 创建字典项

**步骤**：
1. 进入"数据字典"页面
2. 选择字典分类
3. 点击"新增字典项"
4. 填写字典信息
5. 保存字典项

**字段说明**：
- **编码 (code)**：唯一标识，建议使用英文小写
- **名称 (name)**：显示名称，支持中文
- **值 (value)**：字典值，用于存储和比较
- **描述 (description)**：详细说明
- **排序 (sort_order)**：显示顺序，数字越小越靠前
- **父级 (parent)**：支持层级结构
- **状态 (is_active)**：是否启用

**示例**：
```json
{
  "code": "senior_engineer",
  "name": "高级工程师",
  "value": "5",
  "category": "position_level",
  "description": "高级工程师职位",
  "sort_order": 5,
  "parent": null,
  "is_active": true
}
```

#### 2. 编辑字典项

**步骤**：
1. 在字典列表中找到目标项
2. 点击"编辑"按钮
3. 修改字典信息
4. 保存更改

**注意事项**：
- 编码不能修改
- 修改后需要更新相关引用
- 建议先备份数据

#### 3. 删除字典项

**步骤**：
1. 选择要删除的字典项
2. 点击"删除"按钮
3. 确认删除操作

**注意事项**：
- 删除前检查是否有引用
- 删除后无法恢复
- 建议先禁用再删除

#### 4. 字典项排序

**方法一：通过排序字段**
```json
{
  "sort_order": 1  // 数字越小排序越靠前
}
```

**方法二：通过拖拽排序**
- 在字典列表中直接拖拽
- 自动更新排序值
- 实时保存排序结果

### 字典使用

#### 1. 前端使用

**获取字典数据**：
```javascript
// 获取员工状态选项
const employeeStatusOptions = await dictionaryApi.getDictionaries({
  category: 'employee_status'
})

// 获取学历层次选项
const educationOptions = await dictionaryApi.getDictionaries({
  category: 'education_level'
})
```

**表单中使用**：
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

**数据验证**：
```javascript
// 验证员工状态
const validStatuses = ['active', 'leave', 'resigned', 'retired']
if (!validStatuses.includes(employee.status)) {
  throw new Error('无效的员工状态')
}
```

#### 2. 后端使用

**获取字典数据**：
```python
from organizations.models import Dictionary

# 获取员工状态字典
employee_statuses = Dictionary.objects.filter(
    category='employee_status',
    is_active=True
).order_by('sort_order')

# 获取学历层次字典
education_levels = Dictionary.objects.filter(
    category='education_level',
    is_active=True
).order_by('sort_order')
```

**数据验证**：
```python
def validate_employee_status(status):
    valid_statuses = Dictionary.objects.filter(
        category='employee_status',
        is_active=True
    ).values_list('code', flat=True)
    
    if status not in valid_statuses:
        raise ValidationError('无效的员工状态')
```

#### 3. 报表统计

**按学历统计员工数量**：
```python
from django.db.models import Count

education_stats = Employee.objects.values(
    'education_level'
).annotate(
    count=Count('id')
).order_by('education_level')
```

**按部门类型统计**：
```python
department_stats = Department.objects.values(
    'department_type'
).annotate(
    count=Count('id')
).order_by('department_type')
```

## ⚙️ 系统配置管理

### 概述

系统配置用于管理系统的各种参数和设置，实现系统的灵活配置和个性化定制。

### 配置分类详解

#### 1. 组织架构配置 (organization)

管理组织架构相关的配置参数。

**主要配置项**：

##### max_department_levels
- **描述**：最大部门层级数
- **类型**：integer
- **默认值**：5
- **用途**：限制部门层级深度

```json
{
  "key": "max_department_levels",
  "value": "5",
  "category": "organization",
  "description": "最大部门层级数",
  "data_type": "integer",
  "is_required": true,
  "is_active": true
}
```

##### allow_cross_department_position
- **描述**：是否允许跨部门职位
- **类型**：boolean
- **默认值**：false
- **用途**：控制职位分配规则

```json
{
  "key": "allow_cross_department_position",
  "value": "false",
  "category": "organization",
  "description": "是否允许跨部门职位",
  "data_type": "boolean",
  "is_required": false,
  "is_active": true
}
```

##### department_naming_rule
- **描述**：部门命名规则
- **类型**：string
- **默认值**："{parent}_{type}_{level}"
- **用途**：自动生成部门名称

```json
{
  "key": "department_naming_rule",
  "value": "{parent}_{type}_{level}",
  "category": "organization",
  "description": "部门命名规则",
  "data_type": "string",
  "is_required": false,
  "is_active": true
}
```

#### 2. 职位配置 (position)

管理职位相关的配置参数。

**主要配置项**：

##### position_level_validation
- **描述**：是否启用职位级别验证
- **类型**：boolean
- **默认值**：true
- **用途**：控制职位级别验证

```json
{
  "key": "position_level_validation",
  "value": "true",
  "category": "position",
  "description": "是否启用职位级别验证",
  "data_type": "boolean",
  "is_required": true,
  "is_active": true
}
```

##### position_naming_rule
- **描述**：职位命名规则
- **类型**：string
- **默认值**："{level}_{type}_{department}"
- **用途**：自动生成职位名称

```json
{
  "key": "position_naming_rule",
  "value": "{level}_{type}_{department}",
  "category": "position",
  "description": "职位命名规则",
  "data_type": "string",
  "is_required": false,
  "is_active": true
}
```

##### position_approval_required
- **描述**：职位变更是否需要审批
- **类型**：boolean
- **默认值**：true
- **用途**：控制职位变更流程

```json
{
  "key": "position_approval_required",
  "value": "true",
  "category": "position",
  "description": "职位变更是否需要审批",
  "data_type": "boolean",
  "is_required": false,
  "is_active": true
}
```

#### 3. 员工配置 (employee)

管理员工相关的配置参数。

**主要配置项**：

##### auto_generate_employee_id
- **描述**：是否自动生成员工号
- **类型**：boolean
- **默认值**：true
- **用途**：控制员工号生成

```json
{
  "key": "auto_generate_employee_id",
  "value": "true",
  "category": "employee",
  "description": "是否自动生成员工号",
  "data_type": "boolean",
  "is_required": true,
  "is_active": true
}
```

##### employee_id_prefix
- **描述**：员工号前缀
- **类型**：string
- **默认值**：EMP
- **用途**：员工号生成规则

```json
{
  "key": "employee_id_prefix",
  "value": "EMP",
  "category": "employee",
  "description": "员工号前缀",
  "data_type": "string",
  "is_required": true,
  "is_active": true
}
```

##### require_supervisor
- **描述**：是否必须设置直接上级
- **类型**：boolean
- **默认值**：true
- **用途**：控制组织关系

```json
{
  "key": "require_supervisor",
  "value": "true",
  "category": "employee",
  "description": "是否必须设置直接上级",
  "data_type": "boolean",
  "is_required": true,
  "is_active": true
}
```

#### 4. 工作流配置 (workflow)

管理工作流相关的配置参数。

**主要配置项**：

##### default_workflow_enabled
- **描述**：是否启用默认工作流
- **类型**：boolean
- **默认值**：true
- **用途**：控制工作流执行

```json
{
  "key": "default_workflow_enabled",
  "value": "true",
  "category": "workflow",
  "description": "是否启用默认工作流",
  "data_type": "boolean",
  "is_required": false,
  "is_active": true
}
```

##### workflow_timeout
- **描述**：工作流超时时间（小时）
- **类型**：integer
- **默认值**：24
- **用途**：控制工作流超时

```json
{
  "key": "workflow_timeout",
  "value": "24",
  "category": "workflow",
  "description": "工作流超时时间（小时）",
  "data_type": "integer",
  "is_required": false,
  "is_active": true
}
```

##### workflow_retry_count
- **描述**：工作流重试次数
- **类型**：integer
- **默认值**：3
- **用途**：控制重试机制

```json
{
  "key": "workflow_retry_count",
  "value": "3",
  "category": "workflow",
  "description": "工作流重试次数",
  "data_type": "integer",
  "is_required": false,
  "is_active": true
}
```

#### 5. 集成配置 (integration)

管理系统集成相关的配置参数。

**主要配置项**：

##### performance_system_url
- **描述**：绩效考核系统URL
- **类型**：string
- **默认值**：http://localhost:8000
- **用途**：数据同步目标

```json
{
  "key": "performance_system_url",
  "value": "http://localhost:8000",
  "category": "integration",
  "description": "绩效考核系统URL",
  "data_type": "string",
  "is_required": false,
  "is_active": true
}
```

##### finance_system_url
- **描述**：财务系统URL
- **类型**：string
- **默认值**：http://localhost:8002
- **用途**：数据同步目标

```json
{
  "key": "finance_system_url",
  "value": "http://localhost:8002",
  "category": "integration",
  "description": "财务系统URL",
  "data_type": "string",
  "is_required": false,
  "is_active": true
}
```

##### sync_interval
- **描述**：数据同步间隔（分钟）
- **类型**：integer
- **默认值**：60
- **用途**：控制同步频率

```json
{
  "key": "sync_interval",
  "value": "60",
  "category": "integration",
  "description": "数据同步间隔（分钟）",
  "data_type": "integer",
  "is_required": false,
  "is_active": true
}
```

#### 6. 安全配置 (security)

管理系统安全相关的配置参数。

**主要配置项**：

##### password_policy
- **描述**：密码策略
- **类型**：json
- **默认值**：{"min_length":8,"require_uppercase":true,"require_lowercase":true,"require_numbers":true,"require_symbols":true}
- **用途**：控制密码复杂度

```json
{
  "key": "password_policy",
  "value": "{\"min_length\":8,\"require_uppercase\":true,\"require_lowercase\":true,\"require_numbers\":true,\"require_symbols\":true}",
  "category": "security",
  "description": "密码策略",
  "data_type": "json",
  "is_required": true,
  "is_active": true
}
```

##### session_timeout
- **描述**：会话超时时间（分钟）
- **类型**：integer
- **默认值**：30
- **用途**：控制会话超时

```json
{
  "key": "session_timeout",
  "value": "30",
  "category": "security",
  "description": "会话超时时间（分钟）",
  "data_type": "integer",
  "is_required": false,
  "is_active": true
}
```

##### login_attempt_limit
- **描述**：登录尝试次数限制
- **类型**：integer
- **默认值**：5
- **用途**：防止暴力破解

```json
{
  "key": "login_attempt_limit",
  "value": "5",
  "category": "security",
  "description": "登录尝试次数限制",
  "data_type": "integer",
  "is_required": false,
  "is_active": true
}
```

#### 7. 通知配置 (notification)

管理通知相关的配置参数。

**主要配置项**：

##### notification_enabled
- **描述**：是否启用通知功能
- **类型**：boolean
- **默认值**：true
- **用途**：控制通知功能

```json
{
  "key": "notification_enabled",
  "value": "true",
  "category": "notification",
  "description": "是否启用通知功能",
  "data_type": "boolean",
  "is_required": false,
  "is_active": true
}
```

##### email_smtp_server
- **描述**：邮件SMTP服务器
- **类型**：string
- **默认值**：smtp.company.com
- **用途**：邮件发送配置

```json
{
  "key": "email_smtp_server",
  "value": "smtp.company.com",
  "category": "notification",
  "description": "邮件SMTP服务器",
  "data_type": "string",
  "is_required": false,
  "is_active": true
}
```

##### sms_provider
- **描述**：短信服务提供商
- **类型**：string
- **默认值**：aliyun
- **用途**：短信发送配置

```json
{
  "key": "sms_provider",
  "value": "aliyun",
  "category": "notification",
  "description": "短信服务提供商",
  "data_type": "string",
  "is_required": false,
  "is_active": true
}
```

### 配置管理操作

#### 1. 创建配置

**步骤**：
1. 进入"系统配置"页面
2. 点击"新增配置"
3. 填写配置信息
4. 保存配置

**字段说明**：
- **配置键 (key)**：唯一标识，建议使用小写字母和下划线
- **配置值 (value)**：配置内容，支持多种数据类型
- **配置分类 (category)**：选择配置分类
- **数据类型 (data_type)**：选择数据类型
- **描述 (description)**：详细说明
- **是否必需 (is_required)**：是否必需配置
- **是否启用 (is_active)**：是否启用

**示例**：
```json
{
  "key": "custom_employee_id_format",
  "value": "EMP{year}{month}{sequence}",
  "category": "employee",
  "description": "自定义员工号格式",
  "data_type": "string",
  "is_required": false,
  "is_active": true
}
```

#### 2. 编辑配置

**步骤**：
1. 在配置列表中找到目标配置
2. 点击"编辑"按钮
3. 修改配置值
4. 保存更改

**注意事项**：
- 配置键不能修改
- 修改后需要重启相关服务
- 建议先备份配置

#### 3. 删除配置

**步骤**：
1. 选择要删除的配置
2. 点击"删除"按钮
3. 确认删除操作

**注意事项**：
- 删除前检查是否有引用
- 删除后无法恢复
- 建议先禁用再删除

#### 4. 配置导入/导出

**导出配置**：
1. 进入系统配置页面
2. 点击"导出配置"
3. 选择导出格式（JSON）
4. 下载配置文件

**导入配置**：
1. 准备配置文件
2. 点击"导入配置"
3. 选择配置文件
4. 确认导入操作

### 配置使用

#### 1. 后端使用

**获取配置值**：
```python
from organizations.models import SystemConfig

# 获取单个配置
config = SystemConfig.objects.get(key='max_department_levels')
max_levels = int(config.value)

# 获取分类配置
org_configs = SystemConfig.objects.filter(
    category='organization',
    is_active=True
)
```

**配置缓存**：
```python
from django.core.cache import cache

def get_config(key, default=None):
    cache_key = f"config:{key}"
    value = cache.get(cache_key)
    if value is None:
        try:
            config = SystemConfig.objects.get(key=key, is_active=True)
            value = config.value
            cache.set(cache_key, value, 3600)  # 缓存1小时
        except SystemConfig.DoesNotExist:
            value = default
    return value
```

**配置验证**：
```python
def validate_required_configs():
    required_configs = SystemConfig.objects.filter(
        is_required=True,
        is_active=True
    )
    for config in required_configs:
        if not config.value:
            raise ValueError(f"必需配置 {config.key} 未设置")
```

#### 2. 前端使用

**获取配置值**：
```javascript
// 获取单个配置
const config = await configApi.getConfig('max_department_levels')
const maxLevels = parseInt(config.value)

// 获取分类配置
const orgConfigs = await configApi.getConfigs({
  category: 'organization'
})
```

**配置验证**：
```javascript
// 验证必需配置
const requiredConfigs = await configApi.getConfigs({
  is_required: true
})

for (const config of requiredConfigs) {
  if (!config.value) {
    throw new Error(`必需配置 ${config.key} 未设置`)
  }
}
```

#### 3. 配置应用

**组织架构配置应用**：
```python
def create_department(name, parent=None):
    # 检查部门层级限制
    max_levels = get_config('max_department_levels', 5)
    if parent and parent.level >= max_levels:
        raise ValueError('部门层级超过限制')
    
    # 创建部门
    department = Department.objects.create(
        name=name,
        parent=parent,
        level=parent.level + 1 if parent else 1
    )
    return department
```

**员工配置应用**：
```python
def create_employee(employee_data):
    # 自动生成员工号
    if get_config('auto_generate_employee_id', True):
        prefix = get_config('employee_id_prefix', 'EMP')
        employee_id = generate_employee_id(prefix)
        employee_data['employee_id'] = employee_id
    
    # 创建员工
    employee = Employee.objects.create(**employee_data)
    return employee
```

**工作流配置应用**：
```python
def execute_workflow(rule_id, context):
    # 检查工作流是否启用
    if not get_config('default_workflow_enabled', True):
        return False
    
    # 获取超时时间
    timeout = get_config('workflow_timeout', 24)
    
    # 执行工作流
    result = workflow_service.execute(rule_id, context, timeout)
    return result
```

## 🎯 最佳实践

### 1. 数据字典设计

#### 编码规范
- 使用英文小写字母
- 使用下划线分隔单词
- 保持简洁明了
- 避免使用特殊字符

**好的编码示例**：
```
employee_status
education_level
skill_level
department_type
```

**不好的编码示例**：
```
EmployeeStatus
education-level
skillLevel
dept_type
```

#### 分类管理
- 按业务领域分类
- 保持分类的一致性
- 避免分类过多
- 定期整理分类

#### 值管理
- 值要具有业务意义
- 避免重复和冲突
- 考虑国际化需求
- 支持多语言

### 2. 系统配置设计

#### 配置键命名
- 使用小写字母和下划线
- 包含配置分类前缀
- 保持命名的一致性
- 使用描述性名称

**示例**：
```
max_department_levels
auto_generate_employee_id
notification_enabled
workflow_timeout
```

#### 配置值设计
- 使用合适的数据类型
- 提供默认值
- 考虑配置的依赖关系
- 支持配置验证

#### 配置文档
- 为每个配置提供详细说明
- 说明配置的影响范围
- 提供配置示例
- 记录配置变更历史

### 3. 性能优化

#### 配置缓存
```python
from django.core.cache import cache

def get_config(key, default=None):
    cache_key = f"config:{key}"
    value = cache.get(cache_key)
    if value is None:
        try:
            config = SystemConfig.objects.get(key=key, is_active=True)
            value = config.value
            cache.set(cache_key, value, 3600)  # 缓存1小时
        except SystemConfig.DoesNotExist:
            value = default
    return value
```

#### 字典缓存
```python
def get_dictionary_options(category):
    cache_key = f"dict:{category}"
    options = cache.get(cache_key)
    if options is None:
        options = Dictionary.objects.filter(
            category=category,
            is_active=True
        ).order_by('sort_order')
        cache.set(cache_key, options, 3600)  # 缓存1小时
    return options
```

### 4. 安全考虑

#### 配置加密
```python
from cryptography.fernet import Fernet

def encrypt_config_value(value):
    key = settings.CONFIG_ENCRYPTION_KEY
    f = Fernet(key)
    return f.encrypt(value.encode())

def decrypt_config_value(encrypted_value):
    key = settings.CONFIG_ENCRYPTION_KEY
    f = Fernet(key)
    return f.decrypt(encrypted_value).decode()
```

#### 权限控制
```python
def check_config_permission(user, config_key):
    # 检查用户是否有权限访问配置
    if user.is_superuser:
        return True
    
    # 检查配置的访问权限
    config = SystemConfig.objects.get(key=config_key)
    if config.is_encrypted and not user.has_perm('organizations.view_encrypted_config'):
        return False
    
    return True
```

## ❓ 常见问题

### Q1: 数据字典如何添加新的分类？

**A**: 在字典管理页面：
1. 选择"自定义"分类
2. 创建新的字典项
3. 设置分类名称
4. 添加字典值

### Q2: 系统配置如何备份？

**A**: 使用配置导出功能：
1. 进入系统配置页面
2. 点击"导出配置"
3. 保存JSON文件
4. 定期备份配置文件

### Q3: 配置修改后如何生效？

**A**: 配置修改后：
1. 清除相关缓存
2. 重启相关服务
3. 检查配置是否正确
4. 验证功能是否正常

### Q4: 如何批量导入数据字典？

**A**: 使用批量导入功能：
1. 准备Excel模板文件
2. 进入数据字典页面
3. 点击"批量导入"
4. 上传模板文件
5. 确认导入结果

### Q5: 配置验证失败怎么办？

**A**: 检查以下几个方面：
1. 配置格式是否正确
2. 数据类型是否匹配
3. 必需配置是否完整
4. 配置值是否有效

---

**通过本指南，您应该能够熟练管理数据字典和系统配置。如有任何问题，请参考常见问题部分或联系技术支持。**
