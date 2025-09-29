"""
集成管理序列化器
"""

from rest_framework import serializers
from .integration_models import (
    IntegrationSystem, IntegrationGateway, SyncRule, SyncLog,
    IntegrationMapping, IntegrationTest, APIGateway, APIRoute,
    APIMonitor, DataSyncRule, IntegrationConfig
)


class IntegrationSystemSerializer(serializers.ModelSerializer):
    """集成系统序列化器"""
    system_type_display = serializers.CharField(source='get_system_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = IntegrationSystem
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class IntegrationGatewaySerializer(serializers.ModelSerializer):
    """集成网关序列化器"""
    gateway_type_display = serializers.CharField(source='get_gateway_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = IntegrationGateway
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class SyncRuleSerializer(serializers.ModelSerializer):
    """同步规则序列化器"""
    sync_type_display = serializers.CharField(source='get_sync_type_display', read_only=True)
    sync_direction_display = serializers.CharField(source='get_sync_direction_display', read_only=True)
    source_system_name = serializers.CharField(source='source_system.name', read_only=True)
    target_system_name = serializers.CharField(source='target_system.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = SyncRule
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class SyncLogSerializer(serializers.ModelSerializer):
    """同步日志序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sync_rule_name = serializers.CharField(source='sync_rule.name', read_only=True)
    
    class Meta:
        model = SyncLog
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class IntegrationMappingSerializer(serializers.ModelSerializer):
    """集成映射序列化器"""
    
    class Meta:
        model = IntegrationMapping
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class IntegrationTestSerializer(serializers.ModelSerializer):
    """集成测试序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    integration_system_name = serializers.CharField(source='integration_system.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = IntegrationTest
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class IntegrationStatsSerializer(serializers.Serializer):
    """集成统计序列化器"""
    total_systems = serializers.IntegerField()
    active_systems = serializers.IntegerField()
    total_gateways = serializers.IntegerField()
    active_gateways = serializers.IntegerField()
    total_sync_rules = serializers.IntegerField()
    active_sync_rules = serializers.IntegerField()
    recent_sync_logs = serializers.IntegerField()
    success_rate = serializers.FloatField()


class SyncRuleTestSerializer(serializers.Serializer):
    """同步规则测试序列化器"""
    test_type = serializers.CharField()
    test_config = serializers.DictField()
    expected_result = serializers.DictField()


class APIGatewaySerializer(serializers.ModelSerializer):
    """API网关序列化器"""
    
    class Meta:
        model = APIGateway
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class APIRouteSerializer(serializers.ModelSerializer):
    """API路由序列化器"""
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    
    class Meta:
        model = APIRoute
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class APIMonitorSerializer(serializers.ModelSerializer):
    """API监控序列化器"""
    
    class Meta:
        model = APIMonitor
        fields = '__all__'
        read_only_fields = ('id', 'timestamp')


class DataSyncRuleSerializer(serializers.ModelSerializer):
    """数据同步规则序列化器"""
    sync_type_display = serializers.CharField(source='get_sync_type_display', read_only=True)
    
    class Meta:
        model = DataSyncRule
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class IntegrationConfigSerializer(serializers.ModelSerializer):
    """集成配置序列化器"""
    
    class Meta:
        model = IntegrationConfig
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class IntegrationSystemTestSerializer(serializers.Serializer):
    """集成系统测试序列化器"""
    test_type = serializers.CharField()
    test_config = serializers.DictField()
    expected_result = serializers.DictField()