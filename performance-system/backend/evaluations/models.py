from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import string
import random
from decimal import Decimal
import json


class EvaluationRule(models.Model):
    """考核规则模型"""
    SCOPE_CHOICES = [
        ('department', '本部门'),
        ('unit', '本单位'),
        ('company', '全公司'),
        ('cross_department', '跨部门'),
        ('cross_unit', '跨单位'),
        ('manual', '手动选择'),
    ]
    
    RELATION_CHOICES = [
        ('superior', '上级评下级'),
        ('peer', '同级互评'),
        ('subordinate', '下级评上级'),
        ('self', '自评'),
        ('cross_superior', '跨部门上级'),
        ('cross_peer', '跨部门同级'),
        ('custom', '自定义关系'),
    ]
    
    name = models.CharField('规则名称', max_length=100)
    description = models.TextField('规则描述', blank=True)
    
    # 评价关系配置
    relation_types = models.JSONField('评价关系类型', default=list, help_text='允许的评价关系类型列表')
    
    # 评价范围配置
    evaluation_scope = models.CharField('评价范围', max_length=20, choices=SCOPE_CHOICES, default='department')
    
    # 人数限制
    max_evaluators_per_relation = models.IntegerField('每种关系最大评价人数', default=3)
    min_evaluators_per_relation = models.IntegerField('每种关系最少评价人数', default=1)
    
    # 权重配置
    relation_weights = models.JSONField('关系权重', default=dict, help_text='不同关系的权重分配')
    
    # 特殊规则
    allow_cross_department = models.BooleanField('允许跨部门', default=False)
    allow_cross_unit = models.BooleanField('允许跨单位', default=False)
    allow_self_evaluation = models.BooleanField('允许自评', default=False)
    
    # 级别限制
    position_level_diff_limit = models.IntegerField('职位级别差距限制', default=2, help_text='允许的职位级别差距')
    
    # 高级配置
    custom_rules = models.JSONField('自定义规则', default=dict, blank=True, help_text='高级自定义规则配置')
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '考核规则'
        verbose_name_plural = '考核规则'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_relation_weight(self, relation_type):
        """获取指定关系类型的权重"""
        return self.relation_weights.get(relation_type, 1.0)
    
    def validate_weights(self):
        """验证权重分配是否合理"""
        total_weight = sum(self.relation_weights.values())
        return abs(total_weight - 1.0) < 0.01  # 允许小数误差


class ManualEvaluationAssignment(models.Model):
    """手动评价分配模型"""
    cycle = models.ForeignKey('EvaluationCycle', verbose_name='考核周期', on_delete=models.CASCADE)
    evaluator = models.ForeignKey('Employee', verbose_name='评价人', on_delete=models.CASCADE, related_name='manual_evaluator_assignments')
    evaluatee = models.ForeignKey('Employee', verbose_name='被评价人', on_delete=models.CASCADE, related_name='manual_evaluatee_assignments')
    relation_type = models.CharField('关系类型', max_length=20, default='custom')
    weight = models.DecimalField('权重', max_digits=5, decimal_places=2, default=Decimal('1.00'))
    reason = models.TextField('分配原因', blank=True)
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.CASCADE)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '手动评价分配'
        verbose_name_plural = '手动评价分配'
        unique_together = ['cycle', 'evaluator', 'evaluatee']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.evaluator.name} 评价 {self.evaluatee.name}"


