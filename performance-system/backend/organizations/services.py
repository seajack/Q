import requests
from django.conf import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OrganizationPlatformClient:
    """组织架构中台API客户端"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'ORG_PLATFORM_API_BASE', 'http://127.0.0.1:8001/api')
        self.timeout = getattr(settings, 'ORG_PLATFORM_API_TIMEOUT', 30)
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """发送API请求"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {method} {url} - {str(e)}")
            return None
    
    def get_departments(self, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """获取部门列表"""
        response = self._make_request('GET', '/departments/', params=params)
        return response.get('results', []) if response else None
    
    def get_department_tree(self) -> Optional[List[Dict]]:
        """获取部门树形结构"""
        return self._make_request('GET', '/departments/tree/')
    
    def get_positions(self, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """获取职位列表"""
        response = self._make_request('GET', '/positions/', params=params)
        return response.get('results', []) if response else None
    
    def get_employees(self, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """获取员工列表"""
        response = self._make_request('GET', '/employees/', params=params)
        return response.get('results', []) if response else None
    
    def get_employee_org_tree(self) -> Optional[List[Dict]]:
        """获取员工组织架构树"""
        return self._make_request('GET', '/employees/org_tree/')
    
    def get_department_employees(self, department_id: int) -> Optional[List[Dict]]:
        """获取部门员工"""
        return self._make_request('GET', f'/departments/{department_id}/employees/')
    
    def get_employee_subordinates(self, employee_id: int) -> Optional[List[Dict]]:
        """获取员工下属"""
        return self._make_request('GET', f'/employees/{employee_id}/subordinates/')


class OrganizationService:
    """组织架构服务"""
    
    def __init__(self):
        self.client = OrganizationPlatformClient()
    
    def sync_employees(self) -> Dict[str, int]:
        """同步员工数据"""
        from .models import Employee as LocalEmployee
        
        # 获取所有活跃员工
        employees_data = self.client.get_employees({'status': 'active'})
        if not employees_data:
            return {'synced': 0, 'errors': 1}
        
        synced_count = 0
        error_count = 0
        
        for emp_data in employees_data:
            try:
                # 获取职位信息来确定级别
                position_level = 1  # 默认级别
                if 'position' in emp_data and emp_data['position']:
                    # 这里可以根据职位ID获取更详细信息
                    # 为简化，我们使用默认映射
                    position_level = self._map_position_level(emp_data.get('position_name', ''))
                
                # 更新或创建员工记录
                employee, created = LocalEmployee.objects.update_or_create(
                    employee_id=emp_data['employee_id'],
                    defaults={
                        'name': emp_data['name'],
                        'department_id': emp_data['department'],
                        'department_name': emp_data.get('department_name', ''),
                        'position_id': emp_data['position'],
                        'position_name': emp_data.get('position_name', ''),
                        'position_level': position_level,
                        'supervisor_id': emp_data.get('supervisor'),
                        'email': emp_data.get('email', ''),
                        'phone': emp_data.get('phone', ''),
                        'is_active': emp_data.get('status') == 'active',
                    }
                )
                
                synced_count += 1
                
            except Exception as e:
                logger.error(f"同步员工数据失败: {emp_data.get('employee_id', 'unknown')} - {str(e)}")
                error_count += 1
        
        return {'synced': synced_count, 'errors': error_count}
    
    def _map_position_level(self, position_name: str) -> int:
        \"\"\"根据职位名称映射职位级别\"\"\"
        # 简化的职位级别映射
        level_keywords = {
            8: ['总裁', '总经理', 'CEO', 'CTO', 'CIO'],
            7: ['副总', '副总裁', '总监'],
            6: ['经理', '主管', '主任'],
            5: ['组长', '队长', '领导'],
            4: ['高级', '资深'],
            3: ['中级'],
            2: ['初级', '助理'],
            1: ['员工', '专员', '实习']  # 默认级别
        }
        
        for level, keywords in level_keywords.items():
            if any(keyword in position_name for keyword in keywords):
                return level
        
        return 1  # 默认返回1级
    
    def build_evaluation_relationships(self, cycle_id: int) -> Dict[str, int]:
        \"\"\"构建考核关系\"\"\"
        from evaluations.models import EvaluationTask, EvaluationCycle
        from .models import Employee as LocalEmployee
        
        try:
            cycle = EvaluationCycle.objects.get(id=cycle_id)
        except EvaluationCycle.DoesNotExist:
            return {'created': 0, 'errors': 1}
        
        created_count = 0
        error_count = 0
        
        # 获取所有活跃员工
        employees = LocalEmployee.objects.filter(is_active=True)
        
        for employee in employees:
            try:
                # 1. 上级考核下级关系
                if employee.supervisor_id:
                    try:
                        supervisor = LocalEmployee.objects.get(id=employee.supervisor_id, is_active=True)
                        task, created = EvaluationTask.objects.get_or_create(
                            cycle=cycle,
                            evaluator=supervisor,
                            evaluatee=employee,
                            relation_type='superior',
                            defaults={'weight': self._get_relation_weight('superior', employee.position_level)}
                        )
                        if created:
                            created_count += 1
                    except LocalEmployee.DoesNotExist:
                        pass
                
                # 2. 同级互评关系
                peers = LocalEmployee.objects.filter(
                    department_id=employee.department_id,
                    position_level=employee.position_level,
                    is_active=True
                ).exclude(id=employee.id)
                
                for peer in peers:
                    task, created = EvaluationTask.objects.get_or_create(
                        cycle=cycle,
                        evaluator=peer,
                        evaluatee=employee,
                        relation_type='peer',
                        defaults={'weight': self._get_relation_weight('peer', employee.position_level)}
                    )
                    if created:
                        created_count += 1
                
                # 3. 下级评价上级关系
                subordinates = LocalEmployee.objects.filter(
                    supervisor_id=employee.id,
                    is_active=True
                )
                
                for subordinate in subordinates:
                    task, created = EvaluationTask.objects.get_or_create(
                        cycle=cycle,
                        evaluator=subordinate,
                        evaluatee=employee,
                        relation_type='subordinate',
                        defaults={'weight': self._get_relation_weight('subordinate', employee.position_level)}
                    )
                    if created:
                        created_count += 1
                        
            except Exception as e:
                logger.error(f\"创建考核关系失败: {employee.employee_id} - {str(e)}\")
                error_count += 1
        
        return {'created': created_count, 'errors': error_count}
    
    def _get_relation_weight(self, relation_type: str, position_level: int) -> float:
        \"\"\"根据关系类型和职位级别获取权重\"\"\"
        base_weights = {
            'superior': 0.60,     # 上级考核权重60%
            'peer': 0.25,         # 同级互评权重25%
            'subordinate': 0.15,  # 下级评价权重15%
        }
        
        # 职位级别权重调整
        level_multipliers = {
            1: 1.0,  # 初级
            2: 1.0,  # 初级
            3: 1.2,  # 中级
            4: 1.2,  # 中级
            5: 1.5,  # 高级
            6: 1.5,  # 高级
            7: 2.0,  # 管理级
            8: 2.0,  # 管理级
        }
        
        base_weight = base_weights.get(relation_type, 1.0)
        level_multiplier = level_multipliers.get(position_level, 1.0)
        
        return base_weight * level_multiplier