from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from organizations.integration_models import IntegrationSystem, APIGateway, APIRoute, DataSyncRule
import json


class Command(BaseCommand):
    help = '初始化集成管理示例数据'

    def handle(self, *args, **options):
        # 获取或创建管理员用户
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('创建管理员用户: admin/admin123'))

        # 创建示例集成系统
        systems_data = [
            {
                'name': '绩效考核系统',
                'system_type': 'performance',
                'base_url': 'http://performance.example.com',
                'api_version': 'v1',
                'auth_type': 'token',
                'auth_config': {'token': 'performance_token_123'},
                'status': 'active',
                'description': '绩效考核系统集成'
            },
            {
                'name': 'OA办公系统',
                'system_type': 'oa',
                'base_url': 'http://oa.example.com',
                'api_version': 'v1',
                'auth_type': 'basic',
                'auth_config': {'username': 'api_user', 'password': 'api_password'},
                'status': 'active',
                'description': 'OA办公系统集成'
            },
            {
                'name': '财务系统',
                'system_type': 'finance',
                'base_url': 'http://finance.example.com',
                'api_version': 'v2',
                'auth_type': 'api_key',
                'auth_config': {'api_key': 'finance_api_key_456', 'key_name': 'X-API-Key'},
                'status': 'active',
                'description': '财务系统集成'
            }
        ]

        for system_data in systems_data:
            system, created = IntegrationSystem.objects.get_or_create(
                name=system_data['name'],
                defaults={
                    **system_data,
                    'created_by': admin_user,
                    'timeout': 30,
                    'retry_count': 3,
                    'rate_limit': 100,
                    'sync_enabled': True,
                    'sync_interval': 60,
                    'monitoring_enabled': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'创建集成系统: {system.name}'))

        # 创建示例API网关
        gateway, created = APIGateway.objects.get_or_create(
            name='主网关',
            defaults={
                'base_url': 'http://gateway.example.com',
                'description': '主要API网关',
                'rate_limit_enabled': True,
                'rate_limit_per_minute': 1000,
                'rate_limit_per_hour': 10000,
                'monitoring_enabled': True,
                'log_level': 'info',
                'cors_enabled': True,
                'cors_origins': ['http://localhost:3000', 'http://localhost:8080'],
                'api_key_required': False,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'创建API网关: {gateway.name}'))

        # 创建示例API路由
        routes_data = [
            {
                'name': '绩效考核API代理',
                'path': '/api/performance/*',
                'method': 'GET',
                'target_url': 'http://performance.example.com/api/*',
                'rate_limit': 200,
                'burst_limit': 400,
                'cache_enabled': True,
                'cache_ttl': 300,
                'auth_required': True,
                'is_active': True
            },
            {
                'name': 'OA系统API代理',
                'path': '/api/oa/*',
                'method': 'POST',
                'target_url': 'http://oa.example.com/api/*',
                'rate_limit': 100,
                'burst_limit': 200,
                'cache_enabled': False,
                'auth_required': True,
                'is_active': True
            }
        ]

        for route_data in routes_data:
            route, created = APIRoute.objects.get_or_create(
                gateway=gateway,
                path=route_data['path'],
                method=route_data['method'],
                defaults=route_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'创建API路由: {route.name}'))

        # 创建示例数据同步规则
        performance_system = IntegrationSystem.objects.get(name='绩效考核系统')
        oa_system = IntegrationSystem.objects.get(name='OA办公系统')

        sync_rules_data = [
            {
                'name': '员工数据同步到绩效考核系统',
                'source_system': oa_system,
                'target_system': performance_system,
                'sync_type': 'realtime',
                'status': 'active',
                'source_table': 'employees',
                'target_table': 'performance_employees',
                'field_mapping': {
                    'employee_id': 'id',
                    'name': 'name',
                    'department_id': 'department_id',
                    'position_id': 'position_id',
                    'email': 'email',
                    'phone': 'phone'
                },
                'batch_size': 100,
                'sync_interval': 30,
                'max_retry_count': 3,
                'data_cleaning_enabled': True,
                'cleaning_rules': [
                    {'field': 'name', 'type': 'trim'},
                    {'field': 'email', 'type': 'lowercase'}
                ],
                'validation_enabled': True,
                'validation_rules': [
                    {'field': 'name', 'type': 'required'},
                    {'field': 'email', 'type': 'email'}
                ],
                'monitoring_enabled': True,
                'alert_on_error': True,
                'alert_on_delay': True,
                'delay_threshold': 30,
                'description': '将OA系统的员工数据实时同步到绩效考核系统'
            },
            {
                'name': '部门数据批量同步',
                'source_system': oa_system,
                'target_system': performance_system,
                'sync_type': 'batch',
                'status': 'active',
                'source_table': 'departments',
                'target_table': 'performance_departments',
                'field_mapping': {
                    'dept_id': 'id',
                    'dept_name': 'name',
                    'parent_id': 'parent_id',
                    'manager_id': 'manager_id'
                },
                'batch_size': 50,
                'sync_interval': 60,
                'max_retry_count': 3,
                'data_cleaning_enabled': True,
                'cleaning_rules': [
                    {'field': 'dept_name', 'type': 'trim'}
                ],
                'validation_enabled': True,
                'validation_rules': [
                    {'field': 'dept_name', 'type': 'required'}
                ],
                'monitoring_enabled': True,
                'alert_on_error': True,
                'description': '将OA系统的部门数据批量同步到绩效考核系统'
            }
        ]

        for sync_rule_data in sync_rules_data:
            sync_rule, created = DataSyncRule.objects.get_or_create(
                name=sync_rule_data['name'],
                defaults={
                    **sync_rule_data,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'创建数据同步规则: {sync_rule.name}'))

        self.stdout.write(
            self.style.SUCCESS('集成管理示例数据初始化完成！')
        )
        self.stdout.write(
            self.style.WARNING('请访问 http://localhost:3000/integration-management 查看集成管理功能')
        )
