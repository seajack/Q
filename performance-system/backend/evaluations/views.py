from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import (
    EvaluationCycle, EvaluationIndicator, EvaluationTask,
    EvaluationScore, EvaluationResult, Employee, EvaluationRule, ManualEvaluationAssignment
)
from .serializers import (
    EvaluationCycleSerializer, EvaluationIndicatorSerializer,
    EvaluationTaskSerializer, EvaluationScoreSerializer,
    EvaluationResultSerializer, EvaluationStatsSerializer, EmployeeSerializer,
    EvaluationRuleSerializer, ManualEvaluationAssignmentSerializer
)
import requests
from django.conf import settings
from django.http import HttpResponse
import openpyxl


class EvaluationCycleViewSet(viewsets.ModelViewSet):
    """考核周期管理"""
    queryset = EvaluationCycle.objects.all().order_by('-created_at')
    serializer_class = EvaluationCycleSerializer
    # 服务端筛选/检索/排序
    filterset_fields = ['status']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'name']
    
    def perform_create(self, serializer):
        """创建考核周期时自动设置创建者"""
        # 暂时使用第一个超级用户作为创建者，实际应该使用当前登录用户
        from django.contrib.auth.models import User
        creator = User.objects.filter(is_superuser=True).first()
        if not creator:
            # 如果没有超级用户，创建一个默认用户
            creator = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            creator.is_superuser = True
            creator.is_staff = True
            creator.save()
        serializer.save(created_by=creator)
    
    @action(detail=True, methods=['post'])
    def generate_tasks(self, request, pk=None):
        """为指定周期生成考核任务"""
        cycle = self.get_object()
        
        # 使用新的任务生成器
        from .services import EvaluationTaskGenerator
        
        generator = EvaluationTaskGenerator(cycle)
        result = generator.generate_tasks()
        
        if result['success']:
            return Response({
                'message': result['message'],
                'tasks_created': result['tasks_created']
            })
        else:
            return Response({
                'error': result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EvaluationIndicatorViewSet(viewsets.ModelViewSet):
    """考核指标管理"""
    queryset = EvaluationIndicator.objects.all().order_by('category', 'name')
    serializer_class = EvaluationIndicatorSerializer
    # 与前端对齐：类别/启用状态、名称/描述检索
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['category', 'name', 'weight', 'updated_at']


class EvaluationRuleViewSet(viewsets.ModelViewSet):
    """考核规则管理"""
    queryset = EvaluationRule.objects.all().order_by('-created_at')
    serializer_class = EvaluationRuleSerializer
    # 规则为全局配置：支持启用状态/范围筛选，名称与描述检索
    filterset_fields = ['is_active', 'evaluation_scope']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']
    
    @action(detail=False, methods=['post'])
    def create_defaults(self, request):
        """创建默认考核规则"""
        from .services import create_default_evaluation_rules
        
        try:
            create_default_evaluation_rules()
            return Response({
                'message': '默认考核规则创建成功'
            })
        except Exception as e:
            return Response({
                'error': f'创建默认规则失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ManualEvaluationAssignmentViewSet(viewsets.ModelViewSet):
    """手动评价分配管理"""
    queryset = ManualEvaluationAssignment.objects.all().order_by('-created_at')
    serializer_class = ManualEvaluationAssignmentSerializer
    # 服务端筛选/检索/排序
    filterset_fields = ['cycle', 'evaluator', 'evaluatee', 'relation_type']
    search_fields = ['evaluator__name', 'evaluatee__name', 'reason']
    ordering_fields = ['created_at', 'weight']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        cycle_id = self.request.query_params.get('cycle_id')
        
        if cycle_id:
            queryset = queryset.filter(cycle_id=cycle_id)
            
        return queryset
    
    def perform_create(self, serializer):
        """创建手动分配时自动设置创建者"""
        from django.contrib.auth.models import User
        creator = User.objects.filter(is_superuser=True).first()
        if not creator:
            creator = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            creator.is_superuser = True
            creator.is_staff = True
            creator.save()
        serializer.save(created_by=creator)


class EvaluationTaskViewSet(viewsets.ModelViewSet):
    """考核任务管理"""
    queryset = EvaluationTask.objects.all().order_by('-assigned_at')
    serializer_class = EvaluationTaskSerializer
    # 基本筛选：周期、评价人、被评价人、关系/状态
    filterset_fields = ['cycle', 'evaluator', 'evaluatee', 'relation_type', 'status']
    search_fields = ['evaluation_code', 'evaluator__name', 'evaluatee__name']
    ordering_fields = ['assigned_at', 'completed_at', 'status']
    
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
    
    @action(detail=False, methods=['get'], url_path='by-code/(?P<evaluation_code>[^/.]+)')
    def get_by_code(self, request, evaluation_code=None):
        """根据考核码获取任务和相关信息"""
        try:
            task = EvaluationTask.objects.get(evaluation_code=evaluation_code)
            indicators = EvaluationIndicator.objects.filter(is_active=True)
            
            # 检查是否已经有评分记录
            existing_scores = EvaluationScore.objects.filter(task=task)
            scores_data = {score.indicator_id: score for score in existing_scores}
            
            response_data = {
                'task': EvaluationTaskSerializer(task).data,
                'indicators': EvaluationIndicatorSerializer(indicators, many=True).data,
                'existing_scores': {str(k): {
                    'score': v.score,
                    'comment': v.comment
                } for k, v in scores_data.items()}
            }
            
            return Response(response_data)
            
        except EvaluationTask.DoesNotExist:
            return Response({
                'error': '考核任务不存在'
            }, status=status.HTTP_404_NOT_FOUND)
    
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
    filterset_fields = ['task', 'indicator']
    search_fields = ['comment', 'task__evaluation_code', 'indicator__name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        task_id = self.request.query_params.get('task_id')
        
        if task_id:
            queryset = queryset.filter(task_id=task_id)
            
        return queryset
    
    @action(detail=False, methods=['post'])
    def submit_task_scores(self, request):
        """提交任务的所有评分"""
        task_id = request.data.get('task_id')
        scores_data = request.data.get('scores', [])
        
        try:
            task = EvaluationTask.objects.get(id=task_id)
            
            # 清除原有评分
            EvaluationScore.objects.filter(task=task).delete()
            
            # 创建新评分
            created_scores = []
            for score_data in scores_data:
                score = EvaluationScore.objects.create(
                    task=task,
                    indicator_id=score_data['indicator_id'],
                    score=score_data['score'],
                    comment=score_data.get('comment', '')
                )
                created_scores.append(score)
            
            # 更新任务状态为已完成
            task.status = 'completed'
            from django.utils import timezone
            task.completed_at = timezone.now()
            task.save()
            
            return Response({
                'message': '评分提交成功',
                'scores_count': len(created_scores)
            })
            
        except EvaluationTask.DoesNotExist:
            return Response({
                'error': '考核任务不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'提交评分失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EvaluationResultViewSet(viewsets.ModelViewSet):
    """考核结果管理"""
    queryset = EvaluationResult.objects.all().order_by('-calculated_at')
    serializer_class = EvaluationResultSerializer
    # 支持周期与被评价人筛选
    filterset_fields = ['cycle', 'employee']
    search_fields = ['employee__name']
    ordering_fields = ['weighted_score', 'total_score', 'rank', 'calculated_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        cycle_id = self.request.query_params.get('cycle_id')
        evaluatee_id = self.request.query_params.get('evaluatee_id')
        
        if cycle_id:
            queryset = queryset.filter(cycle_id=cycle_id)
        if evaluatee_id:
            queryset = queryset.filter(employee_id=evaluatee_id)
            
        return queryset
    
    @action(detail=False, methods=['post'])
    def calculate_cycle_results(self, request):
        """计算指定周期的考核结果"""
        cycle_id = request.data.get('cycle_id')
        
        if not cycle_id:
            return Response({
                'error': '缺少周期 ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cycle = EvaluationCycle.objects.get(id=cycle_id)
            
            # 获取该周期下所有已完成的任务
            completed_tasks = EvaluationTask.objects.filter(
                cycle=cycle, 
                status='completed'
            ).select_related('evaluatee', 'evaluator')
            
            if not completed_tasks.exists():
                return Response({
                    'message': '该周期没有已完成的考核任务'
                })
            
            # 按被评价人分组计算结果
            from django.db.models import Avg, Count
            from decimal import Decimal
            
            # 先清除旧的结果
            EvaluationResult.objects.filter(cycle=cycle).delete()
            
            results_created = 0
            
            # 获取所有被评价人
            evaluatees = set(task.evaluatee for task in completed_tasks)
            
            for evaluatee in evaluatees:
                # 获取该员工的所有评分
                employee_tasks = completed_tasks.filter(evaluatee=evaluatee)
                
                if not employee_tasks.exists():
                    continue
                
                # 计算加权平均分
                total_weighted_score = Decimal('0')
                total_weight = Decimal('0')
                
                relation_scores = {}
                
                for task in employee_tasks:
                    # 获取任务的所有评分
                    task_scores = EvaluationScore.objects.filter(task=task)
                    
                    if task_scores.exists():
                        # 计算任务的加权平均分
                        task_total_score = Decimal('0')
                        task_total_weight = Decimal('0')
                        
                        for score in task_scores:
                            indicator_weight = Decimal(str(score.indicator.weight))
                            weighted_score = Decimal(str(score.score)) * indicator_weight
                            task_total_score += weighted_score
                            task_total_weight += indicator_weight
                        
                        if task_total_weight > 0:
                            task_avg_score = task_total_score / task_total_weight
                            task_weight = Decimal(str(task.weight))
                            
                            total_weighted_score += task_avg_score * task_weight
                            total_weight += task_weight
                            
                            # 按关系类型分组记录
                            relation_type = task.relation_type
                            if relation_type not in relation_scores:
                                relation_scores[relation_type] = []
                            relation_scores[relation_type].append(task_avg_score)
                
                if total_weight > 0:
                    weighted_score = total_weighted_score / total_weight
                    
                    # 计算各关系类型的平均分
                    superior_score = None
                    peer_score = None
                    subordinate_score = None
                    
                    if 'superior' in relation_scores:
                        superior_score = sum(relation_scores['superior']) / len(relation_scores['superior'])
                    if 'peer' in relation_scores:
                        peer_score = sum(relation_scores['peer']) / len(relation_scores['peer'])
                    if 'subordinate' in relation_scores:
                        subordinate_score = sum(relation_scores['subordinate']) / len(relation_scores['subordinate'])
                    
                    # 创建结果记录
                    EvaluationResult.objects.create(
                        cycle=cycle,
                        employee=evaluatee,
                        total_score=total_weighted_score,
                        weighted_score=weighted_score,
                        superior_score=superior_score,
                        peer_score=peer_score,
                        subordinate_score=subordinate_score,
                        is_final=True
                    )
                    results_created += 1
            
            # 计算排名
            results = EvaluationResult.objects.filter(cycle=cycle).order_by('-weighted_score')
            for index, result in enumerate(results, 1):
                result.rank = index
                result.save()
            
            return Response({
                'message': f'成功计算 {results_created} 个员工的考核结果',
                'results_created': results_created
            })
            
        except EvaluationCycle.DoesNotExist:
            return Response({
                'error': '考核周期不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'计算结果失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出考核结果为 Excel (xlsx)。支持 ?cycle= 或 ?cycle_id= 过滤。"""
        try:
            cycle_id = request.query_params.get('cycle') or request.query_params.get('cycle_id')
            qs = self.get_queryset()
            if cycle_id:
                qs = qs.filter(cycle_id=cycle_id)

            # 创建工作簿
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = '考核结果'
            headers = ['周期ID', '周期名称', '员工ID', '员工姓名', '加权平均分', '总分', '上级评分', '同级评分', '下级评分', '排名', '是否最终', '计算时间']
            ws.append(headers)

            # 批量预取
            qs = qs.select_related('cycle', 'employee')
            for r in qs:
                ws.append([
                    r.cycle_id,
                    getattr(r.cycle, 'name', ''),
                    r.employee_id,
                    getattr(r.employee, 'name', ''),
                    float(r.weighted_score or 0),
                    float(r.total_score or 0),
                    float(r.superior_score or 0) if r.superior_score is not None else None,
                    float(r.peer_score or 0) if r.peer_score is not None else None,
                    float(r.subordinate_score or 0) if r.subordinate_score is not None else None,
                    r.rank,
                    '是' if r.is_final else '否',
                    r.calculated_at.strftime('%Y-%m-%d %H:%M:%S') if r.calculated_at else ''
                ])

            from io import BytesIO
            bio = BytesIO()
            wb.save(bio)
            bio.seek(0)

            filename = 'results.xlsx' if not cycle_id else f'results_cycle_{cycle_id}.xlsx'
            resp = HttpResponse(bio.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            resp['Content-Disposition'] = f'attachment; filename="{filename}"'
            return resp
        except Exception as e:
            return Response({'error': f'导出失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def overview_stats(request):
    """获取系统概览统计信息"""
    from django.db.models import Avg, Count
    from decimal import Decimal
    
    # 基础统计
    total_cycles = EvaluationCycle.objects.count()
    active_cycles = EvaluationCycle.objects.filter(status='active').count()
    total_tasks = EvaluationTask.objects.count()
    completed_tasks = EvaluationTask.objects.filter(status='completed').count()
    pending_tasks = EvaluationTask.objects.filter(status='pending').count()
    
    # 计算完成率
    completion_rate = 0
    if total_tasks > 0:
        completion_rate = (completed_tasks / total_tasks) * 100
    
    # 计算平均分数
    average_score = 0
    results = EvaluationResult.objects.all()
    if results.exists():
        total_score = sum(float(result.weighted_score) for result in results)
        average_score = total_score / results.count()
    
    # 获取员工总数
    total_employees = Employee.objects.filter(is_active=True).count()
    if total_employees == 0:
        # 如果本地没有员工，尝试从组织架构中台获取
        try:
            org_api_url = getattr(settings, 'ORG_PLATFORM_API_URL', 'http://localhost:8000/api')
            response = requests.get(f'{org_api_url}/employees/')
            if response.status_code == 200:
                employees_data = response.json()
                total_employees = employees_data.get('count', 0)
        except:
            pass
    
    # 计算部门统计
    department_stats = []
    departments = Employee.objects.values('department_name').annotate(
        employee_count=Count('id')
    ).filter(department_name__isnull=False, is_active=True)
    
    for dept in departments:
        dept_name = dept['department_name']
        employee_count = dept['employee_count']
        
        # 部门任务统计
        dept_employees = Employee.objects.filter(department_name=dept_name, is_active=True)
        dept_employee_ids = list(dept_employees.values_list('id', flat=True))
        dept_total_tasks = EvaluationTask.objects.filter(evaluatee_id__in=dept_employee_ids).count()
        dept_completed_tasks = EvaluationTask.objects.filter(
            evaluatee_id__in=dept_employee_ids, 
            status='completed'
        ).count()
        
        dept_completion_rate = 0
        if dept_total_tasks > 0:
            dept_completion_rate = (dept_completed_tasks / dept_total_tasks) * 100
        
        # 部门平均分数
        dept_results = EvaluationResult.objects.filter(employee_id__in=dept_employee_ids)
        dept_average_score = 0
        if dept_results.exists():
            dept_total_score = sum(float(result.weighted_score) for result in dept_results)
            dept_average_score = dept_total_score / dept_results.count()
        
        department_stats.append({
            'department_name': dept_name,
            'employee_count': employee_count,
            'completion_rate': round(dept_completion_rate, 1),
            'average_score': round(dept_average_score, 1)
        })
    
    # 按平均分数排序
    department_stats.sort(key=lambda x: x['average_score'], reverse=True)
    
    stats = {
        'total_cycles': total_cycles,
        'active_cycles': active_cycles,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'total_employees': total_employees,
        'pending_evaluations': pending_tasks,
        'completion_rate': round(completion_rate, 1),
        'average_score': round(average_score, 1),
        'department_stats': department_stats
    }
    
    return Response(stats)


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


class EmployeeViewSet(viewsets.ModelViewSet):
    """员工管理（本地副本）"""
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer
    # 服务端筛选/检索/排序
    filterset_fields = ['department_name', 'status', 'is_active']
    search_fields = ['name', 'email', 'phone', 'employee_id']
    ordering_fields = ['department_name', 'position_level', 'employee_id', 'name']
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """同步组织架构中台的员工数据"""
        try:
            org_api_url = getattr(settings, 'ORG_PLATFORM_API_URL', 'http://localhost:8000/api')
            response = requests.get(f'{org_api_url}/employees/')
            
            if response.status_code == 200:
                employees_data = response.json().get('results', [])
                
                synced_count = 0
                for emp_data in employees_data:
                    employee, created = Employee.objects.get_or_create(
                        employee_id=emp_data['employee_id'],
                        defaults={
                            'name': emp_data['name'],
                            'department_id': emp_data['department'],
                            'department_name': emp_data.get('department_name', ''),
                            'position_id': emp_data['position'],
                            'position_name': emp_data.get('position_name', ''),
                            'status': emp_data.get('status', 'active')
                        }
                    )
                    
                    if not created:
                        # 更新现有员工信息
                        employee.name = emp_data['name']
                        employee.department_id = emp_data['department']
                        employee.department_name = emp_data.get('department_name', '')
                        employee.position_id = emp_data['position']
                        employee.position_name = emp_data.get('position_name', '')
                        employee.status = emp_data.get('status', 'active')
                        employee.save()
                    
                    synced_count += 1
                
                return Response({
                    'message': f'成功同步 {synced_count} 个员工数据',
                    'synced_count': synced_count
                })
            else:
                return Response({
                    'error': '无法连接到组织架构中台'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': f'同步员工数据失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
