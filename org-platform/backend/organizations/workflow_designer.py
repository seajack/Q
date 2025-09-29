"""
工作流可视化设计器后端模块
提供工作流设计、版本管理、测试执行等功能
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


class NodeType(models.TextChoices):
    """节点类型枚举"""
    START = 'start', '开始'
    TIMER = 'timer', '定时器'
    APPROVAL = 'approval', '审批'
    NOTIFICATION = 'notification', '通知'
    DATA = 'data', '数据处理'
    CONDITION = 'condition', '条件判断'
    END = 'end', '结束'
    ERROR = 'error', '错误处理'


class WorkflowStatus(models.TextChoices):
    """工作流状态"""
    DRAFT = 'draft', '草稿'
    ACTIVE = 'active', '激活'
    INACTIVE = 'inactive', '停用'
    ARCHIVED = 'archived', '归档'


class ExecutionStatus(models.TextChoices):
    """执行状态"""
    PENDING = 'pending', '等待中'
    RUNNING = 'running', '执行中'
    COMPLETED = 'completed', '已完成'
    FAILED = 'failed', '失败'
    CANCELLED = 'cancelled', '已取消'


@dataclass
class NodeConfig:
    """节点配置数据类"""
    node_id: str
    node_type: str
    name: str
    x: float
    y: float
    config: Dict[str, Any]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ConnectionConfig:
    """连接配置数据类"""
    connection_id: str
    source_id: str
    target_id: str
    source_port: Optional[str] = None
    target_port: Optional[str] = None
    connection_type: str = 'default'
    label: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


class WorkflowDesign(models.Model):
    """工作流设计模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='工作流名称')
    description = models.TextField(blank=True, verbose_name='描述')
    category = models.CharField(max_length=100, blank=True, verbose_name='分类')
    
    # 设计数据
    nodes = models.JSONField(default=list, verbose_name='节点配置')
    connections = models.JSONField(default=list, verbose_name='连接配置')
    canvas_config = models.JSONField(default=dict, verbose_name='画布配置')
    
    # 状态和版本
    status = models.CharField(
        max_length=20, 
        choices=WorkflowStatus.choices, 
        default=WorkflowStatus.DRAFT,
        verbose_name='状态'
    )
    current_version = models.CharField(max_length=50, default='v1.0.0', verbose_name='当前版本')
    
    # 元数据
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 统计信息
    execution_count = models.IntegerField(default=0, verbose_name='执行次数')
    success_rate = models.FloatField(default=0.0, verbose_name='成功率')
    
    class Meta:
        verbose_name = '工作流设计'
        verbose_name_plural = '工作流设计'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} ({self.current_version})"
    
    def get_node_count(self):
        """获取节点数量"""
        return len(self.nodes)
    
    def get_connection_count(self):
        """获取连接数量"""
        return len(self.connections)
    
    def validate_workflow(self):
        """验证工作流配置"""
        errors = []
        
        # 检查是否有开始节点
        start_nodes = [node for node in self.nodes if node.get('type') == 'start']
        if not start_nodes:
            errors.append('工作流必须包含至少一个开始节点')
        elif len(start_nodes) > 1:
            errors.append('工作流只能包含一个开始节点')
        
        # 检查是否有结束节点
        end_nodes = [node for node in self.nodes if node.get('type') in ['end', 'error']]
        if not end_nodes:
            errors.append('工作流必须包含至少一个结束节点')
        
        # 检查节点连接
        node_ids = {node.get('id') for node in self.nodes}
        for connection in self.connections:
            source_id = connection.get('sourceId')
            target_id = connection.get('targetId')
            
            if source_id not in node_ids:
                errors.append(f'连接源节点 {source_id} 不存在')
            if target_id not in node_ids:
                errors.append(f'连接目标节点 {target_id} 不存在')
        
        if errors:
            raise ValidationError(errors)
        
        return True


