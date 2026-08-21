from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm

from accounts.models import Invitation, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin keyed by e-mail: the stock UserAdmin assumes a username field."""

    change_password_form = AdminPasswordChangeForm
    ordering = ['full_name']
    list_display = ['email', 'full_name', 'tenant', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'tenant']
    search_fields = ['email', 'full_name', 'phone']
    autocomplete_fields = ['tenant']
    readonly_fields = ['last_login', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        ('Dados pessoais', {'fields': ['full_name', 'phone', 'avatar']}),
        ('Corretora e papel', {'fields': ['tenant', 'role']}),
        ('Permissões', {
            'fields': ['is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'],
        }),
        ('Datas', {'fields': ['last_login', 'created_at', 'updated_at']}),
    ]

    add_fieldsets = [
        (None, {
            'classes': ['wide'],
            'fields': ['email', 'full_name', 'tenant', 'role', 'password1', 'password2'],
        }),
    ]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'tenant', 'role', 'status_label', 'expires_at', 'created_at']
    list_filter = ['role', 'tenant', 'accepted_at']
    search_fields = ['email', 'token']
    autocomplete_fields = ['tenant', 'invited_by']
    readonly_fields = ['token', 'accepted_at', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    @admin.display(description='situação')
    def status_label(self, obj):
        return obj.status_label
