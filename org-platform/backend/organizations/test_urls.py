"""
测试URL路由
"""

from rest_framework.routers import DefaultRouter
from .test_views import TestViewSet

router = DefaultRouter()
router.register(r'test', TestViewSet, basename='test')

urlpatterns = router.urls
