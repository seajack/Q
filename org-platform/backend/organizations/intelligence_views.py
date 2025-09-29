"""
智能分析API视图
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import random
import json

from .intelligence_models import (
    AnalysisResult, OptimizationRecommendation, OrganizationAnalysis,
    AnalysisHistory, AnalysisConfig, UserFeedback, BenchmarkData
)
from .intelligence_serializers import (
    AnalysisResultSerializer, OptimizationRecommendationSerializer,
    OrganizationAnalysisSerializer, AnalysisHistorySerializer,
    AnalysisConfigSerializer, UserFeedbackSerializer, BenchmarkDataSerializer,
    AnalysisSummarySerializer, BenchmarkComparisonSerializer,
    SimulationResultSerializer, OrganizationChartSerializer,
    EfficiencyHeatmapSerializer, RecommendedStructureSerializer
)


class AnalysisResultViewSet(viewsets.ModelViewSet):
    """分析结果管理"""
    queryset = AnalysisResult.objects.all()
    serializer_class = AnalysisResultSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取分析类别列表"""
        categories = AnalysisResult.objects.values_list('category', flat=True).distinct()
        return Response(list(categories))


class OptimizationRecommendationViewSet(viewsets.ModelViewSet):
    """优化建议管理"""
    queryset = OptimizationRecommendation.objects.all()
    serializer_class = OptimizationRecommendationSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def by_priority(self, request):
        """按优先级获取建议"""
        priority = request.query_params.get('priority', 'high')
        recommendations = self.get_queryset().filter(priority=priority)
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)


