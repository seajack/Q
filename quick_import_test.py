#!/usr/bin/env python3
"""
快速导入测试
"""

import sys
import os

# 添加路径
sys.path.append('e:/code/Q/org-platform/backend')

print("🧪 测试工作流设计器模块导入...")

try:
    # 测试基本导入
    print("1. 测试基本Python导入...")
    
    # 检查文件是否存在
    workflow_designer_path = 'e:/code/Q/org-platform/backend/organizations/workflow_designer.py'
    views_workflow_path = 'e:/code/Q/org-platform/backend/organizations/views_workflow_designer.py'
    serializers_workflow_path = 'e:/code/Q/org-platform/backend/organizations/serializers_workflow.py'
    
    if os.path.exists(workflow_designer_path):
        print("✅ workflow_designer.py 文件存在")
    else:
        print("❌ workflow_designer.py 文件不存在")
    
    if os.path.exists(views_workflow_path):
        print("✅ views_workflow_designer.py 文件存在")
    else:
        print("❌ views_workflow_designer.py 文件不存在")
    
    if os.path.exists(serializers_workflow_path):
        print("✅ serializers_workflow.py 文件存在")
    else:
        print("❌ serializers_workflow.py 文件不存在")
    
    print("\n2. 测试Django设置...")
    
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'org_platform.settings')
    
    import django
    django.setup()
    print("✅ Django环境设置成功")
    
    print("\n3. 测试模块导入...")
    
    # 测试导入
    from organizations import views_workflow_designer
    print("✅ views_workflow_designer 导入成功")
    
    from organizations.workflow_designer import WorkflowDesign
    print("✅ WorkflowDesign 模型导入成功")
    
    from organizations.serializers_workflow import WorkflowDesignSerializer
    print("✅ WorkflowDesignSerializer 导入成功")
    
    print("\n🎉 所有导入测试通过！")
    
except Exception as e:
    print(f"\n❌ 导入测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n📝 如果导入成功，URL配置应该没有问题。")
print("现在可以尝试启动Django服务器进行测试。")
