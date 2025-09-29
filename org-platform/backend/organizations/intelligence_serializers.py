"""
智能分析序列化器
"""

from rest_framework import serializers
from .intelligence_models import (
    AnalysisResult, OptimizationRecommendation, OrganizationAnalysis,
    AnalysisHistory, AnalysisConfig, UserFeedback, BenchmarkData
)


class AnalysisResultSerializer(serializers.ModelSerializer):
    """分析结果序列化器"""
    
    class Meta:
        model = AnalysisResult
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class OptimizationRecommendationSerializer(serializers.ModelSerializer):
    """优化建议序列化器"""
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = OptimizationRecommendation
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class OrganizationAnalysisSerializer(serializers.ModelSerializer):
    """组织分析序列化器"""
    analysis_results = AnalysisResultSerializer(many=True, read_only=True)
    recommendations = OptimizationRecommendationSerializer(many=True, read_only=True)
    
    class Meta:
        model = OrganizationAnalysis
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class AnalysisHistorySerializer(serializers.ModelSerializer):
    """分析历史序列化器"""
    
    class Meta:
        model = AnalysisHistory
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class AnalysisConfigSerializer(serializers.ModelSerializer):
    """分析配置序列化器"""
    
    class Meta:
        model = AnalysisConfig
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserFeedbackSerializer(serializers.ModelSerializer):
    """用户反馈序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserFeedback
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')


class BenchmarkDataSerializer(serializers.ModelSerializer):
    """基准数据序列化器"""
    
    class Meta:
        model = BenchmarkData
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class AnalysisSummarySerializer(serializers.Serializer):
    """分析摘要序列化器"""
    total_count = serializers.IntegerField()
    by_priority = serializers.DictField()
    summary = serializers.DictField()


class BenchmarkComparisonSerializer(serializers.Serializer):
    """基准对比序列化器"""
    comparison = serializers.DictField()
    overall_assessment = serializers.CharField()
    industry = serializers.CharField()
    company_size = serializers.CharField()


class SimulationResultSerializer(serializers.Serializer):
    """模拟结果序列化器"""
    current_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    predicted_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    improvement = serializers.DecimalField(max_digits=5, decimal_places=2)
    affected_metrics = serializers.DictField()
    risks = serializers.ListField(child=serializers.CharField())
    timeline = serializers.CharField()


class OrganizationChartSerializer(serializers.Serializer):
    """组织架构图序列化器"""
    nodes = serializers.ListField()
    edges = serializers.ListField()


class EfficiencyHeatmapSerializer(serializers.Serializer):
    """效率热图序列化器"""
    departments = serializers.ListField()
    metrics = serializers.DictField()


class RecommendedStructureSerializer(serializers.Serializer):
    """推荐结构序列化器"""
    current_structure = serializers.DictField()
    recommended_structure = serializers.DictField()
    changes = serializers.ListField()
    benefits = serializers.DictField()
