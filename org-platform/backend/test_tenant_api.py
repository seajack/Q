#!/usr/bin/env python
"""
测试多租户管理API
"""
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

def test_tenant_api():
    """测试租户管理API"""
    print("开始测试多租户管理API...")
    
    # 测试租户列表API
    try:
        response = requests.get(f"{BASE_URL}/api/tenant/tenants/")
        print(f"租户列表API状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"租户列表数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"API错误: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"测试失败: {e}")

def test_tenant_models():
    """测试租户模型"""
    print("\n开始测试租户模型...")
    
    try:
        import os
        import sys
        import django
        
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'org_platform.settings')
        sys.path.append('.')
        django.setup()
        
        from organizations.tenant_models import Tenant, TenantUser, TenantSettings
        
        # 检查模型是否正确导入
        print("✓ 租户模型导入成功")
        
        # 检查数据库表是否存在
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%tenant%'")
            tables = cursor.fetchall()
            print(f"租户相关表: {[table[0] for table in tables]}")
            
    except Exception as e:
        print(f"模型测试失败: {e}")

if __name__ == "__main__":
    test_tenant_models()
    test_tenant_api()
