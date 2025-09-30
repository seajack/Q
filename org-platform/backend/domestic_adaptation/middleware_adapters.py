# 国产中间件适配器
"""
支持国产中间件的适配器实现
支持：东方通TongWeb、金蝶Apusic、中创InforSuite
"""

import os
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)

class DomesticMiddlewareAdapter:
    """国产中间件适配器"""
    
    SUPPORTED_MIDDLEWARE = {
        'tongweb': {
            'name': '东方通TongWeb',
            'type': 'application_server',
            'config_file': 'tongweb.xml',
            'port': 8080
        },
        'apusic': {
            'name': '金蝶Apusic',
            'type': 'application_server',
            'config_file': 'apusic.xml',
            'port': 8080
        },
        'inforSuite': {
            'name': '中创InforSuite',
            'type': 'application_server',
            'config_file': 'inforSuite.xml',
            'port': 8080
        },
        'tonglink': {
            'name': '东方通TongLINK/Q',
            'type': 'message_middleware',
            'config_file': 'tonglink.xml',
            'port': 61616
        }
    }
    
    @classmethod
    def get_middleware_config(cls, middleware_type: str) -> Dict[str, Any]:
        """获取国产中间件配置"""
        if middleware_type not in cls.SUPPORTED_MIDDLEWARE:
            raise ValueError(f"不支持的中间件类型: {middleware_type}")
        
        middleware_info = cls.SUPPORTED_MIDDLEWARE[middleware_type]
        
        return {
            'name': middleware_info['name'],
            'type': middleware_info['type'],
            'host': os.getenv('DOMESTIC_MIDDLEWARE_HOST', 'localhost'),
            'port': os.getenv('DOMESTIC_MIDDLEWARE_PORT', middleware_info['port']),
            'config_file': middleware_info['config_file'],
            'username': os.getenv('DOMESTIC_MIDDLEWARE_USER', 'admin'),
            'password': os.getenv('DOMESTIC_MIDDLEWARE_PASSWORD', ''),
        }
    
    @classmethod
    def configure_application_server(cls, server_type: str) -> bool:
        """配置应用服务器"""
        try:
            config = cls.get_middleware_config(server_type)
            
            # 生成服务器配置文件
            config_content = cls._generate_server_config(server_type, config)
            
            # 写入配置文件
            config_path = os.path.join(settings.BASE_DIR, 'config', config['config_file'])
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            logger.info(f"{config['name']}配置完成")
            return True
            
        except Exception as e:
            logger.error(f"应用服务器配置失败: {e}")
            return False
    
    @classmethod
    def configure_message_middleware(cls, middleware_type: str) -> bool:
        """配置消息中间件"""
        try:
            config = cls.get_middleware_config(middleware_type)
            
            # 配置消息队列
            message_config = {
                'broker_url': f"amqp://{config['username']}:{config['password']}@{config['host']}:{config['port']}",
                'result_backend': f"redis://{config['host']}:6379/0",
                'task_serializer': 'json',
                'accept_content': ['json'],
                'result_serializer': 'json',
                'timezone': 'Asia/Shanghai',
                'enable_utc': True,
            }
            
            # 更新Django设置
            settings.CELERY_BROKER_URL = message_config['broker_url']
            settings.CELERY_RESULT_BACKEND = message_config['result_backend']
            
            logger.info(f"{config['name']}消息中间件配置完成")
            return True
            
        except Exception as e:
            logger.error(f"消息中间件配置失败: {e}")
            return False
    
    @classmethod
    def _generate_server_config(cls, server_type: str, config: Dict[str, Any]) -> str:
        """生成服务器配置文件"""
        if server_type == 'tongweb':
            return cls._generate_tongweb_config(config)
        elif server_type == 'apusic':
            return cls._generate_apusic_config(config)
        elif server_type == 'inforSuite':
            return cls._generate_inforSuite_config(config)
        else:
            raise ValueError(f"不支持的服务器类型: {server_type}")
    
    @classmethod
    def _generate_tongweb_config(cls, config: Dict[str, Any]) -> str:
        """生成东方通TongWeb配置"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<server>
    <name>{config['name']}</name>
    <host>{config['host']}</host>
    <port>{config['port']}</port>
    <context-path>/org-platform</context-path>
    <session-timeout>30</session-timeout>
    <max-threads>200</max-threads>
    <min-threads>10</min-threads>
    <connection-timeout>30000</connection-timeout>
    <keep-alive-timeout>60000</keep-alive-timeout>
</server>"""
    
    @classmethod
    def _generate_apusic_config(cls, config: Dict[str, Any]) -> str:
        """生成金蝶Apusic配置"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<apusic>
    <server>
        <name>{config['name']}</name>
        <host>{config['host']}</host>
        <port>{config['port']}</port>
        <context-path>/org-platform</context-path>
        <session-timeout>30</session-timeout>
        <thread-pool>
            <max-threads>200</max-threads>
            <min-threads>10</min-threads>
        </thread-pool>
    </server>
</apusic>"""
    
    @classmethod
    def _generate_inforSuite_config(cls, config: Dict[str, Any]) -> str:
        """生成中创InforSuite配置"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<inforSuite>
    <server>
        <name>{config['name']}</name>
        <host>{config['host']}</host>
        <port>{config['port']}</port>
        <context-path>/org-platform</context-path>
        <session-timeout>30</session-timeout>
        <thread-pool>
            <max-threads>200</max-threads>
            <min-threads>10</min-threads>
        </thread-pool>
    </server>
</inforSuite>"""


