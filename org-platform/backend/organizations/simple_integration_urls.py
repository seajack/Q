"""
简单集成管理URL路由
"""

from rest_framework.routers import DefaultRouter
from .simple_integration_views import SimpleIntegrationViewSet

router = DefaultRouter()
router.register(r'simple-integration', SimpleIntegrationViewSet, basename='simple-integration')

urlpatterns = router.urls
