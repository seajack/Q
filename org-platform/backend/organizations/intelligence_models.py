"""
智能分析数据模型
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import json


class AnalysisResult(models.Model):
    """分析结果模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField('分析类别', max_length=100)
    score = models.DecimalField('评分', max_digits=5, decimal_places=2)
    level = models.CharField('等级', max_length=50)
    description = models.TextField('描述')
    details = models.JSONField('详细信息', default=dict)
    recommendations = models.JSONField('建议', default=list)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '分析结果'
        verbose_name_plural = '分析结果'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category} - {self.score}"


class OptimizationRecommendation(models.Model):
    """优化建议模型"""
    PRIORITY_CHOICES = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    priority = models.CharField('优先级', max_length=10, choices=PRIORITY_CHOICES)
    category = models.CharField('类别', max_length=100)
    title = models.CharField('标题', max_length=200)
    description = models.TextField('描述')
    expected_benefit = models.TextField('预期收益')
    implementation_cost = models.DecimalField('实施成本', max_digits=10, decimal_places=2)
    timeframe = models.CharField('时间框架', max_length=100)
    impacted_departments = models.JSONField('影响部门', default=list)
    metrics = models.JSONField('指标', default=dict)
    is_implemented = models.BooleanField('是否已实施', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '优化建议'
        verbose_name_plural = '优化建议'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"


class OrganizationAnalysis(models.Model):
    """组织分析模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    overall_score = models.DecimalField('总体评分', max_digits=5, decimal_places=2)
    health_level = models.CharField('健康等级', max_length=50)
    analysis_results = models.ManyToManyField(AnalysisResult, verbose_name='分析结果')
    recommendations = models.ManyToManyField(OptimizationRecommendation, verbose_name='建议')
    metrics = models.JSONField('指标', default=dict)
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '组织分析'
        verbose_name_plural = '组织分析'
        ordering = ['-created_at']

    def __str__(self):
        return f"组织分析 - {self.overall_score} ({self.health_level})"


class AnalysisHistory(models.Model):
    """分析历史模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField('分析日期')
    overall_score = models.DecimalField('总体评分', max_digits=5, decimal_places=2)
    health_level = models.CharField('健康等级', max_length=50)
    key_changes = models.JSONField('关键变化', default=list)
    analysis = models.ForeignKey(OrganizationAnalysis, on_delete=models.CASCADE, verbose_name='关联分析')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '分析历史'
        verbose_name_plural = '分析历史'
        ordering = ['-date']

    def __str__(self):
        return f"分析历史 - {self.date} ({self.overall_score})"


class AnalysisConfig(models.Model):
    """分析配置模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('配置名称', max_length=100)
    analysis_weights = models.JSONField('分析权重', default=dict)
    thresholds = models.JSONField('阈值', default=dict)
    enabled_features = models.JSONField('启用功能', default=list)
    update_frequency = models.IntegerField('更新频率(小时)', default=24)
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '分析配置'
        verbose_name_plural = '分析配置'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class UserFeedback(models.Model):
    """用户反馈模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    analysis = models.ForeignKey(OrganizationAnalysis, on_delete=models.CASCADE, verbose_name='分析')
    rating = models.IntegerField('评分', choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField('评论', blank=True)
    helpful_suggestions = models.JSONField('有用建议', default=list)
    improvement_areas = models.JSONField('改进领域', default=list)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户反馈'
        verbose_name_plural = '用户反馈'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.analysis} ({self.rating}星)"


class BenchmarkData(models.Model):
    """基准数据模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    industry = models.CharField('行业', max_length=100)
    company_size = models.CharField('公司规模', max_length=50)
    metric_name = models.CharField('指标名称', max_length=100)
    benchmark_value = models.DecimalField('基准值', max_digits=10, decimal_places=2)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '基准数据'
        verbose_name_plural = '基准数据'
        ordering = ['industry', 'company_size', 'metric_name']

    def __str__(self):
        return f"{self.industry} - {self.metric_name} ({self.benchmark_value})"
