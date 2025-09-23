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
                                  on_delete=models.CASCADE, related_name='positions')
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
        ordering = ['department', '-level', 'code']  # 按职位级别从高到低排序

    def __str__(self):
        return f"{self.department.name} - {self.name}"
    
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
