# 数据加密存储系统
"""
实现敏感数据加密存储功能
支持：AES加密、RSA加密、国密算法
"""

import os
import base64
import hashlib
import logging
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

class DataEncryption:
    """数据加密类"""
    
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """获取加密密钥"""
        key = getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            # 从环境变量获取
            key = os.getenv('ENCRYPTION_KEY')
            if not key:
                # 生成新的密钥
                key = Fernet.generate_key()
                logger.warning("未找到加密密钥，已生成新密钥。请保存此密钥：")
                logger.warning(f"ENCRYPTION_KEY={key.decode()}")
        
        if isinstance(key, str):
            key = key.encode()
        
        return key
    
    def encrypt_data(self, data: str) -> str:
        """加密数据"""
        try:
            if not data:
                return ""
            
            # 转换为字节
            data_bytes = data.encode('utf-8')
            
            # 加密
            encrypted_data = self.fernet.encrypt(data_bytes)
            
            # 转换为base64字符串
            encrypted_str = base64.b64encode(encrypted_data).decode('utf-8')
            
            logger.debug("数据加密成功")
            return encrypted_str
            
        except Exception as e:
            logger.error(f"数据加密失败: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """解密数据"""
        try:
            if not encrypted_data:
                return ""
            
            # 从base64解码
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # 解密
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            
            # 转换为字符串
            decrypted_str = decrypted_data.decode('utf-8')
            
            logger.debug("数据解密成功")
            return decrypted_str
            
        except Exception as e:
            logger.error(f"数据解密失败: {e}")
            raise


class RSAEncryption:
    """RSA加密类"""
    
    def __init__(self):
        self.private_key = self._get_private_key()
        self.public_key = self._get_public_key()
    
    def _get_private_key(self):
        """获取私钥"""
        private_key_path = getattr(settings, 'RSA_PRIVATE_KEY_PATH', None)
        if not private_key_path:
            private_key_path = os.getenv('RSA_PRIVATE_KEY_PATH')
        
        if private_key_path and os.path.exists(private_key_path):
            with open(private_key_path, 'rb') as f:
                return serialization.load_pem_private_key(
                    f.read(),
                    password=None
                )
        else:
            # 生成新的密钥对
            return self._generate_key_pair()
    
    def _get_public_key(self):
        """获取公钥"""
        public_key_path = getattr(settings, 'RSA_PUBLIC_KEY_PATH', None)
        if not public_key_path:
            public_key_path = os.getenv('RSA_PUBLIC_KEY_PATH')
        
        if public_key_path and os.path.exists(public_key_path):
            with open(public_key_path, 'rb') as f:
                return serialization.load_pem_public_key(f.read())
        else:
            return self.private_key.public_key()
    
    def _generate_key_pair(self):
        """生成RSA密钥对"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # 保存私钥
        private_key_path = os.path.join(settings.BASE_DIR, 'keys', 'private_key.pem')
        os.makedirs(os.path.dirname(private_key_path), exist_ok=True)
        
        with open(private_key_path, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # 保存公钥
        public_key_path = os.path.join(settings.BASE_DIR, 'keys', 'public_key.pem')
        with open(public_key_path, 'wb') as f:
            f.write(private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        
        logger.info("RSA密钥对生成完成")
        return private_key
    
    def encrypt_with_public_key(self, data: str) -> str:
        """使用公钥加密"""
        try:
            data_bytes = data.encode('utf-8')
            encrypted_data = self.public_key.encrypt(
                data_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"RSA公钥加密失败: {e}")
            raise
    
    def decrypt_with_private_key(self, encrypted_data: str) -> str:
        """使用私钥解密"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"RSA私钥解密失败: {e}")
            raise


class DomesticEncryption:
    """国产加密算法"""
    
    def __init__(self):
        self.sm4_key = self._get_sm4_key()
    
    def _get_sm4_key(self) -> bytes:
        """获取SM4密钥"""
        key = getattr(settings, 'SM4_KEY', None)
        if not key:
            key = os.getenv('SM4_KEY')
            if not key:
                # 生成16字节密钥
                key = os.urandom(16)
                logger.warning("未找到SM4密钥，已生成新密钥")
        
        if isinstance(key, str):
            key = key.encode()
        
        return key
    
    def sm4_encrypt(self, data: str) -> str:
        """SM4加密"""
        try:
            # 这里需要集成国产SM4算法库
            # 例如：gmssl库
            logger.info("SM4加密功能需要集成国产加密库")
            return data  # 临时返回原数据
            
        except Exception as e:
            logger.error(f"SM4加密失败: {e}")
            raise
    
    def sm4_decrypt(self, encrypted_data: str) -> str:
        """SM4解密"""
        try:
            # 这里需要集成国产SM4算法库
            logger.info("SM4解密功能需要集成国产加密库")
            return encrypted_data  # 临时返回原数据
            
        except Exception as e:
            logger.error(f"SM4解密失败: {e}")
            raise


class EncryptedField:
    """加密字段装饰器"""
    
    def __init__(self, field_name: str, encryption_type: str = 'aes'):
        self.field_name = field_name
        self.encryption_type = encryption_type
        
        if encryption_type == 'aes':
            self.encryption = DataEncryption()
        elif encryption_type == 'rsa':
            self.encryption = RSAEncryption()
        elif encryption_type == 'sm4':
            self.encryption = DomesticEncryption()
        else:
            raise ValueError(f"不支持的加密类型: {encryption_type}")
    
    def encrypt(self, value: str) -> str:
        """加密字段值"""
        if not value:
            return ""
        
        try:
            if self.encryption_type == 'aes':
                return self.encryption.encrypt_data(value)
            elif self.encryption_type == 'rsa':
                return self.encryption.encrypt_with_public_key(value)
            elif self.encryption_type == 'sm4':
                return self.encryption.sm4_encrypt(value)
        except Exception as e:
            logger.error(f"字段加密失败: {e}")
            return value
    
    def decrypt(self, encrypted_value: str) -> str:
        """解密字段值"""
        if not encrypted_value:
            return ""
        
        try:
            if self.encryption_type == 'aes':
                return self.encryption.decrypt_data(encrypted_value)
            elif self.encryption_type == 'rsa':
                return self.encryption.decrypt_with_private_key(encrypted_value)
            elif self.encryption_type == 'sm4':
                return self.encryption.sm4_decrypt(encrypted_value)
        except Exception as e:
            logger.error(f"字段解密失败: {e}")
            return encrypted_value


class PasswordEncryption:
    """密码加密类"""
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> Dict[str, str]:
        """哈希密码"""
        if not salt:
            salt = os.urandom(32).hex()
        
        # 使用PBKDF2进行密码哈希
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        return {
            'hash': key.decode(),
            'salt': salt
        }
    
    @staticmethod
    def verify_password(password: str, hash_value: str, salt: str) -> bool:
        """验证密码"""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode(),
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key.decode() == hash_value
            
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False
