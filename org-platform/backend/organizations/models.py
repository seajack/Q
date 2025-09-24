from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Department(models.Model):
    """部门模型"""
    name = models.CharField('部门名称', max_length=100)
    code = models.CharField('部门编码', max_length=50, unique=True)
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
    
    name = models.CharField('职位名称', max_length=100)
    code = models.CharField('职位编码', max_length=50, unique=True)
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
    
    user = models.OneToOneField(User, verbose_name='用户账号', 
                               on_delete=models.CASCADE, related_name='employee')
    employee_id = models.CharField('员工号', max_length=20, unique=True,
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
    RULE_TYPE_CHOICES = [
        ('approval', '审批流程'),
        ('notification', '通知规则'),
        ('data_sync', '数据同步'),
        ('permission', '权限控制'),
    ]
    
    name = models.CharField('规则名称', max_length=100)
    rule_type = models.CharField('规则类型', max_length=20, choices=RULE_TYPE_CHOICES)
    trigger_conditions = models.JSONField('触发条件', default=dict)
    action_config = models.JSONField('动作配置', default=dict)
    is_active = models.BooleanField('是否启用', default=True)
    priority = models.PositiveIntegerField('优先级', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '工作流规则'
        verbose_name_plural = '工作流规则'
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.get_rule_type_display()} - {self.name}"