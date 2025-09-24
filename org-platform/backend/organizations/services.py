from django.core.cache import cache
from django.conf import settings
from typing import Dict, Any, Optional, List
import json
import logging

logger = logging.getLogger(__name__)


class ConfigService:
    """配置数据服务"""
    
    @staticmethod
    def get_config(key: str, default: Any = None) -> Any:
        """获取配置值"""
        cache_key = f"config:{key}"
        value = cache.get(cache_key)
        
        if value is None:
            try:
                from .models import SystemConfig
                config = SystemConfig.objects.get(key=key, is_active=True)
                value = config.value
                
                # 根据数据类型转换
                if config.data_type == 'integer':
                    value = int(value)
                elif config.data_type == 'boolean':
                    value = value.lower() in ('true', '1', 'yes')
                elif config.data_type in ['json', 'list']:
                    value = json.loads(value)
                
                cache.set(cache_key, value, timeout=3600)  # 缓存1小时
            except Exception as e:
                logger.warning(f"获取配置失败: {key} - {str(e)}")
                value = default
        
        return value
    
    @staticmethod
    def set_config(key: str, value: Any, category: str = 'organization', 
                   data_type: str = 'string', description: str = '') -> bool:
        """设置配置值"""
        try:
            from .models import SystemConfig
            # 根据数据类型转换值
            if data_type == 'json' or data_type == 'list':
                value = json.dumps(value, ensure_ascii=False)
            else:
                value = str(value)
            
            config, created = SystemConfig.objects.update_or_create(
                key=key,
                defaults={
                    'value': value,
                    'category': category,
                    'data_type': data_type,
                    'description': description,
                }
            )
            
            # 清除缓存
            cache.delete(f"config:{key}")
            return True
        except Exception as e:
            logger.error(f"设置配置失败: {key} - {str(e)}")
            return False
    
    @staticmethod
    def get_dictionary_by_category(category: str) -> List[Dict]:
        """获取字典数据"""
        cache_key = f"dictionary:{category}"
        data = cache.get(cache_key)
        
        if data is None:
            try:
                from .models import Dictionary
                dictionaries = Dictionary.objects.filter(
                    category=category, 
                    is_active=True
                ).order_by('sort_order')
                
                data = [
                    {
                        'code': dict_obj.code,
                        'name': dict_obj.name,
                        'value': dict_obj.value,
                        'description': dict_obj.description,
                    }
                    for dict_obj in dictionaries
                ]
                cache.set(cache_key, data, timeout=3600)
            except Exception as e:
                logger.error(f"获取字典数据失败: {category} - {str(e)}")
                data = []
        
        return data
    
    @staticmethod
    def get_organization_config() -> Dict[str, Any]:
        """获取组织架构配置"""
        return {
            'max_department_levels': ConfigService.get_config('max_department_levels', 5),
            'auto_generate_employee_id': ConfigService.get_config('auto_generate_employee_id', True),
            'employee_id_prefix': ConfigService.get_config('employee_id_prefix', 'EMP'),
            'require_supervisor': ConfigService.get_config('require_supervisor', True),
            'allow_cross_department_position': ConfigService.get_config('allow_cross_department_position', False),
            'position_level_validation': ConfigService.get_config('position_level_validation', True),
        }
    
    @staticmethod
    def get_employee_config() -> Dict[str, Any]:
        """获取员工配置"""
        return {
            'auto_generate_employee_id': ConfigService.get_config('auto_generate_employee_id', True),
            'employee_id_prefix': ConfigService.get_config('employee_id_prefix', 'EMP'),
            'require_supervisor': ConfigService.get_config('require_supervisor', True),
        }
    
    @staticmethod
    def get_workflow_config() -> Dict[str, Any]:
        """获取工作流配置"""
        return {
            'default_workflow_enabled': ConfigService.get_config('default_workflow_enabled', True),
            'notification_enabled': ConfigService.get_config('notification_enabled', True),
        }
    
    @staticmethod
    def clear_cache():
        """清除所有配置缓存"""
        try:
            cache.delete_many([f"config:{key}" for key in cache.keys("config:*")])
            cache.delete_many([f"dictionary:{key}" for key in cache.keys("dictionary:*")])
            logger.info("配置缓存已清除")
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")


