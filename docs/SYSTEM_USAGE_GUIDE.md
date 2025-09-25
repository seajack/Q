# 组织架构中台系统使用说明文档

## 📋 目录

- [系统概述](#系统概述)
- [快速开始](#快速开始)
- [核心功能详解](#核心功能详解)
  - [工作流规则管理](#工作流规则管理)
  - [数据字典管理](#数据字典管理)
  - [系统配置管理](#系统配置管理)
  - [职位模板管理](#职位模板管理)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [技术支持](#技术支持)

## 🎯 系统概述

组织架构中台系统是一个企业级的人力资源管理平台，提供完整的组织架构管理、员工管理、职位管理和工作流自动化功能。系统采用前后端分离架构，支持高并发和大规模企业应用。

### 核心特性

- **组织架构管理**：支持无限层级的部门树形结构
- **职位体系管理**：双维度职位级别体系（管理层级 + 职位类型）
- **员工信息管理**：完整的员工档案和用户账号集成
- **工作流自动化**：可视化工作流规则配置
- **数据标准化**：统一的数据字典管理
- **系统配置化**：灵活的配置参数管理

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- SQLite/MySQL/PostgreSQL

### 安装部署

1. **克隆项目**
```bash
git clone https://github.com/seajack/Q.git
cd Q/org-platform
```

2. **后端部署**
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py init_config_data  # 初始化配置数据
python manage.py runserver 0.0.0.0:8001
```

3. **前端部署**
```bash
cd frontend
npm install
npm run dev
```

4. **访问系统**
- 前端地址：http://localhost:3000
- 后端API：http://localhost:8001/api/
- 管理后台：http://localhost:8001/admin/

## 🔧 核心功能详解

### 工作流规则管理

工作流规则是系统的核心功能之一，用于实现业务流程的自动化处理。

#### 1. 规则类型

系统支持四种主要的工作流规则类型：

##### 🔔 审批流程 (approval)
用于处理需要多级审批的业务流程。

**典型场景**：
- 员工入职审批
- 职位变更审批
- 部门调整审批
- 权限申请审批

**配置示例**：
```json
{
  "name": "员工入职审批流程",
  "rule_type": "approval",
  "trigger_conditions": {
    "event": "employee_created",
    "conditions": {
      "position_level": ">=": 8
    }
  },
  "action_config": {
    "approval_flow": [
      {"step": 1, "approver": "direct_supervisor", "required": true},
      {"step": 2, "approver": "hr_manager", "required": true}
    ],
    "timeout": 24
  }
}
```

##### 📧 通知规则 (notification)
用于自动发送各种类型的通知。

**典型场景**：
- 新员工入职通知
- 部门调整通知
- 权限变更通知
- 系统维护通知

**配置示例**：
```json
{
  "name": "新员工入职通知",
  "rule_type": "notification",
  "trigger_conditions": {
    "event": "employee_created"
  },
  "action_config": {
    "notification_type": "email",
    "recipients": ["hr@company.com", "it@company.com"],
    "template": "new_employee_welcome"
  }
}
```

##### 🔄 数据同步 (data_sync)
用于与其他系统进行数据同步。

**典型场景**：
- 与绩效考核系统同步
- 与财务系统同步
- 与OA系统同步
- 与CRM系统同步

**配置示例**：
```json
{
  "name": "员工信息同步到绩效系统",
  "rule_type": "data_sync",
  "trigger_conditions": {
    "event": "employee_updated"
  },
  "action_config": {
    "sync_target": "performance_system",
    "sync_fields": ["basic_info", "organization", "position"],
    "sync_method": "api"
  }
}
```

##### 🔐 权限控制 (permission)
用于自动管理用户权限。

**典型场景**：
- 新员工权限分配
- 职位变更权限调整
- 离职员工权限回收
- 临时权限授予

**配置示例**：
```json
{
  "name": "高级职位权限分配",
  "rule_type": "permission",
  "trigger_conditions": {
    "field": "position_level",
    "operator": ">=",
    "value": "8"
  },
  "action_config": {
    "permission_type": "system",
    "permission_action": "grant",
    "permissions": ["management_access", "report_access"]
  }
}
```

#### 2. 可视化配置

系统提供直观的可视化配置界面，无需编写JSON代码。

##### 触发条件配置

**事件触发**：
- 选择事件类型（员工创建、更新、离职等）
- 设置事件参数
- 配置触发时机

**字段条件**：
- 选择字段名称（职位级别、部门类型等）
- 选择比较操作（等于、大于、包含等）
- 设置比较值

**时间条件**：
- 工作时间/非工作时间
- 特定时间段
- 工作日/周末

**用户条件**：
- 用户角色筛选
- 部门筛选
- 权限级别筛选

**部门条件**：
- 部门类型筛选
- 部门级别筛选
- 部门层级筛选

##### 动作配置

**通知动作**：
- 选择通知类型（邮件、系统、短信、微信）
- 设置接收人
- 编写通知内容

**审批动作**：
- 配置审批流程
- 设置审批时限
- 定义必需审批人

**同步动作**：
- 选择同步目标系统
- 选择同步字段
- 配置同步方式

**权限动作**：
- 选择权限类型
- 设置权限操作
- 定义权限范围

#### 3. 规则管理

##### 创建规则
1. 进入"工作流规则"页面
2. 点击"新增规则"
3. 填写基本信息（名称、类型、优先级）
4. 配置触发条件（可视化或JSON）
5. 配置执行动作（可视化或JSON）
6. 保存规则

##### 编辑规则
1. 在规则列表中找到目标规则
2. 点击"编辑"按钮
3. 修改配置参数
4. 保存更改

##### 启用/禁用规则
- 在规则列表中切换"状态"开关
- 禁用的规则不会执行
- 支持批量操作

##### 规则优先级
- 数字越大优先级越高
- 相同条件下高优先级规则先执行
- 支持动态调整优先级

#### 4. 规则执行

##### 自动执行
- 系统根据触发条件自动执行规则
- 支持实时执行和定时执行
- 执行结果记录在日志中

##### 手动执行
- 支持手动触发规则执行
- 用于测试和调试
- 提供执行结果反馈

##### 执行监控
- 实时监控规则执行状态
- 记录执行日志和错误信息
- 提供性能统计和报告

### 数据字典管理

数据字典用于统一管理系统中的标准化数据，确保数据一致性和规范性。

#### 1. 字典分类

系统预定义了9种主要字典分类：

##### 👥 员工状态 (employee_status)
管理员工的各种状态。

**预定义值**：
- `active` - 在职
- `leave` - 休假
- `resigned` - 离职
- `retired` - 退休

**使用场景**：
- 员工状态筛选
- 报表统计
- 权限控制

##### 🎓 学历层次 (education_level)
管理员工学历信息。

**预定义值**：
- `doctor` - 博士
- `master` - 硕士
- `bachelor` - 本科
- `college` - 专科
- `high_school` - 高中

**使用场景**：
- 员工档案管理
- 招聘要求设置
- 统计分析

##### 🏆 技能等级 (skill_level)
管理员工技能水平。

**预定义值**：
- `expert` - 专家级
- `senior` - 高级
- `intermediate` - 中级
- `junior` - 初级
- `beginner` - 入门级

**使用场景**：
- 技能评估
- 培训计划
- 职业发展

##### 💒 婚姻状况 (marital_status)
管理员工婚姻信息。

**预定义值**：
- `single` - 未婚
- `married` - 已婚
- `divorced` - 离异
- `widowed` - 丧偶

**使用场景**：
- 员工档案
- 福利管理
- 统计分析

##### 🏢 部门类型 (department_type)
管理部门分类。

**预定义值**：
- `management` - 管理部门
- `business` - 业务部门
- `support` - 支持部门
- `technical` - 技术部门

**使用场景**：
- 组织架构管理
- 权限分配
- 报表统计

##### 📊 职位级别 (position_level)
管理职位等级。

**预定义值**：
- `13` - 高层正职
- `12` - 高层副职
- `11` - 高层助理
- `9` - 中层正职
- `8` - 中层副职
- `7` - 中层助理
- `4` - 基层正职
- `3` - 基层副职
- `2` - 基层助理
- `1` - 员工

**使用场景**：
- 职位管理
- 权限控制
- 审批流程

##### 🔄 工作流状态 (workflow_status)
管理工作流执行状态。

**预定义值**：
- `pending` - 待处理
- `processing` - 处理中
- `completed` - 已完成
- `rejected` - 已拒绝
- `cancelled` - 已取消

**使用场景**：
- 工作流监控
- 状态跟踪
- 报表统计

#### 2. 字典管理

##### 创建字典项
1. 进入"数据字典"页面
2. 选择字典分类
3. 点击"新增字典项"
4. 填写字典信息：
   - 编码：唯一标识
   - 名称：显示名称
   - 值：字典值
   - 描述：详细说明
   - 排序：显示顺序
5. 保存字典项

##### 编辑字典项
1. 在字典列表中找到目标项
2. 点击"编辑"按钮
3. 修改字典信息
4. 保存更改

##### 删除字典项
1. 选择要删除的字典项
2. 点击"删除"按钮
3. 确认删除操作

##### 字典项排序
- 通过"排序"字段控制显示顺序
- 数字越小排序越靠前
- 支持拖拽排序

#### 3. 字典使用

##### 表单下拉选项
```javascript
// 获取员工状态选项
const employeeStatusOptions = await dictionaryApi.getDictionaries({
  category: 'employee_status'
})
```

##### 数据验证
```javascript
// 验证员工状态
const validStatuses = ['active', 'leave', 'resigned', 'retired']
if (!validStatuses.includes(employee.status)) {
  throw new Error('无效的员工状态')
}
```

##### 报表统计
```javascript
// 按学历统计员工数量
const educationStats = await reportApi.getEmployeeStatsByEducation()
```

### 系统配置管理

系统配置用于管理系统的各种参数和设置，实现系统的灵活配置。

#### 1. 配置分类

系统支持7种配置分类：

##### 🏗️ 组织架构配置 (organization)
管理组织架构相关的配置。

**主要配置项**：
- `max_department_levels` - 最大部门层级数
- `allow_cross_department_position` - 是否允许跨部门职位
- `department_naming_rule` - 部门命名规则
- `organization_chart_style` - 组织架构图样式

**配置示例**：
```json
{
  "key": "max_department_levels",
  "value": "5",
  "category": "organization",
  "description": "最大部门层级数",
  "data_type": "integer",
  "is_required": true
}
```

##### 👔 职位配置 (position)
管理职位相关的配置。

**主要配置项**：
- `position_level_validation` - 是否启用职位级别验证
- `position_naming_rule` - 职位命名规则
- `position_approval_required` - 职位变更是否需要审批
- `position_template_enabled` - 是否启用职位模板

**配置示例**：
```json
{
  "key": "position_level_validation",
  "value": "true",
  "category": "position",
  "description": "是否启用职位级别验证",
  "data_type": "boolean",
  "is_required": true
}
```

##### 👤 员工配置 (employee)
管理员工相关的配置。

**主要配置项**：
- `auto_generate_employee_id` - 是否自动生成员工号
- `employee_id_prefix` - 员工号前缀
- `require_supervisor` - 是否必须设置直接上级
- `employee_photo_required` - 是否必须上传员工照片

**配置示例**：
```json
{
  "key": "auto_generate_employee_id",
  "value": "true",
  "category": "employee",
  "description": "是否自动生成员工号",
  "data_type": "boolean",
  "is_required": true
}
```

##### ⚙️ 工作流配置 (workflow)
管理工作流相关的配置。

**主要配置项**：
- `default_workflow_enabled` - 是否启用默认工作流
- `workflow_timeout` - 工作流超时时间
- `workflow_retry_count` - 工作流重试次数
- `workflow_notification_enabled` - 是否启用工作流通知

**配置示例**：
```json
{
  "key": "default_workflow_enabled",
  "value": "true",
  "category": "workflow",
  "description": "是否启用默认工作流",
  "data_type": "boolean",
  "is_required": false
}
```

##### 🔗 集成配置 (integration)
管理系统集成相关的配置。

**主要配置项**：
- `performance_system_url` - 绩效考核系统URL
- `finance_system_url` - 财务系统URL
- `oa_system_url` - OA系统URL
- `sync_interval` - 数据同步间隔

**配置示例**：
```json
{
  "key": "performance_system_url",
  "value": "http://localhost:8000",
  "category": "integration",
  "description": "绩效考核系统URL",
  "data_type": "string",
  "is_required": false
}
```

##### 🔒 安全配置 (security)
管理系统安全相关的配置。

**主要配置项**：
- `password_policy` - 密码策略
- `session_timeout` - 会话超时时间
- `login_attempt_limit` - 登录尝试次数限制
- `two_factor_auth_enabled` - 是否启用双因子认证

**配置示例**：
```json
{
  "key": "password_policy",
  "value": "{\"min_length\":8,\"require_uppercase\":true,\"require_lowercase\":true,\"require_numbers\":true,\"require_symbols\":true}",
  "category": "security",
  "description": "密码策略",
  "data_type": "json",
  "is_required": true
}
```

##### 📧 通知配置 (notification)
管理通知相关的配置。

**主要配置项**：
- `notification_enabled` - 是否启用通知功能
- `email_smtp_server` - 邮件SMTP服务器
- `sms_provider` - 短信服务提供商
- `wechat_corp_id` - 企业微信CorpID

**配置示例**：
```json
{
  "key": "notification_enabled",
  "value": "true",
  "category": "notification",
  "description": "是否启用通知功能",
  "data_type": "boolean",
  "is_required": false
}
```

#### 2. 配置管理

##### 创建配置
1. 进入"系统配置"页面
2. 点击"新增配置"
3. 填写配置信息：
   - 配置键：唯一标识
   - 配置值：配置内容
   - 配置分类：选择分类
   - 数据类型：选择数据类型
   - 描述：详细说明
   - 是否必需：是否必需配置
4. 保存配置

##### 编辑配置
1. 在配置列表中找到目标配置
2. 点击"编辑"按钮
3. 修改配置值
4. 保存更改

##### 删除配置
1. 选择要删除的配置
2. 点击"删除"按钮
3. 确认删除操作

##### 配置导入/导出
- 支持JSON格式的配置导入/导出
- 便于配置的备份和迁移
- 支持批量配置操作

#### 3. 配置使用

##### 获取配置值
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

##### 配置验证
```python
# 验证必需配置
required_configs = SystemConfig.objects.filter(is_required=True, is_active=True)
for config in required_configs:
    if not config.value:
        raise ValueError(f"必需配置 {config.key} 未设置")
```

##### 配置缓存
```python
# 使用缓存提高性能
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

### 职位模板管理

职位模板用于快速创建标准化的职位，提高职位管理效率。

#### 1. 模板分类

##### 高层管理模板
- **总经理**：公司最高管理者
- **副总经理**：协助总经理管理
- **总经理助理**：总经理的助手

##### 中层管理模板
- **部门经理**：部门负责人
- **部门副经理**：协助部门经理
- **部门助理**：部门经理的助手

##### 基层管理模板
- **主管**：团队负责人
- **副主管**：协助主管管理
- **组长**：小组负责人

##### 普通员工模板
- **高级员工**：资深员工
- **中级员工**：有经验的员工
- **初级员工**：新员工
- **实习生**：实习人员

#### 2. 模板管理

##### 创建模板
1. 进入"职位模板"页面
2. 点击"新增模板"
3. 填写模板信息：
   - 模板名称：职位名称
   - 管理层级：高层/中层/基层
   - 职位级别：1-13级
   - 默认要求：学历、经验要求
   - 默认职责：工作职责描述
4. 保存模板

##### 使用模板
1. 创建职位时选择模板
2. 系统自动填充模板信息
3. 根据需要调整具体内容
4. 保存职位

##### 模板维护
- 定期更新模板内容
- 根据公司发展调整模板
- 删除过时的模板

## 🎯 最佳实践

### 工作流规则设计

#### 1. 规则命名规范
- 使用描述性的名称
- 包含规则类型和用途
- 避免使用缩写和特殊字符

**好的命名示例**：
- `员工入职审批流程`
- `高级职位权限分配`
- `部门调整通知规则`

**不好的命名示例**：
- `rule1`
- `审批`
- `通知`

#### 2. 触发条件设计
- 条件要具体明确
- 避免过于复杂的条件
- 考虑边界情况

**示例**：
```json
{
  "type": "field",
  "field": "position_level",
  "operator": "gte",
  "value": "8"
}
```

#### 3. 动作配置设计
- 动作要可执行
- 考虑执行失败的情况
- 提供必要的参数

**示例**：
```json
{
  "type": "notification",
  "notificationType": "email",
  "recipients": ["hr@company.com"],
  "message": "新员工入职申请待处理",
  "retryCount": 3
}
```

### 数据字典管理

#### 1. 编码规范
- 使用英文小写字母
- 使用下划线分隔单词
- 保持简洁明了

**好的编码示例**：
- `employee_status`
- `education_level`
- `skill_level`

**不好的编码示例**：
- `EmployeeStatus`
- `education-level`
- `skillLevel`

#### 2. 分类管理
- 按业务领域分类
- 保持分类的一致性
- 避免分类过多

#### 3. 值管理
- 值要具有业务意义
- 避免重复和冲突
- 考虑国际化需求

### 系统配置管理

#### 1. 配置键命名
- 使用小写字母和下划线
- 包含配置分类前缀
- 保持命名的一致性

**示例**：
- `max_department_levels`
- `auto_generate_employee_id`
- `notification_enabled`

#### 2. 配置值设计
- 使用合适的数据类型
- 提供默认值
- 考虑配置的依赖关系

#### 3. 配置文档
- 为每个配置提供详细说明
- 说明配置的影响范围
- 提供配置示例

## ❓ 常见问题

### Q1: 工作流规则不执行怎么办？

**A**: 检查以下几个方面：
1. 确认规则已启用
2. 检查触发条件是否正确
3. 查看执行日志
4. 验证动作配置

### Q2: 数据字典如何添加新的分类？

**A**: 在字典管理页面：
1. 选择"自定义"分类
2. 创建新的字典项
3. 设置分类名称
4. 添加字典值

### Q3: 系统配置如何备份？

**A**: 使用配置导出功能：
1. 进入系统配置页面
2. 点击"导出配置"
3. 保存JSON文件
4. 定期备份配置文件

### Q4: 职位模板如何批量导入？

**A**: 使用模板导入功能：
1. 准备Excel模板文件
2. 进入职位模板页面
3. 点击"批量导入"
4. 上传模板文件
5. 确认导入结果

### Q5: 如何监控工作流执行情况？

**A**: 查看执行日志：
1. 进入工作流规则页面
2. 点击"执行日志"
3. 查看执行状态
4. 分析执行结果

## 🆘 技术支持

### 联系方式
- 技术支持邮箱：support@company.com
- 技术文档：https://docs.company.com
- 问题反馈：https://github.com/seajack/Q/issues

### 版本信息
- 当前版本：v1.0.0
- 最后更新：2024-01-01
- 兼容性：Python 3.11+, Node.js 18+

### 更新日志
- v1.0.0：初始版本发布
- 支持工作流规则管理
- 支持数据字典管理
- 支持系统配置管理
- 支持职位模板管理

---

**感谢使用组织架构中台系统！如有任何问题，请随时联系技术支持团队。**
