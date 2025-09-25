from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json


class Permission(models.Model):
    """权限模型"""
    PERMISSION_TYPE_CHOICES = [
        ('menu', '菜单权限'),
        ('button', '按钮权限'),
        ('api', 'API权限'),
        ('data', '数据权限'),
        ('field', '字段权限'),
    ]
    
    name = models.CharField('权限名称', max_length=100)
    code = models.CharField('权限编码', max_length=100, unique=True)
    permission_type = models.CharField('权限类型', max_length=20, choices=PERMISSION_TYPE_CHOICES)
    description = models.TextField('描述', blank=True)
    
    # 权限资源信息
    resource = models.CharField('资源标识', max_length=200, blank=True)
    action = models.CharField('操作类型', max_length=50, blank=True)
    
    # 权限级别
    level = models.IntegerField('权限级别', default=1)
    parent = models.ForeignKey('self', verbose_name='父权限', on_delete=models.CASCADE, null=True, blank=True)
    
    # 权限配置
    is_active = models.BooleanField('是否启用', default=True)
    sort_order = models.IntegerField('排序', default=0)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '权限'
        verbose_name_plural = '权限'
        ordering = ['level', 'sort_order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_full_path(self):
        """获取权限完整路径"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class Role(models.Model):
    """角色模型"""
    ROLE_TYPE_CHOICES = [
        ('system', '系统角色'),
        ('custom', '自定义角色'),
        ('department', '部门角色'),
    ]
    
    name = models.CharField('角色名称', max_length=100)
    code = models.CharField('角色编码', max_length=100, unique=True)
    role_type = models.CharField('角色类型', max_length=20, choices=ROLE_TYPE_CHOICES, default='custom')
    description = models.TextField('描述', blank=True)
    
    # 角色配置
    is_active = models.BooleanField('是否启用', default=True)
    is_system = models.BooleanField('系统角色', default=False)
    level = models.IntegerField('角色级别', default=1)
    
    # 权限继承
    parent_role = models.ForeignKey('self', verbose_name='父角色', on_delete=models.CASCADE, null=True, blank=True)
    inherit_permissions = models.BooleanField('继承父角色权限', default=True)
    
    # 数据权限范围
    data_scope = models.CharField('数据权限范围', max_length=20, choices=[
        ('all', '全部数据权限'),
        ('custom', '自定义数据权限'),
        ('dept', '本部门数据权限'),
        ('dept_and_child', '本部门及以下数据权限'),
        ('self', '仅本人数据权限'),
    ], default='self')
    
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.CASCADE, related_name='created_roles')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_permissions(self):
        """获取角色权限（包括继承的权限）"""
        permissions = set()
        
        # 获取直接分配的权限
        direct_permissions = self.role_permissions.all()
        for rp in direct_permissions:
            permissions.add(rp.permission)
        
        # 获取继承的权限
        if self.inherit_permissions and self.parent_role:
            parent_permissions = self.parent_role.get_permissions()
            permissions.update(parent_permissions)
        
        return list(permissions)


class RolePermission(models.Model):
    """角色权限关联模型"""
    role = models.ForeignKey(Role, verbose_name='角色', on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, verbose_name='权限', on_delete=models.CASCADE, related_name='role_permissions')
    
    # 权限配置
    is_granted = models.BooleanField('是否授权', default=True)
    granted_at = models.DateTimeField('授权时间', auto_now_add=True)
    granted_by = models.ForeignKey(User, verbose_name='授权者', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = '角色权限'
        verbose_name_plural = '角色权限'
        unique_together = ['role', 'permission']
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class UserRole(models.Model):
    """用户角色关联模型"""
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, verbose_name='角色', on_delete=models.CASCADE, related_name='user_roles')
    
    # 角色配置
    is_active = models.BooleanField('是否启用', default=True)
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)
    assigned_by = models.ForeignKey(User, verbose_name='分配者', on_delete=models.CASCADE, related_name='assigned_roles')
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    
    class Meta:
        verbose_name = '用户角色'
        verbose_name_plural = '用户角色'
        unique_together = ['user', 'role']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
    
    def is_expired(self):
        """检查角色是否过期"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class DataPermission(models.Model):
    """数据权限模型"""
    PERMISSION_TYPE_CHOICES = [
        ('read', '读取权限'),
        ('write', '写入权限'),
        ('delete', '删除权限'),
        ('export', '导出权限'),
    ]
    
    SCOPE_TYPE_CHOICES = [
        ('all', '全部数据'),
        ('dept', '本部门数据'),
        ('dept_and_child', '本部门及下级数据'),
        ('self', '本人数据'),
        ('custom', '自定义范围'),
    ]
    
    name = models.CharField('权限名称', max_length=100)
    permission_type = models.CharField('权限类型', max_length=20, choices=PERMISSION_TYPE_CHOICES)
    scope_type = models.CharField('数据范围', max_length=20, choices=SCOPE_TYPE_CHOICES)
    description = models.TextField('描述', blank=True)
    
    # 权限配置
    resource_type = models.CharField('资源类型', max_length=100)
    resource_id = models.CharField('资源ID', max_length=100, blank=True)
    
    # 自定义范围配置
    custom_scope = models.JSONField('自定义范围', default=dict, blank=True)
    
    # 字段权限
    field_permissions = models.JSONField('字段权限', default=dict, blank=True)
    
    # 数据脱敏配置
    data_masking = models.JSONField('数据脱敏', default=dict, blank=True)
    
    is_active = models.BooleanField('是否启用', default=True)
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.CASCADE)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '数据权限'
        verbose_name_plural = '数据权限'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_permission_type_display()})"


