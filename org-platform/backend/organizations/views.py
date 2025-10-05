from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Department, Position, Employee, OrganizationStructure, SystemConfig, Dictionary, PositionTemplate, WorkflowRule
from .serializers import (
    DepartmentSerializer, DepartmentTreeSerializer,
    PositionSerializer, EmployeeSerializer, EmployeeTreeSerializer,
    OrganizationStructureSerializer, OrganizationStatsSerializer,
    SystemConfigSerializer, DictionarySerializer, PositionTemplateSerializer, WorkflowRuleSerializer
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
        # 使用自定义排序：董事长 > 总经理 > 其他高管
        from django.db.models import Case, When, IntegerField
        
        top_executives = Employee.objects.filter(
            supervisor=None, 
            status='active',
            position__level__gte=10  # 高层职位级别
        ).select_related('position', 'department').annotate(
            sort_priority=Case(
                When(position__name__icontains='董事长', then=1),
                When(position__name__icontains='总经理', then=2),
                default=3,
                output_field=IntegerField()
            )
        ).order_by('sort_priority', '-position__level', 'name')
        
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
        
        # 员工技能统计（模拟数据，实际项目中需要根据具体业务逻辑实现）
        employee_skills = []
        try:
            # 获取前5个活跃员工作为示例
            sample_employees = Employee.objects.filter(status='active')[:5]
            for i, employee in enumerate(sample_employees):
                # 模拟技能数据
                skills_data = {
                    'employee_name': employee.name,
                    'dimensions': [
                        {'name': '技术能力', 'value': 70 + (i * 5)},
                        {'name': '沟通能力', 'value': 80 + (i * 3)},
                        {'name': '领导力', 'value': 60 + (i * 8)},
                        {'name': '学习能力', 'value': 85 + (i * 2)},
                        {'name': '创新能力', 'value': 75 + (i * 4)}
                    ]
                }
                employee_skills.append(skills_data)
        except Exception as e:
            # 如果获取员工数据失败，使用默认模拟数据
            employee_skills = [
                {
                    'employee_name': '张三',
                    'dimensions': [
                        {'name': '技术能力', 'value': 85},
                        {'name': '沟通能力', 'value': 90},
                        {'name': '领导力', 'value': 75},
                        {'name': '学习能力', 'value': 95},
                        {'name': '创新能力', 'value': 80}
                    ]
                },
                {
                    'employee_name': '李四',
                    'dimensions': [
                        {'name': '技术能力', 'value': 90},
                        {'name': '沟通能力', 'value': 85},
                        {'name': '领导力', 'value': 95},
                        {'name': '学习能力', 'value': 80},
                        {'name': '创新能力', 'value': 90}
                    ]
                }
            ]
        
        stats_data = {
            'total_departments': total_departments,
            'active_departments': active_departments,
            'total_positions': total_positions,
            'active_positions': active_positions,
            'total_employees': total_employees,
            'active_employees': active_employees,
            'department_levels': list(department_levels),
            'position_levels': list(position_levels),
            'employee_skills': employee_skills,
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


# 配置管理视图
@extend_schema_view(
    list=extend_schema(summary='获取系统配置列表', tags=['配置管理']),
    create=extend_schema(summary='创建系统配置', tags=['配置管理']),
    retrieve=extend_schema(summary='获取系统配置详情', tags=['配置管理']),
    update=extend_schema(summary='更新系统配置', tags=['配置管理']),
    destroy=extend_schema(summary='删除系统配置', tags=['配置管理']),
)
class SystemConfigViewSet(viewsets.ModelViewSet):
    """系统配置管理"""
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'is_required']
    search_fields = ['key', 'description']
    ordering_fields = ['category', 'key', 'created_at']
    ordering = ['category', 'key']
    
    @extend_schema(
        summary='按分类获取配置',
        description='根据配置分类获取配置列表',
        tags=['配置管理']
    )
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """按分类获取配置"""
        category = request.query_params.get('category')
        if not category:
            return Response({'error': '缺少category参数'}, status=400)
        
        configs = self.queryset.filter(category=category, is_active=True)
        serializer = self.get_serializer(configs, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary='批量更新配置',
        description='批量更新多个配置项',
        tags=['配置管理']
    )
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """批量更新配置"""
        configs_data = request.data.get('configs', [])
        updated_count = 0
        
        for config_data in configs_data:
            try:
                config = SystemConfig.objects.get(key=config_data['key'])
                config.value = config_data['value']
                config.save()
                updated_count += 1
            except SystemConfig.DoesNotExist:
                continue
        
        return Response({
            'message': f'成功更新 {updated_count} 个配置项',
            'updated_count': updated_count
        })
    
    @extend_schema(
        summary='导出配置数据',
        description='导出所有配置数据为JSON格式',
        tags=['配置管理']
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出配置数据"""
        configs = self.queryset.filter(is_active=True)
        export_data = []
        
        for config in configs:
            export_data.append({
                'key': config.key,
                'value': config.value,
                'category': config.category,
                'description': config.description,
                'data_type': config.data_type,
            })
        
        return Response(export_data)
    
    @extend_schema(
        summary='导入配置数据',
        description='从JSON数据导入配置项',
        tags=['配置管理']
    )
    @action(detail=False, methods=['post'])
    def import_configs(self, request):
        """导入配置数据"""
        configs_data = request.data.get('configs', [])
        imported_count = 0
        
        for config_data in configs_data:
            config, created = SystemConfig.objects.update_or_create(
                key=config_data['key'],
                defaults={
                    'value': config_data['value'],
                    'category': config_data.get('category', 'organization'),
                    'description': config_data.get('description', ''),
                    'data_type': config_data.get('data_type', 'string'),
                }
            )
            if created:
                imported_count += 1
        
        return Response({
            'message': f'成功导入 {imported_count} 个配置项',
            'imported_count': imported_count
        })


@extend_schema_view(
    list=extend_schema(summary='获取数据字典列表', tags=['配置管理']),
    create=extend_schema(summary='创建数据字典', tags=['配置管理']),
    retrieve=extend_schema(summary='获取数据字典详情', tags=['配置管理']),
    update=extend_schema(summary='更新数据字典', tags=['配置管理']),
    destroy=extend_schema(summary='删除数据字典', tags=['配置管理']),
)
class DictionaryViewSet(viewsets.ModelViewSet):
    """数据字典管理"""
    queryset = Dictionary.objects.all()
    serializer_class = DictionarySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'parent']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['category', 'sort_order', 'code']
    ordering = ['category', 'sort_order', 'code']
    
    @extend_schema(
        summary='按分类获取字典数据',
        description='根据字典分类获取字典列表',
        tags=['配置管理']
    )
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """按分类获取字典数据"""
        category = request.query_params.get('category')
        if not category:
            return Response({'error': '缺少category参数'}, status=400)
        
        dictionaries = self.queryset.filter(category=category, is_active=True)
        serializer = self.get_serializer(dictionaries, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary='获取字典树形结构',
        description='获取指定分类的字典树形结构',
        tags=['配置管理']
    )
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取字典树形结构"""
        category = request.query_params.get('category')
        if not category:
            return Response({'error': '缺少category参数'}, status=400)
        
        # 获取根级字典
        root_dicts = self.queryset.filter(
            category=category, 
            parent__isnull=True, 
            is_active=True
        ).order_by('sort_order')
        
        def build_tree(dict_obj):
            children = dict_obj.children.filter(is_active=True).order_by('sort_order')
            return {
                'id': dict_obj.id,
                'code': dict_obj.code,
                'name': dict_obj.name,
                'value': dict_obj.value,
                'description': dict_obj.description,
                'children': [build_tree(child) for child in children]
            }
        
        tree_data = [build_tree(dict_obj) for dict_obj in root_dicts]
        return Response(tree_data)


@extend_schema_view(
    list=extend_schema(summary='获取职位模板列表', tags=['配置管理']),
    create=extend_schema(summary='创建职位模板', tags=['配置管理']),
    retrieve=extend_schema(summary='获取职位模板详情', tags=['配置管理']),
    update=extend_schema(summary='更新职位模板', tags=['配置管理']),
    destroy=extend_schema(summary='删除职位模板', tags=['配置管理']),
)
class PositionTemplateViewSet(viewsets.ModelViewSet):
    """职位模板管理"""
    queryset = PositionTemplate.objects.all()
    serializer_class = PositionTemplateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['management_level', 'level', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['management_level', 'level', 'name']
    ordering = ['-level', 'name']
    
    @extend_schema(
        summary='基于模板创建职位',
        description='使用职位模板快速创建职位',
        tags=['配置管理']
    )
    @action(detail=True, methods=['post'])
    def create_position(self, request, pk=None):
        """基于模板创建职位"""
        template = self.get_object()
        position_data = request.data
        
        # 创建职位
        position = Position.objects.create(
            name=position_data.get('name', template.name),
            code=position_data.get('code', ''),
            department_id=position_data.get('department'),
            management_level=template.management_level,
            level=template.level,
            description=position_data.get('description', template.description),
            requirements=position_data.get('requirements', template.default_requirements),
            responsibilities=position_data.get('responsibilities', template.default_responsibilities),
        )
        
        serializer = PositionSerializer(position)
        return Response(serializer.data, status=201)


@extend_schema_view(
    list=extend_schema(summary='获取工作流规则列表', tags=['配置管理']),
    create=extend_schema(summary='创建工作流规则', tags=['配置管理']),
    retrieve=extend_schema(summary='获取工作流规则详情', tags=['配置管理']),
    update=extend_schema(summary='更新工作流规则', tags=['配置管理']),
    destroy=extend_schema(summary='删除工作流规则', tags=['配置管理']),
)
class WorkflowRuleViewSet(viewsets.ModelViewSet):
    """工作流规则管理"""
    queryset = WorkflowRule.objects.all()
    serializer_class = WorkflowRuleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rule_type', 'is_active']
    search_fields = ['name']
    ordering_fields = ['priority', 'name', 'created_at']
    ordering = ['-priority', 'name']
