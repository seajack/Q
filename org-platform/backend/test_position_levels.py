#!/usr/bin/env python
"""测试职位级别API功能"""

import os
import sys
import json
import requests

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'org_platform.settings')

import django
django.setup()

from organizations.models import Department, Position

# API基础URL
BASE_URL = 'http://localhost:8001/api'

def test_position_levels():
    """测试新的职位级别体系"""
    print("开始测试职位级别API功能...")
    
    # 1. 获取第一个部门
    departments = Department.objects.filter(is_active=True).first()
    if not departments:
        print("错误：没有找到可用的部门，请先创建部门")
        return
    
    print(f"使用部门：{departments.name} (ID: {departments.id})")
    
    # 2. 测试创建不同级别的职位
    test_positions = [
        {
            "name": "董事长",
            "code": "CEO_001",
            "department": departments.id,
            "management_level": "senior",
            "level": 13,
            "description": "公司最高管理者"
        },
        {
            "name": "副总经理",
            "code": "VP_001", 
            "department": departments.id,
            "management_level": "senior",
            "level": 12,
            "description": "高层副职管理者"
        },
        {
            "name": "部门经理",
            "code": "MGR_001",
            "department": departments.id,
            "management_level": "middle",
            "level": 9,
            "description": "中层正职管理者"
        },
        {
            "name": "部门副经理",
            "code": "VMGR_001",
            "department": departments.id,
            "management_level": "middle",
            "level": 8,
            "description": "中层副职管理者"
        },
        {
            "name": "主管",
            "code": "SUP_001",
            "department": departments.id,
            "management_level": "junior",
            "level": 4,
            "description": "基层正职管理者"
        },
        {
            "name": "普通员工",
            "code": "EMP_001",
            "department": departments.id,
            "management_level": "junior",
            "level": 1,
            "description": "基层员工"
        }
    ]
    
    created_positions = []
    
    print("\n创建测试职位...")
    for pos_data in test_positions:
        try:
            response = requests.post(f"{BASE_URL}/positions/", json=pos_data)
            if response.status_code == 201:
                position = response.json()
                created_positions.append(position)
                print(f"✓ 创建职位成功: {position['name']} ({position['level_display_with_management']})")
            else:
                print(f"✗ 创建职位失败: {pos_data['name']} - {response.text}")
        except Exception as e:
            print(f"✗ 创建职位异常: {pos_data['name']} - {str(e)}")
    
    # 3. 获取所有职位并验证层级显示
    print("\n获取职位列表...")
    try:
        response = requests.get(f"{BASE_URL}/positions/")
        if response.status_code == 200:
            positions = response.json()['results']
            print(f"✓ 获取到 {len(positions)} 个职位")
            
            print("\n职位级别层次结构：")
            positions_sorted = sorted(positions, key=lambda x: x['level'], reverse=True)
            for pos in positions_sorted:
                print(f"  - {pos['name']}: {pos['level_display_with_management']} (级别: {pos['level']})")
        else:
            print(f"✗ 获取职位列表失败: {response.text}")
    except Exception as e:
        print(f"✗ 获取职位列表异常: {str(e)}")
    
    # 4. 测试管理层级筛选
    print("\n测试管理层级筛选...")
    for level in ['senior', 'middle', 'junior']:
        try:
            response = requests.get(f"{BASE_URL}/positions/", params={'management_level': level})
            if response.status_code == 200:
                positions = response.json()['results']
                level_names = {'senior': '高层', 'middle': '中层', 'junior': '基层'}
                print(f"✓ {level_names[level]}职位: {len(positions)} 个")
            else:
                print(f"✗ 筛选{level}级别失败: {response.text}")
        except Exception as e:
            print(f"✗ 筛选{level}级别异常: {str(e)}")
    
    print("\n职位级别API功能测试完成！")
    return created_positions

if __name__ == '__main__':
    test_position_levels()