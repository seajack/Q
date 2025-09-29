"""
智能组织架构分析模块
提供AI驱动的组织架构分析、优化建议和预测功能
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

from django.db.models import Count, Avg, Q
from django.utils import timezone

from .models import Department, Employee, Position


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    category: str
    score: float
    level: str  # 'excellent', 'good', 'warning', 'critical'
    description: str
    details: Dict
    recommendations: List[str]


@dataclass
class OptimizationRecommendation:
    """优化建议数据类"""
    id: str
    priority: str  # 'high', 'medium', 'low'
    category: str
    title: str
    description: str
    expected_benefit: str
    implementation_cost: float
    timeframe: str
    impacted_departments: List[str]
    metrics: Dict


class OrganizationIntelligence:
    """组织架构智能分析引擎"""
    
    def __init__(self):
        self.analysis_weights = {
            'structure_efficiency': 0.3,
            'communication_effectiveness': 0.25,
            'resource_utilization': 0.2,
            'growth_potential': 0.15,
            'risk_assessment': 0.1
        }
    
    def analyze_organization(self) -> Dict:
        """执行完整的组织架构分析"""
        results = {
            'overall_score': 0,
            'health_level': 'unknown',
            'analysis_results': [],
            'recommendations': [],
            'metrics': {},
            'timestamp': timezone.now().isoformat()
        }
        
        # 执行各项分析
        structure_analysis = self.analyze_structure_efficiency()
        communication_analysis = self.analyze_communication_effectiveness()
        resource_analysis = self.analyze_resource_utilization()
        growth_analysis = self.analyze_growth_potential()
        risk_analysis = self.assess_organizational_risks()
        
        # 收集分析结果
        analyses = [
            structure_analysis,
            communication_analysis,
            resource_analysis,
            growth_analysis,
            risk_analysis
        ]
        
        results['analysis_results'] = analyses
        
        # 计算综合得分
        weighted_score = sum(
            analysis.score * self.analysis_weights.get(analysis.category, 0.2)
            for analysis in analyses
        )
        results['overall_score'] = round(weighted_score, 1)
        
        # 确定健康等级
        results['health_level'] = self._determine_health_level(weighted_score)
        
        # 生成优化建议
        results['recommendations'] = self.generate_optimization_recommendations(analyses)
        
        # 计算关键指标
        results['metrics'] = self.calculate_key_metrics()
        
        return results
    
    def analyze_structure_efficiency(self) -> AnalysisResult:
        """分析组织结构效率"""
        departments = Department.objects.all()
        employees = Employee.objects.all()
        
        # 计算管理幅度
        span_of_control = self._calculate_span_of_control()
        
        # 计算层级深度
        hierarchy_depth = self._calculate_hierarchy_depth()
        
        # 计算部门平衡度
        department_balance = self._calculate_department_balance()
        
        # 综合评分
        efficiency_score = (
            span_of_control['score'] * 0.4 +
            hierarchy_depth['score'] * 0.3 +
            department_balance['score'] * 0.3
        )
        
        return AnalysisResult(
            category='structure_efficiency',
            score=efficiency_score,
            level=self._score_to_level(efficiency_score),
            description=f"组织结构效率得分 {efficiency_score:.1f}分",
            details={
                'span_of_control': span_of_control,
                'hierarchy_depth': hierarchy_depth,
                'department_balance': department_balance,
                'total_departments': departments.count(),
                'total_employees': employees.count()
            },
            recommendations=self._generate_structure_recommendations(
                span_of_control, hierarchy_depth, department_balance
            )
        )
    
    def analyze_communication_effectiveness(self) -> AnalysisResult:
        """分析沟通效率"""
        # 计算跨部门协作指数
        cross_dept_score = self._calculate_cross_department_collaboration()
        
        # 计算汇报链效率
        reporting_efficiency = self._calculate_reporting_efficiency()
        
        # 计算信息传递速度
        information_flow = self._calculate_information_flow_speed()
        
        # 综合评分
        communication_score = (
            cross_dept_score * 0.4 +
            reporting_efficiency * 0.35 +
            information_flow * 0.25
        )
        
        return AnalysisResult(
            category='communication_effectiveness',
            score=communication_score,
            level=self._score_to_level(communication_score),
            description=f"沟通效率得分 {communication_score:.1f}分",
            details={
                'cross_department_collaboration': cross_dept_score,
                'reporting_efficiency': reporting_efficiency,
                'information_flow_speed': information_flow
            },
            recommendations=self._generate_communication_recommendations(
                cross_dept_score, reporting_efficiency, information_flow
            )
        )
    
    def analyze_resource_utilization(self) -> AnalysisResult:
        """分析资源利用率"""
        # 人员配置合理性
        staffing_efficiency = self._calculate_staffing_efficiency()
        
        # 技能匹配度
        skill_matching = self._calculate_skill_matching()
        
        # 工作负载平衡
        workload_balance = self._calculate_workload_balance()
        
        # 综合评分
        resource_score = (
            staffing_efficiency * 0.4 +
            skill_matching * 0.35 +
            workload_balance * 0.25
        )
        
        return AnalysisResult(
            category='resource_utilization',
            score=resource_score,
            level=self._score_to_level(resource_score),
            description=f"资源利用率得分 {resource_score:.1f}分",
            details={
                'staffing_efficiency': staffing_efficiency,
                'skill_matching': skill_matching,
                'workload_balance': workload_balance
            },
            recommendations=self._generate_resource_recommendations(
                staffing_efficiency, skill_matching, workload_balance
            )
        )
    
    def analyze_growth_potential(self) -> AnalysisResult:
        """分析成长潜力"""
        # 扩展能力
        scalability = self._calculate_scalability()
        
        # 创新能力
        innovation_capacity = self._calculate_innovation_capacity()
        
        # 适应性
        adaptability = self._calculate_adaptability()
        
        # 综合评分
        growth_score = (
            scalability * 0.4 +
            innovation_capacity * 0.35 +
            adaptability * 0.25
        )
        
        return AnalysisResult(
            category='growth_potential',
            score=growth_score,
            level=self._score_to_level(growth_score),
            description=f"成长潜力得分 {growth_score:.1f}分",
            details={
                'scalability': scalability,
                'innovation_capacity': innovation_capacity,
                'adaptability': adaptability
            },
            recommendations=self._generate_growth_recommendations(
                scalability, innovation_capacity, adaptability
            )
        )
    
    def assess_organizational_risks(self) -> AnalysisResult:
        """评估组织风险"""
        # 单点故障风险
        single_point_risk = self._assess_single_point_failures()
        
        # 人员流失风险
        turnover_risk = self._assess_turnover_risk()
        
        # 技能缺口风险
        skill_gap_risk = self._assess_skill_gaps()
        
        # 综合风险评分（分数越低风险越高）
        risk_score = 100 - (
            single_point_risk * 0.4 +
            turnover_risk * 0.35 +
            skill_gap_risk * 0.25
        )
        
        return AnalysisResult(
            category='risk_assessment',
            score=max(0, risk_score),
            level=self._risk_to_level(risk_score),
            description=f"风险评估得分 {risk_score:.1f}分",
            details={
                'single_point_failures': single_point_risk,
                'turnover_risk': turnover_risk,
                'skill_gap_risk': skill_gap_risk
            },
            recommendations=self._generate_risk_recommendations(
                single_point_risk, turnover_risk, skill_gap_risk
            )
        )
    
    def generate_optimization_recommendations(self, analyses: List[AnalysisResult]) -> List[OptimizationRecommendation]:
        """生成优化建议"""
        recommendations = []
        
        for analysis in analyses:
            if analysis.score < 70:  # 需要改进的领域
                category_recommendations = self._generate_category_recommendations(analysis)
                recommendations.extend(category_recommendations)
        
        # 按优先级排序
        recommendations.sort(key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x.priority], reverse=True)
        
        return recommendations[:10]  # 返回前10个建议
    
    def _calculate_span_of_control(self) -> Dict:
        """计算管理幅度"""
        departments = Department.objects.all()
        spans = []
        
        for dept in departments:
            if dept.parent:  # 不是根部门
                subordinates = dept.parent.children.count()
                if subordinates > 0:
                    spans.append(subordinates)
        
        if not spans:
            return {'average': 0, 'score': 50, 'assessment': '无法评估'}
        
        avg_span = sum(spans) / len(spans)
        
        # 理想管理幅度为5-8人
        if 5 <= avg_span <= 8:
            score = 90
            assessment = '优秀'
        elif 3 <= avg_span <= 10:
            score = 75
            assessment = '良好'
        elif avg_span < 3:
            score = 60
            assessment = '管理幅度过小'
        else:
            score = 50
            assessment = '管理幅度过大'
        
        return {
            'average': round(avg_span, 1),
            'score': score,
            'assessment': assessment,
            'details': spans
        }
    
    def _calculate_hierarchy_depth(self) -> Dict:
        """计算层级深度"""
        max_depth = 0
        
        def get_depth(department, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            for child in department.children.all():
                get_depth(child, current_depth + 1)
        
        # 从根部门开始计算
        root_departments = Department.objects.filter(parent=None)
        for root in root_departments:
            get_depth(root, 1)
        
        # 理想层级深度为3-5层
        if 3 <= max_depth <= 5:
            score = 90
            assessment = '层级合理'
        elif max_depth <= 2:
            score = 70
            assessment = '层级过浅'
        elif max_depth <= 7:
            score = 60
            assessment = '层级较深'
        else:
            score = 40
            assessment = '层级过深'
        
        return {
            'max_depth': max_depth,
            'score': score,
            'assessment': assessment
        }
    
    def _calculate_department_balance(self) -> Dict:
        """计算部门平衡度"""
        departments = Department.objects.annotate(
            employee_count=Count('employees')
        )
        
        sizes = [dept.employee_count for dept in departments if dept.employee_count > 0]
        
        if not sizes:
            return {'score': 50, 'assessment': '无员工数据'}
        
        # 计算变异系数
        mean_size = sum(sizes) / len(sizes)
        variance = sum((size - mean_size) ** 2 for size in sizes) / len(sizes)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean_size if mean_size > 0 else 0
        
        # 变异系数越小，平衡度越好
        if cv <= 0.3:
            score = 90
            assessment = '部门规模均衡'
        elif cv <= 0.5:
            score = 75
            assessment = '部门规模较均衡'
        elif cv <= 0.8:
            score = 60
            assessment = '部门规模不均衡'
        else:
            score = 40
            assessment = '部门规模严重不均衡'
        
        return {
            'coefficient_of_variation': round(cv, 2),
            'mean_size': round(mean_size, 1),
            'score': score,
            'assessment': assessment
        }
    
    def _calculate_cross_department_collaboration(self) -> float:
        """计算跨部门协作指数"""
        # 这里可以基于项目数据、会议数据等计算
        # 暂时返回模拟数据
        return 75.0
    
    def _calculate_reporting_efficiency(self) -> float:
        """计算汇报链效率"""
        # 基于层级深度和管理幅度计算
        hierarchy = self._calculate_hierarchy_depth()
        span = self._calculate_span_of_control()
        
        # 层级越深效率越低，管理幅度适中效率最高
        depth_penalty = max(0, (hierarchy['max_depth'] - 4) * 10)
        span_bonus = span['score'] * 0.3
        
        efficiency = max(0, 80 - depth_penalty + span_bonus)
        return min(100, efficiency)
    
    def _calculate_information_flow_speed(self) -> float:
        """计算信息传递速度"""
        # 基于组织结构复杂度计算
        hierarchy = self._calculate_hierarchy_depth()
        departments_count = Department.objects.count()
        
        # 部门数量和层级深度影响信息传递速度
        complexity_penalty = (departments_count * 2 + hierarchy['max_depth'] * 5)
        speed = max(30, 100 - complexity_penalty)
        
        return min(100, speed)
    
    def _calculate_staffing_efficiency(self) -> float:
        """计算人员配置效率"""
        departments = Department.objects.annotate(
            employee_count=Count('employees')
        )
        
        # 检查是否有空部门
        empty_departments = departments.filter(employee_count=0).count()
        total_departments = departments.count()
        
        if total_departments == 0:
            return 50
        
        # 空部门比例影响效率
        empty_ratio = empty_departments / total_departments
        efficiency = max(40, 100 - empty_ratio * 50)
        
        return efficiency
    
    def _calculate_skill_matching(self) -> float:
        """计算技能匹配度"""
        # 这里可以基于员工技能和岗位要求匹配度计算
        # 暂时返回模拟数据
        return 78.0
    
    def _calculate_workload_balance(self) -> float:
        """计算工作负载平衡"""
        # 这里可以基于员工工作量数据计算
        # 暂时返回模拟数据
        return 72.0
    
    def _calculate_scalability(self) -> float:
        """计算扩展能力"""
        # 基于组织结构灵活性计算
        hierarchy = self._calculate_hierarchy_depth()
        
        # 层级适中的组织扩展能力更强
        if 3 <= hierarchy['max_depth'] <= 5:
            return 85.0
        elif hierarchy['max_depth'] <= 2:
            return 70.0
        else:
            return 60.0
    
    def _calculate_innovation_capacity(self) -> float:
        """计算创新能力"""
        # 这里可以基于团队多样性、跨部门协作等计算
        # 暂时返回模拟数据
        return 68.0
    
    def _calculate_adaptability(self) -> float:
        """计算适应性"""
        # 基于组织结构复杂度和灵活性计算
        span = self._calculate_span_of_control()
        
        # 管理幅度适中的组织适应性更强
        return span['score'] * 0.8
    
    def _assess_single_point_failures(self) -> float:
        """评估单点故障风险"""
        # 检查关键岗位是否只有一个人
        critical_positions = Position.objects.filter(
            level__gte=8  # 中高层岗位
        ).annotate(
            employee_count=Count('employees')
        )
        
        single_person_positions = critical_positions.filter(employee_count=1).count()
        total_critical = critical_positions.count()
        
        if total_critical == 0:
            return 0
        
        risk_ratio = single_person_positions / total_critical
        return risk_ratio * 100  # 返回风险百分比
    
    def _assess_turnover_risk(self) -> float:
        """评估人员流失风险"""
        # 这里可以基于历史离职数据、员工满意度等计算
        # 暂时返回模拟数据
        return 25.0  # 25%的流失风险
    
    def _assess_skill_gaps(self) -> float:
        """评估技能缺口风险"""
        # 这里可以基于岗位要求和员工技能匹配度计算
        # 暂时返回模拟数据
        return 30.0  # 30%的技能缺口风险
    
    def _score_to_level(self, score: float) -> str:
        """将分数转换为等级"""
        if score >= 85:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 50:
            return 'warning'
        else:
            return 'critical'
    
    def _risk_to_level(self, risk_score: float) -> str:
        """将风险分数转换为等级"""
        if risk_score >= 80:
            return 'excellent'
        elif risk_score >= 60:
            return 'good'
        elif risk_score >= 40:
            return 'warning'
        else:
            return 'critical'
    
    def _determine_health_level(self, overall_score: float) -> str:
        """确定整体健康等级"""
        return self._score_to_level(overall_score)
    
    def _generate_structure_recommendations(self, span, hierarchy, balance) -> List[str]:
        """生成结构优化建议"""
        recommendations = []
        
        if span['score'] < 70:
            if span['average'] < 3:
                recommendations.append("建议合并部分管理层级，增加管理幅度")
            else:
                recommendations.append("建议增加中层管理人员，减少管理幅度")
        
        if hierarchy['score'] < 70:
            if hierarchy['max_depth'] > 6:
                recommendations.append("建议减少组织层级，扁平化管理结构")
            else:
                recommendations.append("建议适当增加管理层级，明确职责分工")
        
        if balance['score'] < 70:
            recommendations.append("建议调整部门人员配置，平衡各部门规模")
        
        return recommendations
    
    def _generate_communication_recommendations(self, cross_dept, reporting, flow) -> List[str]:
        """生成沟通优化建议"""
        recommendations = []
        
        if cross_dept < 70:
            recommendations.append("建议建立跨部门协作机制，提高协作效率")
        
        if reporting < 70:
            recommendations.append("建议优化汇报流程，减少信息传递层级")
        
        if flow < 70:
            recommendations.append("建议建立信息共享平台，提高信息传递速度")
        
        return recommendations
    
    def _generate_resource_recommendations(self, staffing, skill, workload) -> List[str]:
        """生成资源优化建议"""
        recommendations = []
        
        if staffing < 70:
            recommendations.append("建议优化人员配置，消除空置部门")
        
        if skill < 70:
            recommendations.append("建议加强员工培训，提高技能匹配度")
        
        if workload < 70:
            recommendations.append("建议平衡工作负载，避免人员过载或闲置")
        
        return recommendations
    
    def _generate_growth_recommendations(self, scalability, innovation, adaptability) -> List[str]:
        """生成成长优化建议"""
        recommendations = []
        
        if scalability < 70:
            recommendations.append("建议优化组织结构，提高扩展能力")
        
        if innovation < 70:
            recommendations.append("建议建立创新团队，提高创新能力")
        
        if adaptability < 70:
            recommendations.append("建议增强组织灵活性，提高适应能力")
        
        return recommendations
    
    def _generate_risk_recommendations(self, single_point, turnover, skill_gap) -> List[str]:
        """生成风险缓解建议"""
        recommendations = []
        
        if single_point > 30:
            recommendations.append("建议为关键岗位配备备份人员，降低单点故障风险")
        
        if turnover > 20:
            recommendations.append("建议改善员工满意度，降低人员流失风险")
        
        if skill_gap > 25:
            recommendations.append("建议加强人才培养，填补技能缺口")
        
        return recommendations
    
    def _generate_category_recommendations(self, analysis: AnalysisResult) -> List[OptimizationRecommendation]:
        """为特定分析类别生成详细建议"""
        recommendations = []
        
        if analysis.category == 'structure_efficiency' and analysis.score < 70:
            recommendations.append(OptimizationRecommendation(
                id=f"struct_{datetime.now().timestamp()}",
                priority='high',
                category='structure',
                title='优化组织结构',
                description='当前组织结构效率较低，建议进行结构调整',
                expected_benefit='提高管理效率20%，降低沟通成本15%',
                implementation_cost=50000,
                timeframe='2-3个月',
                impacted_departments=['全部'],
                metrics={'efficiency_improvement': 20, 'cost_reduction': 15}
            ))
        
        # 可以继续添加其他类别的建议...
        
        return recommendations
    
    def calculate_key_metrics(self) -> Dict:
        """计算关键指标"""
        return {
            'total_departments': Department.objects.count(),
            'total_employees': Employee.objects.count(),
            'management_ratio': self._calculate_management_ratio(),
            'average_department_size': self._calculate_average_department_size(),
            'organizational_complexity': self._calculate_organizational_complexity()
        }
    
    def _calculate_management_ratio(self) -> float:
        """计算管理人员比例"""
        total_employees = Employee.objects.count()
        if total_employees == 0:
            return 0
        
        # 假设level >= 8的为管理人员
        managers = Employee.objects.filter(position__level__gte=8).count()
        return round((managers / total_employees) * 100, 1)
    
    def _calculate_average_department_size(self) -> float:
        """计算平均部门规模"""
        departments = Department.objects.annotate(
            employee_count=Count('employees')
        )
        
        sizes = [dept.employee_count for dept in departments]
        return round(sum(sizes) / len(sizes), 1) if sizes else 0
    
    def _calculate_organizational_complexity(self) -> float:
        """计算组织复杂度"""
        dept_count = Department.objects.count()
        hierarchy = self._calculate_hierarchy_depth()
        
        # 复杂度 = 部门数量 * 层级深度
        complexity = dept_count * hierarchy['max_depth']
        return complexity
