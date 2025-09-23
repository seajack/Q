from django.contrib import admin
from .models import Department, Position, Employee, OrganizationStructure


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'level', 'sort_order', 'manager', 'is_active', 'created_at']
    list_filter = ['level', 'is_active', 'parent']
    search_fields = ['name', 'code', 'description']
    ordering = ['level', 'sort_order', 'code']
    list_editable = ['sort_order', 'is_active']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'parent', 'manager')
        }),
        ('层级与排序', {
            'fields': ('level', 'sort_order')
        }),
        ('详细信息', {
            'fields': ('description', 'is_active')
        }),
    )


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'level', 'is_active', 'created_at']
    list_filter = ['level', 'is_active', 'department']
    search_fields = ['name', 'code', 'description']
    ordering = ['department', 'level', 'code']
    list_editable = ['is_active']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'department', 'level')
        }),
        ('详细信息', {
            'fields': ('description', 'requirements', 'responsibilities', 'is_active')
        }),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'employee_id', 'department', 'position', 'supervisor', 'status', 'hire_date']
    list_filter = ['status', 'gender', 'department', 'position', 'hire_date']
    search_fields = ['name', 'employee_id', 'phone', 'email']
    ordering = ['department', 'position__level', 'employee_id']
    list_editable = ['status']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'employee_id', 'name', 'gender', 'birth_date')
        }),
        ('联系方式', {
            'fields': ('phone', 'email', 'address')
        }),
        ('工作信息', {
            'fields': ('department', 'position', 'supervisor', 'hire_date', 'status')
        }),
        ('其他', {
            'fields': ('avatar',)
        }),
    )


@admin.register(OrganizationStructure)
class OrganizationStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_current', 'created_by', 'created_at']
    list_filter = ['is_current', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_by', 'created_at']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
