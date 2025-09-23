from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Position, Employee, OrganizationStructure


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class DepartmentTreeSerializer(serializers.ModelSerializer):
    """部门树形序列化器"""
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'parent', 'parent_name', 'level', 
                 'sort_order', 'description', 'manager', 'manager_name', 
                 'full_path', 'employee_count', 'is_active', 'children',
                 'created_at', 'updated_at']

    def get_children(self, obj):
        """获取子部门"""
        children = obj.children.filter(is_active=True).order_by('sort_order', 'code')
        return DepartmentTreeSerializer(children, many=True, context=self.context).data

    def get_employee_count(self, obj):
        """获取部门员工数量"""
        return obj.employees.filter(status='active').count()


class DepartmentSerializer(serializers.ModelSerializer):
    """部门序列化器"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'parent', 'parent_name', 'level', 
                 'sort_order', 'description', 'manager', 'manager_name', 
                 'full_path', 'employee_count', 'is_active',
                 'created_at', 'updated_at']

    def get_employee_count(self, obj):
        """获取部门员工数量"""
        return obj.employees.filter(status='active').count()

    def validate_parent(self, value):
        """验证上级部门"""
        if value and self.instance:
            # 检查是否会形成循环引用
            current = value
            while current:
                if current.id == self.instance.id:
                    raise serializers.ValidationError("不能将自己或下级部门设为上级部门")
                current = current.parent
        return value


class PositionSerializer(serializers.ModelSerializer):
    """职位序列化器"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    management_level_display = serializers.CharField(source='get_management_level_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    level_display_with_management = serializers.CharField(source='get_level_display_with_management', read_only=True)
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ['id', 'name', 'code', 'department', 'department_name', 
                 'management_level', 'management_level_display', 'level', 'level_display', 
                 'level_display_with_management', 'description', 'requirements', 
                 'responsibilities', 'employee_count', 'is_active',
                 'created_at', 'updated_at']

    def get_employee_count(self, obj):
        """获取职位员工数量"""
        return obj.employees.filter(status='active').count()


class EmployeeSerializer(serializers.ModelSerializer):
    """员工序列化器"""
    user_info = UserSerializer(source='user', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    position_level_display = serializers.CharField(source='get_position_level_display_name', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.name', read_only=True)
    subordinate_count = serializers.SerializerMethodField()
    
    # 添加用户账号相关字段
    username = serializers.CharField(write_only=True, required=False, help_text='用户名，默认为员工号')
    password = serializers.CharField(write_only=True, required=False, default='123456', help_text='初始密码，默认123456')

    class Meta:
        model = Employee
        fields = ['id', 'user', 'user_info', 'employee_id', 'name', 'gender', 
                 'birth_date', 'phone', 'email', 'address', 'department', 
                 'department_name', 'position', 'position_name', 'position_level_display',
                 'supervisor', 'supervisor_name', 'subordinate_count', 'hire_date', 
                 'status', 'avatar', 'username', 'password', 'created_at', 'updated_at']
        extra_kwargs = {
            'user': {'read_only': True},  # user字段为只读，通过username和password创建
        }

    def get_subordinate_count(self, obj):
        """获取下属数量"""
        return obj.subordinates.filter(status='active').count()

    def validate_employee_id(self, value):
        """验证员工号唯一性"""
        if self.instance and self.instance.employee_id == value:
            return value
        # 检查员工号是否已存在
        from .models import Employee  # type: ignore
        if Employee.objects.filter(employee_id=value).exists():  # type: ignore
            raise serializers.ValidationError("员工号已存在")
        return value

    def validate_username(self, value):
        """验证用户名唯一性"""
        if not value:
            return value
        # 检查用户名是否已存在
        from django.contrib.auth.models import User
        if self.instance and hasattr(self.instance, 'user') and self.instance.user.username == value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate(self, attrs):
        """验证员工数据"""
        department = attrs.get('department', self.instance.department if self.instance else None)
        position = attrs.get('position', self.instance.position if self.instance else None)
        
        # 验证职位是否属于所选部门
        if position and department and position.department != department:
            raise serializers.ValidationError("所选职位不属于所选部门")
        
        return attrs
    
    def create(self, validated_data):
        """创建员工时同时创建用户账号"""
        from django.contrib.auth.models import User
        
        # 提取用户相关字段
        username = validated_data.pop('username', None) or validated_data['employee_id']
        password = validated_data.pop('password', '123456')
        
        # 创建User账号
        user = User.objects.create_user(
            username=username,
            email=validated_data.get('email', ''),
            password=password,
            first_name=validated_data.get('name', '').split()[0] if validated_data.get('name') else '',
            last_name=' '.join(validated_data.get('name', '').split()[1:]) if len(validated_data.get('name', '').split()) > 1 else ''
        )
        
        # 创建Employee
        validated_data['user'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """更新员工信息时同时更新用户账号"""
        # 提取用户相关字段
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)
        
        # 更新User账号
        if hasattr(instance, 'user'):
            user = instance.user
            if username:
                user.username = username
            if validated_data.get('email'):
                user.email = validated_data['email']
            if validated_data.get('name'):
                name_parts = validated_data['name'].split()
                user.first_name = name_parts[0] if name_parts else ''
                user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            if password:
                user.set_password(password)
            user.save()
        
        return super().update(instance, validated_data)


class EmployeeTreeSerializer(serializers.ModelSerializer):
    """员工树形序列化器（按组织架构展示）"""
    subordinates = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    position_level_display = serializers.CharField(source='get_position_level_display_name', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'name', 'department_name', 'position_name', 
                 'position_level_display', 'phone', 'email', 'status', 'subordinates']

    def get_subordinates(self, obj):
        """获取直接下属"""
        subordinates = obj.subordinates.filter(status='active').order_by('position__level', 'employee_id')
        return EmployeeTreeSerializer(subordinates, many=True, context=self.context).data


class OrganizationStructureSerializer(serializers.ModelSerializer):
    """组织架构快照序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = OrganizationStructure
        fields = ['id', 'name', 'description', 'structure_data', 'is_current', 
                 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class OrganizationStatsSerializer(serializers.Serializer):
    """组织架构统计信息序列化器"""
    total_departments = serializers.IntegerField()
    active_departments = serializers.IntegerField()
    total_positions = serializers.IntegerField()
    active_positions = serializers.IntegerField()
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    department_levels = serializers.ListField(child=serializers.DictField())
    position_levels = serializers.ListField(child=serializers.DictField())