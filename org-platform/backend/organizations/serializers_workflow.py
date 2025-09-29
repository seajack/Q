"""
工作流设计器序列化器
"""

from rest_framework import serializers
from .workflow_designer import WorkflowDesign, WorkflowVersion, WorkflowExecution


class WorkflowDesignSerializer(serializers.ModelSerializer):
    """工作流设计序列化器"""
    
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    node_count = serializers.SerializerMethodField()
    connection_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowDesign
        fields = [
            'id', 'name', 'description', 'category', 'nodes', 'connections',
            'canvas_config', 'status', 'current_version', 'created_by',
            'created_by_name', 'created_at', 'updated_at', 'execution_count',
            'success_rate', 'node_count', 'connection_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_node_count(self, obj):
        return obj.get_node_count()
    
    def get_connection_count(self, obj):
        return obj.get_connection_count()


class WorkflowVersionSerializer(serializers.ModelSerializer):
    """工作流版本序列化器"""
    
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    
    class Meta:
        model = WorkflowVersion
        fields = [
            'id', 'workflow', 'workflow_name', 'version_name', 'description',
            'nodes_snapshot', 'connections_snapshot', 'canvas_snapshot',
            'changes', 'tags', 'created_by', 'created_by_name', 'created_at',
            'is_current'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """工作流执行序列化器"""
    
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    version_name = serializers.CharField(source='version.version_name', read_only=True)
    
    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow', 'workflow_name', 'version', 'version_name',
            'execution_id', 'status', 'input_data', 'output_data',
            'execution_logs', 'error_message', 'started_at', 'completed_at',
            'duration', 'current_node', 'execution_context'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at', 'duration']


class NodeConfigSerializer(serializers.Serializer):
    """节点配置序列化器"""
    
    node_id = serializers.CharField(max_length=100)
    node_type = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=200)
    x = serializers.FloatField()
    y = serializers.FloatField()
    config = serializers.JSONField(default=dict)


class ConnectionConfigSerializer(serializers.Serializer):
    """连接配置序列化器"""
    
    connection_id = serializers.CharField(max_length=100)
    source_id = serializers.CharField(max_length=100)
    target_id = serializers.CharField(max_length=100)
    source_port = serializers.CharField(max_length=50, required=False, allow_null=True)
    target_port = serializers.CharField(max_length=50, required=False, allow_null=True)
    connection_type = serializers.CharField(max_length=50, default='default')
    label = serializers.CharField(max_length=200, required=False, allow_null=True)
