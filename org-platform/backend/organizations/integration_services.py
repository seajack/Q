import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.utils import timezone
from .integration_models import (
    IntegrationSystem, APIGateway, APIRoute, DataSyncRule, 
    SyncLog, APIMonitor, IntegrationConfig
)

logger = logging.getLogger(__name__)


class IntegrationService:
    """系统集成服务"""
    
    def __init__(self, system: IntegrationSystem):
        self.system = system
        self.session = requests.Session()
        self._setup_auth()
    
    def _setup_auth(self):
        """设置认证"""
        auth_config = self.system.auth_config or {}
        
        if self.system.auth_type == 'basic':
            username = auth_config.get('username')
            password = auth_config.get('password')
            if username and password:
                self.session.auth = (username, password)
        
        elif self.system.auth_type == 'token':
            token = auth_config.get('token')
            if token:
                self.session.headers.update({'Authorization': f'Bearer {token}'})
        
        elif self.system.auth_type == 'api_key':
            api_key = auth_config.get('api_key')
            key_name = auth_config.get('key_name', 'X-API-Key')
            if api_key:
                self.session.headers.update({key_name: api_key})
    
    def test_connection(self) -> Dict[str, Any]:
        """测试连接"""
        try:
            start_time = time.time()
            
            # 根据系统类型选择不同的测试端点
            if self.system.system_type == 'performance' or ('performance' in self.system.name.lower()):
                # 绩效考核系统使用cycles端点
                test_url = f"{self.system.base_url}/api/cycles/"
            elif self.system.system_type == 'finance':
                # 财务系统使用health端点
                test_url = f"{self.system.base_url}/health"
            elif self.system.system_type == 'oa':
                # OA系统使用health端点
                test_url = f"{self.system.base_url}/health"
            else:
                # 其他系统使用health端点
                test_url = f"{self.system.base_url}/health"
            
            response = self.session.get(
                test_url,
                timeout=self.system.timeout
            )
            response_time = (time.time() - start_time) * 1000
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response_time,
                'message': '连接成功' if response.status_code == 200 else '连接失败'
            }
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': '连接失败'
            }
    
    def get_data(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """获取数据"""
        try:
            url = f"{self.system.base_url}/{endpoint.lstrip('/')}"
            response = self.session.get(
                url,
                params=params,
                timeout=self.system.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取数据失败: {str(e)}")
            raise
    
    def post_data(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """发送数据"""
        try:
            url = f"{self.system.base_url}/{endpoint.lstrip('/')}"
            response = self.session.post(
                url,
                json=data,
                timeout=self.system.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"发送数据失败: {str(e)}")
            raise
    
    def sync_employees(self, employees_data: List[Dict]) -> Dict[str, Any]:
        """同步员工数据"""
        try:
            endpoint = '/api/employees/sync'
            result = self.post_data(endpoint, {'employees': employees_data})
            return {
                'success': True,
                'synced_count': len(employees_data),
                'result': result
            }
        except Exception as e:
            logger.error(f"同步员工数据失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def sync_departments(self, departments_data: List[Dict]) -> Dict[str, Any]:
        """同步部门数据"""
        try:
            endpoint = '/api/departments/sync'
            result = self.post_data(endpoint, {'departments': departments_data})
            return {
                'success': True,
                'synced_count': len(departments_data),
                'result': result
            }
        except Exception as e:
            logger.error(f"同步部门数据失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class APIGatewayService:
    """API网关服务"""
    
    def __init__(self, gateway: APIGateway):
        self.gateway = gateway
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """设置会话"""
        if self.gateway.api_key_required:
            # 这里应该从配置中获取API Key
            api_key = self.get_api_key()
            if api_key:
                self.session.headers.update({'X-API-Key': api_key})
    
    def get_api_key(self) -> Optional[str]:
        """获取API Key"""
        # 这里应该从安全存储中获取API Key
        return "your-api-key-here"
    
    def route_request(self, route: APIRoute, request_data: Dict) -> Dict[str, Any]:
        """路由请求"""
        try:
            # 应用请求转换
            transformed_data = self._transform_request(route, request_data)
            
            # 发送请求
            response = self.session.request(
                method=route.method,
                url=route.target_url,
                json=transformed_data,
                timeout=30
            )
            
            # 应用响应转换
            transformed_response = self._transform_response(route, response.json())
            
            # 记录监控数据
            self._record_monitor_data(route, response)
            
            return {
                'success': True,
                'data': transformed_response,
                'status_code': response.status_code
            }
        except Exception as e:
            logger.error(f"路由请求失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _transform_request(self, route: APIRoute, data: Dict) -> Dict:
        """转换请求数据"""
        transform_config = route.request_transform or {}
        if not transform_config:
            return data
        
        # 这里实现请求数据转换逻辑
        # 例如：字段映射、数据格式转换等
        return data
    
    def _transform_response(self, route: APIRoute, data: Dict) -> Dict:
        """转换响应数据"""
        transform_config = route.response_transform or {}
        if not transform_config:
            return data
        
        # 这里实现响应数据转换逻辑
        # 例如：字段映射、数据格式转换等
        return data
    
    def _record_monitor_data(self, route: APIRoute, response):
        """记录监控数据"""
        try:
            APIMonitor.objects.create(
                route=route,
                request_count=1,
                success_count=1 if response.status_code < 400 else 0,
                error_count=1 if response.status_code >= 400 else 0,
                avg_response_time=response.elapsed.total_seconds() * 1000,
                max_response_time=response.elapsed.total_seconds() * 1000,
                min_response_time=response.elapsed.total_seconds() * 1000,
                error_rate=100 if response.status_code >= 400 else 0,
                status_code_distribution={str(response.status_code): 1}
            )
        except Exception as e:
            logger.error(f"记录监控数据失败: {str(e)}")


class DataSyncService:
    """数据同步服务"""
    
    def __init__(self, sync_rule: DataSyncRule):
        self.sync_rule = sync_rule
        self.source_service = IntegrationService(sync_rule.source_system)
        self.target_service = IntegrationService(sync_rule.target_system)
    
    def execute_sync(self) -> Dict[str, Any]:
        """执行同步"""
        start_time = timezone.now()
        sync_log = SyncLog.objects.create(
            sync_rule=self.sync_rule,
            status='running',
            start_time=start_time
        )
        
        try:
            # 获取源数据
            source_data = self._get_source_data()
            
            # 数据清洗
            if self.sync_rule.data_cleaning_enabled:
                source_data = self._clean_data(source_data)
            
            # 数据校验
            if self.sync_rule.validation_enabled:
                validation_result = self._validate_data(source_data)
                if not validation_result['valid']:
                    raise Exception(f"数据校验失败: {validation_result['errors']}")
            
            # 字段映射
            mapped_data = self._map_fields(source_data)
            
            # 批量同步
            sync_result = self._batch_sync(mapped_data)
            
            # 更新同步日志
            end_time = timezone.now()
            sync_log.status = 'success'
            sync_log.end_time = end_time
            sync_log.total_records = len(source_data)
            sync_log.success_records = sync_result['success_count']
            sync_log.error_records = sync_result['error_count']
            sync_log.duration_seconds = (end_time - start_time).total_seconds()
            sync_log.records_per_second = sync_log.total_records / sync_log.duration_seconds if sync_log.duration_seconds > 0 else 0
            sync_log.save()
            
            # 更新最后同步时间
            self.sync_rule.source_system.last_sync_time = end_time
            self.sync_rule.source_system.save()
            
            return {
                'success': True,
                'total_records': sync_log.total_records,
                'success_records': sync_log.success_records,
                'error_records': sync_log.error_records,
                'duration': sync_log.duration_seconds
            }
            
        except Exception as e:
            # 更新错误日志
            end_time = timezone.now()
            sync_log.status = 'error'
            sync_log.end_time = end_time
            sync_log.error_message = str(e)
            sync_log.duration_seconds = (end_time - start_time).total_seconds()
            sync_log.save()
            
            logger.error(f"数据同步失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_source_data(self) -> List[Dict]:
        """获取源数据"""
        endpoint = f"/api/{self.sync_rule.source_table}"
        params = self.sync_rule.filter_conditions or {}
        return self.source_service.get_data(endpoint, params)
    
    def _clean_data(self, data: List[Dict]) -> List[Dict]:
        """数据清洗"""
        cleaned_data = []
        cleaning_rules = self.sync_rule.cleaning_rules or []
        
        for record in data:
            cleaned_record = record.copy()
            
            for rule in cleaning_rules:
                field = rule.get('field')
                rule_type = rule.get('type')
                
                if field in cleaned_record:
                    if rule_type == 'trim':
                        cleaned_record[field] = str(cleaned_record[field]).strip()
                    elif rule_type == 'lowercase':
                        cleaned_record[field] = str(cleaned_record[field]).lower()
                    elif rule_type == 'uppercase':
                        cleaned_record[field] = str(cleaned_record[field]).upper()
                    elif rule_type == 'remove_special_chars':
                        import re
                        cleaned_record[field] = re.sub(r'[^\w\s]', '', str(cleaned_record[field]))
                    elif rule_type == 'default_value':
                        if not cleaned_record[field]:
                            cleaned_record[field] = rule.get('value', '')
            
            cleaned_data.append(cleaned_record)
        
        return cleaned_data
    
    def _validate_data(self, data: List[Dict]) -> Dict[str, Any]:
        """数据校验"""
        validation_rules = self.sync_rule.validation_rules or []
        errors = []
        
        for record in data:
            for rule in validation_rules:
                field = rule.get('field')
                rule_type = rule.get('type')
                
                if field in record:
                    value = record[field]
                    
                    if rule_type == 'required' and not value:
                        errors.append(f"字段 {field} 不能为空")
                    elif rule_type == 'email' and value and '@' not in str(value):
                        errors.append(f"字段 {field} 不是有效的邮箱地址")
                    elif rule_type == 'phone' and value:
                        import re
                        if not re.match(r'^1[3-9]\d{9}$', str(value)):
                            errors.append(f"字段 {field} 不是有效的手机号码")
                    elif rule_type == 'length':
                        min_length = rule.get('min_length', 0)
                        max_length = rule.get('max_length', 1000)
                        if len(str(value)) < min_length or len(str(value)) > max_length:
                            errors.append(f"字段 {field} 长度必须在 {min_length}-{max_length} 之间")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _map_fields(self, data: List[Dict]) -> List[Dict]:
        """字段映射"""
        field_mapping = self.sync_rule.field_mapping or {}
        mapped_data = []
        
        for record in data:
            mapped_record = {}
            for source_field, target_field in field_mapping.items():
                if source_field in record:
                    mapped_record[target_field] = record[source_field]
            mapped_data.append(mapped_record)
        
        return mapped_data
    
    def _batch_sync(self, data: List[Dict]) -> Dict[str, int]:
        """批量同步"""
        batch_size = self.sync_rule.batch_size
        success_count = 0
        error_count = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            try:
                endpoint = f"/api/{self.sync_rule.target_table}/batch"
                result = self.target_service.post_data(endpoint, {'data': batch})
                success_count += len(batch)
            except Exception as e:
                logger.error(f"批量同步失败: {str(e)}")
                error_count += len(batch)
        
        return {
            'success_count': success_count,
            'error_count': error_count
        }


class IntegrationMonitorService:
    """集成监控服务"""
    
    @staticmethod
    def get_system_health(system: IntegrationSystem) -> Dict[str, Any]:
        """获取系统健康状态"""
        try:
            service = IntegrationService(system)
            connection_test = service.test_connection()
            
            return {
                'system_id': system.id,
                'system_name': system.name,
                'status': 'healthy' if connection_test['success'] else 'unhealthy',
                'response_time': connection_test.get('response_time', 0),
                'last_check': timezone.now(),
                'details': connection_test
            }
        except Exception as e:
            return {
                'system_id': system.id,
                'system_name': system.name,
                'status': 'error',
                'error': str(e),
                'last_check': timezone.now()
            }
    
    @staticmethod
    def get_sync_statistics(sync_rule: DataSyncRule) -> Dict[str, Any]:
        """获取同步统计"""
        recent_logs = SyncLog.objects.filter(
            sync_rule=sync_rule,
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).order_by('-created_at')
        
        total_syncs = recent_logs.count()
        successful_syncs = recent_logs.filter(status='success').count()
        failed_syncs = recent_logs.filter(status='error').count()
        
        total_records = sum(log.total_records for log in recent_logs)
        success_records = sum(log.success_records for log in recent_logs)
        
        return {
            'total_syncs': total_syncs,
            'successful_syncs': successful_syncs,
            'failed_syncs': failed_syncs,
            'success_rate': (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0,
            'total_records': total_records,
            'success_records': success_records,
            'error_records': total_records - success_records
        }
    
    @staticmethod
    def get_api_statistics(route: APIRoute) -> Dict[str, Any]:
        """获取API统计"""
        recent_monitors = APIMonitor.objects.filter(
            route=route,
            timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
        ).order_by('-timestamp')
        
        total_requests = sum(monitor.request_count for monitor in recent_monitors)
        total_success = sum(monitor.success_count for monitor in recent_monitors)
        total_errors = sum(monitor.error_count for monitor in recent_monitors)
        
        avg_response_time = sum(monitor.avg_response_time for monitor in recent_monitors) / len(recent_monitors) if recent_monitors else 0
        
        return {
            'total_requests': total_requests,
            'success_requests': total_success,
            'error_requests': total_errors,
            'success_rate': (total_success / total_requests * 100) if total_requests > 0 else 0,
            'avg_response_time': avg_response_time,
            'error_rate': (total_errors / total_requests * 100) if total_requests > 0 else 0
        }