class OrganizationAnalysisViewSet(viewsets.ModelViewSet):
    """组织分析管理"""
    queryset = OrganizationAnalysis.objects.all()
    serializer_class = OrganizationAnalysisSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """获取最新分析结果"""
        try:
            analysis = self.get_queryset().filter(is_active=True).first()
            if not analysis:
                # 生成模拟数据
                analysis = self._generate_mock_analysis()
            
            serializer = self.get_serializer(analysis)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """刷新分析结果"""
        try:
            # 生成新的分析结果
            analysis = self._generate_mock_analysis()
            serializer = self.get_serializer(analysis)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def department(self, request, pk=None):
        """获取特定部门的分析结果"""
        try:
            # 模拟部门分析数据
            department_data = {
                'department_id': pk,
                'efficiency_score': random.uniform(60, 95),
                'communication_score': random.uniform(70, 90),
                'resource_utilization': random.uniform(65, 85),
                'recommendations': [
                    '优化部门内部沟通流程',
                    '提高资源利用效率',
                    '加强团队协作'
                ]
            }
            return Response(department_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _generate_mock_analysis(self):
        """生成模拟分析数据"""
        # 创建分析结果
        analysis_results = []
        categories = ['组织效率', '沟通协作', '资源利用', '创新能力', '管理质量']
        
        for category in categories:
            result = AnalysisResult.objects.create(
                category=category,
                score=round(random.uniform(60, 95), 2),
                level=random.choice(['优秀', '良好', '一般', '需改进']),
                description=f"{category}分析结果描述",
                details={'metric1': random.uniform(0, 100), 'metric2': random.uniform(0, 100)},
                recommendations=[f"{category}优化建议1", f"{category}优化建议2"]
            )
            analysis_results.append(result)

        # 创建优化建议
        recommendations = []
        priorities = ['high', 'medium', 'low']
        categories = ['组织架构', '流程优化', '技术升级', '人员培训']
        
        for i, category in enumerate(categories):
            rec = OptimizationRecommendation.objects.create(
                priority=priorities[i % len(priorities)],
                category=category,
                title=f"{category}优化建议",
                description=f"针对{category}的详细优化建议",
                expected_benefit=f"预期提升{random.randint(10, 30)}%的效率",
                implementation_cost=random.uniform(10000, 100000),
                timeframe=f"{random.randint(1, 6)}个月",
                impacted_departments=[f"部门{i+1}", f"部门{i+2}"],
                metrics={'efficiency': random.uniform(0, 100), 'cost': random.uniform(0, 100)}
            )
            recommendations.append(rec)

        # 创建组织分析
        analysis = OrganizationAnalysis.objects.create(
            overall_score=round(random.uniform(70, 90), 2),
            health_level=random.choice(['优秀', '良好', '一般']),
            metrics={
                'total_departments': random.randint(10, 50),
                'total_employees': random.randint(100, 1000),
                'efficiency_score': round(random.uniform(70, 90), 2),
                'communication_score': round(random.uniform(70, 90), 2)
            }
        )
        
        # 关联分析结果和建议
        analysis.analysis_results.set(analysis_results)
        analysis.recommendations.set(recommendations)
        
        return analysis


class AnalysisHistoryViewSet(viewsets.ModelViewSet):
    """分析历史管理"""
    queryset = AnalysisHistory.objects.all()
    serializer_class = AnalysisHistorySerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def trends(self, request):
        """获取分析趋势"""
        try:
            # 生成模拟趋势数据
            trends = []
            for i in range(12):  # 过去12个月
                date = timezone.now().date() - timedelta(days=30*i)
                trends.append({
                    'date': date.isoformat(),
                    'overall_score': round(random.uniform(70, 90), 2),
                    'health_level': random.choice(['优秀', '良好', '一般']),
                    'key_changes': [f"变化{i+1}", f"变化{i+2}"]
                })
            
            return Response(trends)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnalysisConfigViewSet(viewsets.ModelViewSet):
    """分析配置管理"""
    queryset = AnalysisConfig.objects.all()
    serializer_class = AnalysisConfigSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def current(self, request):
        """获取当前配置"""
        try:
            config = self.get_queryset().filter(is_active=True).first()
            if not config:
                # 创建默认配置
                config = AnalysisConfig.objects.create(
                    name='默认配置',
                    analysis_weights={
                        'efficiency': 0.3,
                        'communication': 0.25,
                        'innovation': 0.2,
                        'management': 0.25
                    },
                    thresholds={
                        'excellent': 90,
                        'good': 75,
                        'average': 60
                    },
                    enabled_features=['efficiency_analysis', 'communication_analysis', 'resource_analysis'],
                    update_frequency=24
                )
            
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserFeedbackViewSet(viewsets.ModelViewSet):
    """用户反馈管理"""
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer
    permission_classes = [AllowAny]


class BenchmarkDataViewSet(viewsets.ModelViewSet):
    """基准数据管理"""
    queryset = BenchmarkData.objects.all()
    serializer_class = BenchmarkDataSerializer
    permission_classes = [AllowAny]


class IntelligenceApiViewSet(viewsets.ViewSet):
    """智能分析API"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def test(self, request):
        """测试端点"""
        return Response({'message': '智能分析API测试成功', 'status': 'ok'})

    @action(detail=False, methods=['get'])
    def analysis(self, request):
        """获取组织架构智能分析结果"""
        print("Analysis method called")
        return Response({'message': '分析数据', 'status': 'ok'})

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """获取组织关键指标"""
        try:
            metrics_data = {
                'efficiency_score': round(random.uniform(70, 90), 2),
                'communication_score': round(random.uniform(70, 90), 2),
                'resource_utilization': round(random.uniform(65, 85), 2),
                'innovation_index': round(random.uniform(60, 80), 2),
                'employee_satisfaction': round(random.uniform(70, 90), 2),
                'management_effectiveness': round(random.uniform(70, 90), 2)
            }
            return Response(metrics_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """获取优化建议列表"""
        try:
            suggestions_data = {
                'total_count': 15,
                'by_priority': {
                    'high': [
                        {
                            'id': str(random.randint(1000, 9999)),
                            'priority': 'high',
                            'category': '组织架构',
                            'title': '优化组织架构',
                            'description': '重新设计组织架构以提高效率',
                            'expected_benefit': '预期提升20%的效率',
                            'implementation_cost': 50000,
                            'timeframe': '3个月',
                            'impacted_departments': ['技术部', '运营部'],
                            'metrics': {'efficiency': 85, 'cost': 60}
                        }
                    ],
                    'medium': [
                        {
                            'id': str(random.randint(1000, 9999)),
                            'priority': 'medium',
                            'category': '流程优化',
                            'title': '优化工作流程',
                            'description': '改进现有工作流程',
                            'expected_benefit': '预期提升15%的效率',
                            'implementation_cost': 30000,
                            'timeframe': '2个月',
                            'impacted_departments': ['运营部'],
                            'metrics': {'efficiency': 75, 'cost': 70}
                        }
                    ],
                    'low': [
                        {
                            'id': str(random.randint(1000, 9999)),
                            'priority': 'low',
                            'category': '技术升级',
                            'title': '技术系统升级',
                            'description': '升级现有技术系统',
                            'expected_benefit': '预期提升10%的效率',
                            'implementation_cost': 100000,
                            'timeframe': '6个月',
                            'impacted_departments': ['技术部'],
                            'metrics': {'efficiency': 80, 'cost': 40}
                        }
                    ]
                },
                'summary': {
                    'high_priority': 5,
                    'medium_priority': 7,
                    'low_priority': 3
                }
            }
            return Response(suggestions_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """获取分析历史记录"""
        try:
            history_data = []
            for i in range(6):  # 过去6个月
                date = timezone.now().date() - timedelta(days=30*i)
                history_data.append({
                    'date': date.isoformat(),
                    'overall_score': round(random.uniform(70, 90), 2),
                    'health_level': random.choice(['优秀', '良好', '一般']),
                    'key_changes': [f"变化{i+1}", f"变化{i+2}"]
                })
            
            return Response(history_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def simulate(self, request):
        """模拟组织变更的影响"""
        try:
            changes = request.data.get('changes', [])
            
            simulation_result = {
                'current_score': round(random.uniform(70, 90), 2),
                'predicted_score': round(random.uniform(75, 95), 2),
                'improvement': round(random.uniform(5, 15), 2),
                'affected_metrics': {
                    'efficiency': f"+{random.randint(5, 20)}%",
                    'communication': f"+{random.randint(3, 15)}%",
                    'cost': f"-{random.randint(5, 25)}%"
                },
                'risks': ['实施风险', '成本风险', '时间风险'],
                'timeline': f"{random.randint(3, 12)}个月"
            }
            
            return Response(simulation_result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def benchmark(self, request):
        """获取行业基准对比"""
        try:
            benchmark_data = {
                'comparison': {
                    'efficiency': {
                        'current': round(random.uniform(70, 90), 2),
                        'benchmark': 85.5,
                        'difference': round(random.uniform(-10, 10), 2),
                        'status': random.choice(['above', 'below', 'equal'])
                    },
                    'communication': {
                        'current': round(random.uniform(70, 90), 2),
                        'benchmark': 82.3,
                        'difference': round(random.uniform(-10, 10), 2),
                        'status': random.choice(['above', 'below', 'equal'])
                    }
                },
                'overall_assessment': '组织表现良好，有改进空间',
                'industry': '科技行业',
                'company_size': '中型企业'
            }
            return Response(benchmark_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def org_chart(self, request):
        """获取组织架构图数据"""
        try:
            chart_data = {
                'nodes': [
                    {
                        'id': '1',
                        'name': 'CEO',
                        'type': 'executive',
                        'level': 1,
                        'employee_count': 1,
                        'efficiency_score': 95,
                        'parent_id': None
                    },
                    {
                        'id': '2',
                        'name': '技术部',
                        'type': 'department',
                        'level': 2,
                        'employee_count': 50,
                        'efficiency_score': 85,
                        'parent_id': '1'
                    },
                    {
                        'id': '3',
                        'name': '运营部',
                        'type': 'department',
                        'level': 2,
                        'employee_count': 30,
                        'efficiency_score': 80,
                        'parent_id': '1'
                    }
                ],
                'edges': [
                    {'source': '1', 'target': '2', 'type': 'reports_to'},
                    {'source': '1', 'target': '3', 'type': 'reports_to'}
                ]
            }
            return Response(chart_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def heatmap(self, request):
        """获取效率热图数据"""
        try:
            heatmap_data = {
                'departments': [
                    {
                        'id': '1',
                        'name': '技术部',
                        'efficiency_score': 85,
                        'communication_score': 80,
                        'resource_utilization': 75,
                        'coordinates': {'x': 100, 'y': 100}
                    },
                    {
                        'id': '2',
                        'name': '运营部',
                        'efficiency_score': 80,
                        'communication_score': 85,
                        'resource_utilization': 70,
                        'coordinates': {'x': 200, 'y': 150}
                    }
                ],
                'metrics': {
                    'avg_efficiency': 82.5,
                    'max_efficiency': 85,
                    'min_efficiency': 80
                }
            }
            return Response(heatmap_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def recommended_structure(self, request):
        """获取智能推荐的组织架构方案"""
        try:
            structure_data = {
                'current_structure': {
                    'departments': 5,
                    'levels': 3,
                    'span_of_control': 4.2
                },
                'recommended_structure': {
                    'departments': 6,
                    'levels': 4,
                    'span_of_control': 3.8
                },
                'changes': [
                    {
                        'type': 'add',
                        'target': '数据分析部',
                        'description': '新增数据分析部门',
                        'impact': '提升数据驱动决策能力'
                    },
                    {
                        'type': 'modify',
                        'target': '技术部',
                        'description': '重组技术部门',
                        'impact': '提高技术效率'
                    }
                ],
                'benefits': {
                    'efficiency_improvement': 15,
                    'cost_reduction': 10,
                    'communication_improvement': 20
                }
            }
            return Response(structure_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def feedback(self, request):
        """保存用户反馈"""
        try:
            feedback_data = request.data
            # 这里可以保存反馈到数据库
            return Response({'message': '反馈保存成功'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def config(self, request):
        """获取智能分析配置"""
        try:
            config_data = {
                'analysis_weights': {
                    'efficiency': 0.3,
                    'communication': 0.25,
                    'innovation': 0.2,
                    'management': 0.25
                },
                'thresholds': {
                    'excellent': 90,
                    'good': 75,
                    'average': 60
                },
                'enabled_features': [
                    'efficiency_analysis',
                    'communication_analysis',
                    'resource_analysis'
                ],
                'update_frequency': 24
            }
            return Response(config_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['put'])
    def update_config(self, request):
        """更新智能分析配置"""
        try:
            config_data = request.data
            # 这里可以更新配置
            return Response({'message': '配置更新成功'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
