from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .multidimensional_views import (
    EvaluationDimensionViewSet, EvaluationMethodViewSet,
    EvaluationCycleTypeViewSet, MultidimensionalEvaluationViewSet,
    MultidimensionalIndicatorViewSet, EvaluationTemplateViewSet
)

router = DefaultRouter()
router.register(r'dimensions', EvaluationDimensionViewSet)
router.register(r'methods', EvaluationMethodViewSet)
router.register(r'cycle-types', EvaluationCycleTypeViewSet)
router.register(r'evaluations', MultidimensionalEvaluationViewSet)
router.register(r'indicators', MultidimensionalIndicatorViewSet)
router.register(r'templates', EvaluationTemplateViewSet)

urlpatterns = [
    path('multidimensional/', include(router.urls)),
]
