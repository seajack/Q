from django.db import models
from django.contrib.auth.models import User
import json


class IntegrationSystem(models.Model):
    """集成系统模型"""
    SYSTEM_TYPE_CHOICES = [
        ('performance', '绩效考核系统'),
        ('oa', 'OA系统'),
        ('finance', '财务系统'),
        ('crm', 'CRM系统'),
        ('erp', 'ERP系统'),
        ('hr', '人力资源系统'),
        ('custom', '自定义系统'),
    ]
    
    STATUS_CHOICES = [
        ('active', '启用'),
        ('inactive', '禁用'),
        ('error', '错误'),
        ('testing', '测试中'),
    ]
    
    name = models.CharField('系统名称', max_length=100)
    system_type = models.CharField('系统类型', max_length=20, choices=SYSTEM_TYPE_CHOICES)
    base_url = models.URLField('系统地址')
    api_version = models.CharField('API版本', max_length=20, default='v1')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='inactive')
    
    # 认证配置
    auth_type = models.CharField('认证类型', max_length=20, choices=[
        ('none', '无认证'),
        ('basic', '基础认证'),
        ('token', 'Token认证'),
        ('oauth2', 'OAuth2'),
        ('api_key', 'API Key'),
    ], default='none')
    auth_config = models.JSONField('认证配置', default=dict, blank=True)
    
    # 连接配置
    timeout = models.IntegerField('超时时间(秒)', default=30)
    retry_count = models.IntegerField('重试次数', default=3)
    rate_limit = models.IntegerField('限流(请求/分钟)', default=100)
    
    # 同步配置
    sync_enabled = models.BooleanField('启用同步', default=False)
    sync_interval = models.IntegerField('同步间隔(分钟)', default=60)
    last_sync_time = models.DateTimeField('最后同步时间', null=True, blank=True)
    
    # 监控配置
    monitoring_enabled = models.BooleanField('启用监控', default=True)
    health_check_url = models.URLField('健康检查地址', blank=True)
    alert_email = models.EmailField('告警邮箱', blank=True)
    
    description = models.TextField('描述', blank=True)
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.CASCADE)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '集成系统'
        verbose_name_plural = '集成系统'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_system_type_display()})"


class APIGateway(models.Model):
    """API网关配置"""
    name = models.CharField('网关名称', max_length=100)
    base_url = models.URLField('网关地址')
    description = models.TextField('描述', blank=True)
    
    # 限流配置
    rate_limit_enabled = models.BooleanField('启用限流', default=True)
    rate_limit_per_minute = models.IntegerField('每分钟请求限制', default=1000)
    rate_limit_per_hour = models.IntegerField('每小时请求限制', default=10000)
    
    # 监控配置
    monitoring_enabled = models.BooleanField('启用监控', default=True)
    log_level = models.CharField('日志级别', max_length=20, choices=[
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ], default='info')
    
    # 安全配置
    cors_enabled = models.BooleanField('启用CORS', default=True)
    cors_origins = models.JSONField('CORS源', default=list, blank=True)
    api_key_required = models.BooleanField('需要API Key', default=False)
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = 'API网关'
        verbose_name_plural = 'API网关'
    
    def __str__(self):
        return self.name


class APIRoute(models.Model):
    """API路由配置"""
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    ]
    
    gateway = models.ForeignKey(APIGateway, verbose_name='API网关', on_delete=models.CASCADE, related_name='routes')
    name = models.CharField('路由名称', max_length=100)
    path = models.CharField('路径', max_length=200)
    method = models.CharField('请求方法', max_length=10, choices=METHOD_CHOICES)
    target_url = models.URLField('目标地址')
    
    # 限流配置
    rate_limit = models.IntegerField('限流(请求/分钟)', default=100)
    burst_limit = models.IntegerField('突发限制', default=200)
    
    # 缓存配置
    cache_enabled = models.BooleanField('启用缓存', default=False)
    cache_ttl = models.IntegerField('缓存时间(秒)', default=300)
    
    # 认证配置
    auth_required = models.BooleanField('需要认证', default=True)
    roles_required = models.JSONField('所需角色', default=list, blank=True)
    
    # 转换配置
    request_transform = models.JSONField('请求转换', default=dict, blank=True)
    response_transform = models.JSONField('响应转换', default=dict, blank=True)
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = 'API路由'
        verbose_name_plural = 'API路由'
        unique_together = ['gateway', 'path', 'method']
    
    def __str__(self):
        return f"{self.method} {self.path} -> {self.target_url}"


