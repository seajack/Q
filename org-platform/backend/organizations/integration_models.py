"""
集成管理数据模型
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import json


class IntegrationSystem(models.Model):
    """集成系统模型"""
    SYSTEM_TYPE_CHOICES = [
        ('hr', '人力资源系统'),
        ('erp', 'ERP系统'),
        ('crm', 'CRM系统'),
        ('oa', 'OA系统'),
        ('finance', '财务系统'),
        ('performance', '绩效考核系统'),
        ('custom', '自定义系统'),
        ('other', '其他系统'),
    ]
    
    STATUS_CHOICES = [
        ('active', '激活'),
        ('inactive', '未激活'),
        ('maintenance', '维护中'),
        ('error', '错误'),
    ]

    id = models.BigAutoField(primary_key=True)
    name = models.CharField('系统名称', max_length=100)
    system_type = models.CharField('系统类型', max_length=20, choices=SYSTEM_TYPE_CHOICES)
    description = models.TextField('描述', blank=True)
    base_url = models.URLField('API端点', max_length=500)
    api_version = models.CharField('API版本', max_length=20, default='v1')
    auth_type = models.CharField('认证类型', max_length=50, default='token')
    auth_config = models.JSONField('认证配置', default=dict)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='inactive')
    
    # 数据库中存在但模型中缺失的字段
    timeout = models.IntegerField('超时时间(秒)', default=30)
    retry_count = models.IntegerField('重试次数', default=3)
    rate_limit = models.IntegerField('限流(请求/分钟)', default=100)
    sync_enabled = models.BooleanField('启用同步', default=False)
    sync_interval = models.IntegerField('同步间隔(分钟)', default=60)
    last_sync_time = models.DateTimeField('最后同步时间', null=True, blank=True)
    monitoring_enabled = models.BooleanField('启用监控', default=True)
    health_check_url = models.URLField('健康检查URL', max_length=200, blank=True)
    alert_email = models.EmailField('告警邮箱', max_length=254, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '集成系统'
        verbose_name_plural = '集成系统'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class APIGateway(models.Model):
    """API网关模型"""
    id = models.BigAutoField(primary_key=True)
    name = models.CharField('网关名称', max_length=100)
    base_url = models.URLField('网关地址')
    description = models.TextField('描述', blank=True)
    rate_limit_enabled = models.BooleanField('启用限流', default=True)
    rate_limit_per_minute = models.IntegerField('每分钟请求限制', default=1000)
    rate_limit_per_hour = models.IntegerField('每小时请求限制', default=10000)
    monitoring_enabled = models.BooleanField('启用监控', default=True)
    log_level = models.CharField('日志级别', max_length=20, choices=[
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error')
    ], default='info')
    cors_enabled = models.BooleanField('启用CORS', default=True)
    cors_origins = models.JSONField('CORS源', default=list, blank=True)
    api_key_required = models.BooleanField('需要API Key', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = 'API网关'
        verbose_name_plural = 'API网关'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class IntegrationGateway(models.Model):
    """集成网关模型"""
    GATEWAY_TYPE_CHOICES = [
        ('api_gateway', 'API网关'),
        ('message_queue', '消息队列'),
        ('webhook', 'Webhook'),
        ('file_sync', '文件同步'),
        ('database_sync', '数据库同步'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('网关名称', max_length=100)
    gateway_type = models.CharField('网关类型', max_length=20, choices=GATEWAY_TYPE_CHOICES)
    description = models.TextField('描述', blank=True)
    endpoint = models.URLField('端点', max_length=500)
    configuration = models.JSONField('配置', default=dict)
    is_active = models.BooleanField('是否激活', default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '集成网关'
        verbose_name_plural = '集成网关'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class SyncRule(models.Model):
    """同步规则模型"""
    SYNC_TYPE_CHOICES = [
        ('real_time', '实时同步'),
        ('scheduled', '定时同步'),
        ('manual', '手动同步'),
        ('event_driven', '事件驱动'),
    ]

    SYNC_DIRECTION_CHOICES = [
        ('import', '导入'),
        ('export', '导出'),
        ('bidirectional', '双向'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('规则名称', max_length=100)
    source_system = models.ForeignKey(IntegrationSystem, on_delete=models.CASCADE, verbose_name='源系统', related_name='source_rules')
    target_system = models.ForeignKey(IntegrationSystem, on_delete=models.CASCADE, verbose_name='目标系统', related_name='target_rules')
    sync_type = models.CharField('同步类型', max_length=20, choices=SYNC_TYPE_CHOICES)
    sync_direction = models.CharField('同步方向', max_length=20, choices=SYNC_DIRECTION_CHOICES)
    sync_frequency = models.CharField('同步频率', max_length=50, default='daily')
    field_mapping = models.JSONField('字段映射', default=dict)
    filter_conditions = models.JSONField('过滤条件', default=dict)
    is_active = models.BooleanField('是否激活', default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '同步规则'
        verbose_name_plural = '同步规则'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class SyncLog(models.Model):
    """同步日志模型"""
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
        ('partial', '部分成功'),
        ('running', '运行中'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sync_rule = models.ForeignKey(SyncRule, on_delete=models.CASCADE, verbose_name='同步规则', related_name='sync_logs')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES)
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    records_processed = models.IntegerField('处理记录数', default=0)
    records_success = models.IntegerField('成功记录数', default=0)
    records_failed = models.IntegerField('失败记录数', default=0)
    error_message = models.TextField('错误信息', blank=True)
    details = models.JSONField('详细信息', default=dict)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '同步日志'
        verbose_name_plural = '同步日志'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sync_rule.name} - {self.status}"


class IntegrationMapping(models.Model):
    """集成映射模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('映射名称', max_length=100)
    source_field = models.CharField('源字段', max_length=100)
    target_field = models.CharField('目标字段', max_length=100)
    field_type = models.CharField('字段类型', max_length=50)
    transformation_rule = models.TextField('转换规则', blank=True)
    is_required = models.BooleanField('是否必需', default=False)
    default_value = models.CharField('默认值', max_length=200, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '集成映射'
        verbose_name_plural = '集成映射'
        ordering = ['name']

    def __str__(self):
        return f"{self.source_field} -> {self.target_field}"


class APIRoute(models.Model):
    """API路由模型"""
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    ]

    id = models.BigAutoField(primary_key=True)
    name = models.CharField('路由名称', max_length=100)
    path = models.CharField('路径', max_length=200)
    method = models.CharField('请求方法', max_length=10, choices=METHOD_CHOICES)
    target_url = models.URLField('目标地址')
    rate_limit = models.IntegerField('限流(请求/分钟)', default=100)
    burst_limit = models.IntegerField('突发限制', default=200)
    cache_enabled = models.BooleanField('启用缓存', default=False)
    cache_ttl = models.IntegerField('缓存TTL(秒)', default=300)
    auth_required = models.BooleanField('需要认证', default=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = 'API路由'
        verbose_name_plural = 'API路由'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.method} {self.path}"


