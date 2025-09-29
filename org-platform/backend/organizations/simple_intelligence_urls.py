"""
简单智能分析URL路由
"""

from rest_framework.routers import DefaultRouter
from .simple_intelligence_views import SimpleIntelligenceViewSet

router = DefaultRouter()
router.register(r'simple-intelligence', SimpleIntelligenceViewSet, basename='simple-intelligence')

urlpatterns = router.urls
