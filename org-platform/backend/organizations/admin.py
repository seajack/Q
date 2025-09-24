from django.contrib import admin
from .models import Department, Position, Employee, OrganizationStructure, SystemConfig, Dictionary, PositionTemplate, WorkflowRule


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


# 配置管理Admin
@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'category', 'data_type', 'is_active', 'is_required', 'updated_at']
    list_filter = ['category', 'data_type', 'is_active', 'is_required', 'is_encrypted']
    search_fields = ['key', 'description', 'value']
    ordering = ['category', 'key']
    list_editable = ['is_active', 'is_required']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('key', 'value', 'category', 'data_type')
        }),
        ('描述与状态', {
            'fields': ('description', 'is_active', 'is_required', 'is_encrypted')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Dictionary)
class DictionaryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'parent', 'sort_order', 'is_active', 'updated_at']
    list_filter = ['category', 'is_active', 'parent']
    search_fields = ['name', 'code', 'description', 'value']
    ordering = ['category', 'sort_order', 'code']
    list_editable = ['sort_order', 'is_active']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('category', 'code', 'name', 'value', 'parent')
        }),
        ('排序与状态', {
            'fields': ('sort_order', 'is_active')
        }),
        ('详细信息', {
            'fields': ('description',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


@admin.register(PositionTemplate)
class PositionTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'management_level', 'level', 'is_active', 'created_at']
    list_filter = ['management_level', 'level', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['-level', 'name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'management_level', 'level')
        }),
        ('模板内容', {
            'fields': ('description', 'default_requirements', 'default_responsibilities')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
    )


@admin.register(WorkflowRule)
class WorkflowRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'priority', 'is_active', 'created_at']
    list_filter = ['rule_type', 'is_active']
    search_fields = ['name']
    ordering = ['-priority', 'name']
    list_editable = ['priority', 'is_active']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'rule_type', 'priority')
        }),
        ('规则配置', {
            'fields': ('trigger_conditions', 'action_config')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)