class EvaluationCycle(models.Model):
    """考核周期模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    name = models.CharField('周期名称', max_length=100)
    description = models.TextField('周期描述', blank=True)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # 考核规则关联
    evaluation_rule = models.ForeignKey('EvaluationRule', verbose_name='考核规则', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.CASCADE)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '考核周期'
        verbose_name_plural = '考核周期'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class EvaluationIndicator(models.Model):
    """考核指标模型"""
    CATEGORY_CHOICES = [
        ('performance', '工作绩效'),
        ('ability', '工作能力'),
        ('attitude', '工作态度'),
        ('teamwork', '团队合作'),
        ('innovation', '创新能力'),
    ]
    
    name = models.CharField('指标名称', max_length=100)
    category = models.CharField('指标类别', max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField('指标描述')
    weight = models.DecimalField('权重', max_digits=5, decimal_places=2, 
                                validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('1.00'))])
    max_score = models.IntegerField('最高分数', default=100)
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '考核指标'
        verbose_name_plural = '考核指标'
        ordering = ['category', '-weight']

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"


class Employee(models.Model):
    """员工模型（从中台同步）"""
    employee_id = models.CharField('员工号', max_length=20, unique=True)
    name = models.CharField('姓名', max_length=50)
    department_id = models.IntegerField('部门ID')
    department_name = models.CharField('部门名称', max_length=100)
    position_id = models.IntegerField('职位 ID')
    position_name = models.CharField('职位名称', max_length=100)
    position_level = models.IntegerField('职位级别', default=1)
    supervisor_id = models.IntegerField('上级ID', null=True, blank=True)
    email = models.EmailField('邮箱', blank=True)
    phone = models.CharField('手机', max_length=20, blank=True)
    status = models.CharField('状态', max_length=20, default='active')
    is_active = models.BooleanField('是否激活', default=True)
    last_sync = models.DateTimeField('最后同步时间', auto_now=True)

    class Meta:
        verbose_name = '员工'
        verbose_name_plural = '员工'
        ordering = ['department_name', 'position_level', 'employee_id']

    def __str__(self):
        return f"{self.name} ({self.employee_id})"


class EvaluationTask(models.Model):
    """考核任务模型"""
    RELATION_CHOICES = [
        ('superior', '上级考核下级'),
        ('peer', '同级互评'),
        ('subordinate', '下级评价上级'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待考核'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('overdue', '已过期'),
    ]
    
    cycle = models.ForeignKey(EvaluationCycle, verbose_name='考核周期', on_delete=models.CASCADE)
    evaluator = models.ForeignKey(Employee, verbose_name='考核人', on_delete=models.CASCADE, related_name='evaluation_tasks')
    evaluatee = models.ForeignKey(Employee, verbose_name='被考核人', on_delete=models.CASCADE, related_name='being_evaluated')
    relation_type = models.CharField('考核关系', max_length=20, choices=RELATION_CHOICES)
    evaluation_code = models.CharField('考核码', max_length=16, unique=True)
    weight = models.DecimalField('考核权重', max_digits=5, decimal_places=2, default=Decimal('1.00'))
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)

    class Meta:
        verbose_name = '考核任务'
        verbose_name_plural = '考核任务'
        unique_together = ['cycle', 'evaluator', 'evaluatee', 'relation_type']
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.evaluator.name} 评价 {self.evaluatee.name} ({self.get_relation_type_display()})"

    def save(self, *args, **kwargs):
        if not self.evaluation_code:
            self.evaluation_code = self.generate_evaluation_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_evaluation_code():
        """生成 16 位唯一考核码"""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(characters, k=16))
            if not EvaluationTask.objects.filter(evaluation_code=code).exists():
                return code


class EvaluationScore(models.Model):
    """考核评分模型"""
    task = models.ForeignKey(EvaluationTask, verbose_name='考核任务', on_delete=models.CASCADE)
    indicator = models.ForeignKey(EvaluationIndicator, verbose_name='考核指标', on_delete=models.CASCADE)
    score = models.IntegerField('评分', validators=[MinValueValidator(0), MaxValueValidator(100)])
    comment = models.TextField('评价意见', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '考核评分'
        verbose_name_plural = '考核评分'
        unique_together = ['task', 'indicator']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task.evaluator.name} - {self.indicator.name}: {self.score}分"


class EvaluationResult(models.Model):
    """考核结果汇总模型"""
    cycle = models.ForeignKey(EvaluationCycle, verbose_name='考核周期', on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, verbose_name='被考核员工', on_delete=models.CASCADE)
    total_score = models.DecimalField('总分', max_digits=6, decimal_places=2, default=Decimal('0.00'))
    weighted_score = models.DecimalField('加权平均分', max_digits=6, decimal_places=2, default=Decimal('0.00'))
    superior_score = models.DecimalField('上级评分', max_digits=6, decimal_places=2, null=True, blank=True)
    peer_score = models.DecimalField('同级评分', max_digits=6, decimal_places=2, null=True, blank=True)
    subordinate_score = models.DecimalField('下级评分', max_digits=6, decimal_places=2, null=True, blank=True)
    rank = models.IntegerField('排名', null=True, blank=True)
    is_final = models.BooleanField('是否最终结果', default=False)
    calculated_at = models.DateTimeField('计算时间', auto_now=True)

    class Meta:
        verbose_name = '考核结果'
        verbose_name_plural = '考核结果'
        unique_together = ['cycle', 'employee']
        ordering = ['-weighted_score']

    def __str__(self):
        return f"{self.cycle.name} - {self.employee.name}: {self.weighted_score}分"
