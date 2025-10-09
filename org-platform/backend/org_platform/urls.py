"""
URL configuration for org_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('organizations.urls')),
    path('api/tenant/', include('organizations.tenant_urls')),  # 多租户API
    path('api/', include('organizations.intelligence_urls')),  # 智能分析API
    path('api/', include('organizations.simple_intelligence_urls')),  # 简单智能分析API
    path('api/', include('organizations.simple_integration_urls')),  # 简单集成管理API
    path('api/', include('organizations.simple_permission_urls')),  # 简单权限管理API
    path('api/', include('organizations.workflow_urls')),  # 工作流管理API
    path('api/', include('organizations.test_urls')),  # 测试API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