class DataSyncRule(models.Model):
    """数据同步规则"""
    SYNC_TYPE_CHOICES = [
        ('realtime', '实时同步'),
        ('batch', '批量同步'),
        ('scheduled', '定时同步'),
    ]
    
    STATUS_CHOICES = [
        ('active', '启用'),
        ('inactive', '禁用'),
        ('error', '错误'),
        ('running', '运行中'),
    ]
    
    name = models.CharField('规则名称', max_length=100)
    source_system = models.ForeignKey(IntegrationSystem, verbose_name='源系统', on_delete=models.CASCADE, related_name='source_sync_rules')
    target_system = models.ForeignKey(IntegrationSystem, verbose_name='目标系统', on_delete=models.CASCADE, related_name='target_sync_rules')
    
    sync_type = models.CharField('同步类型', max_length=20, choices=SYNC_TYPE_CHOICES)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='inactive')
    
    # 数据配置
    source_table = models.CharField('源表名', max_length=100)
    target_table = models.CharField('目标表名', max_length=100)
    field_mapping = models.JSONField('字段映射', default=dict)
    
    # 过滤条件
    filter_conditions = models.JSONField('过滤条件', default=dict, blank=True)
    
    # 同步配置
    batch_size = models.IntegerField('批次大小', default=1000)
    sync_interval = models.IntegerField('同步间隔(分钟)', default=60)
    max_retry_count = models.IntegerField('最大重试次数', default=3)
    
    # 数据清洗
    data_cleaning_enabled = models.BooleanField('启用数据清洗', default=True)
    cleaning_rules = models.JSONField('清洗规则', default=list, blank=True)
    
    # 数据校验
    validation_enabled = models.BooleanField('启用数据校验', default=True)
    validation_rules = models.JSONField('校验规则', default=list, blank=True)
    
    # 监控配置
    monitoring_enabled = models.BooleanField('启用监控', default=True)
    alert_on_error = models.BooleanField('错误告警', default=True)
    alert_on_delay = models.BooleanField('延迟告警', default=True)
    delay_threshold = models.IntegerField('延迟阈值(分钟)', default=30)
    
    description = models.TextField('描述', blank=True)
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.CASCADE)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '数据同步规则'
        verbose_name_plural = '数据同步规则'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.source_system.name} -> {self.target_system.name})"


class SyncLog(models.Model):
    """同步日志"""
    STATUS_CHOICES = [
        ('success', '成功'),
        ('error', '错误'),
        ('warning', '警告'),
        ('running', '运行中'),
    ]
    
    sync_rule = models.ForeignKey(DataSyncRule, verbose_name='同步规则', on_delete=models.CASCADE, related_name='logs')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES)
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    
    # 统计信息
    total_records = models.IntegerField('总记录数', default=0)
    success_records = models.IntegerField('成功记录数', default=0)
    error_records = models.IntegerField('错误记录数', default=0)
    skipped_records = models.IntegerField('跳过记录数', default=0)
    
    # 错误信息
    error_message = models.TextField('错误信息', blank=True)
    error_details = models.JSONField('错误详情', default=dict, blank=True)
    
    # 性能信息
    duration_seconds = models.FloatField('耗时(秒)', null=True, blank=True)
    records_per_second = models.FloatField('每秒记录数', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '同步日志'
        verbose_name_plural = '同步日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sync_rule.name} - {self.get_status_display()} ({self.start_time})"


class APIMonitor(models.Model):
    """API监控"""
    route = models.ForeignKey(APIRoute, verbose_name='API路由', on_delete=models.CASCADE, related_name='monitors')
    timestamp = models.DateTimeField('时间戳', auto_now_add=True)
    
    # 请求统计
    request_count = models.IntegerField('请求次数', default=0)
    success_count = models.IntegerField('成功次数', default=0)
    error_count = models.IntegerField('错误次数', default=0)
    
    # 响应时间
    avg_response_time = models.FloatField('平均响应时间(ms)', default=0)
    max_response_time = models.FloatField('最大响应时间(ms)', default=0)
    min_response_time = models.FloatField('最小响应时间(ms)', default=0)
    
    # 错误统计
    error_rate = models.FloatField('错误率(%)', default=0)
    status_code_distribution = models.JSONField('状态码分布', default=dict)
    
    class Meta:
        verbose_name = 'API监控'
        verbose_name_plural = 'API监控'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.route.name} - {self.timestamp}"


class IntegrationConfig(models.Model):
    """集成配置"""
    system = models.ForeignKey(IntegrationSystem, verbose_name='集成系统', on_delete=models.CASCADE, related_name='configs')
    config_key = models.CharField('配置键', max_length=100)
    config_value = models.TextField('配置值')
    config_type = models.CharField('配置类型', max_length=20, choices=[
        ('string', '字符串'),
        ('integer', '整数'),
        ('boolean', '布尔值'),
        ('json', 'JSON对象'),
        ('url', 'URL'),
        ('email', '邮箱'),
    ], default='string')
    is_encrypted = models.BooleanField('是否加密', default=False)
    description = models.TextField('描述', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '集成配置'
        verbose_name_plural = '集成配置'
        unique_together = ['system', 'config_key']
    
    def __str__(self):
        return f"{self.system.name} - {self.config_key}"
