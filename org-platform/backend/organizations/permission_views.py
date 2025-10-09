from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from .permission_models import (
    Permission, Role, RolePermission, UserRole, DataPermission,
    RoleDataPermission, PermissionLog, FieldPermission, DepartmentPermission
)
from .permission_services import PermissionService, DataPermissionService, FieldPermissionService
from .serializers import (
    PermissionSerializer, RoleSerializer, RolePermissionSerializer,
    UserRoleSerializer, DataPermissionSerializer, RoleDataPermissionSerializer,
    PermissionLogSerializer, FieldPermissionSerializer, DepartmentPermissionSerializer
)
from rest_framework.serializers import ModelSerializer
import logging

logger = logging.getLogger(__name__)


class PermissionViewSet(viewsets.ModelViewSet):
    """权限管理"""
    queryset = Permission.objects.all()  # 返回所有权限
    serializer_class = PermissionSerializer
    permission_classes = [AllowAny]  # 临时允许匿名访问，用于开发环境
    filter_backends = [SearchFilter, OrderingFilter]
    # filterset_fields = ['permission_type', 'level']  # 暂时禁用过滤器
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['sort_order', 'name']
    ordering = ['sort_order', 'name']
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取权限树"""
        # 暂时返回空数组，因为数据库字段不匹配
        return Response([])
        
        # 构建树形结构
        permission_dict = {}
        root_permissions = []
        
        for permission in permissions:
            permission_dict[permission.id] = {
                'id': permission.id,
                'name': permission.name,
                'code': permission.code,
                'permission_type': permission.permission_type,
                'level': permission.level,
                'children': []
            }
        
        for permission in permissions:
            if permission.parent:
                permission_dict[permission.parent.id]['children'].append(permission_dict[permission.id])
            else:
                root_permissions.append(permission_dict[permission.id])
        
        return Response(root_permissions)
    
    @action(detail=True, methods=['post'])
    def assign_to_role(self, request, pk=None):
        """将权限分配给角色"""
        permission = self.get_object()
        role_id = request.data.get('role_id')
        is_granted = request.data.get('is_granted', True)
        
        try:
            role = Role.objects.get(id=role_id)
            role_permission, created = RolePermission.objects.get_or_create(
                role=role,
                permission=permission,
                defaults={
                    'is_granted': is_granted,
                    'granted_by': request.user
                }
            )
            
            if not created:
                role_permission.is_granted = is_granted
                role_permission.granted_by = request.user
                role_permission.granted_at = timezone.now()
                role_permission.save()
            
            return Response({
                'success': True,
                'message': '权限分配成功'
            })
        except Role.DoesNotExist:
            return Response({
                'success': False,
                'message': '角色不存在'
            }, status=status.HTTP_400_BAD_REQUEST)


class RoleViewSet(viewsets.ModelViewSet):
    """角色管理"""
    queryset = Role.objects.all()  # 返回所有角色
    serializer_class = RoleSerializer
    permission_classes = [AllowAny]  # 临时允许匿名访问，用于开发环境
    filter_backends = [SearchFilter, OrderingFilter]
    # filterset_fields = ['role_type', 'is_active', 'is_system', 'level']  # 暂时禁用过滤器
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """获取角色权限"""
        role = self.get_object()
        role_permissions = RolePermission.objects.filter(role=role, is_granted=True)
        serializer = RolePermissionSerializer(role_permissions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_permissions(self, request, pk=None):
        """分配权限给角色"""
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        
        # 清除现有权限
        RolePermission.objects.filter(role=role).delete()
        
        # 分配新权限
        for permission_id in permission_ids:
            try:
                permission = Permission.objects.get(id=permission_id)
                RolePermission.objects.create(
                    role=role,
                    permission=permission,
                    is_granted=True,
                    granted_by=request.user
                )
            except Permission.DoesNotExist:
                continue
        
        return Response({
            'success': True,
            'message': '权限分配成功'
        })
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """获取角色用户"""
        role = self.get_object()
        user_roles = UserRole.objects.filter(role=role, is_active=True)
        serializer = UserRoleSerializer(user_roles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_users(self, request, pk=None):
        """分配用户给角色"""
        role = self.get_object()
        user_ids = request.data.get('user_ids', [])
        expires_at = request.data.get('expires_at')
        
        if expires_at:
            expires_at = timezone.datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        assigned_count = 0
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                user_role, created = UserRole.objects.get_or_create(
                    user=user,
                    role=role,
                    defaults={
                        'assigned_by': request.user,
                        'expires_at': expires_at
                    }
                )
                
                if not created:
                    user_role.is_active = True
                    user_role.assigned_by = request.user
                    user_role.assigned_at = timezone.now()
                    user_role.expires_at = expires_at
                    user_role.save()
                
                assigned_count += 1
            except User.DoesNotExist:
                continue
        
        return Response({
            'success': True,
            'message': f'成功分配 {assigned_count} 个用户'
        })


class UserRoleViewSet(viewsets.ModelViewSet):
    """用户角色管理"""
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [AllowAny]  # 临时允许匿名访问，用于开发环境
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'role', 'is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'role__name']
    ordering_fields = ['assigned_at', 'expires_at']
    ordering = ['-assigned_at']
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """撤销用户角色"""
        user_role = self.get_object()
        user_role.is_active = False
        user_role.save()
        
        return Response({
            'success': True,
            'message': '角色撤销成功'
        })


class DataPermissionViewSet(viewsets.ModelViewSet):
    """数据权限管理"""
    queryset = DataPermission.objects.all()  # 返回所有数据权限
    serializer_class = DataPermissionSerializer
    permission_classes = [AllowAny]  # 临时允许匿名访问，用于开发环境
    filter_backends = [SearchFilter, OrderingFilter]
    # filterset_fields = ['permission_type', 'scope_type', 'resource_type', 'is_active']  # 暂时禁用过滤器
    search_fields = ['resource', 'permission_type']
    ordering_fields = ['created_at', 'resource']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def assign_to_role(self, request, pk=None):
        """将数据权限分配给角色"""
        data_permission = self.get_object()
        role_id = request.data.get('role_id')
        is_granted = request.data.get('is_granted', True)
        
        try:
            role = Role.objects.get(id=role_id)
            role_data_permission, created = RoleDataPermission.objects.get_or_create(
                role=role,
                data_permission=data_permission,
                defaults={
                    'is_granted': is_granted,
                    'granted_by': request.user
                }
            )
            
            if not created:
                role_data_permission.is_granted = is_granted
                role_data_permission.granted_by = request.user
                role_data_permission.granted_at = timezone.now()
                role_data_permission.save()
            
            return Response({
                'success': True,
                'message': '数据权限分配成功'
            })
        except Role.DoesNotExist:
            return Response({
                'success': False,
                'message': '角色不存在'
            }, status=status.HTTP_400_BAD_REQUEST)


class FieldPermissionViewSet(viewsets.ModelViewSet):
    """字段权限管理"""
    queryset = FieldPermission.objects.all()
    serializer_class = FieldPermissionSerializer
    permission_classes = [AllowAny]  # 临时允许匿名访问，用于开发环境
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'resource_type', 'permission_type', 'is_active']
    search_fields = ['field_name', 'resource_type']
    ordering_fields = ['created_at', 'field_name']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def user_fields(self, request):
        """获取用户字段权限"""
        user_id = request.query_params.get('user_id')
        resource_type = request.query_params.get('resource_type')
        
        if not user_id:
            return Response({'error': '用户ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(user_id=user_id)
        
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DepartmentPermissionViewSet(viewsets.ModelViewSet):
    """部门权限管理"""
    queryset = DepartmentPermission.objects.all()
    serializer_class = DepartmentPermissionSerializer
    permission_classes = [AllowAny]  # 临时允许匿名访问，用于开发环境
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'department', 'data_scope', 'is_active']
    search_fields = ['user__username', 'department__name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class PermissionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """权限日志查看"""
    queryset = PermissionLog.objects.none()  # 暂时返回空查询集
    serializer_class = PermissionLogSerializer
    permission_classes = [AllowAny]  # 临时允许匿名访问，用于开发环境
    filter_backends = [SearchFilter, OrderingFilter]
    # filterset_fields = ['user', 'action_type', 'resource_type', 'result']  # 暂时禁用过滤器
    search_fields = ['user__username']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class PermissionDashboardViewSet(viewsets.ViewSet):
    """权限仪表板"""
    permission_classes = [AllowAny]  # 临时允许匿名访问，用于开发环境
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取权限概览"""
        try:
            # 统计信息
            total_permissions = Permission.objects.count()
            active_permissions = Permission.objects.count()  # 暂时使用总数，因为数据库字段不匹配
            
            total_roles = Role.objects.count()
            active_roles = Role.objects.count()  # 暂时使用总数，因为数据库字段不匹配
            
            total_users = User.objects.count()
            users_with_roles = UserRole.objects.filter(is_active=True).values('user').distinct().count()
            
            # 权限类型分布
            permission_types = Permission.objects.values('permission_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # 角色类型分布 - 暂时返回空数组
            role_types = []
            
            # 最近权限操作 - 暂时返回空数组
            recent_logs_data = []
            
            return Response({
                'permissions': {
                    'total': total_permissions,
                    'active': active_permissions,
                    'inactive': total_permissions - active_permissions
                },
                'roles': {
                    'total': total_roles,
                    'active': active_roles,
                    'inactive': total_roles - active_roles
                },
                'users': {
                    'total': total_users,
                    'with_roles': users_with_roles,
                    'without_roles': total_users - users_with_roles
                },
                'permission_types': list(permission_types),
                'role_types': list(role_types),
                'recent_logs': recent_logs_data
            })
        except Exception as e:
            logger.error(f"获取权限概览失败: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def user_permissions(self, request):
        """获取用户权限"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': '用户ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            permission_service = PermissionService(user)
            
            # 获取用户权限
            permissions = permission_service.get_user_permissions()
            permission_data = PermissionSerializer(permissions, many=True).data
            
            # 获取用户角色
            roles = permission_service.get_user_roles()
            role_data = RoleSerializer(roles, many=True).data
            
            # 获取数据权限
            data_permission_service = DataPermissionService(user)
            data_scopes = {}
            for resource_type in ['employee', 'department', 'position']:
                data_scopes[resource_type] = data_permission_service.get_data_scope(resource_type)
            
            return Response({
                'permissions': permission_data,
                'roles': role_data,
                'data_scopes': data_scopes
            })
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"获取用户权限失败: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def check_permission(self, request):
        """检查权限"""
        user_id = request.query_params.get('user_id')
        permission_code = request.query_params.get('permission_code')
        
        if not user_id or not permission_code:
            return Response({'error': '用户ID和权限编码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            permission_service = PermissionService(user)
            
            has_permission = permission_service.has_permission(permission_code)
            
            return Response({
                'user_id': user_id,
                'permission_code': permission_code,
                'has_permission': has_permission
            })
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"检查权限失败: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 用户序列化器
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']


class UserViewSet(viewsets.ModelViewSet):
    """用户管理"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # 临时允许匿名访问，用于开发环境
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined']
    ordering = ['-date_joined']
