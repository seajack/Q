"""
消息通知数据模型
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Notification(models.Model):
    """消息通知模型"""
    NOTIFICATION_TYPES = [
        ('info', '信息'),
        ('warning', '警告'),
        ('success', '成功'),
        ('error', '错误'),
        ('system', '系统'),
        ('workflow', '工作流'),
        ('integration', '集成'),
        ('permission', '权限'),
    ]

    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=200)
    message = models.TextField('消息内容')
    notification_type = models.CharField('通知类型', max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField('优先级', max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # 接收者
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='接收者', related_name='notifications')
    
    # 状态
    is_read = models.BooleanField('是否已读', default=False)
    is_deleted = models.BooleanField('是否已删除', default=False)
    
    # 关联数据
    related_object_type = models.CharField('关联对象类型', max_length=50, blank=True)
    related_object_id = models.CharField('关联对象ID', max_length=100, blank=True)
    
    # 额外数据
    extra_data = models.JSONField('额外数据', default=dict, blank=True)
    
    # 时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)

    class Meta:
        verbose_name = '消息通知'
        verbose_name_plural = '消息通知'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
            models.Index(fields=['notification_type', 'priority']),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

    def mark_as_read(self):
        """标记为已读"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def is_expired(self):
        """检查是否过期"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @classmethod
    def create_notification(cls, recipient, title, message, notification_type='info', 
                          priority='medium', related_object_type=None, related_object_id=None, 
                          extra_data=None, expires_at=None):
        """创建通知的便捷方法"""
        return cls.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
            extra_data=extra_data or {},
            expires_at=expires_at
        )


class NotificationTemplate(models.Model):
    """通知模板模型"""
    name = models.CharField('模板名称', max_length=100)
    code = models.CharField('模板编码', max_length=50, unique=True)
    title_template = models.CharField('标题模板', max_length=200)
    message_template = models.TextField('消息模板')
    notification_type = models.CharField('通知类型', max_length=20, choices=Notification.NOTIFICATION_TYPES)
    priority = models.CharField('优先级', max_length=10, choices=Notification.PRIORITY_CHOICES, default='medium')
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '通知模板'
        verbose_name_plural = '通知模板'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def render_notification(self, context=None):
        """渲染通知内容"""
        context = context or {}
        return {
            'title': self.title_template.format(**context),
            'message': self.message_template.format(**context),
            'notification_type': self.notification_type,
            'priority': self.priority
        }
