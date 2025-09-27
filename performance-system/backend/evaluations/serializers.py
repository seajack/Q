from rest_framework import serializers
from .models import (
    EvaluationCycle, EvaluationIndicator, EvaluationTask, 
    EvaluationScore, EvaluationResult, Employee, EvaluationRule, ManualEvaluationAssignment,
    PositionWeight
)


class EvaluationCycleSerializer(serializers.ModelSerializer):
    evaluation_rule_name = serializers.CharField(source='evaluation_rule.name', read_only=True)
    evaluation_indicators_names = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationCycle
        exclude = ['created_by']  # 排除created_by字段，将在视图中自动设置
    
    def get_evaluation_indicators_names(self, obj):
        """获取考核指标名称列表"""
        return [indicator.name for indicator in obj.evaluation_indicators.all()]
    
    def validate(self, data):
        """验证数据"""
        # 检查开始日期和结束日期
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("开始日期不能晚于结束日期")
        return data


class EvaluationIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationIndicator
        fields = '__all__'
        
    def update(self, instance, validated_data):
        """支持部分更新"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EvaluationTaskSerializer(serializers.ModelSerializer):
    evaluatee_name = serializers.CharField(source='evaluatee.name', read_only=True)
    evaluator_name = serializers.CharField(source='evaluator.name', read_only=True)
    evaluatee_position = serializers.CharField(source='evaluatee.position_name', read_only=True)
    evaluator_position = serializers.CharField(source='evaluator.position_name', read_only=True)
    evaluatee_department = serializers.CharField(source='evaluatee.department_name', read_only=True)
    evaluator_department = serializers.CharField(source='evaluator.department_name', read_only=True)
    evaluatee_position_level = serializers.IntegerField(source='evaluatee.position_level', read_only=True)
    evaluator_position_level = serializers.IntegerField(source='evaluator.position_level', read_only=True)
    cycle_name = serializers.CharField(source='cycle.name', read_only=True)
    avg_score = serializers.SerializerMethodField()
    
    def get_avg_score(self, obj):
        """计算任务的平均分"""
        from django.db.models import Avg
        avg_score = obj.evaluationscore_set.aggregate(avg=Avg('score'))['avg']
        return round(avg_score or 0, 1)
    
    class Meta:
        model = EvaluationTask
        fields = '__all__'


class PositionWeightSerializer(serializers.ModelSerializer):
    """职级权重序列化器"""
    
    class Meta:
        model = PositionWeight
        fields = '__all__'


class EvaluationScoreSerializer(serializers.ModelSerializer):
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    evaluator_position = serializers.CharField(source='task.evaluator.position_name', read_only=True)
    evaluator_weight = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationScore
        fields = '__all__'
    
    def get_evaluator_weight(self, obj):
        """获取评价人的职级权重"""
        try:
            from .models import PositionWeight
            weight_config = PositionWeight.objects.filter(
                position_id=obj.task.evaluator.position_id,
                is_active=True
            ).first()
            return float(weight_config.weight) if weight_config else 1.0
        except:
            return 1.0


class EvaluationResultSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_department = serializers.CharField(source='employee.department_name', read_only=True)
    employee_position = serializers.CharField(source='employee.position_name', read_only=True)
    cycle_name = serializers.CharField(source='cycle.name', read_only=True)
    
    class Meta:
        model = EvaluationResult
        fields = '__all__'


class EvaluationStatsSerializer(serializers.Serializer):
    """统计信息序列化器"""
    total_cycles = serializers.IntegerField()
    active_cycles = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    total_employees = serializers.IntegerField()
    pending_evaluations = serializers.IntegerField()


class EvaluationRuleSerializer(serializers.ModelSerializer):
    """考核规则序列化器"""
    class Meta:
        model = EvaluationRule
        fields = '__all__'


class ManualEvaluationAssignmentSerializer(serializers.ModelSerializer):
    """手动评价分配序列化器"""
    evaluator_name = serializers.CharField(source='evaluator.name', read_only=True)
    evaluatee_name = serializers.CharField(source='evaluatee.name', read_only=True)
    cycle_name = serializers.CharField(source='cycle.name', read_only=True)
    
    class Meta:
        model = ManualEvaluationAssignment
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']


class EmployeeSerializer(serializers.ModelSerializer):
    """员工序列化器（本地副本）"""
    class Meta:
        model = Employee
        fields = '__all__'