class WorkflowVersion(models.Model):
    """工作流版本模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(WorkflowDesign, on_delete=models.CASCADE, related_name='versions')
    version_name = models.CharField(max_length=50, verbose_name='版本号')
    description = models.TextField(verbose_name='版本描述')
    
    # 版本快照
    nodes_snapshot = models.JSONField(verbose_name='节点快照')
    connections_snapshot = models.JSONField(verbose_name='连接快照')
    canvas_snapshot = models.JSONField(default=dict, verbose_name='画布快照')
    
    # 变更信息
    changes = models.JSONField(default=list, verbose_name='变更记录')
    tags = models.JSONField(default=list, verbose_name='标签')
    
    # 元数据
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    # 统计信息
    is_current = models.BooleanField(default=False, verbose_name='是否当前版本')
    
    class Meta:
        verbose_name = '工作流版本'
        verbose_name_plural = '工作流版本'
        ordering = ['-created_at']
        unique_together = ['workflow', 'version_name']
    
    def __str__(self):
        return f"{self.workflow.name} - {self.version_name}"
    
    def set_as_current(self):
        """设置为当前版本"""
        with transaction.atomic():
            # 取消其他版本的当前状态
            WorkflowVersion.objects.filter(
                workflow=self.workflow, 
                is_current=True
            ).update(is_current=False)
            
            # 设置当前版本
            self.is_current = True
            self.save()
            
            # 更新工作流的当前版本
            self.workflow.current_version = self.version_name
            self.workflow.nodes = self.nodes_snapshot
            self.workflow.connections = self.connections_snapshot
            self.workflow.canvas_config = self.canvas_snapshot
            self.workflow.save()


class WorkflowExecution(models.Model):
    """工作流执行记录"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(WorkflowDesign, on_delete=models.CASCADE, related_name='executions')
    version = models.ForeignKey(WorkflowVersion, on_delete=models.SET_NULL, null=True, blank=True)
    
    # 执行信息
    execution_id = models.CharField(max_length=100, unique=True, verbose_name='执行ID')
    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PENDING,
        verbose_name='执行状态'
    )
    
    # 输入输出数据
    input_data = models.JSONField(default=dict, verbose_name='输入数据')
    output_data = models.JSONField(default=dict, verbose_name='输出数据')
    
    # 执行日志
    execution_logs = models.JSONField(default=list, verbose_name='执行日志')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    # 时间信息
    started_at = models.DateTimeField(verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    duration = models.FloatField(null=True, blank=True, verbose_name='执行时长(秒)')
    
    # 执行上下文
    current_node = models.CharField(max_length=100, blank=True, verbose_name='当前节点')
    execution_context = models.JSONField(default=dict, verbose_name='执行上下文')
    
    class Meta:
        verbose_name = '工作流执行'
        verbose_name_plural = '工作流执行'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.workflow.name} - {self.execution_id}"
    
    def add_log(self, level: str, message: str, node_id: str = None):
        """添加执行日志"""
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'level': level,
            'message': message,
            'node_id': node_id
        }
        self.execution_logs.append(log_entry)
        self.save(update_fields=['execution_logs'])
    
    def complete_execution(self, success: bool = True, error_message: str = None):
        """完成执行"""
        self.completed_at = timezone.now()
        self.duration = (self.completed_at - self.started_at).total_seconds()
        
        if success:
            self.status = ExecutionStatus.COMPLETED
        else:
            self.status = ExecutionStatus.FAILED
            if error_message:
                self.error_message = error_message
        
        self.save()


