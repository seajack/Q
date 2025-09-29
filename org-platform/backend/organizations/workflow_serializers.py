"""
工作流相关序列化器
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import WorkflowRule, WorkflowRuleExecution, WorkflowTemplate


class WorkflowRuleSerializer(serializers.ModelSerializer):
    """工作流规则序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    success_rate = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    rule_type_display = serializers.CharField(source='get_rule_type_display', read_only=True)

    class Meta:
        model = WorkflowRule
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'execution_count', 'last_executed', 'success_count', 'failure_count')

    def get_success_rate(self, obj):
        """获取成功率"""
        return obj.get_success_rate()


class WorkflowRuleCreateSerializer(serializers.ModelSerializer):
    """工作流规则创建序列化器"""
    class Meta:
        model = WorkflowRule
        fields = ['name', 'code', 'description', 'rule_type', 'trigger_conditions', 'execution_actions', 'priority', 'is_active']

    def validate_code(self, value):
        """验证规则编码唯一性"""
        if WorkflowRule.objects.filter(code=value).exists():
            raise serializers.ValidationError("规则编码已存在")
        return value

    def validate_trigger_conditions(self, value):
        """验证触发条件格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("触发条件必须是JSON对象")
        
        required_fields = ['event_type']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"触发条件缺少必需字段: {field}")
        
        return value

    def validate_execution_actions(self, value):
        """验证执行动作格式"""
        if not isinstance(value, list):
            raise serializers.ValidationError("执行动作必须是数组")
        
        for action in value:
            if not isinstance(action, dict):
                raise serializers.ValidationError("执行动作必须是对象")
            
            if 'action' not in action:
                raise serializers.ValidationError("执行动作缺少action字段")
        
        return value


class WorkflowRuleExecutionSerializer(serializers.ModelSerializer):
    """工作流规则执行记录序列化器"""
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    executed_by_name = serializers.CharField(source='executed_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowRuleExecution
        fields = '__all__'
        read_only_fields = ('id', 'started_at', 'completed_at', 'duration')

    def get_duration_display(self, obj):
        """获取执行时长显示"""
        if obj.duration:
            total_seconds = obj.duration.total_seconds()
            if total_seconds < 60:
                return f"{total_seconds:.1f}秒"
            elif total_seconds < 3600:
                return f"{total_seconds/60:.1f}分钟"
            else:
                return f"{total_seconds/3600:.1f}小时"
        return None


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    """工作流模板序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = WorkflowTemplate
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'usage_count')

    def validate_code(self, value):
        """验证模板编码唯一性"""
        if WorkflowTemplate.objects.filter(code=value).exists():
            raise serializers.ValidationError("模板编码已存在")
        return value


class WorkflowRuleExecutionSerializer(serializers.Serializer):
    """工作流规则执行序列化器"""
    context = serializers.JSONField(required=False, default=dict)
    trigger_data = serializers.JSONField(required=False, default=dict)

    def validate_context(self, value):
        """验证执行上下文"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("执行上下文必须是JSON对象")
        return value

    def validate_trigger_data(self, value):
        """验证触发数据"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("触发数据必须是JSON对象")
        return value


class WorkflowRuleTestSerializer(serializers.Serializer):
    """工作流规则测试序列化器"""
    test_data = serializers.JSONField(required=True)
    
    def validate_test_data(self, value):
        """验证测试数据"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("测试数据必须是JSON对象")
        
        required_fields = ['event_type', 'table', 'operation', 'record']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"测试数据缺少必需字段: {field}")
        
        return value


class WorkflowStatsSerializer(serializers.Serializer):
    """工作流统计序列化器"""
    total_rules = serializers.IntegerField()
    active_rules = serializers.IntegerField()
    total_executions = serializers.IntegerField()
    successful_executions = serializers.IntegerField()
    failed_executions = serializers.IntegerField()
    success_rate = serializers.FloatField()
    avg_execution_time = serializers.DurationField()
    most_used_rules = serializers.ListField(child=serializers.DictField())
    recent_executions = serializers.ListField(child=serializers.DictField())
