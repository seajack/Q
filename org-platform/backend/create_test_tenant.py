#!/usr/bin/env python
"""
创建测试租户数据
"""
import os
import sys
import django
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'org_platform.settings')
sys.path.append('.')
django.setup()

from organizations.tenant_models import Tenant, TenantUser, TenantSettings, TenantSubscription
from django.contrib.auth.models import User

def create_test_tenant():
    """创建测试租户"""
    print("开始创建测试租户...")
    
    try:
        # 检查是否已存在测试租户
        tenant = Tenant.objects.filter(code="TEST001").first()
        if tenant:
            print(f"测试租户已存在: {tenant.name}")
        else:
            # 创建测试租户
            tenant = Tenant.objects.create(
                name="测试租户",
                code="TEST001",
                domain="test.example.com",
                description="这是一个测试租户",
                status="active",
                max_users=100,
                max_departments=50,
                max_employees=1000,
                contact_name="测试管理员",
                contact_email="admin@test.com",
                contact_phone="13800138000",
                expires_at=datetime.now() + timedelta(days=365)
            )
            print(f"创建租户成功: {tenant.name}")
        
        # 创建或获取租户设置
        settings, created = TenantSettings.objects.get_or_create(
            tenant=tenant,
            defaults={
                'timezone': "Asia/Shanghai",
                'language': "zh-cn",
                'company_name': "测试公司",
                'company_address': "北京市朝阳区测试大厦",
                'enable_employee_self_service': True,
                'enable_workflow_approval': True,
                'enable_integration_api': True
            }
        )
        if created:
            print(f"创建租户设置成功")
        else:
            print(f"租户设置已存在")
        
        # 创建或获取租户订阅
        subscription, created = TenantSubscription.objects.get_or_create(
            tenant=tenant,
            defaults={
                'plan': "professional",
                'status': "active",
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=365),
                'max_users': 100,
                'max_departments': 50,
                'max_employees': 1000
            }
        )
        if created:
            print(f"创建租户订阅成功")
        else:
            print(f"租户订阅已存在")
        
        # 创建或获取测试用户
        user, created = User.objects.get_or_create(
            username="testuser",
            defaults={
                'email': 'test@example.com',
                'first_name': '测试',
                'last_name': '用户'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"创建测试用户成功")
        else:
            print(f"测试用户已存在")
        
        # 创建租户用户关联
        tenant_user, created = TenantUser.objects.get_or_create(
            tenant=tenant,
            user=user,
            defaults={
                'role': 'admin',
                'is_active': True,
                'can_manage_users': True,
                'can_manage_departments': True,
                'can_manage_employees': True,
                'can_view_reports': True
            }
        )
        if created:
            print(f"创建租户用户关联成功")
        else:
            print(f"租户用户关联已存在")
        
        print(f"\n测试租户创建完成!")
        print(f"租户ID: {tenant.id}")
        print(f"租户名称: {tenant.name}")
        print(f"租户代码: {tenant.code}")
        print(f"域名: {tenant.domain}")
        
    except Exception as e:
        print(f"创建测试租户失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_tenant()
