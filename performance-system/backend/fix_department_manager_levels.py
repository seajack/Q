#!/usr/bin/env python
"""
修复部门经理级别脚本
将许褚和张辽的级别从L1修正为L9
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'performance_system.settings')
django.setup()

from organizations.models import Employee

def fix_department_manager_levels():
    """修复部门经理级别"""
    print("开始修复部门经理级别...")
    
    # 查找许褚和张辽
    xuchu = Employee.objects.filter(name='许褚').first()
    zhangliao = Employee.objects.filter(name='张辽').first()
    
    if xuchu:
        print(f"修复前 - 许褚: {xuchu.name}, 职位: {xuchu.position_name}, 级别: L{xuchu.position_level}")
        xuchu.position_level = 9
        xuchu.save()
        print(f"修复后 - 许褚: {xuchu.name}, 职位: {xuchu.position_name}, 级别: L{xuchu.position_level}")
    else:
        print("未找到许褚")
    
    if zhangliao:
        print(f"修复前 - 张辽: {zhangliao.name}, 职位: {zhangliao.position_name}, 级别: L{zhangliao.position_level}")
        zhangliao.position_level = 9
        zhangliao.save()
        print(f"修复后 - 张辽: {zhangliao.name}, 职位: {zhangliao.position_name}, 级别: L{zhangliao.position_level}")
    else:
        print("未找到张辽")
    
    # 验证修复结果
    print("\n验证修复结果:")
    all_managers = Employee.objects.filter(position_name__contains='部门经理')
    for manager in all_managers:
        print(f"{manager.name}: {manager.position_name}, 级别: L{manager.position_level}")
    
    print("\n修复完成！")

if __name__ == '__main__':
    fix_department_manager_levels()
