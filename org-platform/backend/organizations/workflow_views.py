"""
工作流相关视图
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import WorkflowRule, WorkflowRuleExecution, WorkflowTemplate
from .workflow_serializers import (
    WorkflowRuleSerializer, WorkflowRuleCreateSerializer, WorkflowRuleExecutionSerializer,
    WorkflowTemplateSerializer, WorkflowRuleTestSerializer, WorkflowStatsSerializer
)


class WorkflowRuleViewSet(viewsets.ModelViewSet):
    """工作流规则管理"""
    queryset = WorkflowRule.objects.all()
    serializer_class = WorkflowRuleSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rule_type', 'is_active', 'status']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['priority', 'created_at', 'execution_count']
    ordering = ['priority', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return WorkflowRuleCreateSerializer
        return WorkflowRuleSerializer

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """手动执行工作流规则"""
        rule = self.get_object()
        serializer = WorkflowRuleExecutionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # 创建执行记录
            execution = WorkflowExecution.objects.create(
                rule=rule,
                context=serializer.validated_data.get('context', {}),
                trigger_data=serializer.validated_data.get('trigger_data', {}),
                executed_by=request.user if request.user.is_authenticated else None
            )
            
            # 执行规则
            result = rule.execute(serializer.validated_data.get('context', {}))
            
            # 更新执行记录
            execution.complete(result={'success': result})
            
            return Response({
                'message': '工作流规则执行成功',
                'execution_id': str(execution.id),
                'result': result
            })
            
        except Exception as e:
            if 'execution' in locals():
                execution.complete(error_message=str(e))
            return Response({
                'error': '工作流规则执行失败',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """测试工作流规则"""
        rule = self.get_object()
        serializer = WorkflowRuleTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        test_data = serializer.validated_data['test_data']
        
        # 检查是否触发规则
        is_triggered = rule.is_triggered(test_data)
        
        return Response({
            'is_triggered': is_triggered,
            'rule_name': rule.name,
            'test_data': test_data,
            'trigger_conditions': rule.trigger_conditions
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取工作流规则统计信息"""
        # 基础统计
        total_rules = WorkflowRule.objects.count()
        active_rules = WorkflowRule.objects.filter(is_active=True).count()
        
        # 执行统计
        total_executions = WorkflowExecution.objects.count()
        successful_executions = WorkflowExecution.objects.filter(status='completed').count()
        failed_executions = WorkflowExecution.objects.filter(status='failed').count()
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # 平均执行时间
        avg_duration = WorkflowExecution.objects.filter(
            status='completed',
            duration__isnull=False
        ).aggregate(avg_duration=Avg('duration'))['avg_duration']
        
        # 最常用规则
        most_used_rules = WorkflowRule.objects.annotate(
            execution_count=Count('workflowexecution')
        ).order_by('-execution_count')[:5].values('name', 'code', 'execution_count')
        
        # 最近执行记录
        recent_executions = WorkflowExecution.objects.select_related('rule').order_by('-started_at')[:10].values(
            'id', 'rule__name', 'status', 'started_at', 'duration'
        )
        
        stats_data = {
            'total_rules': total_rules,
            'active_rules': active_rules,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'success_rate': round(success_rate, 2),
            'avg_execution_time': avg_duration,
            'most_used_rules': list(most_used_rules),
            'recent_executions': list(recent_executions)
        }
        
        serializer = WorkflowStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取规则类型分类"""
        categories = WorkflowRule.objects.values('rule_type').annotate(
            count=Count('id')
        ).order_by('rule_type')
        
        return Response(categories)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换规则激活状态"""
        rule = self.get_object()
        rule.is_active = not rule.is_active
        rule.save()
        
        return Response({
            'message': f'规则已{"激活" if rule.is_active else "停用"}',
            'is_active': rule.is_active
        })


class WorkflowRuleExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """工作流规则执行记录管理"""
    queryset = WorkflowRuleExecution.objects.all()
    serializer_class = WorkflowRuleExecutionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'rule__rule_type']
    search_fields = ['rule__name', 'error_message']
    ordering_fields = ['started_at', 'completed_at', 'duration']
    ordering = ['-started_at']

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消执行"""
        execution = self.get_object()
        if execution.status not in ['pending', 'running']:
            return Response({
                'error': '只能取消待执行或执行中的工作流'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reason = request.data.get('reason', '手动取消')
        execution.cancel(reason)
        
        return Response({
            'message': '工作流执行已取消',
            'reason': reason
        })

    @action(detail=False, methods=['get'])
    def status_stats(self, request):
        """获取执行状态统计"""
        stats = WorkflowExecution.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        return Response(list(stats))


class WorkflowTemplateViewSet(viewsets.ModelViewSet):
    """工作流模板管理"""
    queryset = WorkflowTemplate.objects.all()
    serializer_class = WorkflowTemplateSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'is_public']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['usage_count', 'created_at']
    ordering = ['-usage_count', '-created_at']

    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """使用模板"""
        template = self.get_object()
        template.increment_usage()
        
        return Response({
            'message': '模板使用次数已更新',
            'usage_count': template.usage_count
        })

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """获取热门模板"""
        popular_templates = WorkflowTemplate.objects.filter(
            is_active=True, is_public=True
        ).order_by('-usage_count')[:10]
        
        serializer = self.get_serializer(popular_templates, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取模板分类"""
        categories = WorkflowTemplate.objects.values('category').annotate(
            count=Count('id')
        ).order_by('category')
        
        return Response(categories)


