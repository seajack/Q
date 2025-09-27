#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'performance_system.settings')
django.setup()

from evaluations.models import Employee
import requests

def sync_employees():
    """从组织架构系统同步员工数据"""
    try:
        response = requests.get('http://127.0.0.1:8000/api/employees/')
        if response.status_code == 200:
            employees_data = response.json().get('results', [])
            print(f'从组织架构系统获取到 {len(employees_data)} 个员工')
            
            for emp_data in employees_data:
                employee_id = emp_data.get('employee_id', f'EMP{emp_data["id"]}')
                employee, created = Employee.objects.get_or_create(
                    employee_id=employee_id,
                    defaults={
                        'name': emp_data['name'],
                        'department_id': emp_data.get('department', 1),
                        'department_name': emp_data.get('department_name', '未知部门'),
                        'position_id': emp_data.get('position', 1),
                        'position_name': emp_data.get('position_name', '未知职位'),
                        'position_level': emp_data.get('position_level', 1),
                        'supervisor_id': emp_data.get('supervisor'),
                        'email': emp_data.get('email', ''),
                        'phone': emp_data.get('phone', ''),
                        'status': emp_data.get('status', 'active'),
                        'is_active': True
                    }
                )
                
                # 更新现有员工的信息
                if not created:
                    employee.name = emp_data['name']
                    employee.department_id = emp_data.get('department', 1)
                    employee.department_name = emp_data.get('department_name', '未知部门')
                    employee.position_id = emp_data.get('position', 1)
                    employee.position_name = emp_data.get('position_name', '未知职位')
                    employee.position_level = emp_data.get('position_level', 1)
                    employee.supervisor_id = emp_data.get('supervisor')
                    employee.email = emp_data.get('email', '')
                    employee.phone = emp_data.get('phone', '')
                    employee.status = emp_data.get('status', 'active')
                    employee.is_active = True
                    employee.save()
                    print(f'更新员工: {employee.name} (上级ID: {employee.supervisor_id})')
                else:
                    print(f'创建员工: {employee.name} (上级ID: {employee.supervisor_id})')
            
            print(f'同步完成，当前员工总数: {Employee.objects.count()}')
        else:
            print(f'无法连接到组织架构系统: {response.status_code}')
            create_test_data()
    except Exception as e:
        print(f'同步失败: {e}')
        create_test_data()

def create_test_data():
    """创建测试数据"""
    print('创建测试员工数据...')
    test_employees = [
        {'employee_id': 'EMP001', 'name': '张三', 'department_name': '技术部', 'position_name': '高级工程师'},
        {'employee_id': 'EMP002', 'name': '李四', 'department_name': '产品部', 'position_name': '产品经理'},
        {'employee_id': 'EMP003', 'name': '王五', 'department_name': '运营部', 'position_name': '运营专员'},
        {'employee_id': 'EMP004', 'name': '赵六', 'department_name': '人事部', 'position_name': 'HR专员'},
        {'employee_id': 'EMP005', 'name': '钱七', 'department_name': '财务部', 'position_name': '会计师'},
    ]
    
    for emp_data in test_employees:
        employee, created = Employee.objects.get_or_create(
            employee_id=emp_data['employee_id'],
            defaults={
                'name': emp_data['name'],
                'department_id': 1,
                'department_name': emp_data['department_name'],
                'position_id': 1,
                'position_name': emp_data['position_name'],
                'position_level': 5,
                'email': f'{emp_data["employee_id"].lower()}@company.com',
                'phone': '13800138000',
                'status': 'active',
                'is_active': True
            }
        )
        if created:
            print(f'创建测试员工: {employee.name}')
    
    print(f'测试数据创建完成，当前员工总数: {Employee.objects.count()}')

if __name__ == '__main__':
    sync_employees()
