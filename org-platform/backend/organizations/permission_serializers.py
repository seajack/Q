"""
权限管理序列化器
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .permission_models import (
    Permission, Role, RolePermission, UserRole, PermissionLog,
    DataPermission, PermissionCache, RoleDataPermission,
    FieldPermission, DepartmentPermission
)


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_children_count(self, obj):
        return obj.children.count()


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    permissions_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_permissions_count(self, obj):
        return obj.permissions.count()

    def get_users_count(self, obj):
        return obj.user_roles.filter(is_active=True).count()


class RolePermissionSerializer(serializers.ModelSerializer):
    """角色权限序列化器"""
    role_name = serializers.CharField(source='role.name', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.username', read_only=True)

    class Meta:
        model = RolePermission
        fields = '__all__'
        read_only_fields = ('id', 'granted_at')


class UserRoleSerializer(serializers.ModelSerializer):
    """用户角色序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)

    class Meta:
        model = UserRole
        fields = '__all__'
        read_only_fields = ('id', 'assigned_at')


class PermissionLogSerializer(serializers.ModelSerializer):
    """权限日志序列化器"""
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = PermissionLog
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class DataPermissionSerializer(serializers.ModelSerializer):
    """数据权限序列化器"""
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = DataPermission
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class PermissionCacheSerializer(serializers.ModelSerializer):
    """权限缓存序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = PermissionCache
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

    def get_is_expired(self, obj):
        return obj.is_expired()


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    roles = RoleSerializer(source='user_roles', many=True, read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    is_active_display = serializers.CharField(source='get_is_active_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_active_display', 'last_login', 'date_joined', 'roles', 'permissions']
        read_only_fields = ['id', 'date_joined', 'last_login']


class PermissionStatsSerializer(serializers.Serializer):
    """权限统计序列化器"""
    total_permissions = serializers.IntegerField()
    active_permissions = serializers.IntegerField()
    total_roles = serializers.IntegerField()
    active_roles = serializers.IntegerField()
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    recent_logs = serializers.IntegerField()
    permission_distribution = serializers.DictField()
    role_distribution = serializers.DictField()


class RoleDataPermissionSerializer(serializers.ModelSerializer):
    """角色数据权限序列化器"""
    role_name = serializers.CharField(source='role.name', read_only=True)
    data_permission_resource = serializers.CharField(source='data_permission.resource', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.username', read_only=True)

    class Meta:
        model = RoleDataPermission
        fields = '__all__'
        read_only_fields = ('id', 'granted_at')


class FieldPermissionSerializer(serializers.ModelSerializer):
    """字段权限序列化器"""
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = FieldPermission
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class DepartmentPermissionSerializer(serializers.ModelSerializer):
    """部门权限序列化器"""
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = DepartmentPermission
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class PermissionTreeSerializer(serializers.ModelSerializer):
    """权限树序列化器"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'permission_type', 'description', 'resource', 'action', 'status', 'sort_order', 'children']

    def get_children(self, obj):
        children = obj.children.filter(status='active').order_by('sort_order')
        return PermissionTreeSerializer(children, many=True).data