"""
消息通知URL路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .notification_views import NotificationViewSet, NotificationTemplateViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)
router.register(r'notification-templates', NotificationTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