class WorkflowDesigner:
    """工作流设计器核心类"""
    
    def __init__(self, workflow_id: str = None):
        self.workflow = None
        if workflow_id:
            self.workflow = WorkflowDesign.objects.get(id=workflow_id)
    
    def create_workflow(self, name: str, description: str, user: User) -> WorkflowDesign:
        """创建新工作流"""
        workflow = WorkflowDesign.objects.create(
            name=name,
            description=description,
            created_by=user
        )
        
        # 创建初始版本
        self.create_version(
            workflow=workflow,
            version_name='v1.0.0',
            description='初始版本',
            user=user
        )
        
        self.workflow = workflow
        return workflow
    
    def add_node(self, node_config: NodeConfig) -> bool:
        """添加节点"""
        if not self.workflow:
            return False
        
        # 验证节点配置
        if not self._validate_node_config(node_config):
            return False
        
        # 添加节点
        self.workflow.nodes.append(node_config.to_dict())
        self.workflow.save()
        
        return True
    
    def update_node(self, node_id: str, updates: Dict[str, Any]) -> bool:
        """更新节点"""
        if not self.workflow:
            return False
        
        for i, node in enumerate(self.workflow.nodes):
            if node.get('node_id') == node_id:
                node.update(updates)
                self.workflow.nodes[i] = node
                self.workflow.save()
                return True
        
        return False
    
    def delete_node(self, node_id: str) -> bool:
        """删除节点"""
        if not self.workflow:
            return False
        
        # 删除节点
        self.workflow.nodes = [
            node for node in self.workflow.nodes 
            if node.get('node_id') != node_id
        ]
        
        # 删除相关连接
        self.workflow.connections = [
            conn for conn in self.workflow.connections
            if conn.get('source_id') != node_id and conn.get('target_id') != node_id
        ]
        
        self.workflow.save()
        return True
    
    def add_connection(self, connection_config: ConnectionConfig) -> bool:
        """添加连接"""
        if not self.workflow:
            return False
        
        # 验证连接配置
        if not self._validate_connection_config(connection_config):
            return False
        
        # 添加连接
        self.workflow.connections.append(connection_config.to_dict())
        self.workflow.save()
        
        return True
    
    def delete_connection(self, connection_id: str) -> bool:
        """删除连接"""
        if not self.workflow:
            return False
        
        self.workflow.connections = [
            conn for conn in self.workflow.connections
            if conn.get('connection_id') != connection_id
        ]
        
        self.workflow.save()
        return True
    
    def create_version(self, workflow: WorkflowDesign, version_name: str, 
                      description: str, user: User, tags: List[str] = None) -> WorkflowVersion:
        """创建版本"""
        
        # 计算变更
        changes = self._calculate_changes(workflow, version_name)
        
        version = WorkflowVersion.objects.create(
            workflow=workflow,
            version_name=version_name,
            description=description,
            nodes_snapshot=workflow.nodes.copy(),
            connections_snapshot=workflow.connections.copy(),
            canvas_snapshot=workflow.canvas_config.copy(),
            changes=changes,
            tags=tags or [],
            created_by=user
        )
        
        # 设置为当前版本
        version.set_as_current()
        
        return version
    
    def rollback_to_version(self, version_id: str) -> bool:
        """回滚到指定版本"""
        try:
            version = WorkflowVersion.objects.get(id=version_id)
            version.set_as_current()
            return True
        except WorkflowVersion.DoesNotExist:
            return False
    
    def test_workflow(self, input_data: Dict[str, Any]) -> WorkflowExecution:
        """测试工作流"""
        if not self.workflow:
            raise ValueError("未指定工作流")
        
        # 验证工作流
        self.workflow.validate_workflow()
        
        # 创建执行记录
        execution = WorkflowExecution.objects.create(
            workflow=self.workflow,
            execution_id=f"test_{uuid.uuid4().hex[:8]}",
            input_data=input_data,
            started_at=timezone.now()
        )
        
        # 执行工作流
        try:
            self._execute_workflow(execution)
            execution.complete_execution(success=True)
        except Exception as e:
            execution.complete_execution(success=False, error_message=str(e))
        
        return execution
    
    def _validate_node_config(self, node_config: NodeConfig) -> bool:
        """验证节点配置"""
        # 检查节点ID唯一性
        existing_ids = {node.get('node_id') for node in self.workflow.nodes}
        if node_config.node_id in existing_ids:
            return False
        
        # 检查节点类型
        if node_config.node_type not in [choice[0] for choice in NodeType.choices]:
            return False
        
        return True
    
    def _validate_connection_config(self, connection_config: ConnectionConfig) -> bool:
        """验证连接配置"""
        # 检查源节点和目标节点是否存在
        node_ids = {node.get('node_id') for node in self.workflow.nodes}
        
        if connection_config.source_id not in node_ids:
            return False
        if connection_config.target_id not in node_ids:
            return False
        
        # 检查是否已存在相同连接
        for conn in self.workflow.connections:
            if (conn.get('source_id') == connection_config.source_id and 
                conn.get('target_id') == connection_config.target_id):
                return False
        
        return True
    
    def _calculate_changes(self, workflow: WorkflowDesign, version_name: str) -> List[Dict]:
        """计算版本变更"""
        changes = []
        
        # 获取上一个版本
        previous_version = workflow.versions.filter(is_current=True).first()
        
        if previous_version:
            # 比较节点变更
            old_nodes = {node.get('node_id'): node for node in previous_version.nodes_snapshot}
            new_nodes = {node.get('node_id'): node for node in workflow.nodes}
            
            # 新增节点
            for node_id in new_nodes.keys() - old_nodes.keys():
                changes.append({
                    'id': str(uuid.uuid4()),
                    'type': 'add',
                    'description': f'新增节点: {new_nodes[node_id].get("name", node_id)}'
                })
            
            # 删除节点
            for node_id in old_nodes.keys() - new_nodes.keys():
                changes.append({
                    'id': str(uuid.uuid4()),
                    'type': 'remove',
                    'description': f'删除节点: {old_nodes[node_id].get("name", node_id)}'
                })
            
            # 修改节点
            for node_id in old_nodes.keys() & new_nodes.keys():
                if old_nodes[node_id] != new_nodes[node_id]:
                    changes.append({
                        'id': str(uuid.uuid4()),
                        'type': 'modify',
                        'description': f'修改节点: {new_nodes[node_id].get("name", node_id)}'
                    })
        
        return changes
    
    def _execute_workflow(self, execution: WorkflowExecution):
        """执行工作流（模拟）"""
        execution.add_log('info', '开始执行工作流')
        
        # 找到开始节点
        start_nodes = [node for node in execution.workflow.nodes if node.get('type') == 'start']
        if not start_nodes:
            raise ValueError('未找到开始节点')
        
        current_node = start_nodes[0]
        execution.current_node = current_node.get('node_id')
        execution.save()
        
        # 模拟执行各个节点
        visited_nodes = set()
        
        while current_node and current_node.get('node_id') not in visited_nodes:
            node_id = current_node.get('node_id')
            node_type = current_node.get('type')
            node_name = current_node.get('name', node_id)
            
            execution.add_log('info', f'执行节点: {node_name}', node_id)
            visited_nodes.add(node_id)
            
            # 模拟节点执行时间
            import time
            time.sleep(0.1)
            
            # 根据节点类型执行不同逻辑
            if node_type == 'end':
                execution.add_log('info', '工作流执行完成')
                break
            elif node_type == 'error':
                execution.add_log('error', '工作流执行出错')
                raise Exception('工作流执行出错')
            
            # 找到下一个节点
            next_connections = [
                conn for conn in execution.workflow.connections
                if conn.get('source_id') == node_id
            ]
            
            if next_connections:
                next_node_id = next_connections[0].get('target_id')
                current_node = next(
                    (node for node in execution.workflow.nodes if node.get('node_id') == next_node_id),
                    None
                )
                if current_node:
                    execution.current_node = current_node.get('node_id')
                    execution.save()
            else:
                break
        
        execution.add_log('info', '工作流执行结束')
