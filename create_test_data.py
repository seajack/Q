#!/usr/bin/env python3
"""
创建测试数据脚本
为智能分析功能创建必要的测试数据
"""

import os
import sys
import django

# 设置Django环境
sys.path.append('e:/code/Q/org-platform/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'org_platform.settings')
django.setup()

from organizations.models import Department, Position, Employee
from django.contrib.auth.models import User

def create_test_data():
    print("🏗️ 创建测试数据...")
    
    # 创建测试用户
    if not User.objects.filter(username='testuser').exists():
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print("✅ 创建测试用户: testuser")
    
    # 创建根部门
    if not Department.objects.filter(name='总公司').exists():
        root_dept = Department.objects.create(
            name='总公司',
            code='ROOT',
            description='公司总部',
            level=1,
            is_active=True
        )
        print("✅ 创建根部门: 总公司")
    else:
        root_dept = Department.objects.get(name='总公司')
    
    # 创建子部门
    departments_data = [
        {'name': '技术部', 'code': 'TECH', 'description': '技术研发部门'},
        {'name': '市场部', 'code': 'MARKET', 'description': '市场营销部门'},
        {'name': '人事部', 'code': 'HR', 'description': '人力资源部门'},
        {'name': '财务部', 'code': 'FINANCE', 'description': '财务管理部门'},
    ]
    
    created_depts = []
    for dept_data in departments_data:
        if not Department.objects.filter(name=dept_data['name']).exists():
            dept = Department.objects.create(
                name=dept_data['name'],
                code=dept_data['code'],
                description=dept_data['description'],
                parent=root_dept,
                level=2,
                is_active=True
            )
            created_depts.append(dept)
            print(f"✅ 创建部门: {dept_data['name']}")
        else:
            dept = Department.objects.get(name=dept_data['name'])
            created_depts.append(dept)
    
    # 创建职位
    positions_data = [
        {'name': '总经理', 'level': 13, 'description': '公司总经理'},
        {'name': '部门经理', 'level': 9, 'description': '部门负责人'},
        {'name': '高级工程师', 'level': 7, 'description': '高级技术人员'},
        {'name': '工程师', 'level': 5, 'description': '普通技术人员'},
        {'name': '专员', 'level': 3, 'description': '专业人员'},
    ]
    
    created_positions = []
    for pos_data in positions_data:
        if not Position.objects.filter(name=pos_data['name']).exists():
            position = Position.objects.create(
                name=pos_data['name'],
                level=pos_data['level'],
                description=pos_data['description'],
                is_active=True
            )
            created_positions.append(position)
            print(f"✅ 创建职位: {pos_data['name']}")
        else:
            position = Position.objects.get(name=pos_data['name'])
            created_positions.append(position)
    
    # 创建员工
    employees_data = [
        {'name': '张总', 'employee_id': 'CEO001', 'dept': root_dept, 'pos': created_positions[0]},
        {'name': '李经理', 'employee_id': 'TECH001', 'dept': created_depts[0], 'pos': created_positions[1]},
        {'name': '王工程师', 'employee_id': 'TECH002', 'dept': created_depts[0], 'pos': created_positions[2]},
        {'name': '赵工程师', 'employee_id': 'TECH003', 'dept': created_depts[0], 'pos': created_positions[3]},
        {'name': '刘经理', 'employee_id': 'MKT001', 'dept': created_depts[1], 'pos': created_positions[1]},
        {'name': '陈专员', 'employee_id': 'MKT002', 'dept': created_depts[1], 'pos': created_positions[4]},
        {'name': '周经理', 'employee_id': 'HR001', 'dept': created_depts[2], 'pos': created_positions[1]},
        {'name': '吴专员', 'employee_id': 'HR002', 'dept': created_depts[2], 'pos': created_positions[4]},
    ]
    
    for emp_data in employees_data:
        if not Employee.objects.filter(employee_id=emp_data['employee_id']).exists():
            employee = Employee.objects.create(
                name=emp_data['name'],
                employee_id=emp_data['employee_id'],
                department=emp_data['dept'],
                position=emp_data['pos'],
                status='active',
                email=f"{emp_data['employee_id'].lower()}@company.com",
                phone=f"138{emp_data['employee_id'][-4:]}0000"
            )
            print(f"✅ 创建员工: {emp_data['name']} ({emp_data['employee_id']})")
    
    print("\n📊 测试数据统计:")
    print(f"部门数量: {Department.objects.count()}")
    print(f"职位数量: {Position.objects.count()}")
    print(f"员工数量: {Employee.objects.count()}")
    print("\n✅ 测试数据创建完成！")

if __name__ == "__main__":
    create_test_data()
