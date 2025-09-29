"""
简单权限管理API视图
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random


class SimplePermissionViewSet(viewsets.ViewSet):
    """简单权限管理API"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def permissions(self, request):
        """获取权限列表"""
        return Response([
            {
                'id': '1',
                'name': '用户管理',
                'code': 'user_management',
                'permission_type': 'menu',
                'permission_type_display': '菜单权限',
                'description': '用户管理模块权限',
                'resource': '/users',
                'action': 'view',
                'status': 'active',
                'status_display': '激活',
                'is_system': True,
                'sort_order': 1
            },
            {
                'id': '2',
                'name': '角色管理',
                'code': 'role_management',
                'permission_type': 'menu',
                'permission_type_display': '菜单权限',
                'description': '角色管理模块权限',
                'resource': '/roles',
                'action': 'view',
                'status': 'active',
                'status_display': '激活',
                'is_system': True,
                'sort_order': 2
            },
            {
                'id': '3',
                'name': '权限管理',
                'code': 'permission_management',
                'permission_type': 'menu',
                'permission_type_display': '菜单权限',
                'description': '权限管理模块权限',
                'resource': '/permissions',
                'action': 'view',
                'status': 'active',
                'status_display': '激活',
                'is_system': True,
                'sort_order': 3
            },
            {
                'id': '4',
                'name': '创建用户',
                'code': 'user_create',
                'permission_type': 'button',
                'permission_type_display': '按钮权限',
                'description': '创建用户按钮权限',
                'resource': '/users',
                'action': 'create',
                'status': 'active',
                'status_display': '激活',
                'is_system': False,
                'sort_order': 4
            },
            {
                'id': '5',
                'name': '编辑用户',
                'code': 'user_edit',
                'permission_type': 'button',
                'permission_type_display': '按钮权限',
                'description': '编辑用户按钮权限',
                'resource': '/users',
                'action': 'edit',
                'status': 'active',
                'status_display': '激活',
                'is_system': False,
                'sort_order': 5
            }
        ])

    @action(detail=False, methods=['get'])
    def roles(self, request):
        """获取角色列表"""
        return Response([
            {
                'id': '1',
                'name': '系统管理员',
                'code': 'system_admin',
                'description': '系统管理员角色，拥有所有权限',
                'status': 'active',
                'status_display': '激活',
                'is_system': True,
                'permissions_count': 15,
                'users_count': 2
            },
            {
                'id': '2',
                'name': '部门管理员',
                'code': 'department_admin',
                'description': '部门管理员角色，管理本部门用户',
                'status': 'active',
                'status_display': '激活',
                'is_system': False,
                'permissions_count': 8,
                'users_count': 5
            },
            {
                'id': '3',
                'name': '普通用户',
                'code': 'normal_user',
                'description': '普通用户角色，基础权限',
                'status': 'active',
                'status_display': '激活',
                'is_system': False,
                'permissions_count': 3,
                'users_count': 20
            },
            {
                'id': '4',
                'name': '访客',
                'code': 'guest',
                'description': '访客角色，只读权限',
                'status': 'active',
                'status_display': '激活',
                'is_system': False,
                'permissions_count': 1,
                'users_count': 10
            }
        ])

    @action(detail=False, methods=['get'])
    def users(self, request):
        """获取用户列表"""
        return Response([
            {
                'id': 1,
                'username': 'admin',
                'email': 'admin@example.com',
                'first_name': '系统',
                'last_name': '管理员',
                'is_active': True,
                'is_active_display': '激活',
                'last_login': '2025-09-29T10:30:00Z',
                'date_joined': '2025-01-01T00:00:00Z',
                'roles': [
                    {
                        'id': '1',
                        'name': '系统管理员',
                        'code': 'system_admin'
                    }
                ]
            },
            {
                'id': 2,
                'username': 'manager1',
                'email': 'manager1@example.com',
                'first_name': '张',
                'last_name': '经理',
                'is_active': True,
                'is_active_display': '激活',
                'last_login': '2025-09-29T09:15:00Z',
                'date_joined': '2025-02-01T00:00:00Z',
                'roles': [
                    {
                        'id': '2',
                        'name': '部门管理员',
                        'code': 'department_admin'
                    }
                ]
            },
            {
                'id': 3,
                'username': 'user1',
                'email': 'user1@example.com',
                'first_name': '李',
                'last_name': '员工',
                'is_active': True,
                'is_active_display': '激活',
                'last_login': '2025-09-29T08:45:00Z',
                'date_joined': '2025-03-01T00:00:00Z',
                'roles': [
                    {
                        'id': '3',
                        'name': '普通用户',
                        'code': 'normal_user'
                    }
                ]
            }
        ])

    @action(detail=False, methods=['get'])
    def permission_logs(self, request):
        """获取权限日志列表"""
        return Response([
            {
                'id': '1',
                'user': 1,
                'user_name': 'admin',
                'action': 'login',
                'action_display': '登录',
                'resource': '/login',
                'description': '用户登录系统',
                'ip_address': '192.168.1.100',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'result': 'success',
                'result_display': '成功',
                'created_at': '2025-09-29T15:30:00Z'
            },
            {
                'id': '2',
                'user': 2,
                'user_name': 'manager1',
                'action': 'assign',
                'action_display': '分配',
                'resource': '/users/3',
                'description': '为用户分配角色',
                'ip_address': '192.168.1.101',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'result': 'success',
                'result_display': '成功',
                'created_at': '2025-09-29T15:25:00Z'
            },
            {
                'id': '3',
                'user': 3,
                'user_name': 'user1',
                'action': 'access',
                'action_display': '访问',
                'resource': '/dashboard',
                'description': '访问仪表板',
                'ip_address': '192.168.1.102',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'result': 'success',
                'result_display': '成功',
                'created_at': '2025-09-29T15:20:00Z'
            },
            {
                'id': '4',
                'user': 3,
                'user_name': 'user1',
                'action': 'deny',
                'action_display': '拒绝',
                'resource': '/admin',
                'description': '尝试访问管理页面',
                'ip_address': '192.168.1.102',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'result': 'denied',
                'result_display': '拒绝',
                'created_at': '2025-09-29T15:15:00Z'
            }
        ])

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取权限管理统计信息"""
        return Response({
            'total_permissions': 25,
            'active_permissions': 23,
            'total_roles': 4,
            'active_roles': 4,
            'total_users': 35,
            'active_users': 33,
            'recent_logs': 156,
            'permission_distribution': {
                'menu': 8,
                'button': 12,
                'api': 3,
                'data': 2
            },
            'role_distribution': {
                'system_admin': 2,
                'department_admin': 5,
                'normal_user': 20,
                'guest': 10
            }
        })
