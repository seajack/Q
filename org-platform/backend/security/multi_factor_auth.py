# 多因子认证系统
"""
实现多因子认证功能
支持：短信验证码、邮箱验证码、TOTP、硬件令牌
"""

import secrets
import hashlib
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import pyotp
import qrcode
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class MultiFactorAuth:
    """多因子认证系统"""
    
    # 验证码类型
    SMS_CODE = 'sms'
    EMAIL_CODE = 'email'
    TOTP_CODE = 'totp'
    HARDWARE_TOKEN = 'hardware'
    
    # 验证码有效期（分钟）
    CODE_VALIDITY_MINUTES = 5
    
    @classmethod
    def generate_sms_code(cls, phone: str) -> Tuple[str, bool]:
        """生成短信验证码"""
        try:
            # 生成6位数字验证码
            code = str(secrets.randbelow(900000) + 100000)
            
            # 存储到缓存，5分钟有效期
            cache_key = f"mfa_sms_{phone}"
            cache.set(cache_key, code, timeout=cls.CODE_VALIDITY_MINUTES * 60)
            
            # 发送短信（这里需要集成短信服务商）
            success = cls._send_sms(phone, code)
            
            if success:
                logger.info(f"短信验证码发送成功: {phone}")
                return code, True
            else:
                logger.error(f"短信验证码发送失败: {phone}")
                return "", False
                
        except Exception as e:
            logger.error(f"生成短信验证码失败: {e}")
            return "", False
    
    @classmethod
    def generate_email_code(cls, email: str) -> Tuple[str, bool]:
        """生成邮箱验证码"""
        try:
            # 生成6位数字验证码
            code = str(secrets.randbelow(900000) + 100000)
            
            # 存储到缓存，5分钟有效期
            cache_key = f"mfa_email_{email}"
            cache.set(cache_key, code, timeout=cls.CODE_VALIDITY_MINUTES * 60)
            
            # 发送邮件
            subject = '组织架构系统 - 验证码'
            message = f"""
            您的验证码是：{code}
            
            验证码有效期为{cls.CODE_VALIDITY_MINUTES}分钟，请及时使用。
            
            如果这不是您的操作，请忽略此邮件。
            """
            
            success = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )
            
            if success:
                logger.info(f"邮箱验证码发送成功: {email}")
                return code, True
            else:
                logger.error(f"邮箱验证码发送失败: {email}")
                return "", False
                
        except Exception as e:
            logger.error(f"生成邮箱验证码失败: {e}")
            return "", False
    
    @classmethod
    def generate_totp_secret(cls, user: User) -> str:
        """生成TOTP密钥"""
        try:
            # 生成32位随机密钥
            secret = pyotp.random_base32()
            
            # 存储到用户配置中
            user.profile.totp_secret = secret
            user.profile.save()
            
            logger.info(f"TOTP密钥生成成功: {user.username}")
            return secret
            
        except Exception as e:
            logger.error(f"生成TOTP密钥失败: {e}")
            return ""
    
    @classmethod
    def generate_totp_qr_code(cls, user: User, secret: str) -> str:
        """生成TOTP二维码"""
        try:
            # 生成TOTP URI
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user.email or user.username,
                issuer_name="组织架构系统"
            )
            
            # 生成二维码
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"生成TOTP二维码失败: {e}")
            return ""
    
    @classmethod
    def verify_totp_code(cls, user: User, code: str) -> bool:
        """验证TOTP验证码"""
        try:
            if not hasattr(user, 'profile') or not user.profile.totp_secret:
                return False
            
            totp = pyotp.TOTP(user.profile.totp_secret)
            is_valid = totp.verify(code, valid_window=1)
            
            if is_valid:
                logger.info(f"TOTP验证成功: {user.username}")
            else:
                logger.warning(f"TOTP验证失败: {user.username}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"TOTP验证失败: {e}")
            return False
    
    @classmethod
    def verify_sms_code(cls, phone: str, code: str) -> bool:
        """验证短信验证码"""
        try:
            cache_key = f"mfa_sms_{phone}"
            stored_code = cache.get(cache_key)
            
            if not stored_code:
                logger.warning(f"短信验证码不存在或已过期: {phone}")
                return False
            
            if stored_code == code:
                # 验证成功后删除验证码
                cache.delete(cache_key)
                logger.info(f"短信验证码验证成功: {phone}")
                return True
            else:
                logger.warning(f"短信验证码验证失败: {phone}")
                return False
                
        except Exception as e:
            logger.error(f"短信验证码验证失败: {e}")
            return False
    
    @classmethod
    def verify_email_code(cls, email: str, code: str) -> bool:
        """验证邮箱验证码"""
        try:
            cache_key = f"mfa_email_{email}"
            stored_code = cache.get(cache_key)
            
            if not stored_code:
                logger.warning(f"邮箱验证码不存在或已过期: {email}")
                return False
            
            if stored_code == code:
                # 验证成功后删除验证码
                cache.delete(cache_key)
                logger.info(f"邮箱验证码验证成功: {email}")
                return True
            else:
                logger.warning(f"邮箱验证码验证失败: {email}")
                return False
                
        except Exception as e:
            logger.error(f"邮箱验证码验证失败: {e}")
            return False
    
    @classmethod
    def _send_sms(cls, phone: str, code: str) -> bool:
        """发送短信验证码"""
        try:
            # 这里需要集成实际的短信服务商
            # 例如：阿里云短信、腾讯云短信等
            
            # 模拟发送成功
            logger.info(f"发送短信验证码到 {phone}: {code}")
            return True
            
        except Exception as e:
            logger.error(f"发送短信失败: {e}")
            return False
    
    @classmethod
    def get_user_mfa_status(cls, user: User) -> Dict[str, Any]:
        """获取用户MFA状态"""
        try:
            status = {
                'sms_enabled': bool(user.profile.phone if hasattr(user, 'profile') else False),
                'email_enabled': bool(user.email),
                'totp_enabled': bool(
                    hasattr(user, 'profile') and 
                    user.profile.totp_secret
                ),
                'hardware_enabled': False,  # 硬件令牌暂未实现
            }
            
            return status
            
        except Exception as e:
            logger.error(f"获取MFA状态失败: {e}")
            return {}
    
    @classmethod
    def enable_mfa_method(cls, user: User, method: str, **kwargs) -> bool:
        """启用MFA方法"""
        try:
            if method == cls.SMS_CODE:
                phone = kwargs.get('phone')
                if phone:
                    user.profile.phone = phone
                    user.profile.save()
                    return True
            
            elif method == cls.EMAIL_CODE:
                # 邮箱验证码不需要额外配置
                return bool(user.email)
            
            elif method == cls.TOTP_CODE:
                secret = cls.generate_totp_secret(user)
                return bool(secret)
            
            return False
            
        except Exception as e:
            logger.error(f"启用MFA方法失败: {e}")
            return False
    
    @classmethod
    def disable_mfa_method(cls, user: User, method: str) -> bool:
        """禁用MFA方法"""
        try:
            if method == cls.SMS_CODE:
                user.profile.phone = None
                user.profile.save()
            
            elif method == cls.TOTP_CODE:
                user.profile.totp_secret = None
                user.profile.save()
            
            logger.info(f"MFA方法已禁用: {method}")
            return True
            
        except Exception as e:
            logger.error(f"禁用MFA方法失败: {e}")
            return False


class MFAMiddleware:
    """MFA中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 检查是否需要MFA验证
        if self._requires_mfa(request):
            if not self._is_mfa_verified(request):
                # 重定向到MFA验证页面
                from django.shortcuts import redirect
                return redirect('/auth/mfa-verify/')
        
        response = self.get_response(request)
        return response
    
    def _requires_mfa(self, request) -> bool:
        """检查是否需要MFA验证"""
        # 排除不需要MFA的路径
        excluded_paths = [
            '/auth/login/',
            '/auth/mfa-verify/',
            '/auth/logout/',
            '/static/',
            '/media/',
        ]
        
        if request.path in excluded_paths:
            return False
        
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            return False
        
        # 检查用户是否启用了MFA
        mfa_status = MultiFactorAuth.get_user_mfa_status(request.user)
        if not any(mfa_status.values()):
            return False
        
        return True
    
    def _is_mfa_verified(self, request) -> bool:
        """检查MFA是否已验证"""
        return request.session.get('mfa_verified', False)
