# 权限管理系统使用指南

## 系统概述

权限管理系统是一个完整的企业级权限控制解决方案，提供了细粒度的权限控制、角色管理、数据权限控制、字段权限和数据脱敏等功能。

## 核心功能

### 1. 权限管理
- **菜单权限**: 控制用户可以看到哪些菜单
- **按钮权限**: 控制用户可以使用哪些操作按钮
- **API权限**: 控制用户可以访问哪些API接口
- **数据权限**: 控制用户可以访问哪些数据
- **字段权限**: 控制用户可以看到哪些字段

### 2. 角色管理
- **角色定义**: 创建和管理不同的角色
- **权限分配**: 为角色分配相应的权限
- **权限继承**: 支持角色之间的权限继承
- **用户分配**: 将用户分配到相应的角色

### 3. 数据权限控制
- **全部数据权限**: 可以访问所有数据
- **部门数据权限**: 只能访问本部门数据
- **本部门及下级数据权限**: 可以访问本部门及下级部门数据
- **个人数据权限**: 只能访问自己的数据
- **自定义数据权限**: 可以自定义数据访问范围

### 4. 字段权限控制
- **可见权限**: 字段对用户可见
- **只读权限**: 字段对用户只读
- **隐藏权限**: 字段对用户隐藏
- **脱敏权限**: 字段对用户进行脱敏处理

### 5. 数据脱敏
- **手机号脱敏**: 138****1234
- **邮箱脱敏**: us**@example.com
- **身份证脱敏**: 110101********1234
- **自定义脱敏**: 支持自定义脱敏规则

## 系统架构

### 数据模型
- **Permission**: 权限模型
- **Role**: 角色模型
- **UserRole**: 用户角色关联
- **RolePermission**: 角色权限关联
- **DataPermission**: 数据权限模型
- **FieldPermission**: 字段权限模型
- **PermissionLog**: 权限操作日志

### 服务层
- **PermissionService**: 权限管理服务
- **DataPermissionService**: 数据权限服务
- **FieldPermissionService**: 字段权限服务

### 中间件
- **PermissionMiddleware**: 权限中间件
- **权限装饰器**: 用于API权限控制

## 使用指南

### 1. 访问权限管理

1. 启动系统后，访问 `http://localhost:3000`
2. 点击导航栏中的"权限管理"菜单
3. 进入权限管理主页面

### 2. 权限管理

#### 创建权限
1. 点击"权限管理" -> "权限管理"
2. 点击"添加权限"按钮
3. 填写权限信息：
   - 权限名称：如"用户管理"
   - 权限编码：如"user_management"
   - 权限类型：选择菜单、按钮、API等
   - 父权限：选择上级权限（可选）
   - 资源标识：如"/api/users"
   - 操作类型：如"GET,POST,PUT,DELETE"
4. 点击"保存"

#### 权限树形结构
- 权限支持树形结构，可以设置父子关系
- 子权限会自动继承父权限的某些属性
- 支持多级权限嵌套

### 3. 角色管理

#### 创建角色
1. 点击"权限管理" -> "角色管理"
2. 点击"添加角色"按钮
3. 填写角色信息：
   - 角色名称：如"系统管理员"
   - 角色编码：如"system_admin"
   - 角色类型：系统角色、自定义角色、部门角色
   - 数据权限范围：选择数据访问范围
   - 父角色：选择上级角色（可选）
4. 点击"保存"

#### 分配权限给角色
1. 在角色列表中，点击"权限"按钮
2. 在权限树中选择要分配的权限
3. 点击"保存"

#### 分配用户给角色
1. 在角色列表中，点击"用户"按钮
2. 在用户列表中选择要分配的用户
3. 点击"保存"

### 4. 数据权限管理

#### 创建数据权限
1. 点击"权限管理" -> "数据权限"
2. 点击"添加数据权限"按钮
3. 填写数据权限信息：
   - 权限名称：如"部门数据权限"
   - 权限类型：读取、写入、删除、导出
   - 数据范围：全部数据、本部门数据、个人数据等
   - 资源类型：如"employee"、"department"
   - 字段权限配置：设置字段的访问权限
   - 数据脱敏配置：设置数据脱敏规则
4. 点击"保存"

#### 字段权限配置
- 可以为每个字段设置不同的权限
- 支持可见、只读、隐藏、脱敏等权限类型
- 支持自定义脱敏规则

#### 数据脱敏配置
- 手机号脱敏：显示前3位和后4位
- 邮箱脱敏：显示用户名前2位
- 身份证脱敏：显示前6位和后4位
- 自定义脱敏：支持自定义脱敏规则

### 5. 权限仪表板

#### 查看权限统计
1. 点击"权限管理" -> "权限仪表板"
2. 查看权限统计信息：
   - 总权限数、启用权限数、禁用权限数
   - 总角色数、启用角色数、禁用角色数
   - 总用户数、有角色用户数、无角色用户数
   - 操作日志数量

#### 权限检查工具
1. 在权限仪表板中，找到"权限检查工具"
2. 选择要检查的用户
3. 输入权限编码
4. 点击"检查权限"
5. 查看检查结果

### 6. 权限中间件使用

