from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import integration_views
from . import permission_views
from .integration_views import DownloadTemplateView, ImportDepartmentsView

router = DefaultRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'positions', views.PositionViewSet)
router.register(r'employees', views.EmployeeViewSet)
router.register(r'structures', views.OrganizationStructureViewSet)
router.register(r'stats', views.OrganizationStatsView, basename='stats')
# 配置管理路由
router.register(r'configs', views.SystemConfigViewSet)
router.register(r'dictionaries', views.DictionaryViewSet)
router.register(r'position-templates', views.PositionTemplateViewSet)
router.register(r'workflow-rules', views.WorkflowRuleViewSet)

# 系统集成路由
integration_router = DefaultRouter()
integration_router.register(r'systems', integration_views.IntegrationSystemViewSet)
integration_router.register(r'gateways', integration_views.APIGatewayViewSet)
integration_router.register(r'routes', integration_views.APIRouteViewSet)
integration_router.register(r'sync-rules', integration_views.DataSyncRuleViewSet)
integration_router.register(r'sync-logs', integration_views.SyncLogViewSet)
integration_router.register(r'api-monitors', integration_views.APIMonitorViewSet)
integration_router.register(r'integration-configs', integration_views.IntegrationConfigViewSet)
integration_router.register(r'dashboard', integration_views.IntegrationDashboardViewSet, basename='integration-dashboard')

# 权限管理路由
permission_router = DefaultRouter()
permission_router.register(r'permissions', permission_views.PermissionViewSet)
permission_router.register(r'roles', permission_views.RoleViewSet)
permission_router.register(r'user-roles', permission_views.UserRoleViewSet)
permission_router.register(r'data-permissions', permission_views.DataPermissionViewSet)
permission_router.register(r'field-permissions', permission_views.FieldPermissionViewSet)
permission_router.register(r'department-permissions', permission_views.DepartmentPermissionViewSet)
permission_router.register(r'permission-logs', permission_views.PermissionLogViewSet)
permission_router.register(r'dashboard', permission_views.PermissionDashboardViewSet, basename='permission-dashboard')

urlpatterns = [
    path('api/', include(router.urls)),
    # 系统集成API
    path('integration/', include(integration_router.urls)),
    # 权限管理API
    path('permission/', include(permission_router.urls)),
    # 绩效考核系统代理API
    path('performance-api/stats/overview/', views.performance_overview_stats, name='performance_overview_stats'),
    path('performance-api/stats/cycle/<int:cycle_id>/', views.performance_cycle_stats, name='performance_cycle_stats'),
    # 部门导入和模板下载API
    path('api/departments-template/', DownloadTemplateView.as_view(), name='download_template'),
    path('api/departments-import/', ImportDepartmentsView.as_view(), name='import_departments'),
]