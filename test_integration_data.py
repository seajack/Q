#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
sys.path.append('org-platform/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'org_platform.settings')
django.setup()

from organizations.integration_models import IntegrationSystem, DataSyncRule, SyncLog, APIMonitor

def check_integration_data():
    print("=== 检查集成数据 ===")
    
    # 检查集成系统
    systems = IntegrationSystem.objects.all()
    print(f"集成系统总数: {systems.count()}")
    for system in systems:
        print(f"  - {system.name} ({system.system_type}) - 状态: {getattr(system, 'status', 'N/A')}")
    
    # 检查同步规则
    sync_rules = DataSyncRule.objects.all()
    print(f"同步规则总数: {sync_rules.count()}")
    
    # 检查同步日志
    sync_logs = SyncLog.objects.all()
    print(f"同步日志总数: {sync_logs.count()}")
    
    # 检查API监控
    api_monitors = APIMonitor.objects.all()
    print(f"API监控总数: {api_monitors.count()}")
    
    # 检查系统字段
    if systems.exists():
        system = systems.first()
        print(f"\n=== 系统字段信息 ===")
        print(f"系统名称: {system.name}")
        print(f"系统类型: {system.system_type}")
        print(f"基础URL: {system.base_url}")
        print(f"状态字段: {hasattr(system, 'status')}")
        if hasattr(system, 'status'):
            print(f"状态值: {system.status}")
        print(f"监控启用: {hasattr(system, 'monitoring_enabled')}")
        if hasattr(system, 'monitoring_enabled'):
            print(f"监控状态: {system.monitoring_enabled}")

if __name__ == "__main__":
    check_integration_data()