class DomesticCacheAdapter:
    """国产缓存适配器"""
    
    @classmethod
    def configure_domestic_cache(cls, cache_type: str = 'redis') -> bool:
        """配置国产缓存"""
        try:
            if cache_type == 'redis':
                # 使用国产Redis替代方案
                cache_config = {
                    'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                    'LOCATION': os.getenv('DOMESTIC_CACHE_URL', 'redis://localhost:6379/1'),
                    'OPTIONS': {
                        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                        'CONNECTION_POOL_KWARGS': {
                            'max_connections': 50,
                            'retry_on_timeout': True,
                        }
                    }
                }
            else:
                # 使用内存缓存作为备选
                cache_config = {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                    'LOCATION': 'unique-snowflake',
                }
            
            # 更新Django缓存配置
            settings.CACHES['default'] = cache_config
            
            logger.info(f"国产缓存配置完成: {cache_type}")
            return True
            
        except Exception as e:
            logger.error(f"缓存配置失败: {e}")
            return False


class DomesticEmailAdapter:
    """国产邮件服务适配器"""
    
    @classmethod
    def configure_domestic_email(cls, email_type: str = 'smtp') -> bool:
        """配置国产邮件服务"""
        try:
            if email_type == 'smtp':
                email_config = {
                    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
                    'EMAIL_HOST': os.getenv('DOMESTIC_EMAIL_HOST', 'smtp.example.com'),
                    'EMAIL_PORT': int(os.getenv('DOMESTIC_EMAIL_PORT', '587')),
                    'EMAIL_USE_TLS': True,
                    'EMAIL_HOST_USER': os.getenv('DOMESTIC_EMAIL_USER', ''),
                    'EMAIL_HOST_PASSWORD': os.getenv('DOMESTIC_EMAIL_PASSWORD', ''),
                    'DEFAULT_FROM_EMAIL': os.getenv('DOMESTIC_EMAIL_FROM', 'noreply@example.com'),
                }
            else:
                # 使用国产邮件服务
                email_config = {
                    'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
                }
            
            # 更新Django邮件配置
            for key, value in email_config.items():
                setattr(settings, key, value)
            
            logger.info(f"国产邮件服务配置完成: {email_type}")
            return True
            
        except Exception as e:
            logger.error(f"邮件服务配置失败: {e}")
            return False