class APIMonitor(models.Model):
    """API监控模型"""
    id = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField('时间戳', auto_now_add=True)
    request_count = models.IntegerField('请求次数', default=0)
    success_count = models.IntegerField('成功次数', default=0)
    error_count = models.IntegerField('错误次数', default=0)
    avg_response_time = models.FloatField('平均响应时间(ms)', default=0)
    max_response_time = models.FloatField('最大响应时间(ms)', default=0)
    min_response_time = models.FloatField('最小响应时间(ms)', default=0)

    class Meta:
        verbose_name = 'API监控'
        verbose_name_plural = 'API监控'
        ordering = ['-timestamp']

    def __str__(self):
        return f"监控数据 - {self.timestamp}"


class DataSyncRule(models.Model):
    """数据同步规则模型"""
    SYNC_TYPE_CHOICES = [
        ('realtime', '实时同步'),
        ('batch', '批量同步'),
        ('scheduled', '定时同步'),
    ]

    id = models.BigAutoField(primary_key=True)
    name = models.CharField('规则名称', max_length=100)
    sync_type = models.CharField('同步类型', max_length=20, choices=SYNC_TYPE_CHOICES)
    source_system = models.CharField('源系统', max_length=100)
    target_system = models.CharField('目标系统', max_length=100)
    sync_frequency = models.CharField('同步频率', max_length=50, default='daily')
    field_mapping = models.JSONField('字段映射', default=dict)
    filter_conditions = models.JSONField('过滤条件', default=dict)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '数据同步规则'
        verbose_name_plural = '数据同步规则'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class IntegrationConfig(models.Model):
    """集成配置模型"""
    id = models.BigAutoField(primary_key=True)
    config_key = models.CharField('配置键', max_length=100)
    config_value = models.TextField('配置值')
    config_type = models.CharField('配置类型', max_length=50, default='string')
    description = models.TextField('描述', blank=True)
    is_encrypted = models.BooleanField('是否加密', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '集成配置'
        verbose_name_plural = '集成配置'
        ordering = ['config_key']

    def __str__(self):
        return self.config_key


class IntegrationTest(models.Model):
    """集成测试模型"""
    STATUS_CHOICES = [
        ('pending', '待测试'),
        ('running', '测试中'),
        ('success', '测试成功'),
        ('failed', '测试失败'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration_system = models.ForeignKey(IntegrationSystem, on_delete=models.CASCADE, verbose_name='集成系统', related_name='tests')
    test_type = models.CharField('测试类型', max_length=50)
    test_config = models.JSONField('测试配置', default=dict)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    test_result = models.JSONField('测试结果', default=dict)
    error_message = models.TextField('错误信息', blank=True)
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '集成测试'
        verbose_name_plural = '集成测试'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.integration_system.name} - {self.test_type}"