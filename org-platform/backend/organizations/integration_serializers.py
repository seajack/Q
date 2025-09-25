from rest_framework import serializers
from .integration_models import (
    IntegrationSystem, APIGateway, APIRoute, DataSyncRule, 
    SyncLog, APIMonitor, IntegrationConfig
)


class IntegrationSystemSerializer(serializers.ModelSerializer):
    """集成系统序列化器"""
    system_type_display = serializers.CharField(source='get_system_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = IntegrationSystem
        fields = [
            'id', 'name', 'system_type', 'system_type_display', 'base_url', 
            'api_version', 'status', 'status_display', 'auth_type', 'auth_config',
            'timeout', 'retry_count', 'rate_limit', 'sync_enabled', 'sync_interval',
            'last_sync_time', 'monitoring_enabled', 'health_check_url', 'alert_email',
            'description', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'last_sync_time']
    
    def validate_auth_config(self, value):
        """验证认证配置"""
        auth_type = self.initial_data.get('auth_type')
        
        if auth_type == 'basic':
            required_fields = ['username', 'password']
            for field in required_fields:
                if field not in value:
                    raise serializers.ValidationError(f"基础认证需要 {field} 字段")
        
        elif auth_type == 'token':
            if 'token' not in value:
                raise serializers.ValidationError("Token认证需要 token 字段")
        
        elif auth_type == 'api_key':
            required_fields = ['api_key']
            for field in required_fields:
                if field not in value:
                    raise serializers.ValidationError(f"API Key认证需要 {field} 字段")
        
        return value


class APIGatewaySerializer(serializers.ModelSerializer):
    """API网关序列化器"""
    route_count = serializers.SerializerMethodField()
    active_route_count = serializers.SerializerMethodField()
    
    class Meta:
        model = APIGateway
        fields = [
            'id', 'name', 'base_url', 'description', 'rate_limit_enabled',
            'rate_limit_per_minute', 'rate_limit_per_hour', 'monitoring_enabled',
            'log_level', 'cors_enabled', 'cors_origins', 'api_key_required',
            'is_active', 'route_count', 'active_route_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_route_count(self, obj):
        return obj.routes.count()
    
    def get_active_route_count(self, obj):
        return obj.routes.filter(is_active=True).count()


class APIRouteSerializer(serializers.ModelSerializer):
    """API路由序列化器"""
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    gateway_name = serializers.CharField(source='gateway.name', read_only=True)
    
    class Meta:
        model = APIRoute
        fields = [
            'id', 'gateway', 'gateway_name', 'name', 'path', 'method', 'method_display',
            'target_url', 'rate_limit', 'burst_limit', 'cache_enabled', 'cache_ttl',
            'auth_required', 'roles_required', 'request_transform', 'response_transform',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_path(self, value):
        """验证路径格式"""
        if not value.startswith('/'):
            value = '/' + value
        return value
    
    def validate(self, data):
        """验证数据"""
        # 检查路径和方法的唯一性
        if 'gateway' in data and 'path' in data and 'method' in data:
            existing = APIRoute.objects.filter(
                gateway=data['gateway'],
                path=data['path'],
                method=data['method']
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing.exists():
                raise serializers.ValidationError("相同网关下路径和方法的组合必须唯一")
        
        return data


class DataSyncRuleSerializer(serializers.ModelSerializer):
    """数据同步规则序列化器"""
    sync_type_display = serializers.CharField(source='get_sync_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_system_name = serializers.CharField(source='source_system.name', read_only=True)
    target_system_name = serializers.CharField(source='target_system.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = DataSyncRule
        fields = [
            'id', 'name', 'source_system', 'source_system_name', 'target_system', 'target_system_name',
            'sync_type', 'sync_type_display', 'status', 'status_display', 'source_table', 'target_table',
            'field_mapping', 'filter_conditions', 'batch_size', 'sync_interval', 'max_retry_count',
            'data_cleaning_enabled', 'cleaning_rules', 'validation_enabled', 'validation_rules',
            'monitoring_enabled', 'alert_on_error', 'alert_on_delay', 'delay_threshold',
            'description', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def validate_field_mapping(self, value):
        """验证字段映射"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("字段映射必须是字典格式")
        
        # 检查是否有空值
        for key, val in value.items():
            if not key or not val:
                raise serializers.ValidationError("字段映射的键和值不能为空")
        
        return value
    
    def validate_cleaning_rules(self, value):
        """验证清洗规则"""
        if not isinstance(value, list):
            raise serializers.ValidationError("清洗规则必须是列表格式")
        
        valid_types = ['trim', 'lowercase', 'uppercase', 'remove_special_chars', 'default_value']
        for rule in value:
            if not isinstance(rule, dict):
                raise serializers.ValidationError("每个清洗规则必须是字典格式")
            
            if 'field' not in rule or 'type' not in rule:
                raise serializers.ValidationError("清洗规则必须包含 field 和 type 字段")
            
            if rule['type'] not in valid_types:
                raise serializers.ValidationError(f"清洗规则类型必须是: {', '.join(valid_types)}")
        
        return value
    
    def validate_validation_rules(self, value):
        """验证校验规则"""
        if not isinstance(value, list):
            raise serializers.ValidationError("校验规则必须是列表格式")
        
        valid_types = ['required', 'email', 'phone', 'length']
        for rule in value:
            if not isinstance(rule, dict):
                raise serializers.ValidationError("每个校验规则必须是字典格式")
            
            if 'field' not in rule or 'type' not in rule:
                raise serializers.ValidationError("校验规则必须包含 field 和 type 字段")
            
            if rule['type'] not in valid_types:
                raise serializers.ValidationError(f"校验规则类型必须是: {', '.join(valid_types)}")
        
        return value


class SyncLogSerializer(serializers.ModelSerializer):
    """同步日志序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sync_rule_name = serializers.CharField(source='sync_rule.name', read_only=True)
    duration_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = SyncLog
        fields = [
            'id', 'sync_rule', 'sync_rule_name', 'status', 'status_display',
            'start_time', 'end_time', 'total_records', 'success_records',
            'error_records', 'skipped_records', 'error_message', 'error_details',
            'duration_seconds', 'duration_formatted', 'records_per_second', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_duration_formatted(self, obj):
        """格式化持续时间"""
        if obj.duration_seconds:
            if obj.duration_seconds < 60:
                return f"{obj.duration_seconds:.2f}秒"
            elif obj.duration_seconds < 3600:
                minutes = obj.duration_seconds / 60
                return f"{minutes:.2f}分钟"
            else:
                hours = obj.duration_seconds / 3600
                return f"{hours:.2f}小时"
        return "0秒"


class APIMonitorSerializer(serializers.ModelSerializer):
    """API监控序列化器"""
    route_name = serializers.CharField(source='route.name', read_only=True)
    route_path = serializers.CharField(source='route.path', read_only=True)
    route_method = serializers.CharField(source='route.method', read_only=True)
    
    class Meta:
        model = APIMonitor
        fields = [
            'id', 'route', 'route_name', 'route_path', 'route_method', 'timestamp',
            'request_count', 'success_count', 'error_count', 'avg_response_time',
            'max_response_time', 'min_response_time', 'error_rate', 'status_code_distribution'
        ]
        read_only_fields = ['timestamp']


class IntegrationConfigSerializer(serializers.ModelSerializer):
    """集成配置序列化器"""
    config_type_display = serializers.CharField(source='get_config_type_display', read_only=True)
    system_name = serializers.CharField(source='system.name', read_only=True)
    
    class Meta:
        model = IntegrationConfig
        fields = [
            'id', 'system', 'system_name', 'config_key', 'config_value',
            'config_type', 'config_type_display', 'is_encrypted', 'description',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_config_value(self, value):
        """验证配置值"""
        config_type = self.initial_data.get('config_type')
        
        if config_type == 'integer':
            try:
                int(value)
            except ValueError:
                raise serializers.ValidationError("配置值必须是整数")
        
        elif config_type == 'boolean':
            if value.lower() not in ['true', 'false', '1', '0']:
                raise serializers.ValidationError("配置值必须是布尔值")
        
        elif config_type == 'json':
            try:
                import json
                json.loads(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError("配置值必须是有效的JSON格式")
        
        return value


class IntegrationSystemCreateSerializer(serializers.ModelSerializer):
    """集成系统创建序列化器"""
    
    class Meta:
        model = IntegrationSystem
        fields = [
            'name', 'system_type', 'base_url', 'api_version', 'auth_type', 'auth_config',
            'timeout', 'retry_count', 'rate_limit', 'sync_enabled', 'sync_interval',
            'monitoring_enabled', 'health_check_url', 'alert_email', 'description'
        ]
    
    def create(self, validated_data):
        """创建集成系统"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class DataSyncRuleCreateSerializer(serializers.ModelSerializer):
    """数据同步规则创建序列化器"""
    
    class Meta:
        model = DataSyncRule
        fields = [
            'name', 'source_system', 'target_system', 'sync_type', 'source_table',
            'target_table', 'field_mapping', 'filter_conditions', 'batch_size',
            'sync_interval', 'max_retry_count', 'data_cleaning_enabled', 'cleaning_rules',
            'validation_enabled', 'validation_rules', 'monitoring_enabled',
            'alert_on_error', 'alert_on_delay', 'delay_threshold', 'description'
        ]
    
    def create(self, validated_data):
        """创建数据同步规则"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class IntegrationTestSerializer(serializers.Serializer):
    """集成测试序列化器"""
    system_id = serializers.IntegerField()
    test_type = serializers.ChoiceField(choices=[
        ('connection', '连接测试'),
        ('auth', '认证测试'),
        ('data_sync', '数据同步测试'),
        ('api_call', 'API调用测试')
    ])
    test_data = serializers.JSONField(required=False, allow_null=True)
    test_endpoint = serializers.CharField(required=False, allow_blank=True)


class SyncExecutionSerializer(serializers.Serializer):
    """同步执行序列化器"""
    sync_rule_id = serializers.IntegerField()
    force_sync = serializers.BooleanField(default=False)
    sync_data = serializers.JSONField(required=False, allow_null=True)
