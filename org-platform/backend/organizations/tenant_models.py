"""
多租户支持模型
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Tenant(models.Model):
    """租户模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="租户名称")
    code = models.CharField(max_length=50, unique=True, verbose_name="租户代码")
    domain = models.CharField(max_length=100, unique=True, verbose_name="域名")
    description = models.TextField(blank=True, verbose_name="描述")
    
    # 租户状态
    STATUS_CHOICES = [
        ('active', '激活'),
        ('suspended', '暂停'),
        ('inactive', '未激活'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive', verbose_name="状态")
    
    # 租户配置
    max_users = models.IntegerField(default=100, verbose_name="最大用户数")
    max_departments = models.IntegerField(default=50, verbose_name="最大部门数")
    max_employees = models.IntegerField(default=1000, verbose_name="最大员工数")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="过期时间")
    
    # 联系信息
    contact_name = models.CharField(max_length=100, verbose_name="联系人")
    contact_email = models.EmailField(verbose_name="联系邮箱")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="联系电话")
    
    class Meta:
        db_table = 'tenants'
        verbose_name = "租户"
        verbose_name_plural = "租户"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def is_active(self):
        """检查租户是否激活"""
        return self.status == 'active'
    
    @property
    def is_expired(self):
        """检查租户是否过期"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class TenantUser(models.Model):
    """租户用户关联"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name="租户")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    
    # 用户角色
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('manager', '管理者'),
        ('user', '普通用户'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name="角色")
    
    # 权限设置
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    can_manage_users = models.BooleanField(default=False, verbose_name="可管理用户")
    can_manage_departments = models.BooleanField(default=False, verbose_name="可管理部门")
    can_manage_employees = models.BooleanField(default=False, verbose_name="可管理员工")
    can_view_reports = models.BooleanField(default=False, verbose_name="可查看报表")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'tenant_users'
        verbose_name = "租户用户"
        verbose_name_plural = "租户用户"
        unique_together = ['tenant', 'user']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.user.username}"


class TenantSettings(models.Model):
    """租户设置"""
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, verbose_name="租户")
    
    # 系统设置
    timezone = models.CharField(max_length=50, default='Asia/Shanghai', verbose_name="时区")
    language = models.CharField(max_length=10, default='zh-cn', verbose_name="语言")
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD', verbose_name="日期格式")
    
    # 组织设置
    company_name = models.CharField(max_length=100, verbose_name="公司名称")
    company_logo = models.URLField(blank=True, verbose_name="公司Logo")
    company_address = models.TextField(blank=True, verbose_name="公司地址")
    
    # 功能设置
    enable_employee_self_service = models.BooleanField(default=True, verbose_name="启用员工自助服务")
    enable_workflow_approval = models.BooleanField(default=True, verbose_name="启用工作流审批")
    enable_integration_api = models.BooleanField(default=True, verbose_name="启用集成API")
    
    # 安全设置
    password_policy = models.JSONField(default=dict, verbose_name="密码策略")
    session_timeout = models.IntegerField(default=30, verbose_name="会话超时(分钟)")
    enable_two_factor = models.BooleanField(default=False, verbose_name="启用双因子认证")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'tenant_settings'
        verbose_name = "租户设置"
        verbose_name_plural = "租户设置"
    
    def __str__(self):
        return f"{self.tenant.name} 设置"


class TenantSubscription(models.Model):
    """租户订阅"""
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, verbose_name="租户")
    
    # 订阅计划
    PLAN_CHOICES = [
        ('basic', '基础版'),
        ('professional', '专业版'),
        ('enterprise', '企业版'),
    ]
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic', verbose_name="订阅计划")
    
    # 订阅状态
    STATUS_CHOICES = [
        ('active', '激活'),
        ('expired', '过期'),
        ('cancelled', '已取消'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="状态")
    
    # 订阅时间
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="开始时间")
    end_date = models.DateTimeField(verbose_name="结束时间")
    auto_renew = models.BooleanField(default=True, verbose_name="自动续费")
    
    # 功能限制
    max_users = models.IntegerField(default=100, verbose_name="最大用户数")
    max_departments = models.IntegerField(default=50, verbose_name="最大部门数")
    max_employees = models.IntegerField(default=1000, verbose_name="最大员工数")
    max_api_calls = models.IntegerField(default=10000, verbose_name="最大API调用数")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'tenant_subscriptions'
        verbose_name = "租户订阅"
        verbose_name_plural = "租户订阅"
    
    def __str__(self):
        return f"{self.tenant.name} - {self.get_plan_display()}"
    
    @property
    def is_active(self):
        """检查订阅是否激活"""
        return self.status == 'active' and timezone.now() < self.end_date
