#!/usr/bin/env python
"""
修复员工数据同步问题
将organizations.models.Employee的数据同步到evaluations.models.Employee
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'performance_system.settings')
django.setup()

from organizations.models import Employee as OrgEmployee
from evaluations.models import Employee as EvalEmployee

def sync_employee_data():
    """将organizations的员工数据同步到evaluations"""
    print("=== 开始同步员工数据到evaluations模型 ===")
    
    # 1. 清空evaluations中的员工数据
    print("\n1. 清空evaluations中的员工数据...")
    
    # 先删除相关的外键记录
    from evaluations.models import ManualEvaluationAssignment, EvaluationTask, EvaluationResult
    print("删除相关的外键记录...")
    ManualEvaluationAssignment.objects.all().delete()
    EvaluationTask.objects.all().delete()
    EvaluationResult.objects.all().delete()
    
    # 然后删除员工记录
    EvalEmployee.objects.all().delete()
    print("已清空evaluations中的员工数据")
    
    # 2. 获取organizations中的员工数据
    print("\n2. 获取organizations中的员工数据...")
    org_employees = OrgEmployee.objects.all()
    print(f"organizations员工总数: {org_employees.count()}")
    
    # 3. 同步到evaluations
    print("\n3. 同步到evaluations...")
    synced_count = 0
    
    for org_emp in org_employees:
        try:
            # 创建evaluations中的员工记录
            eval_emp = EvalEmployee.objects.create(
                employee_id=org_emp.employee_id,
                name=org_emp.name,
                department_id=org_emp.department_id,
                department_name=org_emp.department_name,
                position_id=org_emp.position_id,
                position_name=org_emp.position_name,
                position_level=org_emp.position_level,
                supervisor_id=org_emp.supervisor_id,
                email=org_emp.email,
                phone=org_emp.phone,
                status='active',  # evaluations模型使用status字段
                is_active=org_emp.is_active
            )
            synced_count += 1
            print(f"  同步员工: {eval_emp.name} ({eval_emp.position_name}, L{eval_emp.position_level})")
            
        except Exception as e:
            print(f"  同步员工失败 {org_emp.name}: {e}")
    
    print(f"\n成功同步 {synced_count} 个员工")
    
    # 4. 验证同步结果
    print("\n4. 验证同步结果...")
    eval_employees = EvalEmployee.objects.all()
    print(f"evaluations员工总数: {eval_employees.count()}")
    
    # 按级别分组显示
    level_groups = {}
    for emp in eval_employees:
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
    managers = EvalEmployee.objects.filter(position_name__contains='部门经理')
    print(f"部门经理总数: {managers.count()}")
    for manager in managers:
        print(f"  {manager.name}: {manager.position_name}, L{manager.position_level}")
    
    # 6. 检查公司领导
    print("\n6. 检查公司领导...")
    leaders = EvalEmployee.objects.filter(position_level__gte=12)
    print(f"公司领导总数: {leaders.count()}")
    for leader in leaders:
        print(f"  {leader.name}: {leader.position_name}, L{leader.position_level}")
    
    print("\n=== 员工数据同步完成 ===")

if __name__ == '__main__':
    sync_employee_data()
