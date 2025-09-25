from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from .permission_models import (
    Permission, Role, RolePermission, UserRole, DataPermission,
    RoleDataPermission, PermissionLog, PermissionCache, FieldPermission,
    DepartmentPermission
)
from .models import Department, Employee
import json
import hashlib
from typing import List, Dict, Any, Optional


class PermissionService:
    """权限管理服务"""
    
    def __init__(self, user: User):
        self.user = user
        self.cache_key = f"user_permissions_{user.id}"
        self.cache_timeout = 3600  # 1小时
    
    def get_user_permissions(self, force_refresh: bool = False) -> List[Permission]:
        """获取用户权限"""
        if not force_refresh:
            cached_permissions = self._get_cached_permissions()
            if cached_permissions:
                return cached_permissions
        
        permissions = set()
        
        # 获取用户直接分配的权限
        user_roles = UserRole.objects.filter(
            user=self.user,
            is_active=True,
            expires_at__isnull=True
        ).select_related('role')
        
        for user_role in user_roles:
            if user_role.is_expired():
                continue
            
            role_permissions = user_role.role.get_permissions()
            permissions.update(role_permissions)
        
        # 获取用户直接分配的权限
        direct_permissions = Permission.objects.filter(
            user_permissions__user=self.user,
            user_permissions__is_granted=True
        )
        permissions.update(direct_permissions)
        
        permission_list = list(permissions)
        self._cache_permissions(permission_list)
        
        return permission_list
    
    def has_permission(self, permission_code: str) -> bool:
        """检查用户是否有指定权限"""
        permissions = self.get_user_permissions()
        return any(p.code == permission_code for p in permissions)
    
    def has_any_permission(self, permission_codes: List[str]) -> bool:
        """检查用户是否有任意一个权限"""
        permissions = self.get_user_permissions()
        permission_codes_set = set(permission_codes)
        return any(p.code in permission_codes_set for p in permissions)
    
    def has_all_permissions(self, permission_codes: List[str]) -> bool:
        """检查用户是否有所有权限"""
        permissions = self.get_user_permissions()
        permission_codes_set = set(permission_codes)
        user_permission_codes = {p.code for p in permissions}
        return permission_codes_set.issubset(user_permission_codes)
    
    def get_user_roles(self) -> List[Role]:
        """获取用户角色"""
        user_roles = UserRole.objects.filter(
            user=self.user,
            is_active=True,
            expires_at__isnull=True
        ).select_related('role')
        
        return [ur.role for ur in user_roles if not ur.is_expired()]
    
    def assign_role(self, role: Role, assigned_by: User, expires_at: Optional[timezone.datetime] = None) -> UserRole:
        """分配角色给用户"""
        user_role, created = UserRole.objects.get_or_create(
            user=self.user,
            role=role,
            defaults={
                'assigned_by': assigned_by,
                'expires_at': expires_at
            }
        )
        
        if not created:
            user_role.is_active = True
            user_role.assigned_by = assigned_by
            user_role.assigned_at = timezone.now()
            user_role.expires_at = expires_at
            user_role.save()
        
        # 清除权限缓存
        self._clear_permission_cache()
        
        # 记录权限日志
        self._log_permission_action('grant', 'role', str(role.id), {
            'role_name': role.name,
            'role_code': role.code
        })
        
        return user_role
    
    def revoke_role(self, role: Role, revoked_by: User) -> bool:
        """撤销用户角色"""
        try:
            user_role = UserRole.objects.get(user=self.user, role=role)
            user_role.is_active = False
            user_role.save()
            
            # 清除权限缓存
            self._clear_permission_cache()
            
            # 记录权限日志
            self._log_permission_action('revoke', 'role', str(role.id), {
                'role_name': role.name,
                'role_code': role.code
            })
            
            return True
        except UserRole.DoesNotExist:
            return False
    
    def _get_cached_permissions(self) -> Optional[List[Permission]]:
        """获取缓存的权限"""
        cached_data = cache.get(self.cache_key)
        if cached_data:
            permission_ids = cached_data.get('permission_ids', [])
            return list(Permission.objects.filter(id__in=permission_ids))
        return None
    
    def _cache_permissions(self, permissions: List[Permission]):
        """缓存权限"""
        permission_ids = [p.id for p in permissions]
        cache_data = {
            'permission_ids': permission_ids,
            'cached_at': timezone.now().isoformat()
        }
        cache.set(self.cache_key, cache_data, self.cache_timeout)
    
    def _clear_permission_cache(self):
        """清除权限缓存"""
        cache.delete(self.cache_key)
    
    def _log_permission_action(self, action_type: str, resource_type: str, resource_id: str, action_detail: Dict):
        """记录权限操作日志"""
        PermissionLog.objects.create(
            user=self.user,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action_detail=action_detail,
            result='success'
        )


