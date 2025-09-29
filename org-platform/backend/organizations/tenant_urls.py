"""
租户管理URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .tenant_views import (
    TenantViewSet, TenantUserViewSet, 
    TenantSettingsViewSet, TenantSubscriptionViewSet
)

router = DefaultRouter()
router.register(r'tenants', TenantViewSet)
router.register(r'tenant-users', TenantUserViewSet)
router.register(r'tenant-settings', TenantSettingsViewSet)
router.register(r'tenant-subscriptions', TenantSubscriptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
