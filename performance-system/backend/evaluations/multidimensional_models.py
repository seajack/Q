from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import json


class EvaluationDimension(models.Model):
    """评估维度模型"""
    DIMENSION_TYPES = [
        ('capability', '能力维度'),
        ('attitude', '态度维度'),
        ('performance', '业绩维度'),
        ('innovation', '创新维度'),
        ('leadership', '领导力维度'),
        ('teamwork', '团队合作维度'),
        ('customer_service', '客户服务维度'),
        ('custom', '自定义维度'),
    ]
    
    name = models.CharField('维度名称', max_length=100)
    dimension_type = models.CharField('维度类型', max_length=20, choices=DIMENSION_TYPES)
    description = models.TextField('维度描述', blank=True)
    weight = models.DecimalField('维度权重', max_digits=5, decimal_places=2, default=Decimal('1.00'),
                                validators=[MinValueValidator(0), MaxValueValidator(1)])
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '评估维度'
        verbose_name_plural = '评估维度'
        ordering = ['-weight', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_dimension_type_display()})"


class EvaluationMethod(models.Model):
    """评估方法模型"""
    METHOD_TYPES = [
        ('360_degree', '360度评估'),
        ('okr', 'OKR目标与关键结果'),
        ('kpi', 'KPI关键绩效指标'),
        ('mbo', 'MBO目标管理'),
        ('bsc', 'BSC平衡计分卡'),
        ('custom', '自定义方法'),
    ]
    
    name = models.CharField('方法名称', max_length=100)
    method_type = models.CharField('方法类型', max_length=20, choices=METHOD_TYPES)
    description = models.TextField('方法描述', blank=True)
    configuration = models.JSONField('方法配置', default=dict, help_text='评估方法的具体配置')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '评估方法'
        verbose_name_plural = '评估方法'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_method_type_display()})"


class EvaluationCycleType(models.Model):
    """评估周期类型模型"""
    CYCLE_TYPES = [
        ('annual', '年度'),
        ('quarterly', '季度'),
        ('monthly', '月度'),
        ('weekly', '周度'),
        ('custom', '自定义'),
    ]
    
    name = models.CharField('周期类型名称', max_length=100)
    cycle_type = models.CharField('周期类型', max_length=20, choices=CYCLE_TYPES)
    duration_days = models.IntegerField('周期天数', help_text='一个完整周期的天数')
    description = models.TextField('描述', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '评估周期类型'
        verbose_name_plural = '评估周期类型'
        ordering = ['duration_days']
    
    def __str__(self):
        return f"{self.name} ({self.get_cycle_type_display()})"


class MultidimensionalEvaluation(models.Model):
    """多维度评估模型"""
    cycle = models.ForeignKey('evaluations.EvaluationCycle', verbose_name='考核周期', on_delete=models.CASCADE)
    evaluator = models.ForeignKey('evaluations.Employee', verbose_name='评价人', on_delete=models.CASCADE, related_name='multidimensional_evaluations')
    evaluatee = models.ForeignKey('evaluations.Employee', verbose_name='被评价人', on_delete=models.CASCADE, related_name='multidimensional_evaluated')
    evaluation_method = models.ForeignKey(EvaluationMethod, verbose_name='评估方法', on_delete=models.CASCADE)
    dimensions = models.JSONField('维度评分', default=dict, help_text='各维度的评分结果')
    total_score = models.DecimalField('总分', max_digits=5, decimal_places=2, null=True, blank=True)
    weighted_score = models.DecimalField('加权分', max_digits=5, decimal_places=2, null=True, blank=True)
    comments = models.TextField('评价意见', blank=True)
    status = models.CharField('状态', max_length=20, choices=[
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('reviewed', '已审核'),
        ('finalized', '已确定'),
    ], default='draft')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '多维度评估'
        verbose_name_plural = '多维度评估'
        unique_together = ['cycle', 'evaluator', 'evaluatee', 'evaluation_method']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.evaluator.name} 对 {self.evaluatee.name} 的{self.evaluation_method.name}评估"
    
    def calculate_total_score(self):
        """计算总分"""
        if not self.dimensions:
            return None
        
        total = 0
        for dimension_id, score in self.dimensions.items():
            try:
                dimension = EvaluationDimension.objects.get(id=dimension_id)
                total += float(score) * float(dimension.weight)
            except (EvaluationDimension.DoesNotExist, ValueError):
                continue
        
        self.total_score = Decimal(str(total))
        return self.total_score
    
    def calculate_weighted_score(self, evaluator_weight=1.0):
        """计算加权分"""
        if self.total_score:
            self.weighted_score = self.total_score * Decimal(str(evaluator_weight))
            return self.weighted_score
        return None


class MultidimensionalIndicator(models.Model):
    """多维度评估指标模型"""
    dimension = models.ForeignKey(EvaluationDimension, verbose_name='所属维度', on_delete=models.CASCADE)
    name = models.CharField('指标名称', max_length=200)
    description = models.TextField('指标描述', blank=True)
    weight = models.DecimalField('指标权重', max_digits=5, decimal_places=2, default=Decimal('1.00'),
                                validators=[MinValueValidator(0), MaxValueValidator(1)])
    scoring_criteria = models.JSONField('评分标准', default=dict, help_text='评分标准和规则')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '多维度评估指标'
        verbose_name_plural = '多维度评估指标'
        ordering = ['dimension', '-weight', 'name']
    
    def __str__(self):
        return f"{self.dimension.name} - {self.name}"


class EvaluationTemplate(models.Model):
    """评估模板模型"""
    name = models.CharField('模板名称', max_length=100)
    description = models.TextField('模板描述', blank=True)
    evaluation_method = models.ForeignKey(EvaluationMethod, verbose_name='评估方法', on_delete=models.CASCADE)
    dimensions = models.ManyToManyField(EvaluationDimension, verbose_name='包含维度', through='TemplateDimension')
    is_default = models.BooleanField('是否默认模板', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.CASCADE)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '评估模板'
        verbose_name_plural = '评估模板'
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return self.name


class TemplateDimension(models.Model):
    """模板维度关联模型"""
    template = models.ForeignKey(EvaluationTemplate, verbose_name='模板', on_delete=models.CASCADE)
    dimension = models.ForeignKey(EvaluationDimension, verbose_name='维度', on_delete=models.CASCADE)
    weight = models.DecimalField('权重', max_digits=5, decimal_places=2, default=Decimal('1.00'))
    order = models.IntegerField('排序', default=0)
    
    class Meta:
        verbose_name = '模板维度'
        verbose_name_plural = '模板维度'
        unique_together = ['template', 'dimension']
        ordering = ['order']
    
    def __str__(self):
        return f"{self.template.name} - {self.dimension.name}"
