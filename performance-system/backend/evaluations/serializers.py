from rest_framework import serializers
from .models import (
    EvaluationCycle, EvaluationIndicator, EvaluationTask, 
    EvaluationScore, EvaluationResult, Employee, EvaluationRule, ManualEvaluationAssignment
)


class EvaluationCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCycle
        exclude = ['created_by']  # 排除created_by字段，将在视图中自动设置
    
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
    evaluatee_position_level = serializers.IntegerField(source='evaluatee.position_level', read_only=True)
    evaluator_position_level = serializers.IntegerField(source='evaluator.position_level', read_only=True)
    cycle_name = serializers.CharField(source='cycle.name', read_only=True)
    
    class Meta:
        model = EvaluationTask
        fields = '__all__'


class EvaluationScoreSerializer(serializers.ModelSerializer):
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    
    class Meta:
        model = EvaluationScore
        fields = '__all__'


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
    
    class Meta:
        model = ManualEvaluationAssignment
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    """员工序列化器（本地副本）"""
    class Meta:
        model = Employee
        fields = '__all__'