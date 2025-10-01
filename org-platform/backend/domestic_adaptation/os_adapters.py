# 国产操作系统适配器
"""
支持国产操作系统的适配器实现
支持：麒麟操作系统、统信UOS、中科方德
"""

import platform
import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DomesticOSAdapter:
    """国产操作系统适配器"""
    
    SUPPORTED_OS = {
        'kylin': {
            'name': '麒麟操作系统',
            'detect_cmd': 'cat /etc/kylin-release',
            'package_manager': 'yum',
            'python_path': '/usr/bin/python3'
        },
        'uos': {
            'name': '统信UOS',
            'detect_cmd': 'cat /etc/uos-release',
            'package_manager': 'apt',
            'python_path': '/usr/bin/python3'
        },
        'neokylin': {
            'name': '中科方德',
            'detect_cmd': 'cat /etc/neokylin-release',
            'package_manager': 'yum',
            'python_path': '/usr/bin/python3'
        }
    }
    
    @classmethod
    def detect_os(cls):
        """检测当前操作系统"""
        try:
            for os_type, config in cls.SUPPORTED_OS.items():
                try:
                    result = subprocess.run(
                        config['detect_cmd'].split(),
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        logger.info(f"检测到国产操作系统: {config['name']}")
                        return os_type, config
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            # 如果未检测到国产操作系统，返回通用Linux
            return 'generic', {
                'name': '通用Linux',
                'package_manager': 'apt',
                'python_path': '/usr/bin/python3'
            }
            
        except Exception as e:
            logger.error(f"操作系统检测失败: {e}")
            return 'unknown', {}
    
    @classmethod
    def install_dependencies(cls, os_type=None):
        """安装系统依赖"""
        if not os_type:
            os_type, _ = cls.detect_os()
        
        if os_type not in cls.SUPPORTED_OS:
            logger.warning(f"不支持的操作系统类型: {os_type}")
            return False
        
        config = cls.SUPPORTED_OS[os_type]
        package_manager = config['package_manager']
        
        # 定义需要安装的依赖包
        dependencies = [
            'python3-dev',
            'python3-pip',
            'build-essential',
            'libssl-dev',
            'libffi-dev',
            'libjpeg-dev',
            'libpng-dev',
            'libxml2-dev',
            'libxslt1-dev',
            'zlib1g-dev'
        ]
        
        try:
            if package_manager == 'apt':
                cmd = ['sudo', 'apt', 'update']
                subprocess.run(cmd, check=True)
                
                cmd = ['sudo', 'apt', 'install', '-y'] + dependencies
                subprocess.run(cmd, check=True)
                
            elif package_manager == 'yum':
                cmd = ['sudo', 'yum', 'update', '-y']
                subprocess.run(cmd, check=True)
                
                cmd = ['sudo', 'yum', 'install', '-y'] + dependencies
                subprocess.run(cmd, check=True)
            
            logger.info("系统依赖安装完成")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"依赖安装失败: {e}")
            return False
    
    @classmethod
    def configure_environment(cls, os_type=None):
        """配置环境变量"""
        if not os_type:
            os_type, _ = cls.detect_os()
        
        config = cls.SUPPORTED_OS.get(os_type, {})
        python_path = config.get('python_path', '/usr/bin/python3')
        
        # 设置环境变量
        env_vars = {
            'PYTHON_PATH': python_path,
            'DOMESTIC_OS': os_type,
            'DOMESTIC_OS_NAME': config.get('name', 'Unknown'),
        }
        
        for key, value in env_vars.items():
            os.environ[key] = value
        
        logger.info(f"环境配置完成: {env_vars}")
        return env_vars
    
    @classmethod
    def check_compatibility(cls):
        """检查系统兼容性"""
        os_type, config = cls.detect_os()
        
        compatibility_report = {
            'os_type': os_type,
            'os_name': config.get('name', 'Unknown'),
            'python_version': platform.python_version(),
            'architecture': platform.machine(),
            'compatible': True,
            'issues': []
        }
        
        # 检查Python版本
        python_version = platform.python_version()
        if python_version < '3.8':
            compatibility_report['compatible'] = False
            compatibility_report['issues'].append(
                f"Python版本过低: {python_version}, 需要3.8+"
            )
        
        # 检查必要的系统命令
        required_commands = ['python3', 'pip3', 'git']
        for cmd in required_commands:
            try:
                subprocess.run([cmd, '--version'], 
                             capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                compatibility_report['issues'].append(f"缺少命令: {cmd}")
        
        return compatibility_report


class DomesticOSSetup:
    """国产操作系统设置类"""
    
    def __init__(self):
        self.os_type, self.config = DomesticOSAdapter.detect_os()
    
    def setup_environment(self):
        """设置环境"""
        logger.info(f"开始设置{self.config.get('name', 'Unknown')}环境...")
        
        # 1. 安装依赖
        if not DomesticOSAdapter.install_dependencies(self.os_type):
            return False
        
        # 2. 配置环境变量
        DomesticOSAdapter.configure_environment(self.os_type)
        
        # 3. 检查兼容性
        compatibility = DomesticOSAdapter.check_compatibility()
        if not compatibility['compatible']:
            logger.error(f"兼容性检查失败: {compatibility['issues']}")
            return False
        
        logger.info("环境设置完成")
        return True
    
    def get_system_info(self):
        """获取系统信息"""
        return {
            'os_type': self.os_type,
            'os_name': self.config.get('name', 'Unknown'),
            'python_version': platform.python_version(),
            'architecture': platform.machine(),
            'platform': platform.platform()
        }
