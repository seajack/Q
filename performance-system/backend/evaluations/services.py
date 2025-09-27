"""
考核任务生成服务
实现基于规则的智能考核关系生成
"""

import requests
import string
import random
from django.conf import settings
from typing import List, Dict, Any, Tuple
from .models import EvaluationCycle, EvaluationRule, EvaluationTask, Employee, ManualEvaluationAssignment


class EvaluationTaskGenerator:
    """考核任务生成器"""
    
    def __init__(self, cycle: EvaluationCycle):
        self.cycle = cycle
        self.rule = cycle.evaluation_rule
        self.org_employees_data = []
        self.local_employee_map = {}
        self.org_employee_map = {}
        self.evaluator_codes = {}  # 存储每个考核人的考核码
        
    def _generate_evaluator_code(self, evaluator_id: int) -> str:
        """为考核人生成唯一的考核码"""
        # 如果该考核人已经有考核码，直接返回
        if evaluator_id in self.evaluator_codes:
            return self.evaluator_codes[evaluator_id]
        
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(characters, k=16))
            # 检查这个考核码是否已经被使用
            if not EvaluationTask.objects.filter(evaluation_code=code).exists():
                self.evaluator_codes[evaluator_id] = code
                return code
        
    def generate_tasks(self) -> Dict[str, Any]:
        """根据规则生成考核任务"""
        try:
            # 1. 获取数据
            self._fetch_employee_data()
            
            # 2. 删除现有任务，避免重复约束错误
            existing_tasks = EvaluationTask.objects.filter(cycle=self.cycle)
            if existing_tasks.exists():
                deleted_count = existing_tasks.delete()[0]
                print(f"删除了 {deleted_count} 个现有任务")
            
            # 3. 如果没有规则，使用默认规则
            if not self.rule:
                return self._generate_default_tasks()
            
            # 4. 根据规则生成任务
            tasks_created = 0
            
            # 处理手动分配的评价关系
            if 'manual' in self.rule.relation_types:
                tasks_created += self._generate_manual_tasks()
            
            # 处理自动生成的评价关系
            for relation_type in self.rule.relation_types:
                if relation_type != 'manual':
                    tasks_created += self._generate_tasks_by_relation(relation_type)
            
            return {
                'success': True,
                'message': f'成功生成 {tasks_created} 个考核任务',
                'tasks_created': tasks_created
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'生成考核任务失败: {str(e)}'
            }
    
    def _fetch_employee_data(self):
        """获取员工数据"""
        # 从组织架构中台获取员工数据
        org_api_url = getattr(settings, 'ORG_PLATFORM_API_BASE', 'http://localhost:8000/api')
        response = requests.get(f'{org_api_url}/employees/')
        
        if response.status_code != 200:
            raise Exception('无法连接到组织架构中台获取员工数据')
        
        self.org_employees_data = response.json().get('results', [])
        self.org_employee_map = {emp['id']: emp for emp in self.org_employees_data}
        self.local_employee_map = {emp.employee_id: emp for emp in Employee.objects.filter(is_active=True)}
    
    def _generate_default_tasks(self) -> Dict[str, Any]:
        """生成默认的考核任务（上级评下级）"""
        tasks_created = 0
        
        for org_emp in self.org_employees_data:
            evaluatee = self.local_employee_map.get(org_emp['employee_id'])
            if not evaluatee or not org_emp.get('supervisor'):
                continue
                
            supervisor_org = self.org_employee_map.get(org_emp['supervisor'])
            if not supervisor_org:
                continue
                
            supervisor_local = self.local_employee_map.get(supervisor_org['employee_id'])
            if not supervisor_local:
                continue
            
            # 为考核人生成考核码
            evaluator_code = self._generate_evaluator_code(supervisor_local.id)
            
            EvaluationTask.objects.create(
                cycle=self.cycle,
                evaluatee=evaluatee,
                evaluator=supervisor_local,
                relation_type='superior',
                weight=1.0,
                status='pending',
                evaluation_code=evaluator_code
            )
            tasks_created += 1
        
        return {
            'success': True,
            'message': f'成功生成 {tasks_created} 个默认考核任务',
            'tasks_created': tasks_created
        }
    
    def _generate_manual_tasks(self) -> int:
        """生成手动分配的考核任务"""
        tasks_created = 0
        
        manual_assignments = ManualEvaluationAssignment.objects.filter(cycle=self.cycle)
        
        for assignment in manual_assignments:
            # 为考核人生成考核码
            evaluator_code = self._generate_evaluator_code(assignment.evaluator.id)
            
            EvaluationTask.objects.create(
                cycle=self.cycle,
                evaluatee=assignment.evaluatee,
                evaluator=assignment.evaluator,
                relation_type=assignment.relation_type,
                weight=assignment.weight,
                status='pending',
                evaluation_code=evaluator_code
            )
            tasks_created += 1
        
        return tasks_created
    
    def _generate_tasks_by_relation(self, relation_type: str) -> int:
        """根据关系类型生成考核任务"""
        if relation_type == 'superior':
            return self._generate_superior_tasks()
        elif relation_type == 'peer':
            return self._generate_peer_tasks()
        elif relation_type == 'subordinate':
            return self._generate_subordinate_tasks()
        elif relation_type == 'self':
            return self._generate_self_tasks()
        elif relation_type == 'cross_superior':
            return self._generate_cross_superior_tasks()
        elif relation_type == 'cross_peer':
            return self._generate_cross_peer_tasks()
        else:
            return 0
    
    def _generate_superior_tasks(self) -> int:
        """生成上级评下级的任务 - 全公司上级评下级逻辑"""
        tasks_created = 0
        weight = self.rule.get_relation_weight('superior')
        
        # 获取高层领导 (L12-L13)
        high_level_employees = [
            emp for emp in self.org_employees_data 
            if emp.get('position_level', 0) >= 12
        ]
        
        # 获取部门经理 (L9)
        manager_employees = [
            emp for emp in self.org_employees_data 
            if emp.get('position_level', 0) == 9
        ]
        
        # 获取主管 (L4)
        supervisor_employees = [
            emp for emp in self.org_employees_data 
            if emp.get('position_level', 0) == 4
        ]
        
        
        # 1. 高层领导评价部门经理 (4x4=16个关系)
        for high_org in high_level_employees:
            high_local = self.local_employee_map.get(high_org['employee_id'])
            if not high_local:
                continue
                
            for manager_org in manager_employees:
                manager_local = self.local_employee_map.get(manager_org['employee_id'])
                if not manager_local:
                    continue
                
                # 检查是否允许该评价关系
                if not self._is_evaluation_allowed(high_org, manager_org):
                    continue
                
                # 为每个任务生成唯一的考核码
                evaluator_code = self._generate_evaluator_code(high_local.id)
                
                EvaluationTask.objects.create(
                    cycle=self.cycle,
                    evaluatee=manager_local,
                    evaluator=high_local,
                    relation_type='superior',
                    weight=weight,
                    status='pending',
                    evaluation_code=evaluator_code
                )
                tasks_created += 1
        
        # 2. 部门经理评价主管 (1个关系)
        for manager_org in manager_employees:
            manager_local = self.local_employee_map.get(manager_org['employee_id'])
            if not manager_local:
                continue
                
            for supervisor_org in supervisor_employees:
                supervisor_local = self.local_employee_map.get(supervisor_org['employee_id'])
                if not supervisor_local:
                    continue
                
                # 必须是同部门
                if manager_org['department'] != supervisor_org['department']:
                    continue
                
                # 检查是否允许该评价关系
                if not self._is_evaluation_allowed(manager_org, supervisor_org):
                    continue
                
                # 为每个任务生成唯一的考核码
                evaluator_code = self._generate_evaluator_code(manager_local.id)
                
                EvaluationTask.objects.create(
                    cycle=self.cycle,
                    evaluatee=supervisor_local,
                    evaluator=manager_local,
                    relation_type='superior',
                    weight=weight,
                    status='pending',
                    evaluation_code=evaluator_code
                )
                tasks_created += 1
        
        return tasks_created
    
    def _generate_peer_tasks(self) -> int:
        """生成同级互评的任务"""
        tasks_created = 0
        weight = self.rule.get_relation_weight('peer')
        max_evaluators = self.rule.max_evaluators_per_relation
        
        for org_emp in self.org_employees_data:
            evaluatee = self.local_employee_map.get(org_emp['employee_id'])
            if not evaluatee:
                continue
            
            # 找同级同事
            peers = self._find_peers(org_emp)
            
            # 限制评价人数
            selected_peers = peers[:max_evaluators]
            
            for peer_org in selected_peers:
                peer_local = self.local_employee_map.get(peer_org['employee_id'])
                if not peer_local:
                    continue
                
                if not self._is_evaluation_allowed(peer_org, org_emp):
                    continue
                
                # 为考核人生成考核码
                evaluator_code = self._generate_evaluator_code(peer_local.id)
                
                EvaluationTask.objects.create(
                    cycle=self.cycle,
                    evaluatee=evaluatee,
                    evaluator=peer_local,
                    relation_type='peer',
                    weight=weight,
                    status='pending',
                    evaluation_code=evaluator_code
                )
                tasks_created += 1
        
        return tasks_created
    
    def _generate_subordinate_tasks(self) -> int:
        """生成下级评上级的任务"""
        tasks_created = 0
        weight = self.rule.get_relation_weight('subordinate')
        max_evaluators = self.rule.max_evaluators_per_relation
        
        for org_emp in self.org_employees_data:
            evaluatee = self.local_employee_map.get(org_emp['employee_id'])
            if not evaluatee:
                continue
            
            # 找直接下属
            subordinates = [
                emp for emp in self.org_employees_data 
                if emp.get('supervisor') == org_emp['id']
            ]
            
            # 限制评价人数
            selected_subordinates = subordinates[:max_evaluators]
            
            for sub_org in selected_subordinates:
                sub_local = self.local_employee_map.get(sub_org['employee_id'])
                if not sub_local:
                    continue
                
                if not self._is_evaluation_allowed(sub_org, org_emp):
                    continue
                
                # 为考核人生成考核码
                evaluator_code = self._generate_evaluator_code(sub_local.id)
                
                EvaluationTask.objects.create(
                    cycle=self.cycle,
                    evaluatee=evaluatee,
                    evaluator=sub_local,
                    relation_type='subordinate',
                    weight=weight,
                    status='pending',
                    evaluation_code=evaluator_code
                )
                tasks_created += 1
        
        return tasks_created
    
    def _generate_self_tasks(self) -> int:
        """生成自评任务"""
        if not self.rule.allow_self_evaluation:
            return 0
            
        tasks_created = 0
        weight = self.rule.get_relation_weight('self')
        
        for org_emp in self.org_employees_data:
            employee = self.local_employee_map.get(org_emp['employee_id'])
            if not employee:
                continue
            
            # 为考核人生成考核码
            evaluator_code = self._generate_evaluator_code(employee.id)
            
            EvaluationTask.objects.create(
                cycle=self.cycle,
                evaluatee=employee,
                evaluator=employee,
                relation_type='self',
                weight=weight,
                status='pending',
                evaluation_code=evaluator_code
            )
            tasks_created += 1
        
        return tasks_created
    
    def _generate_cross_superior_tasks(self) -> int:
        """生成跨部门上级评价任务 - 全公司上级评下级逻辑中不需要单独的跨部门上级任务"""
        # 在全公司上级评下级逻辑中，所有关系都在 _generate_superior_tasks 中处理
        # 这里返回0，避免重复生成任务
        return 0
    
    def _generate_cross_peer_tasks(self) -> int:
        """生成跨部门同级评价任务"""
        if not self.rule.allow_cross_department:
            return 0
        
        tasks_created = 0
        weight = self.rule.get_relation_weight('cross_peer')
        max_evaluators = self.rule.max_evaluators_per_relation
        
        for org_emp in self.org_employees_data:
            evaluatee = self.local_employee_map.get(org_emp['employee_id'])
            if not evaluatee:
                continue
            
            # 找到跨部门的同级同事
            cross_peers = self._find_cross_peers(org_emp)
            
            # 限制评价人数
            selected_peers = cross_peers[:max_evaluators]
            
            for peer_org in selected_peers:
                peer_local = self.local_employee_map.get(peer_org['employee_id'])
                if not peer_local:
                    continue
                
                if not self._is_evaluation_allowed(peer_org, org_emp):
                    continue
                
                # 为考核人生成考核码
                evaluator_code = self._generate_evaluator_code(peer_local.id)
                
                EvaluationTask.objects.create(
                    cycle=self.cycle,
                    evaluatee=evaluatee,
                    evaluator=peer_local,
                    relation_type='cross_peer',
                    weight=weight,
                    status='pending',
                    evaluation_code=evaluator_code
                )
                tasks_created += 1
        
        return tasks_created
    
    def _find_peers(self, org_emp: Dict[str, Any]) -> List[Dict[str, Any]]:
        """找到同级同事"""
        peers = []
        
        if self.rule.evaluation_scope == 'department':
            # 同部门同级
            peers = [
                emp for emp in self.org_employees_data 
                if emp['department'] == org_emp['department'] 
                and emp['id'] != org_emp['id']  # 排除自己
                and emp['id'] != org_emp.get('supervisor')  # 排除上级
                and emp.get('supervisor') == org_emp.get('supervisor')  # 同一个上级（同级）
            ]
        elif self.rule.evaluation_scope == 'unit':
            # 同单位同级（需要根据实际的单位字段调整）
            peers = [
                emp for emp in self.org_employees_data 
                if emp.get('unit_id') == org_emp.get('unit_id')
                and emp['id'] != org_emp['id']
                and abs(emp.get('position_level', 0) - org_emp.get('position_level', 0)) <= self.rule.position_level_diff_limit
            ]
        elif self.rule.evaluation_scope == 'company':
            # 全公司同级
            peers = [
                emp for emp in self.org_employees_data 
                if emp['id'] != org_emp['id']
                and abs(emp.get('position_level', 0) - org_emp.get('position_level', 0)) <= self.rule.position_level_diff_limit
            ]
        
        return peers
    
    def _find_cross_peers(self, org_emp: Dict[str, Any]) -> List[Dict[str, Any]]:
        """找到跨部门的同级同事"""
        cross_peers = []
        
        for emp in self.org_employees_data:
            # 排除自己
            if emp['id'] == org_emp['id']:
                continue
            
            # 排除上级和下级
            if emp['id'] == org_emp.get('supervisor') or org_emp['id'] == emp.get('supervisor'):
                continue
            
            # 必须是不同部门
            if emp['department'] == org_emp['department']:
                continue
            
            # 检查职位级别差距
            level_diff = abs(emp.get('position_level', 0) - org_emp.get('position_level', 0))
            if level_diff <= self.rule.position_level_diff_limit:
                cross_peers.append(emp)
        
        return cross_peers
    
    def _is_evaluation_allowed(self, evaluator_org: Dict[str, Any], evaluatee_org: Dict[str, Any]) -> bool:
        """检查是否允许该评价关系"""
        # 检查跨部门限制
        if not self.rule.allow_cross_department and evaluator_org['department'] != evaluatee_org['department']:
            return False
        
        # 检查跨单位限制
        if not self.rule.allow_cross_unit and evaluator_org.get('unit_id') != evaluatee_org.get('unit_id'):
            return False
        
        # 检查职位级别差距限制
        evaluator_level = evaluator_org.get('position_level', 0)
        evaluatee_level = evaluatee_org.get('position_level', 0)
        level_diff = abs(evaluator_level - evaluatee_level)
        if level_diff > self.rule.position_level_diff_limit:
            return False
        
        return True
    


