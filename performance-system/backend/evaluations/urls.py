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

urlpatterns = [
    path('', include(router.urls)),
    path('stats/overview/', views.overview_stats, name='overview_stats'),
    path('stats/cycle/<int:cycle_id>/', views.cycle_stats, name='cycle_stats'),
]