class DataPermissionService:
    """数据权限服务"""
    
    def __init__(self, user: User):
        self.user = user
    
    def get_data_scope(self, resource_type: str) -> str:
        """获取用户对指定资源的数据权限范围"""
        # 获取用户角色
        user_roles = UserRole.objects.filter(
            user=self.user,
            is_active=True,
            expires_at__isnull=True
        ).select_related('role')
        
        max_scope = 'self'  # 默认最小权限
        
        for user_role in user_roles:
            if user_role.is_expired():
                continue
            
            role = user_role.role
            
            # 检查角色数据权限
            role_data_permissions = RoleDataPermission.objects.filter(
                role=role,
                is_granted=True,
                data_permission__resource_type=resource_type,
                data_permission__is_active=True
            ).select_related('data_permission')
            
            for rdp in role_data_permissions:
                scope = rdp.data_permission.scope_type
                if self._compare_scope_priority(scope, max_scope) > 0:
                    max_scope = scope
        
        return max_scope
    
    def can_access_data(self, resource_type: str, resource_id: str = None, department_id: int = None) -> bool:
        """检查用户是否可以访问指定数据"""
        scope = self.get_data_scope(resource_type)
        
        if scope == 'all':
            return True
        elif scope == 'self':
            # 检查是否是用户自己的数据
            if hasattr(self.user, 'employee'):
                employee = self.user.employee
                if department_id and employee.department_id == department_id:
                    return True
                if resource_id and str(employee.id) == str(resource_id):
                    return True
            return False
        elif scope == 'dept':
            # 检查是否是本部门数据
            if hasattr(self.user, 'employee') and department_id:
                return self.user.employee.department_id == department_id
            return False
        elif scope == 'dept_and_child':
            # 检查是否是本部门及下级部门数据
            if hasattr(self.user, 'employee') and department_id:
                user_dept = self.user.employee.department
                target_dept = Department.objects.get(id=department_id)
                return self._is_department_child(user_dept, target_dept)
            return False
        
        return False
    
    def get_accessible_departments(self) -> List[Department]:
        """获取用户可访问的部门列表"""
        scope = self.get_data_scope('department')
        
        if scope == 'all':
            return list(Department.objects.all())
        elif scope == 'self':
            if hasattr(self.user, 'employee'):
                return [self.user.employee.department]
            return []
        elif scope == 'dept':
            if hasattr(self.user, 'employee'):
                return [self.user.employee.department]
            return []
        elif scope == 'dept_and_child':
            if hasattr(self.user, 'employee'):
                return self._get_department_and_children(self.user.employee.department)
            return []
        
        return []
    
    def get_accessible_employees(self) -> List[Employee]:
        """获取用户可访问的员工列表"""
        accessible_departments = self.get_accessible_departments()
        department_ids = [dept.id for dept in accessible_departments]
        
        return list(Employee.objects.filter(department_id__in=department_ids))
    
    def _compare_scope_priority(self, scope1: str, scope2: str) -> int:
        """比较数据权限范围优先级"""
        priority = {
            'self': 1,
            'dept': 2,
            'dept_and_child': 3,
            'all': 4
        }
        return priority.get(scope1, 0) - priority.get(scope2, 0)
    
    def _is_department_child(self, parent_dept: Department, child_dept: Department) -> bool:
        """检查是否是部门子级关系"""
        if parent_dept.id == child_dept.id:
            return True
        
        # 递归检查父部门
        current = child_dept
        while current.parent:
            if current.parent.id == parent_dept.id:
                return True
            current = current.parent
        
        return False
    
    def _get_department_and_children(self, department: Department) -> List[Department]:
        """获取部门及其所有子部门"""
        departments = [department]
        
        def get_children(dept):
            children = Department.objects.filter(parent=dept, is_active=True)
            for child in children:
                departments.append(child)
                get_children(child)
        
        get_children(department)
        return departments


