"""
初始化常用工作流规则
"""

from django.core.management.base import BaseCommand
from organizations.models import WorkflowRule
import json


class Command(BaseCommand):
    help = '初始化常用工作流规则'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化工作流规则...')
        
        # 预置工作流规则数据
        workflow_rules = [
            {
                'name': '新员工入职流程',
                'code': 'employee_onboarding',
                'description': '新员工入职的完整流程，包括信息收集、部门确认、权限分配等步骤',
                'rule_type': 'employee_management',
                'trigger_conditions': {
                    'event_type': 'data_change',
                    'table': 'employees',
                    'operation': 'insert',
                    'conditions': [
                        {
                            'field': 'status',
                            'operator': 'equals',
                            'value': 'pending'
                        },
                        {
                            'field': 'employee_type',
                            'operator': 'equals',
                            'value': 'new_hire'
                        }
                    ]
                },
                'execution_actions': [
                    {
                        'action': 'start_workflow',
                        'workflow_id': 'employee_onboarding_workflow',
                        'parameters': {
                            'employee_id': '{{record.id}}',
                            'department_id': '{{record.department_id}}',
                            'manager_id': '{{record.manager_id}}'
                        }
                    },
                    {
                        'action': 'send_notification',
                        'template': 'workflow_started',
                        'recipients': ['hr@company.com']
                    }
                ],
                'is_active': True,
                'priority': 1
            },
            {
                'name': '员工离职流程',
                'code': 'employee_offboarding',
                'description': '员工离职的完整流程，包括工作交接、权限回收、设备归还等步骤',
                'rule_type': 'employee_management',
                'trigger_conditions': {
                    'event_type': 'data_change',
                    'table': 'employees',
                    'operation': 'update',
                    'conditions': [
                        {
                            'field': 'status',
                            'operator': 'equals',
                            'value': 'resigned'
                        }
                    ]
                },
                'execution_actions': [
                    {
                        'action': 'start_workflow',
                        'workflow_id': 'employee_offboarding_workflow',
                        'parameters': {
                            'employee_id': '{{record.id}}',
                            'department_id': '{{record.department_id}}',
                            'manager_id': '{{record.manager_id}}'
                        }
                    },
                    {
                        'action': 'send_notification',
                        'template': 'offboarding_started',
                        'recipients': ['hr@company.com', '{{record.manager.email}}']
                    }
                ],
                'is_active': True,
                'priority': 1
            },
            {
                'name': '部门重组流程',
                'code': 'department_reorganization',
                'description': '部门重组时的自动化流程，包括员工重新分配、权限调整等',
                'rule_type': 'department_management',
                'trigger_conditions': {
                    'event_type': 'data_change',
                    'table': 'departments',
                    'operation': 'update',
                    'conditions': [
                        {
                            'field': 'status',
                            'operator': 'equals',
                            'value': 'reorganizing'
                        }
                    ]
                },
                'execution_actions': [
                    {
                        'action': 'start_workflow',
                        'workflow_id': 'department_reorganization_workflow',
                        'parameters': {
                            'department_id': '{{record.id}}',
                            'old_structure': '{{record.old_structure}}',
                            'new_structure': '{{record.new_structure}}'
                        }
                    },
                    {
                        'action': 'send_notification',
                        'template': 'reorganization_started',
                        'recipients': ['hr@company.com', 'management@company.com']
                    }
                ],
                'is_active': True,
                'priority': 2
            },
            {
                'name': '职位调整流程',
                'code': 'position_adjustment',
                'description': '员工职位调整的审批流程，包括薪资调整、权限变更等',
                'rule_type': 'position_management',
                'trigger_conditions': {
                    'event_type': 'data_change',
                    'table': 'employees',
                    'operation': 'update',
                    'conditions': [
                        {
                            'field': 'position_id',
                            'operator': 'changed'
                        },
                        {
                            'field': 'status',
                            'operator': 'equals',
                            'value': 'active'
                        }
                    ]
                },
                'execution_actions': [
                    {
                        'action': 'start_workflow',
                        'workflow_id': 'position_adjustment_workflow',
                        'parameters': {
                            'employee_id': '{{record.id}}',
                            'old_position': '{{record.old_position}}',
                            'new_position': '{{record.new_position}}',
                            'department_id': '{{record.department_id}}'
                        }
                    },
                    {
                        'action': 'send_notification',
                        'template': 'position_adjustment_started',
                        'recipients': ['hr@company.com', '{{record.manager.email}}']
                    }
                ],
                'is_active': True,
                'priority': 2
            },
            {
                'name': '权限变更流程',
                'code': 'permission_change',
                'description': '用户权限变更的审批流程，确保权限变更的合规性',
                'rule_type': 'permission_management',
                'trigger_conditions': {
                    'event_type': 'data_change',
                    'table': 'user_roles',
                    'operation': 'insert',
                    'conditions': [
                        {
                            'field': 'role.level',
                            'operator': 'gte',
                            'value': 5
                        }
                    ]
                },
                'execution_actions': [
                    {
                        'action': 'start_workflow',
                        'workflow_id': 'permission_change_workflow',
                        'parameters': {
                            'user_id': '{{record.user_id}}',
                            'role_id': '{{record.role_id}}',
                            'granted_by': '{{record.granted_by}}'
                        }
                    },
                    {
                        'action': 'send_notification',
                        'template': 'permission_change_started',
                        'recipients': ['security@company.com', 'hr@company.com']
                    }
                ],
                'is_active': True,
                'priority': 3
            },
            {
                'name': '数据同步规则',
                'code': 'data_sync_rule',
                'description': '与第三方系统数据同步的自动化规则',
                'rule_type': 'integration',
                'trigger_conditions': {
                    'event_type': 'scheduled',
                    'schedule': 'daily',
                    'time': '02:00'
                },
                'execution_actions': [
                    {
                        'action': 'start_workflow',
                        'workflow_id': 'data_sync_workflow',
                        'parameters': {
                            'sync_type': 'full',
                            'source_systems': ['hr_system', 'erp_system']
                        }
                    },
                    {
                        'action': 'log_activity',
                        'message': '数据同步任务已启动'
                    }
                ],
                'is_active': True,
                'priority': 4
            },
            {
                'name': '异常数据检测',
                'code': 'data_anomaly_detection',
                'description': '检测组织架构数据异常并自动处理',
                'rule_type': 'data_quality',
                'trigger_conditions': {
                    'event_type': 'data_validation',
                    'conditions': [
                        {
                            'field': 'employee.department_id',
                            'operator': 'is_null'
                        },
                        {
                            'field': 'employee.manager_id',
                            'operator': 'is_null'
                        }
                    ]
                },
                'execution_actions': [
                    {
                        'action': 'send_alert',
                        'template': 'data_anomaly_detected',
                        'recipients': ['admin@company.com', 'hr@company.com']
                    },
                    {
                        'action': 'create_ticket',
                        'ticket_type': 'data_quality',
                        'priority': 'high'
                    }
                ],
                'is_active': True,
                'priority': 5
            },
            {
                'name': '月度报告生成',
                'code': 'monthly_report_generation',
                'description': '自动生成月度组织架构报告',
                'rule_type': 'reporting',
                'trigger_conditions': {
                    'event_type': 'scheduled',
                    'schedule': 'monthly',
                    'day': 1,
                    'time': '09:00'
                },
                'execution_actions': [
                    {
                        'action': 'start_workflow',
                        'workflow_id': 'monthly_report_workflow',
                        'parameters': {
                            'report_type': 'organization_structure',
                            'period': 'previous_month'
                        }
                    },
                    {
                        'action': 'send_notification',
                        'template': 'monthly_report_generated',
                        'recipients': ['management@company.com']
                    }
                ],
                'is_active': True,
                'priority': 6
            }
        ]

        # 创建或更新工作流规则
        for rule_data in workflow_rules:
            rule, created = WorkflowRule.objects.get_or_create(
                code=rule_data['code'],
                defaults={
                    'name': rule_data['name'],
                    'description': rule_data['description'],
                    'rule_type': rule_data['rule_type'],
                    'trigger_conditions': rule_data['trigger_conditions'],
                    'execution_actions': rule_data['execution_actions'],
                    'is_active': rule_data['is_active'],
                    'priority': rule_data['priority']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 创建工作流规则: {rule.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ 工作流规则已存在: {rule.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'✓ 工作流规则初始化完成，共处理 {len(workflow_rules)} 个规则')
        )