class DictionaryService:
    """数据字典服务"""
    
    @staticmethod
    def get_employee_status_choices() -> List[Dict]:
        """获取员工状态选项"""
        return ConfigService.get_dictionary_by_category('employee_status')
    
    @staticmethod
    def get_education_level_choices() -> List[Dict]:
        """获取学历层次选项"""
        return ConfigService.get_dictionary_by_category('education_level')
    
    @staticmethod
    def get_skill_level_choices() -> List[Dict]:
        """获取技能等级选项"""
        return ConfigService.get_dictionary_by_category('skill_level')
    
    @staticmethod
    def get_marital_status_choices() -> List[Dict]:
        """获取婚姻状况选项"""
        return ConfigService.get_dictionary_by_category('marital_status')
    
    @staticmethod
    def get_department_type_choices() -> List[Dict]:
        """获取部门类型选项"""
        return ConfigService.get_dictionary_by_category('department_type')


class PositionTemplateService:
    """职位模板服务"""
    
    @staticmethod
    def create_position_from_template(template_id: int, position_data: Dict) -> Optional[Any]:
        """基于模板创建职位"""
        try:
            from .models import PositionTemplate, Position
            
            template = PositionTemplate.objects.get(id=template_id, is_active=True)
            
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
            
            return position
        except Exception as e:
            logger.error(f"基于模板创建职位失败: {str(e)}")
            return None
    
    @staticmethod
    def get_templates_by_level(management_level: str = None, level: int = None) -> List[Dict]:
        """根据级别获取模板"""
        try:
            from .models import PositionTemplate
            
            queryset = PositionTemplate.objects.filter(is_active=True)
            
            if management_level:
                queryset = queryset.filter(management_level=management_level)
            if level:
                queryset = queryset.filter(level=level)
            
            return [
                {
                    'id': template.id,
                    'name': template.name,
                    'description': template.description,
                    'management_level': template.management_level,
                    'level': template.level,
                    'default_requirements': template.default_requirements,
                    'default_responsibilities': template.default_responsibilities,
                }
                for template in queryset.order_by('-level', 'name')
            ]
        except Exception as e:
            logger.error(f"获取职位模板失败: {str(e)}")
            return []


class WorkflowService:
    """工作流服务"""
    
    @staticmethod
    def get_active_rules(rule_type: str = None) -> List[Dict]:
        """获取活跃的工作流规则"""
        try:
            from .models import WorkflowRule
            
            queryset = WorkflowRule.objects.filter(is_active=True)
            
            if rule_type:
                queryset = queryset.filter(rule_type=rule_type)
            
            return [
                {
                    'id': rule.id,
                    'name': rule.name,
                    'rule_type': rule.rule_type,
                    'trigger_conditions': rule.trigger_conditions,
                    'action_config': rule.action_config,
                    'priority': rule.priority,
                }
                for rule in queryset.order_by('-priority', 'name')
            ]
        except Exception as e:
            logger.error(f"获取工作流规则失败: {str(e)}")
            return []
    
    @staticmethod
    def execute_rule(rule_id: int, context: Dict) -> bool:
        """执行工作流规则"""
        try:
            from .models import WorkflowRule
            
            rule = WorkflowRule.objects.get(id=rule_id, is_active=True)
            
            # 检查触发条件
            if not WorkflowService._check_conditions(rule.trigger_conditions, context):
                return False
            
            # 执行动作
            return WorkflowService._execute_actions(rule.action_config, context)
            
        except Exception as e:
            logger.error(f"执行工作流规则失败: {str(e)}")
            return False
    
    @staticmethod
    def _check_conditions(conditions: Dict, context: Dict) -> bool:
        """检查触发条件"""
        # 这里可以实现复杂的条件检查逻辑
        # 简化实现，实际项目中需要更复杂的条件引擎
        return True
    
    @staticmethod
    def _execute_actions(actions: Dict, context: Dict) -> bool:
        """执行动作"""
        # 这里可以实现复杂的动作执行逻辑
        # 简化实现，实际项目中需要更复杂的动作引擎
        logger.info(f"执行工作流动作: {actions}")
        return True
