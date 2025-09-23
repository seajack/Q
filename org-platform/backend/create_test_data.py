#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'org_platform.settings')
django.setup()

from organizations.models import Department, Position

# 创建部门
tech_dept = Department.objects.get_or_create(
    code='TECH',
    defaults={
        'name': '技术部',
        'level': 1,
        'sort_order': 1,
        'description': '技术开发部门',
        'is_active': True
    }
)[0]

hr_dept = Department.objects.get_or_create(
    code='HR',
    defaults={
        'name': '人力资源部',
        'level': 1,
        'sort_order': 2,
        'description': '人力资源管理部门',
        'is_active': True
    }
)[0]

finance_dept = Department.objects.get_or_create(
    code='FINANCE',
    defaults={
        'name': '财务部',
        'level': 1,
        'sort_order': 3,
        'description': '财务管理部门',
        'is_active': True
    }
)[0]

# 创建职位
Position.objects.get_or_create(
    code='DEV_SENIOR',
    defaults={
        'name': '高级开发工程师',
        'department': tech_dept,
        'level': 3,
        'description': '负责核心系统开发',
        'requirements': '3年以上开发经验',
        'responsibilities': '系统设计、代码开发、技术指导',
        'is_active': True
    }
)

Position.objects.get_or_create(
    code='DEV_JUNIOR',
    defaults={
        'name': '初级开发工程师',
        'department': tech_dept,
        'level': 1,
        'description': '参与项目开发',
        'requirements': '计算机相关专业',
        'responsibilities': '编写代码、单元测试',
        'is_active': True
    }
)

Position.objects.get_or_create(
    code='HR_SPECIALIST',
    defaults={
        'name': '人力资源专员',
        'department': hr_dept,
        'level': 2,
        'description': '负责人员招聘和管理',
        'requirements': '人力资源相关专业',
        'responsibilities': '招聘、培训、绩效管理',
        'is_active': True
    }
)

Position.objects.get_or_create(
    code='ACCOUNTANT',
    defaults={
        'name': '会计',
        'department': finance_dept,
        'level': 2,
        'description': '负责日常账务处理',
        'requirements': '会计专业',
        'responsibilities': '记账、报税、财务报表',
        'is_active': True
    }
)

print("测试数据创建完成！")
print(f"部门数量: {Department.objects.count()}")
print(f"职位数量: {Position.objects.count()}")