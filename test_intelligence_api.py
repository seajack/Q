#!/usr/bin/env python3
"""
智能组织架构API测试脚本
测试所有智能分析相关的API接口
"""

import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/intelligence"

# 测试用的认证token（如果需要的话）
# 这里假设有一个测试用户token，实际使用时需要先登录获取
HEADERS = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer your_token_here"  # 如果需要认证
}

class IntelligenceAPITester:
    def __init__(self):
        self.base_url = API_BASE
        self.headers = HEADERS
        self.test_results = []
    
    def log_test(self, test_name, success, message="", response_data=None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if response_data and isinstance(response_data, dict):
            if "error" in response_data:
                print(f"   Error: {response_data['error']}")
    
    def test_organization_analysis(self):
        """测试组织分析接口"""
        print("\n🧠 测试组织分析接口...")
        
        try:
            response = requests.get(f"{self.base_url}/analysis/", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    analysis_data = data.get("data", {})
                    
                    # 验证返回数据结构
                    required_fields = ["overall_score", "health_level", "analysis_results", "recommendations"]
                    missing_fields = [field for field in required_fields if field not in analysis_data]
                    
                    if not missing_fields:
                        self.log_test(
                            "组织分析接口", 
                            True, 
                            f"成功获取分析结果，综合得分: {analysis_data.get('overall_score', 0)}分",
                            analysis_data
                        )
                    else:
                        self.log_test(
                            "组织分析接口", 
                            False, 
                            f"返回数据缺少字段: {missing_fields}",
                            data
                        )
                else:
                    self.log_test("组织分析接口", False, "API返回success=False", data)
            else:
                self.log_test("组织分析接口", False, f"HTTP状态码: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("组织分析接口", False, f"请求异常: {str(e)}")
    
    def test_organization_metrics(self):
        """测试组织指标接口"""
        print("\n📊 测试组织指标接口...")
        
        try:
            response = requests.get(f"{self.base_url}/metrics/", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    metrics = data.get("data", {})
                    
                    # 验证指标数据
                    expected_metrics = ["total_departments", "total_employees", "management_ratio"]
                    
                    if any(metric in metrics for metric in expected_metrics):
                        self.log_test(
                            "组织指标接口", 
                            True, 
                            f"成功获取指标数据，部门数: {metrics.get('total_departments', 0)}",
                            metrics
                        )
                    else:
                        self.log_test("组织指标接口", False, "返回数据不包含预期指标", data)
                else:
                    self.log_test("组织指标接口", False, "API返回success=False", data)
            else:
                self.log_test("组织指标接口", False, f"HTTP状态码: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("组织指标接口", False, f"请求异常: {str(e)}")
    
    def test_refresh_analysis(self):
        """测试刷新分析接口"""
        print("\n🔄 测试刷新分析接口...")
        
        try:
            response = requests.post(f"{self.base_url}/refresh/", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    self.log_test(
                        "刷新分析接口", 
                        True, 
                        "成功刷新分析结果",
                        {"message": data.get("message", "")}
                    )
                else:
                    self.log_test("刷新分析接口", False, "API返回success=False", data)
            else:
                self.log_test("刷新分析接口", False, f"HTTP状态码: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("刷新分析接口", False, f"请求异常: {str(e)}")
    
    def test_optimization_suggestions(self):
        """测试优化建议接口"""
        print("\n💡 测试优化建议接口...")
        
        try:
            response = requests.get(f"{self.base_url}/suggestions/", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    suggestions_data = data.get("data", {})
                    
                    # 验证建议数据结构
                    if "by_priority" in suggestions_data and "summary" in suggestions_data:
                        total_suggestions = suggestions_data.get("total_count", 0)
                        self.log_test(
                            "优化建议接口", 
                            True, 
                            f"成功获取优化建议，共{total_suggestions}条",
                            suggestions_data["summary"]
                        )
                    else:
                        self.log_test("优化建议接口", False, "返回数据结构不正确", data)
                else:
                    self.log_test("优化建议接口", False, "API返回success=False", data)
            else:
                self.log_test("优化建议接口", False, f"HTTP状态码: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("优化建议接口", False, f"请求异常: {str(e)}")
    
    def test_simulate_changes(self):
        """测试变更模拟接口"""
        print("\n🎯 测试变更模拟接口...")
        
        # 模拟变更数据
        test_changes = [
            {
                "type": "department_merge",
                "target": "人事部",
                "action": "merge_with",
                "parameters": {"target_department": "行政部"}
            }
        ]
        
        try:
            response = requests.post(
                f"{self.base_url}/simulate/", 
                headers=self.headers,
                json={"changes": test_changes}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    simulation_result = data.get("data", {})
                    
                    # 验证模拟结果
                    expected_fields = ["current_score", "predicted_score", "improvement"]
                    
                    if all(field in simulation_result for field in expected_fields):
                        improvement = simulation_result.get("improvement", 0)
                        self.log_test(
                            "变更模拟接口", 
                            True, 
                            f"成功模拟变更影响，预期改善: {improvement}分",
                            simulation_result
                        )
                    else:
                        self.log_test("变更模拟接口", False, "返回数据缺少必要字段", data)
                else:
                    self.log_test("变更模拟接口", False, "API返回success=False", data)
            else:
                self.log_test("变更模拟接口", False, f"HTTP状态码: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("变更模拟接口", False, f"请求异常: {str(e)}")
    
    def test_benchmark_comparison(self):
        """测试基准对比接口"""
        print("\n📈 测试基准对比接口...")
        
        try:
            response = requests.get(f"{self.base_url}/benchmark/", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    benchmark_data = data.get("data", {})
                    
                    # 验证对比数据
                    if "comparison" in benchmark_data and "overall_assessment" in benchmark_data:
                        assessment = benchmark_data.get("overall_assessment", "")
                        self.log_test(
                            "基准对比接口", 
                            True, 
                            f"成功获取基准对比: {assessment}",
                            benchmark_data
                        )
                    else:
                        self.log_test("基准对比接口", False, "返回数据结构不正确", data)
                else:
                    self.log_test("基准对比接口", False, "API返回success=False", data)
            else:
                self.log_test("基准对比接口", False, f"HTTP状态码: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("基准对比接口", False, f"请求异常: {str(e)}")
    
    def test_analysis_history(self):
        """测试分析历史接口"""
        print("\n📚 测试分析历史接口...")
        
        try:
            response = requests.get(f"{self.base_url}/history/", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    history_data = data.get("data", [])
                    
                    if isinstance(history_data, list):
                        self.log_test(
                            "分析历史接口", 
                            True, 
                            f"成功获取历史记录，共{len(history_data)}条",
                            {"count": len(history_data)}
                        )
                    else:
                        self.log_test("分析历史接口", False, "返回数据不是列表格式", data)
                else:
                    self.log_test("分析历史接口", False, "API返回success=False", data)
            else:
                self.log_test("分析历史接口", False, f"HTTP状态码: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("分析历史接口", False, f"请求异常: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始智能组织架构API测试...")
        print("=" * 60)
        
        # 测试服务器连接
        try:
            response = requests.get(BASE_URL, timeout=5)
            print(f"✅ 服务器连接正常 (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ 服务器连接失败: {str(e)}")
            return
        
        # 运行各项测试
        self.test_organization_analysis()
        self.test_organization_metrics()
        self.test_refresh_analysis()
        self.test_optimization_suggestions()
        self.test_simulate_changes()
        self.test_benchmark_comparison()
        self.test_analysis_history()
        
        # 输出测试总结
        self.print_test_summary()
    
    def print_test_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("📋 测试总结")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        print("\n💾 详细测试结果已保存到 test_results.json")
        
        # 保存详细结果到文件
        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    tester = IntelligenceAPITester()
    tester.run_all_tests()
