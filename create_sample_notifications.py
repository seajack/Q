#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
sys.path.append('org-platform/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'org_platform.settings')
django.setup()

from organizations.notification_models import Notification
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def create_sample_notifications():
    print("=== 创建示例通知数据 ===")
    
    # 获取或创建用户
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': '管理员',
            'last_name': '用户'
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"创建用户: {user.username}")
    else:
        print(f"使用现有用户: {user.username}")
    
    # 创建示例通知
    notifications_data = [
        {
            'title': '系统更新通知',
            'message': '系统已更新到最新版本，新增了智能分析功能',
            'notification_type': 'info',
            'priority': 'medium',
            'is_read': False,
            'created_at': timezone.now() - timedelta(hours=2)
        },
        {
            'title': '数据同步异常',
            'message': '绩效考核系统数据同步出现异常，请检查连接状态',
            'notification_type': 'warning',
            'priority': 'high',
            'is_read': False,
            'created_at': timezone.now() - timedelta(hours=4)
        },
        {
            'title': '员工入职完成',
            'message': '新员工张三的入职流程已完成，请分配相关权限',
            'notification_type': 'success',
            'priority': 'medium',
            'is_read': True,
            'created_at': timezone.now() - timedelta(days=1)
        },
        {
            'title': '系统维护通知',
            'message': '系统将于今晚22:00-24:00进行维护，期间可能无法正常访问',
            'notification_type': 'info',
            'priority': 'high',
            'is_read': False,
            'created_at': timezone.now() - timedelta(hours=1)
        },
        {
            'title': '权限变更提醒',
            'message': '您的权限已更新，新增了数据导出功能',
            'notification_type': 'success',
            'priority': 'low',
            'is_read': True,
            'created_at': timezone.now() - timedelta(days=2)
        }
    ]
    
    created_count = 0
    for data in notifications_data:
        notification, created = Notification.objects.get_or_create(
            recipient=user,
            title=data['title'],
            defaults={
                'message': data['message'],
                'notification_type': data['notification_type'],
                'priority': data['priority'],
                'is_read': data['is_read'],
                'created_at': data['created_at']
            }
        )
        if created:
            created_count += 1
            print(f"创建通知: {notification.title}")
        else:
            print(f"通知已存在: {notification.title}")
    
    print(f"\n总共创建了 {created_count} 条新通知")
    print(f"用户 {user.username} 现在有 {Notification.objects.filter(recipient=user).count()} 条通知")

if __name__ == "__main__":
    create_sample_notifications()
