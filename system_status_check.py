#!/usr/bin/env python3
"""
系统状态检查和优化脚本
"""

import requests
import json
import time
from datetime import datetime

# 服务配置
BACKEND_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:5173"

def check_service_health(url, service_name):
    """检查服务健康状态"""
    try:
        # 对于后端，检查API根路径
        if "8001" in url:
            test_url = f"{url}/api/"
        else:
            test_url = url
            
        response = requests.get(test_url, timeout=5)
        if response.status_code in [200, 301, 302]:
            print(f"✅ {service_name}: 运行正常")
            return True
        else:
            print(f"⚠️ {service_name}: 状态码 {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service_name}: 连接失败 - {e}")
        return False

def test_api_endpoints():
    """测试关键API端点"""
    print("\n🧪 测试API端点...")
    
    critical_endpoints = [
        ("/api/departments/", "部门管理API"),
        ("/api/employees/", "员工管理API"),
        ("/api/workflow-templates/", "工作流模板API"),
        ("/api/intelligence/analysis/", "智能分析API"),
        ("/api/permission/users/", "用户管理API"),
        ("/api/integration/systems/", "集成系统API"),
    ]
    
    success_count = 0
    for endpoint, name in critical_endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=3)
            if response.status_code in [200, 401]:  # 200正常，401需要认证也算正常
                print(f"  ✅ {name}")
                success_count += 1
            else:
                print(f"  ❌ {name} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {name} - 错误: {str(e)[:50]}")
    
    print(f"\n📊 API测试结果: {success_count}/{len(critical_endpoints)} 个端点正常")
    return success_count == len(critical_endpoints)

def check_database_migrations():
    """检查数据库迁移状态"""
    print("\n🗄️ 检查数据库状态...")
    
    # 这里可以添加数据库连接检查
    # 由于我们使用Django，可以通过API端点间接检查
    try:
        response = requests.get(f"{BACKEND_URL}/api/departments/", timeout=5)
        if response.status_code in [200, 401]:
            print("  ✅ 数据库连接正常")
            return True
        else:
            print("  ⚠️ 数据库可能有问题")
            return False
    except Exception as e:
        print(f"  ❌ 数据库连接失败: {str(e)[:50]}")
        return False

def generate_system_report():
    """生成系统状态报告"""
    print("\n📋 生成系统状态报告...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "services": {
            "backend": f"{BACKEND_URL} - Django后端服务",
            "frontend": f"{FRONTEND_URL} - Vue前端服务"
        },
        "features": {
            "workflow_designer": "工作流可视化设计器",
            "intelligent_analysis": "智能组织分析",
            "permission_management": "权限管理系统",
            "integration_management": "系统集成管理"
        },
        "access_urls": {
            "main_app": f"{FRONTEND_URL}",
            "workflow_management": f"{FRONTEND_URL}/workflow-list",
            "workflow_designer": f"{FRONTEND_URL}/workflow-designer",
            "intelligent_analysis": f"{FRONTEND_URL}/intelligent-analysis",
            "api_docs": f"{BACKEND_URL}/api/"
        }
    }
    
    return report

def print_usage_guide():
    """打印使用指南"""
    print("\n🎯 系统使用指南:")
    print("=" * 60)
    
    print("\n📱 前端访问:")
    print(f"  • 主页面: {FRONTEND_URL}")
    print(f"  • 工作流管理: {FRONTEND_URL}/workflow-list")
    print(f"  • 流程设计器: {FRONTEND_URL}/workflow-designer")
    print(f"  • 智能分析: {FRONTEND_URL}/intelligent-analysis")
    
    print("\n🔗 后端API:")
    print(f"  • API根路径: {BACKEND_URL}/api/")
    print(f"  • 工作流API: {BACKEND_URL}/workflow/")
    print(f"  • 权限API: {BACKEND_URL}/api/permission/")
    print(f"  • 集成API: {BACKEND_URL}/api/integration/")
    
    print("\n🚀 快速开始:")
    print("  1. 访问主页面，点击'工作流管理'")
    print("  2. 查看工作流概览和快速入口")
    print("  3. 点击'流程设计器'开始创建工作流")
    print("  4. 使用拖拽方式设计业务流程")
    print("  5. 测试和保存工作流")
    
    print("\n🎨 设计器功能:")
    print("  • 拖拽式节点设计")
    print("  • 实时预览和测试")
    print("  • 版本管理和回滚")
    print("  • 智能连接和验证")
    
    print("\n🧠 智能分析功能:")
    print("  • 组织架构分析")
    print("  • AI优化建议")
    print("  • 数据可视化")
    print("  • 性能指标监控")

def main():
    """主函数"""
    print("🔍 系统状态检查")
    print("=" * 60)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查服务状态
    print("\n🌐 检查服务状态...")
    backend_ok = check_service_health(BACKEND_URL, "后端服务 (Django)")
    frontend_ok = check_service_health(FRONTEND_URL, "前端服务 (Vue)")
    
    # 检查API端点
    api_ok = test_api_endpoints()
    
    # 检查数据库
    db_ok = check_database_migrations()
    
    # 生成报告
    report = generate_system_report()
    
    # 总结
    print("\n📊 系统状态总结:")
    print("=" * 60)
    
    if backend_ok and frontend_ok and api_ok and db_ok:
        print("🎉 所有系统组件运行正常！")
        print("✅ 后端服务: 正常")
        print("✅ 前端服务: 正常") 
        print("✅ API端点: 正常")
        print("✅ 数据库: 正常")
        
        print_usage_guide()
        
    else:
        print("⚠️ 系统存在一些问题:")
        if not backend_ok:
            print("❌ 后端服务异常")
        if not frontend_ok:
            print("❌ 前端服务异常")
        if not api_ok:
            print("❌ 部分API端点异常")
        if not db_ok:
            print("❌ 数据库连接异常")
            
        print("\n🔧 建议操作:")
        print("1. 检查服务是否正确启动")
        print("2. 确认端口没有被占用")
        print("3. 检查数据库迁移是否完成")
        print("4. 查看服务日志获取详细错误信息")

if __name__ == "__main__":
    main()
