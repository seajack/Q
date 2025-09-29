from rest_framework import serializers
from .multidimensional_models import (
    EvaluationDimension, EvaluationMethod, EvaluationCycleType,
    MultidimensionalEvaluation, MultidimensionalIndicator, EvaluationTemplate,
    TemplateDimension
)


class EvaluationDimensionSerializer(serializers.ModelSerializer):
    """评估维度序列化器"""
    
    class Meta:
        model = EvaluationDimension
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class EvaluationMethodSerializer(serializers.ModelSerializer):
    """评估方法序列化器"""
    
    class Meta:
        model = EvaluationMethod
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class EvaluationCycleTypeSerializer(serializers.ModelSerializer):
    """评估周期类型序列化器"""
    
    class Meta:
        model = EvaluationCycleType
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class MultidimensionalIndicatorSerializer(serializers.ModelSerializer):
    """多维度评估指标序列化器"""
    dimension_name = serializers.CharField(source='dimension.name', read_only=True)
    
    class Meta:
        model = MultidimensionalIndicator
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class TemplateDimensionSerializer(serializers.ModelSerializer):
    """模板维度序列化器"""
    dimension_name = serializers.CharField(source='dimension.name', read_only=True)
    dimension_type = serializers.CharField(source='dimension.dimension_type', read_only=True)
    
    class Meta:
        model = TemplateDimension
        fields = '__all__'


class EvaluationTemplateSerializer(serializers.ModelSerializer):
    """评估模板序列化器"""
    template_dimensions = TemplateDimensionSerializer(many=True, read_only=True)
    evaluation_method_name = serializers.CharField(source='evaluation_method.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = EvaluationTemplate
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        """创建模板时处理维度关联"""
        template = super().create(validated_data)
        # 这里可以添加维度关联的逻辑
        return template


class MultidimensionalEvaluationSerializer(serializers.ModelSerializer):
    """多维度评估序列化器"""
    evaluator_name = serializers.CharField(source='evaluator.name', read_only=True)
    evaluatee_name = serializers.CharField(source='evaluatee.name', read_only=True)
    evaluation_method_name = serializers.CharField(source='evaluation_method.name', read_only=True)
    cycle_name = serializers.CharField(source='cycle.name', read_only=True)
    
    class Meta:
        model = MultidimensionalEvaluation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'total_score', 'weighted_score']
    
    def validate_dimensions(self, value):
        """验证维度评分数据"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("维度评分必须是字典格式")
        
        # 验证每个维度的评分是否在合理范围内
        for dimension_id, score in value.items():
            try:
                score_float = float(score)
                if not (0 <= score_float <= 100):
                    raise serializers.ValidationError(f"维度 {dimension_id} 的评分必须在0-100之间")
            except (ValueError, TypeError):
                raise serializers.ValidationError(f"维度 {dimension_id} 的评分格式不正确")
        
        return value
    
    def create(self, validated_data):
        """创建评估时自动计算分数"""
        instance = super().create(validated_data)
        instance.calculate_total_score()
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        """更新评估时重新计算分数"""
        instance = super().update(instance, validated_data)
        instance.calculate_total_score()
        instance.save()
        return instance


class MultidimensionalEvaluationListSerializer(serializers.ModelSerializer):
    """多维度评估列表序列化器（简化版）"""
    evaluator_name = serializers.CharField(source='evaluator.name', read_only=True)
    evaluatee_name = serializers.CharField(source='evaluatee.name', read_only=True)
    evaluation_method_name = serializers.CharField(source='evaluation_method.name', read_only=True)
    cycle_name = serializers.CharField(source='cycle.name', read_only=True)
    
    class Meta:
        model = MultidimensionalEvaluation
        fields = [
            'id', 'cycle', 'cycle_name', 'evaluator', 'evaluator_name',
            'evaluatee', 'evaluatee_name', 'evaluation_method', 'evaluation_method_name',
            'total_score', 'weighted_score', 'status', 'created_at', 'updated_at'
        ]


class EvaluationDimensionDetailSerializer(serializers.ModelSerializer):
    """评估维度详情序列化器"""
    indicators = MultidimensionalIndicatorSerializer(many=True, read_only=True)
    
    class Meta:
        model = EvaluationDimension
        fields = '__all__'


class EvaluationMethodDetailSerializer(serializers.ModelSerializer):
    """评估方法详情序列化器"""
    templates = EvaluationTemplateSerializer(many=True, read_only=True)
    
    class Meta:
        model = EvaluationMethod
        fields = '__all__'


class MultidimensionalEvaluationCreateSerializer(serializers.ModelSerializer):
    """多维度评估创建序列化器"""
    
    class Meta:
        model = MultidimensionalEvaluation
        fields = [
            'cycle', 'evaluator', 'evaluatee', 'evaluation_method',
            'dimensions', 'comments'
        ]
    
    def validate(self, data):
        """验证评估数据"""
        # 检查评估人和被评估人不能是同一人
        if data['evaluator'] == data['evaluatee']:
            raise serializers.ValidationError("评估人和被评估人不能是同一人")
        
        # 检查是否已经存在相同的评估
        existing = MultidimensionalEvaluation.objects.filter(
            cycle=data['cycle'],
            evaluator=data['evaluator'],
            evaluatee=data['evaluatee'],
            evaluation_method=data['evaluation_method']
        ).exists()
        
        if existing:
            raise serializers.ValidationError("该评估已存在")
        
        return data


class EvaluationStatisticsSerializer(serializers.Serializer):
    """评估统计序列化器"""
    total_evaluations = serializers.IntegerField()
    completed_evaluations = serializers.IntegerField()
    pending_evaluations = serializers.IntegerField()
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    dimension_scores = serializers.DictField()
    method_statistics = serializers.DictField()