class FieldPermissionService:
    """字段权限服务"""
    
    def __init__(self, user: User):
        self.user = user
    
    def get_field_permission(self, resource_type: str, field_name: str) -> str:
        """获取字段权限"""
        try:
            field_permission = FieldPermission.objects.get(
                user=self.user,
                resource_type=resource_type,
                field_name=field_name,
                is_active=True
            )
            return field_permission.permission_type
        except FieldPermission.DoesNotExist:
            return 'visible'  # 默认可见
    
    def is_field_visible(self, resource_type: str, field_name: str) -> bool:
        """检查字段是否可见"""
        permission = self.get_field_permission(resource_type, field_name)
        return permission in ['visible', 'readonly', 'masked']
    
    def is_field_editable(self, resource_type: str, field_name: str) -> bool:
        """检查字段是否可编辑"""
        permission = self.get_field_permission(resource_type, field_name)
        return permission == 'visible'
    
    def mask_field_value(self, resource_type: str, field_name: str, value: str) -> str:
        """对字段值进行脱敏处理"""
        try:
            field_permission = FieldPermission.objects.get(
                user=self.user,
                resource_type=resource_type,
                field_name=field_name,
                is_active=True,
                permission_type='masked'
            )
            
            masking_rule = field_permission.masking_rule
            masking_config = field_permission.masking_config or {}
            
            if masking_rule == 'phone':
                return self._mask_phone(value)
            elif masking_rule == 'email':
                return self._mask_email(value)
            elif masking_rule == 'id_card':
                return self._mask_id_card(value)
            elif masking_rule == 'custom':
                return self._mask_custom(value, masking_config)
            
        except FieldPermission.DoesNotExist:
            pass
        
        return value
    
    def _mask_phone(self, phone: str) -> str:
        """手机号脱敏"""
        if len(phone) >= 11:
            return phone[:3] + '****' + phone[-4:]
        return phone
    
    def _mask_email(self, email: str) -> str:
        """邮箱脱敏"""
        if '@' in email:
            username, domain = email.split('@', 1)
            if len(username) > 2:
                return username[:2] + '***@' + domain
        return email
    
    def _mask_id_card(self, id_card: str) -> str:
        """身份证脱敏"""
        if len(id_card) >= 18:
            return id_card[:6] + '********' + id_card[-4:]
        return id_card
    
    def _mask_custom(self, value: str, config: Dict) -> str:
        """自定义脱敏"""
        prefix_len = config.get('prefix_len', 2)
        suffix_len = config.get('suffix_len', 2)
        mask_char = config.get('mask_char', '*')
        
        if len(value) > prefix_len + suffix_len:
            mask_length = len(value) - prefix_len - suffix_len
            return value[:prefix_len] + mask_char * mask_length + value[-suffix_len:]
        
        return value


class PermissionMiddleware:
    """权限中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 在请求处理前添加权限服务
        if request.user.is_authenticated:
            request.permission_service = PermissionService(request.user)
            request.data_permission_service = DataPermissionService(request.user)
            request.field_permission_service = FieldPermissionService(request.user)
        
        response = self.get_response(request)
        return response


def require_permission(permission_code: str):
    """权限装饰器"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': '未登录'}, status=401)
            
            if not hasattr(request, 'permission_service'):
                request.permission_service = PermissionService(request.user)
            
            if not request.permission_service.has_permission(permission_code):
                return JsonResponse({'error': '权限不足'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_data_permission(resource_type: str):
    """数据权限装饰器"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': '未登录'}, status=401)
            
            if not hasattr(request, 'data_permission_service'):
                request.data_permission_service = DataPermissionService(request.user)
            
            # 检查数据权限
            if not request.data_permission_service.can_access_data(resource_type):
                return JsonResponse({'error': '数据权限不足'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
