from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid
from .tenant_models import Tenant

# 导入智能分析模型
from .intelligence_models import *


class Department(models.Model):
    """部门模型"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户', null=True, blank=True)
    name = models.CharField('部门名称', max_length=100)
    code = models.CharField('部门编码', max_length=50)
    parent = models.ForeignKey('self', verbose_name='上级部门', 
                              on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children')
    level = models.PositiveIntegerField('层级', default=1)
    sort_order = models.PositiveIntegerField('排序', default=0)
    description = models.TextField('描述', blank=True)
    manager = models.ForeignKey(User, verbose_name='负责人', 
                               on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='managed_departments')
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门'
        ordering = ['level', 'sort_order', 'code']

    def __str__(self):
        return self.name

    def get_full_path(self):
        """获取部门完整路径"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name

    def get_all_children(self):
        """获取所有子部门（递归）"""
        children = list(self.children.filter(is_active=True))
        for child in self.children.filter(is_active=True):
            children.extend(child.get_all_children())
        return children


class Position(models.Model):
    """职位模型"""
    # 管理层级选择
    MANAGEMENT_LEVEL_CHOICES = [
        ('senior', '高层'),
        ('middle', '中层'),
        ('junior', '基层'),
    ]
    
    # 职务级别选择（按优先级排序，数字越大级别越高）
    POSITION_LEVEL_CHOICES = [
        (13, '高层正职'),
        (12, '高层副职'),
        (11, '高层助理'),
        (9, '中层正职'),
        (8, '中层副职'),
        (7, '中层助理'),
        (4, '基层正职'),
        (3, '基层副职'),
        (2, '基层助理'),
        (1, '员工'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户', null=True, blank=True)
    name = models.CharField('职位名称', max_length=100)
    code = models.CharField('职位编码', max_length=50)
    department = models.ForeignKey(Department, verbose_name='所属部门', 
                                  on_delete=models.SET_NULL, related_name='positions', 
                                  null=True, blank=True)
    management_level = models.CharField('管理层级', max_length=20, choices=MANAGEMENT_LEVEL_CHOICES, default='junior')
    level = models.IntegerField('职位级别', choices=POSITION_LEVEL_CHOICES, default=1)
    description = models.TextField('职位描述', blank=True)
    requirements = models.TextField('任职要求', blank=True)
    responsibilities = models.TextField('岗位职责', blank=True)
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '职位'
        verbose_name_plural = '职位'
        ordering = ['-level', 'code']  # 按职位级别从高到低排序

    def __str__(self):
        dept_name = self.department.name if self.department else '无部门'
        return f"{dept_name} - {self.name}"
    
    def get_level_display_with_management(self):
        """获取包含管理层级的完整显示名称"""
        management_display = self.get_management_level_display()
        level_display = self.get_level_display()
        return f"{management_display} - {level_display}"


class Employee(models.Model):
    """员工模型"""
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
    ]
    
    STATUS_CHOICES = [
        ('active', '在职'),
        ('leave', '休假'),
        ('resigned', '离职'),
        ('retired', '退休'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='用户账号', 
                               on_delete=models.CASCADE, related_name='employee')
    employee_id = models.CharField('员工号', max_length=20,
                                  validators=[RegexValidator(r'^[A-Z0-9]+$', '员工号只能包含大写字母和数字')])
    name = models.CharField('姓名', max_length=50)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField('出生日期', null=True, blank=True)
    phone = models.CharField('手机号码', max_length=20, blank=True)
    email = models.EmailField('邮箱', blank=True)
    address = models.TextField('地址', blank=True)
    
    department = models.ForeignKey(Department, verbose_name='所属部门', 
                                  on_delete=models.CASCADE, related_name='employees')
    position = models.ForeignKey(Position, verbose_name='职位', 
                                on_delete=models.CASCADE, related_name='employees')
    supervisor = models.ForeignKey('self', verbose_name='直接上级', 
                                  on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='subordinates')
    
    hire_date = models.DateField('入职日期')
    status = models.CharField('在职状态', max_length=20, choices=STATUS_CHOICES, default='active')
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '员工'
        verbose_name_plural = '员工'
        ordering = ['department', 'position__level', 'employee_id']

    def __str__(self):
        return f"{self.name} ({self.employee_id})"

    def get_all_subordinates(self):
        """获取所有下属（递归）"""
        subordinates = list(self.subordinates.filter(status='active'))
        for subordinate in self.subordinates.filter(status='active'):
            subordinates.extend(subordinate.get_all_subordinates())
        return subordinates

    def get_position_level_display_name(self):
        """获取职位级别显示名称"""
        return self.position.get_level_display() if self.position else ''


class OrganizationStructure(models.Model):
    """组织架构快照模型（用于版本管理）"""
    name = models.CharField('快照名称', max_length=100)
    description = models.TextField('快照描述', blank=True)
    structure_data = models.JSONField('组织架构数据')
    is_current = models.BooleanField('是否当前版本', default=False)
    created_by = models.ForeignKey(User, verbose_name='创建者', 
                                  on_delete=models.CASCADE, related_name='created_structures')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '组织架构快照'
        verbose_name_plural = '组织架构快照'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            # 确保只有一个当前版本
            OrganizationStructure.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class SystemConfig(models.Model):
    """系统配置模型"""
    CATEGORY_CHOICES = [
        ('organization', '组织架构配置'),
        ('position', '职位配置'),
        ('employee', '员工配置'),
        ('workflow', '工作流配置'),
        ('integration', '集成配置'),
        ('security', '安全配置'),
        ('notification', '通知配置'),
    ]
    
    key = models.CharField('配置键', max_length=100, unique=True)
    value = models.TextField('配置值')
    category = models.CharField('配置分类', max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField('配置描述', blank=True)
    data_type = models.CharField('数据类型', max_length=20, default='string',
                                choices=[
                                    ('string', '字符串'),
                                    ('integer', '整数'),
                                    ('boolean', '布尔值'),
                                    ('json', 'JSON对象'),
                                    ('list', '列表'),
                                ])
    is_encrypted = models.BooleanField('是否加密', default=False)
    is_required = models.BooleanField('是否必需', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.key}"


class Dictionary(models.Model):
    """数据字典模型"""
    CATEGORY_CHOICES = [
        ('employee_status', '员工状态'),
        ('position_type', '职位类型'),
        ('department_type', '部门类型'),
        ('education_level', '学历层次'),
        ('skill_level', '技能等级'),
        ('language', '语言类型'),
        ('nationality', '国籍'),
        ('marital_status', '婚姻状况'),
        ('custom', '自定义'),
    ]
    
    category = models.CharField('字典分类', max_length=50, choices=CATEGORY_CHOICES)
    code = models.CharField('字典编码', max_length=50)
    name = models.CharField('字典名称', max_length=100)
    value = models.CharField('字典值', max_length=200, blank=True)
    description = models.TextField('描述', blank=True)
    sort_order = models.PositiveIntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    parent = models.ForeignKey('self', verbose_name='父级字典', 
                              on_delete=models.CASCADE, null=True, blank=True,
                              related_name='children')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '数据字典'
        verbose_name_plural = '数据字典'
        unique_together = ['category', 'code']
        ordering = ['category', 'sort_order', 'code']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"


class PositionTemplate(models.Model):
    """职位模板模型"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户', null=True, blank=True)
    name = models.CharField('模板名称', max_length=100)
    description = models.TextField('模板描述', blank=True)
    management_level = models.CharField('管理层级', max_length=20, 
                                       choices=Position.MANAGEMENT_LEVEL_CHOICES)
    level = models.IntegerField('职位级别', choices=Position.POSITION_LEVEL_CHOICES)
    default_requirements = models.TextField('默认任职要求', blank=True)
    default_responsibilities = models.TextField('默认岗位职责', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '职位模板'
        verbose_name_plural = '职位模板'
        ordering = ['-level', 'name']
    
    def __str__(self):
        return f"{self.get_management_level_display()} - {self.name}"


class WorkflowRule(models.Model):
    """工作流规则模型"""
    RULE_TYPES = [
        ('employee_management', '员工管理'),
        ('department_management', '部门管理'),
        ('position_management', '职位管理'),
        ('permission_management', '权限管理'),
        ('integration', '系统集成'),
        ('data_quality', '数据质量'),
        ('reporting', '报表生成'),
        ('notification', '通知提醒'),
        ('approval', '审批流程'),
        ('automation', '自动化'),
    ]

    STATUS_CHOICES = [
        ('active', '激活'),
        ('inactive', '停用'),
        ('draft', '草稿'),
        ('testing', '测试中'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('规则名称', max_length=100)
    code = models.CharField('规则编码', max_length=50, unique=True)
    description = models.TextField('规则描述', blank=True)
    rule_type = models.CharField('规则类型', max_length=50, choices=RULE_TYPES)
    
    # 触发条件
    trigger_conditions = models.JSONField('触发条件', default=dict)
    
    # 执行动作
    execution_actions = models.JSONField('执行动作', default=list)
    
    # 规则状态
    is_active = models.BooleanField('是否激活', default=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    priority = models.IntegerField('优先级', default=1, help_text='数字越小优先级越高')
    
    # 时间设置
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建者')
    
    # 执行统计
    execution_count = models.PositiveIntegerField('执行次数', default=0)
    last_executed = models.DateTimeField('最后执行时间', null=True, blank=True)
    success_count = models.PositiveIntegerField('成功次数', default=0)
    failure_count = models.PositiveIntegerField('失败次数', default=0)

    class Meta:
        verbose_name = '工作流规则'
        verbose_name_plural = '工作流规则'
        ordering = ['priority', 'created_at']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def execute(self, context=None):
        """执行工作流规则"""
        try:
            # 增加执行次数
            self.execution_count += 1
            self.last_executed = timezone.now()
            
            # 执行动作
            for action in self.execution_actions:
                self._execute_action(action, context or {})
            
            # 增加成功次数
            self.success_count += 1
            self.save(update_fields=['execution_count', 'last_executed', 'success_count'])
            
            return True
        except Exception as e:
            # 增加失败次数
            self.failure_count += 1
            self.save(update_fields=['failure_count'])
            raise e

    def _execute_action(self, action, context):
        """执行单个动作"""
        action_type = action.get('action')
        
        if action_type == 'start_workflow':
            # 启动工作流
            workflow_id = action.get('workflow_id')
            parameters = action.get('parameters', {})
            # 这里应该调用工作流引擎
            print(f"启动工作流: {workflow_id}, 参数: {parameters}")
            
        elif action_type == 'send_notification':
            # 发送通知
            template = action.get('template')
            recipients = action.get('recipients', [])
            # 这里应该调用通知服务
            print(f"发送通知: {template} 给 {recipients}")
            
        elif action_type == 'send_alert':
            # 发送告警
            template = action.get('template')
            recipients = action.get('recipients', [])
            print(f"发送告警: {template} 给 {recipients}")
            
        elif action_type == 'create_ticket':
            # 创建工单
            ticket_type = action.get('ticket_type')
            priority = action.get('priority', 'medium')
            print(f"创建工单: {ticket_type}, 优先级: {priority}")
            
        elif action_type == 'log_activity':
            # 记录活动日志
            message = action.get('message')
            print(f"记录日志: {message}")
            
        else:
            print(f"未知动作类型: {action_type}")

    def get_success_rate(self):
        """获取成功率"""
        if self.execution_count == 0:
            return 0
        return round((self.success_count / self.execution_count) * 100, 2)

    def is_triggered(self, event_data):
        """检查是否触发规则"""
        conditions = self.trigger_conditions
        
        # 检查事件类型
        if conditions.get('event_type') != event_data.get('event_type'):
            return False
            
        # 检查表名
        if conditions.get('table') != event_data.get('table'):
            return False
            
        # 检查操作类型
        if conditions.get('operation') != event_data.get('operation'):
            return False
            
        # 检查条件
        record_data = event_data.get('record', {})
        for condition in conditions.get('conditions', []):
            field = condition['field']
            operator = condition['operator']
            value = condition['value']
            
            field_value = self._get_nested_value(record_data, field)
            
            if not self._evaluate_condition(field_value, operator, value):
                return False
                
        return True

    def _get_nested_value(self, data, field_path):
        """获取嵌套字段值"""
        keys = field_path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    def _evaluate_condition(self, field_value, operator, expected_value):
        """评估条件"""
        if operator == 'equals':
            return field_value == expected_value
        elif operator == 'not_equals':
            return field_value != expected_value
        elif operator == 'gte':
            return field_value >= expected_value
        elif operator == 'lte':
            return field_value <= expected_value
        elif operator == 'gt':
            return field_value > expected_value
        elif operator == 'lt':
            return field_value < expected_value
        elif operator == 'contains':
            return expected_value in str(field_value)
        elif operator == 'is_null':
            return field_value is None
        elif operator == 'is_not_null':
            return field_value is not None
        elif operator == 'changed':
            return field_value != expected_value
        else:
            return False


class WorkflowRuleExecution(models.Model):
    """工作流执行记录"""
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '执行失败'),
        ('cancelled', '已取消'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(WorkflowRule, on_delete=models.CASCADE, verbose_name='工作流规则')
    status = models.CharField('执行状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 执行上下文
    context = models.JSONField('执行上下文', default=dict)
    trigger_data = models.JSONField('触发数据', default=dict)
    
    # 时间信息
    started_at = models.DateTimeField('开始时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    duration = models.DurationField('执行时长', null=True, blank=True)
    
    # 执行结果
    result = models.JSONField('执行结果', default=dict)
    error_message = models.TextField('错误信息', blank=True)
    
    # 执行者
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='执行者')

    class Meta:
        verbose_name = '工作流执行记录'
        verbose_name_plural = '工作流执行记录'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.rule.name} - {self.get_status_display()}"

    def complete(self, result=None, error_message=None):
        """完成执行"""
        self.completed_at = timezone.now()
        self.duration = self.completed_at - self.started_at
        
        if error_message:
            self.status = 'failed'
            self.error_message = error_message
        else:
            self.status = 'completed'
            self.result = result or {}
            
        self.save()

    def cancel(self, reason=None):
        """取消执行"""
        self.status = 'cancelled'
        if reason:
            self.error_message = reason
        self.save()


class WorkflowTemplate(models.Model):
    """工作流模板"""
    CATEGORY_CHOICES = [
        ('hr', '人力资源'),
        ('finance', '财务管理'),
        ('it', '信息技术'),
        ('operations', '运营管理'),
        ('compliance', '合规管理'),
        ('general', '通用流程'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('模板名称', max_length=100)
    code = models.CharField('模板编码', max_length=50, unique=True)
    description = models.TextField('模板描述', blank=True)
    category = models.CharField('模板分类', max_length=20, choices=CATEGORY_CHOICES)
    
    # 模板内容
    workflow_definition = models.JSONField('工作流定义', default=dict)
    form_schema = models.JSONField('表单结构', default=dict)
    
    # 模板状态
    is_active = models.BooleanField('是否激活', default=True)
    is_public = models.BooleanField('是否公开', default=False)
    
    # 使用统计
    usage_count = models.PositiveIntegerField('使用次数', default=0)
    
    # 时间信息
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建者')

    class Meta:
        verbose_name = '工作流模板'
        verbose_name_plural = '工作流模板'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])