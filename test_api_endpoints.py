#!/usr/bin/env python3
"""
测试API端点是否正常工作
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_endpoint(url, description):
    """测试单个端点"""
    try:
        response = requests.get(f"{BASE_URL}{url}", timeout=5)
        if response.status_code == 200:
            print(f"✅ {description}: {url} - 正常")
            return True
        elif response.status_code == 401:
            print(f"🔐 {description}: {url} - 需要认证")
            return True
        else:
            print(f"⚠️ {description}: {url} - 状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}: {url} - 连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 测试API端点...")
    print("=" * 50)
    
    endpoints = [
        # 基础API
        ("/api/departments/", "部门管理"),
        ("/api/positions/", "职位管理"),
        ("/api/employees/", "员工管理"),
        
        # 智能分析API
        ("/api/intelligence/analysis/", "智能分析"),
        ("/api/intelligence/metrics/", "分析指标"),
        
        # 工作流API
        ("/api/workflow-templates/", "工作流模板"),
        ("/workflow/workflow-designs/", "工作流设计"),
        
        # 集成管理API
        ("/api/integration/systems/", "集成系统"),
        ("/api/integration/sync-rules/", "同步规则"),
        ("/api/integration/gateways/", "API网关"),
        
        # 权限管理API
        ("/api/permission/permissions/", "权限管理"),
        ("/api/permission/roles/", "角色管理"),
        ("/api/permission/users/", "用户管理"),
        ("/api/permission/permission-logs/", "权限日志"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for url, description in endpoints:
        if test_endpoint(url, description):
            success_count += 1
    
    print("=" * 50)
    print(f"📊 测试结果: {success_count}/{total_count} 个端点正常")
    
    if success_count == total_count:
        print("🎉 所有API端点都正常工作！")
    else:
        print(f"⚠️ 有 {total_count - success_count} 个端点需要检查")

if __name__ == "__main__":
    main()
