from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Position, Employee, OrganizationStructure, SystemConfig, Dictionary, PositionTemplate, WorkflowRule
from .integration_models import (
    IntegrationSystem, APIGateway, APIRoute, DataSyncRule, 
    SyncLog, APIMonitor, IntegrationConfig
)
from .permission_models import (
    Permission, Role, RolePermission, UserRole, DataPermission,
    RoleDataPermission, PermissionLog, FieldPermission, DepartmentPermission
)


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class DepartmentTreeSerializer(serializers.ModelSerializer):
    """部门树形序列化器"""
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    manager_name = serializers.SerializerMethodField()
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
    
    def get_manager_name(self, obj):
        """获取部门经理姓名"""
        # 先检查是否有设置的manager字段
        if obj.manager:
            # 查找对应的员工记录
            try:
                employee = obj.manager.employee
                return f"{employee.name}({employee.position.name if employee.position else '无职位'})"
            except:
                # 如果找不到员工记录，返回用户名
                return obj.manager.username
        
        # 自动查找部门经理（职位名称包含'经理'且级别较高的员工）
        managers = obj.employees.filter(
            status='active',
            position__name__icontains='经理'
        ).order_by('-position__level').first()
        
        if managers:
            return f"{managers.name}({managers.position.name})"
        
        # 如果没有经理，查找职位级别最高的员工
        top_employee = obj.employees.filter(status='active').order_by('-position__level').first()
        if top_employee:
            return f"{top_employee.name}({top_employee.position.name})"
        
        return '待分配'


