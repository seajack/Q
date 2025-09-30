# 安全审计日志系统
"""
实现完整的安全审计日志功能
记录用户操作、系统事件、安全事件等
"""

import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone as django_timezone
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class AuditLog(models.Model):
    """审计日志模型"""
    
    # 日志级别
    LEVEL_CHOICES = [
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('critical', '严重'),
    ]
    
    # 事件类型
    EVENT_TYPE_CHOICES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('view', '查看'),
        ('export', '导出'),
        ('import', '导入'),
        ('permission', '权限变更'),
        ('security', '安全事件'),
        ('system', '系统事件'),
    ]
    
    # 操作结果
    RESULT_CHOICES = [
        ('success', '成功'),
        ('failure', '失败'),
        ('pending', '待处理'),
    ]
    
    # 基本信息
    timestamp = models.DateTimeField('时间戳', auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='用户')
    session_id = models.CharField('会话ID', max_length=100, blank=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('用户代理', blank=True)
    
    # 事件信息
    event_type = models.CharField('事件类型', max_length=20, choices=EVENT_TYPE_CHOICES)
    event_name = models.CharField('事件名称', max_length=200)
    event_description = models.TextField('事件描述', blank=True)
    
    # 操作信息
    resource_type = models.CharField('资源类型', max_length=50, blank=True)
    resource_id = models.CharField('资源ID', max_length=50, blank=True)
    resource_name = models.CharField('资源名称', max_length=200, blank=True)
    
    # 结果信息
    result = models.CharField('操作结果', max_length=10, choices=RESULT_CHOICES)
    level = models.CharField('日志级别', max_length=10, choices=LEVEL_CHOICES, default='info')
    
    # 详细信息
    details = models.JSONField('详细信息', default=dict, blank=True)
    error_message = models.TextField('错误信息', blank=True)
    
    # 安全信息
    risk_level = models.CharField('风险级别', max_length=10, choices=[
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('critical', '严重'),
    ], default='low')
    
    # 元数据
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['event_type']),
            models.Index(fields=['result']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.timestamp} - {self.event_name} - {self.user}"
    
    def get_hash(self) -> str:
        """获取日志哈希值"""
        content = f"{self.timestamp}{self.user}{self.event_type}{self.event_name}{self.result}"
        return hashlib.sha256(content.encode()).hexdigest()


