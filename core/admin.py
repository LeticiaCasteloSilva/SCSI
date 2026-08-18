from django.contrib import admin

from core.models import Plan, Tenant


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'max_users', 'is_enabled', 'created_at']
    list_filter = ['is_enabled']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['price', 'name']


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['legal_name', 'trade_name', 'cnpj', 'plan', 'is_active', 'created_at']
    list_filter = ['is_active', 'plan']
    search_fields = ['legal_name', 'trade_name', 'cnpj', 'slug', 'email']
    autocomplete_fields = ['plan']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['legal_name']
    fieldsets = [
        ('Identificação', {'fields': ['legal_name', 'trade_name', 'cnpj', 'slug']}),
        ('Contato', {'fields': ['email', 'phone', 'susep_code', 'logo']}),
        ('Situação', {'fields': ['plan', 'is_active']}),
        ('Auditoria', {'fields': ['created_at', 'updated_at']}),
    ]