class RoleDataPermission(models.Model):
    """角色数据权限关联模型"""
    role = models.ForeignKey(Role, verbose_name='角色', on_delete=models.CASCADE, related_name='role_data_permissions')
    data_permission = models.ForeignKey(DataPermission, verbose_name='数据权限', on_delete=models.CASCADE, related_name='role_data_permissions')
    
    # 权限配置
    is_granted = models.BooleanField('是否授权', default=True)
    granted_at = models.DateTimeField('授权时间', auto_now_add=True)
    granted_by = models.ForeignKey(User, verbose_name='授权者', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = '角色数据权限'
        verbose_name_plural = '角色数据权限'
        unique_together = ['role', 'data_permission']
    
    def __str__(self):
        return f"{self.role.name} - {self.data_permission.name}"


class PermissionLog(models.Model):
    """权限操作日志"""
    ACTION_TYPE_CHOICES = [
        ('grant', '授权'),
        ('revoke', '撤销'),
        ('inherit', '继承'),
        ('expire', '过期'),
    ]
    
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, related_name='permission_logs')
    action_type = models.CharField('操作类型', max_length=20, choices=ACTION_TYPE_CHOICES)
    resource_type = models.CharField('资源类型', max_length=100)
    resource_id = models.CharField('资源ID', max_length=100, blank=True)
    
    # 操作详情
    action_detail = models.JSONField('操作详情', default=dict)
    result = models.CharField('操作结果', max_length=20, choices=[
        ('success', '成功'),
        ('failed', '失败'),
        ('denied', '拒绝'),
    ])
    
    # 请求信息
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    user_agent = models.TextField('用户代理', blank=True)
    
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '权限日志'
        verbose_name_plural = '权限日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} - {self.created_at}"


class PermissionCache(models.Model):
    """权限缓存模型"""
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, related_name='permission_cache')
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
        """检查缓存是否过期"""
        return timezone.now() > self.expires_at


class FieldPermission(models.Model):
    """字段权限模型"""
    FIELD_TYPE_CHOICES = [
        ('visible', '可见'),
        ('readonly', '只读'),
        ('hidden', '隐藏'),
        ('masked', '脱敏'),
    ]
    
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, related_name='field_permissions')
    resource_type = models.CharField('资源类型', max_length=100)
    field_name = models.CharField('字段名', max_length=100)
    permission_type = models.CharField('权限类型', max_length=20, choices=FIELD_TYPE_CHOICES)
    
    # 脱敏配置
    masking_rule = models.CharField('脱敏规则', max_length=100, blank=True)
    masking_config = models.JSONField('脱敏配置', default=dict, blank=True)
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '字段权限'
        verbose_name_plural = '字段权限'
        unique_together = ['user', 'resource_type', 'field_name']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.resource_type}.{self.field_name}"


class DepartmentPermission(models.Model):
    """部门权限模型"""
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, related_name='department_permissions')
    department = models.ForeignKey('Department', verbose_name='部门', on_delete=models.CASCADE, related_name='department_permissions')
    
    # 权限配置
    can_view = models.BooleanField('可查看', default=False)
    can_edit = models.BooleanField('可编辑', default=False)
    can_delete = models.BooleanField('可删除', default=False)
    can_manage = models.BooleanField('可管理', default=False)
    
    # 数据范围
    data_scope = models.CharField('数据范围', max_length=20, choices=[
        ('all', '全部数据'),
        ('dept', '本部门数据'),
        ('dept_and_child', '本部门及下级数据'),
        ('self', '本人数据'),
    ], default='self')
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '部门权限'
        verbose_name_plural = '部门权限'
        unique_together = ['user', 'department']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.department.name}"