class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self):
        self.logger = logging.getLogger('audit')
    
    def log_event(self, 
                  event_type: str,
                  event_name: str,
                  user: Optional[User] = None,
                  request=None,
                  resource_type: str = '',
                  resource_id: str = '',
                  resource_name: str = '',
                  result: str = 'success',
                  level: str = 'info',
                  details: Dict[str, Any] = None,
                  error_message: str = '',
                  risk_level: str = 'low') -> AuditLog:
        """记录审计事件"""
        
        try:
            # 获取请求信息
            ip_address = None
            user_agent = ''
            session_id = ''
            
            if request:
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                session_id = request.session.session_key or ''
            
            # 创建审计日志
            audit_log = AuditLog.objects.create(
                user=user,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                event_type=event_type,
                event_name=event_name,
                event_description=self._generate_description(event_type, event_name, details),
                resource_type=resource_type,
                resource_id=resource_id,
                resource_name=resource_name,
                result=result,
                level=level,
                details=details or {},
                error_message=error_message,
                risk_level=risk_level
            )
            
            # 记录到日志文件
            self._log_to_file(audit_log)
            
            # 检查安全风险
            self._check_security_risks(audit_log)
            
            return audit_log
            
        except Exception as e:
            logger.error(f"记录审计日志失败: {e}")
            return None
    
    def _get_client_ip(self, request) -> str:
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _generate_description(self, event_type: str, event_name: str, details: Dict[str, Any]) -> str:
        """生成事件描述"""
        descriptions = {
            'login': f"用户登录系统",
            'logout': f"用户退出系统",
            'create': f"创建{event_name}",
            'update': f"更新{event_name}",
            'delete': f"删除{event_name}",
            'view': f"查看{event_name}",
            'export': f"导出{event_name}",
            'import': f"导入{event_name}",
            'permission': f"权限变更: {event_name}",
            'security': f"安全事件: {event_name}",
            'system': f"系统事件: {event_name}",
        }
        
        base_description = descriptions.get(event_type, event_name)
        
        if details:
            detail_str = ', '.join([f"{k}: {v}" for k, v in details.items()])
            return f"{base_description} - {detail_str}"
        
        return base_description
    
    def _log_to_file(self, audit_log: AuditLog):
        """记录到日志文件"""
        try:
            log_data = {
                'timestamp': audit_log.timestamp.isoformat(),
                'user': audit_log.user.username if audit_log.user else 'Anonymous',
                'event_type': audit_log.event_type,
                'event_name': audit_log.event_name,
                'result': audit_log.result,
                'ip_address': str(audit_log.ip_address),
                'resource_type': audit_log.resource_type,
                'resource_id': audit_log.resource_id,
                'details': audit_log.details,
            }
            
            self.logger.info(json.dumps(log_data, ensure_ascii=False))
            
        except Exception as e:
            logger.error(f"记录到日志文件失败: {e}")
    
    def _check_security_risks(self, audit_log: AuditLog):
        """检查安全风险"""
        try:
            # 检查异常登录
            if audit_log.event_type == 'login' and audit_log.result == 'success':
                self._check_abnormal_login(audit_log)
            
            # 检查频繁操作
            if audit_log.event_type in ['create', 'update', 'delete']:
                self._check_frequent_operations(audit_log)
            
            # 检查权限变更
            if audit_log.event_type == 'permission':
                self._check_permission_changes(audit_log)
            
            # 检查敏感操作
            if audit_log.resource_type in ['user', 'permission', 'system']:
                self._check_sensitive_operations(audit_log)
                
        except Exception as e:
            logger.error(f"安全检查失败: {e}")
    
    def _check_abnormal_login(self, audit_log: AuditLog):
        """检查异常登录"""
        try:
            # 检查同一IP的登录频率
            recent_logins = AuditLog.objects.filter(
                ip_address=audit_log.ip_address,
                event_type='login',
                timestamp__gte=django_timezone.now() - django_timezone.timedelta(hours=1)
            ).count()
            
            if recent_logins > 10:  # 1小时内超过10次登录
                self._create_security_alert(
                    'abnormal_login_frequency',
                    f"IP {audit_log.ip_address} 在1小时内登录{recent_logins}次",
                    audit_log
                )
            
            # 检查异常时间登录
            hour = audit_log.timestamp.hour
            if hour < 6 or hour > 22:  # 非工作时间登录
                self._create_security_alert(
                    'abnormal_login_time',
                    f"用户在非工作时间 {audit_log.timestamp} 登录",
                    audit_log
                )
                
        except Exception as e:
            logger.error(f"异常登录检查失败: {e}")
    
    def _check_frequent_operations(self, audit_log: AuditLog):
        """检查频繁操作"""
        try:
            # 检查同一用户的操作频率
            recent_operations = AuditLog.objects.filter(
                user=audit_log.user,
                event_type__in=['create', 'update', 'delete'],
                timestamp__gte=django_timezone.now() - django_timezone.timedelta(minutes=5)
            ).count()
            
            if recent_operations > 20:  # 5分钟内超过20次操作
                self._create_security_alert(
                    'frequent_operations',
                    f"用户 {audit_log.user} 在5分钟内执行{recent_operations}次操作",
                    audit_log
                )
                
        except Exception as e:
            logger.error(f"频繁操作检查失败: {e}")
    
    def _check_permission_changes(self, audit_log: AuditLog):
        """检查权限变更"""
        try:
            # 权限变更总是高风险
            self._create_security_alert(
                'permission_change',
                f"用户 {audit_log.user} 执行权限变更操作",
                audit_log
            )
            
        except Exception as e:
            logger.error(f"权限变更检查失败: {e}")
    
    def _check_sensitive_operations(self, audit_log: AuditLog):
        """检查敏感操作"""
        try:
            # 敏感操作需要特别关注
            self._create_security_alert(
                'sensitive_operation',
                f"用户 {audit_log.user} 执行敏感操作: {audit_log.event_name}",
                audit_log
            )
            
        except Exception as e:
            logger.error(f"敏感操作检查失败: {e}")
    
    def _create_security_alert(self, alert_type: str, message: str, audit_log: AuditLog):
        """创建安全告警"""
        try:
            # 记录安全告警
            self.log_event(
                event_type='security',
                event_name=f'安全告警: {alert_type}',
                user=audit_log.user,
                result='success',
                level='warning',
                details={'alert_type': alert_type, 'message': message},
                risk_level='high'
            )
            
            # 可以在这里添加邮件通知、短信通知等
            logger.warning(f"安全告警: {message}")
            
        except Exception as e:
            logger.error(f"创建安全告警失败: {e}")


class AuditLogMiddleware:
    """审计日志中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.audit_logger = AuditLogger()
    
    def __call__(self, request):
        # 记录请求开始时间
        request.start_time = django_timezone.now()
        
        response = self.get_response(request)
        
        # 记录请求结束时间
        request.end_time = django_timezone.now()
        
        # 记录API请求
        if request.path.startswith('/api/'):
            self._log_api_request(request, response)
        
        return response
    
    def _log_api_request(self, request, response):
        """记录API请求"""
        try:
            # 确定事件类型
            event_type = self._get_event_type(request.method, request.path)
            
            # 确定操作结果
            result = 'success' if 200 <= response.status_code < 400 else 'failure'
            
            # 记录审计日志
            self.audit_logger.log_event(
                event_type=event_type,
                event_name=f"{request.method} {request.path}",
                user=request.user if request.user.is_authenticated else None,
                request=request,
                resource_type='api',
                resource_id=request.path,
                result=result,
                level='info' if result == 'success' else 'warning',
                details={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration': (request.end_time - request.start_time).total_seconds(),
                }
            )
            
        except Exception as e:
            logger.error(f"记录API请求失败: {e}")
    
    def _get_event_type(self, method: str, path: str) -> str:
        """根据HTTP方法和路径确定事件类型"""
        if method == 'GET':
            return 'view'
        elif method == 'POST':
            return 'create'
        elif method == 'PUT' or method == 'PATCH':
            return 'update'
        elif method == 'DELETE':
            return 'delete'
        else:
            return 'system'


# 全局审计日志记录器实例
audit_logger = AuditLogger()
