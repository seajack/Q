from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import string
import random
from decimal import Decimal


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
