from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import (
    EvaluationCycle, EvaluationIndicator, EvaluationTask,
    EvaluationScore, EvaluationResult
)
from .serializers import (
    EvaluationCycleSerializer, EvaluationIndicatorSerializer,
    EvaluationTaskSerializer, EvaluationScoreSerializer,
    EvaluationResultSerializer, EvaluationStatsSerializer
)
import requests
from django.conf import settings


class EvaluationCycleViewSet(viewsets.ModelViewSet):
    """考核周期管理"""
    queryset = EvaluationCycle.objects.all().order_by('-created_at')
    serializer_class = EvaluationCycleSerializer
    
    @action(detail=True, methods=['post'])
    def generate_tasks(self, request, pk=None):
        """为指定周期生成考核任务"""
        cycle = self.get_object()
        
        # 从组织架构中台获取员工数据
        try:
            org_api_url = getattr(settings, 'ORG_PLATFORM_API_URL', 'http://localhost:8001/api')
            response = requests.get(f'{org_api_url}/employees/')
            if response.status_code == 200:
                employees_data = response.json().get('results', [])
                
                # 生成考核任务的逻辑
                tasks_created = 0
                for employee in employees_data:
                    # 根据职位级别生成考核关系
                    # 这里简化实现，实际应根据组织架构生成复杂的考核关系
                    task = EvaluationTask.objects.create(
                        cycle=cycle,
                        evaluatee_id=employee['id'],
                        evaluator_id=employee['id'],  # 临时设为自己，实际应该是上级
                        evaluation_code=f"EVAL{cycle.id}{employee['id']}{tasks_created:04d}",
                        relationship_type='superior',
                        weight=60.0,
                        status='pending'
                    )
                    tasks_created += 1
                
                return Response({
                    'message': f'成功生成 {tasks_created} 个考核任务',
                    'tasks_created': tasks_created
                })
            else:
                return Response({
                    'error': '无法获取员工数据'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': f'生成考核任务失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EvaluationIndicatorViewSet(viewsets.ModelViewSet):
    """考核指标管理"""
    queryset = EvaluationIndicator.objects.all().order_by('category', 'name')
    serializer_class = EvaluationIndicatorSerializer


class EvaluationTaskViewSet(viewsets.ModelViewSet):
    """考核任务管理"""
    queryset = EvaluationTask.objects.all().order_by('-created_at')
    serializer_class = EvaluationTaskSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        cycle_id = self.request.query_params.get('cycle_id')
        evaluator_id = self.request.query_params.get('evaluator_id')
        evaluatee_id = self.request.query_params.get('evaluatee_id')
        
        if cycle_id:
            queryset = queryset.filter(cycle_id=cycle_id)
        if evaluator_id:
            queryset = queryset.filter(evaluator_id=evaluator_id)
        if evaluatee_id:
            queryset = queryset.filter(evaluatee_id=evaluatee_id)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def evaluation_form(self, request, pk=None):
        """获取考核表单"""
        task = self.get_object()
        indicators = EvaluationIndicator.objects.filter(is_active=True)
        
        form_data = {
            'task': EvaluationTaskSerializer(task).data,
            'indicators': EvaluationIndicatorSerializer(indicators, many=True).data
        }
        
        return Response(form_data)


class EvaluationScoreViewSet(viewsets.ModelViewSet):
    """考核评分管理"""
    queryset = EvaluationScore.objects.all()
    serializer_class = EvaluationScoreSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        task_id = self.request.query_params.get('task_id')
        
        if task_id:
            queryset = queryset.filter(task_id=task_id)
            
        return queryset


class EvaluationResultViewSet(viewsets.ModelViewSet):
    """考核结果管理"""
    queryset = EvaluationResult.objects.all().order_by('-created_at')
    serializer_class = EvaluationResultSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        cycle_id = self.request.query_params.get('cycle_id')
        evaluatee_id = self.request.query_params.get('evaluatee_id')
        
        if cycle_id:
            queryset = queryset.filter(cycle_id=cycle_id)
        if evaluatee_id:
            queryset = queryset.filter(evaluatee_id=evaluatee_id)
            
        return queryset


@api_view(['GET'])
def overview_stats(request):
    """获取系统概览统计信息"""
    stats = {
        'total_cycles': EvaluationCycle.objects.count(),
        'active_cycles': EvaluationCycle.objects.filter(status='active').count(),
        'total_tasks': EvaluationTask.objects.count(),
        'completed_tasks': EvaluationTask.objects.filter(status='completed').count(),
        'total_employees': 0,  # 需要从组织架构中台获取
        'pending_evaluations': EvaluationTask.objects.filter(status='pending').count()
    }
    
    # 尝试从组织架构中台获取员工总数
    try:
        org_api_url = getattr(settings, 'ORG_PLATFORM_API_URL', 'http://localhost:8001/api')
        response = requests.get(f'{org_api_url}/employees/')
        if response.status_code == 200:
            employees_data = response.json()
            stats['total_employees'] = employees_data.get('count', 0)
    except:
        pass  # 如果获取失败，保持为0
    
    serializer = EvaluationStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
def cycle_stats(request, cycle_id):
    """获取指定周期的统计信息"""
    try:
        cycle = EvaluationCycle.objects.get(id=cycle_id)
        
        stats = {
            'cycle': EvaluationCycleSerializer(cycle).data,
            'total_tasks': EvaluationTask.objects.filter(cycle=cycle).count(),
            'completed_tasks': EvaluationTask.objects.filter(cycle=cycle, status='completed').count(),
            'pending_tasks': EvaluationTask.objects.filter(cycle=cycle, status='pending').count(),
            'total_results': EvaluationResult.objects.filter(cycle=cycle).count(),
        }
        
        return Response(stats)
        
    except EvaluationCycle.DoesNotExist:
        return Response({
            'error': '考核周期不存在'
        }, status=status.HTTP_404_NOT_FOUND)
