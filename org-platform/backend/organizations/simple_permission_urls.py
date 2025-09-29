"""
简单权限管理URL路由
"""

from rest_framework.routers import DefaultRouter
from .simple_permission_views import SimplePermissionViewSet

router = DefaultRouter()
router.register(r'simple-permission', SimplePermissionViewSet, basename='simple-permission')

urlpatterns = router.urls