class DepartmentSerializer(serializers.ModelSerializer):
    """部门序列化器"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    manager_name = serializers.SerializerMethodField()
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
    
    def get_manager_name(self, obj):
        """获取部门经理姓名"""
        # 先检查是否有设置的manager字段
        if obj.manager:
            # 查找对应的员工记录
            try:
                employee = obj.manager.employee
                return f"{employee.name}({employee.position.name if employee.position else '无职位'})"
            except:
                # 如果找不到员工记录，返回用户名
                return obj.manager.username
        
        # 自动查找部门经理（职位名称包含'经理'且级别较高的员工）
        managers = obj.employees.filter(
            status='active',
            position__name__icontains='经理'
        ).order_by('-position__level').first()
        
        if managers:
            return f"{managers.name}({managers.position.name})"
        
        # 如果没有经理，查找职位级别最高的员工
        top_employee = obj.employees.filter(status='active').order_by('-position__level').first()
        if top_employee:
            return f"{top_employee.name}({top_employee.position.name})"
        
        return '待分配'

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
    position_level = serializers.IntegerField(source='position.level', read_only=True)
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
                 'department_name', 'position', 'position_name', 'position_level', 'position_level_display',
                 'supervisor', 'supervisor_name', 'subordinate_count', 'hire_date', 
                 'status', 'avatar', 'username', 'password', 'created_at', 'updated_at']
        extra_kwargs = {
            'user': {'read_only': True},  # user字段为只读，通过username和password创建
        }

    def validate_hire_date(self, value):
        """验证入职日期"""
        print(f"hire_date 验证: 值={value}, 类型={type(value)}")
        
        if not value:
            raise serializers.ValidationError("入职日期不能为空")
        
        from datetime import date
        import datetime
        
        # 如果是字符串，尝试解析
        if isinstance(value, str):
            try:
                parsed_date = datetime.datetime.strptime(value, '%Y-%m-%d').date()
                return parsed_date
            except ValueError:
                raise serializers.ValidationError("日期格式错误，请使用 YYYY-MM-DD 格式")
        
        # 如果是 date 或 datetime 对象
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, date):
            return value
            
        raise serializers.ValidationError("不支持的日期格式")

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
        # 如果值为空或空字符串，返回 None
        if not value or not value.strip():
            return None
            
        # 检查用户名是否已存在
        from django.contrib.auth.models import User
        if self.instance and hasattr(self.instance, 'user') and self.instance.user.username == value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate(self, attrs):
        """验证员工数据"""
        print(f"验证员工数据: {attrs}")
        
        # 移除职位与部门的关联验证
        # department = attrs.get('department', self.instance.department if self.instance else None)
        # position = attrs.get('position', self.instance.position if self.instance else None)
        
        # 验证职位是否属于所选部门
        # if position and department and position.department != department:
        #     raise serializers.ValidationError("所选职位不属于所选部门")
        
        return attrs
    
    def create(self, validated_data):
        """创建员工时同时创建用户账号"""
        from django.contrib.auth.models import User
        
        print(f"创建员工，验证后数据: {validated_data}")
        
        # 提取用户相关字段
        username = validated_data.pop('username', None) or validated_data['employee_id']
        password = validated_data.pop('password', '123456')
        
        # 确保用户名唯一性
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}_{counter}"
            counter += 1
        
        print(f"创建用户: username={username}, password={password}")
        
        # 创建User账号
        try:
            user = User.objects.create_user(
                username=username,
                email=validated_data.get('email', ''),
                password=password,
                first_name=validated_data.get('name', '').split()[0] if validated_data.get('name') else '',
                last_name=' '.join(validated_data.get('name', '').split()[1:]) if len(validated_data.get('name', '').split()) > 1 else ''
            )
            print(f"用户创建成功: {user}")
        except Exception as e:
            print(f"用户创建失败: {e}")
            raise serializers.ValidationError(f"用户创建失败: {str(e)}")
        
        # 创建Employee
        validated_data['user'] = user
        
        try:
            employee = super().create(validated_data)
            print(f"员工创建成功: {employee}")
            return employee
        except Exception as e:
            print(f"员工创建失败: {e}")
            # 如果员工创建失败，删除已创建的用户
            user.delete()
            raise
    
    def update(self, instance, validated_data):
        """更新员工信息时同时更新用户账号"""
        print(f"更新员工: {instance.name} ({instance.employee_id})")
        print(f"更新数据: {validated_data}")
        
        # 提取用户相关字段
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)
        
        print(f"用户相关字段: username={username}, password={password}")
        
        # 更新User账号
        if hasattr(instance, 'user'):
            user = instance.user
            print(f"更新用户账号: {user.username}")
            
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
            print(f"用户账号更新成功")
        
        result = super().update(instance, validated_data)
        print(f"员工更新成功: {result}")
        return result


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
    employee_skills = serializers.ListField(child=serializers.DictField(), required=False)


# 配置数据序列化器
class SystemConfigSerializer(serializers.ModelSerializer):
    """系统配置序列化器"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    data_type_display = serializers.CharField(source='get_data_type_display', read_only=True)
    
    class Meta:
        model = SystemConfig
        fields = ['id', 'key', 'value', 'category', 'category_display', 'description', 
                 'data_type', 'data_type_display', 'is_encrypted', 'is_required', 
                 'is_active', 'created_at', 'updated_at']
    
    def validate_value(self, value):
        """验证配置值格式"""
        data_type = self.initial_data.get('data_type', 'string')
        
        if data_type == 'integer':
            try:
                int(value)
            except ValueError:
                raise serializers.ValidationError("整数类型的配置值必须是有效数字")
        elif data_type == 'boolean':
            if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                raise serializers.ValidationError("布尔类型的配置值必须是 true/false 或 1/0")
        elif data_type in ['json', 'list']:
            import json
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("JSON类型的配置值必须是有效的JSON格式")
        
        return value


