"""
系统健康检查视图
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.conf import settings
import json

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """系统健康检查"""
    try:
        # 检查数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # 检查基本信息
    health_data = {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": "2025-09-29T14:25:00Z",
        "services": {
            "database": db_status,
            "django": "healthy"
        },
        "version": "1.0.0",
        "debug": settings.DEBUG
    }
    
    status_code = 200 if health_data["status"] == "healthy" else 503
    return JsonResponse(health_data, status=status_code)

@csrf_exempt
@require_http_methods(["GET"])
def api_status(request):
    """API状态检查"""
    return JsonResponse({
        "message": "API is running",
        "endpoints": {
            "departments": "/api/departments/",
            "employees": "/api/employees/",
            "workflow": "/workflow/workflow-designs/",
            "intelligence": "/api/intelligence/analysis/",
            "permissions": "/api/permission/permissions/",
            "integration": "/api/integration/systems/"
        },
        "status": "active"
    })
