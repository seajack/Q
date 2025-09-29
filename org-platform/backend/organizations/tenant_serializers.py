"""
租户管理序列化器
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .tenant_models import Tenant, TenantUser, TenantSettings, TenantSubscription


class TenantSerializer(serializers.ModelSerializer):
    """租户序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'code', 'domain', 'description', 'status', 'status_display',
            'max_users', 'max_departments', 'max_employees', 'is_active', 'is_expired',
            'created_at', 'updated_at', 'expires_at', 'contact_name', 'contact_email', 'contact_phone'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantCreateSerializer(serializers.ModelSerializer):
    """租户创建序列化器"""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Tenant
        fields = [
            'name', 'code', 'domain', 'description', 'contact_name', 'contact_email', 'contact_phone',
            'max_users', 'max_departments', 'max_employees', 'expires_at',
            'password', 'confirm_password'
        ]
    
    def validate(self, attrs):
        """验证数据"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("密码不匹配")
        return attrs
    
    def create(self, validated_data):
        """创建租户"""
        # 移除密码相关字段
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        
        # 创建租户
        tenant = Tenant.objects.create(**validated_data)
        
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username=f"{tenant.code}_admin",
            email=tenant.contact_email,
            password=password
        )
        
        # 创建租户用户关联
        TenantUser.objects.create(
            tenant=tenant,
            user=admin_user,
            role='admin',
            is_active=True,
            can_manage_users=True,
            can_manage_departments=True,
            can_manage_employees=True,
            can_view_reports=True
        )
        
        # 创建租户设置
        TenantSettings.objects.create(
            tenant=tenant,
            company_name=tenant.name
        )
        
        # 创建租户订阅
        from django.utils import timezone
        from datetime import timedelta
        TenantSubscription.objects.create(
            tenant=tenant,
            plan='basic',
            status='active',
            end_date=timezone.now() + timedelta(days=30)
        )
        
        return tenant


class TenantUserSerializer(serializers.ModelSerializer):
    """租户用户序列化器"""
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)
    is_superuser = serializers.BooleanField(source='user.is_superuser', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    last_login = serializers.DateTimeField(source='user.last_login', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = TenantUser
        fields = [
            'id', 'tenant', 'user_id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'can_manage_users', 'can_manage_departments',
            'can_manage_employees', 'can_view_reports', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantSettingsSerializer(serializers.ModelSerializer):
    """租户设置序列化器"""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = TenantSettings
        fields = [
            'id', 'tenant', 'tenant_name', 'timezone', 'language', 'date_format',
            'company_name', 'company_logo', 'company_address',
            'enable_employee_self_service', 'enable_workflow_approval', 'enable_integration_api',
            'password_policy', 'session_timeout', 'enable_two_factor',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantSubscriptionSerializer(serializers.ModelSerializer):
    """租户订阅序列化器"""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = TenantSubscription
        fields = [
            'id', 'tenant', 'tenant_name', 'plan', 'plan_display', 'status', 'status_display',
            'start_date', 'end_date', 'auto_renew', 'is_active', 'days_remaining',
            'max_users', 'max_departments', 'max_employees', 'max_api_calls',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_days_remaining(self, obj):
        """计算剩余天数"""
        if obj.end_date:
            from django.utils import timezone
            delta = obj.end_date - timezone.now()
            return max(0, delta.days)
        return None


class TenantStatsSerializer(serializers.Serializer):
    """租户统计序列化器"""
    tenant_name = serializers.CharField()
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    total_employees = serializers.IntegerField()
    subscription_status = serializers.CharField()
    created_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField(allow_null=True)


class TenantInviteSerializer(serializers.Serializer):
    """租户邀请序列化器"""
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=TenantUser.ROLE_CHOICES, default='user')
    permissions = serializers.DictField(required=False)
    
    def validate_email(self, value):
        """验证邮箱"""
        # 检查邮箱是否已经被邀请
        tenant = self.context.get('tenant')
        if tenant:
            existing_user = User.objects.filter(email=value).first()
            if existing_user:
                if TenantUser.objects.filter(tenant=tenant, user=existing_user).exists():
                    raise serializers.ValidationError("该用户已经是租户成员")
        return value


class TenantPermissionUpdateSerializer(serializers.Serializer):
    """租户权限更新序列化器"""
    permissions = serializers.DictField()
    
    def validate_permissions(self, value):
        """验证权限字段"""
        valid_permissions = [
            'can_manage_users', 'can_manage_departments', 
            'can_manage_employees', 'can_view_reports'
        ]
        
        for permission in value.keys():
            if permission not in valid_permissions:
                raise serializers.ValidationError(f"无效的权限字段: {permission}")
        
        return value
