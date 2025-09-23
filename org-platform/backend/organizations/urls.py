from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'positions', views.PositionViewSet)
router.register(r'employees', views.EmployeeViewSet)
router.register(r'structures', views.OrganizationStructureViewSet)
router.register(r'stats', views.OrganizationStatsView, basename='stats')

urlpatterns = [
    path('api/', include(router.urls)),
    # 绩效考核系统代理API
    path('performance-api/stats/overview/', views.performance_overview_stats, name='performance_overview_stats'),
    path('performance-api/stats/cycle/<int:cycle_id>/', views.performance_cycle_stats, name='performance_cycle_stats'),
]