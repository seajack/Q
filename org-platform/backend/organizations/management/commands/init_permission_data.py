from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from organizations.permission_models import (
    Permission, Role, RolePermission, UserRole, DataPermission,
    RoleDataPermission, FieldPermission, DepartmentPermission
)
from organizations.models import Department, Employee
from django.utils import timezone


class Command(BaseCommand):
    help = '初始化权限管理示例数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化权限管理数据...')

        # 创建权限
        self.create_permissions()
        
        # 创建角色
        self.create_roles()
        
        # 创建数据权限
        self.create_data_permissions()
        
        # 创建字段权限
        self.create_field_permissions()
        
        # 分配权限给角色
        self.assign_permissions_to_roles()
        
        # 分配数据权限给角色
        self.assign_data_permissions_to_roles()
        
        # 分配角色给用户
        self.assign_roles_to_users()

        self.stdout.write(
            self.style.SUCCESS('权限管理示例数据初始化完成！\n')
        )
        self.stdout.write('请访问 http://localhost:3000/permission-management 查看权限管理功能')

    def create_permissions(self):
        """创建权限"""
        self.stdout.write('创建权限...')
        
        # 系统管理权限
        system_permission, created = Permission.objects.get_or_create(
            code='system_management',
            defaults={
                'name': '系统管理',
                'permission_type': 'menu',
                'description': '系统管理菜单权限',
                'level': 1,
                'sort_order': 1
            }
        )
        
        # 用户管理权限
        user_management, created = Permission.objects.get_or_create(
            code='user_management',
            defaults={
                'name': '用户管理',
                'permission_type': 'menu',
                'description': '用户管理菜单权限',
                'level': 2,
                'parent': system_permission,
                'sort_order': 1
            }
        )
        
        Permission.objects.get_or_create(
            code='user_view',
            defaults={
                'name': '查看用户',
                'permission_type': 'button',
                'description': '查看用户列表权限',
                'level': 3,
                'parent': user_management,
                'sort_order': 1
            }
        )
        
        Permission.objects.get_or_create(
            code='user_add',
            defaults={
                'name': '添加用户',
                'permission_type': 'button',
                'description': '添加用户权限',
                'level': 3,
                'parent': user_management,
                'sort_order': 2
            }
        )
        
        Permission.objects.get_or_create(
            code='user_edit',
            defaults={
                'name': '编辑用户',
                'permission_type': 'button',
                'description': '编辑用户权限',
                'level': 3,
                'parent': user_management,
                'sort_order': 3
            }
        )
        
        Permission.objects.get_or_create(
            code='user_delete',
            defaults={
                'name': '删除用户',
                'permission_type': 'button',
                'description': '删除用户权限',
                'level': 3,
                'parent': user_management,
                'sort_order': 4
            }
        )
        
        # 部门管理权限
        dept_management, created = Permission.objects.get_or_create(
            code='department_management',
            defaults={
                'name': '部门管理',
                'permission_type': 'menu',
                'description': '部门管理菜单权限',
                'level': 2,
                'parent': system_permission,
                'sort_order': 2
            }
        )
        
        Permission.objects.get_or_create(
            code='department_view',
            defaults={
                'name': '查看部门',
                'permission_type': 'button',
                'description': '查看部门列表权限',
                'level': 3,
                'parent': dept_management,
                'sort_order': 1
            }
        )
        
        Permission.objects.get_or_create(
            code='department_add',
            defaults={
                'name': '添加部门',
                'permission_type': 'button',
                'description': '添加部门权限',
                'level': 3,
                'parent': dept_management,
                'sort_order': 2
            }
        )
        
        Permission.objects.get_or_create(
            code='department_edit',
            defaults={
                'name': '编辑部门',
                'permission_type': 'button',
                'description': '编辑部门权限',
                'level': 3,
                'parent': dept_management,
                'sort_order': 3
            }
        )
        
        Permission.objects.get_or_create(
            code='department_delete',
            defaults={
                'name': '删除部门',
                'permission_type': 'button',
                'description': '删除部门权限',
                'level': 3,
                'parent': dept_management,
                'sort_order': 4
            }
        )
        
        # 权限管理权限
        permission_management, created = Permission.objects.get_or_create(
            code='permission_management',
            defaults={
                'name': '权限管理',
                'permission_type': 'menu',
                'description': '权限管理菜单权限',
                'level': 2,
                'parent': system_permission,
                'sort_order': 3
            }
        )
        
        Permission.objects.get_or_create(
            code='permission_view',
            defaults={
                'name': '查看权限',
                'permission_type': 'button',
                'description': '查看权限列表权限',
                'level': 3,
                'parent': permission_management,
                'sort_order': 1
            }
        )
        
        Permission.objects.get_or_create(
            code='permission_manage',
            defaults={
                'name': '管理权限',
                'permission_type': 'button',
                'description': '管理权限权限',
                'level': 3,
                'parent': permission_management,
                'sort_order': 2
            }
        )
        
        # API权限
        Permission.objects.get_or_create(
            code='api_access',
            defaults={
                'name': 'API访问权限',
                'permission_type': 'api',
                'description': 'API访问权限',
                'level': 1,
                'resource': '/api/',
                'action': 'GET,POST,PUT,DELETE',
                'sort_order': 10
            }
        )

    def create_roles(self):
        """创建角色"""
        self.stdout.write('创建角色...')
        
        # 获取管理员用户
        admin_user = User.objects.get(username='admin')
        
        # 超级管理员角色
        super_admin_role, created = Role.objects.get_or_create(
            code='super_admin',
            defaults={
                'name': '超级管理员',
                'role_type': 'system',
                'description': '系统超级管理员，拥有所有权限',
                'is_system': True,
                'level': 1,
                'data_scope': 'all',
                'created_by': admin_user
            }
        )
        
        # 系统管理员角色
        system_admin_role, created = Role.objects.get_or_create(
            code='system_admin',
            defaults={
                'name': '系统管理员',
                'role_type': 'system',
                'description': '系统管理员，管理用户和权限',
                'is_system': True,
                'level': 2,
                'data_scope': 'all',
                'created_by': admin_user
            }
        )
        
        # 部门管理员角色
        dept_admin_role, created = Role.objects.get_or_create(
            code='department_admin',
            defaults={
                'name': '部门管理员',
                'role_type': 'department',
                'description': '部门管理员，管理本部门数据',
                'level': 3,
                'data_scope': 'dept_and_child',
                'created_by': admin_user
            }
        )
        
        # 普通用户角色
        user_role, created = Role.objects.get_or_create(
            code='user',
            defaults={
                'name': '普通用户',
                'role_type': 'custom',
                'description': '普通用户，只能查看自己的数据',
                'level': 4,
                'data_scope': 'self',
                'created_by': admin_user
            }
        )

    def create_data_permissions(self):
        """创建数据权限"""
        self.stdout.write('创建数据权限...')
        
        admin_user = User.objects.get(username='admin')
        
        # 全部数据权限
        DataPermission.objects.get_or_create(
            name='全部数据权限',
            defaults={
                'permission_type': 'read',
                'scope_type': 'all',
                'resource_type': 'all',
                'description': '可以访问所有数据',
                'created_by': admin_user
            }
        )
        
        # 部门数据权限
        DataPermission.objects.get_or_create(
            name='部门数据权限',
            defaults={
                'permission_type': 'read',
                'scope_type': 'dept',
                'resource_type': 'employee',
                'description': '可以访问本部门员工数据',
                'created_by': admin_user
            }
        )
        
        # 个人数据权限
        DataPermission.objects.get_or_create(
            name='个人数据权限',
            defaults={
                'permission_type': 'read',
                'scope_type': 'self',
                'resource_type': 'employee',
                'description': '只能访问自己的数据',
                'created_by': admin_user
            }
        )

    def create_field_permissions(self):
        """创建字段权限"""
        self.stdout.write('创建字段权限...')
        
        # 获取所有用户
        users = User.objects.all()
        
        for user in users:
            # 手机号脱敏权限
            FieldPermission.objects.get_or_create(
                user=user,
                resource_type='employee',
                field_name='phone',
                defaults={
                    'permission_type': 'masked',
                    'masking_rule': 'phone',
                    'masking_config': {'prefix_len': 3, 'suffix_len': 4, 'mask_char': '*'}
                }
            )
            
            # 邮箱脱敏权限
            FieldPermission.objects.get_or_create(
                user=user,
                resource_type='employee',
                field_name='email',
                defaults={
                    'permission_type': 'masked',
                    'masking_rule': 'email',
                    'masking_config': {'prefix_len': 2, 'suffix_len': 0, 'mask_char': '*'}
                }
            )

    def assign_permissions_to_roles(self):
        """分配权限给角色"""
        self.stdout.write('分配权限给角色...')
        
        admin_user = User.objects.get(username='admin')
        
        # 获取角色
        super_admin_role = Role.objects.get(code='super_admin')
        system_admin_role = Role.objects.get(code='system_admin')
        dept_admin_role = Role.objects.get(code='department_admin')
        user_role = Role.objects.get(code='user')
        
        # 获取权限
        all_permissions = Permission.objects.all()
        
        # 超级管理员拥有所有权限
        for permission in all_permissions:
            RolePermission.objects.get_or_create(
                role=super_admin_role,
                permission=permission,
                defaults={
                    'is_granted': True,
                    'granted_by': admin_user
                }
            )
        
        # 系统管理员拥有大部分权限
        system_permissions = Permission.objects.filter(
            code__in=['system_management', 'user_management', 'department_management', 
                     'permission_management', 'user_view', 'user_add', 'user_edit',
                     'department_view', 'department_add', 'department_edit',
                     'permission_view', 'permission_manage', 'api_access']
        )
        for permission in system_permissions:
            RolePermission.objects.get_or_create(
                role=system_admin_role,
                permission=permission,
                defaults={
                    'is_granted': True,
                    'granted_by': admin_user
                }
            )
        
        # 部门管理员拥有部门相关权限
        dept_permissions = Permission.objects.filter(
            code__in=['department_management', 'department_view', 'department_add', 
                     'department_edit', 'user_view', 'api_access']
        )
        for permission in dept_permissions:
            RolePermission.objects.get_or_create(
                role=dept_admin_role,
                permission=permission,
                defaults={
                    'is_granted': True,
                    'granted_by': admin_user
                }
            )
        
        # 普通用户只有查看权限
        user_permissions = Permission.objects.filter(
            code__in=['user_view', 'department_view', 'api_access']
        )
        for permission in user_permissions:
            RolePermission.objects.get_or_create(
                role=user_role,
                permission=permission,
                defaults={
                    'is_granted': True,
                    'granted_by': admin_user
                }
            )

    def assign_data_permissions_to_roles(self):
        """分配数据权限给角色"""
        self.stdout.write('分配数据权限给角色...')
        
        admin_user = User.objects.get(username='admin')
        
        # 获取角色
        super_admin_role = Role.objects.get(code='super_admin')
        system_admin_role = Role.objects.get(code='system_admin')
        dept_admin_role = Role.objects.get(code='department_admin')
        user_role = Role.objects.get(code='user')
        
        # 获取数据权限
        all_data_permission = DataPermission.objects.get(name='全部数据权限')
        dept_data_permission = DataPermission.objects.get(name='部门数据权限')
        self_data_permission = DataPermission.objects.get(name='个人数据权限')
        
        # 分配数据权限
        RoleDataPermission.objects.get_or_create(
            role=super_admin_role,
            data_permission=all_data_permission,
            defaults={
                'is_granted': True,
                'granted_by': admin_user
            }
        )
        
        RoleDataPermission.objects.get_or_create(
            role=system_admin_role,
            data_permission=all_data_permission,
            defaults={
                'is_granted': True,
                'granted_by': admin_user
            }
        )
        
        RoleDataPermission.objects.get_or_create(
            role=dept_admin_role,
            data_permission=dept_data_permission,
            defaults={
                'is_granted': True,
                'granted_by': admin_user
            }
        )
        
        RoleDataPermission.objects.get_or_create(
            role=user_role,
            data_permission=self_data_permission,
            defaults={
                'is_granted': True,
                'granted_by': admin_user
            }
        )

    def assign_roles_to_users(self):
        """分配角色给用户"""
        self.stdout.write('分配角色给用户...')
        
        admin_user = User.objects.get(username='admin')
        
        # 获取角色
        super_admin_role = Role.objects.get(code='super_admin')
        system_admin_role = Role.objects.get(code='system_admin')
        user_role = Role.objects.get(code='user')
        
        # 管理员用户分配超级管理员角色
        UserRole.objects.get_or_create(
            user=admin_user,
            role=super_admin_role,
            defaults={
                'is_active': True,
                'assigned_by': admin_user
            }
        )
        
        # 其他用户分配普通用户角色
        other_users = User.objects.exclude(username='admin')
        for user in other_users:
            UserRole.objects.get_or_create(
                user=user,
                role=user_role,
                defaults={
                    'is_active': True,
                    'assigned_by': admin_user
                }
            )