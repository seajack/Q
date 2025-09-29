#!/usr/bin/env python3
"""
智能组织架构功能完整测试脚本
"""

import subprocess
import time
import requests
import json
import os

def run_command(cmd, cwd=None):
    """执行命令"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_service(url, name):
    """检查服务状态"""
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ {name} 服务正常 (状态码: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ {name} 服务异常: {e}")
        return False

def test_api_endpoint(url, name):
    """测试API端点"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ {name} API测试通过")
                return True
            else:
                print(f"⚠️ {name} API返回success=False: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ {name} API测试失败 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {name} API测试异常: {e}")
        return False

def main():
    print("🚀 智能组织架构功能测试")
    print("=" * 60)
    
    # 1. 检查后端服务
    print("\n1️⃣ 检查后端服务...")
    backend_ok = check_service("http://localhost:8001", "Django后端")
    
    if not backend_ok:
        print("❌ 后端服务未启动，请先运行:")
        print("   cd e:\\code\\Q\\org-platform\\backend")
        print("   python manage.py runserver 0.0.0.0:8001")
        return
    
    # 2. 创建测试数据
    print("\n2️⃣ 创建测试数据...")
    success, stdout, stderr = run_command("python create_test_data.py", cwd="e:\\code\\Q")
    if success:
        print("✅ 测试数据创建成功")
    else:
        print(f"⚠️ 测试数据创建可能有问题: {stderr}")
    
    # 3. 测试API端点
    print("\n3️⃣ 测试API端点...")
    
    api_tests = [
        ("http://localhost:8001/api/intelligence/analysis/", "组织分析"),
        ("http://localhost:8001/api/intelligence/metrics/", "组织指标"),
        ("http://localhost:8001/api/intelligence/suggestions/", "优化建议"),
        ("http://localhost:8001/api/intelligence/history/", "分析历史"),
        ("http://localhost:8001/api/intelligence/benchmark/", "基准对比"),
    ]
    
    passed_tests = 0
    total_tests = len(api_tests)
    
    for url, name in api_tests:
        if test_api_endpoint(url, name):
            passed_tests += 1
        time.sleep(0.5)  # 避免请求过快
    
    # 4. 测试POST接口
    print("\n4️⃣ 测试POST接口...")
    
    # 测试刷新分析
    try:
        response = requests.post("http://localhost:8001/api/intelligence/refresh/", timeout=10)
        if response.status_code == 200:
            print("✅ 刷新分析API测试通过")
            passed_tests += 1
        else:
            print(f"❌ 刷新分析API测试失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 刷新分析API测试异常: {e}")
    
    total_tests += 1
    
    # 测试变更模拟
    try:
        test_data = {"changes": [{"type": "test", "target": "test", "action": "test", "parameters": {}}]}
        response = requests.post(
            "http://localhost:8001/api/intelligence/simulate/", 
            json=test_data, 
            timeout=10
        )
        if response.status_code == 200:
            print("✅ 变更模拟API测试通过")
            passed_tests += 1
        else:
            print(f"❌ 变更模拟API测试失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 变更模拟API测试异常: {e}")
    
    total_tests += 1
    
    # 5. 检查前端文件
    print("\n5️⃣ 检查前端文件...")
    
    frontend_files = [
        "e:\\code\\Q\\org-platform\\frontend\\src\\views\\IntelligentAnalysis.vue",
        "e:\\code\\Q\\org-platform\\frontend\\src\\api\\intelligence.ts",
        "e:\\code\\Q\\.superdesign\\design_iterations\\intelligent_org_architecture_1.html"
    ]
    
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)} 文件存在")
        else:
            print(f"❌ {os.path.basename(file_path)} 文件缺失")
    
    # 6. 输出测试结果
    print("\n" + "=" * 60)
    print("📋 测试结果总结")
    print("=" * 60)
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"API测试通过率: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 测试结果良好！功能基本可用")
    elif success_rate >= 60:
        print("⚠️ 测试结果一般，部分功能可能有问题")
    else:
        print("❌ 测试结果较差，需要检查配置和代码")
    
    # 7. 提供下一步指导
    print("\n📝 下一步测试建议:")
    print("1. 在浏览器访问: http://localhost:8001/admin/ (检查后端)")
    print("2. 查看界面效果: http://127.0.0.1:21962/intelligent_org_architecture_1.html")
    print("3. 启动前端服务: cd org-platform/frontend && npm run dev")
    print("4. 集成Vue组件到前端项目")
    
    # 8. 保存测试报告
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": success_rate,
        "api_results": []
    }
    
    with open("test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细测试报告已保存到: test_report.json")

if __name__ == "__main__":
    main()