class DictionarySerializer(serializers.ModelSerializer):
    """数据字典序列化器"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Dictionary
        fields = ['id', 'category', 'category_display', 'code', 'name', 'value', 
                 'description', 'sort_order', 'is_active', 'parent', 'parent_name', 
                 'children', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        """获取子字典项"""
        children = obj.children.filter(is_active=True).order_by('sort_order')
        return DictionarySerializer(children, many=True, context=self.context).data
    
    def validate_code(self, value):
        """验证字典编码唯一性"""
        category = self.initial_data.get('category')
        if self.instance and self.instance.code == value and self.instance.category == category:
            return value
        
        if Dictionary.objects.filter(category=category, code=value).exists():
            raise serializers.ValidationError("该分类下已存在相同编码的字典项")
        return value


class PositionTemplateSerializer(serializers.ModelSerializer):
    """职位模板序列化器"""
    management_level_display = serializers.CharField(source='get_management_level_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = PositionTemplate
        fields = ['id', 'name', 'description', 'management_level', 'management_level_display',
                 'level', 'level_display', 'default_requirements', 'default_responsibilities',
                 'is_active', 'created_at', 'updated_at']


class WorkflowRuleSerializer(serializers.ModelSerializer):
    """工作流规则序列化器"""
    rule_type_display = serializers.CharField(source='get_rule_type_display', read_only=True)
    
    class Meta:
        model = WorkflowRule
        fields = ['id', 'name', 'rule_type', 'rule_type_display', 'trigger_conditions',
                 'action_config', 'is_active', 'priority', 'created_at', 'updated_at']
    
    def validate_trigger_conditions(self, value):
        """验证触发条件格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("触发条件必须是JSON对象格式")
        return value
    
    def validate_action_config(self, value):
        """验证动作配置格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("动作配置必须是JSON对象格式")
        return value


# 系统集成序列化器
class IntegrationSystemSerializer(serializers.ModelSerializer):
    """集成系统序列化器"""
    system_type_display = serializers.CharField(source='get_system_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = IntegrationSystem
        fields = [
            'id', 'name', 'system_type', 'system_type_display', 'base_url', 
            'api_version', 'status', 'status_display', 'auth_type', 'auth_config',
            'timeout', 'retry_count', 'rate_limit', 'sync_enabled', 'sync_interval',
            'last_sync_time', 'monitoring_enabled', 'health_check_url', 'alert_email',
            'description', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'last_sync_time']
    
    def validate_auth_config(self, value):
        """验证认证配置"""
        auth_type = self.initial_data.get('auth_type')
        
        if auth_type == 'basic':
            required_fields = ['username', 'password']
            for field in required_fields:
                if field not in value:
                    raise serializers.ValidationError(f"基础认证需要 {field} 字段")
        
        elif auth_type == 'token':
            if 'token' not in value:
                raise serializers.ValidationError("Token认证需要 token 字段")
        
        elif auth_type == 'api_key':
            required_fields = ['api_key']
            for field in required_fields:
                if field not in value:
                    raise serializers.ValidationError(f"API Key认证需要 {field} 字段")
        
        return value


class APIGatewaySerializer(serializers.ModelSerializer):
    """API网关序列化器"""
    route_count = serializers.SerializerMethodField()
    active_route_count = serializers.SerializerMethodField()
    
    class Meta:
        model = APIGateway
        fields = [
            'id', 'name', 'base_url', 'description', 'rate_limit_enabled',
            'rate_limit_per_minute', 'rate_limit_per_hour', 'monitoring_enabled',
            'log_level', 'cors_enabled', 'cors_origins', 'api_key_required',
            'is_active', 'route_count', 'active_route_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_route_count(self, obj):
        # 暂时返回0，因为APIRoute模型没有gateway外键
        return 0
    
    def get_active_route_count(self, obj):
        # 暂时返回0，因为APIRoute模型没有gateway外键
        return 0


class APIRouteSerializer(serializers.ModelSerializer):
    """API路由序列化器"""
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    gateway_name = serializers.CharField(source='gateway.name', read_only=True)
    
    class Meta:
        model = APIRoute
        fields = [
            'id', 'gateway', 'gateway_name', 'name', 'path', 'method', 'method_display',
            'target_url', 'rate_limit', 'burst_limit', 'cache_enabled', 'cache_ttl',
            'auth_required', 'roles_required', 'request_transform', 'response_transform',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_path(self, value):
        """验证路径格式"""
        if not value.startswith('/'):
            value = '/' + value
        return value
    
    def validate(self, data):
        """验证数据"""
        # 检查路径和方法的唯一性
        if 'gateway' in data and 'path' in data and 'method' in data:
            existing = APIRoute.objects.filter(
                gateway=data['gateway'],
                path=data['path'],
                method=data['method']
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing.exists():
                raise serializers.ValidationError("相同网关下路径和方法的组合必须唯一")
        
        return data


class DataSyncRuleSerializer(serializers.ModelSerializer):
    """数据同步规则序列化器"""
    sync_type_display = serializers.CharField(source='get_sync_type_display', read_only=True)
    
    class Meta:
        model = DataSyncRule
        fields = [
            'id', 'name', 'source_system_id', 'target_system_id', 'sync_type', 'sync_type_display',
            'source_table', 'target_table', 'field_mapping', 'filter_conditions', 'batch_size',
            'sync_interval', 'max_retry_count', 'data_cleaning_enabled', 'cleaning_rules',
            'validation_enabled', 'validation_rules', 'monitoring_enabled', 'alert_on_error',
            'alert_on_delay', 'delay_threshold', 'description', 'created_by_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_field_mapping(self, value):
        """验证字段映射"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("字段映射必须是字典格式")
        
        # 检查是否有空值
        for key, val in value.items():
            if not key or not val:
                raise serializers.ValidationError("字段映射的键和值不能为空")
        
        return value
    
    def validate_cleaning_rules(self, value):
        """验证清洗规则"""
        if not isinstance(value, list):
            raise serializers.ValidationError("清洗规则必须是列表格式")
        
        valid_types = ['trim', 'lowercase', 'uppercase', 'remove_special_chars', 'default_value']
        for rule in value:
            if not isinstance(rule, dict):
                raise serializers.ValidationError("每个清洗规则必须是字典格式")
            
            if 'field' not in rule or 'type' not in rule:
                raise serializers.ValidationError("清洗规则必须包含 field 和 type 字段")
            
            if rule['type'] not in valid_types:
                raise serializers.ValidationError(f"清洗规则类型必须是: {', '.join(valid_types)}")
        
        return value
    
    def validate_validation_rules(self, value):
        """验证校验规则"""
        if not isinstance(value, list):
            raise serializers.ValidationError("校验规则必须是列表格式")
        
        valid_types = ['required', 'email', 'phone', 'length']
        for rule in value:
            if not isinstance(rule, dict):
                raise serializers.ValidationError("每个校验规则必须是字典格式")
            
            if 'field' not in rule or 'type' not in rule:
                raise serializers.ValidationError("校验规则必须包含 field 和 type 字段")
            
            if rule['type'] not in valid_types:
                raise serializers.ValidationError(f"校验规则类型必须是: {', '.join(valid_types)}")
        
        return value


