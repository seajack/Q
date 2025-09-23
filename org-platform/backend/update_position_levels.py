#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'org_platform.settings')
django.setup()

from organizations.models import Position

# 更新现有职位的管理层级
positions_to_update = [
    {'code': 'DEV_SENIOR', 'management_level': 'middle', 'level': 8},  # 中层副职
    {'code': 'DEV_JUNIOR', 'management_level': 'junior', 'level': 1},  # 员工
    {'code': 'HR_SPECIALIST', 'management_level': 'junior', 'level': 2},  # 基层助理
    {'code': 'ACCOUNTANT', 'management_level': 'junior', 'level': 2},  # 基层助理
]

# 添加一些新的职位示例
new_positions = [
    {
        'name': '技术总监',
        'code': 'CTO',
        'department_code': 'TECH',
        'management_level': 'senior',
        'level': 12,  # 高层副职
        'description': '负责公司技术战略和团队管理',
        'requirements': '10年以上技术管理经验',
        'responsibilities': '制定技术战略、管理技术团队、技术决策'
    },
    {
        'name': '开发经理',
        'code': 'DEV_MANAGER',
        'department_code': 'TECH',
        'management_level': 'middle',
        'level': 9,  # 中层正职
        'description': '负责开发团队管理',
        'requirements': '5年以上开发管理经验',
        'responsibilities': '团队管理、项目协调、技术指导'
    },
    {
        'name': '项目主管',
        'code': 'PROJECT_LEAD',
        'department_code': 'TECH',
        'management_level': 'junior',
        'level': 4,  # 基层正职
        'description': '负责具体项目管理',
        'requirements': '3年以上项目经验',
        'responsibilities': '项目管理、进度跟踪、质量控制'
    }
]

# 更新现有职位
for pos_data in positions_to_update:
    try:
        position = Position.objects.get(code=pos_data['code'])
        position.management_level = pos_data['management_level']
        position.level = pos_data['level']
        position.save()
        print(f"更新职位: {position.name} - {position.get_level_display()}")
    except Position.DoesNotExist:
        print(f"职位不存在: {pos_data['code']}")

# 创建新职位
from organizations.models import Department

for pos_data in new_positions:
    try:
        department = Department.objects.get(code=pos_data['department_code'])
        position, created = Position.objects.get_or_create(
            code=pos_data['code'],
            defaults={
                'name': pos_data['name'],
                'department': department,
                'management_level': pos_data['management_level'],
                'level': pos_data['level'],
                'description': pos_data['description'],
                'requirements': pos_data['requirements'],
                'responsibilities': pos_data['responsibilities'],
                'is_active': True
            }
        )
        if created:
            print(f"创建新职位: {position.name} - {position.get_level_display()}")
        else:
            print(f"职位已存在: {position.name}")
    except Department.DoesNotExist:
        print(f"部门不存在: {pos_data['department_code']}")

print("\n职位级别更新完成！")
print(f"总职位数量: {Position.objects.count()}")

# 显示所有职位的层级信息
print("\n当前所有职位:")
for position in Position.objects.all().order_by('-level'):
    print(f"  {position.name} ({position.code}) - {position.get_management_level_display()}/{position.get_level_display()}")