from django.db import models


class Employee(models.Model):
    """员工模型（从中台同步）"""
    employee_id = models.CharField('员工号', max_length=20, unique=True)
    name = models.CharField('姓名', max_length=50)
    department_id = models.IntegerField('部门ID')
    department_name = models.CharField('部门名称', max_length=100)
    position_id = models.IntegerField('职位ID')
    position_name = models.CharField('职位名称', max_length=100)
    position_level = models.IntegerField('职位级别', default=1)
    supervisor_id = models.IntegerField('上级ID', null=True, blank=True)
    email = models.EmailField('邮箱', blank=True)
    phone = models.CharField('手机', max_length=20, blank=True)
    is_active = models.BooleanField('是否激活', default=True)
    last_sync = models.DateTimeField('最后同步时间', auto_now=True)

    class Meta:
        verbose_name = '员工'
        verbose_name_plural = '员工'
        ordering = ['department_name', 'position_level', 'employee_id']

    def __str__(self):
        return f"{self.name} ({self.employee_id})"