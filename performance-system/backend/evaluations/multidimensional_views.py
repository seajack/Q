from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Avg, Count, Sum
from django.db import transaction
from django.utils import timezone
from .multidimensional_models import (
    EvaluationDimension, EvaluationMethod, EvaluationCycleType,
    MultidimensionalEvaluation, MultidimensionalIndicator, EvaluationTemplate,
    TemplateDimension
)
from .multidimensional_serializers import (
    EvaluationDimensionSerializer, EvaluationMethodSerializer,
    EvaluationCycleTypeSerializer, MultidimensionalEvaluationSerializer,
    MultidimensionalEvaluationListSerializer, MultidimensionalIndicatorSerializer,
    EvaluationTemplateSerializer, EvaluationDimensionDetailSerializer,
    EvaluationMethodDetailSerializer, MultidimensionalEvaluationCreateSerializer,
    EvaluationStatisticsSerializer
)


class EvaluationDimensionViewSet(viewsets.ModelViewSet):
    """评估维度视图集"""
    queryset = EvaluationDimension.objects.all()
    serializer_class = EvaluationDimensionSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EvaluationDimensionDetailSerializer
        return EvaluationDimensionSerializer
    
    @action(detail=True, methods=['get'])
    def indicators(self, request, pk=None):
        """获取维度的指标列表"""
        dimension = self.get_object()
        indicators = dimension.indicators.filter(is_active=True)
        serializer = MultidimensionalIndicatorSerializer(indicators, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取启用的维度"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def batch_update_weights(self, request):
        """批量更新维度权重"""
        weight_data = request.data.get('weights', {})
        
        with transaction.atomic():
            for dimension_id, weight in weight_data.items():
                try:
                    dimension = EvaluationDimension.objects.get(id=dimension_id)
                    dimension.weight = weight
                    dimension.save()
                except EvaluationDimension.DoesNotExist:
                    continue
        
        return Response({'message': '权重更新成功'})


class EvaluationMethodViewSet(viewsets.ModelViewSet):
    """评估方法视图集"""
    queryset = EvaluationMethod.objects.all()
    serializer_class = EvaluationMethodSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EvaluationMethodDetailSerializer
        return EvaluationMethodSerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取启用的评估方法"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def templates(self, request, pk=None):
        """获取方法的模板列表"""
        method = self.get_object()
        templates = method.templates.filter(is_active=True)
        serializer = EvaluationTemplateSerializer(templates, many=True)
        return Response(serializer.data)


class EvaluationCycleTypeViewSet(viewsets.ModelViewSet):
    """评估周期类型视图集"""
    queryset = EvaluationCycleType.objects.all()
    serializer_class = EvaluationCycleTypeSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取启用的周期类型"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MultidimensionalEvaluationViewSet(viewsets.ModelViewSet):
    """多维度评估视图集"""
    queryset = MultidimensionalEvaluation.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MultidimensionalEvaluationListSerializer
        elif self.action == 'create':
            return MultidimensionalEvaluationCreateSerializer
        return MultidimensionalEvaluationSerializer
    
    def get_queryset(self):
        """根据用户权限过滤查询集"""
        queryset = super().get_queryset()
        
        # 根据用户角色过滤数据
        user = self.request.user
        if hasattr(user, 'employee'):
            employee = user.employee
            # 只显示该员工相关的评估
            queryset = queryset.filter(
                Q(evaluator=employee) | Q(evaluatee=employee)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_evaluations(self, request):
        """获取我的评估任务"""
        if not hasattr(request.user, 'employee'):
            return Response({'error': '用户没有关联的员工信息'}, status=status.HTTP_400_BAD_REQUEST)
        
        employee = request.user.employee
        queryset = self.get_queryset().filter(evaluator=employee)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_evaluated(self, request):
        """获取我被评估的记录"""
        if not hasattr(request.user, 'employee'):
            return Response({'error': '用户没有关联的员工信息'}, status=status.HTTP_400_BAD_REQUEST)
        
        employee = request.user.employee
        queryset = self.get_queryset().filter(evaluatee=employee)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """提交评估"""
        evaluation = self.get_object()
        
        if evaluation.status != 'draft':
            return Response({'error': '只能提交草稿状态的评估'}, status=status.HTTP_400_BAD_REQUEST)
        
        evaluation.status = 'submitted'
        evaluation.save()
        
        serializer = self.get_serializer(evaluation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """审核评估"""
        evaluation = self.get_object()
        
        if evaluation.status != 'submitted':
            return Response({'error': '只能审核已提交的评估'}, status=status.HTTP_400_BAD_REQUEST)
        
        evaluation.status = 'reviewed'
        evaluation.save()
        
        serializer = self.get_serializer(evaluation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        """确定评估结果"""
        evaluation = self.get_object()
        
        if evaluation.status != 'reviewed':
            return Response({'error': '只能确定已审核的评估'}, status=status.HTTP_400_BAD_REQUEST)
        
        evaluation.status = 'finalized'
        evaluation.save()
        
        serializer = self.get_serializer(evaluation)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取评估统计信息"""
        cycle_id = request.query_params.get('cycle_id')
        if not cycle_id:
            return Response({'error': '需要提供cycle_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(cycle_id=cycle_id)
        
        # 计算统计数据
        total_evaluations = queryset.count()
        completed_evaluations = queryset.filter(status__in=['submitted', 'reviewed', 'finalized']).count()
        pending_evaluations = queryset.filter(status='draft').count()
        
        # 计算平均分
        avg_score = queryset.filter(total_score__isnull=False).aggregate(
            avg_score=Avg('total_score')
        )['avg_score'] or 0
        
        # 按维度统计
        dimension_scores = {}
        for evaluation in queryset.filter(total_score__isnull=False):
            for dimension_id, score in evaluation.dimensions.items():
                if dimension_id not in dimension_scores:
                    dimension_scores[dimension_id] = []
                dimension_scores[dimension_id].append(float(score))
        
        # 计算各维度平均分
        for dimension_id in dimension_scores:
            scores = dimension_scores[dimension_id]
            dimension_scores[dimension_id] = sum(scores) / len(scores) if scores else 0
        
        # 按方法统计
        method_stats = queryset.values('evaluation_method__name').annotate(
            count=Count('id'),
            avg_score=Avg('total_score')
        )
        
        statistics_data = {
            'total_evaluations': total_evaluations,
            'completed_evaluations': completed_evaluations,
            'pending_evaluations': pending_evaluations,
            'average_score': float(avg_score),
            'dimension_scores': dimension_scores,
            'method_statistics': list(method_stats)
        }
        
        serializer = EvaluationStatisticsSerializer(statistics_data)
        return Response(serializer.data)


class MultidimensionalIndicatorViewSet(viewsets.ModelViewSet):
    """多维度评估指标视图集"""
    queryset = MultidimensionalIndicator.objects.all()
    serializer_class = MultidimensionalIndicatorSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def by_dimension(self, request):
        """根据维度获取指标"""
        dimension_id = request.query_params.get('dimension_id')
        if not dimension_id:
            return Response({'error': '需要提供dimension_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(dimension_id=dimension_id, is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EvaluationTemplateViewSet(viewsets.ModelViewSet):
    """评估模板视图集"""
    queryset = EvaluationTemplate.objects.all()
    serializer_class = EvaluationTemplateSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取启用的模板"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """获取默认模板"""
        queryset = self.get_queryset().filter(is_default=True, is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def copy(self, request, pk=None):
        """复制模板"""
        template = self.get_object()
        
        new_template = EvaluationTemplate.objects.create(
            name=f"{template.name} (副本)",
            description=template.description,
            evaluation_method=template.evaluation_method,
            created_by=request.user
        )
        
        # 复制维度关联
        for template_dimension in template.templatedimension_set.all():
            TemplateDimension.objects.create(
                template=new_template,
                dimension=template_dimension.dimension,
                weight=template_dimension.weight,
                order=template_dimension.order
            )
        
        serializer = self.get_serializer(new_template)
        return Response(serializer.data)
