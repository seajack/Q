from django.core.management.base import BaseCommand
from organizations.models import SystemConfig, Dictionary, PositionTemplate


class Command(BaseCommand):
    help = '初始化配置数据'
    
    def handle(self, *args, **options):
        self.init_system_configs()
        self.init_dictionaries()
        self.init_position_templates()
        self.stdout.write(self.style.SUCCESS('配置数据初始化完成'))
    
    def init_system_configs(self):
        """初始化系统配置"""
        self.stdout.write('初始化系统配置...')
        configs = [
            {
                'key': 'max_department_levels',
                'value': '5',
                'category': 'organization',
                'description': '最大部门层级数',
                'data_type': 'integer',
                'is_required': True,
            },
            {
                'key': 'auto_generate_employee_id',
                'value': 'true',
                'category': 'employee',
                'description': '是否自动生成员工号',
                'data_type': 'boolean',
                'is_required': True,
            },
            {
                'key': 'employee_id_prefix',
                'value': 'EMP',
                'category': 'employee',
                'description': '员工号前缀',
                'data_type': 'string',
                'is_required': True,
            },
            {
                'key': 'require_supervisor',
                'value': 'true',
                'category': 'employee',
                'description': '是否必须设置直接上级',
                'data_type': 'boolean',
                'is_required': True,
            },
            {
                'key': 'position_level_validation',
                'value': 'true',
                'category': 'position',
                'description': '是否启用职位级别验证',
                'data_type': 'boolean',
                'is_required': True,
            },
            {
                'key': 'allow_cross_department_position',
                'value': 'false',
                'category': 'position',
                'description': '是否允许跨部门职位',
                'data_type': 'boolean',
                'is_required': False,
            },
            {
                'key': 'default_workflow_enabled',
                'value': 'true',
                'category': 'workflow',
                'description': '是否启用默认工作流',
                'data_type': 'boolean',
                'is_required': False,
            },
            {
                'key': 'notification_enabled',
                'value': 'true',
                'category': 'notification',
                'description': '是否启用通知功能',
                'data_type': 'boolean',
                'is_required': False,
            },
        ]
        
        created_count = 0
        for config_data in configs:
            config, created = SystemConfig.objects.get_or_create(
                key=config_data['key'],
                defaults=config_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'  - 创建了 {created_count} 个系统配置项')
    
    def init_dictionaries(self):
        """初始化数据字典"""
        self.stdout.write('初始化数据字典...')
        dictionaries = [
            # 员工状态
            {'category': 'employee_status', 'code': 'active', 'name': '在职', 'sort_order': 1},
            {'category': 'employee_status', 'code': 'leave', 'name': '休假', 'sort_order': 2},
            {'category': 'employee_status', 'code': 'resigned', 'name': '离职', 'sort_order': 3},
            {'category': 'employee_status', 'code': 'retired', 'name': '退休', 'sort_order': 4},
            
            # 学历层次
            {'category': 'education_level', 'code': 'doctor', 'name': '博士', 'sort_order': 1},
            {'category': 'education_level', 'code': 'master', 'name': '硕士', 'sort_order': 2},
            {'category': 'education_level', 'code': 'bachelor', 'name': '本科', 'sort_order': 3},
            {'category': 'education_level', 'code': 'college', 'name': '专科', 'sort_order': 4},
            {'category': 'education_level', 'code': 'high_school', 'name': '高中', 'sort_order': 5},
            
            # 技能等级
            {'category': 'skill_level', 'code': 'expert', 'name': '专家级', 'sort_order': 1},
            {'category': 'skill_level', 'code': 'senior', 'name': '高级', 'sort_order': 2},
            {'category': 'skill_level', 'code': 'intermediate', 'name': '中级', 'sort_order': 3},
            {'category': 'skill_level', 'code': 'junior', 'name': '初级', 'sort_order': 4},
            {'category': 'skill_level', 'code': 'beginner', 'name': '入门级', 'sort_order': 5},
            
            # 婚姻状况
            {'category': 'marital_status', 'code': 'single', 'name': '未婚', 'sort_order': 1},
            {'category': 'marital_status', 'code': 'married', 'name': '已婚', 'sort_order': 2},
            {'category': 'marital_status', 'code': 'divorced', 'name': '离异', 'sort_order': 3},
            {'category': 'marital_status', 'code': 'widowed', 'name': '丧偶', 'sort_order': 4},
            
            # 部门类型
            {'category': 'department_type', 'code': 'management', 'name': '管理部门', 'sort_order': 1},
            {'category': 'department_type', 'code': 'business', 'name': '业务部门', 'sort_order': 2},
            {'category': 'department_type', 'code': 'support', 'name': '支持部门', 'sort_order': 3},
            {'category': 'department_type', 'code': 'technical', 'name': '技术部门', 'sort_order': 4},
        ]
        
        created_count = 0
        for dict_data in dictionaries:
            dict_obj, created = Dictionary.objects.get_or_create(
                category=dict_data['category'],
                code=dict_data['code'],
                defaults=dict_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'  - 创建了 {created_count} 个数据字典项')
    
    def init_position_templates(self):
        """初始化职位模板"""
        self.stdout.write('初始化职位模板...')
        templates = [
            {
                'name': '总经理',
                'description': '公司总经理职位模板',
                'management_level': 'senior',
                'level': 13,
                'default_requirements': '本科以上学历，5年以上管理经验，具备战略思维和领导能力',
                'default_responsibilities': '负责公司整体运营管理，制定发展战略，领导管理团队',
            },
            {
                'name': '副总经理',
                'description': '公司副总经理职位模板',
                'management_level': 'senior',
                'level': 12,
                'default_requirements': '本科以上学历，3年以上管理经验，具备专业能力和管理经验',
                'default_responsibilities': '协助总经理管理公司运营，分管特定业务领域',
            },
            {
                'name': '部门经理',
                'description': '部门经理职位模板',
                'management_level': 'middle',
                'level': 9,
                'default_requirements': '本科以上学历，3年以上管理经验，具备部门管理能力',
                'default_responsibilities': '负责部门日常管理，制定部门工作计划，管理团队',
            },
            {
                'name': '部门副经理',
                'description': '部门副经理职位模板',
                'management_level': 'middle',
                'level': 8,
                'default_requirements': '本科以上学历，2年以上工作经验，具备协助管理能力',
                'default_responsibilities': '协助部门经理管理，分管特定业务模块',
            },
            {
                'name': '主管',
                'description': '主管职位模板',
                'management_level': 'junior',
                'level': 4,
                'default_requirements': '大专以上学历，2年以上工作经验，具备团队管理能力',
                'default_responsibilities': '负责团队日常管理，执行部门工作计划',
            },
            {
                'name': '普通员工',
                'description': '普通员工职位模板',
                'management_level': 'junior',
                'level': 1,
                'default_requirements': '大专以上学历，具备基本工作技能',
                'default_responsibilities': '完成本职工作，执行上级安排的任务',
            },
        ]
        
        created_count = 0
        for template_data in templates:
            template, created = PositionTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'  - 创建了 {created_count} 个职位模板')
