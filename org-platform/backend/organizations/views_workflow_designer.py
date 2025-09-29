"""
工作流设计器API视图
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from .workflow_designer import (
    WorkflowDesign, WorkflowVersion, WorkflowExecution,
    WorkflowDesigner, NodeConfig, ConnectionConfig
)
from .serializers_workflow import (
    WorkflowDesignSerializer, WorkflowVersionSerializer,
    WorkflowExecutionSerializer, NodeConfigSerializer,
    ConnectionConfigSerializer
)


class WorkflowDesignViewSet(viewsets.ModelViewSet):
    """工作流设计视图集"""
    queryset = WorkflowDesign.objects.all()
    serializer_class = WorkflowDesignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """过滤当前用户的工作流"""
        return WorkflowDesign.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        """创建工作流时设置创建者"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_node(self, request, pk=None):
        """添加节点"""
        workflow = self.get_object()
        designer = WorkflowDesigner(workflow.id)
        
        serializer = NodeConfigSerializer(data=request.data)
        if serializer.is_valid():
            node_config = NodeConfig(**serializer.validated_data)
            
            if designer.add_node(node_config):
                return Response({'success': True, 'message': '节点添加成功'})
            else:
                return Response(
                    {'success': False, 'message': '节点添加失败'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def update_node(self, request, pk=None):
        """更新节点"""
        workflow = self.get_object()
        designer = WorkflowDesigner(workflow.id)
        
        node_id = request.data.get('node_id')
        updates = request.data.get('updates', {})
        
        if designer.update_node(node_id, updates):
            return Response({'success': True, 'message': '节点更新成功'})
        else:
            return Response(
                {'success': False, 'message': '节点更新失败'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['delete'])
    def delete_node(self, request, pk=None):
        """删除节点"""
        workflow = self.get_object()
        designer = WorkflowDesigner(workflow.id)
        
        node_id = request.query_params.get('node_id')
        
        if designer.delete_node(node_id):
            return Response({'success': True, 'message': '节点删除成功'})
        else:
            return Response(
                {'success': False, 'message': '节点删除失败'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def add_connection(self, request, pk=None):
        """添加连接"""
        workflow = self.get_object()
        designer = WorkflowDesigner(workflow.id)
        
        serializer = ConnectionConfigSerializer(data=request.data)
        if serializer.is_valid():
            connection_config = ConnectionConfig(**serializer.validated_data)
            
            if designer.add_connection(connection_config):
                return Response({'success': True, 'message': '连接添加成功'})
            else:
                return Response(
                    {'success': False, 'message': '连接添加失败'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def delete_connection(self, request, pk=None):
        """删除连接"""
        workflow = self.get_object()
        designer = WorkflowDesigner(workflow.id)
        
        connection_id = request.query_params.get('connection_id')
        
        if designer.delete_connection(connection_id):
            return Response({'success': True, 'message': '连接删除成功'})
        else:
            return Response(
                {'success': False, 'message': '连接删除失败'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """验证工作流"""
        workflow = self.get_object()
        
        try:
            workflow.validate_workflow()
            return Response({
                'success': True,
                'message': '工作流验证通过',
                'valid': True
            })
        except Exception as e:
            return Response({
                'success': True,
                'message': '工作流验证失败',
                'valid': False,
                'errors': str(e).split('\n') if '\n' in str(e) else [str(e)]
            })
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """测试工作流"""
        workflow = self.get_object()
        designer = WorkflowDesigner(workflow.id)
        
        input_data = request.data.get('input_data', {})
        
        try:
            execution = designer.test_workflow(input_data)
            serializer = WorkflowExecutionSerializer(execution)
            
            return Response({
                'success': True,
                'message': '工作流测试完成',
                'execution': serializer.data
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'工作流测试失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """获取工作流版本列表"""
        workflow = self.get_object()
        versions = workflow.versions.all()
        serializer = WorkflowVersionSerializer(versions, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """创建新版本"""
        workflow = self.get_object()
        designer = WorkflowDesigner(workflow.id)
        
        version_name = request.data.get('version_name')
        description = request.data.get('description')
        tags = request.data.get('tags', [])
        
        if not version_name or not description:
            return Response({
                'success': False,
                'message': '版本号和描述不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            version = designer.create_version(
                workflow=workflow,
                version_name=version_name,
                description=description,
                user=request.user,
                tags=tags
            )
            
            serializer = WorkflowVersionSerializer(version)
            return Response({
                'success': True,
                'message': '版本创建成功',
                'version': serializer.data
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'版本创建失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def rollback(self, request, pk=None):
        """回滚到指定版本"""
        workflow = self.get_object()
        designer = WorkflowDesigner(workflow.id)
        
        version_id = request.data.get('version_id')
        
        if designer.rollback_to_version(version_id):
            return Response({
                'success': True,
                'message': '版本回滚成功'
            })
        else:
            return Response({
                'success': False,
                'message': '版本回滚失败'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """获取执行历史"""
        workflow = self.get_object()
        executions = workflow.executions.all()[:20]  # 最近20次执行
        serializer = WorkflowExecutionSerializer(executions, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取工作流统计信息"""
        workflow = self.get_object()
        
        # 计算统计数据
        total_executions = workflow.executions.count()
        successful_executions = workflow.executions.filter(
            status='completed'
        ).count()
        
        success_rate = (
            (successful_executions / total_executions * 100) 
            if total_executions > 0 else 0
        )
        
        # 最近7天的执行次数
        from datetime import timedelta
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_executions = workflow.executions.filter(
            started_at__gte=seven_days_ago
        ).count()
        
        # 平均执行时间
        completed_executions = workflow.executions.filter(
            status='completed',
            duration__isnull=False
        )
        
        avg_duration = 0
        if completed_executions.exists():
            total_duration = sum(ex.duration for ex in completed_executions)
            avg_duration = total_duration / completed_executions.count()
        
        return Response({
            'success': True,
            'data': {
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'success_rate': round(success_rate, 2),
                'recent_executions': recent_executions,
                'average_duration': round(avg_duration, 2),
                'node_count': workflow.get_node_count(),
                'connection_count': workflow.get_connection_count(),
                'version_count': workflow.versions.count()
            }
        })


class WorkflowVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """工作流版本视图集"""
    queryset = WorkflowVersion.objects.all()
    serializer_class = WorkflowVersionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """过滤当前用户的版本"""
        return WorkflowVersion.objects.filter(
            workflow__created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        """设置为当前版本"""
        version = self.get_object()
        
        try:
            version.set_as_current()
            return Response({
                'success': True,
                'message': '版本切换成功'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'版本切换失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def compare(self, request, pk=None):
        """版本对比"""
        source_version = self.get_object()
        target_version_id = request.query_params.get('target_version_id')
        
        if not target_version_id:
            return Response({
                'success': False,
                'message': '请指定对比目标版本'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_version = WorkflowVersion.objects.get(id=target_version_id)
            
            # 计算差异
            differences = self._calculate_version_differences(
                source_version, target_version
            )
            
            return Response({
                'success': True,
                'data': {
                    'source_version': WorkflowVersionSerializer(source_version).data,
                    'target_version': WorkflowVersionSerializer(target_version).data,
                    'differences': differences
                }
            })
        except WorkflowVersion.DoesNotExist:
            return Response({
                'success': False,
                'message': '目标版本不存在'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def _calculate_version_differences(self, source_version, target_version):
        """计算版本差异"""
        differences = {
            'nodes': {
                'added': [],
                'removed': [],
                'modified': []
            },
            'connections': {
                'added': [],
                'removed': [],
                'modified': []
            }
        }
        
        # 比较节点
        source_nodes = {node.get('node_id'): node for node in source_version.nodes_snapshot}
        target_nodes = {node.get('node_id'): node for node in target_version.nodes_snapshot}
        
        # 新增的节点
        for node_id in target_nodes.keys() - source_nodes.keys():
            differences['nodes']['added'].append(target_nodes[node_id])
        
        # 删除的节点
        for node_id in source_nodes.keys() - target_nodes.keys():
            differences['nodes']['removed'].append(source_nodes[node_id])
        
        # 修改的节点
        for node_id in source_nodes.keys() & target_nodes.keys():
            if source_nodes[node_id] != target_nodes[node_id]:
                differences['nodes']['modified'].append({
                    'node_id': node_id,
                    'source': source_nodes[node_id],
                    'target': target_nodes[node_id]
                })
        
        # 比较连接（类似逻辑）
        source_connections = {
            f"{conn.get('source_id')}-{conn.get('target_id')}": conn 
            for conn in source_version.connections_snapshot
        }
        target_connections = {
            f"{conn.get('source_id')}-{conn.get('target_id')}": conn 
            for conn in target_version.connections_snapshot
        }
        
        # 新增的连接
        for conn_key in target_connections.keys() - source_connections.keys():
            differences['connections']['added'].append(target_connections[conn_key])
        
        # 删除的连接
        for conn_key in source_connections.keys() - target_connections.keys():
            differences['connections']['removed'].append(source_connections[conn_key])
        
        return differences


class WorkflowExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """工作流执行视图集"""
    queryset = WorkflowExecution.objects.all()
    serializer_class = WorkflowExecutionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """过滤当前用户的执行记录"""
        return WorkflowExecution.objects.filter(
            workflow__created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消执行"""
        execution = self.get_object()
        
        if execution.status in ['pending', 'running']:
            execution.status = 'cancelled'
            execution.completed_at = timezone.now()
            execution.save()
            
            return Response({
                'success': True,
                'message': '执行已取消'
            })
        else:
            return Response({
                'success': False,
                'message': '无法取消已完成的执行'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workflow_templates(request):
    """获取工作流模板"""
    templates = [
        {
            'id': 'approval_template',
            'name': '审批流程模板',
            'description': '标准的审批流程，包含申请、审批、通知等节点',
            'category': 'approval',
            'nodes': [
                {
                    'node_id': 'start_1',
                    'node_type': 'start',
                    'name': '开始',
                    'x': 100,
                    'y': 100,
                    'config': {}
                },
                {
                    'node_id': 'approval_1',
                    'node_type': 'approval',
                    'name': '部门审批',
                    'x': 300,
                    'y': 100,
                    'config': {
                        'approver': 'direct_supervisor',
                        'timeout': 24
                    }
                },
                {
                    'node_id': 'notification_1',
                    'node_type': 'notification',
                    'name': '结果通知',
                    'x': 500,
                    'y': 100,
                    'config': {
                        'type': 'email',
                        'template': 'approval_result'
                    }
                },
                {
                    'node_id': 'end_1',
                    'node_type': 'end',
                    'name': '结束',
                    'x': 700,
                    'y': 100,
                    'config': {}
                }
            ],
            'connections': [
                {
                    'connection_id': 'conn_1',
                    'source_id': 'start_1',
                    'target_id': 'approval_1'
                },
                {
                    'connection_id': 'conn_2',
                    'source_id': 'approval_1',
                    'target_id': 'notification_1'
                },
                {
                    'connection_id': 'conn_3',
                    'source_id': 'notification_1',
                    'target_id': 'end_1'
                }
            ]
        },
        {
            'id': 'data_processing_template',
            'name': '数据处理模板',
            'description': '数据处理流程，包含数据获取、处理、存储等节点',
            'category': 'data',
            'nodes': [
                {
                    'node_id': 'start_1',
                    'node_type': 'start',
                    'name': '开始',
                    'x': 100,
                    'y': 100,
                    'config': {}
                },
                {
                    'node_id': 'data_1',
                    'node_type': 'data',
                    'name': '数据获取',
                    'x': 300,
                    'y': 100,
                    'config': {
                        'source': 'database',
                        'query': 'SELECT * FROM table'
                    }
                },
                {
                    'node_id': 'condition_1',
                    'node_type': 'condition',
                    'name': '数据验证',
                    'x': 500,
                    'y': 100,
                    'config': {
                        'condition': 'data_count > 0'
                    }
                },
                {
                    'node_id': 'end_1',
                    'node_type': 'end',
                    'name': '成功结束',
                    'x': 700,
                    'y': 50,
                    'config': {}
                },
                {
                    'node_id': 'error_1',
                    'node_type': 'error',
                    'name': '错误处理',
                    'x': 700,
                    'y': 150,
                    'config': {}
                }
            ],
            'connections': [
                {
                    'connection_id': 'conn_1',
                    'source_id': 'start_1',
                    'target_id': 'data_1'
                },
                {
                    'connection_id': 'conn_2',
                    'source_id': 'data_1',
                    'target_id': 'condition_1'
                },
                {
                    'connection_id': 'conn_3',
                    'source_id': 'condition_1',
                    'target_id': 'end_1',
                    'connection_type': 'success',
                    'label': '验证通过'
                },
                {
                    'connection_id': 'conn_4',
                    'source_id': 'condition_1',
                    'target_id': 'error_1',
                    'connection_type': 'failure',
                    'label': '验证失败'
                }
            ]
        }
    ]
    
    return Response({
        'success': True,
        'data': templates
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_from_template(request):
    """从模板创建工作流"""
    template_id = request.data.get('template_id')
    workflow_name = request.data.get('name')
    workflow_description = request.data.get('description', '')
    
    if not template_id or not workflow_name:
        return Response({
            'success': False,
            'message': '模板ID和工作流名称不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 获取模板（这里简化处理，实际应该从数据库获取）
    templates_response = workflow_templates(request)
    templates = templates_response.data['data']
    
    template = next((t for t in templates if t['id'] == template_id), None)
    if not template:
        return Response({
            'success': False,
            'message': '模板不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # 创建工作流
        workflow = WorkflowDesign.objects.create(
            name=workflow_name,
            description=workflow_description,
            nodes=template['nodes'],
            connections=template['connections'],
            created_by=request.user
        )
        
        # 创建初始版本
        designer = WorkflowDesigner(workflow.id)
        designer.create_version(
            workflow=workflow,
            version_name='v1.0.0',
            description='从模板创建',
            user=request.user
        )
        
        serializer = WorkflowDesignSerializer(workflow)
        return Response({
            'success': True,
            'message': '工作流创建成功',
            'workflow': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'工作流创建失败: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
