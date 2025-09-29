#!/usr/bin/env python3
"""
工作流设计器安装和配置脚本
"""

import os
import sys
import django

# 设置Django环境
sys.path.append('e:/code/Q/org-platform/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'org_platform.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from organizations.workflow_designer import WorkflowDesign, WorkflowDesigner

def setup_workflow_designer():
    """设置工作流设计器"""
    print("🚀 开始设置工作流设计器...")
    
    # 1. 创建数据库迁移
    print("📊 创建数据库迁移...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations', 'organizations'])
        print("✅ 迁移文件创建成功")
    except Exception as e:
        print(f"⚠️ 迁移文件创建可能有问题: {e}")
    
    # 2. 执行迁移
    print("🔄 执行数据库迁移...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ 数据库迁移成功")
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return
    
    # 3. 创建测试用户（如果不存在）
    print("👤 创建测试用户...")
    if not User.objects.filter(username='workflow_admin').exists():
        user = User.objects.create_user(
            username='workflow_admin',
            email='workflow@example.com',
            password='workflow123'
        )
        print("✅ 测试用户创建成功: workflow_admin / workflow123")
    else:
        user = User.objects.get(username='workflow_admin')
        print("✅ 测试用户已存在")
    
    # 4. 创建示例工作流
    print("📋 创建示例工作流...")
    create_sample_workflows(user)
    
    print("\n🎉 工作流设计器设置完成！")
    print("\n📝 使用说明:")
    print("1. 启动后端服务: cd backend && python manage.py runserver 0.0.0.0:8001")
    print("2. 启动前端服务: cd frontend && npm run dev")
    print("3. 访问工作流设计器: http://localhost:3000/workflow-designer")
    print("4. 测试用户: workflow_admin / workflow123")

def create_sample_workflows(user):
    """创建示例工作流"""
    
    # 示例1: 请假审批流程
    if not WorkflowDesign.objects.filter(name='请假审批流程').exists():
        designer = WorkflowDesigner()
        workflow = designer.create_workflow(
            name='请假审批流程',
            description='员工请假申请的标准审批流程',
            user=user
        )
        
        # 添加节点
        workflow.nodes = [
            {
                'node_id': 'start_1',
                'node_type': 'start',
                'name': '提交申请',
                'x': 100,
                'y': 200,
                'config': {}
            },
            {
                'node_id': 'approval_1',
                'node_type': 'approval',
                'name': '直接上级审批',
                'x': 300,
                'y': 200,
                'config': {
                    'approver': 'direct_supervisor',
                    'timeout': 24,
                    'required': True
                }
            },
            {
                'node_id': 'condition_1',
                'node_type': 'condition',
                'name': '请假天数判断',
                'x': 500,
                'y': 200,
                'config': {
                    'condition': 'days > 3',
                    'operator': 'greater_than',
                    'value': 3
                }
            },
            {
                'node_id': 'approval_2',
                'node_type': 'approval',
                'name': 'HR审批',
                'x': 700,
                'y': 150,
                'config': {
                    'approver': 'hr_manager',
                    'timeout': 48,
                    'required': True
                }
            },
            {
                'node_id': 'notification_1',
                'node_type': 'notification',
                'name': '结果通知',
                'x': 900,
                'y': 200,
                'config': {
                    'type': 'email',
                    'template': 'leave_approval_result',
                    'recipients': ['applicant', 'supervisor']
                }
            },
            {
                'node_id': 'end_1',
                'node_type': 'end',
                'name': '流程结束',
                'x': 1100,
                'y': 200,
                'config': {}
            }
        ]
        
        # 添加连接
        workflow.connections = [
            {
                'connection_id': 'conn_1',
                'source_id': 'start_1',
                'target_id': 'approval_1',
                'connection_type': 'default'
            },
            {
                'connection_id': 'conn_2',
                'source_id': 'approval_1',
                'target_id': 'condition_1',
                'connection_type': 'success',
                'label': '审批通过'
            },
            {
                'connection_id': 'conn_3',
                'source_id': 'condition_1',
                'target_id': 'approval_2',
                'connection_type': 'success',
                'label': '超过3天'
            },
            {
                'connection_id': 'conn_4',
                'source_id': 'condition_1',
                'target_id': 'notification_1',
                'connection_type': 'failure',
                'label': '3天以内'
            },
            {
                'connection_id': 'conn_5',
                'source_id': 'approval_2',
                'target_id': 'notification_1',
                'connection_type': 'success',
                'label': 'HR审批通过'
            },
            {
                'connection_id': 'conn_6',
                'source_id': 'notification_1',
                'target_id': 'end_1',
                'connection_type': 'default'
            }
        ]
        
        workflow.status = 'active'
        workflow.save()
        
        print("✅ 创建示例工作流: 请假审批流程")
    
    # 示例2: 报销审批流程
    if not WorkflowDesign.objects.filter(name='报销审批流程').exists():
        designer = WorkflowDesigner()
        workflow = designer.create_workflow(
            name='报销审批流程',
            description='员工报销申请的审批流程',
            user=user
        )
        
        workflow.nodes = [
            {
                'node_id': 'start_1',
                'node_type': 'start',
                'name': '提交报销',
                'x': 100,
                'y': 200,
                'config': {}
            },
            {
                'node_id': 'data_1',
                'node_type': 'data',
                'name': '发票验证',
                'x': 300,
                'y': 200,
                'config': {
                    'validation_rules': ['invoice_format', 'amount_limit'],
                    'auto_process': True
                }
            },
            {
                'node_id': 'approval_1',
                'node_type': 'approval',
                'name': '财务审批',
                'x': 500,
                'y': 200,
                'config': {
                    'approver': 'finance_manager',
                    'timeout': 72,
                    'required': True
                }
            },
            {
                'node_id': 'notification_1',
                'node_type': 'notification',
                'name': '打款通知',
                'x': 700,
                'y': 200,
                'config': {
                    'type': 'system',
                    'template': 'payment_notification'
                }
            },
            {
                'node_id': 'end_1',
                'node_type': 'end',
                'name': '流程完成',
                'x': 900,
                'y': 200,
                'config': {}
            }
        ]
        
        workflow.connections = [
            {
                'connection_id': 'conn_1',
                'source_id': 'start_1',
                'target_id': 'data_1',
                'connection_type': 'default'
            },
            {
                'connection_id': 'conn_2',
                'source_id': 'data_1',
                'target_id': 'approval_1',
                'connection_type': 'success',
                'label': '验证通过'
            },
            {
                'connection_id': 'conn_3',
                'source_id': 'approval_1',
                'target_id': 'notification_1',
                'connection_type': 'success',
                'label': '审批通过'
            },
            {
                'connection_id': 'conn_4',
                'source_id': 'notification_1',
                'target_id': 'end_1',
                'connection_type': 'default'
            }
        ]
        
        workflow.status = 'active'
        workflow.save()
        
        print("✅ 创建示例工作流: 报销审批流程")

if __name__ == "__main__":
    setup_workflow_designer()
