"""
简单集成管理API视图
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class SimpleIntegrationViewSet(viewsets.ViewSet):
    """简单集成管理API"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def systems(self, request):
        """获取集成系统列表"""
        return Response([
            {
                'id': '1',
                'name': 'HR人力资源系统',
                'system_type': 'hr',
                'description': '企业人力资源管理系统',
                'api_endpoint': 'https://hr.example.com/api',
                'status': 'active',
                'is_active': True
            },
            {
                'id': '2',
                'name': 'ERP企业资源计划系统',
                'system_type': 'erp',
                'description': '企业资源计划管理系统',
                'api_endpoint': 'https://erp.example.com/api',
                'status': 'active',
                'is_active': True
            }
        ])

    @action(detail=False, methods=['get'])
    def gateways(self, request):
        """获取集成网关列表"""
        return Response([
            {
                'id': '1',
                'name': 'API网关',
                'gateway_type': 'api_gateway',
                'description': '统一API网关服务',
                'endpoint': 'https://gateway.example.com',
                'is_active': True
            }
        ])

    @action(detail=False, methods=['get'])
    def sync_rules(self, request):
        """获取同步规则列表"""
        return Response([
            {
                'id': '1',
                'name': '员工信息同步规则',
                'source_system': 'HR人力资源系统',
                'target_system': 'ERP企业资源计划系统',
                'sync_type': 'real_time',
                'sync_direction': 'bidirectional',
                'is_active': True
            }
        ])

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取集成管理统计信息"""
        return Response({
            'total_systems': 3,
            'active_systems': 2,
            'total_gateways': 2,
            'active_gateways': 2,
            'total_sync_rules': 2,
            'active_sync_rules': 2,
            'recent_sync_logs': 15,
            'success_rate': 95.5
        })
