"""
智能组织架构分析API视图
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

from .intelligence import OrganizationIntelligence
from .models import Department, Employee


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organization_analysis(request):
    """
    获取组织架构智能分析结果
    """
    try:
        # 检查缓存
        cache_key = 'org_analysis_result'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response({
                'success': True,
                'data': cached_result,
                'from_cache': True
            })
        
        # 执行分析
        intelligence = OrganizationIntelligence()
        analysis_result = intelligence.analyze_organization()
        
        # 缓存结果（1小时）
        cache.set(cache_key, analysis_result, 3600)
        
        return Response({
            'success': True,
            'data': analysis_result,
            'from_cache': False
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organization_metrics(request):
    """
    获取组织关键指标
    """
    try:
        intelligence = OrganizationIntelligence()
        metrics = intelligence.calculate_key_metrics()
        
        # 添加实时统计
        metrics.update({
            'active_departments': Department.objects.filter(is_active=True).count(),
            'active_employees': Employee.objects.filter(status='active').count(),
            'last_updated': timezone.now().isoformat()
        })
        
        return Response({
            'success': True,
            'data': metrics
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_analysis(request):
    """
    刷新分析结果
    """
    try:
        # 清除缓存
        cache.delete('org_analysis_result')
        
        # 重新分析
        intelligence = OrganizationIntelligence()
        analysis_result = intelligence.analyze_organization()
        
        # 更新缓存
        cache.set('org_analysis_result', analysis_result, 3600)
        
        return Response({
            'success': True,
            'data': analysis_result,
            'message': '分析结果已刷新'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def department_analysis(request, department_id):
    """
    获取特定部门的分析结果
    """
    try:
        department = Department.objects.get(id=department_id)
        
        # 部门基础信息
        dept_info = {
            'id': department.id,
            'name': department.name,
            'employee_count': department.employees.count(),
            'child_departments': department.children.count(),
            'level': department.level,
            'parent': department.parent.name if department.parent else None
        }
        
        # 部门效率分析
        intelligence = OrganizationIntelligence()
        
        # 这里可以添加针对特定部门的分析逻辑
        dept_analysis = {
            'basic_info': dept_info,
            'efficiency_score': 75.0,  # 示例数据
            'communication_score': 80.0,
            'resource_utilization': 70.0,
            'recommendations': [
                '建议增加1名项目经理',
                '优化内部沟通流程',
                '加强跨部门协作'
            ]
        }
        
        return Response({
            'success': True,
            'data': dept_analysis
        })
        
    except Department.DoesNotExist:
        return Response({
            'success': False,
            'error': '部门不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def optimization_suggestions(request):
    """
    获取优化建议列表
    """
    try:
        # 获取分析结果
        cache_key = 'org_analysis_result'
        analysis_result = cache.get(cache_key)
        
        if not analysis_result:
            intelligence = OrganizationIntelligence()
            analysis_result = intelligence.analyze_organization()
            cache.set(cache_key, analysis_result, 3600)
        
        # 提取建议
        recommendations = analysis_result.get('recommendations', [])
        
        # 按优先级分组
        grouped_recommendations = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for rec in recommendations:
            priority = rec.get('priority', 'medium')
            grouped_recommendations[priority].append(rec)
        
        return Response({
            'success': True,
            'data': {
                'total_count': len(recommendations),
                'by_priority': grouped_recommendations,
                'summary': {
                    'high_priority': len(grouped_recommendations['high']),
                    'medium_priority': len(grouped_recommendations['medium']),
                    'low_priority': len(grouped_recommendations['low'])
                }
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analysis_history(request):
    """
    获取分析历史记录
    """
    try:
        # 这里可以从数据库获取历史分析记录
        # 暂时返回模拟数据
        history_data = [
            {
                'date': '2024-01-15',
                'overall_score': 82.5,
                'health_level': 'good',
                'key_changes': ['新增市场部', '技术部扩编']
            },
            {
                'date': '2024-01-01',
                'overall_score': 78.0,
                'health_level': 'good',
                'key_changes': ['人事部重组']
            }
        ]
        
        return Response({
            'success': True,
            'data': history_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def simulate_changes(request):
    """
    模拟组织变更的影响
    """
    try:
        changes = request.data.get('changes', [])
        
        if not changes:
            return Response({
                'success': False,
                'error': '请提供变更内容'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 这里可以实现变更模拟逻辑
        # 暂时返回模拟结果
        simulation_result = {
            'current_score': 78.5,
            'predicted_score': 82.0,
            'improvement': 3.5,
            'affected_metrics': {
                'efficiency': '+5%',
                'communication': '+8%',
                'cost': '-12%'
            },
            'risks': [
                '短期内可能影响工作效率',
                '需要额外的培训成本'
            ],
            'timeline': '预计2-3个月见效'
        }
        
        return Response({
            'success': True,
            'data': simulation_result
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def benchmark_comparison(request):
    """
    获取行业基准对比
    """
    try:
        # 获取当前组织指标
        intelligence = OrganizationIntelligence()
        current_metrics = intelligence.calculate_key_metrics()
        
        # 行业基准数据（示例）
        industry_benchmarks = {
            'management_ratio': 15.0,  # 行业平均管理人员比例
            'average_department_size': 12.0,  # 行业平均部门规模
            'hierarchy_depth': 4.0,  # 行业平均层级深度
            'efficiency_score': 75.0  # 行业平均效率分数
        }
        
        # 计算对比结果
        comparison = {}
        for key, benchmark_value in industry_benchmarks.items():
            current_value = current_metrics.get(key, 0)
            difference = current_value - benchmark_value
            comparison[key] = {
                'current': current_value,
                'benchmark': benchmark_value,
                'difference': round(difference, 1),
                'status': 'above' if difference > 0 else 'below' if difference < 0 else 'equal'
            }
        
        return Response({
            'success': True,
            'data': {
                'comparison': comparison,
                'overall_assessment': '整体表现优于行业平均水平',
                'industry': '科技行业',
                'company_size': '中型企业'
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