class SyncLogSerializer(serializers.ModelSerializer):
    """同步日志序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sync_rule_name = serializers.CharField(source='sync_rule.name', read_only=True)
    duration_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = SyncLog
        fields = [
            'id', 'sync_rule', 'sync_rule_name', 'status', 'status_display',
            'start_time', 'end_time', 'total_records', 'success_records',
            'error_records', 'skipped_records', 'error_message', 'error_details',
            'duration_seconds', 'duration_formatted', 'records_per_second', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_duration_formatted(self, obj):
        """格式化持续时间"""
        if obj.duration_seconds:
            if obj.duration_seconds < 60:
                return f"{obj.duration_seconds:.2f}秒"
            elif obj.duration_seconds < 3600:
                minutes = obj.duration_seconds / 60
                return f"{minutes:.2f}分钟"
            else:
                hours = obj.duration_seconds / 3600
                return f"{hours:.2f}小时"
        return "0秒"


class APIMonitorSerializer(serializers.ModelSerializer):
    """API监控序列化器"""
    route_name = serializers.CharField(source='route.name', read_only=True)
    route_path = serializers.CharField(source='route.path', read_only=True)
    route_method = serializers.CharField(source='route.method', read_only=True)
    
    class Meta:
        model = APIMonitor
        fields = [
            'id', 'route', 'route_name', 'route_path', 'route_method', 'timestamp',
            'request_count', 'success_count', 'error_count', 'avg_response_time',
            'max_response_time', 'min_response_time', 'error_rate', 'status_code_distribution'
        ]
        read_only_fields = ['timestamp']


class IntegrationConfigSerializer(serializers.ModelSerializer):
    """集成配置序列化器"""
    config_type_display = serializers.CharField(source='get_config_type_display', read_only=True)
    system_name = serializers.CharField(source='system.name', read_only=True)
    
    class Meta:
        model = IntegrationConfig
        fields = [
            'id', 'system', 'system_name', 'config_key', 'config_value',
            'config_type', 'config_type_display', 'is_encrypted', 'description',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_config_value(self, value):
        """验证配置值"""
        config_type = self.initial_data.get('config_type')
        
        if config_type == 'integer':
            try:
                int(value)
            except ValueError:
                raise serializers.ValidationError("配置值必须是整数")
        
        elif config_type == 'boolean':
            if value.lower() not in ['true', 'false', '1', '0']:
                raise serializers.ValidationError("配置值必须是布尔值")
        
        elif config_type == 'json':
            try:
                import json
                json.loads(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError("配置值必须是有效的JSON格式")
        
        return value


# 权限管理序列化器
class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Permission
        fields = [
            'id', 'name', 'code', 'permission_type', 'permission_type_display',
            'description', 'resource', 'action', 'parent', 'parent_name',
            'full_path', 'status', 'is_system', 'sort_order', 'children_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_children_count(self, obj):
        """获取子权限数量"""
        return obj.children.count()
    
    def validate_code(self, value):
        """验证权限编码唯一性"""
        if self.instance and self.instance.code == value:
            return value
        
        if Permission.objects.filter(code=value).exists():
            raise serializers.ValidationError("权限编码已存在")
        return value


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    # 暂时简化序列化器，避免字段不匹配问题
    permissions_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'description',
            'created_at', 'updated_at', 'permissions_count', 'users_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_permissions_count(self, obj):
        """获取角色权限数量"""
        return obj.rolepermission_set.filter(granted=True).count()
    
    def get_users_count(self, obj):
        """获取角色用户数量"""
        return obj.user_roles.filter(is_active=True).count()
    
    def validate_code(self, value):
        """验证角色编码唯一性"""
        if self.instance and self.instance.code == value:
            return value
        
        if Role.objects.filter(code=value).exists():
            raise serializers.ValidationError("角色编码已存在")
        return value


class RolePermissionSerializer(serializers.ModelSerializer):
    """角色权限序列化器"""
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_code = serializers.CharField(source='permission.code', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.username', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'permission', 'permission_name', 'permission_code',
            'is_granted', 'granted_at', 'granted_by', 'granted_by_name'
        ]
        read_only_fields = ['granted_at']


class UserRoleSerializer(serializers.ModelSerializer):
    """用户角色序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_code = serializers.CharField(source='role.code', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_name', 'user_full_name', 'role', 'role_name', 'role_code',
            'is_active', 'assigned_at', 'assigned_by', 'assigned_by_name',
            'expires_at', 'is_expired'
        ]
        read_only_fields = ['assigned_at']
    
    def get_user_full_name(self, obj):
        """获取用户全名"""
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return obj.user.username
    
    def get_is_expired(self, obj):
        """检查是否过期"""
        return obj.is_expired()


