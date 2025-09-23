from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Department, Position, Employee, OrganizationStructure
from .serializers import (
    DepartmentSerializer, DepartmentTreeSerializer,
    PositionSerializer, EmployeeSerializer, EmployeeTreeSerializer,
    OrganizationStructureSerializer, OrganizationStatsSerializer
)


@extend_schema_view(
    list=extend_schema(summary='获取部门列表', tags=['部门管理']),
    create=extend_schema(summary='创建部门', tags=['部门管理']),
    retrieve=extend_schema(summary='获取部门详情', tags=['部门管理']),
    update=extend_schema(summary='更新部门', tags=['部门管理']),
    destroy=extend_schema(summary='删除部门', tags=['部门管理']),
)
class DepartmentViewSet(viewsets.ModelViewSet):
    """部门管理ViewSet"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'level', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['level', 'sort_order', 'created_at']
    ordering = ['level', 'sort_order']

    @extend_schema(
        summary='获取部门树形结构',
        description='返回完整的部门树形结构，包含所有层级的部门',
        tags=['部门管理']
    )
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取部门树形结构"""
        # 只获取根部门（parent为None）
        root_departments = Department.objects.filter(parent=None, is_active=True).order_by('sort_order')
        serializer = DepartmentTreeSerializer(root_departments, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        summary='获取完整组织架构树',
        description='返回包含部门和员工的完整组织架构树',
        tags=['部门管理']
    )
    @action(detail=False, methods=['get'])
    def full_tree(self, request):
        """获取包含员工的完整组织架构树"""
        from django.db.models import Prefetch
        
        # 获取所有部门，按层级和排序顺序
        departments = Department.objects.filter(is_active=True).prefetch_related(
            Prefetch('employees', 
                    queryset=Employee.objects.filter(status='active')
                    .select_related('position')
                    .order_by('-position__level', 'name'))
        ).order_by('level', 'sort_order')
        
        # 获取高层领导（无上级且职位级别高的员工）
        top_executives = Employee.objects.filter(
            supervisor=None, 
            status='active',
            position__level__gte=10  # 高层职位级别
        ).select_related('position', 'department').order_by('-position__level', 'name')
        
        # 构建树形结构
        def build_department_tree(departments_list, parent_id=None):
            tree = []
            for dept in departments_list:
                if dept.parent_id == parent_id:
                    # 部门节点
                    dept_node = {
                        'id': f'dept_{dept.id}',
                        'name': dept.name,
                        'type': 'department',
                        'employee_count': dept.employees.count(),
                        'children': []
                    }
                    
                    # 添加部门下的员工
                    for emp in dept.employees.all():
                        emp_node = {
                            'id': f'emp_{emp.id}',
                            'name': emp.name,
                            'type': 'employee',
                            'position_name': emp.position.name if emp.position else '',
                            'position_level': emp.position.level if emp.position else 0,
                            'employee_id': emp.employee_id,
                            'status': emp.status
                        }
                        dept_node['children'].append(emp_node)
                    
                    # 添加子部门
                    dept_node['children'].extend(build_department_tree(departments_list, dept.id))
                    tree.append(dept_node)
            return tree
        
        # 构建根节点（公司）
        root_dept = departments.filter(parent=None).first()
        if root_dept:
            result = {
                'id': f'dept_{root_dept.id}',
                'name': root_dept.name,
                'type': 'department',
                'employee_count': Employee.objects.filter(status='active').count(),
                'children': []
            }
            
            # 添加高层领导（直接在公司下面）
            for emp in top_executives:
                emp_node = {
                    'id': f'emp_{emp.id}',
                    'name': emp.name,
                    'type': 'employee',
                    'position_name': emp.position.name if emp.position else '',
                    'position_level': emp.position.level if emp.position else 0,
                    'employee_id': emp.employee_id,
                    'status': emp.status
                }
                result['children'].append(emp_node)
            
            # 添加子部门
            result['children'].extend(build_department_tree(departments, root_dept.id))
            
            return Response([result])
        
        return Response([])

    @extend_schema(
        summary='获取部门的所有子部门',
        description='获取指定部门的所有子部门（递归）',
        tags=['部门管理']
    )
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """获取部门的所有子部门"""
        department = self.get_object()
        children = department.get_all_children()
        serializer = DepartmentSerializer(children, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        summary='获取部门员工',
        description='获取指定部门的所有员工',
        tags=['部门管理']
    )
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """获取部门员工"""
        department = self.get_object()
        employees = department.employees.filter(status='active')
        serializer = EmployeeSerializer(employees, many=True, context={'request': request})
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary='获取职位列表', tags=['职位管理']),
    create=extend_schema(summary='创建职位', tags=['职位管理']),
    retrieve=extend_schema(summary='获取职位详情', tags=['职位管理']),
    update=extend_schema(summary='更新职位', tags=['职位管理']),
    destroy=extend_schema(summary='删除职位', tags=['职位管理']),
)
class PositionViewSet(viewsets.ModelViewSet):
    """职位管理ViewSet"""
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'level', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['level', 'created_at']
    ordering = ['department', 'level']

    @extend_schema(
        summary='获取职位员工',
        description='获取指定职位的所有员工',
        tags=['职位管理']
    )
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """获取职位员工"""
        position = self.get_object()
        employees = position.employees.filter(status='active')
        serializer = EmployeeSerializer(employees, many=True, context={'request': request})
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary='获取员工列表', tags=['员工管理']),
    create=extend_schema(summary='创建员工', tags=['员工管理']),
    retrieve=extend_schema(summary='获取员工详情', tags=['员工管理']),
    update=extend_schema(summary='更新员工', tags=['员工管理']),
    destroy=extend_schema(summary='删除员工', tags=['员工管理']),
)
class EmployeeViewSet(viewsets.ModelViewSet):
    """员工管理ViewSet"""
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'position', 'supervisor', 'status', 'gender']
    search_fields = ['name', 'employee_id', 'phone', 'email']
    ordering_fields = ['employee_id', 'hire_date', 'created_at']
    ordering = ['department', 'position__level', 'employee_id']

    @extend_schema(
        summary='获取组织架构树',
        description='返回按组织架构组织的员工树形结构',
        tags=['员工管理']
    )
    @action(detail=False, methods=['get'])
    def org_tree(self, request):
        """获取组织架构树"""
        # 获取没有上级的员工（顶层管理者）
        top_employees = Employee.objects.filter(supervisor=None, status='active')
        serializer = EmployeeTreeSerializer(top_employees, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        summary='获取员工下属',
        description='获取指定员工的所有下属（递归）',
        tags=['员工管理']
    )
    @action(detail=True, methods=['get'])
    def subordinates(self, request, pk=None):
        """获取员工下属"""
        employee = self.get_object()
        subordinates = employee.get_all_subordinates()
        serializer = EmployeeSerializer(subordinates, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        summary='获取直接下属',
        description='获取指定员工的直接下属',
        tags=['员工管理']
    )
    @action(detail=True, methods=['get'])
    def direct_subordinates(self, request, pk=None):
        """获取直接下属"""
        employee = self.get_object()
        subordinates = employee.subordinates.filter(status='active')
        serializer = EmployeeSerializer(subordinates, many=True, context={'request': request})
        return Response(subordinates.data)


