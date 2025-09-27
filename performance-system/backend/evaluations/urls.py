from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cycles', views.EvaluationCycleViewSet)
router.register(r'indicators', views.EvaluationIndicatorViewSet)
router.register(r'rules', views.EvaluationRuleViewSet)
router.register(r'manual-assignments', views.ManualEvaluationAssignmentViewSet)
router.register(r'tasks', views.EvaluationTaskViewSet)
router.register(r'scores', views.EvaluationScoreViewSet)
router.register(r'results', views.EvaluationResultViewSet)
router.register(r'employees', views.EmployeeViewSet)
router.register(r'position-weights', views.PositionWeightViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/overview/', views.stats_overview, name='stats_overview'),
    path('stats/cycle/<int:cycle_id>/', views.stats_cycle, name='stats_cycle'),
]