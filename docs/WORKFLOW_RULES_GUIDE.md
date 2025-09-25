# 工作流规则配置详细指南

## 📋 目录

- [工作流规则概述](#工作流规则概述)
- [触发条件详解](#触发条件详解)
- [动作配置详解](#动作配置详解)
- [可视化配置指南](#可视化配置指南)
- [实际应用场景](#实际应用场景)
- [高级配置技巧](#高级配置技巧)
- [故障排除](#故障排除)

## 🎯 工作流规则概述

工作流规则是组织架构中台系统的核心功能，用于实现业务流程的自动化处理。通过配置工作流规则，可以实现：

- **自动化审批流程**：减少人工干预，提高审批效率
- **智能通知推送**：及时通知相关人员，确保信息传递
- **数据自动同步**：保持各系统间数据的一致性
- **权限自动管理**：根据业务规则自动分配和回收权限

### 规则组成

每个工作流规则由以下部分组成：

1. **基本信息**：规则名称、类型、优先级、描述
2. **触发条件**：定义规则何时被触发
3. **执行动作**：定义规则触发后执行的操作
4. **执行设置**：超时时间、重试次数、执行顺序等

## 🔧 触发条件详解

### 1. 事件触发 (Event Trigger)

事件触发是最常用的触发方式，当系统中发生特定事件时自动执行规则。

#### 支持的事件类型

##### 员工相关事件
- `employee_created` - 员工创建
- `employee_updated` - 员工信息更新
- `employee_resigned` - 员工离职
- `employee_transferred` - 员工调岗
- `employee_promoted` - 员工晋升

##### 部门相关事件
- `department_created` - 部门创建
- `department_updated` - 部门信息更新
- `department_deleted` - 部门删除
- `department_merged` - 部门合并

##### 职位相关事件
- `position_created` - 职位创建
- `position_updated` - 职位信息更新
- `position_deleted` - 职位删除
- `position_assigned` - 职位分配

#### 配置示例

**员工入职事件**：
```json
{
  "type": "event",
  "event": "employee_created",
  "conditions": {
    "position_level": ">=": 8
  }
}
```

**部门调整事件**：
```json
{
  "type": "event",
  "event": "department_updated",
  "conditions": {
    "department_type": "in": ["management", "business"]
  }
}
```

### 2. 字段条件 (Field Condition)

基于数据字段的值进行条件判断。

#### 支持的字段

##### 员工字段
- `position_level` - 职位级别
- `department_type` - 部门类型
- `employee_status` - 员工状态
- `education_level` - 学历层次
- `join_date` - 入职时间
- `salary_level` - 薪资级别

##### 部门字段
- `department_level` - 部门级别
- `department_type` - 部门类型
- `parent_department` - 上级部门
- `department_size` - 部门规模

##### 职位字段
- `position_level` - 职位级别
- `management_level` - 管理层级
- `position_type` - 职位类型
- `is_management` - 是否管理职位

#### 比较操作符

- `eq` - 等于
- `ne` - 不等于
- `gt` - 大于
- `gte` - 大于等于
- `lt` - 小于
- `lte` - 小于等于
- `in` - 包含
- `nin` - 不包含
- `like` - 模糊匹配
- `regex` - 正则表达式

#### 配置示例

**高级职位条件**：
```json
{
  "type": "field",
  "field": "position_level",
  "operator": "gte",
  "value": "8"
}
```

**特定部门条件**：
```json
{
  "type": "field",
  "field": "department_type",
  "operator": "in",
  "value": ["management", "business"]
}
```

**薪资级别条件**：
```json
{
  "type": "field",
  "field": "salary_level",
  "operator": "gte",
  "value": "5"
}
```

### 3. 时间条件 (Time Condition)

基于时间进行条件判断。

#### 时间类型

##### 工作时间条件
- `work_time` - 工作时间（9:00-18:00）
- `non_work_time` - 非工作时间
- `weekday` - 工作日
- `weekend` - 周末
- `holiday` - 节假日

##### 特定时间条件
- `specific_time` - 特定时间点
- `time_range` - 时间范围
- `recurring_time` - 重复时间

#### 配置示例

**工作时间条件**：
```json
{
  "type": "time",
  "timeType": "work_time",
  "startTime": "09:00",
  "endTime": "18:00"
}
```

**特定时间条件**：
```json
{
  "type": "time",
  "timeType": "specific_time",
  "specificTime": "14:30"
}
```

### 4. 用户条件 (User Condition)

基于用户属性进行条件判断。

#### 用户属性

- `role` - 用户角色
- `department` - 用户部门
- `position_level` - 职位级别
- `permissions` - 用户权限
- `login_time` - 登录时间
- `last_activity` - 最后活动时间

#### 配置示例

**管理员条件**：
```json
{
  "type": "user",
  "role": "admin",
  "department": "hr"
}
```

**高级职位用户条件**：
```json
{
  "type": "user",
  "position_level": "gte:8",
  "permissions": "in:['management_access']"
}
```

### 5. 部门条件 (Department Condition)

基于部门属性进行条件判断。

#### 部门属性

- `department_type` - 部门类型
- `department_level` - 部门级别
- `parent_department` - 上级部门
- `department_size` - 部门规模
- `department_status` - 部门状态

#### 配置示例

**管理部门条件**：
```json
{
  "type": "department",
  "departmentType": "management",
  "departmentLevel": "gte:2"
}
```

## ⚡ 动作配置详解

### 1. 通知动作 (Notification Action)

发送各种类型的通知。

#### 通知类型

##### 邮件通知
```json
{
  "type": "notification",
  "notificationType": "email",
  "recipients": ["hr@company.com", "manager@company.com"],
  "subject": "新员工入职通知",
  "template": "new_employee_welcome",
  "attachments": ["employee_info.pdf"]
}
```

##### 系统通知
```json
{
  "type": "notification",
  "notificationType": "system",
  "recipients": ["direct_supervisor", "hr_manager"],
  "message": "新员工入职申请待处理",
  "priority": "high",
  "expireTime": "24h"
}
```

##### 短信通知
```json
{
  "type": "notification",
  "notificationType": "sms",
  "recipients": ["+8613800138000"],
  "message": "您有新的审批任务待处理",
  "template": "approval_reminder"
}
```

##### 微信通知
```json
{
  "type": "notification",
  "notificationType": "wechat",
  "recipients": ["user123"],
  "message": "新员工入职通知",
  "template": "workflow_notification"
}
```

#### 接收人配置

##### 固定接收人
```json
{
  "recipients": ["hr@company.com", "manager@company.com"]
}
```

##### 动态接收人
```json
{
  "recipients": ["direct_supervisor", "hr_manager", "department_manager"]
}
```

##### 条件接收人
```json
{
  "recipients": {
    "condition": "position_level >= 8",
    "users": ["general_manager", "hr_director"]
  }
}
```

### 2. 审批动作 (Approval Action)

创建多级审批流程。

#### 审批流程配置

##### 简单审批流程
```json
{
  "type": "approval",
  "approvalFlow": [
    {
      "step": 1,
      "approver": "direct_supervisor",
      "required": true,
      "timeout": 24
    },
    {
      "step": 2,
      "approver": "hr_manager",
      "required": true,
      "timeout": 48
    }
  ]
}
```

##### 复杂审批流程
```json
{
  "type": "approval",
  "approvalFlow": [
    {
      "step": 1,
      "approver": "direct_supervisor",
      "required": true,
      "timeout": 24,
      "conditions": {
        "position_level": "<": 8
      }
    },
    {
      "step": 2,
      "approver": "department_manager",
      "required": true,
      "timeout": 48,
      "conditions": {
        "position_level": ">=": 8
      }
    },
    {
      "step": 3,
      "approver": "general_manager",
      "required": false,
      "timeout": 72,
      "conditions": {
        "position_level": ">=": 10
      }
    }
  ]
}
```

#### 审批人类型

- `direct_supervisor` - 直接上级
- `department_manager` - 部门经理
- `hr_manager` - HR经理
- `general_manager` - 总经理
- `specific_user` - 指定用户
- `role_based` - 基于角色

### 3. 数据同步动作 (Sync Action)

与其他系统进行数据同步。

#### 同步目标

##### 绩效考核系统
```json
{
  "type": "sync",
  "syncTarget": "performance_system",
  "syncFields": ["basic_info", "organization", "position"],
  "syncMethod": "api",
  "endpoint": "/api/employees/sync",
  "retryCount": 3,
  "timeout": 30
}
```

##### 财务系统
```json
{
  "type": "sync",
  "syncTarget": "finance_system",
  "syncFields": ["basic_info", "salary_info"],
  "syncMethod": "database",
  "connection": "finance_db",
  "table": "employees"
}
```

##### OA系统
```json
{
  "type": "sync",
  "syncTarget": "oa_system",
  "syncFields": ["basic_info", "organization"],
  "syncMethod": "file",
  "fileFormat": "csv",
  "filePath": "/sync/employees.csv"
}
```

#### 同步字段

- `basic_info` - 基本信息
- `organization` - 组织关系
- `position` - 职位信息
- `contact` - 联系方式
- `salary_info` - 薪资信息
- `permissions` - 权限信息

### 4. 权限变更动作 (Permission Action)

自动管理用户权限。

#### 权限类型

##### 系统权限
```json
{
  "type": "permission",
  "permissionType": "system",
  "permissionAction": "grant",
  "permissions": ["management_access", "report_access"],
  "scope": "department",
  "conditions": {
    "position_level": ">=": 8
  }
}
```

##### 数据权限
```json
{
  "type": "permission",
  "permissionType": "data",
  "permissionAction": "grant",
  "permissions": ["employee_data_access", "salary_data_access"],
  "scope": "department",
  "conditions": {
    "department_type": "in": ["hr", "finance"]
  }
}
```

##### 功能权限
```json
{
  "type": "permission",
  "permissionType": "function",
  "permissionAction": "grant",
  "permissions": ["approval_access", "report_generation"],
  "scope": "role",
  "conditions": {
    "role": "in": ["manager", "hr"]
  }
}
```

#### 权限操作

- `grant` - 授予权限
- `revoke` - 撤销权限
- `modify` - 修改权限
- `transfer` - 转移权限

### 5. 自动执行动作 (Auto Execute Action)

执行自动化任务。

#### 执行类型

##### 自动创建账号
```json
{
  "type": "auto_execute",
  "executeType": "create_account",
  "executeParams": {
    "username": "{{employee.employee_id}}",
    "email": "{{employee.email}}",
    "role": "employee",
    "permissions": ["basic_access"]
  }
}
```

##### 自动分配权限
```json
{
  "type": "auto_execute",
  "executeType": "assign_permission",
  "executeParams": {
    "user": "{{employee.user_id}}",
    "permissions": ["employee_access", "department_access"],
    "scope": "department"
  }
}
```

##### 自动发送邮件
```json
{
  "type": "auto_execute",
  "executeType": "send_email",
  "executeParams": {
    "template": "welcome_email",
    "recipients": ["{{employee.email}}"],
    "variables": {
      "name": "{{employee.name}}",
      "department": "{{employee.department}}"
    }
  }
}
```

## 🎨 可视化配置指南

### 1. 触发条件配置

#### 事件触发配置
1. 选择"事件触发"类型
2. 从下拉列表中选择事件类型
3. 设置事件参数（如需要）
4. 配置触发时机

#### 字段条件配置
1. 选择"字段条件"类型
2. 选择要比较的字段
3. 选择比较操作符
4. 输入比较值

#### 时间条件配置
1. 选择"时间条件"类型
2. 选择时间类型
3. 设置具体时间（如需要）
4. 配置时间范围

### 2. 动作配置

#### 通知动作配置
1. 选择"发送通知"类型
2. 选择通知类型（邮件、系统、短信、微信）
3. 设置接收人
4. 编写通知内容

#### 审批动作配置
1. 选择"创建审批"类型
2. 配置审批流程
3. 设置审批时限
4. 定义必需审批人

#### 同步动作配置
1. 选择"数据同步"类型
2. 选择同步目标系统
3. 选择同步字段
4. 配置同步方式

## 🏢 实际应用场景

### 1. 员工入职流程

#### 场景描述
新员工入职时，需要自动触发一系列流程：
1. 发送入职通知给HR和直接上级
2. 创建审批流程
3. 自动创建用户账号
4. 分配基本权限
5. 同步数据到其他系统

#### 配置示例

**触发条件**：
```json
{
  "type": "event",
  "event": "employee_created"
}
```

**执行动作**：
```json
[
  {
    "type": "notification",
    "notificationType": "email",
    "recipients": ["hr@company.com", "direct_supervisor"],
    "template": "new_employee_welcome"
  },
  {
    "type": "approval",
    "approvalFlow": [
      {"step": 1, "approver": "direct_supervisor", "required": true},
      {"step": 2, "approver": "hr_manager", "required": true}
    ]
  },
  {
    "type": "auto_execute",
    "executeType": "create_account",
    "executeParams": {
      "username": "{{employee.employee_id}}",
      "email": "{{employee.email}}"
    }
  },
  {
    "type": "sync",
    "syncTarget": "performance_system",
    "syncFields": ["basic_info", "organization"]
  }
]
```

### 2. 高级职位审批流程

#### 场景描述
当创建或调整高级职位（级别>=8）时，需要特殊的审批流程：
1. 部门经理审批
2. HR总监审批
3. 总经理审批（可选）
4. 权限自动分配

#### 配置示例

**触发条件**：
```json
{
  "type": "field",
  "field": "position_level",
  "operator": "gte",
  "value": "8"
}
```

**执行动作**：
```json
[
  {
    "type": "approval",
    "approvalFlow": [
      {"step": 1, "approver": "department_manager", "required": true, "timeout": 24},
      {"step": 2, "approver": "hr_director", "required": true, "timeout": 48},
      {"step": 3, "approver": "general_manager", "required": false, "timeout": 72}
    ]
  },
  {
    "type": "permission",
    "permissionType": "system",
    "permissionAction": "grant",
    "permissions": ["management_access", "report_access"]
  }
]
```

### 3. 部门调整通知流程

#### 场景描述
当部门发生调整时，需要通知相关人员：
1. 部门成员
2. 相关部门经理
3. HR部门
4. 上级部门

#### 配置示例

**触发条件**：
```json
{
  "type": "event",
  "event": "department_updated"
}
```

**执行动作**：
```json
[
  {
    "type": "notification",
    "notificationType": "system",
    "recipients": ["department_members", "department_manager"],
    "message": "部门信息已更新，请查看最新信息"
  },
  {
    "type": "notification",
    "notificationType": "email",
    "recipients": ["hr@company.com"],
    "template": "department_change_notification"
  }
]
```

## 🔧 高级配置技巧

### 1. 条件组合

#### 多条件组合
```json
{
  "type": "combined",
  "operator": "AND",
  "conditions": [
    {
      "type": "field",
      "field": "position_level",
      "operator": "gte",
      "value": "8"
    },
    {
      "type": "field",
      "field": "department_type",
      "operator": "in",
      "value": ["management", "business"]
    }
  ]
}
```

#### 条件嵌套
```json
{
  "type": "combined",
  "operator": "OR",
  "conditions": [
    {
      "type": "field",
      "field": "position_level",
      "operator": "gte",
      "value": "10"
    },
    {
      "type": "combined",
      "operator": "AND",
      "conditions": [
        {
          "type": "field",
          "field": "position_level",
          "operator": "gte",
          "value": "8"
        },
        {
          "type": "field",
          "field": "department_type",
          "operator": "eq",
          "value": "management"
        }
      ]
    }
  ]
}
```

### 2. 动作链式执行

#### 顺序执行
```json
[
  {
    "type": "notification",
    "notificationType": "system",
    "message": "流程开始执行"
  },
  {
    "type": "approval",
    "approvalFlow": [...]
  },
  {
    "type": "sync",
    "syncTarget": "performance_system"
  },
  {
    "type": "notification",
    "notificationType": "email",
    "message": "流程执行完成"
  }
]
```

#### 条件执行
```json
[
  {
    "type": "notification",
    "notificationType": "system",
    "message": "流程开始执行"
  },
  {
    "type": "approval",
    "approvalFlow": [...],
    "onSuccess": [
      {
        "type": "sync",
        "syncTarget": "performance_system"
      }
    ],
    "onFailure": [
      {
        "type": "notification",
        "notificationType": "email",
        "message": "审批失败，请重新处理"
      }
    ]
  }
]
```

### 3. 变量使用

#### 系统变量
- `{{employee.name}}` - 员工姓名
- `{{employee.email}}` - 员工邮箱
- `{{employee.department}}` - 员工部门
- `{{employee.position}}` - 员工职位
- `{{employee.supervisor}}` - 直接上级

#### 动态变量
- `{{current_user}}` - 当前用户
- `{{current_time}}` - 当前时间
- `{{current_date}}` - 当前日期
- `{{system_version}}` - 系统版本

#### 变量使用示例
```json
{
  "type": "notification",
  "notificationType": "email",
  "recipients": ["{{employee.supervisor.email}}"],
  "subject": "{{employee.name}}的入职申请",
  "message": "您好，{{employee.name}}（{{employee.position}}）的入职申请已提交，请及时处理。"
}
```

## 🔍 故障排除

### 1. 规则不执行

#### 检查步骤
1. 确认规则已启用
2. 检查触发条件是否正确
3. 查看执行日志
4. 验证动作配置

#### 常见问题
- 触发条件过于严格
- 动作配置错误
- 系统权限不足
- 网络连接问题

### 2. 通知发送失败

#### 检查步骤
1. 检查通知配置
2. 验证接收人信息
3. 检查网络连接
4. 查看错误日志

#### 常见问题
- 邮箱地址错误
- SMTP配置问题
- 模板不存在
- 权限不足

### 3. 审批流程卡住

#### 检查步骤
1. 检查审批人配置
2. 验证审批人权限
3. 查看审批日志
4. 检查超时设置

#### 常见问题
- 审批人不存在
- 审批人权限不足
- 超时时间过短
- 审批流程配置错误

### 4. 数据同步失败

#### 检查步骤
1. 检查目标系统连接
2. 验证同步字段
3. 查看同步日志
4. 检查数据格式

#### 常见问题
- 目标系统不可用
- 字段映射错误
- 数据格式不匹配
- 权限不足

## 📊 监控和统计

### 1. 执行统计
- 规则执行次数
- 执行成功率
- 平均执行时间
- 失败原因分析

### 2. 性能监控
- 系统资源使用
- 响应时间
- 并发处理能力
- 错误率统计

### 3. 业务分析
- 流程效率分析
- 审批时间统计
- 通知送达率
- 用户满意度

---

**通过本指南，您应该能够熟练配置和使用工作流规则系统。如有任何问题，请参考常见问题部分或联系技术支持。**