class DataPermissionSerializer(serializers.ModelSerializer):
    """数据权限序列化器"""
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = DataPermission
        fields = [
            'id', 'user', 'user_name', 'permission_type', 'permission_type_display',
            'resource', 'conditions', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_conditions(self, value):
        """验证条件"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("条件必须是字典格式")
        return value
    
    def validate_field_permissions(self, value):
        """验证字段权限"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("字段权限必须是字典格式")
        return value
    
    def validate_data_masking(self, value):
        """验证数据脱敏配置"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("数据脱敏配置必须是字典格式")
        return value


class RoleDataPermissionSerializer(serializers.ModelSerializer):
    """角色数据权限序列化器"""
    data_permission_name = serializers.CharField(source='data_permission.name', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.username', read_only=True)
    
    class Meta:
        model = RoleDataPermission
        fields = [
            'id', 'role', 'data_permission', 'data_permission_name',
            'is_granted', 'granted_at', 'granted_by', 'granted_by_name'
        ]
        read_only_fields = ['granted_at']


class PermissionLogSerializer(serializers.ModelSerializer):
    """权限日志序列化器"""
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PermissionLog
        fields = [
            'id', 'user', 'user_name', 'action_type', 'action_type_display',
            'resource_type', 'resource_id', 'action_detail', 'result', 'result_display',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['created_at']


class FieldPermissionSerializer(serializers.ModelSerializer):
    """字段权限序列化器"""
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = FieldPermission
        fields = [
            'id', 'user', 'user_name', 'resource_type', 'field_name',
            'permission_type', 'permission_type_display', 'masking_rule',
            'masking_config', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_masking_config(self, value):
        """验证脱敏配置"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("脱敏配置必须是字典格式")
        return value


class DepartmentPermissionSerializer(serializers.ModelSerializer):
    """部门权限序列化器"""
    data_scope_display = serializers.CharField(source='get_data_scope_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = DepartmentPermission
        fields = [
            'id', 'user', 'user_name', 'department', 'department_name',
            'can_view', 'can_edit', 'can_delete', 'can_manage',
            'data_scope', 'data_scope_display', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']