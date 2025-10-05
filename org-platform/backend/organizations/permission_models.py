"""
权限管理数据模型
"""

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
import uuid


class Permission(models.Model):
    """权限模型"""
    PERMISSION_TYPE_CHOICES = [
        ('menu', '菜单权限'),
        ('button', '按钮权限'),
        ('api', 'API权限'),
        ('data', '数据权限'),
        ('field', '字段权限'),
    ]
    
    STATUS_CHOICES = [
        ('active', '激活'),
        ('inactive', '未激活'),
        ('deprecated', '已废弃'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('权限名称', max_length=100)
    code = models.CharField('权限编码', max_length=100, unique=True)
    permission_type = models.CharField('权限类型', max_length=20, choices=PERMISSION_TYPE_CHOICES)
    description = models.TextField('描述', blank=True)
    resource = models.CharField('资源', max_length=200, blank=True)
    action = models.CharField('操作', max_length=50, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    is_system = models.BooleanField('系统权限', default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='父权限', related_name='children')
    sort_order = models.PositiveIntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '权限'
        verbose_name_plural = '权限'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Role(models.Model):
    """角色模型"""
    STATUS_CHOICES = [
        ('active', '激活'),
        ('inactive', '未激活'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('角色名称', max_length=100)
    code = models.CharField('角色编码', max_length=100, unique=True)
    description = models.TextField('描述', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    is_system = models.BooleanField('系统角色', default=False)
    permissions = models.ManyToManyField(Permission, verbose_name='权限', blank=True, through='RolePermission')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """角色权限关联模型"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='角色')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name='权限')
    granted = models.BooleanField('是否授权', default=True)
    granted_at = models.DateTimeField('授权时间', auto_now_add=True)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='授权人')

    class Meta:
        verbose_name = '角色权限'
        verbose_name_plural = '角色权限'
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class UserRole(models.Model):
    """用户角色关联模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='角色', related_name='user_roles')
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分配人', related_name='assigned_roles')
    is_active = models.BooleanField('是否激活', default=True)

    class Meta:
        verbose_name = '用户角色'
        verbose_name_plural = '用户角色'
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


class PermissionLog(models.Model):
    """权限日志模型"""
    ACTION_CHOICES = [
        ('grant', '授权'),
        ('revoke', '撤销'),
        ('assign', '分配'),
        ('remove', '移除'),
        ('login', '登录'),
        ('logout', '登出'),
        ('access', '访问'),
        ('deny', '拒绝'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', related_name='permission_logs')
    action = models.CharField('操作', max_length=20, choices=ACTION_CHOICES, default='access')
    resource = models.CharField('资源', max_length=200, blank=True)
    description = models.TextField('描述', blank=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('用户代理', blank=True)
    result = models.CharField('结果', max_length=20, choices=[
        ('success', '成功'),
        ('failed', '失败'),
        ('denied', '拒绝'),
    ], default='success')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '权限日志'
        verbose_name_plural = '权限日志'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()}"


class DataPermission(models.Model):
    """数据权限模型"""
    PERMISSION_TYPE_CHOICES = [
        ('all', '全部数据'),
        ('department', '部门数据'),
        ('self', '个人数据'),
        ('custom', '自定义'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', related_name='data_permissions', null=True, blank=True)
    permission_type = models.CharField('权限类型', max_length=20, choices=PERMISSION_TYPE_CHOICES)
    resource = models.CharField('资源', max_length=200, default='')
    conditions = models.JSONField('条件', default=dict, blank=True)
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '数据权限'
        verbose_name_plural = '数据权限'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_permission_type_display()}"


class RoleDataPermission(models.Model):
    """角色数据权限模型"""
    role = models.ForeignKey('Role', on_delete=models.CASCADE, verbose_name='角色', related_name='role_data_permissions')
    data_permission = models.ForeignKey(DataPermission, on_delete=models.CASCADE, verbose_name='数据权限', related_name='role_data_permissions')
    is_granted = models.BooleanField('是否授权', default=True)
    granted_at = models.DateTimeField('授权时间', auto_now_add=True)
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='授权者')

    class Meta:
        verbose_name = '角色数据权限'
        verbose_name_plural = '角色数据权限'
        unique_together = ('role', 'data_permission')

    def __str__(self):
        return f"{self.role.name} - {self.data_permission.resource}"


class FieldPermission(models.Model):
    """字段权限模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', related_name='field_permissions')
    resource_type = models.CharField('资源类型', max_length=100)
    field_name = models.CharField('字段名', max_length=100)
    permission_type = models.CharField('权限类型', max_length=20, choices=[
        ('read', '只读'),
        ('write', '可写'),
        ('hidden', '隐藏'),
    ], default='read')
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '字段权限'
        verbose_name_plural = '字段权限'
        unique_together = ('user', 'resource_type', 'field_name')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.resource_type}.{self.field_name}"


class DepartmentPermission(models.Model):
    """部门权限模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', related_name='department_permissions')
    department = models.ForeignKey('organizations.Department', on_delete=models.CASCADE, verbose_name='部门')
    permission_type = models.CharField('权限类型', max_length=20, choices=[
        ('view', '查看'),
        ('edit', '编辑'),
        ('admin', '管理'),
    ], default='view')
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '部门权限'
        verbose_name_plural = '部门权限'
        unique_together = ('user', 'department')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.department.name}"


class PermissionCache(models.Model):
    """权限缓存模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', related_name='permission_caches')
    cache_key = models.CharField('缓存键', max_length=200, unique=True)
    cache_data = models.JSONField('缓存数据', default=dict)
    expires_at = models.DateTimeField('过期时间')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '权限缓存'
        verbose_name_plural = '权限缓存'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.cache_key}"

    def is_expired(self):
        return timezone.now() > self.expires_at