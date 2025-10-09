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
    path('deadline-reminders/', views.deadline_reminders, name='deadline_reminders'),
    # 用户相关API
    path('user/profile/', views.user_profile, name='user_profile'),
    path('user/profile/', views.update_user_profile, name='update_user_profile'),
    path('user/avatar/', views.upload_user_avatar, name='upload_user_avatar'),
    path('user/login-history/', views.user_login_history, name='user_login_history'),
    path('user/change-password/', views.change_user_password, name='change_user_password'),
]