#!/usr/bin/env python3
"""
快速API测试脚本
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_api():
    print("🧪 快速API测试")
    print("=" * 40)
    
    # 测试基本连接
    try:
        response = requests.get(f"{BASE_URL}/api/", timeout=5)
        print(f"✅ 服务器连接: {response.status_code}")
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return
    
    # 测试智能分析接口
    try:
        response = requests.get(f"{BASE_URL}/api/intelligence/analysis/")
        print(f"📊 智能分析接口: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   返回数据: {data.get('success', False)}")
    except Exception as e:
        print(f"❌ 智能分析接口错误: {e}")
    
    # 测试指标接口
    try:
        response = requests.get(f"{BASE_URL}/api/intelligence/metrics/")
        print(f"📈 指标接口: {response.status_code}")
    except Exception as e:
        print(f"❌ 指标接口错误: {e}")

if __name__ == "__main__":
    test_api()
