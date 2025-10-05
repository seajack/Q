"""
消息通知视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .notification_models import Notification, NotificationTemplate
from .notification_serializers import (
    NotificationSerializer, NotificationCreateSerializer, 
    NotificationUpdateSerializer, NotificationTemplateSerializer,
    NotificationStatsSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """消息通知管理"""
    queryset = Notification.objects.filter(is_deleted=False)
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]  # 临时允许匿名访问，用于开发环境
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'priority', 'is_read', 'is_deleted']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'priority', 'is_read']
    ordering = ['-created_at']

    def get_queryset(self):
        """获取当前用户的通知"""
        # 在实际应用中，这里应该根据当前用户过滤
        # 现在暂时返回所有通知
        return Notification.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'create':
            return NotificationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NotificationUpdateSerializer
        return NotificationSerializer

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """标记为已读"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'message': '通知已标记为已读'})

    @action(detail=True, methods=['post'])
    def mark_as_unread(self, request, pk=None):
        """标记为未读"""
        notification = self.get_object()
        notification.is_read = False
        notification.read_at = None
        notification.save()
        return Response({'message': '通知已标记为未读'})

    @action(detail=True, methods=['post'])
    def delete_notification(self, request, pk=None):
        """删除通知"""
        notification = self.get_object()
        notification.is_deleted = True
        notification.save()
        return Response({'message': '通知已删除'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """全部标记为已读"""
        queryset = self.get_queryset().filter(is_read=False)
        updated_count = queryset.update(is_read=True, read_at=timezone.now())
        return Response({'message': f'已标记 {updated_count} 条通知为已读'})

    @action(detail=False, methods=['post'])
    def delete_all_read(self, request):
        """删除所有已读通知"""
        queryset = self.get_queryset().filter(is_read=True)
        deleted_count = queryset.update(is_deleted=True)
        return Response({'message': f'已删除 {deleted_count} 条已读通知'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取通知统计"""
        queryset = self.get_queryset()
        
        # 基本统计
        total_count = queryset.count()
        unread_count = queryset.filter(is_read=False).count()
        read_count = queryset.filter(is_read=True).count()
        
        # 按类型统计
        by_type = queryset.values('notification_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 按优先级统计
        by_priority = queryset.values('priority').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 最近通知
        recent_notifications = queryset[:10]
        
        stats_data = {
            'total_count': total_count,
            'unread_count': unread_count,
            'read_count': read_count,
            'by_type': {item['notification_type']: item['count'] for item in by_type},
            'by_priority': {item['priority']: item['count'] for item in by_priority},
            'recent_notifications': NotificationSerializer(recent_notifications, many=True).data
        }
        
        serializer = NotificationStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读通知数量"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """通知模板管理"""
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [AllowAny]  # 临时允许匿名访问，用于开发环境
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'priority', 'is_active']
    search_fields = ['name', 'code', 'title_template', 'message_template']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def test_template(self, request, pk=None):
        """测试模板"""
        template = self.get_object()
        context = request.data.get('context', {})
        rendered = template.render_notification(context)
        return Response(rendered)

    @action(detail=True, methods=['post'])
    def send_notification(self, request, pk=None):
        """使用模板发送通知"""
        template = self.get_object()
        recipient_id = request.data.get('recipient_id')
        context = request.data.get('context', {})
        
        if not recipient_id:
            return Response({'error': '缺少接收者ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.contrib.auth.models import User
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response({'error': '接收者不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 渲染通知内容
        rendered = template.render_notification(context)
        
        # 创建通知
        notification = Notification.create_notification(
            recipient=recipient,
            title=rendered['title'],
            message=rendered['message'],
            notification_type=rendered['notification_type'],
            priority=rendered['priority']
        )
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
