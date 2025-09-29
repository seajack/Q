from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponse
import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)
from .models import Department, Position, Employee
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
import io
from django.http import HttpResponse
import pandas as pd
from rest_framework.views import APIView

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


class ImportDepartmentsView(APIView):
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        try:
            file = request.FILES.get('file')
            mode = request.data.get('mode', 'incremental')
            
            if not file:
                return Response({'error': '没有上传文件'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 读取Excel文件的所有工作表
            excel_file = pd.ExcelFile(file)
            results = {
                'departments': {'created': 0, 'updated': 0, 'errors': []},
                'positions': {'created': 0, 'updated': 0, 'errors': []},
                'employees': {'created': 0, 'updated': 0, 'errors': []}
            }
            
            # 开始事务
            with transaction.atomic():
                if mode == 'full':
                    # 全量替换：删除所有现有数据
                    Employee.objects.all().delete()
                    Position.objects.all().delete()
                    Department.objects.all().delete()
                
                # 1. 导入部门数据
                if '部门信息' in excel_file.sheet_names:
                    dept_df = pd.read_excel(file, sheet_name='部门信息')
                    results['departments'] = self._import_departments(dept_df, mode)
                
                # 2. 导入职位数据
                if '职位信息' in excel_file.sheet_names:
                    position_df = pd.read_excel(file, sheet_name='职位信息')
                    results['positions'] = self._import_positions(position_df, mode)
                
                # 3. 导入员工数据
                if '员工信息' in excel_file.sheet_names:
                    employee_df = pd.read_excel(file, sheet_name='员工信息')
                    results['employees'] = self._import_employees(employee_df, mode)
                
                return Response({
                    'message': '导入完成',
                    'results': results
                })
                
        except Exception as e:
            logger.error(f'导入组织架构失败: {str(e)}')
            return Response({
                'error': f'导入失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _import_departments(self, df, mode):
        """导入部门数据"""
        created_count = 0
        updated_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                if pd.isna(row.get('name')):
                    continue
                    
                dept_data = {
                    'name': str(row['name']),
                    'code': str(row.get('code', '')),
                    'level': int(row.get('level', 1)),
                    'sort_order': int(row.get('sort_order', 0)),
                    'description': str(row.get('description', '')),
                    'is_active': bool(row.get('is_active', True))
                }
                
                # 处理父部门
                if pd.notna(row.get('parent_id')):
                    try:
                        # 先尝试按ID查找，如果失败则按编码查找
                        try:
                            parent = Department.objects.get(id=int(row['parent_id']))
                        except (ValueError, Department.DoesNotExist):
                            parent = Department.objects.get(code=str(row['parent_id']))
                        dept_data['parent'] = parent
                    except Department.DoesNotExist:
                        errors.append(f"第{index+1}行: 父部门ID/编码 {row['parent_id']} 不存在")
                        continue
                
                # 处理部门经理
                if pd.notna(row.get('manager_id')):
                    try:
                        from django.contrib.auth.models import User
                        manager = User.objects.get(id=int(row['manager_id']))
                        dept_data['manager'] = manager
                    except User.DoesNotExist:
                        errors.append(f"第{index+1}行: 部门经理ID {row['manager_id']} 不存在")
                
                # 创建或更新部门
                if 'id' in df.columns and pd.notna(row.get('id')):
                    dept, created = Department.objects.update_or_create(
                        id=int(row['id']),
                        defaults=dept_data
                    )
                else:
                    dept, created = Department.objects.get_or_create(
                        name=dept_data['name'],
                        defaults=dept_data
                    )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                errors.append(f"第{index+1}行: {str(e)}")
        
        return {'created': created_count, 'updated': updated_count, 'errors': errors}
    
    def _import_positions(self, df, mode):
        """导入职位数据"""
        created_count = 0
        updated_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                if pd.isna(row.get('name')):
                    continue
                    
                position_data = {
                    'name': str(row['name']),
                    'code': str(row.get('code', '')),
                    'management_level': str(row.get('management_level', 'junior')),
                    'level': int(row.get('level', 1)),
                    'description': str(row.get('description', '')),
                    'requirements': str(row.get('requirements', '')),
                    'responsibilities': str(row.get('responsibilities', '')),
                    'is_active': bool(row.get('is_active', True))
                }
                
                # 处理所属部门
                if pd.notna(row.get('department_id')):
                    try:
                        # 先尝试按ID查找，如果失败则按编码查找
                        try:
                            department = Department.objects.get(id=int(row['department_id']))
                        except (ValueError, Department.DoesNotExist):
                            department = Department.objects.get(code=str(row['department_id']))
                        position_data['department'] = department
                    except Department.DoesNotExist:
                        errors.append(f"第{index+1}行: 部门ID/编码 {row['department_id']} 不存在")
                        continue
                
                # 创建或更新职位
                if 'id' in df.columns and pd.notna(row.get('id')):
                    position, created = Position.objects.update_or_create(
                        id=int(row['id']),
                        defaults=position_data
                    )
                else:
                    # 先尝试按编码查找，如果不存在则创建
                    try:
                        position = Position.objects.get(code=position_data['code'])
                        # 更新现有职位
                        for key, value in position_data.items():
                            setattr(position, key, value)
                        position.save()
                        created = False
                    except Position.DoesNotExist:
                        position = Position.objects.create(**position_data)
                        created = True
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                errors.append(f"第{index+1}行: {str(e)}")
        
        return {'created': created_count, 'updated': updated_count, 'errors': errors}
    
    def _import_employees(self, df, mode):
        """导入员工数据"""
        created_count = 0
        updated_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                if pd.isna(row.get('name')) or pd.isna(row.get('employee_id')):
                    continue
                    
                # 创建或获取用户账号
                from django.contrib.auth.models import User
                username = f"emp_{row['employee_id']}"
                user, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': str(row['name']),
                        'email': str(row.get('email', ''))
                    }
                )
                
                employee_data = {
                    'user': user,
                    'employee_id': str(row['employee_id']),
                    'name': str(row['name']),
                    'gender': str(row.get('gender', 'M')),
                    'phone': str(row.get('phone', '')),
                    'email': str(row.get('email', '')),
                    'address': str(row.get('address', '')),
                    'hire_date': pd.to_datetime(row.get('hire_date', '2024-01-01')).date(),
                    'status': str(row.get('status', 'active'))
                }
                
                # 处理出生日期
                if pd.notna(row.get('birth_date')):
                    employee_data['birth_date'] = pd.to_datetime(row['birth_date']).date()
                
                # 处理所属部门
                if pd.notna(row.get('department_id')):
                    try:
                        # 先尝试按ID查找，如果失败则按编码查找
                        try:
                            department = Department.objects.get(id=int(row['department_id']))
                        except (ValueError, Department.DoesNotExist):
                            department = Department.objects.get(code=str(row['department_id']))
                        employee_data['department'] = department
                    except Department.DoesNotExist:
                        errors.append(f"第{index+1}行: 部门ID/编码 {row['department_id']} 不存在")
                        continue
                
                # 处理职位
                if pd.notna(row.get('position_id')):
                    try:
                        # 先尝试按ID查找，如果失败则按编码查找
                        try:
                            position = Position.objects.get(id=int(row['position_id']))
                        except (ValueError, Position.DoesNotExist):
                            position = Position.objects.get(code=str(row['position_id']))
                        employee_data['position'] = position
                    except Position.DoesNotExist:
                        errors.append(f"第{index+1}行: 职位ID/编码 {row['position_id']} 不存在")
                        continue
                
                # 处理直接上级
                if pd.notna(row.get('supervisor_id')):
                    try:
                        supervisor = Employee.objects.get(id=int(row['supervisor_id']))
                        employee_data['supervisor'] = supervisor
                    except Employee.DoesNotExist:
                        errors.append(f"第{index+1}行: 上级员工ID {row['supervisor_id']} 不存在")
                
                # 创建或更新员工
                if 'id' in df.columns and pd.notna(row.get('id')):
                    employee, created = Employee.objects.update_or_create(
                        id=int(row['id']),
                        defaults=employee_data
                    )
                else:
                    # 先尝试按员工号查找，如果不存在则创建
                    try:
                        employee = Employee.objects.get(employee_id=employee_data['employee_id'])
                        # 更新现有员工
                        for key, value in employee_data.items():
                            setattr(employee, key, value)
                        employee.save()
                        created = False
                    except Employee.DoesNotExist:
                        employee = Employee.objects.create(**employee_data)
                        created = True
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                errors.append(f"第{index+1}行: {str(e)}")
        
        return {'created': created_count, 'updated': updated_count, 'errors': errors}


class DownloadTemplateView(APIView):
    def get(self, request):
        # 创建多个工作表
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 1. 部门工作表
            dept_columns = [
                'id', 'name', 'code', 'parent_id', 'manager_id', 'level', 
                'sort_order', 'description', 'is_active'
            ]
            dept_df = pd.DataFrame(columns=dept_columns)
            dept_df.to_excel(writer, sheet_name='部门信息', index=False)
            
            # 2. 职位工作表
            position_columns = [
                'id', 'name', 'code', 'department_id', 'management_level', 
                'level', 'description', 'requirements', 'responsibilities', 'is_active'
            ]
            position_df = pd.DataFrame(columns=position_columns)
            position_df.to_excel(writer, sheet_name='职位信息', index=False)
            
            # 3. 员工工作表
            employee_columns = [
                'id', 'employee_id', 'name', 'gender', 'birth_date', 'phone', 
                'email', 'address', 'department_id', 'position_id', 'supervisor_id', 
                'hire_date', 'status'
            ]
            employee_df = pd.DataFrame(columns=employee_columns)
            employee_df.to_excel(writer, sheet_name='员工信息', index=False)
            
            # 4. 使用指南工作表
            guide_data = [
                ['Excel模板使用指南', '', '', '', '', '', '', '', ''],
                ['', '', '', '', '', '', '', '', ''],
                ['1. 部门信息表', '', '', '', '', '', '', '', ''],
                ['字段说明：', '', '', '', '', '', '', '', ''],
                ['id', '部门唯一标识符', '首次导入可留空，系统自动生成；更新时填写现有ID', '', '', '', '', '', ''],
                ['name', '部门名称', '必填，如：销售部、技术部', '', '', '', '', '', ''],
                ['code', '部门编码', '必填，唯一标识，如：SALES、TECH', '', '', '', '', '', ''],
                ['parent_id', '父部门ID', '顶级部门留空，子部门填写父部门ID或编码', '', '', '', '', '', ''],
                ['manager_id', '部门经理员工ID', '可选，填写员工ID', '', '', '', '', '', ''],
                ['level', '部门层级', '1=顶级，2=二级，以此类推', '', '', '', '', '', ''],
                ['sort_order', '排序', '数字，用于同级别部门排序', '', '', '', '', '', ''],
                ['description', '部门描述', '可选，部门说明', '', '', '', '', '', ''],
                ['is_active', '是否激活', 'true/false，默认true', '', '', '', '', '', ''],
                ['', '', '', '', '', '', '', '', ''],
                ['2. 职位信息表', '', '', '', '', '', '', '', ''],
                ['字段说明：', '', '', '', '', '', '', '', ''],
                ['id', '职位唯一标识符', '首次导入可留空，系统自动生成', '', '', '', '', '', ''],
                ['name', '职位名称', '必填，如：部门经理、高级工程师', '', '', '', '', '', ''],
                ['code', '职位编码', '必填，唯一标识，如：MGR、ENG', '', '', '', '', '', ''],
                ['department_id', '所属部门ID', '必填，填写部门ID或编码', '', '', '', '', '', ''],
                ['management_level', '管理层级', 'senior(高层)/middle(中层)/junior(基层)', '', '', '', '', '', ''],
                ['level', '职位级别', '1-13，数字越大级别越高', '', '', '', '', '', ''],
                ['description', '职位描述', '可选，职位说明', '', '', '', '', '', ''],
                ['requirements', '任职要求', '可选，任职条件', '', '', '', '', '', ''],
                ['responsibilities', '岗位职责', '可选，工作职责', '', '', '', '', '', ''],
                ['is_active', '是否激活', 'true/false，默认true', '', '', '', '', '', ''],
                ['', '', '', '', '', '', '', '', ''],
                ['3. 员工信息表', '', '', '', '', '', '', '', ''],
                ['字段说明：', '', '', '', '', '', '', '', ''],
                ['id', '员工唯一标识符', '首次导入可留空，系统自动生成', '', '', '', '', '', ''],
                ['employee_id', '员工号', '必填，唯一，如：E001、E002', '', '', '', '', '', ''],
                ['name', '姓名', '必填，员工姓名', '', '', '', '', '', ''],
                ['gender', '性别', 'M(男)/F(女)', '', '', '', '', '', ''],
                ['birth_date', '出生日期', '格式：YYYY-MM-DD，如：1990-01-01', '', '', '', '', '', ''],
                ['phone', '手机号码', '可选，联系电话', '', '', '', '', '', ''],
                ['email', '邮箱', '可选，邮箱地址', '', '', '', '', '', ''],
                ['address', '地址', '可选，居住地址', '', '', '', '', '', ''],
                ['department_id', '所属部门ID', '必填，填写部门ID或编码', '', '', '', '', '', ''],
                ['position_id', '职位ID', '必填，填写职位ID', '', '', '', '', '', ''],
                ['supervisor_id', '直接上级员工ID', '可选，填写上级员工ID', '', '', '', '', '', ''],
                ['hire_date', '入职日期', '必填，格式：YYYY-MM-DD', '', '', '', '', '', ''],
                ['status', '在职状态', 'active(在职)/leave(休假)/resigned(离职)/retired(退休)', '', '', '', '', '', ''],
                ['', '', '', '', '', '', '', '', ''],
                ['4. 导入模式说明', '', '', '', '', '', '', '', ''],
                ['增量更新', '根据ID更新现有数据，添加新数据，保留未在文件中的数据', '', '', '', '', '', '', ''],
                ['全量替换', '删除所有现有数据，完全使用Excel文件重建组织架构', '', '', '', '', '', '', ''],
                ['', '', '', '', '', '', '', '', ''],
                ['5. 注意事项', '', '', '', '', '', '', '', ''],
                ['• 请按顺序填写：先部门，再职位，最后员工', '', '', '', '', '', '', '', ''],
                ['• 父部门必须在子部门之前定义', '', '', '', '', '', '', '', ''],
                ['• 部门ID和职位ID必须在员工信息中正确引用', '', '', '', '', '', '', '', ''],
                ['• 建议先备份现有数据', '', '', '', '', '', '', '', ''],
                ['• 测试小批量数据后再进行大批量导入', '', '', '', '', '', '', '', ''],
            ]
            guide_df = pd.DataFrame(guide_data)
            guide_df.to_excel(writer, sheet_name='使用指南', index=False)
        
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="organization_template.xlsx"'
        return response
