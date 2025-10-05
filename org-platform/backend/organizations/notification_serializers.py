"""
消息通知序列化器
"""

from rest_framework import serializers
from .notification_models import Notification, NotificationTemplate
from django.contrib.auth.models import User


class NotificationSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    recipient_name = serializers.CharField(source='recipient.username', read_only=True)
    is_expired = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'notification_type_display',
            'priority', 'priority_display', 'recipient', 'recipient_name',
            'is_read', 'is_deleted', 'related_object_type', 'related_object_id',
            'extra_data', 'created_at', 'read_at', 'expires_at', 'is_expired', 'time_ago'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']

    def get_is_expired(self, obj):
        """检查是否过期"""
        return obj.is_expired()

    def get_time_ago(self, obj):
        """获取相对时间"""
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}小时前"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"


class NotificationCreateSerializer(serializers.ModelSerializer):
    """创建通知序列化器"""
    
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'notification_type', 'priority',
            'recipient', 'related_object_type', 'related_object_id',
            'extra_data', 'expires_at'
        ]

    def create(self, validated_data):
        """创建通知"""
        return Notification.objects.create(**validated_data)


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """更新通知序列化器"""
    
    class Meta:
        model = Notification
        fields = ['is_read', 'is_deleted']

    def update(self, instance, validated_data):
        """更新通知"""
        if validated_data.get('is_read') and not instance.is_read:
            instance.mark_as_read()
        else:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """通知模板序列化器"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'code', 'title_template', 'message_template',
            'notification_type', 'notification_type_display',
            'priority', 'priority_display', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationStatsSerializer(serializers.Serializer):
    """通知统计序列化器"""
    total_count = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    read_count = serializers.IntegerField()
    by_type = serializers.DictField()
    by_priority = serializers.DictField()
    recent_notifications = NotificationSerializer(many=True)
