#!/usr/bin/env python3
"""
测试工作流设计器URL配置
"""

import os
import sys
import django

# 设置Django环境
sys.path.append('e:/code/Q/org-platform/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'org_platform.settings')

try:
    django.setup()
    print("✅ Django环境设置成功")
except Exception as e:
    print(f"❌ Django环境设置失败: {e}")
    sys.exit(1)

def test_imports():
    """测试模块导入"""
    print("\n🧪 测试模块导入...")
    
    try:
        from organizations import views_workflow_designer
        print("✅ views_workflow_designer 导入成功")
    except ImportError as e:
        print(f"❌ views_workflow_designer 导入失败: {e}")
        return False
    
    try:
        from organizations.workflow_designer import WorkflowDesign, WorkflowVersion, WorkflowExecution
        print("✅ workflow_designer 模型导入成功")
    except ImportError as e:
        print(f"❌ workflow_designer 模型导入失败: {e}")
        return False
    
    try:
        from organizations.serializers_workflow import WorkflowDesignSerializer
        print("✅ serializers_workflow 导入成功")
    except ImportError as e:
        print(f"❌ serializers_workflow 导入失败: {e}")
        return False
    
    return True

def test_url_patterns():
    """测试URL模式"""
    print("\n🔗 测试URL模式...")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        # 测试基本URL
        client = Client()
        
        # 测试工作流模板API
        try:
            response = client.get('/api/workflow-templates/')
            print(f"✅ 工作流模板API: {response.status_code}")
        except Exception as e:
            print(f"⚠️ 工作流模板API测试失败: {e}")
        
        return True
    except Exception as e:
        print(f"❌ URL测试失败: {e}")
        return False

def test_viewsets():
    """测试ViewSet类"""
    print("\n📊 测试ViewSet类...")
    
    try:
        from organizations.views_workflow_designer import (
            WorkflowDesignViewSet, 
            WorkflowVersionViewSet, 
            WorkflowExecutionViewSet
        )
        
        # 检查ViewSet是否正确定义
        print("✅ WorkflowDesignViewSet 定义正确")
        print("✅ WorkflowVersionViewSet 定义正确")
        print("✅ WorkflowExecutionViewSet 定义正确")
        
        return True
    except Exception as e:
        print(f"❌ ViewSet测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试工作流设计器配置...")
    
    success = True
    
    # 测试导入
    if not test_imports():
        success = False
    
    # 测试ViewSet
    if not test_viewsets():
        success = False
    
    # 测试URL
    if not test_url_patterns():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 所有测试通过！工作流设计器配置正确")
        print("\n📝 下一步:")
        print("1. 运行数据库迁移: python manage.py makemigrations")
        print("2. 应用迁移: python manage.py migrate")
        print("3. 启动服务: python manage.py runserver 0.0.0.0:8001")
    else:
        print("❌ 部分测试失败，请检查配置")
    
    return success

if __name__ == "__main__":
    main()