#### API权限控制
```python
from organizations.permission_services import require_permission

@require_permission('user_management')
def user_list(request):
    # 只有拥有user_management权限的用户才能访问
    pass
```

#### 数据权限控制
```python
from organizations.permission_services import require_data_permission

@require_data_permission('employee')
def employee_list(request):
    # 只有拥有employee数据权限的用户才能访问
    pass
```

### 7. 权限服务使用

#### 检查用户权限
```python
from organizations.permission_services import PermissionService

# 创建权限服务实例
permission_service = PermissionService(user)

# 检查单个权限
if permission_service.has_permission('user_management'):
    # 用户拥有user_management权限
    pass

# 检查多个权限（任意一个）
if permission_service.has_any_permission(['user_management', 'department_management']):
    # 用户拥有其中任意一个权限
    pass

# 检查多个权限（全部）
if permission_service.has_all_permissions(['user_management', 'department_management']):
    # 用户拥有全部权限
    pass
```

#### 数据权限控制
```python
from organizations.permission_services import DataPermissionService

# 创建数据权限服务实例
data_permission_service = DataPermissionService(user)

# 获取数据权限范围
scope = data_permission_service.get_data_scope('employee')

# 检查是否可以访问特定数据
if data_permission_service.can_access_data('employee', resource_id='123'):
    # 用户可以访问该数据
    pass

# 获取可访问的部门列表
departments = data_permission_service.get_accessible_departments()

# 获取可访问的员工列表
employees = data_permission_service.get_accessible_employees()
```

#### 字段权限控制
```python
from organizations.permission_services import FieldPermissionService

# 创建字段权限服务实例
field_permission_service = FieldPermissionService(user)

# 检查字段是否可见
if field_permission_service.is_field_visible('employee', 'phone'):
    # 用户可以查看phone字段
    pass

# 检查字段是否可编辑
if field_permission_service.is_field_editable('employee', 'name'):
    # 用户可以编辑name字段
    pass

# 对字段值进行脱敏处理
masked_phone = field_permission_service.mask_field_value('employee', 'phone', '13812345678')
# 结果：138****5678
```

## 最佳实践

### 1. 权限设计原则
- **最小权限原则**: 用户只获得完成工作所需的最小权限
- **职责分离**: 不同角色承担不同的职责
- **权限继承**: 合理使用权限继承减少配置工作量
- **定期审查**: 定期审查和更新用户权限

### 2. 角色设计建议
- **系统角色**: 用于系统级管理，如超级管理员、系统管理员
- **业务角色**: 用于业务管理，如部门管理员、项目经理
- **功能角色**: 用于特定功能，如财务人员、HR人员
- **临时角色**: 用于临时任务，如项目成员、临时访问者

### 3. 数据权限设计
- **按部门隔离**: 不同部门的数据相互隔离
- **按级别控制**: 上级可以查看下级数据，下级不能查看上级数据
- **按时间控制**: 可以设置数据访问的时间范围
- **按状态控制**: 可以设置数据访问的状态条件

### 4. 字段权限设计
- **敏感信息脱敏**: 对手机号、邮箱、身份证等敏感信息进行脱敏
- **分级显示**: 不同角色看到不同级别的信息
- **动态权限**: 根据数据状态动态调整字段权限

### 5. 安全建议
- **定期审计**: 定期检查权限分配是否合理
- **权限回收**: 及时回收离职用户的权限
- **操作日志**: 记录所有权限操作，便于审计
- **权限测试**: 定期测试权限配置是否正确

## 故障排除

### 1. 权限不生效
- 检查用户是否分配了正确的角色
- 检查角色是否分配了正确的权限
- 检查权限是否启用
- 检查权限缓存是否过期

### 2. 数据权限问题
- 检查数据权限配置是否正确
- 检查用户的数据权限范围
- 检查数据权限是否启用
- 检查数据权限的继承关系

### 3. 字段权限问题
- 检查字段权限配置是否正确
- 检查脱敏规则是否正确
- 检查字段权限是否启用
- 检查脱敏配置是否完整

### 4. 性能问题
- 检查权限缓存是否启用
- 检查权限查询是否优化
- 检查权限检查频率
- 考虑使用权限缓存

## 扩展功能

### 1. 自定义权限类型
- 可以扩展新的权限类型
- 可以自定义权限验证逻辑
- 可以集成第三方权限系统

### 2. 权限审批流程
- 可以添加权限申请流程
- 可以设置权限审批规则
- 可以集成工作流引擎

### 3. 权限分析
- 可以分析权限使用情况
- 可以生成权限报告
- 可以优化权限配置

### 4. 多租户支持
- 可以支持多租户权限隔离
- 可以设置租户级权限
- 可以管理租户权限

## 总结

权限管理系统提供了完整的权限控制解决方案，包括权限管理、角色管理、数据权限控制、字段权限和数据脱敏等功能。通过合理配置和使用，可以实现细粒度的权限控制，保障系统安全。

系统支持权限继承、动态权限、权限缓存等高级功能，可以满足复杂的企业级权限管理需求。同时，系统提供了丰富的API和中间件，便于集成到现有系统中。
