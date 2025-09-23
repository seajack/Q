from rest_framework import serializers
from .models import (
    EvaluationCycle, EvaluationIndicator, EvaluationTask, 
    EvaluationScore, EvaluationResult
)


class EvaluationCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCycle
        fields = '__all__'


class EvaluationIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationIndicator
        fields = '__all__'


class EvaluationTaskSerializer(serializers.ModelSerializer):
    evaluatee_name = serializers.CharField(source='evaluatee.name', read_only=True)
    evaluator_name = serializers.CharField(source='evaluator.name', read_only=True)
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
    evaluatee_name = serializers.CharField(source='evaluatee.name', read_only=True)
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