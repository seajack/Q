#!/usr/bin/env python
"""
完整数据同步和修复脚本
1. 从组织架构中台同步员工数据
2. 修复部门经理级别
3. 验证数据完整性
"""
import os
import django
import requests
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'performance_system.settings')
django.setup()

from organizations.models import Employee
from organizations.services import OrganizationService

def sync_and_fix_data():
    """同步和修复数据"""
    print("=== 开始完整数据同步和修复 ===")
    
    # 1. 从组织架构中台获取员工数据
    print("\n1. 从组织架构中台获取员工数据...")
    try:
        response = requests.get('http://127.0.0.1:8000/api/employees/')
        if response.status_code == 200:
            data = response.json()
            print(f"API响应数据类型: {type(data)}")
            print(f"API响应数据: {data}")
            
            # 处理不同的响应格式
            if isinstance(data, list):
                org_employees = data
            elif isinstance(data, dict) and 'results' in data:
                org_employees = data['results']
            else:
                print(f"未知的响应格式: {data}")
                return
                
            print(f"组织架构中台员工数: {len(org_employees)}")
            
            # 显示组织架构中台的员工信息
            for emp in org_employees:
                print(f"  {emp['name']}: {emp.get('position_name', '未知职位')}, L{emp.get('position_level', '未知级别')}")
        else:
            print(f"获取组织架构中台数据失败: {response.status_code}")
            return
    except Exception as e:
        print(f"连接组织架构中台失败: {e}")
        return
    
    # 2. 清空绩效考核系统的员工数据
    print("\n2. 清空绩效考核系统的员工数据...")
    Employee.objects.all().delete()
    print("已清空所有员工数据")
    
    # 3. 手动创建员工数据（基于组织架构中台的数据）
    print("\n3. 手动创建员工数据...")
    created_count = 0
    
    for emp_data in org_employees:
        try:
            # 确定正确的职位级别
            position_name = emp_data.get('position_name', '')
            position_level = emp_data.get('position_level', 1)
            
            # 如果是部门经理，强制设置为L9
            if '部门经理' in position_name:
                position_level = 9
                print(f"  修正 {emp_data['name']} 的级别为 L9")
            
            # 创建员工记录
            employee = Employee.objects.create(
                employee_id=str(emp_data.get('id')),
                name=emp_data['name'],
                department_id=emp_data.get('department', 0),
                department_name=emp_data.get('department_name', ''),
                position_id=emp_data.get('position', 0),
                position_name=position_name,
                position_level=position_level,
                supervisor_id=emp_data.get('supervisor', None),
                email=emp_data.get('email', ''),
                phone=emp_data.get('phone', ''),
                is_active=True
            )
            created_count += 1
            print(f"  创建员工: {employee.name} ({employee.position_name}, L{employee.position_level})")
            
        except Exception as e:
            print(f"  创建员工失败 {emp_data.get('name', 'unknown')}: {e}")
    
    print(f"\n成功创建 {created_count} 个员工")
    
    # 4. 验证修复结果
    print("\n4. 验证修复结果...")
    all_employees = Employee.objects.all()
    print(f"绩效考核系统员工总数: {all_employees.count()}")
    
    # 按级别分组显示
    level_groups = {}
    for emp in all_employees:
        level = emp.position_level
        if level not in level_groups:
            level_groups[level] = []
        level_groups[level].append(emp)
    
    for level in sorted(level_groups.keys(), reverse=True):
        employees = level_groups[level]
        print(f"\nL{level}级别 ({len(employees)}人):")
        for emp in employees:
            print(f"  {emp.name}: {emp.position_name}")
    
    # 5. 检查部门经理
    print("\n5. 检查部门经理...")
    managers = Employee.objects.filter(position_name__contains='部门经理')
    print(f"部门经理总数: {managers.count()}")
    for manager in managers:
        print(f"  {manager.name}: {manager.position_name}, L{manager.position_level}")
    
    # 6. 检查公司领导
    print("\n6. 检查公司领导...")
    leaders = Employee.objects.filter(position_level__gte=12)
    print(f"公司领导总数: {leaders.count()}")
    for leader in leaders:
        print(f"  {leader.name}: {leader.position_name}, L{leader.position_level}")
    
    # 7. 计算应该生成的考核关系
    print("\n7. 计算考核关系...")
    managers = Employee.objects.filter(position_name__contains='部门经理')
    leaders = Employee.objects.filter(position_level__gte=12)
    expected_relationships = leaders.count() * managers.count()
    print(f"应该生成的考核关系: {leaders.count()} × {managers.count()} = {expected_relationships}")
    
    print("\n=== 数据同步和修复完成 ===")

if __name__ == '__main__':
    sync_and_fix_data()
