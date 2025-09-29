"""
智能分析URL路由
"""

from rest_framework.routers import DefaultRouter
from .intelligence_views import (
    AnalysisResultViewSet, OptimizationRecommendationViewSet,
    OrganizationAnalysisViewSet, AnalysisHistoryViewSet,
    AnalysisConfigViewSet, UserFeedbackViewSet, BenchmarkDataViewSet,
    IntelligenceApiViewSet
)

router = DefaultRouter()
router.register(r'analysis-results', AnalysisResultViewSet)
router.register(r'optimization-recommendations', OptimizationRecommendationViewSet)
router.register(r'organization-analyses', OrganizationAnalysisViewSet)
router.register(r'analysis-histories', AnalysisHistoryViewSet)
router.register(r'analysis-configs', AnalysisConfigViewSet)
router.register(r'user-feedbacks', UserFeedbackViewSet)
router.register(r'benchmark-data', BenchmarkDataViewSet)
router.register(r'intelligence', IntelligenceApiViewSet, basename='intelligence')

urlpatterns = router.urls