class SimpleWorkflowApiViewSet(viewsets.ViewSet):
    """简化的工作流API，用于快速验证和调试"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def rules(self, request):
        """获取工作流规则列表"""
        rules_data = [
            {
                "id": "1",
                "name": "新员工入职流程",
                "code": "employee_onboarding",
                "description": "新员工入职的完整流程，包括信息收集、部门确认、权限分配等步骤",
                "rule_type": "employee_management",
                "is_active": True,
                "priority": 1,
                "execution_count": 15,
                "success_count": 14,
                "failure_count": 1,
                "success_rate": 93.33,
                "last_executed": "2025-01-29T10:30:00Z",
                "created_at": "2025-01-20T09:00:00Z"
            },
            {
                "id": "2",
                "name": "员工离职流程",
                "code": "employee_offboarding",
                "description": "员工离职的完整流程，包括工作交接、权限回收、设备归还等步骤",
                "rule_type": "employee_management",
                "is_active": True,
                "priority": 1,
                "execution_count": 8,
                "success_count": 8,
                "failure_count": 0,
                "success_rate": 100.0,
                "last_executed": "2025-01-28T16:45:00Z",
                "created_at": "2025-01-20T09:00:00Z"
            },
            {
                "id": "3",
                "name": "部门重组流程",
                "code": "department_reorganization",
                "description": "部门重组时的自动化流程，包括员工重新分配、权限调整等",
                "rule_type": "department_management",
                "is_active": True,
                "priority": 2,
                "execution_count": 3,
                "success_count": 3,
                "failure_count": 0,
                "success_rate": 100.0,
                "last_executed": "2025-01-25T09:15:00Z",
                "created_at": "2025-01-20T09:00:00Z"
            },
            {
                "id": "4",
                "name": "权限变更流程",
                "code": "permission_change",
                "description": "用户权限变更的审批流程，确保权限变更的合规性",
                "rule_type": "permission_management",
                "is_active": True,
                "priority": 3,
                "execution_count": 25,
                "success_count": 23,
                "failure_count": 2,
                "success_rate": 92.0,
                "last_executed": "2025-01-29T14:20:00Z",
                "created_at": "2025-01-20T09:00:00Z"
            },
            {
                "id": "5",
                "name": "数据同步规则",
                "code": "data_sync_rule",
                "description": "与第三方系统数据同步的自动化规则",
                "rule_type": "integration",
                "is_active": True,
                "priority": 4,
                "execution_count": 120,
                "success_count": 118,
                "failure_count": 2,
                "success_rate": 98.33,
                "last_executed": "2025-01-29T02:00:00Z",
                "created_at": "2025-01-20T09:00:00Z"
            },
            {
                "id": "6",
                "name": "异常数据检测",
                "code": "data_anomaly_detection",
                "description": "检测组织架构数据异常并自动处理",
                "rule_type": "data_quality",
                "is_active": True,
                "priority": 5,
                "execution_count": 45,
                "success_count": 44,
                "failure_count": 1,
                "success_rate": 97.78,
                "last_executed": "2025-01-29T12:00:00Z",
                "created_at": "2025-01-20T09:00:00Z"
            },
            {
                "id": "7",
                "name": "月度报告生成",
                "code": "monthly_report_generation",
                "description": "自动生成月度组织架构报告",
                "rule_type": "reporting",
                "is_active": True,
                "priority": 6,
                "execution_count": 12,
                "success_count": 12,
                "failure_count": 0,
                "success_rate": 100.0,
                "last_executed": "2025-01-01T09:00:00Z",
                "created_at": "2025-01-20T09:00:00Z"
            },
            {
                "id": "8",
                "name": "自动化任务调度",
                "code": "automation_scheduler",
                "description": "自动化任务调度和执行",
                "rule_type": "automation",
                "is_active": True,
                "priority": 7,
                "execution_count": 200,
                "success_count": 198,
                "failure_count": 2,
                "success_rate": 99.0,
                "last_executed": "2025-01-29T15:00:00Z",
                "created_at": "2025-01-20T09:00:00Z"
            }
        ]
        
        # 支持分页和筛选
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        rule_type = request.GET.get('rule_type')
        search = request.GET.get('search')
        
        # 筛选数据
        filtered_data = rules_data
        if rule_type:
            filtered_data = [rule for rule in filtered_data if rule['rule_type'] == rule_type]
        if search:
            filtered_data = [rule for rule in filtered_data if search.lower() in rule['name'].lower()]
        
        # 分页
        total_count = len(filtered_data)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_data = filtered_data[start_index:end_index]
        
        return Response({
            'results': paginated_data,
            'count': total_count,
            'next': None if end_index >= total_count else f'?page={page + 1}',
            'previous': None if page == 1 else f'?page={page - 1}'
        })

    @action(detail=False, methods=['get'])
    def executions(self, request):
        """获取工作流执行记录"""
        executions_data = [
            {
                "id": "1",
                "rule_name": "新员工入职流程",
                "status": "completed",
                "started_at": "2025-01-29T10:30:00Z",
                "completed_at": "2025-01-29T10:35:00Z",
                "duration": "5分钟",
                "executed_by": "system"
            },
            {
                "id": "2",
                "rule_name": "权限变更流程",
                "status": "completed",
                "started_at": "2025-01-29T14:20:00Z",
                "completed_at": "2025-01-29T14:22:00Z",
                "duration": "2分钟",
                "executed_by": "admin"
            },
            {
                "id": "3",
                "rule_name": "数据同步规则",
                "status": "completed",
                "started_at": "2025-01-29T02:00:00Z",
                "completed_at": "2025-01-29T02:15:00Z",
                "duration": "15分钟",
                "executed_by": "system"
            },
            {
                "id": "4",
                "rule_name": "员工离职流程",
                "status": "running",
                "started_at": "2025-01-29T16:00:00Z",
                "completed_at": None,
                "duration": None,
                "executed_by": "hr_manager"
            },
            {
                "id": "5",
                "rule_name": "新员工入职流程",
                "status": "failed",
                "started_at": "2025-01-28T15:30:00Z",
                "completed_at": "2025-01-28T15:32:00Z",
                "duration": "2分钟",
                "executed_by": "system",
                "error_message": "权限分配服务不可用"
            }
        ]
        return Response(executions_data)

    @action(detail=False, methods=['get'])
    def templates(self, request):
        """获取工作流模板列表"""
        templates_data = [
            {
                "id": "1",
                "name": "新员工入职模板",
                "code": "employee_onboarding_template",
                "description": "标准的新员工入职流程模板，包含信息收集、部门确认、权限分配等步骤",
                "category": "hr",
                "is_active": True,
                "is_public": True,
                "usage_count": 25,
                "created_at": "2025-01-20T09:00:00Z"
            },
            {
                "id": "2",
                "name": "员工离职模板",
                "code": "employee_offboarding_template",
                "description": "标准的员工离职流程模板",
                "category": "hr",
                "is_active": True,
                "is_public": True,
                "usage_count": 18
            },
            {
                "id": "3",
                "name": "部门重组模板",
                "code": "department_reorganization_template",
                "description": "部门重组流程模板",
                "category": "operations",
                "is_active": True,
                "is_public": True,
                "usage_count": 8
            },
            {
                "id": "4",
                "name": "权限审批模板",
                "code": "permission_approval_template",
                "description": "权限变更审批流程模板",
                "category": "compliance",
                "is_active": True,
                "is_public": True,
                "usage_count": 32
            },
            {
                "id": "5",
                "name": "数据同步模板",
                "code": "data_sync_template",
                "description": "数据同步流程模板",
                "category": "it",
                "is_active": True,
                "is_public": False,
                "usage_count": 45
            }
        ]
        
        # 支持分页和筛选
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        category = request.GET.get('category')
        search = request.GET.get('search')
        
        # 筛选数据
        filtered_data = templates_data
        if category:
            filtered_data = [template for template in filtered_data if template['category'] == category]
        if search:
            filtered_data = [template for template in filtered_data if search.lower() in template['name'].lower()]
        
        # 分页
        total_count = len(filtered_data)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_data = filtered_data[start_index:end_index]
        
        return Response({
            'results': paginated_data,
            'count': total_count,
            'next': None if end_index >= total_count else f'?page={page + 1}',
            'previous': None if page == 1 else f'?page={page - 1}'
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取工作流统计信息"""
        stats_data = {
            "total_rules": 8,
            "active_rules": 7,
            "total_executions": 171,
            "successful_executions": 166,
            "failed_executions": 5,
            "success_rate": 97.08,
            "avg_execution_time": "3.5分钟",
            "most_used_rules": [
                {"name": "数据同步规则", "code": "data_sync_rule", "execution_count": 120},
                {"name": "权限变更流程", "code": "permission_change", "execution_count": 25},
                {"name": "新员工入职流程", "code": "employee_onboarding", "execution_count": 15}
            ],
            "recent_executions": [
                {
                    "id": "1",
                    "rule_name": "新员工入职流程",
                    "status": "completed",
                    "started_at": "2025-01-29T10:30:00Z",
                    "duration": "5分钟"
                },
                {
                    "id": "2",
                    "rule_name": "权限变更流程",
                    "status": "completed",
                    "started_at": "2025-01-29T14:20:00Z",
                    "duration": "2分钟"
                }
            ]
        }
        return Response(stats_data)
