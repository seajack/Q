# 安全配置管理
"""
统一管理安全相关配置
包括密码策略、会话管理、访问控制等
"""

import os
import logging
from typing import Dict, Any, List, Optional
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import re

logger = logging.getLogger(__name__)

class SecurityConfig:
    """安全配置类"""
    
    # 默认安全配置
    DEFAULT_CONFIG = {
        # 密码策略
        'password_policy': {
            'min_length': 8,
            'max_length': 128,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_symbols': True,
            'forbidden_patterns': [
                r'password',
                r'123456',
                r'admin',
                r'user',
            ],
            'history_count': 5,  # 不能重复使用最近5个密码
            'expiry_days': 90,   # 密码90天过期
        },
        
        # 会话管理
        'session_policy': {
            'timeout_minutes': 30,  # 30分钟无操作自动登出
            'max_concurrent_sessions': 3,  # 最多3个并发会话
            'require_mfa': False,  # 是否要求MFA
            'remember_me_days': 7,  # 记住我功能有效期
        },
        
        # 访问控制
        'access_control': {
            'max_login_attempts': 5,  # 最大登录尝试次数
            'lockout_duration_minutes': 15,  # 账户锁定时间
            'ip_whitelist': [],  # IP白名单
            'ip_blacklist': [],  # IP黑名单
            'allowed_user_agents': [],  # 允许的用户代理
            'blocked_user_agents': [],  # 阻止的用户代理
        },
        
        # 数据保护
        'data_protection': {
            'encrypt_sensitive_fields': True,  # 加密敏感字段
            'audit_sensitive_operations': True,  # 审计敏感操作
            'data_retention_days': 365,  # 数据保留天数
            'backup_frequency_days': 7,  # 备份频率
        },
        
        # 安全监控
        'security_monitoring': {
            'enable_real_time_monitoring': True,  # 启用实时监控
            'alert_threshold': 10,  # 告警阈值
            'notification_channels': ['email', 'sms'],  # 通知渠道
            'log_retention_days': 90,  # 日志保留天数
        }
    }
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载安全配置"""
        try:
            # 从数据库或配置文件加载
            config = self.DEFAULT_CONFIG.copy()
            
            # 从环境变量覆盖配置
            self._load_from_env(config)
            
            # 从数据库加载用户自定义配置
            self._load_from_database(config)
            
            return config
            
        except Exception as e:
            logger.error(f"加载安全配置失败: {e}")
            return self.DEFAULT_CONFIG
    
    def _load_from_env(self, config: Dict[str, Any]):
        """从环境变量加载配置"""
        env_mappings = {
            'PASSWORD_MIN_LENGTH': ('password_policy', 'min_length', int),
            'PASSWORD_EXPIRY_DAYS': ('password_policy', 'expiry_days', int),
            'SESSION_TIMEOUT_MINUTES': ('session_policy', 'timeout_minutes', int),
            'MAX_LOGIN_ATTEMPTS': ('access_control', 'max_login_attempts', int),
            'LOCKOUT_DURATION_MINUTES': ('access_control', 'lockout_duration_minutes', int),
        }
        
        for env_var, (section, key, type_func) in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                try:
                    config[section][key] = type_func(value)
                except (ValueError, TypeError) as e:
                    logger.warning(f"环境变量 {env_var} 值无效: {e}")
    
    def _load_from_database(self, config: Dict[str, Any]):
        """从数据库加载配置"""
        try:
            # 这里可以从数据库加载用户自定义的安全配置
            # 例如从SystemConfig模型加载
            pass
        except Exception as e:
            logger.error(f"从数据库加载配置失败: {e}")
    
    def get_config(self, section: str = None, key: str = None) -> Any:
        """获取配置值"""
        try:
            if section is None:
                return self.config
            
            if key is None:
                return self.config.get(section, {})
            
            return self.config.get(section, {}).get(key)
            
        except Exception as e:
            logger.error(f"获取配置失败: {e}")
            return None
    
    def update_config(self, section: str, key: str, value: Any) -> bool:
        """更新配置"""
        try:
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section][key] = value
            
            # 保存到数据库
            self._save_to_database(section, key, value)
            
            # 清除缓存
            cache.delete('security_config')
            
            logger.info(f"安全配置已更新: {section}.{key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            return False
    
    def _save_to_database(self, section: str, key: str, value: Any):
        """保存配置到数据库"""
        try:
            # 这里可以保存到SystemConfig模型
            pass
        except Exception as e:
            logger.error(f"保存配置到数据库失败: {e}")


class PasswordPolicy:
    """密码策略验证器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.password_config = config.get_config('password_policy')
    
    def validate_password(self, password: str, user=None) -> List[str]:
        """验证密码是否符合策略"""
        errors = []
        
        try:
            # 基本长度检查
            min_length = self.password_config.get('min_length', 8)
            max_length = self.password_config.get('max_length', 128)
            
            if len(password) < min_length:
                errors.append(f"密码长度不能少于{min_length}个字符")
            
            if len(password) > max_length:
                errors.append(f"密码长度不能超过{max_length}个字符")
            
            # 字符类型检查
            if self.password_config.get('require_uppercase', True):
                if not re.search(r'[A-Z]', password):
                    errors.append("密码必须包含大写字母")
            
            if self.password_config.get('require_lowercase', True):
                if not re.search(r'[a-z]', password):
                    errors.append("密码必须包含小写字母")
            
            if self.password_config.get('require_numbers', True):
                if not re.search(r'\d', password):
                    errors.append("密码必须包含数字")
            
            if self.password_config.get('require_symbols', True):
                if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                    errors.append("密码必须包含特殊字符")
            
            # 禁止模式检查
            forbidden_patterns = self.password_config.get('forbidden_patterns', [])
            for pattern in forbidden_patterns:
                if re.search(pattern, password, re.IGNORECASE):
                    errors.append(f"密码不能包含'{pattern}'")
            
            # 历史密码检查
            if user:
                history_errors = self._check_password_history(password, user)
                errors.extend(history_errors)
            
            return errors
            
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return [f"密码验证失败: {e}"]
    
    def _check_password_history(self, password: str, user) -> List[str]:
        """检查密码历史"""
        try:
            history_count = self.password_config.get('history_count', 5)
            
            # 这里需要实现密码历史检查逻辑
            # 可以从数据库查询用户的历史密码哈希值进行比较
            
            return []
            
        except Exception as e:
            logger.error(f"密码历史检查失败: {e}")
            return [f"密码历史检查失败: {e}"]


