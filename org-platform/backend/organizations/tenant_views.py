"""
租户管理API视图
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone
from .tenant_models import Tenant, TenantUser, TenantSettings, TenantSubscription
from .tenant_serializers import (
    TenantSerializer, TenantUserSerializer, TenantSettingsSerializer,
    TenantSubscriptionSerializer, TenantCreateSerializer
)
from .tenant_middleware import TenantContextMixin, TenantPermissionMixin


class TenantViewSet(TenantContextMixin, TenantPermissionMixin, viewsets.ModelViewSet):
    """租户管理视图集"""
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TenantCreateSerializer
        return TenantSerializer
    
    @action(detail=False, methods=['get'])
    def my_tenants(self, request):
        """获取当前用户的租户列表"""
        user = request.user
        tenant_users = TenantUser.objects.filter(user=user, is_active=True)
        tenants = [tu.tenant for tu in tenant_users]
        serializer = self.get_serializer(tenants, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def switch_tenant(self, request, pk=None):
        """切换租户"""
        tenant = self.get_object()
        
        # 检查用户是否有权限访问该租户
        if not self.check_tenant_access(request.user, tenant):
            return Response(
                {'error': '没有权限访问该租户'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 将租户信息存储到会话中
        request.session['current_tenant_id'] = str(tenant.id)
        
        return Response({
            'message': f'已切换到租户: {tenant.name}',
            'tenant': TenantSerializer(tenant).data
        })
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """获取租户统计信息"""
        tenant = self.get_object()
        
        # 检查权限
        if not self.check_tenant_access(request.user, tenant):
            return Response(
                {'error': '没有权限访问该租户'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 统计信息
        stats = {
            'tenant_name': tenant.name,
            'total_users': TenantUser.objects.filter(tenant=tenant).count(),
            'active_users': TenantUser.objects.filter(tenant=tenant, is_active=True).count(),
            'total_departments': tenant.department_set.count(),
            'total_employees': tenant.employee_set.count(),
            'subscription_status': tenant.tenantsubscription.status if hasattr(tenant, 'tenantsubscription') else 'unknown',
            'created_at': tenant.created_at,
            'expires_at': tenant.expires_at,
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def invite_user(self, request, pk=None):
        """邀请用户加入租户"""
        tenant = self.get_object()
        
        # 检查权限
        if not self.has_tenant_permission(request.user, tenant, 'can_manage_users'):
            return Response(
                {'error': '没有权限管理用户'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        email = request.data.get('email')
        role = request.data.get('role', 'user')
        
        if not email:
            return Response(
                {'error': '邮箱地址不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 查找或创建用户
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # 创建新用户
            user = User.objects.create_user(
                username=email,
                email=email,
                password='temp_password'  # 临时密码，需要用户重置
            )
        
        # 创建租户用户关联
        tenant_user, created = TenantUser.objects.get_or_create(
            tenant=tenant,
            user=user,
            defaults={
                'role': role,
                'is_active': True
            }
        )
        
        if not created:
            return Response(
                {'error': '用户已经是该租户的成员'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': '用户邀请成功',
            'user': TenantUserSerializer(tenant_user).data
        })


class TenantUserViewSet(TenantContextMixin, TenantPermissionMixin, viewsets.ModelViewSet):
    """租户用户管理视图集"""
    queryset = TenantUser.objects.all()
    serializer_class = TenantUserSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """获取当前租户的用户列表"""
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        
        if tenant:
            return queryset.filter(tenant=tenant)
        
        return queryset.none()
    
    @action(detail=True, methods=['post'])
    def update_permissions(self, request, pk=None):
        """更新用户权限"""
        tenant_user = self.get_object()
        tenant = tenant_user.tenant
        
        # 检查权限
        if not self.has_tenant_permission(request.user, tenant, 'can_manage_users'):
            return Response(
                {'error': '没有权限管理用户'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 更新权限
        permissions = request.data.get('permissions', {})
        for permission, value in permissions.items():
            if hasattr(tenant_user, permission):
                setattr(tenant_user, permission, value)
        
        tenant_user.save()
        
        return Response({
            'message': '权限更新成功',
            'user': TenantUserSerializer(tenant_user).data
        })


class TenantSettingsViewSet(TenantContextMixin, TenantPermissionMixin, viewsets.ModelViewSet):
    """租户设置管理视图集"""
    queryset = TenantSettings.objects.all()
    serializer_class = TenantSettingsSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """获取当前租户的设置"""
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        
        if tenant:
            return queryset.filter(tenant=tenant)
        
        return queryset.none()
    
    @action(detail=False, methods=['get'])
    def current_settings(self, request):
        """获取当前租户的设置"""
        tenant = get_current_tenant()
        
        if not tenant:
            return Response(
                {'error': '未找到当前租户'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            settings = TenantSettings.objects.get(tenant=tenant)
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
        except TenantSettings.DoesNotExist:
            return Response(
                {'error': '租户设置不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class TenantSubscriptionViewSet(TenantContextMixin, TenantPermissionMixin, viewsets.ModelViewSet):
    """租户订阅管理视图集"""
    queryset = TenantSubscription.objects.all()
    serializer_class = TenantSubscriptionSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """获取当前租户的订阅信息"""
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        
        if tenant:
            return queryset.filter(tenant=tenant)
        
        return queryset.none()
    
    @action(detail=True, methods=['post'])
    def renew_subscription(self, request, pk=None):
        """续费订阅"""
        subscription = self.get_object()
        tenant = subscription.tenant
        
        # 检查权限
        if not self.has_tenant_permission(request.user, tenant, 'can_manage_users'):
            return Response(
                {'error': '没有权限管理订阅'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 续费逻辑
        months = request.data.get('months', 1)
        subscription.end_date = timezone.now() + timezone.timedelta(days=30 * months)
        subscription.status = 'active'
        subscription.save()
        
        return Response({
            'message': f'订阅已续费 {months} 个月',
            'subscription': TenantSubscriptionSerializer(subscription).data
        })
