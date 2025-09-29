"""
多租户中间件
"""
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from .tenant_models import Tenant, TenantUser
import threading

# 线程本地存储，用于存储当前请求的租户信息
_thread_locals = threading.local()


class TenantMiddleware(MiddlewareMixin):
    """租户中间件"""
    
    def process_request(self, request):
        """处理请求，识别租户"""
        # 从请求中获取租户信息
        tenant = self.get_tenant_from_request(request)
        
        if tenant:
            # 将租户信息存储到线程本地存储中
            _thread_locals.tenant = tenant
            request.tenant = tenant
        else:
            # 如果没有找到租户，设置为None
            _thread_locals.tenant = None
            request.tenant = None
    
    def get_tenant_from_request(self, request):
        """从请求中获取租户信息"""
        # 方法1: 从子域名获取租户
        host = request.get_host().split(':')[0]  # 移除端口号
        subdomain = host.split('.')[0] if '.' in host else None
        
        if subdomain and subdomain != 'www':
            try:
                return Tenant.objects.get(domain=subdomain, status='active')
            except Tenant.DoesNotExist:
                pass
        
        # 方法2: 从请求头获取租户
        tenant_code = request.META.get('HTTP_X_TENANT_CODE')
        if tenant_code:
            try:
                return Tenant.objects.get(code=tenant_code, status='active')
            except Tenant.DoesNotExist:
                pass
        
        # 方法3: 从URL参数获取租户
        tenant_code = request.GET.get('tenant')
        if tenant_code:
            try:
                return Tenant.objects.get(code=tenant_code, status='active')
            except Tenant.DoesNotExist:
                pass
        
        # 方法4: 从用户会话获取租户
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                tenant_user = TenantUser.objects.get(user=request.user, is_active=True)
                return tenant_user.tenant
            except TenantUser.DoesNotExist:
                pass
        
        return None


def get_current_tenant():
    """获取当前租户"""
    return getattr(_thread_locals, 'tenant', None)


def set_current_tenant(tenant):
    """设置当前租户"""
    _thread_locals.tenant = tenant


class TenantContextMixin:
    """租户上下文混入类"""
    
    def get_queryset(self):
        """重写get_queryset方法，自动过滤租户数据"""
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        
        if tenant and hasattr(queryset.model, 'tenant'):
            return queryset.filter(tenant=tenant)
        
        return queryset
    
    def perform_create(self, serializer):
        """重写perform_create方法，自动设置租户"""
        tenant = get_current_tenant()
        if tenant:
            serializer.save(tenant=tenant)
        else:
            serializer.save()


class TenantPermissionMixin:
    """租户权限混入类"""
    
    def has_tenant_permission(self, user, tenant, permission):
        """检查用户是否有租户权限"""
        try:
            tenant_user = TenantUser.objects.get(user=user, tenant=tenant, is_active=True)
            return getattr(tenant_user, permission, False)
        except TenantUser.DoesNotExist:
            return False
    
    def check_tenant_access(self, user, tenant):
        """检查用户是否有租户访问权限"""
        if not tenant or not tenant.is_active:
            return False
        
        if tenant.is_expired:
            return False
        
        try:
            tenant_user = TenantUser.objects.get(user=user, tenant=tenant, is_active=True)
            return True
        except TenantUser.DoesNotExist:
            return False
