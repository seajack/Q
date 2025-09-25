from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import models
from .permission_models import (
    Permission, Role, RolePermission, UserRole, DataPermission,
    RoleDataPermission, PermissionLog, FieldPermission, DepartmentPermission
)
from .models import Department


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Permission
        fields = [
            'id', 'name', 'code', 'permission_type', 'permission_type_display',
            'description', 'resource', 'action', 'level', 'parent', 'parent_name',
            'full_path', 'is_active', 'sort_order', 'children_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_children_count(self, obj):
        """获取子权限数量"""
        return obj.children.count()
    
    def validate_code(self, value):
        """验证权限编码唯一性"""
        if self.instance and self.instance.code == value:
            return value
        
        if Permission.objects.filter(code=value).exists():
            raise serializers.ValidationError("权限编码已存在")
        return value


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    role_type_display = serializers.CharField(source='get_role_type_display', read_only=True)
    data_scope_display = serializers.CharField(source='get_data_scope_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    parent_role_name = serializers.CharField(source='parent_role.name', read_only=True)
    permissions_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'role_type', 'role_type_display', 'description',
            'is_active', 'is_system', 'level', 'parent_role', 'parent_role_name',
            'inherit_permissions', 'data_scope', 'data_scope_display',
            'created_by', 'created_by_name', 'permissions_count', 'users_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_permissions_count(self, obj):
        """获取角色权限数量"""
        return obj.role_permissions.filter(is_granted=True).count()
    
    def get_users_count(self, obj):
        """获取角色用户数量"""
        return obj.user_roles.filter(is_active=True).count()
    
    def validate_code(self, value):
        """验证角色编码唯一性"""
        if self.instance and self.instance.code == value:
            return value
        
        if Role.objects.filter(code=value).exists():
            raise serializers.ValidationError("角色编码已存在")
        return value


class RolePermissionSerializer(serializers.ModelSerializer):
    """角色权限序列化器"""
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_code = serializers.CharField(source='permission.code', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.username', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'permission', 'permission_name', 'permission_code',
            'is_granted', 'granted_at', 'granted_by', 'granted_by_name'
        ]
        read_only_fields = ['granted_at']


class UserRoleSerializer(serializers.ModelSerializer):
    """用户角色序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_code = serializers.CharField(source='role.code', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_name', 'user_full_name', 'role', 'role_name', 'role_code',
            'is_active', 'assigned_at', 'assigned_by', 'assigned_by_name',
            'expires_at', 'is_expired'
        ]
        read_only_fields = ['assigned_at']
    
    def get_user_full_name(self, obj):
        """获取用户全名"""
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return obj.user.username
    
    def get_is_expired(self, obj):
        """检查是否过期"""
        return obj.is_expired()


class DataPermissionSerializer(serializers.ModelSerializer):
    """数据权限序列化器"""
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    scope_type_display = serializers.CharField(source='get_scope_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = DataPermission
        fields = [
            'id', 'name', 'permission_type', 'permission_type_display',
            'scope_type', 'scope_type_display', 'resource_type', 'resource_id',
            'custom_scope', 'field_permissions', 'data_masking',
            'is_active', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def validate_custom_scope(self, value):
        """验证自定义范围"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("自定义范围必须是字典格式")
        return value
    
    def validate_field_permissions(self, value):
        """验证字段权限"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("字段权限必须是字典格式")
        return value
    
    def validate_data_masking(self, value):
        """验证数据脱敏配置"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("数据脱敏配置必须是字典格式")
        return value


class RoleDataPermissionSerializer(serializers.ModelSerializer):
    """角色数据权限序列化器"""
    data_permission_name = serializers.CharField(source='data_permission.name', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.username', read_only=True)
    
    class Meta:
        model = RoleDataPermission
        fields = [
            'id', 'role', 'data_permission', 'data_permission_name',
            'is_granted', 'granted_at', 'granted_by', 'granted_by_name'
        ]
        read_only_fields = ['granted_at']


class PermissionLogSerializer(serializers.ModelSerializer):
    """权限日志序列化器"""
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PermissionLog
        fields = [
            'id', 'user', 'user_name', 'action_type', 'action_type_display',
            'resource_type', 'resource_id', 'action_detail', 'result', 'result_display',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['created_at']


class FieldPermissionSerializer(serializers.ModelSerializer):
    """字段权限序列化器"""
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = FieldPermission
        fields = [
            'id', 'user', 'user_name', 'resource_type', 'field_name',
            'permission_type', 'permission_type_display', 'masking_rule',
            'masking_config', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_masking_config(self, value):
        """验证脱敏配置"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("脱敏配置必须是字典格式")
        return value


class DepartmentPermissionSerializer(serializers.ModelSerializer):
    """部门权限序列化器"""
    data_scope_display = serializers.CharField(source='get_data_scope_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = DepartmentPermission
        fields = [
            'id', 'user', 'user_name', 'department', 'department_name',
            'can_view', 'can_edit', 'can_delete', 'can_manage',
            'data_scope', 'data_scope_display', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PermissionTreeSerializer(serializers.ModelSerializer):
    """权限树序列化器"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Permission
        fields = [
            'id', 'name', 'code', 'permission_type', 'level',
            'is_active', 'sort_order', 'children'
        ]
    
    def get_children(self, obj):
        """获取子权限"""
        children = obj.children.filter(is_active=True).order_by('sort_order')
        return PermissionTreeSerializer(children, many=True, context=self.context).data


class RolePermissionAssignSerializer(serializers.Serializer):
    """角色权限分配序列化器"""
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="权限ID列表"
    )
    
    def validate_permission_ids(self, value):
        """验证权限ID列表"""
        if not value:
            raise serializers.ValidationError("权限ID列表不能为空")
        
        # 检查权限是否存在
        existing_permissions = Permission.objects.filter(id__in=value, is_active=True)
        if len(existing_permissions) != len(value):
            raise serializers.ValidationError("部分权限不存在或已禁用")
        
        return value


class UserRoleAssignSerializer(serializers.Serializer):
    """用户角色分配序列化器"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="用户ID列表"
    )
    expires_at = serializers.DateTimeField(
        required=False,
        help_text="过期时间"
    )
    
    def validate_user_ids(self, value):
        """验证用户ID列表"""
        if not value:
            raise serializers.ValidationError("用户ID列表不能为空")
        
        # 检查用户是否存在
        existing_users = User.objects.filter(id__in=value)
        if len(existing_users) != len(value):
            raise serializers.ValidationError("部分用户不存在")
        
        return value


class PermissionCheckSerializer(serializers.Serializer):
    """权限检查序列化器"""
    permission_codes = serializers.ListField(
        child=serializers.CharField(),
        help_text="权限编码列表"
    )
    require_all = serializers.BooleanField(
        default=False,
        help_text="是否需要所有权限"
    )


class DataScopeSerializer(serializers.Serializer):
    """数据范围序列化器"""
    resource_type = serializers.CharField(help_text="资源类型")
    resource_id = serializers.CharField(
        required=False,
        help_text="资源ID"
    )
    department_id = serializers.IntegerField(
        required=False,
        help_text="部门ID"
    )


class FieldMaskingSerializer(serializers.Serializer):
    """字段脱敏序列化器"""
    resource_type = serializers.CharField(help_text="资源类型")
    field_name = serializers.CharField(help_text="字段名")
    value = serializers.CharField(help_text="字段值")