def create_default_evaluation_rules():
    """创建默认的考核规则"""
    from .models import EvaluationRule
    
    # 1. 上级评下级规则
    EvaluationRule.objects.get_or_create(
        name='上级评下级',
        defaults={
            'description': '仅上级对下级进行考核评价',
            'relation_types': ['superior'],
            'evaluation_scope': 'department',
            'max_evaluators_per_relation': 1,
            'min_evaluators_per_relation': 1,
            'relation_weights': {'superior': 1.0},
            'allow_cross_department': False,
            'allow_cross_unit': False,
            'allow_self_evaluation': False,
        }
    )
    
    # 2. 360度评价规则
    EvaluationRule.objects.get_or_create(
        name='360度全方位评价',
        defaults={
            'description': '包含上级、同级、下级和自评的全方位评价',
            'relation_types': ['superior', 'peer', 'subordinate', 'self'],
            'evaluation_scope': 'department',
            'max_evaluators_per_relation': 3,
            'min_evaluators_per_relation': 1,
            'relation_weights': {
                'superior': 0.5,
                'peer': 0.3,
                'subordinate': 0.1,
                'self': 0.1
            },
            'allow_cross_department': False,
            'allow_cross_unit': False,
            'allow_self_evaluation': True,
        }
    )
    
    # 3. 同级互评规则
    EvaluationRule.objects.get_or_create(
        name='同级互评',
        defaults={
            'description': '仅同级同事之间互相评价',
            'relation_types': ['peer'],
            'evaluation_scope': 'department',
            'max_evaluators_per_relation': 5,
            'min_evaluators_per_relation': 2,
            'relation_weights': {'peer': 1.0},
            'allow_cross_department': True,
            'allow_cross_unit': False,
            'allow_self_evaluation': False,
        }
    )
    
    # 4. 跨部门评价规则
    EvaluationRule.objects.get_or_create(
        name='跨部门协作评价',
        defaults={
            'description': '允许跨部门的上级和同级评价',
            'relation_types': ['superior', 'cross_superior', 'peer', 'cross_peer'],
            'evaluation_scope': 'company',
            'max_evaluators_per_relation': 3,
            'min_evaluators_per_relation': 1,
            'relation_weights': {
                'superior': 0.4,
                'cross_superior': 0.2,
                'peer': 0.2,
                'cross_peer': 0.2
            },
            'allow_cross_department': True,
            'allow_cross_unit': False,
            'allow_self_evaluation': False,
        }
    )