class SessionManager:
    """会话管理器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.session_config = config.get_config('session_policy')
    
    def check_session_validity(self, request) -> bool:
        """检查会话有效性"""
        try:
            if not request.user.is_authenticated:
                return False
            
            # 检查会话超时
            if self._is_session_expired(request):
                return False
            
            # 检查并发会话数
            if self._exceeds_max_sessions(request):
                return False
            
            # 检查MFA要求
            if self._requires_mfa(request):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"会话有效性检查失败: {e}")
            return False
    
    def _is_session_expired(self, request) -> bool:
        """检查会话是否过期"""
        try:
            timeout_minutes = self.session_config.get('timeout_minutes', 30)
            last_activity = request.session.get('last_activity')
            
            if not last_activity:
                return True
            
            last_activity_time = timezone.datetime.fromisoformat(last_activity)
            timeout_threshold = timezone.now() - timedelta(minutes=timeout_minutes)
            
            return last_activity_time < timeout_threshold
            
        except Exception as e:
            logger.error(f"会话过期检查失败: {e}")
            return True
    
    def _exceeds_max_sessions(self, request) -> bool:
        """检查是否超过最大会话数"""
        try:
            max_sessions = self.session_config.get('max_concurrent_sessions', 3)
            
            # 这里需要实现并发会话数检查
            # 可以从数据库或缓存中查询用户的活跃会话数
            
            return False
            
        except Exception as e:
            logger.error(f"并发会话检查失败: {e}")
            return False
    
    def _requires_mfa(self, request) -> bool:
        """检查是否需要MFA"""
        try:
            require_mfa = self.session_config.get('require_mfa', False)
            
            if not require_mfa:
                return False
            
            # 检查MFA是否已验证
            return not request.session.get('mfa_verified', False)
            
        except Exception as e:
            logger.error(f"MFA检查失败: {e}")
            return True


class AccessController:
    """访问控制器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.access_config = config.get_config('access_control')
    
    def check_access_permission(self, request) -> bool:
        """检查访问权限"""
        try:
            # 检查IP白名单/黑名单
            if not self._check_ip_access(request):
                return False
            
            # 检查用户代理
            if not self._check_user_agent(request):
                return False
            
            # 检查登录尝试次数
            if not self._check_login_attempts(request):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"访问权限检查失败: {e}")
            return False
    
    def _check_ip_access(self, request) -> bool:
        """检查IP访问权限"""
        try:
            client_ip = self._get_client_ip(request)
            
            # 检查IP黑名单
            blacklist = self.access_config.get('ip_blacklist', [])
            if client_ip in blacklist:
                return False
            
            # 检查IP白名单
            whitelist = self.access_config.get('ip_whitelist', [])
            if whitelist and client_ip not in whitelist:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"IP访问检查失败: {e}")
            return False
    
    def _check_user_agent(self, request) -> bool:
        """检查用户代理"""
        try:
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # 检查被阻止的用户代理
            blocked_agents = self.access_config.get('blocked_user_agents', [])
            for blocked_agent in blocked_agents:
                if blocked_agent in user_agent:
                    return False
            
            # 检查允许的用户代理
            allowed_agents = self.access_config.get('allowed_user_agents', [])
            if allowed_agents:
                for allowed_agent in allowed_agents:
                    if allowed_agent in user_agent:
                        return True
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"用户代理检查失败: {e}")
            return False
    
    def _check_login_attempts(self, request) -> bool:
        """检查登录尝试次数"""
        try:
            client_ip = self._get_client_ip(request)
            max_attempts = self.access_config.get('max_login_attempts', 5)
            
            # 从缓存获取登录尝试次数
            cache_key = f"login_attempts_{client_ip}"
            attempts = cache.get(cache_key, 0)
            
            if attempts >= max_attempts:
                # 检查锁定时间
                lockout_duration = self.access_config.get('lockout_duration_minutes', 15)
                lockout_key = f"login_lockout_{client_ip}"
                lockout_time = cache.get(lockout_key)
                
                if lockout_time:
                    # 检查是否还在锁定期内
                    if timezone.now() < lockout_time:
                        return False
                    else:
                        # 锁定期已过，清除锁定
                        cache.delete(lockout_key)
                        cache.delete(cache_key)
                else:
                    # 设置锁定
                    cache.set(lockout_key, timezone.now() + timedelta(minutes=lockout_duration))
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"登录尝试检查失败: {e}")
            return False
    
    def _get_client_ip(self, request) -> str:
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def record_login_attempt(self, request, success: bool):
        """记录登录尝试"""
        try:
            client_ip = self._get_client_ip(request)
            
            if success:
                # 登录成功，清除尝试次数
                cache.delete(f"login_attempts_{client_ip}")
                cache.delete(f"login_lockout_{client_ip}")
            else:
                # 登录失败，增加尝试次数
                cache_key = f"login_attempts_{client_ip}"
                attempts = cache.get(cache_key, 0) + 1
                cache.set(cache_key, attempts, timeout=3600)  # 1小时过期
                
        except Exception as e:
            logger.error(f"记录登录尝试失败: {e}")


# 全局安全配置实例
security_config = SecurityConfig()
password_policy = PasswordPolicy(security_config)
session_manager = SessionManager(security_config)
access_controller = AccessController(security_config)
