from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q
from .integration_models import (
    IntegrationSystem, APIGateway, APIRoute, DataSyncRule, 
    SyncLog, APIMonitor, IntegrationConfig
)
from .integration_services import (
    IntegrationService, APIGatewayService, DataSyncService, IntegrationMonitorService
)
from .serializers import (
    IntegrationSystemSerializer, APIGatewaySerializer, APIRouteSerializer,
    DataSyncRuleSerializer, SyncLogSerializer, APIMonitorSerializer,
    IntegrationConfigSerializer
)
import logging

logger = logging.getLogger(__name__)


class IntegrationSystemViewSet(viewsets.ModelViewSet):
    """集成系统管理"""
    queryset = IntegrationSystem.objects.all()
    serializer_class = IntegrationSystemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['system_type', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """测试连接"""
        system = self.get_object()
        try:
            service = IntegrationService(system)
            result = service.test_connection()
            return Response(result)
        except Exception as e:
            logger.error(f"测试连接失败: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def sync_employees(self, request, pk=None):
        """同步员工数据"""
        system = self.get_object()
        employees_data = request.data.get('employees', [])
        
        try:
            service = IntegrationService(system)
            result = service.sync_employees(employees_data)
            return Response(result)
        except Exception as e:
            logger.error(f"同步员工数据失败: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def sync_departments(self, request, pk=None):
        """同步部门数据"""
        system = self.get_object()
        departments_data = request.data.get('departments', [])
        
        try:
            service = IntegrationService(system)
            result = service.sync_departments(departments_data)
            return Response(result)
        except Exception as e:
            logger.error(f"同步部门数据失败: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def health_status(self, request, pk=None):
        """获取健康状态"""
        system = self.get_object()
        try:
            health = IntegrationMonitorService.get_system_health(system)
            return Response(health)
        except Exception as e:
            logger.error(f"获取健康状态失败: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class APIGatewayViewSet(viewsets.ModelViewSet):
    """API网关管理"""
    queryset = APIGateway.objects.all()
    serializer_class = APIGatewaySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['get'])
    def routes(self, request, pk=None):
        """获取网关路由"""
        gateway = self.get_object()
        routes = APIRoute.objects.filter(gateway=gateway, is_active=True)
        serializer = APIRouteSerializer(routes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取网关统计"""
        gateway = self.get_object()
        routes = APIRoute.objects.filter(gateway=gateway)
        
        total_routes = routes.count()
        active_routes = routes.filter(is_active=True).count()
        
        # 获取最近24小时的监控数据
        recent_monitors = APIMonitor.objects.filter(
            route__gateway=gateway,
            timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
        )
        
        total_requests = sum(monitor.request_count for monitor in recent_monitors)
        total_success = sum(monitor.success_count for monitor in recent_monitors)
        total_errors = sum(monitor.error_count for monitor in recent_monitors)
        
        return Response({
            'total_routes': total_routes,
            'active_routes': active_routes,
            'total_requests': total_requests,
            'success_requests': total_success,
            'error_requests': total_errors,
            'success_rate': (total_success / total_requests * 100) if total_requests > 0 else 0
        })


class APIRouteViewSet(viewsets.ModelViewSet):
    """API路由管理"""
    queryset = APIRoute.objects.all()
    serializer_class = APIRouteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['gateway', 'method', 'is_active']
    search_fields = ['name', 'path']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def test_route(self, request, pk=None):
        """测试路由"""
        route = self.get_object()
        test_data = request.data.get('data', {})
        
        try:
            gateway_service = APIGatewayService(route.gateway)
            result = gateway_service.route_request(route, test_data)
            return Response(result)
        except Exception as e:
            logger.error(f"测试路由失败: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取路由统计"""
        route = self.get_object()
        try:
            stats = IntegrationMonitorService.get_api_statistics(route)
            return Response(stats)
        except Exception as e:
            logger.error(f"获取路由统计失败: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataSyncRuleViewSet(viewsets.ModelViewSet):
    """数据同步规则管理"""
    queryset = DataSyncRule.objects.all()
    serializer_class = DataSyncRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sync_type', 'status', 'source_system', 'target_system']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def execute_sync(self, request, pk=None):
        """执行同步"""
        sync_rule = self.get_object()
        
        try:
            sync_service = DataSyncService(sync_rule)
            result = sync_service.execute_sync()
            return Response(result)
        except Exception as e:
            logger.error(f"执行同步失败: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def sync_logs(self, request, pk=None):
        """获取同步日志"""
        sync_rule = self.get_object()
        logs = SyncLog.objects.filter(sync_rule=sync_rule).order_by('-created_at')[:50]
        serializer = SyncLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取同步统计"""
        sync_rule = self.get_object()
        try:
            stats = IntegrationMonitorService.get_sync_statistics(sync_rule)
            return Response(stats)
        except Exception as e:
            logger.error(f"获取同步统计失败: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def sync_status(self, request):
        """获取所有同步规则状态"""
        rules = DataSyncRule.objects.filter(status='active')
        status_list = []
        
        for rule in rules:
            try:
                stats = IntegrationMonitorService.get_sync_statistics(rule)
                status_list.append({
                    'id': rule.id,
                    'name': rule.name,
                    'source_system': rule.source_system.name,
                    'target_system': rule.target_system.name,
                    'last_sync': rule.source_system.last_sync_time,
                    'status': rule.status,
                    'statistics': stats
                })
            except Exception as e:
                logger.error(f"获取同步状态失败: {str(e)}")
        
        return Response(status_list)


class SyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """同步日志查看"""
    queryset = SyncLog.objects.all()
    serializer_class = SyncLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sync_rule', 'status']
    search_fields = ['error_message']
    ordering_fields = ['created_at', 'start_time']
    ordering = ['-created_at']


class APIMonitorViewSet(viewsets.ReadOnlyModelViewSet):
    """API监控查看"""
    queryset = APIMonitor.objects.all()
    serializer_class = APIMonitorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['route']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


class IntegrationConfigViewSet(viewsets.ModelViewSet):
    """集成配置管理"""
    queryset = IntegrationConfig.objects.all()
    serializer_class = IntegrationConfigSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['system', 'config_type', 'is_active']
    search_fields = ['config_key', 'description']
    ordering_fields = ['created_at', 'config_key']
    ordering = ['system', 'config_key']


class IntegrationDashboardViewSet(viewsets.ViewSet):
    """集成仪表板"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取概览数据"""
        try:
            # 系统统计
            total_systems = IntegrationSystem.objects.count()
            active_systems = IntegrationSystem.objects.filter(status='active').count()
            
            # 同步规则统计
            total_sync_rules = DataSyncRule.objects.count()
            active_sync_rules = DataSyncRule.objects.filter(status='active').count()
            
            # 最近同步统计
            recent_syncs = SyncLog.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            )
            total_syncs = recent_syncs.count()
            successful_syncs = recent_syncs.filter(status='success').count()
            
            # API统计
            recent_monitors = APIMonitor.objects.filter(
                timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
            )
            total_requests = sum(monitor.request_count for monitor in recent_monitors)
            total_success = sum(monitor.success_count for monitor in recent_monitors)
            
            return Response({
                'systems': {
                    'total': total_systems,
                    'active': active_systems,
                    'inactive': total_systems - active_systems
                },
                'sync_rules': {
                    'total': total_sync_rules,
                    'active': active_sync_rules,
                    'inactive': total_sync_rules - active_sync_rules
                },
                'recent_syncs': {
                    'total': total_syncs,
                    'successful': successful_syncs,
                    'success_rate': (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
                },
                'api_requests': {
                    'total': total_requests,
                    'successful': total_success,
                    'success_rate': (total_success / total_requests * 100) if total_requests > 0 else 0
                }
            })
        except Exception as e:
            logger.error(f"获取概览数据失败: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def system_health(self, request):
        """获取系统健康状态"""
        try:
            systems = IntegrationSystem.objects.filter(monitoring_enabled=True)
            health_status = []
            
            for system in systems:
                health = IntegrationMonitorService.get_system_health(system)
                health_status.append(health)
            
            return Response(health_status)
        except Exception as e:
            logger.error(f"获取系统健康状态失败: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def sync_performance(self, request):
        """获取同步性能数据"""
        try:
            # 获取最近7天的同步性能数据
            recent_logs = SyncLog.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7),
                status='success'
            ).order_by('created_at')
            
            performance_data = []
            for log in recent_logs:
                performance_data.append({
                    'date': log.created_at.date(),
                    'duration': log.duration_seconds,
                    'records_per_second': log.records_per_second,
                    'total_records': log.total_records,
                    'sync_rule': log.sync_rule.name
                })
            
            return Response(performance_data)
        except Exception as e:
            logger.error(f"获取同步性能数据失败: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