@extend_schema_view(
    list=extend_schema(summary='获取组织架构快照列表', tags=['组织架构']),
    create=extend_schema(summary='创建组织架构快照', tags=['组织架构']),
    retrieve=extend_schema(summary='获取组织架构快照详情', tags=['组织架构']),
    update=extend_schema(summary='更新组织架构快照', tags=['组织架构']),
    destroy=extend_schema(summary='删除组织架构快照', tags=['组织架构']),
)
class OrganizationStructureViewSet(viewsets.ModelViewSet):
    """组织架构快照管理ViewSet"""
    queryset = OrganizationStructure.objects.all()
    serializer_class = OrganizationStructureSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_current', 'created_by']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

    @extend_schema(
        summary='获取当前组织架构',
        description='获取当前激活的组织架构快照',
        tags=['组织架构']
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        """获取当前组织架构"""
        try:
            current_structure = OrganizationStructure.objects.get(is_current=True)
            serializer = self.get_serializer(current_structure)
            return Response(serializer.data)
        except OrganizationStructure.DoesNotExist:
            return Response({'error': '没有当前激活的组织架构'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary='创建当前组织架构快照',
        description='基于当前组织架构数据创建快照',
        tags=['组织架构']
    )
    @action(detail=False, methods=['post'])
    def create_snapshot(self, request):
        """创建当前组织架构快照"""
        from django.core import serializers as django_serializers
        
        # 获取当前所有组织架构数据
        departments = list(Department.objects.filter(is_active=True))
        positions = list(Position.objects.filter(is_active=True))
        employees = list(Employee.objects.filter(status='active'))
        
        structure_data = {
            'departments': django_serializers.serialize('json', departments),
            'positions': django_serializers.serialize('json', positions),
            'employees': django_serializers.serialize('json', employees),
            'created_at': str(timezone.now())
        }
        
        name = request.data.get('name', f'组织架构快照_{timezone.now().strftime("%Y%m%d_%H%M%S")}')
        description = request.data.get('description', '')
        
        snapshot = OrganizationStructure.objects.create(
            name=name,
            description=description,
            structure_data=structure_data,
            created_by=request.user
        )
        
        serializer = self.get_serializer(snapshot)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrganizationStatsView(viewsets.GenericViewSet):
    """组织架构统计信息ViewSet"""
    
    @extend_schema(
        summary='获取组织架构统计信息',
        description='获取组织架构的各项统计数据',
        tags=['组织架构']
    )
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取组织架构统计信息"""
        # 基本统计
        total_departments = Department.objects.count()
        active_departments = Department.objects.filter(is_active=True).count()
        total_positions = Position.objects.count()
        active_positions = Position.objects.filter(is_active=True).count()
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(status='active').count()
        
        # 部门层级统计
        department_levels = Department.objects.filter(is_active=True) \
            .values('level') \
            .annotate(count=Count('id')) \
            .order_by('level')
        
        # 职位级别统计
        position_levels = Position.objects.filter(is_active=True) \
            .values('level') \
            .annotate(count=Count('id')) \
            .order_by('level')
        
        stats_data = {
            'total_departments': total_departments,
            'active_departments': active_departments,
            'total_positions': total_positions,
            'active_positions': active_positions,
            'total_employees': total_employees,
            'active_employees': active_employees,
            'department_levels': list(department_levels),
            'position_levels': list(position_levels),
        }
        
        serializer = OrganizationStatsSerializer(stats_data)
        return Response(serializer.data)


# 绩效考核系统的临时API端点
@api_view(['GET'])
def performance_overview_stats(request):
    """绩效考核系统概览统计信息"""
    # 模拟绩效考核统计数据
    stats = {
        'total_cycles': 3,
        'active_cycles': 1,
        'total_tasks': 25,
        'completed_tasks': 18,
        'total_employees': Employee.objects.filter(status='active').count(),
        'pending_evaluations': 7
    }
    
    return Response(stats)


@api_view(['GET'])
def performance_cycle_stats(request, cycle_id):
    """绩效考核周期统计信息"""
    # 模拟周期统计数据
    stats = {
        'cycle': {
            'id': cycle_id,
            'name': f'2023年第{cycle_id}季度考核',
            'status': 'active' if cycle_id == 1 else 'completed'
        },
        'total_tasks': 25,
        'completed_tasks': 18,
        'pending_tasks': 7,
        'total_results': 18,
    }
    
    return Response(stats)
